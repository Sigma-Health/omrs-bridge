"""
Schemas for chief complaint notes.
"""

from pydantic import BaseModel, model_validator
from typing import Optional, List
from datetime import datetime


class ChiefComplaintInput(BaseModel):
    """
    A single chief complaint group to record.

    Supply either value_coded (coded concept 57385) or value_text (free-text concept 30201),
    not both. duration_value and duration_unit_coded are required together.
    """

    value_coded: Optional[int] = None
    value_text: Optional[str] = None
    duration_value: Optional[float] = None
    duration_unit_coded: Optional[int] = None
    obs_datetime: Optional[datetime] = None
    comments: Optional[str] = None

    @model_validator(mode="after")
    def validate_complaint(self) -> "ChiefComplaintInput":
        if self.value_coded is None and self.value_text is None:
            raise ValueError(
                "Either value_coded or value_text must be provided for chief complaint"
            )
        if self.value_coded is not None and self.value_text is not None:
            raise ValueError("Provide either value_coded or value_text, not both")
        if (self.duration_value is None) != (self.duration_unit_coded is None):
            raise ValueError(
                "duration_value and duration_unit_coded must both be provided or both omitted"
            )
        return self


class ChiefComplaintCreate(BaseModel):
    """Request body for creating a chief complaint."""

    visit_id: Optional[int] = None
    visit_uuid: Optional[str] = None
    creator: int
    location_id: int
    provider_id: Optional[int] = None
    encounter_role_id: Optional[int] = 1
    hpi: Optional[str] = None
    obs_datetime: Optional[datetime] = None
    complaint: ChiefComplaintInput

    @model_validator(mode="after")
    def require_visit_identifier(self) -> "ChiefComplaintCreate":
        if not self.visit_id and not self.visit_uuid:
            raise ValueError("Either visit_id or visit_uuid must be provided")
        return self


class ChiefComplaintObsItem(BaseModel):
    """A single obs within a chief complaint group as returned in a response."""

    obs_id: int
    uuid: str
    concept_id: int
    concept_name: Optional[str] = None
    value_coded: Optional[int] = None
    value_coded_name: Optional[str] = None
    value_text: Optional[str] = None
    value_numeric: Optional[float] = None
    obs_datetime: Optional[datetime] = None
    comments: Optional[str] = None

    class Config:
        from_attributes = True


class ChiefComplaintGroupResponse(BaseModel):
    """A complete chief complaint obs group (57422 + children)."""

    group_obs_id: int
    group_uuid: str
    encounter_id: int
    encounter_uuid: str
    visit_id: int
    obs_datetime: Optional[datetime] = None
    complaint: Optional[ChiefComplaintObsItem] = None
    duration: Optional[ChiefComplaintObsItem] = None
    duration_unit: Optional[ChiefComplaintObsItem] = None
    hpi: Optional[ChiefComplaintObsItem] = None


class ChiefComplaintVisitResponse(BaseModel):
    """All chief complaint groups for a visit."""

    encounter_id: int
    encounter_uuid: str
    visit_id: int
    complaints: List[ChiefComplaintGroupResponse]


class ChiefComplaintUpdate(BaseModel):
    """Fields that can be updated on an existing chief complaint group."""

    value_coded: Optional[int] = None
    value_text: Optional[str] = None
    duration_value: Optional[float] = None
    duration_unit_coded: Optional[int] = None
    hpi: Optional[str] = None
    obs_datetime: Optional[datetime] = None
    comments: Optional[str] = None
    editor: Optional[int] = None


class ChiefComplaintVoid(BaseModel):
    """Optional body for voiding a chief complaint group."""

    void_reason: Optional[str] = None
    voided_by: Optional[int] = None
