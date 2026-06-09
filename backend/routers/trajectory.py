"""
trajectory.py
Score trajectory and recommendations endpoint for ScoreSeva API.

POST /trajectory
  - Accepts full applicant profile (ApplicantInput schema)
  - Builds feature row matching Phase 1E training format
  - Runs Gradient Boosting Regressor to predict T+12 improved score
  - Simulates T+6, T+12, T+24 under natural and improvement scenarios
  - Generates top 3 personalized action recommendations
  - Returns full roadmap with score timeline and actions
"""

import logging
import pandas as pd
import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from schemas.applicant import (
    ApplicantInput,
    TrajectoryResponse,
    TrajectoryPoint,
    Recommendation,
)
from models.model_loader import get_registry, ModelRegistry

logger = logging.getLogger("scoreseva.trajectory")

router = APIRouter(prefix="/trajectory", tags=["Score Trajectory"])


# ── Helper: convert applicant input to current ScoreSeva score ────────

def estimate_current_score(applicant: ApplicantInput) -> int:
    """
    Compute a weighted composite ScoreSeva score from the
    applicant's current feature values.
    Mirrors the composite score formula from Phase 1A Cell 9.
    Used as the baseline for trajectory simulation.
    """
    ext_avg = (
        applicant.ext_credit_score_1 +
        applicant.ext_credit_score_2 +
        applicant.ext_credit_score_3
    ) / 3

    upi_norm   = applicant.upi_consistency_score / 100
    phone_norm = applicant.phone_bill_regularity / 100
    geo_norm   = applicant.geo_stability_score / 100
    ecom_norm  = applicant.ecommerce_payment_score / 100
    social_norm = 1 - applicant.social_network_risk

    emp_score = min(applicant.employment_years / 10, 1.0)
    enquiry_penalty = min(
        applicant.credit_enquiries_last_year / 10, 1.0
    ) * 0.1

    raw = (
        ext_avg     * 0.30 +
        upi_norm    * 0.15 +
        phone_norm  * 0.12 +
        geo_norm    * 0.10 +
        ecom_norm   * 0.08 +
        social_norm * 0.10 +
        emp_score   * 0.15 -
        enquiry_penalty
    )

    score = int(300 + (raw * 600))
    return max(300, min(900, score))


# ── Helper: build feature row for trajectory model ────────────────────

def build_trajectory_features(
    applicant: ApplicantInput,
    current_score: int,
    feature_columns: list,
) -> pd.DataFrame:
    """
    Build a single-row DataFrame matching the exact feature set
    used to train the Gradient Boosting Regressor in Phase 1E.

    Args:
        applicant:       Validated API input
        current_score:   Computed composite ScoreSeva score
        feature_columns: Ordered list from trajectory_pipeline

    Returns:
        Single-row DataFrame ready for model.predict()
    """

    loan_to_income = (
        applicant.loan_amount / (applicant.annual_income + 1)
    )

    raw = {
        "scoreseva_score":            float(current_score),
        "upi_consistency_score":      applicant.upi_consistency_score,
        "phone_bill_regularity":      applicant.phone_bill_regularity,
        "geo_stability_score":        applicant.geo_stability_score,
        "app_usage_score":            applicant.app_usage_score,
        "social_network_risk":        applicant.social_network_risk,
        "ext_credit_score_2":         applicant.ext_credit_score_2,
        "employment_years":           applicant.employment_years,
        "id_stability_years":         applicant.id_stability_years,
        "age_years":                  float(applicant.age_years),
        "annual_income":              applicant.annual_income,
        "loan_to_income_ratio":       loan_to_income,
        "credit_enquiries_last_year": float(
            applicant.credit_enquiries_last_year
        ),
        "num_children":               float(applicant.num_children),
        "owns_property":              float(int(applicant.owns_property)),
    }

    row = {col: raw.get(col, 0.0) for col in feature_columns}
    df  = pd.DataFrame([row])[feature_columns].fillna(0)
    return df


# ── Helper: simulate trajectory at a given timeframe ─────────────────

def simulate_trajectory(
    applicant: ApplicantInput,
    current_score: int,
    months: int,
    improvement: bool,
) -> int:
    """
    Simulate score change over N months.
    Mirrors the simulation logic from Phase 1E Cell 4.

    Args:
        applicant:     Full applicant profile
        current_score: Starting ScoreSeva score
        months:        6, 12, or 24
        improvement:   True = with actions, False = natural drift

    Returns:
        Predicted future score (300-900)
    """

    loan_to_income = applicant.loan_amount / (applicant.annual_income + 1)

    # Natural drift factors
    employment_drift = min(applicant.employment_years / 10, 1.0) * 0.3
    age_factor       = min(applicant.age_years / 50, 1.0) * 0.2
    debt_drag        = loan_to_income * -0.5
    enquiry_drag     = applicant.credit_enquiries_last_year * -2.0

    monthly_natural = (
        employment_drift + age_factor + debt_drag + enquiry_drag
    ) * (months / 12)

    if not improvement:
        noise        = np.random.normal(0, 5)
        future_score = current_score + monthly_natural + noise

    else:
        # Improvement action boosts
        phone_gap   = max(0.0, 85 - applicant.phone_bill_regularity)
        phone_boost = (phone_gap / 100) * 40 * (months / 12)

        upi_gap   = max(0.0, 80 - applicant.upi_consistency_score)
        upi_boost = (upi_gap / 100) * 35 * (months / 12)

        geo_gap   = max(0.0, 75 - applicant.geo_stability_score)
        geo_boost = (geo_gap / 100) * 25 * (months / 12)

        enquiry_improvement = (
            applicant.credit_enquiries_last_year * 3.0
        )
        social_improvement  = (
            applicant.social_network_risk * 10 * (months / 24)
        )

        total_boost = (
            phone_boost + upi_boost + geo_boost +
            enquiry_improvement + social_improvement
        )

        # Diminishing returns as score approaches 900
        headroom       = max(0.0, 900 - current_score)
        effective_boost = total_boost * (headroom / 600)

        noise        = np.random.normal(0, 3)
        future_score = (
            current_score + monthly_natural + effective_boost + noise
        )

    return int(np.clip(round(future_score), 300, 900))


# ── Helper: generate personalized recommendations ─────────────────────

def generate_recommendations(
    applicant: ApplicantInput,
) -> list[Recommendation]:
    """
    Identify the applicant's weakest signals and return top 3
    personalized improvement actions sorted by impact.
    Mirrors the logic from Phase 1E Cell 7.
    """

    actions = []

    # UPI consistency
    upi_gap = max(0.0, 80 - applicant.upi_consistency_score)
    if upi_gap > 15:
        actions.append((
            upi_gap,
            Recommendation(
                action="Use UPI for all daily payments consistently",
                current=f"{applicant.upi_consistency_score:.0f}/100",
                target="80+/100",
                score_impact=f"+{round(upi_gap * 0.35)} points",
                timeframe="3-6 months",
            )
        ))

    # Phone bill regularity
    phone_gap = max(0.0, 85 - applicant.phone_bill_regularity)
    if phone_gap > 10:
        actions.append((
            phone_gap,
            Recommendation(
                action="Set auto-pay for phone and utility bills",
                current=f"{applicant.phone_bill_regularity:.0f}/100",
                target="85+/100",
                score_impact=f"+{round(phone_gap * 0.30)} points",
                timeframe="2-4 months",
            )
        ))

    # Credit enquiries
    if applicant.credit_enquiries_last_year >= 3:
        impact = applicant.credit_enquiries_last_year * 3
        actions.append((
            applicant.credit_enquiries_last_year * 5,
            Recommendation(
                action="Stop applying for new loans for 6 months",
                current=f"{applicant.credit_enquiries_last_year} enquiries",
                target="0-1 enquiries",
                score_impact=f"+{impact} points",
                timeframe="6 months",
            )
        ))

    # Geo stability
    geo_gap = max(0.0, 75 - applicant.geo_stability_score)
    if geo_gap > 20:
        actions.append((
            geo_gap * 0.8,
            Recommendation(
                action="Maintain stable home and work location",
                current=f"{applicant.geo_stability_score:.0f}/100",
                target="75+/100",
                score_impact=f"+{round(geo_gap * 0.20)} points",
                timeframe="6-12 months",
            )
        ))

    # Social network risk
    if applicant.social_network_risk > 0.40:
        impact = round(applicant.social_network_risk * 15)
        actions.append((
            applicant.social_network_risk * 30,
            Recommendation(
                action=(
                    "Reduce guarantor relationships "
                    "with high-risk contacts"
                ),
                current=f"{applicant.social_network_risk:.2f} risk score",
                target="< 0.25 risk score",
                score_impact=f"+{impact} points",
                timeframe="12-18 months",
            )
        ))

    # App usage
    app_gap = max(0.0, 70 - applicant.app_usage_score)
    if app_gap > 20:
        actions.append((
            app_gap * 0.6,
            Recommendation(
                action=(
                    "Use ScoreSeva app regularly "
                    "to build digital profile"
                ),
                current=f"{applicant.app_usage_score:.0f}/100",
                target="70+/100",
                score_impact=f"+{round(app_gap * 0.15)} points",
                timeframe="1-3 months",
            )
        ))

    # Sort by priority descending, return top 3
    actions.sort(key=lambda x: x[0], reverse=True)
    return [rec for _, rec in actions[:3]]


# ── Main trajectory endpoint ──────────────────────────────────────────

@router.post(
    "/",
    response_model=TrajectoryResponse,
    summary="Predict score trajectory and get improvement roadmap",
    description="""
Submit a full applicant profile and receive:
- **Current ScoreSeva score** (composite estimate)
- **Score trajectory** at T+6, T+12, T+24 months
  under natural drift and with improvement actions
- **Top 3 personalized recommendations** with estimated
  score impact and timeframe for each action
- **Total 24-month potential gain** in score points

This is the feature that turns a loan rejection into
an empowerment roadmap. No credit bureau in India
offers this today.
    """,
)
async def get_trajectory(
    applicant: ApplicantInput,
    registry: ModelRegistry = Depends(get_registry),
) -> TrajectoryResponse:
    """
    Score trajectory and personalized improvement roadmap.
    Uses GBR model from Phase 1E for T+12 prediction.
    """

    # ── Guard: check model is loaded ─────────────────────────────────
    if registry.trajectory_pipeline is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "model_not_loaded",
                "message": (
                    "Trajectory predictor is not available. "
                    "Check /health for model status."
                )
            }
        )

    trajectory_pipeline = registry.trajectory_pipeline
    feature_columns     = trajectory_pipeline["feature_cols"]
    gbr_model           = trajectory_pipeline["model"]

    # ── Compute current score ─────────────────────────────────────────
    try:
        current_score = estimate_current_score(applicant)
    except Exception as e:
        logger.error(f"Score estimation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=422,
            detail={
                "error": "score_estimation_failed",
                "message": str(e),
            }
        )

    # ── Build feature row and predict T+12 improved score ────────────
    try:
        feature_row    = build_trajectory_features(
            applicant, current_score, feature_columns
        )
        t12_improved   = int(np.clip(
            round(float(gbr_model.predict(feature_row)[0])),
            300, 900
        ))
    except Exception as e:
        logger.error(f"GBR prediction failed: {e}", exc_info=True)
        # Fallback to simulation if model fails
        t12_improved = simulate_trajectory(
            applicant, current_score, 12, improvement=True
        )

    # ── Simulate all timeframes ───────────────────────────────────────
    try:
        np.random.seed(42)  # Deterministic for consistent demo results
        t6_natural  = simulate_trajectory(
            applicant, current_score, 6,  improvement=False
        )
        t6_improved = simulate_trajectory(
            applicant, current_score, 6,  improvement=True
        )
        t12_natural = simulate_trajectory(
            applicant, current_score, 12, improvement=False
        )
        t24_natural = simulate_trajectory(
            applicant, current_score, 24, improvement=False
        )
        t24_improved = simulate_trajectory(
            applicant, current_score, 24, improvement=True
        )
    except Exception as e:
        logger.error(f"Trajectory simulation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "simulation_failed",
                "message": str(e),
            }
        )

    # ── Generate recommendations ──────────────────────────────────────
    try:
        recommendations = generate_recommendations(applicant)
    except Exception as e:
        logger.warning(f"Recommendation generation failed: {e}")
        recommendations = []

    # ── Compute total potential gain ──────────────────────────────────
    total_potential_gain = max(0, t24_improved - current_score)

    # ── Log summary ───────────────────────────────────────────────────
    logger.info(
        f"Trajectory | Current: {current_score} | "
        f"T+12 improved: {t12_improved} | "
        f"T+24 improved: {t24_improved} | "
        f"Gain: +{total_potential_gain}"
    )

    return TrajectoryResponse(
        current_score=current_score,
        trajectory={
            "T+6m":  TrajectoryPoint(
                natural=t6_natural,
                improved=t6_improved,
            ),
            "T+12m": TrajectoryPoint(
                natural=t12_natural,
                improved=t12_improved,
            ),
            "T+24m": TrajectoryPoint(
                natural=t24_natural,
                improved=t24_improved,
            ),
        },
        recommendations=recommendations,
        total_potential_gain=total_potential_gain,
    )


# ── Persona demo endpoint ─────────────────────────────────────────────

@router.get(
    "/demo/{persona_name}",
    summary="Get trajectory for a pre-built demo persona",
    description="""
Returns the pre-computed trajectory for one of the 5 hackathon
demo personas by name. Use during live demos to avoid typing.

Valid persona names:
- ramesh   (auto-rickshaw driver, score ~705)
- priya    (street vendor, score ~735)
- suresh   (kirana owner, score ~625)
- fatima   (rural woman, score ~645)
- vikram   (rejected applicant, score ~490)
    """,
)
async def get_demo_persona_trajectory(
    persona_name: str,
    registry: ModelRegistry = Depends(get_registry),
) -> dict:
    """
    Returns pre-built trajectory for a named demo persona.
    Useful for reliable, consistent hackathon demos.
    """

    PERSONAS = {
        "ramesh": ApplicantInput(
            annual_income=180000, loan_amount=50000,
            monthly_emi=2500, age_years=38, gender="M",
            employment_years=8.0, id_stability_years=3.2,
            upi_consistency_score=81.0, phone_bill_regularity=88.0,
            geo_stability_score=76.0, ecommerce_payment_score=60.0,
            social_network_risk=0.12, app_usage_score=74.0,
            ext_credit_score_1=0.55, ext_credit_score_2=0.62,
            ext_credit_score_3=0.58, credit_enquiries_last_year=0,
            num_children=2, family_size=4, region_risk_rating=2,
        ),
        "priya": ApplicantInput(
            annual_income=120000, loan_amount=30000,
            monthly_emi=1500, age_years=32, gender="F",
            employment_years=5.0, id_stability_years=4.0,
            upi_consistency_score=91.0, phone_bill_regularity=94.0,
            geo_stability_score=85.0, ecommerce_payment_score=70.0,
            social_network_risk=0.08, app_usage_score=82.0,
            ext_credit_score_1=0.48, ext_credit_score_2=0.51,
            ext_credit_score_3=0.50, credit_enquiries_last_year=0,
            num_children=1, family_size=3, region_risk_rating=2,
        ),
        "suresh": ApplicantInput(
            annual_income=240000, loan_amount=100000,
            monthly_emi=5000, age_years=45, gender="M",
            employment_years=12.0, id_stability_years=7.0,
            upi_consistency_score=65.0, phone_bill_regularity=70.0,
            geo_stability_score=88.0, ecommerce_payment_score=55.0,
            social_network_risk=0.22, app_usage_score=60.0,
            ext_credit_score_1=0.60, ext_credit_score_2=0.58,
            ext_credit_score_3=0.55, credit_enquiries_last_year=2,
            num_children=3, family_size=5, region_risk_rating=2,
        ),
        "fatima": ApplicantInput(
            annual_income=90000, loan_amount=20000,
            monthly_emi=1000, age_years=27, gender="F",
            employment_years=2.0, id_stability_years=2.5,
            upi_consistency_score=74.0, phone_bill_regularity=79.0,
            geo_stability_score=70.0, ecommerce_payment_score=45.0,
            social_network_risk=0.18, app_usage_score=65.0,
            ext_credit_score_1=0.40, ext_credit_score_2=0.42,
            ext_credit_score_3=0.38, credit_enquiries_last_year=0,
            num_children=1, family_size=4, region_risk_rating=3,
        ),
        "vikram": ApplicantInput(
            annual_income=150000, loan_amount=80000,
            monthly_emi=4000, age_years=24, gender="M",
            employment_years=1.5, id_stability_years=1.2,
            upi_consistency_score=42.0, phone_bill_regularity=38.0,
            geo_stability_score=55.0, ecommerce_payment_score=30.0,
            social_network_risk=0.45, app_usage_score=35.0,
            ext_credit_score_1=0.35, ext_credit_score_2=0.35,
            ext_credit_score_3=0.33, credit_enquiries_last_year=4,
            num_children=0, family_size=1, region_risk_rating=2,
        ),
    }

    name = persona_name.lower().strip()
    if name not in PERSONAS:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "persona_not_found",
                "message": (
                    f"Persona '{persona_name}' not found. "
                    f"Valid names: {list(PERSONAS.keys())}"
                )
            }
        )

    applicant     = PERSONAS[name]
    current_score = estimate_current_score(applicant)

    if registry.trajectory_pipeline is None:
        raise HTTPException(
            status_code=503,
            detail={"error": "model_not_loaded"}
        )

    feature_columns = registry.trajectory_pipeline["feature_cols"]
    gbr_model       = registry.trajectory_pipeline["model"]

    feature_row  = build_trajectory_features(
        applicant, current_score, feature_columns
    )
    t12_improved = int(np.clip(
        round(float(gbr_model.predict(feature_row)[0])), 300, 900
    ))

    np.random.seed(42)
    t6_nat  = simulate_trajectory(applicant, current_score, 6,  False)
    t6_imp  = simulate_trajectory(applicant, current_score, 6,  True)
    t12_nat = simulate_trajectory(applicant, current_score, 12, False)
    t24_nat = simulate_trajectory(applicant, current_score, 24, False)
    t24_imp = simulate_trajectory(applicant, current_score, 24, True)

    recs  = generate_recommendations(applicant)
    gain  = max(0, t24_imp - current_score)

    return {
        "persona":       persona_name,
        "current_score": current_score,
        "trajectory": {
            "T+6m":  {"natural": t6_nat,  "improved": t6_imp},
            "T+12m": {"natural": t12_nat, "improved": t12_improved},
            "T+24m": {"natural": t24_nat, "improved": t24_imp},
        },
        "recommendations": [r.model_dump() for r in recs],
        "total_potential_gain": gain,
    }
