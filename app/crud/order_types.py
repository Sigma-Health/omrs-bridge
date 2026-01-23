"""
Order Type-specific CRUD operations.
Extends BaseCRUD with order type-specific functionality.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .base import BaseCRUD
from app.models import OrderType


class OrderTypesCRUD(BaseCRUD[OrderType]):
    """
    CRUD operations for OrderType model.

    Provides order type-specific database operations including:
    - Basic CRUD operations (inherited from BaseCRUD)
    - Order type-specific queries (by name, java class, parent, etc.)
    - Order type status management (active, retired)
    """

    def __init__(self):
        super().__init__(OrderType)

    def get_by_name(self, db: Session, name: str) -> Optional[OrderType]:
        """
        Get order type by name.

        Args:
            db: Database session
            name: Order type name

        Returns:
            Order type if found, None otherwise
        """
        return db.query(self.model).filter(self.model.name == name).first()

    def get_active_order_types(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[OrderType]:
        """
        Get active (non-retired) order types.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active order types
        """
        return (
            db.query(self.model)
            .filter(self.model.retired == False)
            .order_by(self.model.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_retired_order_types(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[OrderType]:
        """
        Get retired order types.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of retired order types
        """
        return (
            db.query(self.model)
            .filter(self.model.retired == True)
            .order_by(self.model.date_retired.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_java_class(
        self, db: Session, java_class_name: str, skip: int = 0, limit: int = 100
    ) -> List[OrderType]:
        """
        Get order types by Java class name.

        Args:
            db: Database session
            java_class_name: Java class name
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of order types with the specified Java class
        """
        return (
            db.query(self.model)
            .filter(self.model.java_class_name == java_class_name)
            .order_by(self.model.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_parent(
        self, db: Session, parent_id: int, skip: int = 0, limit: int = 100
    ) -> List[OrderType]:
        """
        Get order types by parent ID.

        Args:
            db: Database session
            parent_id: Parent order type ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of child order types
        """
        return (
            db.query(self.model)
            .filter(self.model.parent == parent_id)
            .order_by(self.model.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_root_order_types(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[OrderType]:
        """
        Get root order types (no parent).

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of root order types
        """
        return (
            db.query(self.model)
            .filter(self.model.parent.is_(None))
            .order_by(self.model.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_order_types(
        self, db: Session, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[OrderType]:
        """
        Search order types by name or description.

        Args:
            db: Database session
            search_term: Search term for name or description
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching order types
        """
        search_pattern = f"%{search_term}%"
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.retired == False,
                    (
                        self.model.name.ilike(search_pattern)
                        | self.model.description.ilike(search_pattern)
                    ),
                )
            )
            .order_by(self.model.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def retire_order_type(
        self,
        db: Session,
        order_type_id: int,
        retired_by: int,
        retire_reason: Optional[str] = None,
    ) -> Optional[OrderType]:
        """
        Retire an order type.

        Args:
            db: Database session
            order_type_id: Order type ID
            retired_by: User ID who retired the order type
            retire_reason: Optional reason for retirement

        Returns:
            Updated order type if found, None otherwise

        Raises:
            Exception: If database operation fails
        """
        order_type = self.get(db, order_type_id)
        if not order_type:
            return None

        from datetime import datetime

        order_type.retired = True
        order_type.retired_by = retired_by
        order_type.date_retired = datetime.utcnow()
        order_type.retire_reason = retire_reason
        order_type.changed_by = retired_by
        order_type.date_changed = datetime.utcnow()

        try:
            db.commit()
            db.refresh(order_type)
            return order_type
        except Exception as e:
            db.rollback()
            raise e

    def unretire_order_type(
        self, db: Session, order_type_id: int, unretired_by: int
    ) -> Optional[OrderType]:
        """
        Unretire an order type.

        Args:
            db: Database session
            order_type_id: Order type ID
            unretired_by: User ID who unretired the order type

        Returns:
            Updated order type if found, None otherwise

        Raises:
            Exception: If database operation fails
        """
        order_type = self.get(db, order_type_id)
        if not order_type:
            return None

        from datetime import datetime

        order_type.retired = False
        order_type.retired_by = None
        order_type.date_retired = None
        order_type.retire_reason = None
        order_type.changed_by = unretired_by
        order_type.date_changed = datetime.utcnow()

        try:
            db.commit()
            db.refresh(order_type)
            return order_type
        except Exception as e:
            db.rollback()
            raise e

    def _set_default_values(self, obj_data: dict) -> None:
        """
        Set default values for new order type objects.

        Args:
            obj_data: Dictionary containing order type data
        """
        # Set default retired status if not provided
        if "retired" not in obj_data:
            obj_data["retired"] = False

    def _set_audit_fields(self, db_obj: OrderType, update_data: dict) -> None:
        """
        Set audit fields when updating order type objects.

        Args:
            db_obj: Order type object being updated
            update_data: Data being used for the update
        """
        from datetime import datetime

        # Set changed_by and date_changed if not already set
        if not hasattr(db_obj, "changed_by") or db_obj.changed_by is None:
            # Try to get from update_data, otherwise use creator
            db_obj.changed_by = update_data.get("changed_by", db_obj.creator)

        db_obj.date_changed = datetime.utcnow()
