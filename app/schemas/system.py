"""
System / diagnostics schemas.
"""

from typing import Optional, List

from pydantic import BaseModel


class SearchIndexAvailabilityResponse(BaseModel):
    """Response model describing availability of the OpenMRS search index endpoint."""

    available: bool
    status_code: int
    reason: str
    requires_authentication: bool
    allowed_methods: Optional[List[str]] = None
    message: Optional[str] = None
