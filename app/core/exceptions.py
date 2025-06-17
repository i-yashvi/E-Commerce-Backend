from fastapi.responses import JSONResponse
from fastapi import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logger import logger  


async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP error: {exc.detail} - Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "code": exc.status_code
        }
    )

async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception at {request.url.path}: {repr(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal Server Error",
            "code": 500
        }
    )
