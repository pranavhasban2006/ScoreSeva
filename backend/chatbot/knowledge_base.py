SCORESEVA_PROJECT_KNOWLEDGE = """What ScoreSeva is and why: ScoreSeva is an AI-driven alternative credit scoring platform designed for the 190 million credit-invisible Indians who lack traditional bureau history. 

The core insight: Bureau-only lenders automatically reject applicants on a missing or thin CIBIL file alone, regardless of their actual financial behavior and capability to repay.

Tech stack: The platform is built with a Python/FastAPI backend, XGBoost with SHAP for explainability, a React/Vite frontend, and utilizes Isolation Forest, Gradient Boosting, DistilBERT, and Logistic Regression models.

The 4 major capabilities built:
1. Bank Statement Intelligence Engine: Parses transactions and extracts 15 behavioral features.
2. CIBIL Augmentation Layer: Blends bureau data with alternative data, weighted by file confidence (FOUND, THIN_FILE, NOT_FOUND), ensuring it never fully replaces bureau data.
3. Anti-Gaming Engine: Detects 7 behavioral signatures of score manipulation (salary injection, circular transactions, round-number bias, income gaps, tenure mismatches, reapplication patterns, dormant reactivation) and applies score penalties accordingly.
4. Rejection Letter Generator: Produces SHAP-derived plain-English reason codes and exports as PDF, ensuring decisions are explainable by design."""
