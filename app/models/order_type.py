"""
Order Type model.
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


class OrderType(Base):
    __tablename__ = "order_type"

    order_type_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True)
    description = Column(Text, nullable=True)
    creator = Column(Integer)
    date_created = Column(DateTime, default=func.now())
    retired = Column(Boolean, default=False)
    retired_by = Column(Integer, nullable=True)
    date_retired = Column(DateTime, nullable=True)
    retire_reason = Column(Text, nullable=True)
    uuid = Column(String(38), unique=True, index=True)
    java_class_name = Column(String(255), nullable=True)
    parent = Column(Integer, nullable=True)
    changed_by = Column(Integer, nullable=True)
    date_changed = Column(DateTime, nullable=True)
