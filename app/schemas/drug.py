"""
Drug schemas.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class DrugBase(BaseModel):
    """Base schema for drug data."""

    concept_id: Optional[int] = None
    name: Optional[str] = None
    combination: Optional[bool] = None
    dosage_form: Optional[int] = None
    maximum_daily_dose: Optional[float] = None
    minimum_daily_dose: Optional[float] = None
    route: Optional[int] = None
    strength: Optional[str] = None
    dose_limit_units: Optional[int] = None
    retired: Optional[bool] = None
    retire_reason: Optional[str] = None
    changed_by: Optional[int] = None


class DrugCreate(DrugBase):
    """Schema for creating drugs (POST) - required fields."""

    concept_id: int
    name: str
    creator: Optional[int] = None
    combination: Optional[bool] = None
    dosage_form: Optional[int] = None
    maximum_daily_dose: Optional[float] = None
    minimum_daily_dose: Optional[float] = None
    route: Optional[int] = None
    strength: Optional[str] = None
    dose_limit_units: Optional[int] = None


class DrugUpdate(DrugBase):
    """Schema for updating drugs (PATCH)."""

    retired_by: Optional[int] = None
    date_retired: Optional[datetime] = None
    uuid: Optional[str] = None


class DrugReplace(DrugBase):
    """Schema for replacing drugs (PUT) - required fields."""

    concept_id: int
    name: str
    creator: int
    combination: Optional[bool] = None
    dosage_form: Optional[int] = None
    maximum_daily_dose: Optional[float] = None
    minimum_daily_dose: Optional[float] = None
    route: Optional[int] = None
    strength: Optional[str] = None
    dose_limit_units: Optional[int] = None
    uuid: Optional[str] = None
    retired_by: Optional[int] = None
    date_retired: Optional[datetime] = None


class DrugResponse(DrugBase):
    """Schema for drug responses."""

    drug_id: int
    concept_id: int
    name: str
    creator: int
    date_created: datetime
    uuid: str
    retired: bool
    combination: bool
    retired_by: Optional[int] = None
    date_retired: Optional[datetime] = None
    date_changed: Optional[datetime] = None
    search_index_update_status: Optional[str] = None

    class Config:
        from_attributes = True


class DrugUpdateResponse(BaseModel):
    """Schema for drug update response."""

    success: bool
    message: str
    drug_id: int
    updated_fields: List[str]
    drug: Optional[DrugResponse] = None
