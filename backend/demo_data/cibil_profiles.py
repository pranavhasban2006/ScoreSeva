DEMO_CIBIL_PROFILES = {
    "ramesh": {
        "cibil_score": None,
        "report_status": "NOT_FOUND",
        "accounts": [],
        "enquiries_last_6_months": 0,
        "enquiries_last_12_months": 0
    },
    "priya": {
        "cibil_score": None,
        "report_status": "NOT_FOUND",
        "accounts": [],
        "enquiries_last_6_months": 0,
        "enquiries_last_12_months": 0
    },
    "vikram": {
        "cibil_score": 590,
        "report_status": "FOUND",
        "accounts": [
            {
                "account_type": "Personal Loan",
                "status": "Active",
                "sanctioned_amount": 100000,
                "current_balance": 80000,
                "overdue_amount": 5000,
                "payment_history": "000030600000",
                "opened_date": "2023-01-15"
            },
            {
                "account_type": "Credit Card",
                "status": "Active",
                "sanctioned_amount": 50000,
                "current_balance": 48000,
                "overdue_amount": 0,
                "payment_history": "000000000000",
                "opened_date": "2022-05-10"
            }
        ],
        "enquiries_last_6_months": 7,
        "enquiries_last_12_months": 9
    },
    "suresh": {
        "cibil_score": 680,
        "report_status": "THIN_FILE",
        "accounts": [
            {
                "account_type": "Gold Loan",
                "status": "Active",
                "sanctioned_amount": 150000,
                "current_balance": 150000,
                "overdue_amount": 0,
                "payment_history": "000000000", # 9 months
                "opened_date": "2023-09-01"
            }
        ],
        "enquiries_last_6_months": 1,
        "enquiries_last_12_months": 1
    },
    "arjun": {
        "cibil_score": 710,
        "report_status": "FOUND",
        "accounts": [
            {
                "account_type": "Credit Card",
                "status": "Active",
                "sanctioned_amount": 200000,
                "current_balance": 30000,
                "overdue_amount": 0,
                "payment_history": "00000000000000000000",
                "opened_date": "2021-02-15"
            },
            {
                "account_type": "Auto Loan",
                "status": "Active",
                "sanctioned_amount": 500000,
                "current_balance": 200000,
                "overdue_amount": 0,
                "payment_history": "00000000000000000000000000",
                "opened_date": "2020-08-10"
            }
        ],
        "enquiries_last_6_months": 1,
        "enquiries_last_12_months": 2
    },
    "deepak": {
        "cibil_score": 705,
        "report_status": "THIN_FILE",
        "accounts": [
            {
                "account_type": "Personal Loan",
                "status": "Closed",
                "sanctioned_amount": 25000,
                "current_balance": 0,
                "overdue_amount": 0,
                "payment_history": "00000000",
                "opened_date": "2022-01-10"
            }
        ],
        "enquiries_last_6_months": 0,
        "enquiries_last_12_months": 1
    }
}
