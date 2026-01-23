from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ConceptNameInfo(BaseModel):
    display: str
    uuid: str
    name: str
    locale: str
    localePreferred: bool
    conceptNameType: str


class ConceptDatatypeInfo(BaseModel):
    uuid: str
    display: str
    name: str
    description: Optional[str] = None


class ConceptClassInfo(BaseModel):
    uuid: str
    display: str


class ConceptAnswerInfo(BaseModel):
    uuid: str
    display: str
    name: ConceptNameInfo
    datatype: ConceptDatatypeInfo
    conceptClass: ConceptClassInfo
    set: bool
    version: str
    retired: bool
    names: List[dict]
    descriptions: List[dict]
    mappings: List[dict]
    answers: List[dict]
    setMembers: List[dict]
    attributes: List[dict]
    links: List[dict]
    resourceVersion: str


class ConceptInfo(BaseModel):
    uuid: str
    display: str
    name: str
    datatype: Optional[ConceptDatatypeInfo] = None
    concept_class: str
    answers: List[ConceptAnswerInfo] = []


class SetMemberInfo(BaseModel):
    uuid: str
    concept: ConceptInfo


class OpenMRSOrderResponse(BaseModel):
    uuid: str
    order_number: str
    concept: ConceptInfo
    status: str
    date_activated: Optional[datetime] = None
    instructions: Optional[str] = None
    accession_number: Optional[str] = None
    encounter_uuid: Optional[str] = None
    is_panel: bool
    is_set_member: bool
    set_members: List[SetMemberInfo] = []
