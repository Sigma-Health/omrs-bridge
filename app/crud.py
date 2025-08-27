from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Order, Obs
from app.schemas import OrderUpdate, OrderReplace, ObsUpdate, ObsReplace, ObsCreate
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


# ============================================================================
# OBSERVATION (OBS) CRUD OPERATIONS
# ============================================================================

def create_obs(db: Session, obs_create: ObsCreate) -> Obs:
    """Create a new observation"""
    # Generate UUID for new observation
    import uuid
    obs_uuid = str(uuid.uuid4())
    
    # Create observation data
    obs_data = obs_create.dict()
    obs_data['uuid'] = obs_uuid
    obs_data['date_created'] = datetime.utcnow()
    obs_data['voided'] = False
    
    # Create new observation
    db_obs = Obs(**obs_data)
    
    try:
        db.add(db_obs)
        db.commit()
        db.refresh(db_obs)
        return db_obs
    except Exception as e:
        db.rollback()
        raise e


def get_obs(db: Session, obs_id: int) -> Optional[Obs]:
    """Get observation by ID"""
    return db.query(Obs).filter(Obs.obs_id == obs_id).first()


def get_obs_by_uuid(db: Session, uuid: str) -> Optional[Obs]:
    """Get observation by UUID"""
    return db.query(Obs).filter(Obs.uuid == uuid).first()


def update_obs_partial(db: Session, obs_id: int, obs_update: ObsUpdate) -> Optional[Obs]:
    """
    Update observation partially (PATCH) by ID
    Only updates provided fields
    """
    db_obs = get_obs(db, obs_id)
    if not db_obs:
        return None
    
    # Get update data, excluding None values
    update_data = obs_update.dict(exclude_unset=True)
    
    if not update_data:
        return db_obs
    
    # Update fields
    for field, value in update_data.items():
        if hasattr(db_obs, field):
            setattr(db_obs, field, value)
    
    try:
        db.commit()
        db.refresh(db_obs)
        return db_obs
    except Exception as e:
        db.rollback()
        raise e


def update_obs_partial_by_uuid(db: Session, uuid: str, obs_update: ObsUpdate) -> Optional[Obs]:
    """
    Update observation partially (PATCH) by UUID
    Only updates provided fields
    """
    db_obs = get_obs_by_uuid(db, uuid)
    if not db_obs:
        return None
    
    # Get update data, excluding None values
    update_data = obs_update.dict(exclude_unset=True)
    
    if not update_data:
        return db_obs
    
    # Update fields
    for field, value in update_data.items():
        if hasattr(db_obs, field):
            setattr(db_obs, field, value)
    
    try:
        db.commit()
        db.refresh(db_obs)
        return db_obs
    except Exception as e:
        db.rollback()
        raise e


def update_obs_full(db: Session, obs_id: int, obs_replace: ObsReplace) -> Optional[Obs]:
    """
    Replace observation completely (PUT) by ID
    Updates all fields with provided values
    """
    db_obs = get_obs(db, obs_id)
    if not db_obs:
        return None
    
    # Get all data from the replace schema
    replace_data = obs_replace.dict()
    
    # Update all fields
    for field, value in replace_data.items():
        if hasattr(db_obs, field):
            setattr(db_obs, field, value)
    
    try:
        db.commit()
        db.refresh(db_obs)
        return db_obs
    except Exception as e:
        db.rollback()
        raise e


def update_obs_full_by_uuid(db: Session, uuid: str, obs_replace: ObsReplace) -> Optional[Obs]:
    """
    Replace observation completely (PUT) by UUID
    Updates all fields with provided values
    """
    db_obs = get_obs_by_uuid(db, uuid)
    if not db_obs:
        return None
    
    # Get all data from the replace schema
    replace_data = obs_replace.dict()
    
    # Update all fields
    for field, value in replace_data.items():
        if hasattr(db_obs, field):
            setattr(db_obs, field, value)
    
    try:
        db.commit()
        db.refresh(db_obs)
        return db_obs
    except Exception as e:
        db.rollback()
        raise e


def get_updated_obs_fields(original_obs: Obs, updated_obs: Obs) -> List[str]:
    """Get list of fields that were updated"""
    updated_fields = []
    
    # Compare all fields
    for field in Obs.__table__.columns:
        field_name = field.name
        original_value = getattr(original_obs, field_name)
        updated_value = getattr(updated_obs, field_name)
        
        if original_value != updated_value:
            updated_fields.append(field_name)
    
    return updated_fields


def list_obs(db: Session, skip: int = 0, limit: int = 100) -> List[Obs]:
    """List observations with pagination"""
    return db.query(Obs).offset(skip).limit(limit).all()


def get_obs_by_person(db: Session, person_id: int, skip: int = 0, limit: int = 100) -> List[Obs]:
    """Get observations for a specific person"""
    return db.query(Obs).filter(
        and_(Obs.person_id == person_id, Obs.voided == False)
    ).offset(skip).limit(limit).all()


def get_obs_by_encounter(db: Session, encounter_id: int, skip: int = 0, limit: int = 100) -> List[Obs]:
    """Get observations for a specific encounter"""
    return db.query(Obs).filter(
        and_(Obs.encounter_id == encounter_id, Obs.voided == False)
    ).offset(skip).limit(limit).all()


def get_obs_by_concept(db: Session, concept_id: int, skip: int = 0, limit: int = 100) -> List[Obs]:
    """Get observations for a specific concept"""
    return db.query(Obs).filter(
        and_(Obs.concept_id == concept_id, Obs.voided == False)
    ).offset(skip).limit(limit).all()


def get_obs_by_order(db: Session, order_id: int, skip: int = 0, limit: int = 100) -> List[Obs]:
    """Get observations for a specific order"""
    return db.query(Obs).filter(
        and_(Obs.order_id == order_id, Obs.voided == False)
    ).offset(skip).limit(limit).all() 