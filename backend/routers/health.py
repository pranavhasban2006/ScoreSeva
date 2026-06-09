"""
health.py
Health check endpoints for ScoreSeva API.
Used by load balancers, monitoring tools, and demo judges
to confirm the API is live and all models are loaded.
"""

import time
from fastapi import APIRouter, Depends
from schemas.applicant import HealthResponse
from models.model_loader import get_registry, ModelRegistry
from config import get_settings, Settings

router = APIRouter(prefix="/health", tags=["Health"])

APP_START_TIME = time.time()


@router.get(
    "/",
    response_model=HealthResponse,
    summary="Basic health check",
    description="Returns API status and which ML models are loaded."
)
async def health_check(
    registry: ModelRegistry = Depends(get_registry),
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    """
    Returns:
    - status: 'healthy' if all models loaded, 'degraded' if some missing
    - models: dict showing which of the 6 models are loaded
    """
    model_status = {
        "xgboost_scorer":       registry.xgboost_model is not None,
        "feature_columns":      registry.feature_columns is not None,
        "label_encoders":       registry.label_encoders is not None,
        "nlp_psychometric":     registry.nlp_pipeline is not None,
        "fraud_detector":       registry.fraud_pipeline is not None,
        "trajectory_predictor": registry.trajectory_pipeline is not None,
    }

    all_loaded = all(model_status.values())
    status = "healthy" if all_loaded else "degraded"

    return HealthResponse(
        status=status,
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        models=model_status,
    )


@router.get(
    "/ping",
    summary="Simple liveness probe",
    description="Returns pong. Use this for basic uptime monitoring."
)
async def ping():
    """Lightest possible check — just confirms the server is alive."""
    return {"ping": "pong", "status": "alive"}


@router.get(
    "/uptime",
    summary="Server uptime",
    description="Returns how long the server has been running."
)
async def uptime():
    """Returns server uptime in seconds and a human-readable string."""
    uptime_seconds = round(time.time() - APP_START_TIME, 1)
    minutes = int(uptime_seconds // 60)
    seconds = int(uptime_seconds % 60)
    return {
        "uptime_seconds": uptime_seconds,
        "uptime_human": f"{minutes}m {seconds}s",
        "status": "running"
    }
