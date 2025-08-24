from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Order
from app.schemas import OrderUpdate, OrderReplace
from typing import Optional, List
from datetime import datetime


def get_order(db: Session, order_id: int) -> Optional[Order]:
    """Get order by ID"""
    return db.query(Order).filter(Order.order_id == order_id).first()


def get_order_by_uuid(db: Session, uuid: str) -> Optional[Order]:
    """Get order by UUID"""
    return db.query(Order).filter(Order.uuid == uuid).first()


def get_order_by_number(db: Session, order_number: str) -> Optional[Order]:
    """Get order by order number"""
    return db.query(Order).filter(Order.order_number == order_number).first()


def update_order_partial(db: Session, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
    """
    Update order partially (PATCH) by ID
    Only updates provided fields
    """
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    
    # Get update data, excluding None values
    update_data = order_update.dict(exclude_unset=True)
    
    if not update_data:
        return db_order
    
    # Update fields
    for field, value in update_data.items():
        if hasattr(db_order, field):
            setattr(db_order, field, value)
    
    try:
        db.commit()
        db.refresh(db_order)
        return db_order
    except Exception as e:
        db.rollback()
        raise e


def update_order_partial_by_uuid(db: Session, uuid: str, order_update: OrderUpdate) -> Optional[Order]:
    """
    Update order partially (PATCH) by UUID
    Only updates provided fields
    """
    db_order = get_order_by_uuid(db, uuid)
    if not db_order:
        return None
    
    # Get update data, excluding None values
    update_data = order_update.dict(exclude_unset=True)
    
    if not update_data:
        return db_order
    
    # Update fields
    for field, value in update_data.items():
        if hasattr(db_order, field):
            setattr(db_order, field, value)
    
    try:
        db.commit()
        db.refresh(db_order)
        return db_order
    except Exception as e:
        db.rollback()
        raise e


def update_order_full(db: Session, order_id: int, order_replace: OrderReplace) -> Optional[Order]:
    """
    Replace order completely (PUT) by ID
    Updates all fields with provided values
    """
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    
    # Get all data from the replace schema
    replace_data = order_replace.dict()
    
    # Update all fields
    for field, value in replace_data.items():
        if hasattr(db_order, field):
            setattr(db_order, field, value)
    
    try:
        db.commit()
        db.refresh(db_order)
        return db_order
    except Exception as e:
        db.rollback()
        raise e


def update_order_full_by_uuid(db: Session, uuid: str, order_replace: OrderReplace) -> Optional[Order]:
    """
    Replace order completely (PUT) by UUID
    Updates all fields with provided values
    """
    db_order = get_order_by_uuid(db, uuid)
    if not db_order:
        return None
    
    # Get all data from the replace schema
    replace_data = order_replace.dict()
    
    # Update all fields
    for field, value in replace_data.items():
        if hasattr(db_order, field):
            setattr(db_order, field, value)
    
    try:
        db.commit()
        db.refresh(db_order)
        return db_order
    except Exception as e:
        db.rollback()
        raise e


def get_updated_fields(original_order: Order, updated_order: Order) -> List[str]:
    """Get list of fields that were updated"""
    updated_fields = []
    
    # Compare all fields
    for field in Order.__table__.columns:
        field_name = field.name
        original_value = getattr(original_order, field_name)
        updated_value = getattr(updated_order, field_name)
        
        if original_value != updated_value:
            updated_fields.append(field_name)
    
    return updated_fields


def list_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    """List orders with pagination"""
    return db.query(Order).offset(skip).limit(limit).all()


def get_orders_by_patient(db: Session, patient_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get orders for a specific patient"""
    return db.query(Order).filter(
        and_(Order.patient_id == patient_id, Order.voided == False)
    ).offset(skip).limit(limit).all() 