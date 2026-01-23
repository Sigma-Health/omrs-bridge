"""
Provider model.
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


class Provider(Base):
    __tablename__ = "provider"

    provider_id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, index=True)
    name = Column(String(255), nullable=True)
    identifier = Column(String(255), nullable=True)
    creator = Column(Integer)
    date_created = Column(DateTime, default=func.now())
    changed_by = Column(Integer, nullable=True)
    date_changed = Column(DateTime, nullable=True)
    retired = Column(Boolean, default=False)
    retired_by = Column(Integer, nullable=True)
    date_retired = Column(DateTime, nullable=True)
    retire_reason = Column(Text, nullable=True)
    uuid = Column(String(38), unique=True, index=True)
    role_id = Column(Integer, nullable=True)
    speciality_id = Column(Integer, nullable=True)
    provider_role_id = Column(Integer, nullable=True)
