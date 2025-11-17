from typing import Any, Dict
from fastapi import status
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base application error with code and status."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}

    def to_response(self) -> JSONResponse:
        body = {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }
        return JSONResponse(status_code=self.status_code, content=body)
