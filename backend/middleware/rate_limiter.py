"""
rate_limiter.py
In-memory sliding window rate limiter middleware for ScoreSeva API.
Limits each client IP to MAX_REQUESTS_PER_MINUTE requests per minute.
Uses a deque per IP — no Redis required for hackathon deployment.
"""

import time
import logging
from collections import defaultdict, deque
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from config import get_settings

logger   = logging.getLogger("scoreseva.ratelimit")
settings = get_settings()

# Global in-memory store: IP → deque of request timestamps
_request_store: dict[str, deque] = defaultdict(deque)

EXEMPT_PATHS = {"/", "/health", "/health/ping", "/health/uptime", "/docs",
                "/redoc", "/openapi.json"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health and docs endpoints
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        client_ip = request.client.host or "unknown"
        now       = time.time()
        window    = 60.0  # 1 minute sliding window
        limit     = settings.max_requests_per_minute

        # Evict timestamps older than window
        dq = _request_store[client_ip]
        while dq and dq[0] < now - window:
            dq.popleft()

        if len(dq) >= limit:
            logger.warning(
                f"Rate limit exceeded — IP: {client_ip} | "
                f"Path: {request.url.path} | "
                f"Requests in last 60s: {len(dq)}"
            )
            return Response(
                content='{"error":"rate_limit_exceeded",'
                        '"message":"Too many requests. '
                        'Limit is 60 per minute.",'
                        '"retry_after_seconds":60}',
                status_code=429,
                media_type="application/json",
                headers={"Retry-After": "60",
                         "X-RateLimit-Limit": str(limit),
                         "X-RateLimit-Remaining": "0"},
            )

        dq.append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"]     = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(limit - len(dq))
        return response
