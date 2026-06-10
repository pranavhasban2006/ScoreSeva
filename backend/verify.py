import requests

personas = [
  {'id': 'ramesh', 'annual_income': 180000, 'loan_amount': 50000, 'monthly_emi': 2500, 'age_years': 38, 'gender': 'M', 'num_children': 2, 'family_size': 4, 'employment_years': 8.0, 'income_source': 'Working', 'occupation': 'Drivers', 'ext_credit_score_1': 0.55, 'ext_credit_score_2': 0.62, 'ext_credit_score_3': 0.58, 'credit_enquiries_last_year': 0, 'owns_car': False, 'owns_property': False, 'id_stability_years': 3.2, 'region_risk_rating': 2, 'education_level': 'Secondary / secondary special', 'family_status': 'Married', 'upi_consistency_score': 81.0, 'phone_bill_regularity': 88.0, 'geo_stability_score': 76.0, 'ecommerce_payment_score': 60.0, 'social_network_risk': 0.12, 'app_usage_score': 74.0},
  {'id': 'priya', 'annual_income': 120000, 'loan_amount': 30000, 'monthly_emi': 1500, 'age_years': 32, 'gender': 'F', 'num_children': 1, 'family_size': 3, 'employment_years': 5.0, 'income_source': 'Working', 'occupation': 'Sales', 'ext_credit_score_1': 0.48, 'ext_credit_score_2': 0.51, 'ext_credit_score_3': 0.50, 'credit_enquiries_last_year': 0, 'owns_car': False, 'owns_property': False, 'id_stability_years': 4.0, 'region_risk_rating': 2, 'education_level': 'Secondary / secondary special', 'family_status': 'Married', 'upi_consistency_score': 91.0, 'phone_bill_regularity': 94.0, 'geo_stability_score': 85.0, 'ecommerce_payment_score': 70.0, 'social_network_risk': 0.08, 'app_usage_score': 82.0},
  {'id': 'suresh', 'annual_income': 240000, 'loan_amount': 100000, 'monthly_emi': 5000, 'age_years': 45, 'gender': 'M', 'num_children': 2, 'family_size': 4, 'employment_years': 12.0, 'income_source': 'Commercial associate', 'occupation': 'Managers', 'ext_credit_score_1': 0.6, 'ext_credit_score_2': 0.65, 'ext_credit_score_3': 0.55, 'credit_enquiries_last_year': 2, 'owns_car': True, 'owns_property': True, 'id_stability_years': 8.0, 'region_risk_rating': 1, 'education_level': 'Higher education', 'family_status': 'Married', 'upi_consistency_score': 55.0, 'phone_bill_regularity': 60.0, 'geo_stability_score': 70.0, 'ecommerce_payment_score': 50.0, 'social_network_risk': 0.3, 'app_usage_score': 45.0},
  {'id': 'fatima', 'annual_income': 90000, 'loan_amount': 20000, 'monthly_emi': 1000, 'age_years': 29, 'gender': 'F', 'num_children': 0, 'family_size': 2, 'employment_years': 3.0, 'income_source': 'Working', 'occupation': 'Laborers', 'ext_credit_score_1': 0.4, 'ext_credit_score_2': 0.42, 'ext_credit_score_3': 0.38, 'credit_enquiries_last_year': 0, 'owns_car': False, 'owns_property': False, 'id_stability_years': 2.0, 'region_risk_rating': 3, 'education_level': 'Secondary / secondary special', 'family_status': 'Married', 'upi_consistency_score': 85.0, 'phone_bill_regularity': 82.0, 'geo_stability_score': 88.0, 'ecommerce_payment_score': 40.0, 'social_network_risk': 0.15, 'app_usage_score': 65.0},
  {'id': 'vikram', 'annual_income': 150000, 'loan_amount': 80000, 'monthly_emi': 4000, 'age_years': 24, 'gender': 'M', 'num_children': 0, 'family_size': 1, 'employment_years': 1.5, 'income_source': 'Working', 'occupation': 'Sales', 'ext_credit_score_1': 0.35, 'ext_credit_score_2': 0.35, 'ext_credit_score_3': 0.33, 'credit_enquiries_last_year': 4, 'owns_car': False, 'owns_property': False, 'id_stability_years': 1.2, 'region_risk_rating': 2, 'education_level': 'Secondary / secondary special', 'family_status': 'Single / not married', 'upi_consistency_score': 42.0, 'phone_bill_regularity': 38.0, 'geo_stability_score': 55.0, 'ecommerce_payment_score': 30.0, 'social_network_risk': 0.45, 'app_usage_score': 35.0}
]

for p in personas:
    traj_res = requests.post('http://localhost:8000/trajectory', json=p)
    if traj_res.status_code == 200:
        gain = traj_res.json().get('total_potential_gain', 0)
    else:
        gain = 'error'
        
    res = requests.post('http://localhost:8000/fraud-check/with-score', json=p)
    if res.status_code == 200:
        data = res.json()
        print(f"{p['id']:<8} Score: {data['credit_score']['scoreseva_score']:<4} Band: {data['credit_score']['band']:<10} Fraud: {data['fraud_check']['verdict']:<15} RedFlags: {data['fraud_check']['red_flag_count']}  Gain: {gain}")
    else:
        print(f"{p['id']:<8} Failed {res.status_code} {res.text}")
