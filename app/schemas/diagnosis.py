"""
Diagnosis schemas for API responses.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReferenceCode(BaseModel):
    """Reference code information (ICD10, CIEL, IMO, etc.)"""

    code: str
    name: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None
    source_name: Optional[str] = None
    source_description: Optional[str] = None
    hl7_code: Optional[str] = None


class DiagnosisConcept(BaseModel):
    """Diagnosis concept information"""

    concept_id: int
    uuid: str
    name: str
    short_name: Optional[str] = None
    description: Optional[str] = None
    reference_codes: Optional[List[ReferenceCode]] = None


class PatientInfo(BaseModel):
    """Patient information for diagnosis"""

    patient_id: int
    uuid: str
    name: str
    gender: Optional[str] = None
    birthdate: Optional[datetime] = None


class EncounterInfo(BaseModel):
    """Encounter information for diagnosis"""

    encounter_id: int
    uuid: str
    encounter_datetime: datetime
    encounter_type: Optional[int] = None
    location_id: Optional[int] = None


class DiagnosisObservation(BaseModel):
    """Individual diagnosis observation"""

    obs_id: int
    uuid: str
    obs_datetime: datetime
    concept: DiagnosisConcept
    patient: PatientInfo
    encounter: EncounterInfo
    comments: Optional[str] = None
    status: Optional[str] = None
    interpretation: Optional[str] = None


class VisitDiagnoses(BaseModel):
    """Diagnoses for a specific visit"""

    visit_id: int
    visit_uuid: str
    patient: PatientInfo
    diagnoses: List[DiagnosisObservation]
    total_count: int


class DiagnosisResponse(BaseModel):
    """Response schema for diagnosis queries"""

    diagnoses: List[DiagnosisObservation]
    total_count: int
    skip: int
    limit: int
