from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    # App
    app_name: str = "ScoreSeva API"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Model paths
    xgboost_model_path: str = "saved_models/xgboost_scorer.pkl"
    feature_cols_path: str = "saved_models/feature_columns.pkl"
    label_encoders_path: str = "saved_models/label_encoders.pkl"
    nlp_model_path: str = "saved_models/nlp_psychometric.pkl"
    fraud_model_path: str = "saved_models/fraud_detector.pkl"
    trajectory_model_path: str = "saved_models/trajectory_predictor.pkl"

    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"

    # Rate limiting
    max_requests_per_minute: int = 60

    # API Keys
    gemini_api_key: str = ""

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
