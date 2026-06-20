def generate_rejection_letter(applicant_name: str, final_score: int, primary_reasons: list, application_date: str) -> str:
    reasons_text = "\n".join([f"• {r['explanation']}" for r in primary_reasons])
    
    constructive_steps = []
    reasons_keys = [r['feature'] for r in primary_reasons]
    
    if "bounce_count" in reasons_keys:
        constructive_steps.append("• Maintaining 3-6 months of bounce-free transactions can improve future applications.")
    if "income_regularity_score" in reasons_keys or "annual_income" in reasons_keys:
        constructive_steps.append("• Building a more consistent income deposit pattern, even through smaller regular transfers, can help.")
    if "gaming_risk_score" in reasons_keys:
        constructive_steps.append("• Ensuring your submitted financial history accurately and organically reflects your standard behavior without staged activity.")
    if "credit_utilization_ratio" in reasons_keys:
        constructive_steps.append("• Reducing your existing credit utilization ratio below 30% will positively impact your score.")
        
    if not constructive_steps:
        constructive_steps.append("• Continuing to build a consistent digital transaction footprint.")
        constructive_steps.append("• Reducing existing debt obligations where possible.")
        
    steps_text = "\n".join(constructive_steps)
    
    return f"""ScoreSeva — Decision Notice
Date: {application_date}

Dear {applicant_name},

Thank you for your application to ScoreSeva. We have carefully reviewed your financial profile and alternative data signals. We regret to inform you that we are unable to approve your application at this time.

Your final ScoreSeva credit score was {final_score}. 

Our decision was primarily influenced by the following factors in your profile:
{reasons_text}

What you can do next:
{steps_text}

You have the right to request a manual human review of this automated decision. If you believe your data was interpreted incorrectly, please contact our support team.

Sincerely,
The ScoreSeva Team"""

def generate_approval_letter(applicant_name: str, final_score: int, strength_factors: list, application_date: str) -> str:
    factors_text = "\n".join([f"• {r['explanation']}" for r in strength_factors])
    
    return f"""ScoreSeva — Decision Notice
Date: {application_date}

Dear {applicant_name},

Congratulations! Thank you for your application to ScoreSeva. We have carefully reviewed your financial profile and are pleased to inform you that your application has been APPROVED.

Your final ScoreSeva credit score was an excellent {final_score}. 

Our decision was positively influenced by these strong factors in your profile:
{factors_text}

We are thrilled to be your financial partner and provide access to credit based on your actual financial behavior. 

Sincerely,
The ScoreSeva Team"""

def generate_review_letter(applicant_name: str, final_score: int, primary_reasons: list, application_date: str) -> str:
    reasons_text = "\n".join([f"• {r['explanation']}" for r in primary_reasons])
    
    return f"""ScoreSeva — Decision Notice
Date: {application_date}

Dear {applicant_name},

Thank you for your application to ScoreSeva. We have carefully reviewed your financial profile. At this time, your application requires further MANUAL REVIEW before a final decision can be made.

Your final ScoreSeva credit score was {final_score}. 

The automated system flagged the following areas that require human verification:
{reasons_text}

Our credit team will review your profile within 1-2 business days. We may reach out if any additional documentation is needed.

Sincerely,
The ScoreSeva Team"""

def generate_letter(applicant_name: str, decision: str, final_score: int, reason_codes: dict, application_date: str) -> dict:
    
    primary_reasons = reason_codes.get("primary_reasons", [])
    
    if decision == "REJECTED":
        letter_text = generate_rejection_letter(applicant_name, final_score, primary_reasons, application_date)
    elif decision == "APPROVED":
        letter_text = generate_approval_letter(applicant_name, final_score, primary_reasons, application_date)
    else:
        letter_text = generate_review_letter(applicant_name, final_score, primary_reasons, application_date)
        
    technical_appendix = []
    for r in primary_reasons:
        technical_appendix.append({
            "feature": r["feature"],
            "shap_value": r["shap_value"],
            "contribution_pct": r["contribution_pct"]
        })
        
    return {
        "letter_text": letter_text,
        "technical_appendix": technical_appendix,
        "decision": decision,
        "generated_date": application_date
    }
