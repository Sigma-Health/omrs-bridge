"""
EncounterProvider model.
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base


class EncounterProvider(Base):
    __tablename__ = "encounter_provider"

    encounter_provider_id = Column(Integer, primary_key=True, index=True)
    encounter_id = Column(Integer, index=True)
    provider_id = Column(Integer, index=True)
    encounter_role_id = Column(Integer)
    creator = Column(Integer)
    date_created = Column(DateTime, default=func.now())
    changed_by = Column(Integer, nullable=True)
    date_changed = Column(DateTime, nullable=True)
    voided = Column(Boolean, default=False)
    date_voided = Column(DateTime, nullable=True)
    voided_by = Column(Integer, nullable=True)
    void_reason = Column(Text, nullable=True)
    uuid = Column(String(38), unique=True, index=True)
