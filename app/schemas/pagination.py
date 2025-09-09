"""
Pagination schemas for API responses.
"""

from pydantic import BaseModel
from typing import List, TypeVar, Generic, Optional

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata"""

    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""

    data: List[T]
    meta: PaginationMeta


class PaginationParams(BaseModel):
    """Pagination parameters"""

    skip: int = 0
    limit: int = 100

    @property
    def page(self) -> int:
        """Calculate current page number (1-based)"""
        return (self.skip // self.limit) + 1 if self.limit > 0 else 1

    @property
    def per_page(self) -> int:
        """Get items per page"""
        return self.limit
