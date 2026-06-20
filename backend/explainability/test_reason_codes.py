import json
from reason_codes import generate_reason_codes

def test_reason_codes():
    rejected_shap = {
        "annual_income": 0.5,
        "income_regularity_score": -1.2,
        "bounce_count": -0.8,
        "gaming_risk_score": -1.5,
        "cibil_score": -0.3,
        "savings_rate": 0.1
    }
    rejected_vals = {
        "annual_income": 450000,
        "income_regularity_score": 40,
        "bounce_count": 2,
        "gaming_risk_score": 85,
        "cibil_score": 580,
        "savings_rate": 0.05
    }
    
    print("--- REJECTED CASE ---")
    res1 = generate_reason_codes(rejected_shap, rejected_vals, "REJECTED")
    print(json.dumps(res1, indent=2))
    
    approved_shap = {
        "annual_income": 1.5,
        "upi_consistency_score": 1.2,
        "phone_bill_regularity": 0.8,
        "bounce_count": -0.1,
        "credit_utilization_ratio": 0.5
    }
    approved_vals = {
        "annual_income": 800000,
        "upi_consistency_score": 95,
        "phone_bill_regularity": 100,
        "bounce_count": 0,
        "credit_utilization_ratio": 15
    }
    
    print("\n--- APPROVED CASE ---")
    res2 = generate_reason_codes(approved_shap, approved_vals, "APPROVED")
    print(json.dumps(res2, indent=2))

if __name__ == "__main__":
    test_reason_codes()
