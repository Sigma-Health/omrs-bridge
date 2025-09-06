"""
Order Type schemas.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class OrderTypeBase(BaseModel):
    """Base schema for order type data"""

    name: Optional[str] = None
    description: Optional[str] = None
    retired: Optional[bool] = None
    retire_reason: Optional[str] = None
    java_class_name: Optional[str] = None
    parent: Optional[int] = None


class OrderTypeCreate(OrderTypeBase):
    """Schema for creating order types (POST) - required fields"""

    creator: int
    name: str
    # Optional fields
    description: Optional[str] = None
    java_class_name: Optional[str] = None
    parent: Optional[int] = None


class OrderTypeUpdate(OrderTypeBase):
    """Schema for updating order types (PATCH)"""

    pass


class OrderTypeReplace(OrderTypeBase):
    """Schema for replacing order types (PUT) - all fields required"""

    creator: int
    name: str
    description: str
    java_class_name: str
    parent: int


class OrderTypeResponse(OrderTypeBase):
    """Schema for order type responses"""

    order_type_id: int
    creator: int
    date_created: datetime
    uuid: str
    retired_by: Optional[int] = None
    date_retired: Optional[datetime] = None
    changed_by: Optional[int] = None
    date_changed: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderTypeUpdateResponse(BaseModel):
    """Schema for order type update response"""

    success: bool
    message: str
    order_type_id: int
    updated_fields: list[str]
    order_type: Optional[OrderTypeResponse] = None
