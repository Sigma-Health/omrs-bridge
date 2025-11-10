from typing import List, Optional
from sqlalchemy.orm import Session, selectinload, with_loader_criteria
from sqlalchemy import and_, or_, func
from datetime import datetime

from .base import BaseCRUD

from app.models import Concept, ConceptName, ConceptClass


class ConceptsCRUD(BaseCRUD[Concept]):
    """
    CRUD operations for Concept entities.

    Provides concept-specific database operations including search,
    filtering by various criteria, and concept lifecycle management.
    """

    def __init__(self):
        """Initialize with the Concept model."""
        super().__init__(Concept)

    def _query_with_names(self, db: Session, locale: Optional[str] = None):
        """Return base concept query with concept names eagerly loaded.

        Args:
            db: Database session
            locale: Optional locale filter for concept names
        """
        query = db.query(Concept).options(selectinload(Concept.names))

        if locale:
            query = query.options(
                with_loader_criteria(
                    ConceptName,
                    ConceptName.locale == locale,
                    include_aliases=True,
                )
            )

        return query

    def list(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        locale: Optional[str] = None,
    ) -> List[Concept]:
        """
        List concepts with eager-loaded names.
        """
        return self._query_with_names(db, locale=locale).offset(skip).limit(limit).all()

    def get(
        self, db: Session, id: int, locale: Optional[str] = None
    ) -> Optional[Concept]:
        """
        Get a concept by ID with names eagerly loaded.
        """
        return (
            self._query_with_names(db, locale=locale)
            .filter(Concept.concept_id == id)
            .first()
        )

    def get_by_uuid(
        self, db: Session, uuid: str, locale: Optional[str] = None
    ) -> Optional[Concept]:
        """
        Get a concept by UUID with names eagerly loaded.
        """
        return (
            self._query_with_names(db, locale=locale)
            .filter(Concept.uuid == uuid)
            .first()
        )

    def _set_default_values(self, obj_data: dict) -> None:
        """Set concept-specific default values."""
        obj_data["retired"] = False

    def _set_audit_fields(self, db_obj: Concept, update_data: dict) -> None:
        """Set concept-specific audit fields."""
        db_obj.changed_by = update_data.get("changed_by", db_obj.changed_by)
        db_obj.date_changed = datetime.utcnow()

    def get_by_name(
        self, db: Session, name: str, locale: Optional[str] = None
    ) -> Optional[Concept]:
        """
        Get concept by short name.

        Args:
            db: Database session
            name: Short name of the concept

        Returns:
            The concept if found, None otherwise
        """
        return (
            self._query_with_names(db, locale=locale)
            .filter(Concept.short_name == name)
            .first()
        )

    def get_by_short_name(
        self, db: Session, short_name: str, locale: Optional[str] = None
    ) -> Optional[Concept]:
        """
        Compatibility helper for APIs that reference get_by_short_name.
        """
        return self.get_by_name(db, short_name, locale=locale)

    def get_by_description(
        self, db: Session, description: str, locale: Optional[str] = None
    ) -> Optional[Concept]:
        """
        Get concept by description.

        Args:
            db: Database session
            description: Description of the concept

        Returns:
            The concept if found, None otherwise
        """
        return (
            self._query_with_names(db, locale=locale)
            .filter(Concept.description == description)
            .first()
        )

    def get_concepts_by_datatype(
        self,
        db: Session,
        datatype_id: int,
        skip: int = 0,
        limit: int = 100,
        locale: Optional[str] = None,
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
            self._query_with_names(db, locale=locale)
            .filter(
                and_(
                    Concept.datatype_id == datatype_id,
                    Concept.retired.is_(False),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_concepts_by_class(
        self,
        db: Session,
        class_identifier: str,
        skip: int = 0,
        limit: int = 100,
        locale: Optional[str] = None,
    ) -> List[Concept]:
        """
        Get concepts for a specific class.

        Args:
            db: Database session
            class_identifier: ID or name of the concept class
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of concepts with the specified class
        """
        query = self._query_with_names(db, locale=locale)

        filters = [Concept.retired.is_(False)]

        try:
            class_id = int(class_identifier)
            filters.append(Concept.class_id == class_id)
        except ValueError:
            query = query.join(
                ConceptClass,
                ConceptClass.concept_class_id == Concept.class_id,
            )
            filters.append(func.lower(ConceptClass.name) == class_identifier.lower())

        return query.filter(and_(*filters)).offset(skip).limit(limit).all()

    def get_concepts_by_creator(
        self,
        db: Session,
        creator: int,
        skip: int = 0,
        limit: int = 100,
        locale: Optional[str] = None,
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
            self._query_with_names(db, locale=locale)
            .filter(
                and_(
                    Concept.creator == creator,
                    Concept.retired.is_(False),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_concepts(
        self,
        db: Session,
        name: str,
        skip: int = 0,
        limit: int = 100,
        locale: Optional[str] = None,
        class_identifier: Optional[str] = None,
    ) -> List[Concept]:
        """
        Search concepts by short_name, description, or concept names.

        Args:
            db: Database session
            name: Search term for concept name or description
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of concepts matching the search criteria
        """
        search_term = f"%{name}%"
        query = (
            self._query_with_names(db, locale=locale)
            .outerjoin(ConceptName, ConceptName.concept_id == Concept.concept_id)
            .filter(
                and_(
                    Concept.retired.is_(False),
                    or_(
                        Concept.short_name.ilike(search_term),
                        Concept.description.ilike(search_term),
                        ConceptName.name.ilike(search_term),
                    ),
                )
            )
            .distinct()
        )
        if class_identifier:
            try:
                class_id = int(class_identifier)
                query = query.filter(Concept.class_id == class_id)
            except ValueError:
                query = query.join(
                    ConceptClass,
                    ConceptClass.concept_class_id == Concept.class_id,
                ).filter(func.lower(ConceptClass.name) == class_identifier.lower())
        if locale:
            query = query.filter(ConceptName.locale == locale)

        return query.offset(skip).limit(limit).all()

    def search_concepts_by_name(
        self,
        db: Session,
        name: str,
        skip: int = 0,
        limit: int = 100,
        locale: Optional[str] = None,
        class_identifier: Optional[str] = None,
    ) -> List[Concept]:
        """
        Compatibility method for the previous API; forwards to search_concepts.
        """
        return self.search_concepts(
            db,
            name,
            skip,
            limit,
            locale,
            class_identifier,
        )

    def get_active_concepts(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        locale: Optional[str] = None,
    ) -> List[Concept]:
        """
        Get only active (non-retired) concepts.
        """
        return (
            self._query_with_names(db, locale=locale)
            .filter(Concept.retired.is_(False))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_retired_concepts(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        locale: Optional[str] = None,
    ) -> List[Concept]:
        """
        Get only retired concepts.
        """
        return (
            self._query_with_names(db, locale=locale)
            .filter(Concept.retired.is_(True))
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
