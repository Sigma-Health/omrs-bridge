"""
Observation (Obs) schemas.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ObsBase(BaseModel):
    """Base schema for observation data"""

    person_id: Optional[int] = None
    concept_id: Optional[int] = None
    encounter_id: Optional[int] = None
    order_id: Optional[int] = None
    obs_datetime: Optional[datetime] = None
    location_id: Optional[int] = None
    obs_group_id: Optional[int] = None
    accession_number: Optional[str] = None
    value_group_id: Optional[int] = None
    value_coded: Optional[int] = None
    value_coded_name_id: Optional[int] = None
    value_drug: Optional[int] = None
    value_datetime: Optional[datetime] = None
    value_numeric: Optional[float] = None
    value_modifier: Optional[str] = None
    value_text: Optional[str] = None
    value_complex: Optional[str] = None
    comments: Optional[str] = None
    voided: Optional[bool] = None
    voided_by: Optional[int] = None
    date_voided: Optional[datetime] = None
    void_reason: Optional[str] = None
    previous_version: Optional[int] = None
    form_namespace_and_path: Optional[str] = None
    status: Optional[str] = None
    interpretation: Optional[str] = None


class ObsCreate(ObsBase):
    """Schema for creating observations (POST) - required fields"""

    person_id: int
    concept_id: int
    encounter_id: int
    creator: int
    # Optional fields for different value types
    value_coded: Optional[int] = None
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    value_datetime: Optional[datetime] = None
    value_drug: Optional[int] = None
    value_complex: Optional[str] = None
    # Other optional fields
    order_id: Optional[int] = None
    obs_datetime: Optional[datetime] = None
    location_id: Optional[int] = None
    obs_group_id: Optional[int] = None
    accession_number: Optional[str] = None
    value_group_id: Optional[int] = None
    value_coded_name_id: Optional[int] = None
    value_modifier: Optional[str] = None
    comments: Optional[str] = None
    form_namespace_and_path: Optional[str] = None
    status: Optional[str] = None
    interpretation: Optional[str] = None


class ObsUpdate(ObsBase):
    """Schema for updating observations (PATCH)"""

    pass


class ObsReplace(ObsBase):
    """Schema for replacing observations (PUT) - all fields required"""

    person_id: int
    concept_id: int
    encounter_id: int
    creator: int
    uuid: str


class ObsResponse(ObsBase):
    """Schema for observation responses"""

    obs_id: int
    creator: int
    date_created: datetime
    uuid: str

    class Config:
        from_attributes = True


class ObsUpdateResponse(BaseModel):
    """Schema for update response"""

    success: bool
    message: str
    obs_id: int
    updated_fields: list[str]
    obs: Optional[ObsResponse] = None
