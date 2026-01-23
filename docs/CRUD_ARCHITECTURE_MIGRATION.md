# CRUD Architecture Migration Guide

## Overview

This document outlines the planned migration from the current function-based CRUD operations to a class-based architecture with separation of concerns. The new architecture will provide better maintainability, extensibility, and code organization as your CRUD operations grow.

## Current State

### Existing Architecture
- **File**: `app/crud.py` (855 lines)
- **Pattern**: Function-based CRUD operations
- **Structure**: All operations mixed in single file
- **Entities**: Orders, Observations, Concepts, Encounters

### Current Issues
- Single large file becoming unwieldy
- Mixed concerns (all entities in one place)
- Difficult to maintain and extend
- Hard to test individual components
- No clear separation of responsibilities

## Target Architecture

### New Structure
```
app/crud/
├── __init__.py              # Package exports
├── base.py                  # Base CRUD class
├── concepts.py              # Concept-specific operations
├── encounters.py            # Encounter-specific operations
├── observations.py          # Observation-specific operations
├── orders.py                # Order-specific operations
├── compatibility.py         # Backward compatibility layer
└── README.md                # Architecture documentation
```

### Class Hierarchy
```
BaseCRUD (Generic[ModelType])
├── ConceptsCRUD
├── EncountersCRUD
├── ObservationsCRUD
└── OrdersCRUD
```

## Key Benefits

### 1. Separation of Concerns
- Each entity has its own CRUD class
- Clear boundaries between different operations
- Easier to understand and maintain

### 2. Code Reuse
- Common operations defined in base class
- Consistent patterns across all entities
- DRY (Don't Repeat Yourself) principle

### 3. Type Safety
- Generic typing with `ModelType`
- Better IDE support and autocomplete
- Compile-time error checking

### 4. Extensibility
- Easy to add new entities
- Simple to add entity-specific methods
- Consistent interface across all CRUD classes

### 5. Testing
- Individual CRUD classes can be tested in isolation
- Easier to mock and test specific functionality
- Better test coverage and organization

## Implementation Plan

### Phase 1: Create New Architecture
1. **Create `app/crud/` directory**
2. **Implement `BaseCRUD` class** with common operations
3. **Create entity-specific CRUD classes**
4. **Add backward compatibility layer**

### Phase 2: Gradual Migration
1. **Update imports** in API endpoints
2. **Test new functionality** alongside existing code
3. **Migrate one entity at a time**
4. **Validate functionality** after each migration

### Phase 3: Cleanup
1. **Remove old `app/crud.py`**
2. **Update all references**
3. **Remove compatibility layer** (optional)

## Detailed Implementation

### Base CRUD Class (`app/crud/base.py`)

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

ModelType = TypeVar("ModelType")

class BaseCRUD(Generic[ModelType], ABC):
    """Base CRUD class with common database operations."""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    def create(self, db: Session, obj_create: Any) -> ModelType:
        """Create a new record."""
        # Implementation details...
    
    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get record by primary key."""
        # Implementation details...
    
    def get_by_uuid(self, db: Session, uuid: str) -> Optional[ModelType]:
        """Get record by UUID."""
        # Implementation details...
    
    def update_partial(self, db: Session, id: int, obj_update: Any) -> Optional[ModelType]:
        """Partial update (PATCH)."""
        # Implementation details...
    
    def update_full(self, db: Session, id: int, obj_replace: Any) -> Optional[ModelType]:
        """Full update (PUT)."""
        # Implementation details...
    
    def list(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """List records with pagination."""
        # Implementation details...
    
    def _set_default_values(self, obj_data: Dict[str, Any]) -> None:
        """Set entity-specific default values."""
        pass
    
    def _set_audit_fields(self, db_obj: ModelType, update_data: Dict[str, Any]) -> None:
        """Set entity-specific audit fields."""
        pass
```

### Entity-Specific CRUD Classes

#### ConceptsCRUD (`app/crud/concepts.py`)

```python
from .base import BaseCRUD
from app.models import Concept
from app.schemas import ConceptCreate, ConceptUpdate, ConceptReplace

class ConceptsCRUD(BaseCRUD[Concept]):
    """CRUD operations for Concept entities."""
    
    def __init__(self):
        super().__init__(Concept)
    
    def _set_default_values(self, obj_data: dict) -> None:
        obj_data['retired'] = False
    
    def _set_audit_fields(self, db_obj: Concept, update_data: dict) -> None:
        db_obj.changed_by = update_data.get('changed_by', db_obj.changed_by)
        db_obj.date_changed = datetime.utcnow()
    
    # Entity-specific methods
    def get_by_name(self, db: Session, name: str) -> Optional[Concept]:
        """Get concept by short name."""
        return db.query(Concept).filter(Concept.short_name == name).first()
    
    def search_concepts_by_name(self, db: Session, name: str, skip: int = 0, limit: int = 100) -> List[Concept]:
        """Search concepts by name or description."""
        return db.query(Concept).filter(
            and_(Concept.retired == False,
                 (Concept.short_name.contains(name) | Concept.description.contains(name)))
        ).offset(skip).limit(limit).all()
    
    def retire_concept(self, db: Session, concept_id: int, retired_by: int, reason: str = None) -> Optional[Concept]:
        """Retire a concept."""
        # Implementation details...
```

#### EncountersCRUD (`app/crud/encounters.py`)

```python
from .base import BaseCRUD
from app.models import Encounter
from app.schemas import EncounterCreate, EncounterUpdate, EncounterReplace

class EncountersCRUD(BaseCRUD[Encounter]):
    """CRUD operations for Encounter entities."""
    
    def __init__(self):
        super().__init__(Encounter)
    
    def _set_default_values(self, obj_data: dict) -> None:
        obj_data['voided'] = False
    
    # Entity-specific methods
    def get_encounters_by_patient(self, db: Session, patient_id: int, skip: int = 0, limit: int = 100) -> List[Encounter]:
        """Get encounters for a specific patient."""
        return db.query(Encounter).filter(
            and_(Encounter.patient_id == patient_id, Encounter.voided == False)
        ).offset(skip).limit(limit).all()
    
    def void_encounter(self, db: Session, encounter_id: int, voided_by: int, reason: str = None) -> Optional[Encounter]:
        """Void an encounter."""
        # Implementation details...
```

#### ObservationsCRUD (`app/crud/observations.py`)

```python
from .base import BaseCRUD
from app.models import Obs
from app.schemas import ObsCreate, ObsUpdate, ObsReplace

class ObservationsCRUD(BaseCRUD[Obs]):
    """CRUD operations for Observation entities."""
    
    def __init__(self):
        super().__init__(Obs)
    
    def _set_default_values(self, obj_data: dict) -> None:
        obj_data['voided'] = False
    
    # Entity-specific methods
    def get_obs_by_person(self, db: Session, person_id: int, skip: int = 0, limit: int = 100) -> List[Obs]:
        """Get observations for a specific person."""
        return db.query(Obs).filter(
            and_(Obs.person_id == person_id, Obs.voided == False)
        ).offset(skip).limit(limit).all()
    
    def get_obs_by_encounter(self, db: Session, encounter_id: int, skip: int = 0, limit: int = 100) -> List[Obs]:
        """Get observations for a specific encounter."""
        return db.query(Obs).filter(
            and_(Obs.encounter_id == encounter_id, Obs.voided == False)
        ).offset(skip).limit(limit).all()
```

#### OrdersCRUD (`app/crud/orders.py`)

```python
from .base import BaseCRUD
from app.models import Order
from app.schemas import OrderCreate, OrderUpdate, OrderReplace

class OrdersCRUD(BaseCRUD[Order]):
    """CRUD operations for Order entities."""
    
    def __init__(self):
        super().__init__(Order)
    
    def _set_default_values(self, obj_data: dict) -> None:
        obj_data['voided'] = False
    
    # Entity-specific methods
    def get_orders_by_patient(self, db: Session, patient_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get orders for a specific patient."""
        return db.query(Order).filter(
            and_(Order.patient_id == patient_id, Order.voided == False)
        ).offset(skip).limit(limit).all()
    
    def get_orders_by_urgency(self, db: Session, urgency: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get orders by urgency level."""
        return db.query(Order).filter(
            and_(Order.urgency == urgency, Order.voided == False)
        ).offset(skip).limit(limit).all()
```

### Backward Compatibility Layer (`app/crud/compatibility.py`)

```python
"""
Compatibility layer for the old function-based CRUD API.
This maintains backward compatibility while using the new class-based structure.
"""

from .concepts import ConceptsCRUD
from .encounters import EncountersCRUD
from .observations import ObservationsCRUD
from .orders import OrdersCRUD

# Initialize CRUD instances
concepts_crud = ConceptsCRUD()
encounters_crud = EncountersCRUD()
observations_crud = ObservationsCRUD()
orders_crud = OrdersCRUD()

# Compatibility functions that use the new CRUD classes
def get_concept(db: Session, concept_id: int):
    """Get concept by ID - Compatibility function"""
    return concepts_crud.get(db, concept_id)

def create_concept(db: Session, concept_create):
    """Create a new concept - Compatibility function"""
    return concepts_crud.create(db, concept_create)

# ... more compatibility functions for all entities
```

### Package Exports (`app/crud/__init__.py`)

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

## Migration Steps

### Step 1: Create New Directory Structure
```bash
mkdir app/crud
touch app/crud/__init__.py
touch app/crud/base.py
touch app/crud/concepts.py
touch app/crud/encounters.py
touch app/crud/observations.py
touch app/crud/orders.py
touch app/crud/compatibility.py
```

### Step 2: Implement Base CRUD Class
- Copy the `BaseCRUD` implementation from above
- Test basic functionality
- Ensure all common operations work correctly

### Step 3: Implement Entity-Specific Classes
- Start with one entity (e.g., Concepts)
- Copy existing functions and adapt them to class methods
- Test thoroughly before moving to next entity
- Repeat for all entities

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

## Testing Strategy

### Unit Tests
- Test each CRUD class individually
- Mock database sessions
- Test error conditions and edge cases

### Integration Tests
- Test with real database
- Test API endpoints
- Test backward compatibility

### Performance Tests
- Ensure no performance regression
- Test with large datasets
- Monitor memory usage

## Risk Mitigation

### 1. Gradual Migration
- Don't migrate everything at once
- Test each component thoroughly
- Have rollback plan ready

### 2. Backward Compatibility
- Maintain existing API during transition
- No breaking changes to existing code
- Clear migration path for developers

### 3. Testing
- Comprehensive test coverage
- Test both old and new APIs
- Performance benchmarking

## Benefits After Migration

### Immediate Benefits
- Better code organization
- Easier to understand and maintain
- Clear separation of concerns

### Long-term Benefits
- Easier to add new entities
- Better testing capabilities
- Improved developer experience
- Consistent patterns across codebase

### Performance Benefits
- No performance regression
- Better memory management
- Optimized database queries

## Conclusion

This migration will significantly improve your codebase's maintainability and extensibility. The class-based architecture provides a solid foundation for future growth while maintaining all existing functionality.

The key is to take a gradual approach, testing thoroughly at each step, and ensuring backward compatibility throughout the process. This will minimize risk while maximizing the benefits of the new architecture.

## Next Steps

1. **Review this document** thoroughly
2. **Plan the migration timeline** based on your team's capacity
3. **Start with a small entity** (e.g., Concepts) as a proof of concept
4. **Test extensively** before proceeding
5. **Gradually expand** to other entities
6. **Monitor and optimize** as you go

Remember: This is a significant architectural improvement that will pay dividends in the long run, but it's important to implement it carefully and methodically. 