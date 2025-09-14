"""
Order and Concept Details schemas.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ConceptDatatypeInfo(BaseModel):
    """Schema for concept datatype information"""

    concept_datatype_id: int
    name: str
    hl7_abbreviation: Optional[str] = None
    description: Optional[str] = None
    uuid: str


class ConceptClassInfo(BaseModel):
    """Schema for concept class information"""

    concept_class_id: int
    name: str
    description: Optional[str] = None
    uuid: str


class ConceptAnswerInfo(BaseModel):
    """Schema for concept answer information"""

    concept_id: int
    uuid: str
    name: Optional[str] = None
    description: Optional[str] = None
    datatype: Optional[ConceptDatatypeInfo] = None
    concept_class: Optional[ConceptClassInfo] = None


class ConceptSetMemberInfo(BaseModel):
    """Schema for concept set member information"""

    concept_id: int
    uuid: str
    name: Optional[str] = None
    description: Optional[str] = None
    datatype: Optional[ConceptDatatypeInfo] = None
    concept_class: Optional[ConceptClassInfo] = None
    answers: Optional[List[ConceptAnswerInfo]] = None
    sort_weight: Optional[int] = None


class ConceptDetailsInfo(BaseModel):
    """Schema for comprehensive concept information"""

    concept_id: int
    uuid: str
    name: Optional[str] = None
    description: Optional[str] = None
    short_name: Optional[str] = None
    datatype: Optional[ConceptDatatypeInfo] = None
    concept_class: Optional[ConceptClassInfo] = None
    is_set: Optional[bool] = None
    answers: Optional[List[ConceptAnswerInfo]] = None
    set_members: Optional[List[ConceptSetMemberInfo]] = None


class OrderConceptDetailsResponse(BaseModel):
    """Schema for order and concept details response"""

    # Order information
    order_id: int
    order_type_id: int
    concept_id: int
    orderer: int
    encounter_id: int
    instructions: Optional[str] = None
    date_activated: Optional[datetime] = None
    auto_expire_date: Optional[datetime] = None
    date_stopped: Optional[datetime] = None
    order_reason: Optional[int] = None
    order_reason_non_coded: Optional[str] = None
    voided: Optional[bool] = None
    voided_by: Optional[int] = None
    date_voided: Optional[datetime] = None
    void_reason: Optional[str] = None
    patient_id: Optional[int] = None
    accession_number: Optional[str] = None
    urgency: Optional[str] = None
    order_number: Optional[str] = None
    previous_order_id: Optional[int] = None
    order_action: Optional[str] = None
    comment_to_fulfiller: Optional[str] = None
    care_setting: Optional[int] = None
    scheduled_date: Optional[datetime] = None
    order_group_id: Optional[int] = None
    sort_weight: Optional[int] = None
    fulfiller_comment: Optional[str] = None
    fulfiller_status: Optional[str] = None
    form_namespace_and_path: Optional[str] = None
    creator: int
    date_created: datetime
    uuid: str

    # Orderer information
    orderer_info: Optional[dict] = None

    # Patient information
    patient_info: Optional[dict] = None

    # Comprehensive concept information
    concept_details: Optional[ConceptDetailsInfo] = None
