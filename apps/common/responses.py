from typing import Any, Optional
from pydantic import BaseModel

class StandardResponse(BaseModel):
    """Standardized API response envelope"""
    status: str
    message: str
    data: Optional[Any] = None

def success_response(data: Any = None, message: str = "Success") -> dict:
    """Helper to create a standard success response"""
    return {
        "status": "success",
        "message": message,
        "data": data
    }

def error_response(message: str = "Error", data: Any = None) -> dict:
    """Helper to create a standard error response"""
    return {
        "status": "error",
        "message": message,
        "data": data
    }
