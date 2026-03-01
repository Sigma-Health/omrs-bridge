"""
Schemas for physical examination note creation.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from .vitals import VitalSign


class ExamNoteInput(BaseModel):
    """A single examination note observation to record."""

    value_text: str
    concept_id: Optional[int] = None
    comments: Optional[str] = None
    obs_datetime: Optional[datetime] = None


class ExamNoteUpdate(BaseModel):
    """Fields that can be updated on an existing examination note."""

    value_text: Optional[str] = None
    comments: Optional[str] = None
    obs_datetime: Optional[datetime] = None


class PhysicalExamCreate(BaseModel):
    """Request body for creating physical examination notes."""

    visit_id: Optional[int] = None
    visit_uuid: Optional[str] = None
    creator: int
    location_id: int
    provider_id: Optional[int] = None
    encounter_role_id: Optional[int] = 1
    notes: List[ExamNoteInput]


class PhysicalExamResponse(BaseModel):
    """Response after creating physical examination notes."""

    encounter_id: int
    encounter_uuid: str
    visit_id: int
    created: bool
    observations: List[VitalSign]
