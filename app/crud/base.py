from abc import ABC
from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy.orm import Session
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
        obj_data["uuid"] = obj_uuid
        obj_data["date_created"] = datetime.utcnow()

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
        return (
            db.query(self.model)
            .filter(self.model.__table__.primary_key.columns[0] == id)
            .first()
        )

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

    def update_partial(
        self, db: Session, id: int, obj_update: Any
    ) -> Optional[ModelType]:
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

    def update_partial_by_uuid(
        self, db: Session, uuid: str, obj_update: Any
    ) -> Optional[ModelType]:
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

    def update_full(
        self, db: Session, id: int, obj_replace: Any
    ) -> Optional[ModelType]:
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

    def update_full_by_uuid(
        self, db: Session, uuid: str, obj_replace: Any
    ) -> Optional[ModelType]:
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

    def get_updated_fields(
        self, original_obj: ModelType, updated_obj: ModelType
    ) -> List[str]:
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
