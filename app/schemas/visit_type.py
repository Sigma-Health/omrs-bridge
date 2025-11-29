"""
Visit Type schemas.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class VisitTypeBase(BaseModel):
    """Base schema for visit type data"""

    name: Optional[str] = None
    description: Optional[str] = None
    retired: Optional[bool] = None
    retire_reason: Optional[str] = None


class VisitTypeCreate(VisitTypeBase):
    """Schema for creating visit types (POST) - required fields"""

    creator: int
    name: str
    # Optional fields
    description: Optional[str] = None


class VisitTypeUpdate(VisitTypeBase):
    """Schema for updating visit types (PATCH)"""

    pass


class VisitTypeReplace(VisitTypeBase):
    """Schema for replacing visit types (PUT) - all fields required"""

    creator: int
    name: str
    description: Optional[str] = None


class VisitTypeResponse(VisitTypeBase):
    """Schema for visit type responses"""

    visit_type_id: int
    creator: int
    date_created: datetime
    uuid: str
    retired_by: Optional[int] = None
    date_retired: Optional[datetime] = None
    changed_by: Optional[int] = None
    date_changed: Optional[datetime] = None

    class Config:
        from_attributes = True


class VisitTypeUpdateResponse(BaseModel):
    """Schema for visit type update response"""

    success: bool
    message: str
    visit_type_id: int
    updated_fields: list[str]
    visit_type: Optional[VisitTypeResponse] = None

