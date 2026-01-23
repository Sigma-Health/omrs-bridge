"""
Observation (Obs) model.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Text,
    Float,
)
from sqlalchemy.sql import func
from app.database import Base


class Obs(Base):
    __tablename__ = "obs"

    obs_id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, index=True)
    concept_id = Column(Integer, index=True)
    encounter_id = Column(Integer, index=True)
    order_id = Column(Integer, nullable=True)
    obs_datetime = Column(DateTime, default=func.now())
    location_id = Column(Integer, nullable=True)
    obs_group_id = Column(Integer, nullable=True)
    accession_number = Column(String(255), nullable=True)
    value_group_id = Column(Integer, nullable=True)
    value_coded = Column(Integer, nullable=True)
    value_coded_name_id = Column(Integer, nullable=True)
    value_drug = Column(Integer, nullable=True)
    value_datetime = Column(DateTime, nullable=True)
    value_numeric = Column(Float, nullable=True)
    value_modifier = Column(String(2), nullable=True)
    value_text = Column(Text, nullable=True)
    value_complex = Column(String(255), nullable=True)
    comments = Column(Text, nullable=True)
    creator = Column(Integer)
    date_created = Column(DateTime, default=func.now())
    voided = Column(Boolean, default=False)
    voided_by = Column(Integer, nullable=True)
    date_voided = Column(DateTime, nullable=True)
    void_reason = Column(Text, nullable=True)
    uuid = Column(String(38), unique=True, index=True)
    previous_version = Column(Integer, nullable=True)
    form_namespace_and_path = Column(Text, nullable=True)
    status = Column(String(16), default="FINAL")
    interpretation = Column(String(32), nullable=True)
