from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Order, Obs, Concept
from app.schemas import OrderUpdate, OrderReplace, ObsUpdate, ObsReplace, ObsCreate, ConceptUpdate, ConceptReplace, ConceptCreate
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


# ============================================================================
# CONCEPT CRUD OPERATIONS
# ============================================================================

def create_concept(db: Session, concept_create: ConceptCreate) -> Concept:
    """Create a new concept"""
    # Generate UUID for new concept
    import uuid
    concept_uuid = str(uuid.uuid4())
    
    # Create concept data
    concept_data = concept_create.dict()
    concept_data['uuid'] = concept_uuid
    concept_data['date_created'] = datetime.utcnow()
    concept_data['retired'] = False
    
    # Create new concept
    db_concept = Concept(**concept_data)
    
    try:
        db.add(db_concept)
        db.commit()
        db.refresh(db_concept)
        return db_concept
    except Exception as e:
        db.rollback()
        raise e


def get_concept(db: Session, concept_id: int) -> Optional[Concept]:
    """Get concept by ID"""
    return db.query(Concept).filter(Concept.concept_id == concept_id).first()


def get_concept_by_uuid(db: Session, uuid: str) -> Optional[Concept]:
    """Get concept by UUID"""
    return db.query(Concept).filter(Concept.uuid == uuid).first()


def update_concept_partial(db: Session, concept_id: int, concept_update: ConceptUpdate) -> Optional[Concept]:
    """
    Update concept partially (PATCH) by ID
    Only updates provided fields
    """
    db_concept = get_concept(db, concept_id)
    if not db_concept:
        return None
    
    # Get update data, excluding None values
    update_data = concept_update.dict(exclude_unset=True)
    
    if not update_data:
        return db_concept
    
    # Update fields
    for field, value in update_data.items():
        if hasattr(db_concept, field):
            setattr(db_concept, field, value)
    
    # Set changed_by and date_changed if any field was updated
    if update_data:
        db_concept.changed_by = update_data.get('changed_by', db_concept.changed_by)
        db_concept.date_changed = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(db_concept)
        return db_concept
    except Exception as e:
        db.rollback()
        raise e


def update_concept_partial_by_uuid(db: Session, uuid: str, concept_update: ConceptUpdate) -> Optional[Concept]:
    """
    Update concept partially (PATCH) by UUID
    Only updates provided fields
    """
    db_concept = get_concept_by_uuid(db, uuid)
    if not db_concept:
        return None
    
    # Get update data, excluding None values
    update_data = concept_update.dict(exclude_unset=True)
    
    if not update_data:
        return db_concept
    
    # Update fields
    for field, value in update_data.items():
        if hasattr(db_concept, field):
            setattr(db_concept, field, value)
    
    # Set changed_by and date_changed if any field was updated
    if update_data:
        db_concept.changed_by = update_data.get('changed_by', db_concept.changed_by)
        db_concept.date_changed = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(db_concept)
        return db_concept
    except Exception as e:
        db.rollback()
        raise e


def update_concept_full(db: Session, concept_id: int, concept_replace: ConceptReplace) -> Optional[Concept]:
    """
    Replace concept completely (PUT) by ID
    Updates all fields with provided values
    """
    db_concept = get_concept(db, concept_id)
    if not db_concept:
        return None
    
    # Get all data from the replace schema
    replace_data = concept_replace.dict()
    
    # Update all fields
    for field, value in replace_data.items():
        if hasattr(db_concept, field):
            setattr(db_concept, field, value)
    
    # Set changed_by and date_changed
    db_concept.changed_by = replace_data.get('changed_by', db_concept.changed_by)
    db_concept.date_changed = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(db_concept)
        return db_concept
    except Exception as e:
        db.rollback()
        raise e


def update_concept_full_by_uuid(db: Session, uuid: str, concept_replace: ConceptReplace) -> Optional[Concept]:
    """
    Replace concept completely (PUT) by UUID
    Updates all fields with provided values
    """
    db_concept = get_concept_by_uuid(db, uuid)
    if not db_concept:
        return None
    
    # Get all data from the replace schema
    replace_data = concept_replace.dict()
    
    # Update all fields
    for field, value in replace_data.items():
        if hasattr(db_concept, field):
            setattr(db_concept, field, value)
    
    # Set changed_by and date_changed
    db_concept.changed_by = replace_data.get('changed_by', db_concept.changed_by)
    db_concept.date_changed = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(db_concept)
        return db_concept
    except Exception as e:
        db.rollback()
        raise e


def get_updated_concept_fields(original_concept: Concept, updated_concept: Concept) -> List[str]:
    """Get list of fields that were updated"""
    updated_fields = []
    
    # Compare all fields
    for field in Concept.__table__.columns:
        field_name = field.name
        original_value = getattr(original_concept, field_name)
        updated_value = getattr(updated_concept, field_name)
        
        if original_value != updated_value:
            updated_fields.append(field_name)
    
    return updated_fields


def list_concepts(db: Session, skip: int = 0, limit: int = 100) -> List[Concept]:
    """List concepts with pagination"""
    return db.query(Concept).offset(skip).limit(limit).all()


def get_concepts_by_datatype(db: Session, datatype_id: int, skip: int = 0, limit: int = 100) -> List[Concept]:
    """Get concepts for a specific datatype"""
    return db.query(Concept).filter(
        and_(Concept.datatype_id == datatype_id, Concept.retired == False)
    ).offset(skip).limit(limit).all()


def get_concepts_by_class(db: Session, class_id: int, skip: int = 0, limit: int = 100) -> List[Concept]:
    """Get concepts for a specific class"""
    return db.query(Concept).filter(
        and_(Concept.class_id == class_id, Concept.retired == False)
    ).offset(skip).limit(limit).all()


def get_concepts_by_creator(db: Session, creator: int, skip: int = 0, limit: int = 100) -> List[Concept]:
    """Get concepts created by a specific user"""
    return db.query(Concept).filter(
        and_(Concept.creator == creator, Concept.retired == False)
    ).offset(skip).limit(limit).all()


def search_concepts_by_name(db: Session, name: str, skip: int = 0, limit: int = 100) -> List[Concept]:
    """Search concepts by short_name or description"""
    return db.query(Concept).filter(
        and_(
            Concept.retired == False,
            (Concept.short_name.contains(name) | Concept.description.contains(name))
        )
    ).offset(skip).limit(limit).all()


def get_active_concepts(db: Session, skip: int = 0, limit: int = 100) -> List[Concept]:
    """Get only active (non-retired) concepts"""
    return db.query(Concept).filter(
        Concept.retired == False
    ).offset(skip).limit(limit).all()


def get_retired_concepts(db: Session, skip: int = 0, limit: int = 100) -> List[Concept]:
    """Get only retired concepts"""
    return db.query(Concept).filter(
        Concept.retired == True
    ).offset(skip).limit(limit).all() 