from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any

from parsers.cibil_parser import parse_cibil_report
from scoring.cibil_augmentation import augment_with_cibil
from routers.fraud import fraud_check_with_score
from models.model_loader import get_registry
from schemas.applicant import ApplicantInput
from demo_data.cibil_profiles import DEMO_CIBIL_PROFILES

router = APIRouter(prefix="/cibil", tags=["CIBIL Augmentation"])

class ParseCibilRequest(BaseModel):
    data: Dict[str, Any]
    source: str

class AugmentedScoreRequest(BaseModel):
    applicant: ApplicantInput
    cibil_data: Dict[str, Any]
    cibil_source: str

@router.post("/parse")
async def parse_cibil(req: ParseCibilRequest):
    """
    Parses a CIBIL report (JSON or manual entry) into 10 key features.
    """
    try:
        features = parse_cibil_report(req.data, req.source)
        return {"features": features}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CIBIL data: {str(e)}")

@router.post("/score-augmented")
async def score_augmented(req: AugmentedScoreRequest):
    """
    Scores an applicant using both alternative data and CIBIL data.
    """
    try:
        # 1. Parse CIBIL
        cibil_features = parse_cibil_report(req.cibil_data, req.cibil_source)
        
        # 2. Get base applicant features (we can extract some basic ones for augmentation logic)
        # e.g., if we had a financial_stress_score, we'd pull it. 
        # We will pass the applicant dict.
        applicant_dict = req.applicant.dict()
        
        # 3. Get augmentation logic
        augmentation = augment_with_cibil(applicant_dict, cibil_features)
        
        # 4. Get base ScoreSeva score and fraud check (Alternative Data)
        base_result = await fraud_check_with_score(req.applicant, get_registry())
        
        base_score = base_result["credit_score"]["scoreseva_score"]
        cibil_score = cibil_features.get("cibil_score")
        
        # 5. Blend scores based on weights
        alt_weight = augmentation["alt_data_weight"]
        cibil_weight = augmentation["cibil_weight"]
        
        if cibil_score:
            final_score = int((base_score * alt_weight) + (cibil_score * cibil_weight))
            bureau_only_score = cibil_score
            alt_points = int(base_score * alt_weight)
            cibil_points = int(cibil_score * cibil_weight)
        else:
            final_score = base_score
            bureau_only_score = None
            alt_points = base_score
            cibil_points = 0
            
        augmentation["alt_data_contribution_points"] = alt_points
        augmentation["cibil_contribution_points"] = cibil_points
        
        # 6. Generate verdict string
        verdict = ""
        score_diff = None
        if bureau_only_score is None:
            verdict = f"ScoreSeva surfaces {final_score} points of creditworthiness invisible to bureau-only scoring"
        else:
            score_diff = final_score - bureau_only_score
            if score_diff > 50:
                verdict = f"ScoreSeva adds {score_diff} points by considering alternative data (bureau score was dragging them down)"
            elif score_diff < -50:
                verdict = f"ScoreSeva caught {abs(score_diff)} points of hidden risk not reflected in the bureau score"
            else:
                verdict = "Alternative data aligns with bureau data, providing high confidence in the final score"

        # Construct final response
        return {
            "final_score": final_score,
            "cibil_features": cibil_features,
            "augmentation": augmentation,
            "score_breakdown": {
                "from_bureau_data": cibil_points,
                "from_alternative_data": alt_points
            },
            "comparison": {
                "bureau_only_score_estimate": bureau_only_score,
                "scoreseva_score": final_score,
                "score_difference": score_diff,
                "verdict": verdict
            },
            "base_score_result": base_result # Include the original score breakdown for the UI if needed
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Augmented scoring failed: {str(e)}")

@router.get("/demo/{persona_name}")
async def get_demo_cibil(persona_name: str):
    """
    Returns a mock CIBIL report for a given persona.
    """
    profile = DEMO_CIBIL_PROFILES.get(persona_name.lower())
    if not profile:
        raise HTTPException(status_code=404, detail="Persona not found in CIBIL demo data")
    return profile
