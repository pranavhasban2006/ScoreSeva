import json
from counterfactual import find_counterfactual

def mock_scoring_function(features: dict) -> int:
    """
    A simplified weighted-sum stand-in for testing purposes.
    The real endpoint in 10B will use the actual XGBoost pipeline.
    Base score is 500.
    bounce_count = -20 pts per bounce
    income_regularity_score = +1 pt per %
    savings_rate = +2 pts per %
    emi_obligation_ratio = -1 pt per %
    """
    score = 500
    score -= features.get("bounce_count", 0) * 20
    score += features.get("income_regularity_score", 0) * 1
    score += features.get("savings_rate", 0) * 2
    score -= features.get("emi_obligation_ratio", 0) * 1
    return int(score)

def test():
    applicant_features = {
        "bounce_count": 3,
        "income_regularity_score": 40,
        "savings_rate": 5,
        "emi_obligation_ratio": 60,
        "age": 28,
        "annual_income": 300000
    }
    
    current_score = mock_scoring_function(applicant_features)
    print(f"Current Score: {current_score}")
    
    shap_values = {
        "bounce_count": -1.5,
        "emi_obligation_ratio": -0.8,
        "savings_rate": -0.5,
        "income_regularity_score": -0.3,
        "age": 0.1,
        "annual_income": 0.2
    }
    
    result = find_counterfactual(
        applicant_features=applicant_features,
        current_score=current_score,
        decision="REJECTED",
        shap_values=shap_values,
        scoring_function=mock_scoring_function,
        approval_threshold=650
    )
    
    print("Result:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test()
