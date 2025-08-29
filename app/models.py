from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
from typing import Optional


class Order(Base):
    __tablename__ = "orders"
    
    order_id = Column(Integer, primary_key=True, index=True)
    order_type_id = Column(Integer)
    concept_id = Column(Integer)
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


class Obs(Base):
    __tablename__ = "obs"
    
    obs_id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, index=True)
    concept_id = Column(Integer, index=True)
    encounter_id = Column(Integer, index=True)
    order_id = Column(Integer, nullable=True)
    obs_datetime = Column(DateTime, default=func.now())
    location_id = Column(Integer, nullable=True)
    obs_group_id = Column(Integer, nullable=True)
    accession_number = Column(String(255), nullable=True)
    value_group_id = Column(Integer, nullable=True)
    value_coded = Column(Integer, nullable=True)
    value_coded_name_id = Column(Integer, nullable=True)
    value_drug = Column(Integer, nullable=True)
    value_datetime = Column(DateTime, nullable=True)
    value_numeric = Column(Float, nullable=True)
    value_modifier = Column(String(2), nullable=True)
    value_text = Column(Text, nullable=True)
    value_complex = Column(String(255), nullable=True)
    comments = Column(Text, nullable=True)
    creator = Column(Integer)
    date_created = Column(DateTime, default=func.now())
    voided = Column(Boolean, default=False)
    voided_by = Column(Integer, nullable=True)
    date_voided = Column(DateTime, nullable=True)
    void_reason = Column(Text, nullable=True)
    uuid = Column(String(38), unique=True, index=True)
    previous_version = Column(Integer, nullable=True)
    form_namespace_and_path = Column(Text, nullable=True)
    status = Column(String(16), default="FINAL")
    interpretation = Column(String(32), nullable=True)


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