"""
error_handler.py
Structured error response handlers for ScoreSeva API.
Ensures every error — validation, not found, server crash —
returns a consistent JSON shape that the frontend can parse.
"""

import logging
import traceback
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

logger = logging.getLogger("scoreseva.errors")


def _build_error_response(
    status_code: int,
    error_code: str,
    message: str,
    detail=None,
    path: str = "",
) -> JSONResponse:
    body = {
        "status_code": status_code,
        "error":       error_code,
        "message":     message,
        "path":        path,
    }
    if detail is not None:
        body["detail"] = detail
    return JSONResponse(status_code=status_code, content=body)


async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    logger.warning(
        f"HTTP {exc.status_code} — {request.method} "
        f"{request.url.path} — {exc.detail}"
    )
    return _build_error_response(
        status_code=exc.status_code,
        error_code=f"http_{exc.status_code}",
        message=str(exc.detail) if isinstance(exc.detail, str)
                else "Request failed",
        detail=exc.detail if not isinstance(exc.detail, str) else None,
        path=request.url.path,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = []
    for err in exc.errors():
        field = " → ".join(str(loc) for loc in err["loc"])
        errors.append({"field": field, "message": err["msg"],
                       "type": err["type"]})
    logger.warning(
        f"Validation error — {request.method} {request.url.path} "
        f"— {len(errors)} field(s) invalid"
    )
    return _build_error_response(
        status_code=422,
        error_code="validation_error",
        message=f"{len(errors)} field(s) failed validation.",
        detail=errors,
        path=request.url.path,
    )


async def pydantic_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    return _build_error_response(
        status_code=422,
        error_code="schema_error",
        message="Request schema validation failed.",
        detail=exc.errors(),
        path=request.url.path,
    )


async def global_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    logger.error(
        f"Unhandled exception — {request.method} {request.url.path}\n"
        + traceback.format_exc()
    )
    return _build_error_response(
        status_code=500,
        error_code="internal_server_error",
        message="An unexpected error occurred. Our team has been notified.",
        path=request.url.path,
    )
