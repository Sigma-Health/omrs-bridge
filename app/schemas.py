from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re


class OrderBase(BaseModel):
    """Base schema for order data"""
    order_type_id: Optional[int] = None
    concept_id: Optional[int] = None
    orderer: Optional[int] = None
    encounter_id: Optional[int] = None
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


class OrderUpdate(OrderBase):
    """Schema for updating orders (PATCH)"""
    pass


class OrderReplace(OrderBase):
    """Schema for replacing orders (PUT) - all fields required"""
    order_type_id: int
    concept_id: int
    orderer: int
    encounter_id: int
    creator: int
    patient_id: int
    uuid: str
    care_setting: int


class OrderResponse(OrderBase):
    """Schema for order responses"""
    order_id: int
    creator: int
    date_created: datetime
    uuid: str
    
    class Config:
        from_attributes = True


class OrderUpdateResponse(BaseModel):
    """Schema for update response"""
    success: bool
    message: str
    order_id: int
    updated_fields: list[str]
    order: Optional[OrderResponse] = None


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


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    success: bool = False
    error: str
    detail: Optional[str] = None 