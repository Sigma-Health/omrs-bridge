from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from .base import BaseCRUD
from app.models import Concept


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
        obj_data["retired"] = False

    def _set_audit_fields(self, db_obj: Concept, update_data: dict) -> None:
        """Set concept-specific audit fields."""
        db_obj.changed_by = update_data.get("changed_by", db_obj.changed_by)
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

    def get_concepts_by_datatype(
        self, db: Session, datatype_id: int, skip: int = 0, limit: int = 100
    ) -> List[Concept]:
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
        return (
            db.query(Concept)
            .filter(and_(Concept.datatype_id == datatype_id, Concept.retired == False))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_concepts_by_class(
        self, db: Session, class_id: int, skip: int = 0, limit: int = 100
    ) -> List[Concept]:
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
        return (
            db.query(Concept)
            .filter(and_(Concept.class_id == class_id, Concept.retired == False))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_concepts_by_creator(
        self, db: Session, creator: int, skip: int = 0, limit: int = 100
    ) -> List[Concept]:
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
        return (
            db.query(Concept)
            .filter(and_(Concept.creator == creator, Concept.retired == False))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_concepts_by_name(
        self, db: Session, name: str, skip: int = 0, limit: int = 100
    ) -> List[Concept]:
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
        return (
            db.query(Concept)
            .filter(
                and_(
                    Concept.retired == False,
                    (
                        Concept.short_name.contains(name)
                        | Concept.description.contains(name)
                    ),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_concepts(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[Concept]:
        """
        Get only active (non-retired) concepts.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active concepts
        """
        return (
            db.query(Concept)
            .filter(Concept.retired == False)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_retired_concepts(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[Concept]:
        """
        Get only retired concepts.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of retired concepts
        """
        return (
            db.query(Concept)
            .filter(
                Concept.retired == True  # noqa: E712
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def retire_concept(
        self, db: Session, concept_id: int, retired_by: int, reason: str = None
    ) -> Optional[Concept]:
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

    def unretire_concept(
        self, db: Session, concept_id: int, unretired_by: int
    ) -> Optional[Concept]:
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
