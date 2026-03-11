"""
DrugOrder schemas.
"""

from pydantic import BaseModel
from typing import Optional, Any, Dict

from .order import OrderBase


class ConceptNameInfo(BaseModel):
    """Schema for concept name information"""

    concept_id: int
    name: Optional[str] = None


class DrugInfo(BaseModel):
    """Schema for drug information"""

    drug_id: int
    concept_id: int
    name: str
    uuid: str
    combination: Optional[bool] = None
    strength: Optional[str] = None
    dosage_form: Optional[int] = None
    route: Optional[int] = None


class DosingInstructions(BaseModel):
    """Schema for dosing instructions JSON"""

    instructions: Optional[str] = None


class DrugOrderInfo(BaseModel):
    """Schema for drug order information with prescription details"""

    order_id: int
    drug_inventory_id: Optional[int] = None
    dose: Optional[float] = None
    as_needed: Optional[bool] = None
    dosing_type: Optional[str] = None
    quantity: Optional[float] = None
    as_needed_condition: Optional[str] = None
    num_refills: Optional[int] = None
    dosing_instructions: Optional[DosingInstructions] = None
    duration: Optional[int] = None
    duration_units: Optional[int] = None
    duration_units_name: Optional[str] = None
    quantity_units: Optional[int] = None
    quantity_units_name: Optional[str] = None
    route: Optional[int] = None
    route_name: Optional[str] = None
    dose_units: Optional[int] = None
    dose_units_name: Optional[str] = None
    frequency: Optional[int] = None
    frequency_name: Optional[str] = None
    brand_name: Optional[str] = None
    dispense_as_written: Optional[bool] = None
    drug_non_coded: Optional[str] = None
    drug_info: Optional[DrugInfo] = None

    class Config:
        from_attributes = True


class DrugOrderCreateForVisit(OrderBase):
    """Schema for creating a drug order using a visit UUID."""

    concept_id: int
    orderer: int
    creator: int
    care_setting: int
    drug_inventory_id: int
    dose: Optional[float] = None
    as_needed: Optional[bool] = False
    dosing_type: Optional[str] = None
    quantity: Optional[float] = None
    as_needed_condition: Optional[str] = None
    num_refills: Optional[int] = 0
    dosing_instructions: Optional[Dict[str, Any]] = None
    duration: Optional[int] = None
    duration_units: Optional[int] = None
    quantity_units: Optional[int] = None
    route: Optional[int] = None
    dose_units: Optional[int] = None
    frequency: Optional[int] = None
    brand_name: Optional[str] = None
    dispense_as_written: Optional[bool] = False
    drug_non_coded: Optional[str] = None
