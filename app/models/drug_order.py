"""
DrugOrder model.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Float,
    Text,
)

from app.database import Base


class DrugOrder(Base):
    __tablename__ = "drug_order"

    order_id = Column(Integer, primary_key=True, index=True)
    drug_inventory_id = Column(Integer, nullable=True)
    dose = Column(Float, nullable=True)
    as_needed = Column(Boolean, default=False)
    dosing_type = Column(Text, nullable=True)
    quantity = Column(Float, nullable=True)
    as_needed_condition = Column(String(255), nullable=True)
    num_refills = Column(Integer, default=0)
    dosing_instructions = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)
    duration_units = Column(Integer, nullable=True)
    quantity_units = Column(Integer, nullable=True)
    route = Column(Integer, nullable=True)
    dose_units = Column(Integer, nullable=True)
    frequency = Column(Integer, nullable=True)
    brand_name = Column(String(255), nullable=True)
    dispense_as_written = Column(Boolean, default=False)
    drug_non_coded = Column(String(255), nullable=True)
