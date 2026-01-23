"""
Base schemas and common utilities.
"""

from pydantic import BaseModel
from typing import Optional


class ErrorResponse(BaseModel):
    """Schema for error responses"""

    success: bool = False
    error: str
    detail: Optional[str] = None
