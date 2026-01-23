"""
Encounter model.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
)
from sqlalchemy.sql import func
from app.database import Base


class Encounter(Base):
    __tablename__ = "encounter"

    encounter_id = Column(Integer, primary_key=True, index=True)
    encounter_type = Column(Integer)
    patient_id = Column(Integer, index=True)
    location_id = Column(Integer, nullable=True)
    form_id = Column(Integer, nullable=True)
    encounter_datetime = Column(DateTime, default=func.now())
    creator = Column(Integer)
    date_created = Column(DateTime, default=func.now())
    voided = Column(Boolean, default=False)
    voided_by = Column(Integer, nullable=True)
    date_voided = Column(DateTime, nullable=True)
    void_reason = Column(Text, nullable=True)
    changed_by = Column(Integer, nullable=True)
    date_changed = Column(DateTime, nullable=True)
    visit_id = Column(Integer, nullable=True)
    uuid = Column(String(38), unique=True, index=True)
