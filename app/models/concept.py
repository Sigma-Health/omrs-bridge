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
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class ConceptName(Base):
    __tablename__ = "concept_name"

    concept_name_id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(
        Integer,
        ForeignKey("concept.concept_id"),
        nullable=False,
        index=True,
    )
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

    concept = relationship(
        "Concept",
        back_populates="names",
    )


class ConceptAnswer(Base):
    __tablename__ = "concept_answer"

    concept_answer_id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(Integer, nullable=False, index=True)
    answer_concept = Column(Integer, nullable=False, index=True)
    creator = Column(Integer)
    date_created = Column(DateTime, default=func.now())
    uuid = Column(String(38), unique=True, index=True)
    sort_weight = Column(Integer, nullable=True)


class ConceptClass(Base):
    __tablename__ = "concept_class"

    concept_class_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    creator = Column(Integer)
    date_created = Column(DateTime, default=func.now())
    retired = Column(Boolean, default=False)
    retired_by = Column(Integer, nullable=True)
    date_retired = Column(DateTime, nullable=True)
    retire_reason = Column(Text, nullable=True)
    uuid = Column(String(38), unique=True, index=True)
    changed_by = Column(Integer, nullable=True)
    date_changed = Column(DateTime, nullable=True)


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


class ConceptSet(Base):
    __tablename__ = "concept_set"

    concept_set_id = Column(Integer, primary_key=True, index=True)
    concept_id = Column(Integer, nullable=False, index=True)
    concept_set = Column(Integer, nullable=False, index=True)
    sort_weight = Column(Integer, nullable=True)
    creator = Column(Integer)
    date_created = Column(DateTime, default=func.now())
    uuid = Column(String(38), unique=True, index=True)


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

    names = relationship(
        "ConceptName",
        back_populates="concept",
        lazy="selectin",
        order_by="ConceptName.locale_preferred.desc(), ConceptName.concept_name_id",
    )

    orders = relationship("Order", back_populates="concept")

    @property
    def preferred_name(self):
        """Return the preferred (locale_preferred) concept name if available."""
        for concept_name in self.names:
            if not concept_name.voided and concept_name.locale_preferred:
                return concept_name.name
        for concept_name in self.names:
            if not concept_name.voided:
                return concept_name.name
        return self.short_name

    @property
    def active_names(self):
        """Return non-voided concept names."""
        return [concept_name for concept_name in self.names if not concept_name.voided]
