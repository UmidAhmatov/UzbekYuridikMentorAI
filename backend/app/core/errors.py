from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        first_error = exc.errors()[0] if exc.errors() else {}
        location = ".".join(str(item) for item in first_error.get("loc", []) if item != "body")
        message = first_error.get("msg", "Kiritilgan ma'lumotlarni tekshiring.")
        detail = f"{location}: {message}" if location else message
        return JSONResponse(
            status_code=422,
            content={"detail": detail, "error_code": "validation_error"},
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception("Unhandled API error on %s", request.url.path, exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Serverda kutilmagan xato yuz berdi. Birozdan keyin qayta urinib ko'ring.",
                "error_code": "internal_error",
            },
        )

