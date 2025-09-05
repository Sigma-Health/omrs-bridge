# CRUD Implementation Details

## Complete Code Examples

This document provides the complete implementation details for the class-based CRUD architecture. Use these examples when you're ready to implement the migration.

## 1. Base CRUD Class Implementation

### File: `app/crud/base.py`

```python
"""
Base CRUD class providing common database operations.
All entity-specific CRUD classes inherit from this base class.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import uuid

# Generic type for SQLAlchemy models
ModelType = TypeVar("ModelType")

class BaseCRUD(Generic[ModelType], ABC):
    """
    Base CRUD class with common database operations.
    
    This class provides a foundation for all entity-specific CRUD operations,
    including common patterns for create, read, update, and delete operations.
    """
    
    def __init__(self, model: Type[ModelType]):
        """
        Initialize the CRUD class with a specific model.
        
        Args:
            model: The SQLAlchemy model class to operate on
        """
        self.model = model
    
    def create(self, db: Session, obj_create: Any) -> ModelType:
        """
        Create a new record in the database.
        
        Args:
            db: Database session
            obj_create: Pydantic schema for creating the object
            
        Returns:
            The created database object
            
        Raises:
            Exception: If database operation fails
        """
        # Generate UUID for new record
        obj_uuid = str(uuid.uuid4())
        
        # Create object data
        obj_data = obj_create.dict()
        obj_data['uuid'] = obj_uuid
        obj_data['date_created'] = datetime.utcnow()
        
        # Set default values based on model type
        self._set_default_values(obj_data)
        
        # Create new database object
        db_obj = self.model(**obj_data)
        
        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            raise e
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """
        Get a record by its primary key ID.
        
        Args:
            db: Database session
            id: Primary key ID
            
        Returns:
            The database object if found, None otherwise
        """
        return db.query(self.model).filter(self.model.__table__.primary_key.columns[0] == id).first()
    
    def get_by_uuid(self, db: Session, uuid: str) -> Optional[ModelType]:
        """
        Get a record by its UUID.
        
        Args:
            db: Database session
            uuid: UUID of the record
            
        Returns:
            The database object if found, None otherwise
        """
        return db.query(self.model).filter(self.model.uuid == uuid).first()
    
    def update_partial(self, db: Session, id: int, obj_update: Any) -> Optional[ModelType]:
        """
        Update a record partially (PATCH) by ID.
        Only updates provided fields.
        
        Args:
            db: Database session
            id: Primary key ID
            obj_update: Pydantic schema for partial update
            
        Returns:
            The updated database object if found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        db_obj = self.get(db, id)
        if not db_obj:
            return None
        
        # Get update data, excluding None values
        update_data = obj_update.dict(exclude_unset=True)
        
        if not update_data:
            return db_obj
        
        # Update fields
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        # Set audit fields if any field was updated
        if update_data:
            self._set_audit_fields(db_obj, update_data)
        
        try:
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            raise e
    
    def update_partial_by_uuid(self, db: Session, uuid: str, obj_update: Any) -> Optional[ModelType]:
        """
        Update a record partially (PATCH) by UUID.
        Only updates provided fields.
        
        Args:
            db: Database session
            uuid: UUID of the record
            obj_update: Pydantic schema for partial update
            
        Returns:
            The updated database object if found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        db_obj = self.get_by_uuid(db, uuid)
        if not db_obj:
            return None
        
        # Get update data, excluding None values
        update_data = obj_update.dict(exclude_unset=True)
        
        if not update_data:
            return db_obj
        
        # Update fields
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        # Set audit fields if any field was updated
        if update_data:
            self._set_audit_fields(db_obj, update_data)
        
        try:
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            raise e
    
    def update_full(self, db: Session, id: int, obj_replace: Any) -> Optional[ModelType]:
        """
        Replace a record completely (PUT) by ID.
        Updates all fields with provided values.
        
        Args:
            db: Database session
            id: Primary key ID
            obj_replace: Pydantic schema for complete replacement
            
        Returns:
            The updated database object if found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        db_obj = self.get(db, id)
        if not db_obj:
            return None
        
        # Get all data from the replace schema
        replace_data = obj_replace.dict()
        
        # Update all fields
        for field, value in replace_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        # Set audit fields
        self._set_audit_fields(db_obj, replace_data)
        
        try:
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            raise e
    
    def update_full_by_uuid(self, db: Session, uuid: str, obj_replace: Any) -> Optional[ModelType]:
        """
        Replace a record completely (PUT) by UUID.
        Updates all fields with provided values.
        
        Args:
            db: Database session
            uuid: UUID of the record
            obj_replace: Pydantic schema for complete replacement
            
        Returns:
            The updated database object if found, None otherwise
            
        Raises:
            Exception: If database operation fails
        """
        db_obj = self.get_by_uuid(db, uuid)
        if not db_obj:
            return None
        
        # Get all data from the replace schema
        replace_data = obj_replace.dict()
        
        # Update all fields
        for field, value in replace_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        # Set audit fields
        self._set_audit_fields(db_obj, replace_data)
        
        try:
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except Exception as e:
            db.rollback()
            raise e
    
    def list(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        List records with pagination.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of database objects
        """
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def get_updated_fields(self, original_obj: ModelType, updated_obj: ModelType) -> List[str]:
        """
        Get list of fields that were updated.
        
        Args:
            original_obj: Original database object
            updated_obj: Updated database object
            
        Returns:
            List of field names that were updated
        """
        updated_fields = []
        
        # Compare all fields
        for field in self.model.__table__.columns:
            field_name = field.name
            original_value = getattr(original_obj, field_name)
            updated_value = getattr(updated_obj, field_name)
            
            if original_value != updated_value:
                updated_fields.append(field_name)
        
        return updated_fields
    
    def _set_default_values(self, obj_data: Dict[str, Any]) -> None:
        """
        Set default values for new objects based on model type.
        Override this method in subclasses for entity-specific defaults.
        
        Args:
            obj_data: Dictionary containing object data
        """
        # Default implementation - subclasses can override
        pass
    
    def _set_audit_fields(self, db_obj: ModelType, update_data: Dict[str, Any]) -> None:
        """
        Set audit fields when updating objects.
        Override this method in subclasses for entity-specific audit fields.
        
        Args:
            db_obj: Database object being updated
            update_data: Data being used for the update
        """
        # Default implementation - subclasses can override
        pass
```

## 2. Concepts CRUD Implementation

### File: `app/crud/concepts.py`

```python
"""
Concepts CRUD operations.
Provides concept-specific database operations inheriting from BaseCRUD.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from .base import BaseCRUD
from app.models import Concept
from app.schemas import ConceptCreate, ConceptUpdate, ConceptReplace


class ConceptsCRUD(BaseCRUD[Concept]):
    """
    CRUD operations for Concept entities.
    
    Provides concept-specific database operations including search,
    filtering by various criteria, and concept lifecycle management.
    """
    
    def __init__(self):
        """Initialize with the Concept model."""
        super().__init__(Concept)
    
    def _set_default_values(self, obj_data: dict) -> None:
        """Set concept-specific default values."""
        obj_data['retired'] = False
    
    def _set_audit_fields(self, db_obj: Concept, update_data: dict) -> None:
        """Set concept-specific audit fields."""
        db_obj.changed_by = update_data.get('changed_by', db_obj.changed_by)
        db_obj.date_changed = datetime.utcnow()
    
    def get_by_name(self, db: Session, name: str) -> Optional[Concept]:
        """
        Get concept by short name.
        
        Args:
            db: Database session
            name: Short name of the concept
            
        Returns:
            The concept if found, None otherwise
        """
        return db.query(Concept).filter(Concept.short_name == name).first()
    
    def get_by_description(self, db: Session, description: str) -> Optional[Concept]:
        """
        Get concept by description.
        
        Args:
            db: Database session
            description: Description of the concept
            
        Returns:
            The concept if found, None otherwise
        """
        return db.query(Concept).filter(Concept.description == description).first()
    
    def get_concepts_by_datatype(self, db: Session, datatype_id: int, skip: int = 0, limit: int = 100) -> List[Concept]:
        """
        Get concepts for a specific datatype.
        
        Args:
            db: Database session
            datatype_id: ID of the datatype
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of concepts with the specified datatype
        """
        return db.query(Concept).filter(
            and_(Concept.datatype_id == datatype_id, Concept.retired == False)
        ).offset(skip).limit(limit).all()
    
    def get_concepts_by_class(self, db: Session, class_id: int, skip: int = 0, limit: int = 100) -> List[Concept]:
        """
        Get concepts for a specific class.
        
        Args:
            db: Database session
            class_id: ID of the concept class
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of concepts with the specified class
        """
        return db.query(Concept).filter(
            and_(Concept.class_id == class_id, Concept.retired == False)
        ).offset(skip).limit(limit).all()
    
    def get_concepts_by_creator(self, db: Session, creator: int, skip: int = 0, limit: int = 100) -> List[Concept]:
        """
        Get concepts created by a specific user.
        
        Args:
            db: Database session
            creator: ID of the user who created the concepts
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of concepts created by the specified user
        """
        return db.query(Concept).filter(
            and_(Concept.creator == creator, Concept.retired == False)
        ).offset(skip).limit(limit).all()
    
    def search_concepts_by_name(self, db: Session, name: str, skip: int = 0, limit: int = 100) -> List[Concept]:
        """
        Search concepts by short_name or description.
        
        Args:
            db: Database session
            name: Search term for concept name or description
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of concepts matching the search criteria
        """
        return db.query(Concept).filter(
            and_(
                Concept.retired == False,
                (Concept.short_name.contains(name) | Concept.description.contains(name))
            )
        ).offset(skip).limit(limit).all()
    
    def get_active_concepts(self, db: Session, skip: int = 0, limit: int = 100) -> List[Concept]:
        """
        Get only active (non-retired) concepts.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active concepts
        """
        return db.query(Concept).filter(
            Concept.retired == False
        ).offset(skip).limit(limit).all()
    
    def get_retired_concepts(self, db: Session, skip: int = 0, limit: int = 100) -> List[Concept]:
        """
        Get only retired concepts.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of retired concepts
        """
        return db.query(Concept).filter(
            Concept.retired == True
        ).offset(skip).limit(limit).all()
    
    def retire_concept(self, db: Session, concept_id: int, retired_by: int, reason: str = None) -> Optional[Concept]:
        """
        Retire a concept.
        
        Args:
            db: Database session
            concept_id: ID of the concept to retire
            retired_by: ID of the user retiring the concept
            reason: Optional reason for retirement
            
        Returns:
            The retired concept if found, None otherwise
        """
        db_concept = self.get(db, concept_id)
        if not db_concept:
            return None
        
        db_concept.retired = True
        db_concept.retired_by = retired_by
        db_concept.date_retired = datetime.utcnow()
        db_concept.retire_reason = reason
        
        try:
            db.commit()
            db.refresh(db_concept)
            return db_concept
        except Exception as e:
            db.rollback()
            raise e
    
    def unretire_concept(self, db: Session, concept_id: int, unretired_by: int) -> Optional[Concept]:
        """
        Unretire a concept.
        
        Args:
            db: Database session
            concept_id: ID of the concept to unretire
            unretired_by: ID of the user unretiring the concept
            
        Returns:
            The unretired concept if found, None otherwise
        """
        db_concept = self.get(db, concept_id)
        if not db_concept:
            return None
        
        db_concept.retired = False
        db_concept.retired_by = None
        db_concept.date_retired = None
        db_concept.retire_reason = None
        
        try:
            db.commit()
            db.refresh(db_concept)
            return db_concept
        except Exception as e:
            db.rollback()
            raise e
```

## 3. Backward Compatibility Layer

### File: `app/crud/compatibility.py`

```python
"""
Compatibility layer for the old function-based CRUD API.
This module maintains backward compatibility while using the new class-based structure.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from .concepts import ConceptsCRUD
from .encounters import EncountersCRUD
from .observations import ObservationsCRUD
from .orders import OrdersCRUD
from app.schemas import (
    OrderUpdate, OrderReplace, ObsUpdate, ObsReplace, ObsCreate,
    ConceptUpdate, ConceptReplace, ConceptCreate,
    EncounterUpdate, EncounterReplace, EncounterCreate
)

# Initialize CRUD instances
concepts_crud = ConceptsCRUD()
encounters_crud = EncountersCRUD()
observations_crud = ObservationsCRUD()
orders_crud = OrdersCRUD()

# ============================================================================
# CONCEPT CRUD OPERATIONS (Compatibility Functions)
# ============================================================================

def create_concept(db: Session, concept_create: ConceptCreate):
    """Create a new concept - Compatibility function"""
    return concepts_crud.create(db, concept_create)

def get_concept(db: Session, concept_id: int):
    """Get concept by ID - Compatibility function"""
    return concepts_crud.get(db, concept_id)

def get_concept_by_uuid(db: Session, uuid: str):
    """Get concept by UUID - Compatibility function"""
    return concepts_crud.get_by_uuid(db, uuid)

def update_concept_partial(db: Session, concept_id: int, concept_update: ConceptUpdate):
    """Update concept partially (PATCH) by ID - Compatibility function"""
    return concepts_crud.update_partial(db, concept_id, concept_update)

def update_concept_partial_by_uuid(db: Session, uuid: str, concept_update: ConceptUpdate):
    """Update concept partially (PATCH) by UUID - Compatibility function"""
    return concepts_crud.update_partial_by_uuid(db, uuid, concept_update)

def update_concept_full(db: Session, concept_id: int, concept_replace: ConceptReplace):
    """Replace concept completely (PUT) by ID - Compatibility function"""
    return concepts_crud.update_full(db, concept_id, concept_replace)

def update_concept_full_by_uuid(db: Session, uuid: str, concept_replace: ConceptReplace):
    """Replace concept completely (PUT) by UUID - Compatibility function"""
    return concepts_crud.update_full_by_uuid(db, uuid, concept_replace)

def get_updated_concept_fields(original_concept, updated_concept):
    """Get list of fields that were updated - Compatibility function"""
    return concepts_crud.get_updated_fields(original_concept, updated_concept)

def list_concepts(db: Session, skip: int = 0, limit: int = 100):
    """List concepts with pagination - Compatibility function"""
    return concepts_crud.list(db, skip, limit)

def get_concepts_by_datatype(db: Session, datatype_id: int, skip: int = 0, limit: int = 100):
    """Get concepts for a specific datatype - Compatibility function"""
    return concepts_crud.get_concepts_by_datatype(db, datatype_id, skip, limit)

def get_concepts_by_class(db: Session, class_id: int, skip: int = 0, limit: int = 100):
    """Get concepts for a specific class - Compatibility function"""
    return concepts_crud.get_concepts_by_class(db, class_id, skip, limit)

def get_concepts_by_creator(db: Session, creator: int, skip: int = 0, limit: int = 100):
    """Get concepts created by a specific user - Compatibility function"""
    return concepts_crud.get_concepts_by_creator(db, creator, skip, limit)

def search_concepts_by_name(db: Session, name: str, skip: int = 0, limit: int = 100):
    """Search concepts by short_name or description - Compatibility function"""
    return concepts_crud.search_concepts_by_name(db, name, skip, limit)

def get_active_concepts(db: Session, skip: int = 0, limit: int = 100):
    """Get only active (non-retired) concepts - Compatibility function"""
    return concepts_crud.get_active_concepts(db, skip, limit)

def get_retired_concepts(db: Session, skip: int = 0, limit: int = 100):
    """Get only retired concepts - Compatibility function"""
    return concepts_crud.get_retired_concepts(db, skip, limit)

# ============================================================================
# ENCOUNTER CRUD OPERATIONS (Compatibility Functions)
# ============================================================================

def create_encounter(db: Session, encounter_create: EncounterCreate):
    """Create a new encounter - Compatibility function"""
    return encounters_crud.create(db, encounter_create)

def get_encounter(db: Session, encounter_id: int):
    """Get encounter by ID - Compatibility function"""
    return encounters_crud.get(db, encounter_id)

def get_encounter_by_uuid(db: Session, uuid: str):
    """Get encounter by UUID - Compatibility function"""
    return encounters_crud.get_by_uuid(db, uuid)

def update_encounter_partial(db: Session, encounter_id: int, encounter_update: EncounterUpdate):
    """Update encounter partially (PATCH) by ID - Compatibility function"""
    return encounters_crud.update_partial(db, encounter_id, encounter_update)

def update_encounter_partial_by_uuid(db: Session, uuid: str, encounter_update: EncounterUpdate):
    """Update encounter partially (PATCH) by UUID - Compatibility function"""
    return encounters_crud.update_partial_by_uuid(db, uuid, encounter_update)

def update_encounter_full(db: Session, encounter_id: int, encounter_replace: EncounterReplace):
    """Replace encounter completely (PUT) by ID - Compatibility function"""
    return encounters_crud.update_full(db, encounter_id, encounter_replace)

def update_encounter_full_by_uuid(db: Session, uuid: str, encounter_replace: EncounterReplace):
    """Replace encounter completely (PUT) by UUID - Compatibility function"""
    return encounters_crud.update_full_by_uuid(db, uuid, encounter_replace)

def get_updated_encounter_fields(original_encounter, updated_encounter):
    """Get list of fields that were updated - Compatibility function"""
    return encounters_crud.get_updated_fields(original_encounter, updated_encounter)

def list_encounters(db: Session, skip: int = 0, limit: int = 100):
    """List encounters with pagination - Compatibility function"""
    return encounters_crud.list(db, skip, limit)

def get_encounters_by_patient(db: Session, patient_id: int, skip: int = 0, limit: int = 100):
    """Get encounters for a specific patient - Compatibility function"""
    return encounters_crud.get_encounters_by_patient(db, patient_id, skip, limit)

def get_encounters_by_type(db: Session, encounter_type: int, skip: int = 0, limit: int = 100):
    """Get encounters for a specific encounter type - Compatibility function"""
    return encounters_crud.get_encounters_by_type(db, encounter_type, skip, limit)

def get_encounters_by_location(db: Session, location_id: int, skip: int = 0, limit: int = 100):
    """Get encounters for a specific location - Compatibility function"""
    return encounters_crud.get_encounters_by_location(db, location_id, skip, limit)

def get_encounters_by_visit(db: Session, visit_id: int, skip: int = 0, limit: int = 100):
    """Get encounters for a specific visit - Compatibility function"""
    return encounters_crud.get_encounters_by_visit(db, visit_id, skip, limit)

def get_encounters_by_creator(db: Session, creator: int, skip: int = 0, limit: int = 100):
    """Get encounters created by a specific user - Compatibility function"""
    return encounters_crud.get_encounters_by_creator(db, creator, skip, limit)

def get_encounters_by_date_range(db: Session, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100):
    """Get encounters within a date range - Compatibility function"""
    return encounters_crud.get_encounters_by_date_range(db, start_date, end_date, skip, limit)

def get_active_encounters(db: Session, skip: int = 0, limit: int = 100):
    """Get only active (non-voided) encounters - Compatibility function"""
    return encounters_crud.get_active_encounters(db, skip, limit)

def get_voided_encounters(db: Session, skip: int = 0, limit: int = 100):
    """Get only voided encounters - Compatibility function"""
    return encounters_crud.get_voided_encounters(db, skip, limit)

# ============================================================================
# OBSERVATION CRUD OPERATIONS (Compatibility Functions)
# ============================================================================

def create_obs(db: Session, obs_create: ObsCreate):
    """Create a new observation - Compatibility function"""
    return observations_crud.create(db, obs_create)

def get_obs(db: Session, obs_id: int):
    """Get observation by ID - Compatibility function"""
    return observations_crud.get(db, obs_id)

def get_obs_by_uuid(db: Session, uuid: str):
    """Get observation by UUID - Compatibility function"""
    return observations_crud.get_by_uuid(db, uuid)

def update_obs_partial(db: Session, obs_id: int, obs_update: ObsUpdate):
    """Update observation partially (PATCH) by ID - Compatibility function"""
    return observations_crud.update_partial(db, obs_id, obs_update)

def update_obs_partial_by_uuid(db: Session, uuid: str, obs_update: ObsUpdate):
    """Update observation partially (PATCH) by UUID - Compatibility function"""
    return observations_crud.update_partial_by_uuid(db, uuid, obs_update)

def update_obs_full(db: Session, obs_id: int, obs_replace: ObsReplace):
    """Replace observation completely (PUT) by ID - Compatibility function"""
    return observations_crud.update_full(db, obs_id, obs_replace)

def update_obs_full_by_uuid(db: Session, uuid: str, obs_replace: ObsReplace):
    """Replace observation completely (PUT) by UUID - Compatibility function"""
    return observations_crud.update_full_by_uuid(db, uuid, obs_replace)

def get_updated_obs_fields(original_obs, updated_obs):
    """Get list of fields that were updated - Compatibility function"""
    return observations_crud.get_updated_fields(original_obs, updated_obs)

def list_obs(db: Session, skip: int = 0, limit: int = 100):
    """List observations with pagination - Compatibility function"""
    return observations_crud.list(db, skip, limit)

def get_obs_by_person(db: Session, person_id: int, skip: int = 0, limit: int = 100):
    """Get observations for a specific person - Compatibility function"""
    return observations_crud.get_obs_by_person(db, person_id, skip, limit)

def get_obs_by_encounter(db: Session, encounter_id: int, skip: int = 0, limit: int = 100):
    """Get observations for a specific encounter - Compatibility function"""
    return observations_crud.get_obs_by_encounter(db, encounter_id, skip, limit)

def get_obs_by_concept(db: Session, concept_id: int, skip: int = 0, limit: int = 100):
    """Get observations for a specific concept - Compatibility function"""
    return observations_crud.get_obs_by_concept(db, concept_id, skip, limit)

def get_obs_by_order(db: Session, order_id: int, skip: int = 0, limit: int = 100):
    """Get observations for a specific order - Compatibility function"""
    return observations_crud.get_obs_by_order(db, order_id, skip, limit)

# ============================================================================
# ORDER CRUD OPERATIONS (Compatibility Functions)
# ============================================================================

def get_order(db: Session, order_id: int):
    """Get order by ID - Compatibility function"""
    return orders_crud.get(db, order_id)

def get_order_by_uuid(db: Session, uuid: str):
    """Get order by UUID - Compatibility function"""
    return orders_crud.get_by_uuid(db, uuid)

def get_order_by_number(db: Session, order_number: str):
    """Get order by order number - Compatibility function"""
    return orders_crud.get_by_number(db, order_number)

def update_order_partial(db: Session, order_id: int, order_update: OrderUpdate):
    """Update order partially (PATCH) by ID - Compatibility function"""
    return orders_crud.update_partial(db, order_id, order_update)

def update_order_partial_by_uuid(db: Session, uuid: str, order_update: OrderUpdate):
    """Update order partially (PATCH) by UUID - Compatibility function"""
    return orders_crud.update_partial_by_uuid(db, uuid, order_update)

def update_order_full(db: Session, order_id: int, order_replace: OrderReplace):
    """Replace order completely (PUT) by ID - Compatibility function"""
    return orders_crud.update_full(db, order_id, order_replace)

def update_order_full_by_uuid(db: Session, uuid: str, order_replace: OrderReplace):
    """Replace order completely (PUT) by UUID - Compatibility function"""
    return orders_crud.update_full_by_uuid(db, uuid, order_replace)

def get_updated_fields(original_order, updated_order):
    """Get list of fields that were updated - Compatibility function"""
    return orders_crud.get_updated_fields(original_order, updated_order)

def list_orders(db: Session, skip: int = 0, limit: int = 100):
    """List orders with pagination - Compatibility function"""
    return orders_crud.list(db, skip, limit)

def get_orders_by_patient(db: Session, patient_id: int, skip: int = 0, limit: int = 100):
    """Get orders for a specific patient - Compatibility function"""
    return orders_crud.get_orders_by_patient(db, patient_id, skip, limit)
```

## 4. Package Exports

### File: `app/crud/__init__.py`

```python
"""
CRUD package for database operations.
Provides class-based CRUD operations with separation of concerns.
"""

from .base import BaseCRUD
from .concepts import ConceptsCRUD
from .encounters import EncountersCRUD
from .observations import ObservationsCRUD
from .orders import OrdersCRUD

__all__ = [
    "BaseCRUD",
    "ConceptsCRUD", 
    "EncountersCRUD",
    "ObservationsCRUD",
    "OrdersCRUD"
]
```

## 5. Step-by-Step Implementation

### Step 1: Create Directory Structure
```bash
mkdir app/crud
cd app/crud
touch __init__.py base.py concepts.py encounters.py observations.py orders.py compatibility.py
```

### Step 2: Implement Base Class
- Copy the `BaseCRUD` implementation from above
- Test basic functionality with a simple model

### Step 3: Implement Entity Classes
- Start with `ConceptsCRUD` as it's typically simpler
- Copy existing functions from `app/crud.py`
- Adapt them to use the base class methods
- Test thoroughly before moving to next entity

### Step 4: Create Compatibility Layer
- Implement compatibility functions that use new CRUD classes
- Test that old API still works
- Ensure no breaking changes

### Step 5: Update API Endpoints
- Change imports from `app.crud` to `app.crud.compatibility`
- Test each endpoint thoroughly
- Update one endpoint at a time

### Step 6: Test and Validate
- Run all existing tests
- Test new functionality
- Ensure performance is maintained
- Validate all API endpoints work correctly

## 6. Testing Examples

### Basic Test Structure
```python
import pytest
from unittest.mock import Mock
from app.crud import ConceptsCRUD

def test_concepts_crud_initialization():
    """Test that ConceptsCRUD initializes correctly."""
    crud = ConceptsCRUD()
    assert crud.model == Concept

def test_concepts_crud_create():
    """Test concept creation."""
    crud = ConceptsCRUD()
    mock_db = Mock()
    mock_db.add = Mock()
    mock_db.commit = Mock()
    mock_db.refresh = Mock()
    
    # Test implementation...
```

## 7. Migration Checklist

- [ ] Create `app/crud/` directory
- [ ] Implement `BaseCRUD` class
- [ ] Implement `ConceptsCRUD` class
- [ ] Implement `EncountersCRUD` class
- [ ] Implement `ObservationsCRUD` class
- [ ] Implement `OrdersCRUD` class
- [ ] Create compatibility layer
- [ ] Test all CRUD classes
- [ ] Update API endpoint imports
- [ ] Test all API endpoints
- [ ] Validate performance
- [ ] Remove old `app/crud.py` (optional)

## 8. Common Issues and Solutions

### Issue: Import Errors
**Solution**: Ensure all imports are correct and models/schemas exist

### Issue: Database Session Issues
**Solution**: Mock database sessions in tests, use proper session management

### Issue: Type Errors
**Solution**: Check generic type parameters and ensure model types match

### Issue: Performance Degradation
**Solution**: Profile queries and optimize database operations

## 9. Performance Considerations

- The new architecture maintains the same database query performance
- Class instantiation overhead is minimal
- Consider using connection pooling for database sessions
- Use appropriate indexes for frequently queried fields

## 10. Next Steps After Implementation

1. **Add comprehensive tests** for all CRUD classes
2. **Document entity-specific methods** thoroughly
3. **Consider adding new entities** using the same pattern
4. **Optimize database queries** based on usage patterns
5. **Add monitoring and logging** for production use

This implementation provides a solid foundation for future growth while maintaining all existing functionality. Take your time with the migration and test thoroughly at each step. 