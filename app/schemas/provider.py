"""
Provider schemas for API responses.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PersonNameInfo(BaseModel):
    """Schema for person name information"""

    person_name_id: int
    preferred: bool
    prefix: Optional[str] = None
    given_name: Optional[str] = None
    middle_name: Optional[str] = None
    family_name_prefix: Optional[str] = None
    family_name: Optional[str] = None
    family_name2: Optional[str] = None
    family_name_suffix: Optional[str] = None
    degree: Optional[str] = None
    full_name: Optional[str] = None  # Computed full name


class PersonInfo(BaseModel):
    """Schema for person information"""

    person_id: int
    uuid: str
    gender: Optional[str] = None
    birthdate: Optional[datetime] = None
    birthdate_estimated: Optional[bool] = None
    dead: Optional[bool] = None
    death_date: Optional[datetime] = None
    voided: Optional[bool] = None


class ProviderBase(BaseModel):
    """Base schema for provider data"""

    person_id: Optional[int] = None
    name: Optional[str] = None
    identifier: Optional[str] = None
    retired: Optional[bool] = None
    role_id: Optional[int] = None
    speciality_id: Optional[int] = None
    provider_role_id: Optional[int] = None


class ProviderResponse(ProviderBase):
    """Schema for provider responses with person and name information"""

    provider_id: int
    creator: int
    date_created: datetime
    uuid: str
    changed_by: Optional[int] = None
    date_changed: Optional[datetime] = None
    retired_by: Optional[int] = None
    date_retired: Optional[datetime] = None
    retire_reason: Optional[str] = None
    person: Optional[PersonInfo] = None
    person_name: Optional[PersonNameInfo] = None

    class Config:
        from_attributes = True


class ProviderListResponse(BaseModel):
    """Response schema for provider list queries"""

    providers: list[ProviderResponse]
    total_count: int
    skip: int
    limit: int

