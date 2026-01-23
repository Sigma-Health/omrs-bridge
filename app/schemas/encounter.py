"""
Encounter schemas.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EncounterBase(BaseModel):
    """Base schema for encounter data"""

    encounter_type: Optional[int] = None
    patient_id: Optional[int] = None
    location_id: Optional[int] = None
    form_id: Optional[int] = None
    encounter_datetime: Optional[datetime] = None
    visit_id: Optional[int] = None
    voided: Optional[bool] = None
    void_reason: Optional[str] = None


class EncounterCreate(EncounterBase):
    """Schema for creating encounters (POST) - required fields"""

    creator: int
    encounter_type: int
    patient_id: int
    # Optional fields
    location_id: Optional[int] = None
    form_id: Optional[int] = None
    encounter_datetime: Optional[datetime] = None
    visit_id: Optional[int] = None


class EncounterUpdate(EncounterBase):
    """Schema for updating encounters (PATCH)"""

    pass


class EncounterReplace(EncounterBase):
    """Schema for replacing encounters (PUT) - all fields required"""

    creator: int
    encounter_type: int
    patient_id: int
    location_id: int
    form_id: int
    visit_id: int


class EncounterResponse(EncounterBase):
    """Schema for encounter responses"""

    encounter_id: int
    creator: int
    date_created: datetime
    uuid: str
    voided_by: Optional[int] = None
    date_voided: Optional[datetime] = None
    changed_by: Optional[int] = None
    date_changed: Optional[datetime] = None

    class Config:
        from_attributes = True


class EncounterUpdateResponse(BaseModel):
    """Schema for encounter update response"""

    success: bool
    message: str
    encounter_id: int
    updated_fields: list[str]
    encounter: Optional[EncounterResponse] = None
