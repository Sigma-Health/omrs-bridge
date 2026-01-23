import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from .base import BaseCRUD
from app.models import Drug
from app.config import settings


logger = logging.getLogger(__name__)


class DrugsCRUD(BaseCRUD[Drug]):
    """
    CRUD operations for Drug entities.

    Provides drug-specific database operations including search,
    filtering by concept, and lifecycle management (retire/unretire).
    """

    def __init__(self):
        """Initialize with the Drug model."""
        super().__init__(Drug)

    def _set_default_values(self, obj_data: dict) -> None:
        """Set drug-specific default values."""
        obj_data.setdefault("retired", False)
        obj_data.setdefault("combination", False)
        obj_data.setdefault("creator", settings.default_creator_id)

    def _set_audit_fields(self, db_obj: Drug, update_data: dict) -> None:
        """Set drug-specific audit fields."""
        changed_by = update_data.get("changed_by") or update_data.get("retired_by")
        if changed_by is not None:
            db_obj.changed_by = changed_by
        db_obj.date_changed = datetime.utcnow()

    def get_by_name(self, db: Session, name: str) -> Optional[Drug]:
        """
        Get a drug by exact name.

        Args:
            db: Database session
            name: Name of the drug

        Returns:
            The drug if found, None otherwise
        """
        return db.query(Drug).filter(Drug.name == name).first()

    def search_drugs(
        self, db: Session, name: str, skip: int = 0, limit: int = 100
    ) -> List[Drug]:
        """
        Search for drugs by name.

        Args:
            db: Database session
            name: Search term for the drug name
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of matching drugs
        """
        like_pattern = f"%{name}%"
        return (
            db.query(Drug)
            .filter(
                and_(
                    Drug.retired == False,  # noqa: E712
                    Drug.name.ilike(like_pattern),
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_drugs(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[Drug]:
        """
        Get only active (non-retired) drugs.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active drugs
        """
        return (
            db.query(Drug)
            .filter(Drug.retired == False)  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_retired_drugs(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[Drug]:
        """
        Get only retired drugs.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of retired drugs
        """
        return (
            db.query(Drug)
            .filter(Drug.retired == True)  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_drugs_by_concept(
        self, db: Session, concept_id: int, skip: int = 0, limit: int = 100
    ) -> List[Drug]:
        """
        Get drugs associated with a specific concept.

        Args:
            db: Database session
            concept_id: ID of the concept
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of drugs for the specified concept
        """
        return (
            db.query(Drug)
            .filter(
                and_(
                    Drug.concept_id == concept_id,
                    Drug.retired == False,  # noqa: E712
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_drugs_by_creator(
        self, db: Session, creator: int, skip: int = 0, limit: int = 100
    ) -> List[Drug]:
        """
        Get drugs created by a specific user.

        Args:
            db: Database session
            creator: ID of the user who created the drugs
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of drugs created by the specified user
        """
        return (
            db.query(Drug)
            .filter(
                and_(
                    Drug.creator == creator,
                    Drug.retired == False,  # noqa: E712
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def retire_drug(
        self, db: Session, drug_id: int, retired_by: int, reason: Optional[str] = None
    ) -> Optional[Drug]:
        """
        Retire a drug by ID.

        Args:
            db: Database session
            drug_id: ID of the drug to retire
            retired_by: ID of the user retiring the drug
            reason: Optional reason for retirement

        Returns:
            The updated drug if found, None otherwise
        """
        drug = self.get(db, drug_id)
        if not drug:
            return None

        drug.retired = True
        drug.retired_by = retired_by
        drug.date_retired = datetime.utcnow()
        drug.retire_reason = reason
        drug.changed_by = retired_by
        drug.date_changed = datetime.utcnow()

        try:
            db.commit()
            db.refresh(drug)
            return drug
        except Exception as exc:
            logger.error("Failed to retire drug %s: %s", drug_id, exc)
            db.rollback()
            raise

    def retire_drug_by_uuid(
        self, db: Session, uuid: str, retired_by: int, reason: Optional[str] = None
    ) -> Optional[Drug]:
        """
        Retire a drug by UUID.

        Args:
            db: Database session
            uuid: UUID of the drug to retire
            retired_by: ID of the user retiring the drug
            reason: Optional reason for retirement

        Returns:
            The updated drug if found, None otherwise
        """
        drug = self.get_by_uuid(db, uuid)
        if not drug:
            return None

        return self.retire_drug(db, drug.drug_id, retired_by, reason)

    def unretire_drug(
        self, db: Session, drug_id: int, unretired_by: Optional[int] = None
    ) -> Optional[Drug]:
        """
        Unretire a drug by ID.

        Args:
            db: Database session
            drug_id: ID of the drug to unretire
            unretired_by: ID of the user unretiring the drug

        Returns:
            The updated drug if found, None otherwise
        """
        drug = self.get(db, drug_id)
        if not drug:
            return None

        drug.retired = False
        drug.retired_by = None
        drug.date_retired = None
        drug.retire_reason = None
        if unretired_by is not None:
            drug.changed_by = unretired_by
        drug.date_changed = datetime.utcnow()

        try:
            db.commit()
            db.refresh(drug)
            return drug
        except Exception as exc:
            logger.error("Failed to unretire drug %s: %s", drug_id, exc)
            db.rollback()
            raise

    def unretire_drug_by_uuid(
        self, db: Session, uuid: str, unretired_by: Optional[int] = None
    ) -> Optional[Drug]:
        """
        Unretire a drug by UUID.

        Args:
            db: Database session
            uuid: UUID of the drug to unretire
            unretired_by: ID of the user unretiring the drug

        Returns:
            The updated drug if found, None otherwise
        """
        drug = self.get_by_uuid(db, uuid)
        if not drug:
            return None

        return self.unretire_drug(db, drug.drug_id, unretired_by)
