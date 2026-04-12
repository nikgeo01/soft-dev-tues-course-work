from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.common.exceptions import AppException


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers for consistent API errors."""

    @app.exception_handler(AppException)
    async def app_exception_handler(
        _request: Request,
        exc: AppException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": {"code": exc.code, "message": exc.message}},
        )
