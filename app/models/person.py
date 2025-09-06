"""
Person and PersonName models.
"""

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Boolean,
    Text,
    String,
    Date,
)
from sqlalchemy.sql import func
from app.database import Base


class Person(Base):
    __tablename__ = "person"

    person_id = Column(Integer, primary_key=True, index=True)
    gender = Column(String(1), nullable=True)
    birthdate = Column(Date, nullable=True)
    birthdate_estimated = Column(Boolean, default=False)
    dead = Column(Boolean, default=False)
    death_date = Column(DateTime, nullable=True)
    cause_of_death = Column(Integer, nullable=True)
    creator = Column(Integer, nullable=True)
    date_created = Column(DateTime, default=func.now())
    changed_by = Column(Integer, nullable=True)
    date_changed = Column(DateTime, nullable=True)
    voided = Column(Boolean, default=False)
    voided_by = Column(Integer, nullable=True)
    date_voided = Column(DateTime, nullable=True)
    void_reason = Column(Text, nullable=True)
    uuid = Column(String(38), unique=True, index=True)
    deathdate_estimated = Column(Boolean, default=False)
    birthtime = Column(DateTime, nullable=True)
    cause_of_death_non_coded = Column(Text, nullable=True)


class PersonName(Base):
    __tablename__ = "person_name"

    person_name_id = Column(Integer, primary_key=True, index=True)
    preferred = Column(Boolean, default=False)
    person_id = Column(Integer, index=True)
    prefix = Column(String(50), nullable=True)
    given_name = Column(String(50), nullable=True)
    middle_name = Column(String(50), nullable=True)
    family_name_prefix = Column(String(50), nullable=True)
    family_name = Column(String(50), nullable=True)
    family_name2 = Column(String(50), nullable=True)
    family_name_suffix = Column(String(50), nullable=True)
    degree = Column(String(50), nullable=True)
    creator = Column(Integer)
    date_created = Column(DateTime, default=func.now())
    voided = Column(Boolean, default=False)
    voided_by = Column(Integer, nullable=True)
    date_voided = Column(DateTime, nullable=True)
    void_reason = Column(Text, nullable=True)
    changed_by = Column(Integer, nullable=True)
    date_changed = Column(DateTime, nullable=True)
    uuid = Column(String(38), unique=True, index=True)
