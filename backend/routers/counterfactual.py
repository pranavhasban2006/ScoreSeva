import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

from models.model_loader import get_registry, ModelRegistry
from explainability.counterfactual import find_counterfactual
from schemas.applicant import ApplicantInput

logger = logging.getLogger("scoreseva.counterfactual")

router = APIRouter(prefix="/counterfactual", tags=["Counterfactual"])

class CounterfactualRequest(BaseModel):
    applicant_features: Dict[str, Any]
    current_score: int
    decision: str
    shap_values: Dict[str, float]


@router.post("/explain")
async def explain_counterfactual(
    req: CounterfactualRequest,
    registry: ModelRegistry = Depends(get_registry)
):
    """
    Generates a counterfactual explanation showing the minimal actionable changes
    required to reach an approval.
    """
    if registry.xgboost_model is None:
        raise HTTPException(status_code=503, detail="Scoring model not loaded")
        
    def real_scoring_wrapper(features: dict) -> int:
        """
        Wraps the XGBoost pipeline. Since Bank Statement features (like bounce_count) 
        are not native to the XGBoost schema, we interpolate them to emulate the 
        final blended score that the system computes.
        """
        try:
            # 1. Base Score via XGBoost
            from routers.scoring import build_feature_row, probability_to_score
            
            # Map features back to ApplicantInput structure
            app_dict = {}
            for field, field_info in ApplicantInput.model_fields.items():
                if field in features:
                    app_dict[field] = features[field]
                elif field_info.default is not None and field_info.default.__class__.__name__ != 'PydanticUndefinedType':
                    app_dict[field] = field_info.default
                    
            # Set required dummy values if missing
            app_dict.setdefault("annual_income", 180000)
            app_dict.setdefault("loan_amount", 50000)
            app_dict.setdefault("monthly_emi", 2500)
            app_dict.setdefault("age_years", 30)
            app_dict.setdefault("gender", "M")
            app_dict.setdefault("employment_years", 5.0)
            
            app_input = ApplicantInput(**app_dict)
            
            row = build_feature_row(app_input, registry.feature_columns, registry.label_encoders)
            prob = float(registry.xgboost_model.predict_proba(row)[0][1])
            base_score = probability_to_score(prob)
            
            # 2. Interpolate Bank Statement & Augmentation features
            score = base_score
            if "bounce_count" in features:
                score -= features["bounce_count"] * 20
            if "income_regularity_score" in features:
                # Assuming 50 is baseline
                score += (features["income_regularity_score"] - 50) * 1
            if "savings_rate" in features:
                score += features["savings_rate"] * 1.5
            if "emi_obligation_ratio" in features:
                score -= features["emi_obligation_ratio"] * 0.8
            if "cash_withdrawal_ratio" in features:
                score -= features["cash_withdrawal_ratio"] * 0.5
            if "credit_utilization_ratio" in features:
                score -= features["credit_utilization_ratio"] * 1.2
            if "hidden_emi_count" in features:
                score -= features["hidden_emi_count"] * 25
                
            return int(max(300, min(900, score)))
            
        except Exception as e:
            logger.error(f"Wrapper scoring failed: {e}")
            return req.current_score

    try:
        result = find_counterfactual(
            applicant_features=req.applicant_features,
            current_score=req.current_score,
            decision=req.decision,
            shap_values=req.shap_values,
            scoring_function=real_scoring_wrapper,
            approval_threshold=650
        )
        return result
        
    except Exception as e:
        logger.error(f"Counterfactual search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
