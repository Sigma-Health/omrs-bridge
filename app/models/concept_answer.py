"""
Concept Answer model.
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


class ConceptAnswer(Base):
    __tablename__ = "concept_answer"

    concept_answer_id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(Integer, nullable=False, index=True)
    answer_concept = Column(Integer, nullable=False, index=True)
    creator = Column(Integer)
    date_created = Column(DateTime, default=func.now())
    uuid = Column(String(38), unique=True, index=True)
    sort_weight = Column(Integer, nullable=True)
