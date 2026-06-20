import json
from anti_gaming import detect_gaming_patterns

def test_anti_gaming():
    # Helper to generate dates
    from datetime import datetime, timedelta
    now = datetime.now()
    
    # 1. Clean Profile (Ramesh style)
    clean_txs = []
    for i in range(30):
        dt = now - timedelta(days=i*2)
        clean_txs.append({"date": dt.strftime("%Y-%m-%d"), "amount": 500 + i*10, "type": "DEBIT"})
    
    clean_txs.append({"date": (now - timedelta(days=2)).strftime("%Y-%m-%d"), "amount": 15000, "type": "CREDIT", "description": "SALARY"})
    clean_txs.append({"date": (now - timedelta(days=32)).strftime("%Y-%m-%d"), "amount": 15000, "type": "CREDIT", "description": "SALARY"})
    
    clean_bank_features = {"monthly_income_actual": 15000, "salary_detected": True}
    clean_applicant = {"annual_income": 180000, "employment_years": 8.0}
    
    # 2. Salary Injection Profile
    inj_txs = clean_txs.copy()
    inj_txs.append({"date": (now - timedelta(days=3)).strftime("%Y-%m-%d"), "amount": 45000, "type": "CREDIT", "description": "TRANSFER"})
    
    inj_bank_features = {"monthly_income_actual": 15000, "salary_detected": False}
    inj_applicant = {"annual_income": 180000, "employment_years": 1.0}
    
    # 3. Circular Profile
    circ_txs = []
    for i in range(4):
        dt_debit = now - timedelta(days=10 + i*4)
        dt_credit = dt_debit + timedelta(days=1)
        circ_txs.append({"date": dt_debit.strftime("%Y-%m-%d"), "amount": 8000, "type": "DEBIT"})
        circ_txs.append({"date": dt_credit.strftime("%Y-%m-%d"), "amount": 7800, "type": "CREDIT"})
        
    circ_bank_features = {"monthly_income_actual": 15000, "salary_detected": False}
    circ_applicant = {"annual_income": 300000, "employment_years": 1.0}
    
    print("--- 1. CLEAN PROFILE ---")
    res1 = detect_gaming_patterns(clean_txs, clean_bank_features, clean_applicant)
    print(f"Risk Tier: {res1['risk_tier']}, Score: {res1['gaming_risk_score']}")
    
    print("\n--- 2. SALARY INJECTION PROFILE ---")
    res2 = detect_gaming_patterns(inj_txs, inj_bank_features, inj_applicant)
    print(f"Risk Tier: {res2['risk_tier']}, Score: {res2['gaming_risk_score']}")
    
    print("\n--- 3. CIRCULAR PROFILE ---")
    res3 = detect_gaming_patterns(circ_txs, circ_bank_features, circ_applicant)
    print(f"Risk Tier: {res3['risk_tier']}, Score: {res3['gaming_risk_score']}")
    # print(json.dumps(res3["signals"]["circular_transaction_pattern"], indent=2))

if __name__ == "__main__":
    test_anti_gaming()
