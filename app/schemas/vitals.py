"""
Vitals schemas for API responses.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class VitalSign(BaseModel):
    """Individual vital sign observation"""

    obs_id: int
    uuid: str
    obs_datetime: datetime
    concept_id: int
    concept_name: str
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    value_coded: Optional[int] = None
    value_coded_name: Optional[str] = None
    value_datetime: Optional[datetime] = None
    unit: Optional[str] = None
    comments: Optional[str] = None
    status: Optional[str] = None
    interpretation: Optional[str] = None
    # Additional context fields
    patient_id: Optional[int] = None
    patient_uuid: Optional[str] = None
    patient_name: Optional[str] = None
    encounter_id: Optional[int] = None
    encounter_uuid: Optional[str] = None
    encounter_datetime: Optional[datetime] = None
    visit_uuid: Optional[str] = None


class PatientVitalsInfo(BaseModel):
    """Patient information for vitals"""

    patient_id: int
    uuid: str
    name: str
    gender: Optional[str] = None
    birthdate: Optional[datetime] = None


class EncounterVitalsInfo(BaseModel):
    """Encounter information for vitals"""

    encounter_id: int
    uuid: str
    encounter_datetime: Optional[datetime] = None
    encounter_type: Optional[int] = None
    location_id: Optional[int] = None


class VisitVitals(BaseModel):
    """Vitals for a specific visit"""

    visit_id: int
    visit_uuid: str
    patient: PatientVitalsInfo
    encounter: EncounterVitalsInfo
    vitals: List[VitalSign]
    total_count: int


class VitalsResponse(BaseModel):
    """Response schema for vitals queries"""

    vitals: List[VitalSign]
    total_count: int
    skip: int
    limit: int


class VitalsByType(BaseModel):
    """Vitals grouped by type (e.g., Blood Pressure, Temperature)"""

    vital_type: str
    concept_id: int
    vitals: List[VitalSign]


class VitalsGroupedResponse(BaseModel):
    """Response schema for vitals grouped by type"""

    visit_id: int
    visit_uuid: str
    patient: PatientVitalsInfo
    encounter: EncounterVitalsInfo
    vitals_by_type: List[VitalsByType]
    total_count: int


class VitalCreate(BaseModel):
    """Schema for creating a vital sign observation"""

    person_id: int
    concept_id: int
    encounter_id: int
    creator: int
    # Value fields - at least one must be provided
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    value_coded: Optional[int] = None
    value_datetime: Optional[datetime] = None
    # Optional fields
    obs_datetime: Optional[datetime] = None
    location_id: Optional[int] = None
    obs_group_id: Optional[int] = None
    order_id: Optional[int] = None
    comments: Optional[str] = None
    status: Optional[str] = "FINAL"
    interpretation: Optional[str] = None
    value_modifier: Optional[str] = None
    form_namespace_and_path: Optional[str] = None


class VitalUpdate(BaseModel):
    """Schema for updating a vital sign observation (PATCH)"""

    # Value fields
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    value_coded: Optional[int] = None
    value_datetime: Optional[datetime] = None
    # Optional fields
    obs_datetime: Optional[datetime] = None
    comments: Optional[str] = None
    status: Optional[str] = None
    interpretation: Optional[str] = None
    value_modifier: Optional[str] = None


class VitalReplace(BaseModel):
    """Schema for replacing a vital sign observation (PUT)"""

    person_id: int
    concept_id: int
    encounter_id: int
    creator: int
    # Value fields - at least one must be provided
    value_numeric: Optional[float] = None
    value_text: Optional[str] = None
    value_coded: Optional[int] = None
    value_datetime: Optional[datetime] = None
    # Optional fields
    obs_datetime: Optional[datetime] = None
    location_id: Optional[int] = None
    obs_group_id: Optional[int] = None
    order_id: Optional[int] = None
    comments: Optional[str] = None
    status: Optional[str] = "FINAL"
    interpretation: Optional[str] = None
    value_modifier: Optional[str] = None
    form_namespace_and_path: Optional[str] = None


class VitalUpdateResponse(BaseModel):
    """Schema for vital update response"""

    success: bool
    message: str
    obs_id: int
    updated_fields: List[str]
    vital: Optional[VitalSign] = None