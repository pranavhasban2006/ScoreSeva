import pandas as pd
import numpy as np
import joblib
import os
import warnings
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import IsolationForest, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score

warnings.filterwarnings('ignore')

def main():
    print("Loading data...")
    df = pd.read_csv('d:/Projects/ScoreSeva/data/scoreseva_training_data.csv')
    
    print("Applying schema changes...")
    df.drop(columns=['geo_stability_score', 'social_network_risk'], inplace=True, errors='ignore')
    
    if 'app_usage_score' in df.columns and 'ecommerce_payment_score' in df.columns:
        df['digital_payment_activity_score'] = ((df['app_usage_score'] + df['ecommerce_payment_score']) / 2).round(1)
        df.drop(columns=['app_usage_score', 'ecommerce_payment_score'], inplace=True)
    
    df.rename(columns={'phone_bill_regularity': 'phone_bill_regularity_score'}, inplace=True)
    
    os.makedirs('d:/Projects/ScoreSeva/backend/saved_models', exist_ok=True)
    
    # ---------------------------------------------------------
    # 1. XGBoost Scorer Retraining
    # ---------------------------------------------------------
    print("Retraining XGBoost model...")
    EXCLUDE_COLS = [
        'TARGET', 'scoreseva_score',
        'city', 'state', 'preferred_language', 'income_bracket'
    ]

    CATEGORICAL_COLS = [
        'gender', 'education_level', 'occupation',
        'income_source', 'family_status'
    ]

    df_model = df.copy()
    label_encoders = {}
    for col in CATEGORICAL_COLS:
        le = LabelEncoder()
        df_model[col] = le.fit_transform(df_model[col].astype(str))
        label_encoders[col] = le

    FEATURE_COLS = [c for c in df_model.columns if c not in EXCLUDE_COLS]
    
    X = df_model[FEATURE_COLS]
    y = df_model['TARGET']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

    xgb_model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        use_label_encoder=False,
        eval_metric='auc',
        early_stopping_rounds=20,
        random_state=42,
        n_jobs=-1
    )

    xgb_model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        verbose=False
    )

    joblib.dump(xgb_model, 'd:/Projects/ScoreSeva/backend/saved_models/xgboost_scorer.pkl')
    joblib.dump(label_encoders, 'd:/Projects/ScoreSeva/backend/saved_models/label_encoders.pkl')
    joblib.dump(FEATURE_COLS, 'd:/Projects/ScoreSeva/backend/saved_models/feature_columns.pkl')
    print(f"XGBoost model saved. Features used: {len(FEATURE_COLS)}")

    # ---------------------------------------------------------
    # 2. Fraud Detector Retraining
    # ---------------------------------------------------------
    print("Retraining Fraud Detector...")
    df_fraud = df.copy()

    df_fraud['income_upi_mismatch'] = (
        (df_fraud['annual_income'] / (df_fraud['annual_income'].max() + 1)) -
        (df_fraud['upi_consistency_score'] / 100)
    ).round(4)

    df_fraud['loan_to_income_ratio'] = (
        df_fraud['loan_amount'] / (df_fraud['annual_income'] + 1)
    ).round(4)

    df_fraud['emi_stress_ratio'] = (
        df_fraud['monthly_emi'] / ((df_fraud['annual_income'] / 12) + 1)
    ).round(4)

    df_fraud['identity_instability'] = (
        (1 / (df_fraud['id_stability_years'] + 0.1)) *
        (1 - df_fraud['digital_payment_activity_score'] / 100)
    ).round(4)

    df_fraud['credit_hunger_index'] = (
        df_fraud['credit_enquiries_last_year'] * (1 - df_fraud['ext_credit_score_2'])
    ).round(4)

    df_fraud['digital_consistency_index'] = (
        (df_fraud['upi_consistency_score'] +
         df_fraud['phone_bill_regularity_score'] +
         df_fraud['digital_payment_activity_score']) / 300
    ).round(4)

    df_fraud['employment_income_plausibility'] = (
        df_fraud['employment_years'] /
        (df_fraud['annual_income'] / (df_fraud['annual_income'].median() + 1) + 0.1)
    ).clip(0, 10).round(4)

    FRAUD_FEATURES = [
        'income_upi_mismatch',
        'loan_to_income_ratio',
        'emi_stress_ratio',
        'identity_instability',
        'credit_hunger_index',
        'digital_consistency_index',
        'employment_income_plausibility',
        'credit_enquiries_last_year',
        'upi_consistency_score',
        'ext_credit_score_2',
    ]

    X_fraud = df_fraud[FRAUD_FEATURES].fillna(0)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_fraud)

    iso_forest = IsolationForest(
        n_estimators=200,
        contamination=0.05,
        max_samples='auto',
        random_state=42,
        n_jobs=-1
    )

    iso_forest.fit(X_scaled)
    
    df_fraud['isolation_flag'] = iso_forest.predict(X_scaled) == -1
    raw_scores = iso_forest.score_samples(X_scaled)
    
    fraud_pipeline_obj = {
        'isolation_forest': iso_forest,
        'scaler': scaler,
        'feature_cols': FRAUD_FEATURES,
        'score_min': float(raw_scores.min()),
        'score_max': float(raw_scores.max()),
    }

    joblib.dump(fraud_pipeline_obj, 'd:/Projects/ScoreSeva/backend/saved_models/fraud_detector.pkl')
    print("Fraud Detector saved.")

    # ---------------------------------------------------------
    # 3. Trajectory Predictor Retraining
    # ---------------------------------------------------------
    print("Retraining Trajectory Predictor...")
    
    def simulate_trajectory(row, months: int, improvement: bool = False) -> float:
        base_score = float(row['scoreseva_score'])
        employment_drift = min(row['employment_years'] / 10, 1.0) * 0.3
        age_factor = min(row['age_years'] / 50, 1.0) * 0.2
        debt_drag = row['loan_to_income_ratio'] * -0.5 if 'loan_to_income_ratio' in row.index else 0
        enquiry_drag = row['credit_enquiries_last_year'] * -2
        monthly_natural = (employment_drift + age_factor + debt_drag + enquiry_drag) * (months / 12)

        if not improvement:
            np.random.seed(42 + int(base_score))
            noise = np.random.normal(0, 5)
            future_score = base_score + monthly_natural + noise
        else:
            phone_gap = max(0, 85 - row['phone_bill_regularity_score'])
            phone_boost = (phone_gap / 100) * 40 * (months / 12)

            upi_gap = max(0, 80 - row['upi_consistency_score'])
            upi_boost = (upi_gap / 100) * 35 * (months / 12)
            
            digital_gap = max(0, 70 - row['digital_payment_activity_score'])
            digital_boost = (digital_gap / 100) * 40 * (months / 12)

            enquiry_improvement = row['credit_enquiries_last_year'] * 3

            total_boost = (phone_boost + upi_boost + digital_boost + enquiry_improvement)
            headroom = max(0, 900 - base_score)
            effective_boost = total_boost * (headroom / 600)
            
            np.random.seed(42 + int(base_score) + 1)
            noise = np.random.normal(0, 3)
            future_score = (base_score + monthly_natural + effective_boost + noise)

        return float(np.clip(future_score, 300, 900))

    df['loan_to_income_ratio'] = (df['loan_amount'] / (df['annual_income'] + 1))

    for months in [6, 12, 24]:
        df[f'score_t{months}_improved'] = df.apply(
            lambda r: simulate_trajectory(r, months, improvement=True), axis=1
        )

    PREDICTOR_FEATURES = [
        'scoreseva_score',
        'upi_consistency_score',
        'phone_bill_regularity_score',
        'digital_payment_activity_score',
        'ext_credit_score_2',
        'employment_years',
        'id_stability_years',
        'age_years',
        'annual_income',
        'loan_to_income_ratio',
        'credit_enquiries_last_year',
        'num_children',
        'owns_property',
    ]

    TARGET_COL = 'score_t12_improved'
    X_traj = df[PREDICTOR_FEATURES].fillna(0)
    y_traj = df[TARGET_COL]

    X_train_t, X_test_t, y_train_t, y_test_t = train_test_split(
        X_traj, y_traj, test_size=0.20, random_state=42
    )

    gbr = GradientBoostingRegressor(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.8,
        min_samples_leaf=20,
        random_state=42,
    )

    gbr.fit(X_train_t, y_train_t)

    y_pred_t = gbr.predict(X_test_t)
    mae = mean_absolute_error(y_test_t, y_pred_t)
    r2 = r2_score(y_test_t, y_pred_t)

    trajectory_pipeline = {
        'model': gbr,
        'feature_cols': PREDICTOR_FEATURES,
        'mae': mae,
        'r2': r2,
    }

    joblib.dump(trajectory_pipeline, 'd:/Projects/ScoreSeva/backend/saved_models/trajectory_predictor.pkl')
    print("Trajectory Predictor saved.")

if __name__ == "__main__":
    main()
