"""
fraud.py
Fraud and anomaly detection endpoint for ScoreSeva API.

POST /fraud-check
  - Accepts full applicant profile (ApplicantInput schema)
  - Engineers fraud-specific inconsistency features
  - Runs Isolation Forest anomaly detection (Phase 1D model)
  - Applies rule-based red flag engine on top
  - Returns fraud score (0-100), verdict, red flags, and action
"""

import logging
import pandas as pd
import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from schemas.applicant import ApplicantInput, FraudResponse
from models.model_loader import get_registry, ModelRegistry

logger = logging.getLogger("scoreseva.fraud")

router = APIRouter(prefix="/fraud-check", tags=["Fraud Detection"])


# ── Helper: engineer fraud-specific features ─────────────────────────

def build_fraud_features(
    applicant: ApplicantInput,
    fraud_pipeline: dict,
) -> pd.DataFrame:
    """
    Engineer the same 13 fraud-specific inconsistency features
    that were used to train the Isolation Forest in Phase 1D.

    Args:
        applicant:       Validated input from API request
        fraud_pipeline:  Loaded fraud pipeline dict containing
                         isolation_forest, scaler, feature_cols,
                         score_min, score_max

    Returns:
        Single-row DataFrame scaled and ready for inference
    """

    # Reference stats needed for normalization
    # These are approximate medians from the training dataset
    INCOME_MAX    = 3_000_000.0
    LOAN_MAX      = 4_000_000.0
    INCOME_MEDIAN = 180_000.0

    annual_income  = float(applicant.annual_income)
    loan_amount    = float(applicant.loan_amount)
    monthly_emi    = float(applicant.monthly_emi)
    employment_yrs = float(applicant.employment_years)
    id_stability   = float(applicant.id_stability_years)
    geo_score      = float(applicant.geo_stability_score)
    upi_score      = float(applicant.upi_consistency_score)
    phone_score    = float(applicant.phone_bill_regularity)
    app_score      = float(applicant.app_usage_score)
    social_risk    = float(applicant.social_network_risk)
    ext_score_2    = float(applicant.ext_credit_score_2)
    enquiries      = float(applicant.credit_enquiries_last_year)

    # ── Compute engineered features (mirrors Phase 1D Cell 4) ────────

    # 1. Income vs digital behavior mismatch
    income_upi_mismatch = (
        (annual_income / (INCOME_MAX + 1)) -
        (upi_score / 100)
    )

    # 2. Loan-to-income ratio
    loan_to_income_ratio = loan_amount / (annual_income + 1)

    # 3. EMI affordability stress
    monthly_income = annual_income / 12
    emi_stress_ratio = monthly_emi / (monthly_income + 1)

    # 4. Identity instability
    identity_instability = (
        (1 / (id_stability + 0.1)) *
        (1 - geo_score / 100)
    )

    # 5. Credit hunger index
    credit_hunger_index = enquiries * (1 - ext_score_2)

    # 6. Social risk amplified
    social_risk_amplified = (
        social_risk * (loan_amount / (LOAN_MAX + 1))
    )

    # 7. Digital consistency index
    digital_consistency_index = (
        (upi_score + phone_score + geo_score + app_score) / 400
    )

    # 8. Employment-income plausibility
    employment_income_plausibility = min(
        employment_yrs /
        (annual_income / (INCOME_MEDIAN + 1) + 0.1),
        10.0
    )

    raw = {
        "income_upi_mismatch":              income_upi_mismatch,
        "loan_to_income_ratio":             loan_to_income_ratio,
        "emi_stress_ratio":                 emi_stress_ratio,
        "identity_instability":             identity_instability,
        "credit_hunger_index":              credit_hunger_index,
        "social_risk_amplified":            social_risk_amplified,
        "digital_consistency_index":        digital_consistency_index,
        "employment_income_plausibility":   employment_income_plausibility,
        "credit_enquiries_last_year":       enquiries,
        "social_network_risk":              social_risk,
        "geo_stability_score":              geo_score,
        "upi_consistency_score":            upi_score,
        "ext_credit_score_2":               ext_score_2,
    }

    feature_cols = fraud_pipeline["feature_cols"]
    df = pd.DataFrame(
        [[raw.get(col, 0.0) for col in feature_cols]],
        columns=feature_cols
    ).fillna(0)

    # Scale using the scaler fitted during Phase 1D training
    scaled = fraud_pipeline["scaler"].transform(df)
    df_scaled = pd.DataFrame(scaled, columns=feature_cols)

    return df_scaled, raw


# ── Helper: rule-based red flag engine ───────────────────────────────

def apply_red_flag_rules(
    applicant: ApplicantInput,
    derived: dict,
) -> tuple[list[str], int]:
    """
    Apply the same 8 hard rules from Phase 1D.
    Returns (list_of_triggered_flags, total_penalty_score).
    """

    flags   = []
    penalty = 0

    loan_to_income = derived["loan_to_income_ratio"]
    digital_idx    = derived["digital_consistency_index"]

    # Rule 1: Loan > 5x annual income
    if loan_to_income > 5:
        flags.append("LOAN_EXCEEDS_5X_INCOME")
        penalty += 25

    # Rule 2: Excessive recent credit enquiries
    if applicant.credit_enquiries_last_year >= 6:
        flags.append("EXCESSIVE_CREDIT_ENQUIRIES")
        penalty += 20

    # Rule 3: Geo instability + high loan
    if (applicant.geo_stability_score < 25 and
            loan_to_income > 1.5):
        flags.append("GEO_INSTABILITY_HIGH_LOAN")
        penalty += 20

    # Rule 4: High social network risk
    if applicant.social_network_risk > 0.60:
        flags.append("HIGH_SOCIAL_NETWORK_RISK")
        penalty += 15

    # Rule 5: Very recently changed ID
    if applicant.id_stability_years < 0.5:
        flags.append("RECENT_ID_CHANGE")
        penalty += 15

    # Rule 6: Very poor digital footprint
    if digital_idx < 0.30:
        flags.append("POOR_DIGITAL_FOOTPRINT")
        penalty += 15

    # Rule 7: High income claimed but very low digital usage
    if (applicant.annual_income > 400_000 and
            applicant.upi_consistency_score < 35):
        flags.append("INCOME_DIGITAL_MISMATCH")
        penalty += 20

    # Rule 8: Very short employment + very high income
    if (applicant.employment_years < 1 and
            applicant.annual_income > 500_000):
        flags.append("SHORT_EMPLOYMENT_HIGH_INCOME")
        penalty += 15

    return flags, min(penalty, 100)


# ── Helper: verdict from score and flag count ─────────────────────────

def get_fraud_verdict(
    score: float,
    flag_count: int,
) -> tuple[str, str, str]:
    """
    Returns (verdict_label, action_string, hex_color).
    Mirrors the logic from Phase 1D Cell 7.
    """
    if score >= 70 or flag_count >= 4:
        return (
            "HIGH FRAUD RISK",
            "BLOCK — Manual review required",
            "#EF4444",
        )
    elif score >= 45 or flag_count >= 2:
        return (
            "MODERATE FRAUD RISK",
            "FLAG — Additional verification needed",
            "#F59E0B",
        )
    else:
        return (
            "LOW FRAUD RISK",
            "PROCEED — Normal processing",
            "#22C55E",
        )


# ── Main fraud check endpoint ─────────────────────────────────────────

@router.post(
    "/",
    response_model=FraudResponse,
    summary="Check an applicant for fraud and anomalies",
    description="""
Submit a full applicant profile and receive:
- **Fraud score** (0-100, higher = more suspicious)
- **Isolation Forest anomaly risk** (statistical outlier score)
- **Rule-based penalty** (domain knowledge red flags)
- **Red flags triggered** (specific rule violations)
- **Verdict** with recommended action (BLOCK / FLAG / PROCEED)

Combines unsupervised ML anomaly detection with 8 hard
rule checks to catch both known and unknown fraud patterns.
    """,
)
async def fraud_check(
    applicant: ApplicantInput,
    registry: ModelRegistry = Depends(get_registry),
) -> FraudResponse:
    """
    Fraud and anomaly detection endpoint.
    Runs Isolation Forest + rule engine from Phase 1D.
    """

    # ── Guard: check model is loaded ─────────────────────────────────
    if registry.fraud_pipeline is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "model_not_loaded",
                "message": (
                    "Fraud detection model is not available. "
                    "Check /health for model status."
                )
            }
        )

    fraud_pipeline = registry.fraud_pipeline

    # ── Engineer features ─────────────────────────────────────────────
    try:
        df_scaled, derived = build_fraud_features(
            applicant=applicant,
            fraud_pipeline=fraud_pipeline,
        )
    except Exception as e:
        logger.error(
            f"Fraud feature engineering failed: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=422,
            detail={
                "error": "feature_engineering_failed",
                "message": str(e),
            }
        )

    # ── Run Isolation Forest inference ────────────────────────────────
    try:
        iso_forest  = fraud_pipeline["isolation_forest"]
        score_min   = fraud_pipeline["score_min"]
        score_max   = fraud_pipeline["score_max"]

        raw_score   = float(iso_forest.decision_function(df_scaled)[0])

        # Normalize to 0-100 (more negative raw = higher fraud risk)
        isolation_risk = float(np.clip(
            (1 - (raw_score - score_min) / (score_max - score_min + 1e-9))
            * 100,
            0, 100
        ))

    except Exception as e:
        logger.error(f"Isolation Forest inference failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "inference_failed",
                "message": str(e),
            }
        )

    # ── Apply rule-based red flags ────────────────────────────────────
    try:
        red_flags, rule_penalty = apply_red_flag_rules(
            applicant=applicant,
            derived=derived,
        )
    except Exception as e:
        logger.error(f"Rule engine failed: {e}", exc_info=True)
        red_flags    = []
        rule_penalty = 0

    # ── Compute final fraud score ─────────────────────────────────────
    final_fraud_score = float(np.clip(
        isolation_risk * 0.60 + rule_penalty * 0.40,
        0, 100
    ))

    # ── Get verdict ───────────────────────────────────────────────────
    verdict, action, color = get_fraud_verdict(
        score=final_fraud_score,
        flag_count=len(red_flags),
    )

    # ── Log summary ───────────────────────────────────────────────────
    logger.info(
        f"Fraud score: {final_fraud_score:.1f} | "
        f"Verdict: {verdict} | "
        f"Flags: {len(red_flags)} | "
        f"Rules: {red_flags}"
    )

    return FraudResponse(
        fraud_score=round(final_fraud_score, 1),
        isolation_risk=round(isolation_risk, 1),
        rule_penalty=float(rule_penalty),
        red_flags=red_flags,
        red_flag_count=len(red_flags),
        verdict=verdict,
        action=action,
        color=color,
    )


# ── Combined score + fraud endpoint ──────────────────────────────────

@router.post(
    "/with-score",
    summary="Fraud check combined with credit score",
    description="""
Convenience endpoint that runs BOTH the credit scorer (Phase 2B)
and the fraud detector in a single request.
Returns both results together — ideal for the frontend dashboard.
    """,
)
async def fraud_check_with_score(
    applicant: ApplicantInput,
    registry: ModelRegistry = Depends(get_registry),
) -> dict:
    """
    Combined endpoint — runs scoring + fraud check together.
    Returns merged response with both results.
    """

    # ── Guard ─────────────────────────────────────────────────────────
    if registry.fraud_pipeline is None or registry.xgboost_model is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "models_not_loaded",
                "message": "One or more models unavailable. Check /health."
            }
        )

    # ── Run fraud check ───────────────────────────────────────────────
    df_scaled, derived = build_fraud_features(applicant, registry.fraud_pipeline)

    iso_forest  = registry.fraud_pipeline["isolation_forest"]
    score_min   = registry.fraud_pipeline["score_min"]
    score_max   = registry.fraud_pipeline["score_max"]
    raw_score   = float(iso_forest.decision_function(df_scaled)[0])
    isolation_risk = float(np.clip(
        (1 - (raw_score - score_min) /
         (score_max - score_min + 1e-9)) * 100,
        0, 100
    ))
    red_flags, rule_penalty = apply_red_flag_rules(applicant, derived)
    fraud_score = float(np.clip(
        isolation_risk * 0.60 + rule_penalty * 0.40, 0, 100
    ))
    verdict, action, color = get_fraud_verdict(fraud_score, len(red_flags))

    # ── Run credit score ──────────────────────────────────────────────
    # Import inline to avoid circular imports
    from routers.scoring import (
        build_feature_row,
        probability_to_score,
        get_risk_band,
        extract_top_factors,
    )

    feature_row  = build_feature_row(
        applicant, registry.feature_columns, registry.label_encoders
    )
    default_prob = float(
        registry.xgboost_model.predict_proba(feature_row)[0][1]
    )
    score        = probability_to_score(default_prob)
    risk_band    = get_risk_band(score)
    top_pos, top_neg = extract_top_factors(
        feature_row, registry.xgboost_model, registry.feature_columns
    )

    logger.info(
        f"Combined check — Score: {score} | "
        f"Fraud: {fraud_score:.1f} | Verdict: {verdict}"
    )

    return {
        "credit_score": {
            "scoreseva_score":      score,
            "default_probability":  round(default_prob, 4),
            "band":                 risk_band.band,
            "recommendation":       risk_band.recommendation,
            "suggested_rate":       risk_band.suggested_rate,
            "top_positive_factors": top_pos,
            "top_negative_factors": top_neg,
        },
        "fraud_check": {
            "fraud_score":    round(fraud_score, 1),
            "isolation_risk": round(isolation_risk, 1),
            "rule_penalty":   float(rule_penalty),
            "red_flags":      red_flags,
            "red_flag_count": len(red_flags),
            "verdict":        verdict,
            "action":         action,
            "color":          color,
        },
        "combined_recommendation": (
            "BLOCK"   if verdict == "HIGH FRAUD RISK" else
            "REVIEW"  if verdict == "MODERATE FRAUD RISK" else
            risk_band.recommendation
        )
    }
