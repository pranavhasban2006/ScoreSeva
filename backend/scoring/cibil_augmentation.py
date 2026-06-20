def augment_with_cibil(applicant_features: dict, cibil_features: dict) -> dict:
    """
    Blends CIBIL score into the final scoring as a weighted input.
    Handles FOUND, THIN_FILE, and NOT_FOUND (credit invisible) cases explicitly.
    """
    file_status = cibil_features.get("file_status", "NOT_FOUND")
    cibil_score = cibil_features.get("cibil_score")
    
    # Defaults
    cibil_weight = 0.0
    alt_data_weight = 1.0
    bureau_confidence = "NONE"
    scoring_method = "ALTERNATIVE_DATA_ONLY"
    conflict_flag = False
    conflict_reason = None
    
    financial_stress_score = applicant_features.get("financial_stress_score", 0)
    
    if file_status == "FOUND" and cibil_score is not None:
        cibil_weight = 0.35
        alt_data_weight = 0.65
        bureau_confidence = "HIGH"
        scoring_method = "HYBRID"
        
        # Flag conflicts: Bureau strong but alt-data shows stress
        if cibil_score > 750 and financial_stress_score > 70:
            conflict_flag = True
            conflict_reason = "Bureau score strong but recent cash flow stressed"
            
    elif file_status == "THIN_FILE" and cibil_score is not None:
        cibil_weight = 0.15
        alt_data_weight = 0.85
        bureau_confidence = "LOW"
        scoring_method = "HYBRID_THIN"
        
    elif file_status == "NOT_FOUND" or cibil_score is None:
        cibil_weight = 0.0
        alt_data_weight = 1.0
        bureau_confidence = "NONE"
        scoring_method = "ALTERNATIVE_DATA_ONLY"
        explanation = "No bureau history found. Score is based entirely on income stability, transaction behavior, and repayment-relevant alternative signals."
        
    # Calculate points if we were given a final score from the main pipeline.
    # In the router, we actually just need to return weights and logic, the router
    # will combine with XGBoost. But the prompt says return `cibil_contribution_points`
    # We will simulate this by using the cibil_score * cibil_weight if it exists,
    # and the caller will use these weights to blend the final score.
    # Actually, let's just return the weights and confidence. The router can calculate points.
    
    result = {
        "cibil_weight": cibil_weight,
        "alt_data_weight": alt_data_weight,
        "bureau_confidence": bureau_confidence,
        "scoring_method": scoring_method,
        "conflict_flag": conflict_flag,
        "conflict_reason": conflict_reason,
        "cibil_contribution_points": int(cibil_score * cibil_weight) if cibil_score else 0,
        "alt_data_contribution_points": 0 # This will be filled in by the router
    }
    
    if file_status == "NOT_FOUND" or cibil_score is None:
        result["explanation"] = "No bureau history found. Score is based entirely on income stability, transaction behavior, and repayment-relevant alternative signals."
        
    return result
