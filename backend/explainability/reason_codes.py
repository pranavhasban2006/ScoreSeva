FEATURE_EXPLANATION_MAP = {
    "annual_income": "Your reported annual income of ₹{value}",
    "income_regularity_score": "The consistency of your monthly income deposits",
    "emi_obligation_ratio": "Your existing loan repayment burden relative to income",
    "bounce_count": "{value} payment bounce(s) detected in your bank statement",
    "financial_stress_score": "Signs of financial stress in recent transactions",
    "cibil_score": "Your CIBIL bureau score of {value}",
    "credit_utilization_ratio": "How much of your available credit you're currently using",
    "employment_tenure_months": "Your employment tenure of {value} months",
    "gaming_risk_score": "Irregularities detected in your transaction patterns",
    "savings_rate": "Your savings rate relative to income",
    "upi_consistency_score": "Your consistency in digital payments via UPI",
    "phone_bill_regularity": "Your phone bill payment regularity"
}

def humanize_feature_name(feature_name: str) -> str:
    return feature_name.replace("_", " ").capitalize()

def generate_reason_codes(shap_values: dict, feature_values: dict, decision: str, top_n: int = 4) -> dict:
    """
    Converts raw SHAP values into ranked, plain-English reason codes.
    """
    negative_factors = []
    positive_factors = []
    
    total_negative_magnitude = 0.0
    total_positive_magnitude = 0.0
    
    for feature, shap_val in shap_values.items():
        if shap_val < 0:
            negative_factors.append((feature, shap_val))
            total_negative_magnitude += abs(shap_val)
        elif shap_val > 0:
            positive_factors.append((feature, shap_val))
            total_positive_magnitude += shap_val
            
    # Sort by absolute magnitude descending
    negative_factors.sort(key=lambda x: abs(x[1]), reverse=True)
    positive_factors.sort(key=lambda x: x[1], reverse=True)
    
    primary_reasons = []
    
    if decision in ["REJECTED", "REVIEW"]:
        factors_to_use = negative_factors[:top_n]
        direction = "NEGATIVE"
        total_mag = total_negative_magnitude
    else:
        factors_to_use = positive_factors[:top_n]
        direction = "POSITIVE"
        total_mag = total_positive_magnitude
        
    for feature, shap_val in factors_to_use:
        template = FEATURE_EXPLANATION_MAP.get(feature, humanize_feature_name(feature))
        value = feature_values.get(feature, "N/A")
        
        # safely format
        try:
            explanation = template.format(value=value)
        except KeyError:
            # If the template expects {value} but doesn't find it, or doesn't have {value}
            explanation = template
            
        contribution_pct = (abs(shap_val) / total_mag * 100) if total_mag > 0 else 0
        
        primary_reasons.append({
            "feature": feature,
            "explanation": explanation,
            "shap_value": float(shap_val),
            "contribution_pct": round(contribution_pct, 1),
            "direction": direction
        })
        
    return {
        "decision": decision,
        "primary_reasons": primary_reasons,
        "total_factors_considered": len(shap_values)
    }
