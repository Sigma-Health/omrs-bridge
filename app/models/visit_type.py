"""
Visit Type model.
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


class VisitType(Base):
    __tablename__ = "visit_type"

    visit_type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)
    description = Column(Text, nullable=True)
    creator = Column(Integer)
    date_created = Column(DateTime, default=func.now())
    changed_by = Column(Integer, nullable=True)
    date_changed = Column(DateTime, nullable=True)
    retired = Column(Boolean, default=False)
    retired_by = Column(Integer, nullable=True)
    date_retired = Column(DateTime, nullable=True)
    retire_reason = Column(Text, nullable=True)
    uuid = Column(String(38), unique=True, index=True)
