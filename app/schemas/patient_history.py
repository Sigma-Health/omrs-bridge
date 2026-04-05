"""
Schemas for patient history and summary responses.
"""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

from .chief_complaint import ChiefComplaintGroupResponse
from .order import OrderResponse
from .vitals import VitalSign


HistoryType = Literal["all", "complaint", "examination", "orders", "treatments"]


class PatientHistoryVisitGroup(BaseModel):
    """History grouped under a single visit."""

    visit_id: int
    visit_uuid: str
    visit_date_started: Optional[datetime] = None
    visit_date_stopped: Optional[datetime] = None
    complaints: List[ChiefComplaintGroupResponse] = Field(default_factory=list)
    examination_notes: List[VitalSign] = Field(default_factory=list)
    orders: List[OrderResponse] = Field(default_factory=list)
    treatments: List[OrderResponse] = Field(default_factory=list)


class PatientHistoryCounts(BaseModel):
    """Category counts for patient history."""

    visits: int
    complaints: int
    examination_notes: int
    orders: int
    treatments: int


class PatientHistoryResponse(BaseModel):
    """Patient history response grouped by visit."""

    patient_id: int
    patient_uuid: str
    requested_type: HistoryType
    counts: PatientHistoryCounts
    visits: List[PatientHistoryVisitGroup]


class PatientHistorySummaryResponse(BaseModel):
    """High-level patient history summary response."""

    patient_id: int
    patient_uuid: str
    summary: str
    max_items_per_category: int
    counts: PatientHistoryCounts
    visits: List[PatientHistoryVisitGroup]
