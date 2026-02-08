"""
Order model.
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


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    order_type_id = Column(Integer)
    concept_id = Column(Integer, ForeignKey("concept.concept_id"))
    orderer = Column(Integer)
    encounter_id = Column(Integer)
    instructions = Column(Text, nullable=True)
    date_activated = Column(DateTime, default=func.now())
    auto_expire_date = Column(DateTime, nullable=True)
    date_stopped = Column(DateTime, nullable=True)
    order_reason = Column(Integer, nullable=True)
    order_reason_non_coded = Column(Text, nullable=True)
    creator = Column(Integer)
    date_created = Column(DateTime, default=func.now())
    voided = Column(Boolean, default=False)
    voided_by = Column(Integer, nullable=True)
    date_voided = Column(DateTime, nullable=True)
    void_reason = Column(Text, nullable=True)
    patient_id = Column(Integer)
    accession_number = Column(String(255), nullable=True)
    uuid = Column(String(38), unique=True, index=True)
    urgency = Column(String(50), default="ROUTINE")
    order_number = Column(String(50), unique=True, index=True)
    previous_order_id = Column(Integer, nullable=True)
    order_action = Column(String(50), default="NEW")
    comment_to_fulfiller = Column(Text, nullable=True)
    care_setting = Column(Integer)
    scheduled_date = Column(DateTime, nullable=True)
    order_group_id = Column(Integer, nullable=True)
    sort_weight = Column(Integer, nullable=True)
    fulfiller_comment = Column(Text, nullable=True)
    fulfiller_status = Column(String(50), nullable=True)
    form_namespace_and_path = Column(Text, nullable=True)

    # Relationship to Concept
    concept = relationship("Concept", back_populates="orders")
