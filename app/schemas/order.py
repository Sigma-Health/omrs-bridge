"""
Order schemas.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


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
