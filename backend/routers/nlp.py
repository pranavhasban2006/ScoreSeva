"""
nlp.py
NLP Psychometric Analysis endpoint for ScoreSeva API.

POST /nlp-score
  - Accepts free-text applicant responses (NLPRequest schema)
  - Combines all text fields into one analysis string
  - Extracts 8 psychometric features using rule-based signals
  - Runs HuggingFace sentiment analysis
  - Runs Logistic Regression classifier from Phase 1C
  - Returns NLP credit score (0-100), risk label, and signals
"""

import re
import logging
import pandas as pd
import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from schemas.applicant import NLPRequest, NLPDetailedResponse
from models.model_loader import get_registry, ModelRegistry

logger = logging.getLogger("scoreseva.nlp")

router = APIRouter(prefix="/nlp-score", tags=["NLP Psychometric"])


# ── Helper: extract rule-based psychometric features ──────────────────

def extract_psychometric_features(text: str) -> dict:
    """
    Extract 8 psychometric signals from applicant text.
    Mirrors Phase 1C Cell 5 exactly.
    Each signal returns a float between 0 and 1.
    """
    text_lower = text.lower()
    words      = text_lower.split()
    word_count = max(len(words), 1)

    # 1. Planning orientation
    planning_keywords = [
        'plan', 'monthly', 'installment', 'emi', 'repay', 'budget',
        'save', 'saving', 'income', 'earn', 'months', 'years',
        'percent', 'amount', 'schedule', 'systematic', 'regular'
    ]
    planning_score = min(
        sum(1 for w in planning_keywords if w in text_lower) / 5,
        1.0
    )

    # 2. Future orientation
    future_keywords = [
        'will', 'future', 'grow', 'expand', 'improve', 'build',
        'invest', 'increase', 'develop', 'opportunity', 'goal',
        'achieve', 'success', 'profit', 'return', 'generate'
    ]
    future_score = min(
        sum(1 for w in future_keywords if w in text_lower) / 4,
        1.0
    )

    # 3. Urgency / desperation (higher = worse)
    urgency_keywords = [
        'urgent', 'urgently', 'immediately', 'fast', 'quickly',
        'desperate', 'desperately', 'emergency', 'crisis', 'survive',
        'last option', 'no choice', 'somehow', 'anything'
    ]
    urgency_score = min(
        sum(1 for w in urgency_keywords if w in text_lower) / 3,
        1.0
    )

    # 4. Responsibility language
    responsibility_keywords = [
        'responsible', 'discipline', 'commit', 'honor', 'promise',
        'trust', 'reliable', 'consistent', 'never missed', 'always paid',
        'on time', 'understand', 'importance', 'obligation'
    ]
    responsibility_score = min(
        sum(1 for w in responsibility_keywords if w in text_lower) / 3,
        1.0
    )

    # 5. Productive / business use
    productive_keywords = [
        'business', 'shop', 'machine', 'equipment', 'inventory',
        'work', 'delivery', 'tailoring', 'vendor', 'trade',
        'capital', 'stock', 'tool', 'vehicle', 'expand'
    ]
    productive_score = min(
        sum(1 for w in productive_keywords if w in text_lower) / 4,
        1.0
    )

    # 6. Debt stress signals (higher = worse)
    stress_keywords = [
        'debt', 'loan from many', 'multiple loans', 'clear others',
        'lost job', 'no income', 'savings finished', 'rejected',
        'difficult', 'struggling', 'bad situation', 'tough'
    ]
    stress_score = min(
        sum(1 for w in stress_keywords if w in text_lower) / 3,
        1.0
    )

    # 7. Specificity (longer = more thoughtful)
    specificity_score = min(word_count / 50, 1.0)

    # 8. Numeric confidence (mentions specific numbers)
    numbers_found  = len(re.findall(r'\b\d+\b', text))
    numeric_score  = min(numbers_found / 5, 1.0)

    return {
        'planning_score':       round(planning_score, 3),
        'future_orientation':   round(future_score, 3),
        'urgency_flag':         round(urgency_score, 3),
        'responsibility_score': round(responsibility_score, 3),
        'productive_use_score': round(productive_score, 3),
        'stress_flag':          round(stress_score, 3),
        'specificity_score':    round(specificity_score, 3),
        'numeric_confidence':   round(numeric_score, 3),
    }


# ── Helper: compute composite NLP score ──────────────────────────────

def compute_nlp_score(
    features: dict,
    sentiment_score: float,
) -> float:
    """
    Combine all psychometric signals into one NLP credit score (0-100).
    Mirrors Phase 1C Cell 6 exactly.
    Higher score = more creditworthy based on text analysis.
    """
    positive = (
        sentiment_score             * 0.20 +
        features['planning_score']       * 0.20 +
        features['future_orientation']   * 0.15 +
        features['responsibility_score'] * 0.15 +
        features['productive_use_score'] * 0.15 +
        features['specificity_score']    * 0.08 +
        features['numeric_confidence']   * 0.07
    )
    negative = (
        features['urgency_flag']  * 0.25 +
        features['stress_flag']   * 0.20
    )
    raw = positive - (negative * 0.45)
    return round(max(0.0, min(100.0, raw * 100)), 1)


# ── Helper: get sentiment score ───────────────────────────────────────

def get_sentiment_score(
    text: str,
    nlp_pipeline: dict,
) -> float:
    """
    Run HuggingFace sentiment analysis on text.
    Returns float from -1 (very negative) to +1 (very positive).
    Falls back to rule-based estimate if pipeline unavailable.
    """
    try:
        # The sentiment pipeline is stored inside the nlp_pipeline dict
        # It was saved as 'sentiment_pipeline_name' (just the model name)
        # We need to load it on first use and cache it
        # Use a module-level cache to avoid reloading each request

        from transformers import pipeline as hf_pipeline

        # Module-level cache
        if not hasattr(get_sentiment_score, "_cached_pipeline"):
            model_name = nlp_pipeline.get(
                "sentiment_pipeline_name",
                "distilbert-base-uncased-finetuned-sst-2-english"
            )
            logger.info(f"Loading HuggingFace pipeline: {model_name}")
            get_sentiment_score._cached_pipeline = hf_pipeline(
                "sentiment-analysis",
                model=model_name,
                truncation=True,
                max_length=512,
            )
            logger.info("HuggingFace pipeline loaded and cached")

        result = get_sentiment_score._cached_pipeline(text[:512])[0]
        score  = float(result['score'])
        if result['label'] == 'NEGATIVE':
            score = -score
        return round(score, 4)

    except Exception as e:
        logger.warning(
            f"HuggingFace pipeline failed: {e} — "
            f"falling back to rule-based sentiment"
        )
        # Rule-based fallback sentiment
        positive_words = [
            'good', 'great', 'stable', 'reliable', 'consistent',
            'always', 'never missed', 'regular', 'committed',
            'disciplined', 'plan', 'save', 'grow', 'improve'
        ]
        negative_words = [
            'bad', 'urgent', 'desperate', 'problem', 'crisis',
            'debt', 'struggling', 'difficult', 'tough', 'failed'
        ]
        text_lower = text.lower()
        pos = sum(1 for w in positive_words if w in text_lower)
        neg = sum(1 for w in negative_words if w in text_lower)
        total = pos + neg + 1
        return round((pos - neg) / total, 4)


# ── Helper: generate text insights ───────────────────────────────────

def generate_text_insights(
    features: dict,
    sentiment: float,
    score: float,
) -> list[str]:
    """
    Generate 3-5 human-readable insight strings from the
    psychometric signals. These appear in the API response
    and on the frontend dashboard.
    """
    insights = []

    # Sentiment insight
    if sentiment > 0.5:
        insights.append(
            "Applicant uses highly positive language — "
            "indicates confidence and financial optimism."
        )
    elif sentiment > 0:
        insights.append(
            "Applicant tone is moderately positive — "
            "shows reasonable outlook."
        )
    else:
        insights.append(
            "Applicant language carries negative sentiment — "
            "may indicate financial stress or anxiety."
        )

    # Planning insight
    if features['planning_score'] > 0.6:
        insights.append(
            "Strong planning orientation detected — "
            "applicant mentions specific amounts, timelines, "
            "and repayment schedules."
        )
    elif features['planning_score'] < 0.2:
        insights.append(
            "Low planning orientation — "
            "response lacks specific numbers or repayment details."
        )

    # Urgency insight
    if features['urgency_flag'] > 0.3:
        insights.append(
            "⚠️ Urgency language detected — "
            "words like 'immediately', 'desperate', or 'urgent' "
            "suggest financial pressure rather than planned borrowing."
        )

    # Productive use insight
    if features['productive_use_score'] > 0.4:
        insights.append(
            "Loan purpose is productive/business-related — "
            "income-generating use lowers repayment risk."
        )

    # Responsibility insight
    if features['responsibility_score'] > 0.3:
        insights.append(
            "Responsibility language present — "
            "applicant explicitly references payment history "
            "and financial discipline."
        )

    # Stress insight
    if features['stress_flag'] > 0.3:
        insights.append(
            "⚠️ Debt stress signals detected — "
            "mentions of existing debts or financial difficulties "
            "increase repayment risk."
        )

    # Overall score insight
    if score >= 70:
        insights.append(
            f"Overall NLP score {score:.0f}/100 — "
            "STRONG psychometric profile. Text analysis supports approval."
        )
    elif score >= 45:
        insights.append(
            f"Overall NLP score {score:.0f}/100 — "
            "MODERATE psychometric profile. Standard verification advised."
        )
    else:
        insights.append(
            f"Overall NLP score {score:.0f}/100 — "
            "WEAK psychometric profile. Additional due diligence required."
        )

    return insights[:5]  # Cap at 5 insights


# ── Main NLP scoring endpoint ─────────────────────────────────────────

@router.post(
    "/",
    response_model=NLPDetailedResponse,
    summary="Analyze applicant text for psychometric credit signals",
    description="""
Submit free-text applicant responses and receive:
- **NLP credit score** (0-100, higher = more creditworthy)
- **Sentiment score** (-1 to +1, financial tone)
- **Risk probability** (from Logistic Regression classifier)
- **Risk label** (LOW RISK or HIGH RISK)
- **8 psychometric signals** (planning, urgency, responsibility, etc.)
- **Human-readable text insights** explaining the assessment

This is the feature NO traditional credit bureau offers.
A borrower's own words reveal their repayment intent.
    """,
)
async def nlp_score(
    request: NLPRequest,
    registry: ModelRegistry = Depends(get_registry),
) -> NLPDetailedResponse:
    """
    NLP psychometric analysis endpoint.
    Uses Phase 1C Logistic Regression + HuggingFace sentiment.
    """

    # ── Guard: check model loaded ─────────────────────────────────────
    if registry.nlp_pipeline is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "model_not_loaded",
                "message": (
                    "NLP psychometric model is not available. "
                    "Check /health for model status."
                )
            }
        )

    nlp_pipeline = registry.nlp_pipeline

    # ── Combine all text fields ───────────────────────────────────────
    text_parts = [request.why_loan]
    if request.repayment_plan:
        text_parts.append(request.repayment_plan)
    if request.financial_situation:
        text_parts.append(request.financial_situation)

    combined_text = " ".join(text_parts).strip()

    if len(combined_text.split()) < 5:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "text_too_short",
                "message": (
                    "Combined text is too short for analysis. "
                    "Please provide at least 5 words."
                )
            }
        )

    # ── Extract psychometric features ─────────────────────────────────
    try:
        features = extract_psychometric_features(combined_text)
    except Exception as e:
        logger.error(f"Feature extraction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "feature_extraction_failed",
                "message": str(e),
            }
        )

    # ── Get sentiment score ───────────────────────────────────────────
    try:
        sentiment = get_sentiment_score(combined_text, nlp_pipeline)
    except Exception as e:
        logger.warning(f"Sentiment failed, using 0.0: {e}")
        sentiment = 0.0

    # ── Compute NLP credit score ──────────────────────────────────────
    nlp_score_val = compute_nlp_score(features, sentiment)

    # ── Run Logistic Regression classifier ───────────────────────────
    try:
        clf     = nlp_pipeline["classifier"]
        scaler  = nlp_pipeline["scaler"]
        feature_cols = nlp_pipeline["feature_cols"]

        feature_row = {
            'sentiment_score':      sentiment,
            'planning_score':       features['planning_score'],
            'future_orientation':   features['future_orientation'],
            'urgency_flag':         features['urgency_flag'],
            'responsibility_score': features['responsibility_score'],
            'productive_use_score': features['productive_use_score'],
            'stress_flag':          features['stress_flag'],
            'specificity_score':    features['specificity_score'],
            'numeric_confidence':   features['numeric_confidence'],
            'nlp_credit_score':     nlp_score_val / 100,
        }

        X = pd.DataFrame(
            [[feature_row.get(col, 0.0) for col in feature_cols]],
            columns=feature_cols
        )
        X_scaled     = scaler.transform(X)
        risk_prob    = float(clf.predict_proba(X_scaled)[0][1])
        risk_label   = (
            "LOW RISK ✅" if risk_prob < 0.5 else "HIGH RISK ⚠️"
        )

    except Exception as e:
        logger.error(f"Classifier inference failed: {e}", exc_info=True)
        # Fallback: derive risk from NLP score directly
        risk_prob  = float(max(0.0, min(1.0, 1 - nlp_score_val / 100)))
        risk_label = "LOW RISK ✅" if risk_prob < 0.5 else "HIGH RISK ⚠️"

    # ── Generate insights ─────────────────────────────────────────────
    insights = generate_text_insights(features, sentiment, nlp_score_val)

    # ── Log summary ───────────────────────────────────────────────────
    logger.info(
        f"NLP score: {nlp_score_val:.1f} | "
        f"Sentiment: {sentiment:+.3f} | "
        f"Risk prob: {risk_prob:.3f} | "
        f"Label: {risk_label} | "
        f"Words: {len(combined_text.split())}"
    )

    return NLPDetailedResponse(
        applicant_id=request.applicant_id,
        combined_text=combined_text[:200] + (
            "..." if len(combined_text) > 200 else ""
        ),
        nlp_credit_score=nlp_score_val,
        sentiment_score=round(sentiment, 4),
        risk_probability=round(risk_prob, 4),
        risk_label=risk_label,
        psychometric_signals={
            "planning_orientation":  features['planning_score'],
            "future_orientation":    features['future_orientation'],
            "urgency_flag":          features['urgency_flag'],
            "responsibility":        features['responsibility_score'],
            "productive_use":        features['productive_use_score'],
            "stress_flag":           features['stress_flag'],
            "specificity":           features['specificity_score'],
            "numeric_confidence":    features['numeric_confidence'],
        },
        text_insights=insights,
        model_version="1.0.0",
    )


# ── Quick single-text endpoint ────────────────────────────────────────

@router.post(
    "/quick",
    summary="Quick NLP score from a single text input",
    description="""
Lightweight version of the NLP scorer.
Accepts a single text string and returns just the
NLP score, risk label, and top 3 signals.
Perfect for real-time frontend feedback as user types.
    """,
)
async def nlp_quick_score(
    payload: dict,
    registry: ModelRegistry = Depends(get_registry),
) -> dict:
    """
    Quick NLP scorer — single text in, score + label out.
    Accepts: {"text": "your text here"}
    """

    text = payload.get("text", "").strip()

    if len(text) < 10:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "text_too_short",
                "message": "Please provide at least 10 characters."
            }
        )

    if registry.nlp_pipeline is None:
        raise HTTPException(
            status_code=503,
            detail={"error": "model_not_loaded"}
        )

    features  = extract_psychometric_features(text)
    sentiment = get_sentiment_score(text, registry.nlp_pipeline)
    score     = compute_nlp_score(features, sentiment)

    risk_label = (
        "LOW RISK ✅"    if score >= 60 else
        "MODERATE ⚠️"   if score >= 35 else
        "HIGH RISK 🚨"
    )

    # Top 3 signals by absolute value
    signal_map = {
        "Planning":       features['planning_score'],
        "Future focus":   features['future_orientation'],
        "Urgency":        -features['urgency_flag'],
        "Responsibility": features['responsibility_score'],
        "Productive use": features['productive_use_score'],
        "Stress":         -features['stress_flag'],
    }
    top_signals = sorted(
        signal_map.items(), key=lambda x: x[1], reverse=True
    )[:3]

    return {
        "text_preview":  text[:100] + ("..." if len(text) > 100 else ""),
        "nlp_score":     score,
        "risk_label":    risk_label,
        "sentiment":     round(sentiment, 3),
        "top_signals":   [
            {"signal": k, "value": round(v, 3)}
            for k, v in top_signals
        ],
    }


# ── Demo endpoint ─────────────────────────────────────────────────────

@router.get(
    "/demo/{profile}",
    summary="Run NLP analysis on a pre-built demo text profile",
    description="""
Run NLP psychometric analysis on pre-built demo texts.
Use during live demos for reliable, consistent results.

Valid profile names:
- responsible  (planning-oriented, high score)
- desperate    (urgency-driven, low score)
- business     (productive use, high score)
- vague        (no plan, low score)
    """,
)
async def nlp_demo(
    profile: str,
    registry: ModelRegistry = Depends(get_registry),
) -> dict:
    """
    NLP demo using pre-built text profiles.
    Useful for hackathon demo consistency.
    """

    DEMO_TEXTS = {
        "responsible": NLPRequest(
            why_loan=(
                "I need this loan to buy a sewing machine and "
                "grow my tailoring business. I save 25 percent "
                "of my income every month and the EMI will be "
                "very manageable within my budget."
            ),
            repayment_plan=(
                "I plan to repay in 12 equal monthly installments "
                "from my stable tailoring income. I have never "
                "missed any payment in my life and I am committed "
                "to honoring this obligation on time every month."
            ),
            financial_situation=(
                "My finances are stable with regular income and "
                "consistent UPI payments for the last 3 years."
            ),
        ),
        "desperate": NLPRequest(
            why_loan=(
                "I urgently need money for some personal problems "
                "please help me get this loan as fast as possible "
                "my situation is very bad right now."
            ),
            repayment_plan=(
                "I will repay somehow, right now I just need the "
                "money urgently. I have many debts already but "
                "this is my last option."
            ),
            financial_situation=(
                "My financial situation is very difficult and "
                "I am struggling to manage expenses."
            ),
        ),
        "business": NLPRequest(
            why_loan=(
                "I need this loan to purchase inventory for my "
                "kirana store. This capital investment will "
                "generate 40 percent higher profit margins and "
                "I will repay from increased business income "
                "within 18 months."
            ),
            repayment_plan=(
                "My shop earns 20000 per month and the EMI is "
                "only 3000 so repayment is very comfortable. "
                "I have a clear budget and systematic plan."
            ),
            financial_situation=(
                "Stable business income for 8 years with "
                "consistent growth and no outstanding debts."
            ),
        ),
        "vague": NLPRequest(
            why_loan=(
                "I need money for some things and will use it "
                "for important purposes."
            ),
            repayment_plan=(
                "I will repay when I have money."
            ),
        ),
    }

    name = profile.lower().strip()
    if name not in DEMO_TEXTS:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "profile_not_found",
                "message": (
                    f"Profile '{profile}' not found. "
                    f"Valid profiles: {list(DEMO_TEXTS.keys())}"
                )
            }
        )

    if registry.nlp_pipeline is None:
        raise HTTPException(
            status_code=503,
            detail={"error": "model_not_loaded"}
        )

    request   = DEMO_TEXTS[name]
    text_parts = [request.why_loan]
    if request.repayment_plan:
        text_parts.append(request.repayment_plan)
    if request.financial_situation:
        text_parts.append(request.financial_situation)
    combined  = " ".join(text_parts)

    features  = extract_psychometric_features(combined)
    sentiment = get_sentiment_score(combined, registry.nlp_pipeline)
    score     = compute_nlp_score(features, sentiment)

    risk_label = "LOW RISK ✅" if score >= 50 else "HIGH RISK ⚠️"
    insights   = generate_text_insights(features, sentiment, score)

    return {
        "profile":           name,
        "nlp_credit_score":  score,
        "sentiment_score":   round(sentiment, 4),
        "risk_label":        risk_label,
        "psychometric_signals": {
            k: round(v, 3) for k, v in features.items()
        },
        "text_insights": insights,
    }
