"""
Concept Datatype model.
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


class ConceptDatatype(Base):
    __tablename__ = "concept_datatype"

    concept_datatype_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    hl7_abbreviation = Column(String(3), nullable=True)
    description = Column(Text, nullable=True)
    creator = Column(Integer)
    date_created = Column(DateTime, default=func.now())
    retired = Column(Boolean, default=False)
    retired_by = Column(Integer, nullable=True)
    date_retired = Column(DateTime, nullable=True)
    retire_reason = Column(Text, nullable=True)
    uuid = Column(String(38), unique=True, index=True)
