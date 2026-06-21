import copy

# Ethical constraints: Only suggest changes a user can realistically make over time.
# Never suggest fabricating history or gaming the system.

MUTABLE_FEATURES = {
    "bounce_count": {
        "good_direction": "down",
        "step": 1.0,
        "bound": 0.0,
        "template": "Reduce payment bounces from {current} to {target} over the next few months"
    },
    "income_regularity_score": {
        "good_direction": "up",
        "step": 5.0,
        "bound": 100.0,
        "template": "Stabilize income deposits to improve regularity score from {current:.0f} to {target:.0f}"
    },
    "savings_rate": {
        "good_direction": "up",
        "step": 5.0,
        "bound": 50.0,
        "template": "Increase monthly savings rate from {current:.0f}% to {target:.0f}%"
    },
    "emi_obligation_ratio": {
        "good_direction": "down",
        "step": 5.0,
        "bound": 0.0,
        "template": "Pay down existing debt to lower EMI obligation from {current:.0f}% to {target:.0f}%"
    },
    "cash_withdrawal_ratio": {
        "good_direction": "down",
        "step": 5.0,
        "bound": 0.0,
        "template": "Reduce cash withdrawals and use digital channels (from {current:.0f}% to {target:.0f}%)"
    },
    "credit_utilization_ratio": {
        "good_direction": "down",
        "step": 5.0,
        "bound": 30.0,
        "template": "Lower credit card balances to reduce utilization from {current:.0f}% to {target:.0f}%"
    },
    "hidden_emi_count": {
        "good_direction": "down",
        "step": 1.0,
        "bound": 0.0,
        "template": "Consolidate or declare {current} hidden EMI obligation(s) to reach {target}"
    },
    "financial_stress_score": {
        "good_direction": "down",
        "step": 0.0, 
        "bound": 0.0,
        "template": ""
    }
}

FIXED_FEATURES = {
    "age": "Age is immutable.",
    "employment_tenure_months": "Cannot fabricate tenure.",
    "cibil_score": "This is an outcome metric, not directly controllable.",
    "annual_income": "Not actionable short-term advice; conflates with income verification signals.",
    "gaming_risk_score": "Relates to honesty and irregular patterns. Never advise users on how to 'game' the model better."
}


def find_counterfactual(
    applicant_features: dict,
    current_score: int,
    decision: str,
    shap_values: dict,
    scoring_function: callable,
    approval_threshold: int = 650,
) -> dict:
    """
    Greedy coordinate-wise search for the minimal actionable changes needed for approval.
    """
    if decision == "APPROVED" or current_score >= approval_threshold:
        return {
            "counterfactual_needed": False,
            "fully_achievable": True,
            "current_score": current_score,
            "projected_score": current_score,
            "approval_threshold": approval_threshold,
            "changes_required": [],
            "estimated_timeframe": "N/A"
        }
        
    ranked_mutables = []
    for feat, shap_val in shap_values.items():
        if feat in MUTABLE_FEATURES and feat != "financial_stress_score":
            ranked_mutables.append((feat, shap_val))
            
    ranked_mutables.sort(key=lambda x: x[1]) 
    
    current_features = copy.deepcopy(applicant_features)
    projected_score = current_score
    changes_made = {}
    
    iteration_count = 0
    max_iterations = 200
    
    for feat, _ in ranked_mutables:
        if projected_score >= approval_threshold or iteration_count >= max_iterations:
            break
            
        config = MUTABLE_FEATURES[feat]
        good_dir = config["good_direction"]
        step = config["step"]
        bound = config["bound"]
        
        orig_val = float(applicant_features.get(feat, 0))
        curr_val = float(current_features.get(feat, 0))
        
        if good_dir == "up" and curr_val >= bound:
            continue
        if good_dir == "down" and curr_val <= bound:
            continue
            
        while iteration_count < max_iterations and projected_score < approval_threshold:
            iteration_count += 1
            
            if good_dir == "up":
                curr_val += step
                if curr_val >= bound:
                    curr_val = bound
            else:
                curr_val -= step
                if curr_val <= bound:
                    curr_val = bound
                    
            current_features[feat] = curr_val
            
            if "bounce_count" in current_features:
                bounces = current_features["bounce_count"]
                current_features["financial_stress_score"] = min(100, bounces * 20)
                
            projected_score = scoring_function(current_features)
            changes_made[feat] = curr_val
            
            if curr_val == bound:
                break
                
    changes_required = []
    for feat, new_val in changes_made.items():
        orig_val = float(applicant_features.get(feat, 0))
        if abs(orig_val - new_val) > 0:
            template = MUTABLE_FEATURES[feat]["template"]
            if "{current:.0f}" in template:
                explanation = template.format(current=orig_val, target=new_val)
            else:
                explanation = template.format(current=int(orig_val), target=int(new_val))
            changes_required.append({
                "feature": feat,
                "current_value": orig_val,
                "suggested_value": new_val,
                "plain_explanation": explanation
            })
            
    timeframe = "3-6 months of consistent financial behavior"
    if any(feat in ["emi_obligation_ratio", "hidden_emi_count"] for feat in changes_made):
        timeframe = "6-12 months of structured repayment"
        
    return {
        "counterfactual_needed": True,
        "fully_achievable": projected_score >= approval_threshold,
        "current_score": current_score,
        "projected_score": int(projected_score),
        "approval_threshold": approval_threshold,
        "changes_required": changes_required,
        "estimated_timeframe": timeframe
    }
