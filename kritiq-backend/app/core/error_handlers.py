# Sayeed domain - Custom error handling middleware or exception handlers
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

def register_error_handlers(app: FastAPI):
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error_code": "INTERNAL_ERROR", "message": str(exc)},
        )
