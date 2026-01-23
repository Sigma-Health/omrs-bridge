"""
Visit Type-specific CRUD operations.
Extends BaseCRUD with visit type-specific functionality.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .base import BaseCRUD
from app.models import VisitType


class VisitTypesCRUD(BaseCRUD[VisitType]):
    """
    CRUD operations for VisitType model.

    Provides visit type-specific database operations including:
    - Basic CRUD operations (inherited from BaseCRUD)
    - Visit type-specific queries (by name, active, retired, etc.)
    - Visit type status management (active, retired)
    """

    def __init__(self):
        super().__init__(VisitType)

    def get_by_name(self, db: Session, name: str) -> Optional[VisitType]:
        """
        Get visit type by name.

        Args:
            db: Database session
            name: Visit type name

        Returns:
            Visit type if found, None otherwise
        """
        return db.query(self.model).filter(self.model.name == name).first()

    def get_active_visit_types(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[VisitType]:
        """
        Get active (non-retired) visit types.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active visit types
        """
        return (
            db.query(self.model)
            .filter(self.model.retired == False)
            .order_by(self.model.name.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_retired_visit_types(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[VisitType]:
        """
        Get retired visit types.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of retired visit types
        """
        return (
            db.query(self.model)
            .filter(self.model.retired == True)
            .order_by(self.model.date_retired.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_visit_types(
        self, db: Session, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[VisitType]:
        """
        Search visit types by name or description.

        Args:
            db: Database session
            search_term: Search term for name or description
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching visit types
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

    def retire_visit_type(
        self,
        db: Session,
        visit_type_id: int,
        retired_by: int,
        retire_reason: Optional[str] = None,
    ) -> Optional[VisitType]:
        """
        Retire a visit type.

        Args:
            db: Database session
            visit_type_id: Visit type ID
            retired_by: User ID who retired the visit type
            retire_reason: Optional reason for retirement

        Returns:
            Updated visit type if found, None otherwise

        Raises:
            Exception: If database operation fails
        """
        visit_type = self.get(db, visit_type_id)
        if not visit_type:
            return None

        from datetime import datetime

        visit_type.retired = True
        visit_type.retired_by = retired_by
        visit_type.date_retired = datetime.utcnow()
        visit_type.retire_reason = retire_reason
        visit_type.changed_by = retired_by
        visit_type.date_changed = datetime.utcnow()

        try:
            db.commit()
            db.refresh(visit_type)
            return visit_type
        except Exception as e:
            db.rollback()
            raise e

    def unretire_visit_type(
        self, db: Session, visit_type_id: int, unretired_by: int
    ) -> Optional[VisitType]:
        """
        Unretire a visit type.

        Args:
            db: Database session
            visit_type_id: Visit type ID
            unretired_by: User ID who unretired the visit type

        Returns:
            Updated visit type if found, None otherwise

        Raises:
            Exception: If database operation fails
        """
        visit_type = self.get(db, visit_type_id)
        if not visit_type:
            return None

        from datetime import datetime

        visit_type.retired = False
        visit_type.retired_by = None
        visit_type.date_retired = None
        visit_type.retire_reason = None
        visit_type.changed_by = unretired_by
        visit_type.date_changed = datetime.utcnow()

        try:
            db.commit()
            db.refresh(visit_type)
            return visit_type
        except Exception as e:
            db.rollback()
            raise e

    def _set_default_values(self, obj_data: dict) -> None:
        """
        Set default values for new visit type objects.

        Args:
            obj_data: Dictionary containing visit type data
        """
        # Set default retired status if not provided
        if "retired" not in obj_data:
            obj_data["retired"] = False

    def _set_audit_fields(self, db_obj: VisitType, update_data: dict) -> None:
        """
        Set audit fields when updating visit type objects.

        Args:
            db_obj: Visit type object being updated
            update_data: Data being used for the update
        """
        from datetime import datetime

        # Set changed_by and date_changed if not already set
        if not hasattr(db_obj, "changed_by") or db_obj.changed_by is None:
            # Try to get from update_data, otherwise use creator
            db_obj.changed_by = update_data.get("changed_by", db_obj.creator)

        db_obj.date_changed = datetime.utcnow()

