# ScoreSeva — AI-Driven Alternate Credit Scoring

## The Problem
190 million Indians are credit-invisible.
They have no CIBIL score, no credit history,
and no way to access formal loans — not because
they are bad borrowers, but because traditional
credit bureaus ignore their digital lives entirely.

## The Solution
ScoreSeva scores them using 22 alternative signals:
UPI payment consistency, phone bill regularity,
geolocation stability, NLP psychometric analysis,
and social network risk — producing a 300-900 score
that mirrors CIBIL convention but requires zero
prior credit history.

## Quick Start
bash start.sh

## Endpoints
Frontend  → http://localhost:5173
Backend   → http://localhost:8000
API Docs  → http://localhost:8000/docs
Demo Guide → http://localhost:8000/meta/demo-guide

## ML Stack
- XGBoost (credit scoring)
- Isolation Forest (fraud detection)
- Gradient Boosting Regressor (trajectory prediction)
- DistilBERT + Logistic Regression (NLP psychometrics)
- SHAP (explainability)

## Fairness
Bias audited across gender, age, region, and income.
Full report at data/bias_audit_report.json
