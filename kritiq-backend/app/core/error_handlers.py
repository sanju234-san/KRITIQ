# Sayeed domain - Custom error handling middleware or exception handlers
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger("app")

def register_error_handlers(app: FastAPI):
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception occurred: %s", str(exc), exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred. Please try again later."
            },
        )

