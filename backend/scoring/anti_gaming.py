from datetime import datetime
from collections import defaultdict

def apply_gaming_penalty(base_score: int, gaming_risk_score: int) -> int:
    """
    Applies a penalty to the base score based on the gaming risk score.
    """
    if gaming_risk_score <= 15:
        return base_score
    elif gaming_risk_score <= 35:
        return int(base_score * 0.95)
    elif gaming_risk_score <= 60:
        return int(base_score * 0.85)
    else:
        penalty_score = int(base_score * 0.70)
        return min(penalty_score, 550)

def detect_gaming_patterns(transactions: list, bank_features: dict, applicant: dict, previous_application_count: int = 0, days_since_last_application: int = None) -> dict:
    signals = {}
    total_score = 0
    flagged_count = 0
    
    if not transactions:
        return {
            "gaming_risk_score": 0,
            "risk_tier": "CLEAN",
            "signals": {},
            "flagged_signal_count": 0,
            "recommendation": "No action needed - no transactions provided."
        }

    # Sort transactions by date
    try:
        txs = sorted(transactions, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"))
    except:
        txs = transactions

    app_date_str = txs[-1]["date"]
    try:
        app_date = datetime.strptime(app_date_str, "%Y-%m-%d")
    except:
        app_date = datetime.now()

    # 1. SALARY_INJECTION_SPIKE (weight 25)
    salary_injection = {"detected": False, "injected_amount": 0.0, "days_before_application": 0}
    
    # Look for large credits (e.g. > 20000) within 7 days of application date
    # that are not part of regular salary (which usually has recurring description or similar amounts earlier)
    monthly_income = bank_features.get("monthly_income_actual", 0)
    for t in txs:
        if t.get("type", "").upper() == "CREDIT" and t.get("amount", 0) > 20000:
            try:
                t_date = datetime.strptime(t["date"], "%Y-%m-%d")
                days_diff = (app_date - t_date).days
                if 0 <= days_diff <= 7:
                    # Check if it's uniquely large or isolated
                    if t["amount"] > monthly_income * 0.8: 
                        # Simple heuristic: if it's > 80% of derived monthly income and happens right before
                        salary_injection["detected"] = True
                        salary_injection["injected_amount"] = t["amount"]
                        salary_injection["days_before_application"] = days_diff
                        break
            except:
                pass
                
    signals["salary_injection_spike"] = salary_injection
    if salary_injection["detected"]:
        total_score += 25
        flagged_count += 1

    # 2. CIRCULAR_TRANSACTION_PATTERN (weight 20)
    circular = {"detected": False, "cycle_count": 0, "avg_cycle_amount": 0.0}
    cycles = []
    
    # Naive O(N^2) search for pairs within 1-3 days and 5% amount difference
    used_credits = set()
    for i, t1 in enumerate(txs):
        if t1.get("type", "").upper() == "DEBIT":
            try:
                d1 = datetime.strptime(t1["date"], "%Y-%m-%d")
                for j in range(i+1, len(txs)):
                    if j in used_credits: continue
                    t2 = txs[j]
                    if t2.get("type", "").upper() == "CREDIT":
                        d2 = datetime.strptime(t2["date"], "%Y-%m-%d")
                        days_diff = (d2 - d1).days
                        if 0 <= days_diff <= 3:
                            amt1 = t1.get("amount", 0)
                            amt2 = t2.get("amount", 0)
                            if amt1 > 1000 and abs(amt1 - amt2) / max(amt1, 1) <= 0.05:
                                cycles.append((amt1 + amt2) / 2)
                                used_credits.add(j)
                                break
            except:
                pass
                
    if len(cycles) >= 3:
        circular["detected"] = True
        circular["cycle_count"] = len(cycles)
        circular["avg_cycle_amount"] = sum(cycles) / len(cycles)
        total_score += 20
        flagged_count += 1
        
    signals["circular_transaction_pattern"] = circular

    # 3. ROUND_NUMBER_BIAS (weight 10)
    round_number = {"detected": False, "round_number_ratio": 0.0}
    large_txs = [t for t in txs if t.get("amount", 0) > 1000]
    if large_txs:
        round_count = sum(1 for t in large_txs if t.get("amount", 0) % 500 == 0)
        ratio = round_count / len(large_txs)
        round_number["round_number_ratio"] = ratio
        if ratio > 0.40:
            round_number["detected"] = True
            total_score += 10
            flagged_count += 1
    signals["round_number_bias"] = round_number

    # 4. DECLARED_VS_ACTUAL_INCOME_GAP (weight up to 20)
    income_gap = {"detected": False, "gap_percentage": 0.0, "severity": "LOW"}
    declared_annual = applicant.get("annual_income", 0)
    actual_annual = bank_features.get("monthly_income_actual", 0) * 12
    if actual_annual > 0 and declared_annual > actual_annual:
        gap_pct = ((declared_annual - actual_annual) / actual_annual) * 100
        if gap_pct > 25:
            income_gap["detected"] = True
            income_gap["gap_percentage"] = gap_pct
            if gap_pct > 50:
                income_gap["severity"] = "HIGH"
                total_score += 20
            elif gap_pct > 35:
                income_gap["severity"] = "MEDIUM"
                total_score += 12
            else:
                total_score += 5
            flagged_count += 1
    signals["declared_vs_actual_income_gap"] = income_gap

    # 5. EMPLOYMENT_TENURE_INCONSISTENCY (weight 15)
    tenure_inconsistency = {"detected": False, "claimed_months": 0, "evidenced_months": 0}
    claimed_months = int(applicant.get("employment_years", 0) * 12)
    # Estimate evidenced_months from first transaction date to last transaction date
    try:
        first_date = datetime.strptime(txs[0]["date"], "%Y-%m-%d")
        evidenced_months = (app_date - first_date).days // 30
    except:
        evidenced_months = 0
        
    salary_detected = bank_features.get("salary_detected", False)
    if claimed_months > 24 and (not salary_detected or evidenced_months < (claimed_months / 2)):
        # If they claim >2 years but we don't see salary, or we only have a very short history
        tenure_inconsistency["detected"] = True
        tenure_inconsistency["claimed_months"] = claimed_months
        tenure_inconsistency["evidenced_months"] = evidenced_months
        total_score += 15
        flagged_count += 1
    signals["employment_tenure_inconsistency"] = tenure_inconsistency

    # 6. RAPID_REAPPLICATION_PATTERN (weight 5)
    reapp = {"detected": False, "reapplication_count": previous_application_count}
    if previous_application_count >= 2 and days_since_last_application is not None and days_since_last_application < 30:
        reapp["detected"] = True
        total_score += 5
        flagged_count += 1
    signals["rapid_reapplication_pattern"] = reapp

    # 7. DORMANT_ACCOUNT_REACTIVATION (weight 5)
    dormant = {"detected": False, "active_months": 0, "total_months": 0}
    try:
        months_dict = defaultdict(list)
        for t in txs:
            dt = datetime.strptime(t["date"], "%Y-%m-%d")
            months_dict[(dt.year, dt.month)].append(t)
            
        total_months = len(months_dict)
        if total_months >= 3:
            # Sort month keys chronologically
            sorted_months = sorted(months_dict.keys())
            last_month = sorted_months[-1]
            last_month_tx_count = len(months_dict[last_month])
            
            prior_tx_counts = [len(months_dict[m]) for m in sorted_months[:-1]]
            avg_prior = sum(prior_tx_counts) / len(prior_tx_counts)
            
            if avg_prior <= 3 and last_month_tx_count > 10:
                dormant["detected"] = True
                dormant["active_months"] = 1
                dormant["total_months"] = total_months
                total_score += 5
                flagged_count += 1
    except:
        pass
    signals["dormant_account_reactivation"] = dormant

    # Tier assignment
    if total_score <= 15:
        risk_tier = "CLEAN"
        rec = "No action needed"
    elif total_score <= 35:
        risk_tier = "LOW_RISK"
        rec = "Proceed with standard review"
    elif total_score <= 60:
        risk_tier = "ELEVATED"
        rec = "Careful manual review recommended"
    else:
        risk_tier = "HIGH_RISK"
        rec = "Manual review required. Score capped."

    return {
        "gaming_risk_score": total_score,
        "risk_tier": risk_tier,
        "signals": signals,
        "flagged_signal_count": flagged_count,
        "recommendation": rec
    }
