import json
from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from pydantic import ValidationError

from schemas.applicant import ApplicantInput
from parsers.bank_statement_parser import BankStatementParser
from scoring.anti_gaming import detect_gaming_patterns, apply_gaming_penalty
from routers.fraud import fraud_check_with_score
from models.model_loader import get_registry

router = APIRouter(prefix="/anti-gaming", tags=["Anti-Gaming"])
parser = BankStatementParser()

@router.post("/score-with-gaming-check")
async def score_with_gaming_check(
    applicant: str = Form(...),
    statement: UploadFile = File(None),
    previous_application_count: int = Form(0),
    days_since_last_application: int = Form(None)
):
    """
    Runs the full scoring pipeline + anti-gaming check.
    If gaming patterns are detected, applies a penalty to the final score.
    """
    try:
        app_dict = json.loads(applicant)
        applicant_data = ApplicantInput(**app_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid applicant data: {str(e)}")
        
    transactions = []
    bank_features = {}
    
    # 1. Parse statement if provided
    if statement:
        try:
            content = await statement.read()
            filename = statement.filename.lower()
            
            # Simple assumption: parse returns features and transactions.
            # Depending on how Phase 5 is actually implemented, we might need to adjust.
            # Phase 5 says `parse_bank_statement(file_path: str) -> dict`.
            # Let's write to a temp file and parse.
            import tempfile
            import os
            
            suffix = ".csv" if filename.endswith(".csv") else ".pdf"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
                
            try:
                # Assuming parser.parse returns a dict with "extracted_features" and "transactions"
                file_type = "csv" if suffix == ".csv" else "pdf"
                parse_result = parser.parse(tmp_path, file_type=file_type)
                bank_features = parse_result.get("features", {})
                transactions = parse_result.get("transactions", [])
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
            # Overwrite applicant income with verified income for base scoring
            if bank_features.get("monthly_income_actual"):
                applicant_data.annual_income = bank_features["monthly_income_actual"] * 12
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Statement parsing failed: {str(e)}")

    # 2. Get base score
    base_result = await fraud_check_with_score(applicant_data, get_registry())
    base_score = base_result["credit_score"]["scoreseva_score"]

    # 3. Detect Gaming Patterns
    gaming_analysis = detect_gaming_patterns(
        transactions=transactions,
        bank_features=bank_features,
        applicant=app_dict,
        previous_application_count=previous_application_count,
        days_since_last_application=days_since_last_application
    )

    # 4. Apply Gaming Penalty
    final_score = apply_gaming_penalty(base_score, gaming_analysis["gaming_risk_score"])
    
    score_capped = False
    if gaming_analysis["risk_tier"] == "HIGH_RISK" and final_score == 550:
        score_capped = True
        
    penalty_applied = base_score - final_score

    # 5. Determine Verdict
    if penalty_applied > 0:
        if score_capped:
            verdict = f"Score capped at 550. {penalty_applied} points deducted due to high-risk gaming patterns."
        else:
            verdict = f"Score reduced by {penalty_applied} points due to detected transaction gaming patterns."
    else:
        verdict = "No gaming patterns detected — full score stands."

    return {
        "base_score": base_score,
        "final_score": final_score,
        "penalty_applied": penalty_applied,
        "gaming_analysis": gaming_analysis,
        "score_capped": score_capped,
        "verdict": verdict,
        "base_result": base_result # Include original result for UI
    }
