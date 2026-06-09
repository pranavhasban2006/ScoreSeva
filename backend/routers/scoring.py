"""
scoring.py
Core credit scoring endpoint for ScoreSeva API.

POST /score
  - Accepts full applicant profile (ApplicantInput schema)
  - Preprocesses features to match Phase 1B XGBoost training format
  - Runs XGBoost inference
  - Converts default probability → ScoreSeva score (300-900)
  - Returns score, risk band, and top influencing factors
"""

import logging
import pandas as pd
import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from schemas.applicant import ApplicantInput, ScoreResponse, RiskBand
from models.model_loader import get_registry, ModelRegistry

logger = logging.getLogger("scoreseva.scoring")

router = APIRouter(prefix="/score", tags=["Credit Scoring"])


# ── Helper: build feature dataframe from applicant input ─────────────

def build_feature_row(
    applicant: ApplicantInput,
    feature_columns: list,
    label_encoders: dict,
) -> pd.DataFrame:
    """
    Convert ApplicantInput Pydantic model into a single-row DataFrame
    that exactly matches the feature set the XGBoost model was
    trained on in Phase 1B.

    Args:
        applicant:       Validated input from API request
        feature_columns: Ordered list of feature names from training
        label_encoders:  Dict of LabelEncoder objects per categorical col

    Returns:
        Single-row DataFrame ready for model.predict_proba()
    """

    # Build raw feature dict matching training column names
    raw = {
        "annual_income":               applicant.annual_income,
        "loan_amount":                 applicant.loan_amount,
        "monthly_emi":                 applicant.monthly_emi,
        "age_years":                   applicant.age_years,
        "employment_years":            applicant.employment_years,
        "id_stability_years":          applicant.id_stability_years,
        "owns_car":                    int(applicant.owns_car),
        "owns_property":               int(applicant.owns_property),
        "num_children":                applicant.num_children,
        "family_size":                 applicant.family_size,
        "region_risk_rating":          applicant.region_risk_rating,
        "credit_enquiries_last_year":  applicant.credit_enquiries_last_year,
        "ext_credit_score_1":          applicant.ext_credit_score_1,
        "ext_credit_score_2":          applicant.ext_credit_score_2,
        "ext_credit_score_3":          applicant.ext_credit_score_3,
        "upi_consistency_score":       applicant.upi_consistency_score,
        "phone_bill_regularity":       applicant.phone_bill_regularity,
        "geo_stability_score":         applicant.geo_stability_score,
        "ecommerce_payment_score":     applicant.ecommerce_payment_score,
        "social_network_risk":         applicant.social_network_risk,
        "app_usage_score":             applicant.app_usage_score,
        # Categoricals — will be label encoded below
        "gender":                      applicant.gender.value,
        "education_level":             applicant.education_level.value,
        "occupation":                  applicant.occupation or "Unknown",
        "income_source":               applicant.income_source.value,
        "family_status":               applicant.family_status.value,
    }

    # Apply label encoders for categorical columns
    CATEGORICAL_COLS = [
        "gender", "education_level", "occupation",
        "income_source", "family_status"
    ]

    for col in CATEGORICAL_COLS:
        if col in label_encoders and col in raw:
            le = label_encoders[col]
            val = str(raw[col])
            # Handle unseen labels gracefully
            if val in le.classes_:
                raw[col] = int(le.transform([val])[0])
            else:
                # Default to most frequent class (index 0)
                logger.warning(
                    f"Unseen label '{val}' for '{col}' "
                    f"— defaulting to 0"
                )
                raw[col] = 0

    # Build DataFrame with exact column order from training
    row_dict = {col: raw.get(col, 0) for col in feature_columns}
    df = pd.DataFrame([row_dict])[feature_columns]

    return df


# ── Helper: probability → ScoreSeva score ────────────────────────────

def probability_to_score(default_prob: float) -> int:
    """Convert default probability to 300-900 ScoreSeva score."""
    repayment_prob = 1.0 - default_prob
    score = int(300 + (repayment_prob * 600))
    return max(300, min(900, score))


# ── Helper: score → risk band ─────────────────────────────────────────

def get_risk_band(score: int) -> RiskBand:
    """Return full risk band object for a given ScoreSeva score."""
    if score >= 750:
        return RiskBand(
            band="EXCELLENT",
            color="#22C55E",
            label="Very Low Risk",
            recommendation="Approve — competitive rate eligible",
            suggested_rate="8-10% p.a."
        )
    elif score >= 650:
        return RiskBand(
            band="GOOD",
            color="#84CC16",
            label="Low Risk",
            recommendation="Approve — standard rate",
            suggested_rate="10-13% p.a."
        )
    elif score >= 550:
        return RiskBand(
            band="FAIR",
            color="#F59E0B",
            label="Moderate Risk",
            recommendation="Approve with conditions",
            suggested_rate="13-18% p.a."
        )
    elif score >= 450:
        return RiskBand(
            band="POOR",
            color="#F97316",
            label="High Risk",
            recommendation="Decline or require guarantor",
            suggested_rate="N/A"
        )
    else:
        return RiskBand(
            band="VERY POOR",
            color="#EF4444",
            label="Very High Risk",
            recommendation="Decline",
            suggested_rate="N/A"
        )


# ── Helper: extract top positive and negative factors ────────────────

def extract_top_factors(
    feature_row: pd.DataFrame,
    model,
    feature_columns: list,
    top_n: int = 3,
) -> tuple[list[str], list[str]]:
    """
    Use XGBoost feature importances combined with feature values
    to identify the top positive and negative factors for this
    specific applicant.

    Returns:
        (top_positive_factors, top_negative_factors)
        Each is a list of human-readable strings.
    """

    # Feature importance scores from the model
    importances = model.feature_importances_
    importance_map = dict(zip(feature_columns, importances))

    # Human-readable labels for each feature
    FEATURE_LABELS = {
        "ext_credit_score_2":          "External credit history",
        "ext_credit_score_1":          "Alternative credit signal 1",
        "ext_credit_score_3":          "Alternative credit signal 3",
        "upi_consistency_score":       "UPI payment consistency",
        "phone_bill_regularity":       "Phone bill payment regularity",
        "geo_stability_score":         "Geographic stability",
        "ecommerce_payment_score":     "E-commerce payment behavior",
        "app_usage_score":             "Digital app engagement",
        "social_network_risk":         "Social network credit risk",
        "employment_years":            "Employment stability",
        "annual_income":               "Annual income level",
        "loan_amount":                 "Loan amount requested",
        "credit_enquiries_last_year":  "Recent credit enquiries",
        "age_years":                   "Applicant age",
        "owns_property":               "Property ownership",
        "id_stability_years":          "Identity document stability",
        "region_risk_rating":          "Geographic region risk",
        "num_children":                "Number of dependents",
    }

    # Thresholds for good vs bad signal per feature
    # (feature_value, is_good_if_above)
    GOOD_THRESHOLDS = {
        "ext_credit_score_2":          (0.55, True),
        "ext_credit_score_1":          (0.50, True),
        "ext_credit_score_3":          (0.50, True),
        "upi_consistency_score":       (65.0, True),
        "phone_bill_regularity":       (70.0, True),
        "geo_stability_score":         (65.0, True),
        "ecommerce_payment_score":     (55.0, True),
        "app_usage_score":             (55.0, True),
        "social_network_risk":         (0.35, False),  # lower = better
        "employment_years":            (2.0,  True),
        "credit_enquiries_last_year":  (3.0,  False),  # lower = better
        "owns_property":               (0.5,  True),
        "id_stability_years":          (1.5,  True),
    }

    row_values = feature_row.iloc[0].to_dict()

    positive_signals = []
    negative_signals = []

    for feature, (threshold, good_if_above) in GOOD_THRESHOLDS.items():
        if feature not in row_values:
            continue

        val = float(row_values[feature])
        importance = importance_map.get(feature, 0)
        label = FEATURE_LABELS.get(feature, feature)

        if good_if_above:
            is_positive = val >= threshold
        else:
            is_positive = val <= threshold

        signal = (importance, label)

        if is_positive:
            positive_signals.append(signal)
        else:
            negative_signals.append(signal)

    # Sort by importance descending and extract labels
    positive_signals.sort(key=lambda x: x[0], reverse=True)
    negative_signals.sort(key=lambda x: x[0], reverse=True)

    top_positive = [s[1] for s in positive_signals[:top_n]]
    top_negative = [s[1] for s in negative_signals[:top_n]]

    # Fallback if lists are empty
    if not top_positive:
        top_positive = ["Stable repayment capacity"]
    if not top_negative:
        top_negative = ["Limited credit history available"]

    return top_positive, top_negative


# ── Main scoring endpoint ─────────────────────────────────────────────

@router.post(
    "/",
    response_model=ScoreResponse,
    summary="Score a loan applicant",
    description="""
Submit a full applicant profile and receive:
- **ScoreSeva score** (300-900)
- **Risk band** with approval recommendation
- **Default probability** from the XGBoost model
- **Top positive factors** that helped the score
- **Top negative factors** that hurt the score

The score uses 22 features including India-specific
signals (UPI, phone bills, geolocation) that traditional
CIBIL scores ignore entirely.
    """,
)
async def score_applicant(
    applicant: ApplicantInput,
    registry: ModelRegistry = Depends(get_registry),
) -> ScoreResponse:
    """
    Core credit scoring endpoint.
    Loads XGBoost model from registry and runs inference.
    """

    # ── Guard: check models are loaded ───────────────────────────────
    if registry.xgboost_model is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "model_not_loaded",
                "message": (
                    "XGBoost scoring model is not available. "
                    "Check /health for model status."
                )
            }
        )

    if registry.feature_columns is None or registry.label_encoders is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "model_artifacts_missing",
                "message": (
                    "Feature columns or label encoders not loaded. "
                    "Check /health for model status."
                )
            }
        )

    # ── Build feature row ─────────────────────────────────────────────
    try:
        feature_row = build_feature_row(
            applicant=applicant,
            feature_columns=registry.feature_columns,
            label_encoders=registry.label_encoders,
        )
    except Exception as e:
        logger.error(f"Feature engineering failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=422,
            detail={
                "error": "feature_engineering_failed",
                "message": f"Could not build feature row: {str(e)}"
            }
        )

    # ── Run XGBoost inference ─────────────────────────────────────────
    try:
        default_prob = float(
            registry.xgboost_model.predict_proba(feature_row)[0][1]
        )
    except Exception as e:
        logger.error(f"Model inference failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "inference_failed",
                "message": f"Model prediction failed: {str(e)}"
            }
        )

    # ── Convert to ScoreSeva score and risk band ──────────────────────
    score     = probability_to_score(default_prob)
    risk_band = get_risk_band(score)

    # ── Extract top factors ───────────────────────────────────────────
    try:
        top_positive, top_negative = extract_top_factors(
            feature_row=feature_row,
            model=registry.xgboost_model,
            feature_columns=registry.feature_columns,
        )
    except Exception as e:
        logger.warning(f"Factor extraction failed: {e}")
        top_positive = ["Credit signals analyzed"]
        top_negative = ["Insufficient data for factor breakdown"]

    # ── Log summary ───────────────────────────────────────────────────
    logger.info(
        f"Score: {score} | "
        f"Default prob: {default_prob:.3f} | "
        f"Band: {risk_band.band} | "
        f"Income: {applicant.annual_income} | "
        f"UPI: {applicant.upi_consistency_score}"
    )

    return ScoreResponse(
        scoreseva_score=score,
        default_probability=round(default_prob, 4),
        risk_band=risk_band,
        top_positive_factors=top_positive,
        top_negative_factors=top_negative,
        model_version="1.0.0",
    )


# ── Batch scoring endpoint ────────────────────────────────────────────

@router.post(
    "/batch",
    summary="Score multiple applicants at once",
    description="""
Submit up to 50 applicants in one request.
Returns a list of ScoreResponse objects in the same order.
Useful for bulk NBFC processing or demo data generation.
    """,
)
async def score_batch(
    applicants: list[ApplicantInput],
    registry: ModelRegistry = Depends(get_registry),
) -> list[dict]:
    """
    Batch scoring — processes up to 50 applicants per request.
    """

    if len(applicants) > 50:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "batch_too_large",
                "message": "Maximum 50 applicants per batch request."
            }
        )

    if registry.xgboost_model is None:
        raise HTTPException(
            status_code=503,
            detail={"error": "model_not_loaded"}
        )

    results = []

    for i, applicant in enumerate(applicants):
        try:
            feature_row = build_feature_row(
                applicant=applicant,
                feature_columns=registry.feature_columns,
                label_encoders=registry.label_encoders,
            )
            default_prob = float(
                registry.xgboost_model.predict_proba(feature_row)[0][1]
            )
            score     = probability_to_score(default_prob)
            risk_band = get_risk_band(score)

            results.append({
                "index":               i,
                "scoreseva_score":     score,
                "default_probability": round(default_prob, 4),
                "band":                risk_band.band,
                "recommendation":      risk_band.recommendation,
                "status":              "success",
            })

        except Exception as e:
            logger.error(f"Batch item {i} failed: {e}")
            results.append({
                "index":  i,
                "status": "error",
                "error":  str(e),
            })

    logger.info(
        f"Batch scored {len(applicants)} applicants — "
        f"{sum(1 for r in results if r['status'] == 'success')} "
        f"succeeded"
    )

    return results
