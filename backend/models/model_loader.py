"""
model_loader.py
Loads all 6 ScoreSeva ML models at application startup.
Uses a singleton pattern so models are loaded only once
and reused across all requests.
"""

import joblib
import os
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class ModelRegistry:
    """
    Holds all loaded ML models.
    Populated once at startup via load_all_models().
    """
    xgboost_model:        Optional[Any] = None
    feature_columns:      Optional[list] = None
    label_encoders:       Optional[dict] = None
    nlp_pipeline:         Optional[dict] = None
    fraud_pipeline:       Optional[dict] = None
    trajectory_pipeline:  Optional[dict] = None
    is_loaded:            bool = False


# Global singleton registry
registry = ModelRegistry()


def load_all_models(base_path: str = "saved_models") -> ModelRegistry:
    """
    Load all 6 ML model artifacts from disk.
    Called once at FastAPI startup.

    Args:
        base_path: Directory containing .pkl files
                   (relative to backend/)
    Returns:
        Populated ModelRegistry instance
    """
    global registry

    if registry.is_loaded:
        logger.info("Models already loaded — skipping reload")
        return registry

    logger.info("Loading ScoreSeva ML models...")

    model_files = {
        'xgboost_model':       'xgboost_scorer.pkl',
        'feature_columns':     'feature_columns.pkl',
        'label_encoders':      'label_encoders.pkl',
        'nlp_pipeline':        'nlp_psychometric.pkl',
        'fraud_pipeline':      'fraud_detector.pkl',
        'trajectory_pipeline': 'trajectory_predictor.pkl',
    }

    load_errors = []

    for attr, filename in model_files.items():
        path = os.path.join(base_path, filename)
        try:
            obj = joblib.load(path)
            setattr(registry, attr, obj)
            size_kb = os.path.getsize(path) / 1024
            logger.info(f"  ✅ Loaded {filename} ({size_kb:.1f} KB)")
        except FileNotFoundError:
            logger.error(f"  ❌ NOT FOUND: {path}")
            load_errors.append(filename)
        except Exception as e:
            logger.error(f"  ❌ ERROR loading {filename}: {e}")
            load_errors.append(filename)

    if load_errors:
        logger.warning(
            f"  ⚠️  {len(load_errors)} model(s) failed to load: "
            f"{load_errors}"
        )
        logger.warning(
            "  Endpoints depending on missing models will return 503."
        )
    else:
        logger.info("  🎉 All 6 models loaded successfully!")

    registry.is_loaded = True
    return registry


def get_registry() -> ModelRegistry:
    """FastAPI dependency — returns the global model registry."""
    return registry
