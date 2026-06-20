import json
from cibil_parser import parse_cibil_report

def test_cibil_parser():
    # 1. A healthy FOUND profile (score 760, 3 accounts, clean history)
    found_profile = {
        "cibil_score": 760,
        "report_status": "FOUND",
        "accounts": [
            {
                "account_type": "Credit Card",
                "status": "Active",
                "sanctioned_amount": 100000,
                "current_balance": 25000,
                "overdue_amount": 0,
                "payment_history": "000000000000",
                "opened_date": "2020-01-15"
            },
            {
                "account_type": "Personal Loan",
                "status": "Closed",
                "sanctioned_amount": 50000,
                "current_balance": 0,
                "overdue_amount": 0,
                "payment_history": "000000X00000",
                "opened_date": "2019-06-10"
            },
            {
                "account_type": "Auto Loan",
                "status": "Active",
                "sanctioned_amount": 500000,
                "current_balance": 350000,
                "overdue_amount": 0,
                "payment_history": "000000000000",
                "opened_date": "2021-03-20"
            }
        ],
        "enquiries_last_6_months": 1,
        "enquiries_last_12_months": 2
    }

    # 2. A THIN_FILE profile (score 650, 1 account, 8 months old)
    thin_profile = {
        "cibil_score": 650,
        "report_status": "FOUND",
        "accounts": [
            {
                "account_type": "Consumer Loan",
                "status": "Active",
                "sanctioned_amount": 20000,
                "current_balance": 15000,
                "overdue_amount": 0,
                "payment_history": "00000000",
                "opened_date": "2023-10-01" # Assuming current date is ~mid 2024
            }
        ],
        "enquiries_last_6_months": 3,
        "enquiries_last_12_months": 3
    }

    # 3. A NOT_FOUND profile (null score, zero accounts — credit invisible)
    not_found_profile = {
        "cibil_score": None,
        "report_status": "NOT_FOUND",
        "accounts": [],
        "enquiries_last_6_months": 0,
        "enquiries_last_12_months": 0
    }

    print("--- 1. FOUND PROFILE ---")
    print(json.dumps(parse_cibil_report(found_profile, "report"), indent=2))
    print("\n--- 2. THIN_FILE PROFILE ---")
    print(json.dumps(parse_cibil_report(thin_profile, "report"), indent=2))
    print("\n--- 3. NOT_FOUND PROFILE ---")
    print(json.dumps(parse_cibil_report(not_found_profile, "report"), indent=2))

if __name__ == "__main__":
    test_cibil_parser()
