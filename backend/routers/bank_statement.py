import logging
import json
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Optional
from pydantic import ValidationError

from schemas.applicant import ApplicantInput
from parsers.bank_statement_parser import BankStatementParser
from models.model_loader import get_registry, ModelRegistry
from routers.fraud import fraud_check_with_score

logger = logging.getLogger("scoreseva.bank_statement")

router = APIRouter(prefix="/bank-statement", tags=["Bank Statement"])

parser = BankStatementParser()

def validate_file(file: UploadFile):
    allowed_extensions = [".pdf", ".csv"]
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF and CSV are supported.")
    
    # We can check size by reading it, but since we read it for parsing anyway:
    # Max size 10MB
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
        
    return "pdf" if file.filename.lower().endswith(".pdf") else "csv"

@router.post("/analyze")
async def analyze_statement(
    statement: UploadFile = File(...),
    applicant: Optional[str] = Form(None)
):
    file_type = validate_file(statement)
    
    try:
        parsed_data = parser.parse(statement.file, file_type=file_type)
    except Exception as e:
        logger.error(f"Error parsing statement: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to parse statement: {str(e)}")
        
    features = parsed_data["features"]
    
    # Check if applicant data was provided
    claimed_income = None
    if applicant:
        try:
            app_data = json.loads(applicant)
            claimed_income = app_data.get("annual_income")
        except json.JSONDecodeError:
            pass # ignore invalid json
            
    actual_income = features["monthly_income_actual"] * 12
    verification_status = "UNVERIFIED"
    discrepancy_pct = 0.0
    
    if claimed_income:
        if actual_income > 0:
            diff = claimed_income - actual_income
            discrepancy_pct = abs(diff) / claimed_income * 100
            
            if discrepancy_pct <= 10:
                verification_status = "MATCHES"
            elif diff > 0:
                verification_status = "OVERSTATED"
            else:
                verification_status = "UNDERSTATED"
        else:
            verification_status = "UNVERIFIED"
            
    return {
        "statement_summary": {
            "months_analyzed": features["statement_months"],
            "total_transactions": len(parsed_data["transactions"]),
            "salary_detected": features["salary_detected"],
            "monthly_income_actual": features["monthly_income_actual"],
            "income_regularity_score": features["income_regularity_score"],
            "avg_monthly_balance": features["avg_monthly_balance"],
            "bounce_count": features["bounce_count"],
            "hidden_emi_count": features["hidden_emi_count"],
            "financial_stress_score": features["financial_stress_score"]
        },
        "extracted_features": features,
        "income_verification": {
            "claimed_income": claimed_income,
            "actual_income": actual_income,
            "verification_status": verification_status,
            "discrepancy_pct": discrepancy_pct
        },
        "score_available": bool(applicant)
    }

@router.post("/score-with-statement")
async def score_with_statement(
    statement: UploadFile = File(...),
    applicant: str = Form(...),
    registry: ModelRegistry = Depends(get_registry)
):
    file_type = validate_file(statement)
    
    try:
        app_data = json.loads(applicant)
        # Parse into ApplicantInput
        app_input = ApplicantInput(**app_data)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in applicant field")
        
    # Baseline score without statement
    baseline_response = await fraud_check_with_score(app_input, registry)
    baseline_score = baseline_response["credit_score"]["scoreseva_score"]
    
    # Parse statement
    try:
        parsed_data = parser.parse(statement.file, file_type=file_type)
        features = parsed_data["features"]
    except Exception as e:
        logger.error(f"Error parsing statement: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to parse statement: {str(e)}")
        
    # Enhance applicant features
    # If salary is detected, trust the bank statement's income more
    income_verified = False
    if features["salary_detected"]:
        app_input.annual_income = features["monthly_income_actual"] * 12
        income_verified = True
        
    # Rerun the scoring pipeline with updated features
    enhanced_response = await fraud_check_with_score(app_input, registry)
    enhanced_score = enhanced_response["credit_score"]["scoreseva_score"]
    
    enhanced_response["statement_enhancement"] = {
        "income_verified": income_verified,
        "score_delta": enhanced_score - baseline_score,
        "reliability_boost": "HIGH" if features["salary_detected"] else "MEDIUM",
        "features_added": len(features)
    }
    
    return enhanced_response

from fastapi.responses import FileResponse
import os

@router.get("/demo/{persona_name}")
async def get_demo_statement(persona_name: str):
    valid_personas = ["ramesh", "priya", "vikram", "suresh", "arjun"]
    if persona_name not in valid_personas:
        raise HTTPException(status_code=404, detail="Demo persona not found")
        
    file_path = os.path.join("demo_data", "statements", f"{persona_name}_statement.csv")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Demo statement file not found")
        
    return FileResponse(
        path=file_path,
        media_type="text/csv",
        filename=f"{persona_name}_statement.csv"
    )
