"""
logging.py
Request/response logging middleware for ScoreSeva API.
Logs method, path, status code, and response time for every request.
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("scoreseva.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        duration_ms = round((time.time() - start_time) * 1000, 2)

        logger.info(
            f"{request.method} {request.url.path} "
            f"→ {response.status_code} "
            f"[{duration_ms}ms]"
        )

        # Add timing header to every response
        response.headers["X-Response-Time-Ms"] = str(duration_ms)
        return response
