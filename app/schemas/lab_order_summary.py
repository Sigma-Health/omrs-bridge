"""
Lab order daily concept summary schemas.
"""

from typing import List

from pydantic import BaseModel


class ConceptOrderCount(BaseModel):
    """Order count for a single lab concept on a given day."""

    concept_name: str
    order_count: int


class DailyConceptOrders(BaseModel):
    """Concept order counts for one calendar day."""

    date: str
    display_date: str
    concepts: List[ConceptOrderCount]


class LabDailyConceptSummaryResponse(BaseModel):
    """Lab orders grouped by day and concept for a date range."""

    start_date: str
    end_date: str
    days: List[DailyConceptOrders]
