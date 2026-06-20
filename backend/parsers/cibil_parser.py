from datetime import datetime

def parse_cibil_report(data: dict, source: str) -> dict:
    """
    Parses a CIBIL report (from JSON or manual entry) and extracts 10 core features.
    source must be "report" or "manual".
    """
    if source == "manual":
        cibil_score = data.get("cibil_score")
        has_history = data.get("has_credit_history", False)
        active_loans = data.get("num_active_loans", 0)
        overdue_accounts = data.get("num_overdue_accounts", 0)
        age_months = data.get("oldest_account_age_months", 0)
        
        if not has_history or (cibil_score is None and active_loans == 0 and age_months == 0):
            file_status = "NOT_FOUND"
            cibil_score = None
        elif active_loans < 2 and age_months < 12:
            file_status = "THIN_FILE"
        else:
            file_status = "FOUND"
            
        return {
            "cibil_score": cibil_score,
            "file_status": file_status,
            "credit_age_months": age_months,
            "active_account_count": active_loans,
            "total_overdue_amount": 1000.0 if overdue_accounts > 0 else 0.0,
            "payment_history_score": 50 if file_status == "NOT_FOUND" else (100 if overdue_accounts == 0 else 60),
            "credit_utilization_ratio": 30.0 if file_status != "NOT_FOUND" else 0.0,
            "recent_enquiry_intensity": 100,
            "written_off_or_settled_count": 0,
            "credit_mix_diversity": 1 if active_loans > 0 else 0
        }

    # source == "report"
    cibil_score = data.get("cibil_score")
    accounts = data.get("accounts", [])
    
    if cibil_score is None and len(accounts) == 0:
        file_status = "NOT_FOUND"
    else:
        file_status = "FOUND"
        
    credit_age_months = 0
    now = datetime.now()
    
    for acc in accounts:
        opened = acc.get("opened_date")
        if opened:
            try:
                dt = datetime.strptime(opened, "%Y-%m-%d")
                age = (now - dt).days / 30.44
                if age > credit_age_months:
                    credit_age_months = int(age)
            except Exception:
                pass
                
    if file_status != "NOT_FOUND":
        if len(accounts) < 2 or credit_age_months < 12:
            file_status = "THIN_FILE"
            
    active_account_count = sum(1 for a in accounts if a.get("status") == "Active")
    total_overdue_amount = float(sum(a.get("overdue_amount", 0) for a in accounts))
    
    # payment_history_score
    if file_status == "NOT_FOUND":
        payment_history_score = 50
    else:
        total_chars = 0
        on_time_chars = 0
        for acc in accounts:
            hist = str(acc.get("payment_history", ""))
            # Handle '0', 'X', and other characters indicating lateness
            for char in hist:
                if char.upper() == 'X':
                    continue
                total_chars += 1
                if char == '0':
                    on_time_chars += 1
        
        if total_chars > 0:
            payment_history_score = int((on_time_chars / total_chars) * 100)
        else:
            payment_history_score = 50

    # credit_utilization_ratio
    cc_accounts = [a for a in accounts if a.get("account_type") == "Credit Card"]
    total_cc_balance = sum(a.get("current_balance", 0) for a in cc_accounts)
    total_cc_limit = sum(a.get("sanctioned_amount", 0) for a in cc_accounts)
    if total_cc_limit > 0:
        credit_utilization_ratio = (total_cc_balance / total_cc_limit) * 100
    else:
        credit_utilization_ratio = 0.0

    # recent_enquiry_intensity
    enquiries_6m = data.get("enquiries_last_6_months", 0)
    if enquiries_6m == 0:
        recent_enquiry_intensity = 100
    elif 1 <= enquiries_6m <= 2:
        recent_enquiry_intensity = 80
    elif 3 <= enquiries_6m <= 5:
        recent_enquiry_intensity = 50
    else:
        recent_enquiry_intensity = 20

    written_off_or_settled_count = sum(
        1 for a in accounts if a.get("status") in ["Written Off", "Settled"]
    )
    
    credit_mix_diversity = len(set(a.get("account_type") for a in accounts if a.get("account_type")))

    return {
        "cibil_score": cibil_score,
        "file_status": file_status,
        "credit_age_months": credit_age_months,
        "active_account_count": active_account_count,
        "total_overdue_amount": total_overdue_amount,
        "payment_history_score": payment_history_score,
        "credit_utilization_ratio": credit_utilization_ratio,
        "recent_enquiry_intensity": recent_enquiry_intensity,
        "written_off_or_settled_count": written_off_or_settled_count,
        "credit_mix_diversity": credit_mix_diversity
    }
