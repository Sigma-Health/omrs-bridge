"""
Patient model.
"""

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Boolean,
    Text,
    String,
)
from sqlalchemy.sql import func
from app.database import Base


class Patient(Base):
    __tablename__ = "patient"

    patient_id = Column(Integer, primary_key=True, index=True)
    creator = Column(Integer)
    date_created = Column(DateTime, default=func.now())
    changed_by = Column(Integer, nullable=True)
    date_changed = Column(DateTime, nullable=True)
    voided = Column(Boolean, default=False)
    voided_by = Column(Integer, nullable=True)
    date_voided = Column(DateTime, nullable=True)
    void_reason = Column(Text, nullable=True)
    allergy_status = Column(String(50), default="Unknown")
