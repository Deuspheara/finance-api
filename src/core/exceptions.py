import logging

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

class BaseAPIError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundError(BaseAPIError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)

class ValidationError(BaseAPIError):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, 422)

class AuthenticationError(BaseAPIError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, 401)

class AuthorizationError(BaseAPIError):
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, 403)

async def api_exception_handler(request: Request, exc: BaseAPIError):
    logger.error(f"API Exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "status_code": exc.status_code}
    )

async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )
