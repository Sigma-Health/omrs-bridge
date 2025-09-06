"""
Concept schemas.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConceptBase(BaseModel):
    """Base schema for concept data"""

    short_name: Optional[str] = None
    description: Optional[str] = None
    form_text: Optional[str] = None
    datatype_id: Optional[int] = None
    class_id: Optional[int] = None
    is_set: Optional[bool] = None
    version: Optional[str] = None
    retired: Optional[bool] = None
    retire_reason: Optional[str] = None


class ConceptCreate(ConceptBase):
    """Schema for creating concepts (POST) - required fields"""

    creator: int
    # Optional fields
    short_name: Optional[str] = None
    description: Optional[str] = None
    form_text: Optional[str] = None
    datatype_id: Optional[int] = None
    class_id: Optional[int] = None
    is_set: Optional[bool] = None
    version: Optional[str] = None


class ConceptUpdate(ConceptBase):
    """Schema for updating concepts (PATCH)"""

    pass


class ConceptReplace(ConceptBase):
    """Schema for replacing concepts (PUT) - all fields required"""

    creator: int
    short_name: str
    description: str
    datatype_id: int
    class_id: int


class ConceptResponse(ConceptBase):
    """Schema for concept responses"""

    concept_id: int
    creator: int
    date_created: datetime
    uuid: str
    changed_by: Optional[int] = None
    date_changed: Optional[datetime] = None
    retired_by: Optional[int] = None
    date_retired: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConceptUpdateResponse(BaseModel):
    """Schema for concept update response"""

    success: bool
    message: str
    concept_id: int
    updated_fields: list[str]
    concept: Optional[ConceptResponse] = None
