"""
Drug model.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Float,
    Text,
)
from sqlalchemy.sql import func

from app.database import Base


class Drug(Base):
    __tablename__ = "drug"

    drug_id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(Integer, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    combination = Column(Boolean, default=False)
    dosage_form = Column(Integer, nullable=True)
    maximum_daily_dose = Column(Float, nullable=True)
    minimum_daily_dose = Column(Float, nullable=True)
    route = Column(Integer, nullable=True)
    creator = Column(Integer, nullable=False)
    date_created = Column(DateTime, default=func.now())
    retired = Column(Boolean, default=False)
    changed_by = Column(Integer, nullable=True)
    date_changed = Column(DateTime, nullable=True)
    retired_by = Column(Integer, nullable=True)
    date_retired = Column(DateTime, nullable=True)
    retire_reason = Column(Text, nullable=True)
    uuid = Column(String(38), unique=True, index=True)
    strength = Column(String(255), nullable=True)
    dose_limit_units = Column(Integer, nullable=True)
