"""
main.py
ScoreSeva FastAPI application entry point — Phase 2F hardened version.

Start the server:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Swagger UI:  http://localhost:8000/docs
ReDoc:       http://localhost:8000/redoc
Demo guide:  http://localhost:8000/meta/demo-guide
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from config import get_settings
from models.model_loader import load_all_models
from middleware.logging import RequestLoggingMiddleware
from middleware.rate_limiter import RateLimitMiddleware
from middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    pydantic_exception_handler,
    global_exception_handler,
)
from routers import health, scoring, fraud, trajectory, nlp, meta, bank_statement, cibil_augmentation, anti_gaming, letters

# ── Logging setup ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger   = logging.getLogger("scoreseva.main")
settings = get_settings()


# ── Lifespan ──────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 60)
    logger.info(f"  {settings.app_name} v{settings.app_version}")
    logger.info(f"  Environment : {settings.app_env}")
    logger.info(f"  Rate limit  : {settings.max_requests_per_minute} req/min")
    logger.info("=" * 60)
    base_path = os.path.join(os.path.dirname(__file__), "saved_models")
    load_all_models(base_path=base_path)
    logger.info("✅ ScoreSeva API ready")
    yield
    logger.info("ScoreSeva API shutting down")


# ── App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
## ScoreSeva — AI-Driven Alternate Credit Scoring API

Scores **credit-invisible Indians** using alternative signals:
UPI behavior, phone bill regularity, geolocation stability,
NLP psychometrics, and social network risk analysis.

### Endpoints
| Method | Path | Description |
|---|---|---|
| POST | `/score/` | Credit score + risk band |
| POST | `/score/batch` | Batch score up to 50 applicants |
| POST | `/fraud-check/` | Fraud and anomaly detection |
| POST | `/fraud-check/with-score` | Score + fraud combined |
| POST | `/trajectory/` | 6/12/24-month score roadmap |
| GET  | `/trajectory/demo/{name}` | Demo persona (no body) |
| POST | `/nlp-score/` | NLP psychometric analysis |
| GET  | `/nlp-score/demo/{profile}` | Demo NLP profile (no body) |
| GET  | `/meta/demo-guide` | Live demo cheat sheet |
| GET  | `/health/` | API and model health |

### Score Bands
| Score | Band | Action |
|---|---|---|
| 750-900 | EXCELLENT | Approve — best rate |
| 650-749 | GOOD | Approve — standard rate |
| 550-649 | FAIR | Conditional approval |
| 450-549 | POOR | Decline or guarantor |
| 300-449 | VERY POOR | Decline |
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware (order matters: outermost first) ───────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# ── Exception handlers ────────────────────────────────────────────────
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, pydantic_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# ── Routers ───────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(scoring.router)
app.include_router(fraud.router)
app.include_router(trajectory.router)
app.include_router(nlp.router)
app.include_router(meta.router)
app.include_router(bank_statement.router)
app.include_router(cibil_augmentation.router)
app.include_router(anti_gaming.router)
app.include_router(letters.router)

# ── Root ──────────────────────────────────────────────────────────────
@app.get("/", tags=["Root"])
async def root():
    return {
        "app":         settings.app_name,
        "version":     settings.app_version,
        "status":      "running",
        "docs":        "/docs",
        "demo_guide":  "/meta/demo-guide",
        "health":      "/health",
        "endpoints":   "/meta/endpoints",
    }
