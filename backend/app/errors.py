"""Custom errors and global exception handler."""
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class APIError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status: int = 400,
        details: dict | None = None,
    ):
        self.code = code
        self.message = message
        self.status = status
        self.details = details or {}
        super().__init__(message)


def _envelope(code: str, message: str, details: dict) -> dict:
    return {
        "data": None,
        "meta": {},
        "errors": [{"code": code, "message": message, "details": details}],
    }


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status,
        content=_envelope(exc.code, exc.message, exc.details),
    )


async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    code_map = {
        401: "AUTH_TOKEN_INVALID",
        403: "PERMISSION_DENIED",
        404: "ENTITY_NOT_FOUND",
        409: "CONFLICT",
        413: "DOCUMENT_TOO_LARGE",
        415: "DOCUMENT_UNSUPPORTED_TYPE",
        422: "VALIDATION_ERROR",
    }
    code = code_map.get(exc.status_code, "HTTP_ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content=_envelope(code, str(exc.detail), {}),
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=_envelope("VALIDATION_ERROR", "Invalid payload", {"errors": exc.errors()}),
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=_envelope("INTERNAL_ERROR", "Unexpected server error", {}),
    )


def install_error_handlers(app: FastAPI) -> None:
    """Register the demo-extras envelope handler for APIError only.

    Main's existing AppError handler stays untouched. We do NOT install a
    generic HTTPException handler here — main's tests rely on the default
    `{"detail": "..."}` shape for auth/validation failures.
    """
    app.add_exception_handler(APIError, api_error_handler)
