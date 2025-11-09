"""
System-level schemas.
"""

from pydantic import BaseModel


class SearchIndexRebuildRequest(BaseModel):
    """Payload for triggering a search index rebuild."""

    async_mode: bool = True


class SearchIndexRebuildResponse(BaseModel):
    """Response describing outcome of a search index rebuild request."""

    success: bool
    message: str | None = None
