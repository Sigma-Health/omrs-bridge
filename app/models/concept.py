"""
Concept model.
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


class ConceptName(Base):
    __tablename__ = "concept_name"

    concept_name_id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(Integer, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    locale = Column(String(50), nullable=True)
    locale_preferred = Column(Boolean, default=False)
    creator = Column(Integer)
    date_created = Column(DateTime, default=func.now())
    concept_name_type = Column(String(50), nullable=True)
    voided = Column(Boolean, default=False)
    voided_by = Column(Integer, nullable=True)
    date_voided = Column(DateTime, nullable=True)
    void_reason = Column(Text, nullable=True)
    uuid = Column(String(38), unique=True, index=True)
    date_changed = Column(DateTime, nullable=True)
    changed_by = Column(Integer, nullable=True)


class Concept(Base):
    __tablename__ = "concept"

    concept_id = Column(Integer, primary_key=True, index=True)
    retired = Column(Boolean, default=False)
    short_name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    form_text = Column(Text, nullable=True)
    datatype_id = Column(Integer, nullable=True)
    class_id = Column(Integer, nullable=True)
    is_set = Column(Boolean, default=False)
    creator = Column(Integer)
    date_created = Column(DateTime, default=func.now())
    version = Column(String(50), nullable=True)
    changed_by = Column(Integer, nullable=True)
    date_changed = Column(DateTime, nullable=True)
    retired_by = Column(Integer, nullable=True)
    date_retired = Column(DateTime, nullable=True)
    retire_reason = Column(Text, nullable=True)
    uuid = Column(String(38), unique=True, index=True)
