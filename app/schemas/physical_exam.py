"""
Schemas for physical examination note creation.
"""

from pydantic import BaseModel, model_validator, field_validator
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
    editor: Optional[int] = None


class ExamNoteVoid(BaseModel):
    """Optional body for voiding a physical examination note."""

    void_reason: Optional[str] = None
    voided_by: Optional[int] = None


class PhysicalExamCreate(BaseModel):
    """Request body for creating physical examination notes."""

    visit_id: Optional[int] = None
    visit_uuid: Optional[str] = None
    creator: int
    location_id: int
    provider_id: Optional[int] = None
    encounter_role_id: Optional[int] = 1
    notes: List[ExamNoteInput]

    @model_validator(mode="after")
    def require_visit_identifier(self) -> "PhysicalExamCreate":
        if not self.visit_id and not self.visit_uuid:
            raise ValueError("Either visit_id or visit_uuid must be provided")
        return self

    @field_validator("notes")
    @classmethod
    def notes_must_not_be_empty(cls, v: List[ExamNoteInput]) -> List[ExamNoteInput]:
        if not v:
            raise ValueError("notes must contain at least one entry")
        return v


class PhysicalExamResponse(BaseModel):
    """Response after creating physical examination notes."""

    encounter_id: int
    encounter_uuid: str
    visit_id: int
    created: bool
    observations: List[VitalSign]


class PhysicalExamReadResponse(BaseModel):
    """Read-only physical examination response (no created field)."""

    encounter_id: int
    encounter_uuid: str
    visit_id: int
    observations: List[VitalSign]
