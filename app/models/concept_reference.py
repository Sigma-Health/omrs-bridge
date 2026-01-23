"""
Concept reference models for ICD10 and other coding systems.
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


class ConceptReferenceSource(Base):
    __tablename__ = "concept_reference_source"

    concept_source_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    hl7_code = Column(String(50), nullable=True)
    creator = Column(Integer, nullable=True)
    date_created = Column(DateTime, default=func.now())
    retired = Column(Boolean, default=False)
    retired_by = Column(Integer, nullable=True)
    date_retired = Column(DateTime, nullable=True)
    retire_reason = Column(Text, nullable=True)
    uuid = Column(String(38), unique=True, index=True)
    unique_id = Column(String(50), nullable=True)
    date_changed = Column(DateTime, nullable=True)
    changed_by = Column(Integer, nullable=True)


class ConceptReferenceTerm(Base):
    __tablename__ = "concept_reference_term"

    concept_reference_term_id = Column(Integer, primary_key=True, index=True)
    concept_source_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=True)
    code = Column(String(255), nullable=False)
    version = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    creator = Column(Integer, nullable=True)
    date_created = Column(DateTime, default=func.now())
    date_changed = Column(DateTime, nullable=True)
    changed_by = Column(Integer, nullable=True)
    retired = Column(Boolean, default=False)
    retired_by = Column(Integer, nullable=True)
    date_retired = Column(DateTime, nullable=True)
    retire_reason = Column(Text, nullable=True)
    uuid = Column(String(38), unique=True, index=True)


class ConceptReferenceMap(Base):
    __tablename__ = "concept_reference_map"

    concept_map_id = Column(Integer, primary_key=True, index=True)
    concept_reference_term_id = Column(Integer, nullable=False)
    concept_map_type_id = Column(Integer, nullable=False, default=1)
    creator = Column(Integer, nullable=False, default=0)
    date_created = Column(DateTime, nullable=False)
    concept_id = Column(Integer, nullable=False)
    changed_by = Column(Integer, nullable=True)
    date_changed = Column(DateTime, nullable=True)
    uuid = Column(String(38), unique=True, nullable=False)
