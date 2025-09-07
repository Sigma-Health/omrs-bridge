"""
Visit schemas.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PersonInfo(BaseModel):
    """Schema for person information (patient)"""

    person_id: int
    uuid: str
    name: Optional[str] = None
    gender: Optional[str] = None
    birthdate: Optional[datetime] = None


class VisitBase(BaseModel):
    """Base schema for visit data"""

    patient_id: Optional[int] = None
    visit_type_id: Optional[int] = None
    date_started: Optional[datetime] = None
    date_stopped: Optional[datetime] = None
    indication_concept_id: Optional[int] = None
    location_id: Optional[int] = None
    voided: Optional[bool] = None
    voided_by: Optional[int] = None
    date_voided: Optional[datetime] = None
    void_reason: Optional[str] = None


class VisitCreate(VisitBase):
    """Schema for creating visits (POST) - required fields"""

    creator: int
    patient_id: int
    visit_type_id: int
    # Optional fields
    date_started: Optional[datetime] = None
    date_stopped: Optional[datetime] = None
    indication_concept_id: Optional[int] = None
    location_id: Optional[int] = None


class VisitUpdate(VisitBase):
    """Schema for updating visits (PATCH)"""

    pass


class VisitReplace(VisitBase):
    """Schema for replacing visits (PUT) - all fields required"""

    creator: int
    patient_id: int
    visit_type_id: int
    location_id: int
    indication_concept_id: int


class VisitResponse(VisitBase):
    """Schema for visit responses"""

    visit_id: int
    creator: int
    date_created: datetime
    uuid: str
    changed_by: Optional[int] = None
    date_changed: Optional[datetime] = None
    patient_info: Optional[PersonInfo] = None

    class Config:
        from_attributes = True


class VisitUpdateResponse(BaseModel):
    """Schema for visit update response"""

    success: bool
    message: str
    visit_id: int
    updated_fields: list[str]
    visit: Optional[VisitResponse] = None
