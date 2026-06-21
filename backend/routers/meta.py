"""
meta.py
Meta and introspection endpoints for ScoreSeva API.
Provides endpoint catalogue, scoring methodology docs,
and a demo launcher — all GET endpoints for easy browser access.
"""

import time
from fastapi import APIRouter

router = APIRouter(prefix="/meta", tags=["API Meta"])

APP_START_TIME = time.time()


@router.get(
    "/endpoints",
    summary="List all ScoreSeva API endpoints",
)
async def list_endpoints() -> dict:
    """Returns a structured catalogue of all endpoints."""
    return {
        "api": "ScoreSeva API v1.0.0",
        "endpoints": [
            {
                "method": "POST", "path": "/score/",
                "description": "Full credit score + risk band",
                "key_output": "scoreseva_score (300-900), risk_band, top factors",
            },
            {
                "method": "POST", "path": "/score/batch",
                "description": "Score up to 50 applicants at once",
                "key_output": "Array of scores and bands",
            },
            {
                "method": "POST", "path": "/fraud-check/",
                "description": "Fraud and anomaly detection",
                "key_output": "fraud_score (0-100), verdict, red_flags",
            },
            {
                "method": "POST", "path": "/fraud-check/with-score",
                "description": "Credit score + fraud check combined",
                "key_output": "Both credit_score and fraud_check merged",
            },
            {
                "method": "POST", "path": "/trajectory/",
                "description": "Score roadmap at T+6/12/24 months",
                "key_output": "trajectory dict, recommendations, gain",
            },
            {
                "method": "GET", "path": "/trajectory/demo/{name}",
                "description": "Demo persona trajectory (no body needed)",
                "key_output": "Pre-built persona roadmap",
            },
            {
                "method": "POST", "path": "/nlp-score/",
                "description": "NLP psychometric analysis from free text",
                "key_output": "nlp_credit_score, signals, insights",
            },
            {
                "method": "POST", "path": "/nlp-score/quick",
                "description": "Quick single-text NLP score",
                "key_output": "nlp_score, risk_label, top_signals",
            },
            {
                "method": "GET", "path": "/nlp-score/demo/{profile}",
                "description": "Demo NLP profile (no body needed)",
                "key_output": "Pre-built NLP result",
            },
            {
                "method": "GET", "path": "/health/",
                "description": "API + model health status",
                "key_output": "status, models loaded",
            },
            {
                "method": "GET", "path": "/meta/score-methodology",
                "description": "How the ScoreSeva score is computed",
                "key_output": "Methodology documentation",
            },
            {
                "method": "POST", "path": "/bank-statement/analyze",
                "description": "Parse bank statement (PDF/CSV) and extract 15 features",
                "key_output": "statement_summary, extracted_features, income_verification",
            },
            {
                "method": "POST", "path": "/bank-statement/score-with-statement",
                "description": "Credit score enriched with parsed bank statement features",
                "key_output": "Credit score + fraud check + statement_enhancement",
            },
            {
                "method": "POST", "path": "/cibil/parse",
                "description": "Parse CIBIL report JSON or manual entry",
                "key_output": "10 extracted CIBIL features",
            },
            {
                "method": "POST", "path": "/cibil/score-augmented",
                "description": "Combine alt-data with CIBIL data for hybrid score",
                "key_output": "final_score, score_breakdown, comparison verdict",
            },
            {
                "method": "POST", "path": "/anti-gaming/score-with-gaming-check",
                "description": "Base score minus gaming penalties",
                "key_output": "final_score, penalty_applied, gaming_analysis",
            },
            {
                "method": "POST", "path": "/letters/generate",
                "description": "Generates a plain-English decision letter",
                "key_output": "letter_text, technical_appendix, decision",
            },
            {
                "method": "POST", "path": "/letters/generate-pdf",
                "description": "Generates a decision letter PDF",
                "key_output": "PDF binary",
            },
            {
                "method": "POST", "path": "/chatbot/ask",
                "description": "Grounded AI assistant for ScoreSeva",
                "key_output": "response",
            },
            {
                "method": "POST", "path": "/counterfactual/explain",
                "description": "Minimal actionable changes for approval",
                "key_output": "counterfactual_needed, changes_required, projected_score",
            },
        ],
        "demo_shortcuts": {
            "trajectory_demos": [
                "/trajectory/demo/ramesh",
                "/trajectory/demo/priya",
                "/trajectory/demo/vikram",
            ],
            "nlp_demos": [
                "/nlp-score/demo/responsible",
                "/nlp-score/demo/desperate",
            ],
        },
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }


@router.get(
    "/score-methodology",
    summary="ScoreSeva scoring methodology documentation",
)
async def score_methodology() -> dict:
    """Returns a structured explanation of the scoring model."""
    return {
        "model":       "XGBoost Gradient Boosted Trees",
        "score_range": "300 – 900 (mirrors CIBIL convention)",
        "training_data": {
            "base_dataset":    "Home Credit Default Risk (Kaggle, 307k rows)",
            "india_signals":   "Synthetic India-specific signals (50k rows)",
            "target_variable": "Binary loan default (TARGET = 1 means defaulted)",
        },
        "feature_groups": {
            "traditional_financial (30%)": [
                "annual_income", "loan_amount", "monthly_emi",
                "employment_years", "ext_credit_score_1/2/3",
                "credit_enquiries_last_year",
            ],
            "india_digital_signals (40%)": [
                "upi_consistency_score",
                "phone_bill_regularity",
                "geo_stability_score",
                "ecommerce_payment_score",
                "app_usage_score",
                "social_network_risk",
            ],
            "identity_and_assets (15%)": [
                "id_stability_years", "owns_car", "owns_property",
                "region_risk_rating",
            ],
            "demographic (15%)": [
                "age_years", "num_children", "family_size",
                "education_level", "family_status",
            ],
        },
        "risk_bands": {
            "750-900": {"band": "EXCELLENT", "action": "Approve — best rate"},
            "650-749": {"band": "GOOD",      "action": "Approve — standard rate"},
            "550-649": {"band": "FAIR",      "action": "Conditional approval"},
            "450-549": {"band": "POOR",      "action": "Decline or guarantor"},
            "300-449": {"band": "VERY POOR", "action": "Decline"},
        },
        "fairness_audit": {
            "dimensions_audited": ["gender", "age", "region", "income"],
            "standard":           "80-125% approval rate parity threshold",
            "report_path":        "data/bias_audit_report.json",
        },
        "nlp_layer": {
            "model":    "DistilBERT (sentiment) + Logistic Regression",
            "features": [
                "planning_orientation", "future_orientation",
                "urgency_flag", "responsibility_score",
                "productive_use_score", "stress_flag",
                "specificity_score", "numeric_confidence",
            ],
        },
        "fraud_layer": {
            "model":      "Isolation Forest (unsupervised anomaly)",
            "rules":      "8 hard rule checks (loan-to-income, geo, social, etc.)",
            "verdicts":   ["PROCEED", "FLAG", "BLOCK"],
        },
        "regulatory_alignment": [
            "RBI Fair Practices Code for NBFC lending",
            "Proactive gender/age/region bias audit",
            "Explainable top-factor output per decision",
            "No hard rejection without stated reason",
        ],
    }


@router.get(
    "/demo-guide",
    summary="Live demo cheat sheet for judges",
)
async def demo_guide() -> dict:
    """Step-by-step guide for running the hackathon demo."""
    return {
        "title": "ScoreSeva — Hackathon Demo Guide",
        "story": (
            "Show a credit-invisible Indian getting scored, "
            "flagged for fraud, given a roadmap, and assessed "
            "on their own words — all in 4 API calls."
        ),
        "demo_steps": [
            {
                "step": 1,
                "title": "Responsible borrower — full approval",
                "url":   "POST /fraud-check/with-score",
                "persona": "Ramesh Kumar — auto-rickshaw driver",
                "what_to_say": (
                    "Ramesh has no CIBIL score. Traditional banks "
                    "reject him outright. ScoreSeva scores him 705 "
                    "GOOD based on 8 years of UPI payments and phone "
                    "bill regularity. Approved at 10-13% rate."
                ),
            },
            {
                "step": 2,
                "title": "Fraud attempt — caught automatically",
                "url":   "POST /fraud-check/with-score",
                "persona": "Arjun Mehta — synthetic fraud case",
                "what_to_say": (
                    "Arjun claims 8L income but has 22/100 UPI score "
                    "and 8 credit enquiries in 3 months. System fires "
                    "INCOME_DIGITAL_MISMATCH and EXCESSIVE_ENQUIRIES. "
                    "BLOCKED before any human reviews it."
                ),
            },
            {
                "step": 3,
                "title": "Rejected applicant — gets a roadmap",
                "url":   "GET /trajectory/demo/vikram",
                "persona": "Vikram — scored 490, currently rejected",
                "what_to_say": (
                    "Vikram is rejected today. But ScoreSeva tells him "
                    "exactly 3 things to do. In 24 months he can reach "
                    "650 — approved. No other credit system does this."
                ),
            },
            {
                "step": 4,
                "title": "NLP psychometric — words reveal intent",
                "url":   "GET /nlp-score/demo/responsible vs desperate",
                "what_to_say": (
                    "Same loan amount. Different words. 'I save 25% and "
                    "will repay in 12 months' scores 72/100. "
                    "'Urgent help please I have many debts' scores 18/100. "
                    "The model reads intent, not just numbers."
                ),
            },
        ],
        "key_numbers_to_quote": {
            "target_market":   "190 million credit-invisible Indians",
            "CIBIL_gap":       "Only 30% of Indian adults have CIBIL scores",
            "score_range":     "300-900 (matches CIBIL convention)",
            "feature_count":   "22 features including 6 India-specific digital signals",
            "audit_dimensions": "Gender, Age, Region, Income — 4 fairness dimensions",
            "trajectory_gain": "Up to +160 points in 24 months with action plan",
        },
    }
