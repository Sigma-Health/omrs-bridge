"""
Visit model.
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


class Visit(Base):
    __tablename__ = "visit"

    visit_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, index=True)
    visit_type_id = Column(Integer)
    date_started = Column(DateTime, default=func.now())
    date_stopped = Column(DateTime, nullable=True)
    indication_concept_id = Column(Integer, nullable=True)
    location_id = Column(Integer, nullable=True)
    creator = Column(Integer)
    date_created = Column(DateTime, default=func.now())
    changed_by = Column(Integer, nullable=True)
    date_changed = Column(DateTime, nullable=True)
    voided = Column(Boolean, default=False)
    voided_by = Column(Integer, nullable=True)
    date_voided = Column(DateTime, nullable=True)
    void_reason = Column(Text, nullable=True)
    uuid = Column(String(38), unique=True, index=True)
