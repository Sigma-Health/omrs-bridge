"""
Visit-specific CRUD operations.
Extends BaseCRUD with visit-specific functionality.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from .base import BaseCRUD
from app.models import Visit


class VisitsCRUD(BaseCRUD[Visit]):
    """
    CRUD operations for Visit model.

    Provides visit-specific database operations including:
    - Basic CRUD operations (inherited from BaseCRUD)
    - Visit-specific queries (by patient, visit type, date range, etc.)
    - Visit status management (active, completed, voided)
    """

    def __init__(self):
        super().__init__(Visit)

    def get_by_patient(
        self, db: Session, patient_id: int, skip: int = 0, limit: int = 100
    ) -> List[Visit]:
        """
        Get all visits for a specific patient.

        Args:
            db: Database session
            patient_id: Patient ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of visits for the patient
        """
        return (
            db.query(self.model)
            .filter(self.model.patient_id == patient_id)
            .order_by(self.model.date_started.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_visits(
        self,
        db: Session,
        patient_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Visit]:
        """
        Get active visits (not voided and not stopped).

        Args:
            db: Database session
            patient_id: Optional patient ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active visits
        """
        query = db.query(self.model).filter(
            and_(self.model.voided == False, self.model.date_stopped.is_(None))
        )

        if patient_id:
            query = query.filter(self.model.patient_id == patient_id)

        return (
            query.order_by(self.model.date_started.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_completed_visits(
        self,
        db: Session,
        patient_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Visit]:
        """
        Get completed visits (not voided and with date_stopped).

        Args:
            db: Database session
            patient_id: Optional patient ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of completed visits
        """
        query = db.query(self.model).filter(
            and_(self.model.voided == False, self.model.date_stopped.isnot(None))
        )

        if patient_id:
            query = query.filter(self.model.patient_id == patient_id)

        return (
            query.order_by(self.model.date_stopped.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_voided_visits(
        self,
        db: Session,
        patient_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Visit]:
        """
        Get voided visits.

        Args:
            db: Database session
            patient_id: Optional patient ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of voided visits
        """
        query = db.query(self.model).filter(self.model.voided == True)

        if patient_id:
            query = query.filter(self.model.patient_id == patient_id)

        return (
            query.order_by(self.model.date_voided.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_visit_type(
        self, db: Session, visit_type_id: int, skip: int = 0, limit: int = 100
    ) -> List[Visit]:
        """
        Get visits by visit type.

        Args:
            db: Database session
            visit_type_id: Visit type ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of visits of the specified type
        """
        return (
            db.query(self.model)
            .filter(self.model.visit_type_id == visit_type_id)
            .order_by(self.model.date_started.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_location(
        self, db: Session, location_id: int, skip: int = 0, limit: int = 100
    ) -> List[Visit]:
        """
        Get visits by location.

        Args:
            db: Database session
            location_id: Location ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of visits at the specified location
        """
        return (
            db.query(self.model)
            .filter(self.model.location_id == location_id)
            .order_by(self.model.date_started.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_date_range(
        self,
        db: Session,
        start_date: str,
        end_date: str,
        patient_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Visit]:
        """
        Get visits within a date range.

        Args:
            db: Database session
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
            patient_id: Optional patient ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of visits within the date range
        """
        query = db.query(self.model).filter(
            and_(
                self.model.date_started >= start_date,
                self.model.date_started <= end_date,
            )
        )

        if patient_id:
            query = query.filter(self.model.patient_id == patient_id)

        return (
            query.order_by(self.model.date_started.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_visits_with_order_type(
        self,
        db: Session,
        order_type_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        patient_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Visit]:
        """
        Get visits that have orders of a particular order type.

        Args:
            db: Database session
            order_type_id: Order type ID to filter by
            start_date: Optional start date (YYYY-MM-DD format)
            end_date: Optional end date (YYYY-MM-DD format)
            patient_id: Optional patient ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of visits that have orders of the specified type
        """
        from app.models import Order, Encounter

        # Join visits with encounters and orders to find visits that have orders of the specified type
        # Relationship: Visit -> Encounter -> Order
        query = (
            db.query(self.model)
            .join(Encounter, self.model.visit_id == Encounter.visit_id)
            .join(Order, Encounter.encounter_id == Order.encounter_id)
            .filter(Order.order_type_id == order_type_id)
        )

        # Apply date range filter if provided
        if start_date and end_date:
            query = query.filter(
                and_(
                    self.model.date_started >= start_date,
                    self.model.date_started <= end_date,
                )
            )
        elif start_date:
            query = query.filter(self.model.date_started >= start_date)
        elif end_date:
            query = query.filter(self.model.date_started <= end_date)

        # Apply patient filter if provided
        if patient_id:
            query = query.filter(self.model.patient_id == patient_id)

        return (
            query.order_by(self.model.date_started.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_visits_with_order_type_and_patient_info(
        self,
        db: Session,
        order_type_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        patient_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get visits that have orders of a particular order type with enriched patient information.
        Uses joins to avoid N+1 queries for optimal performance.

        Args:
            db: Database session
            order_type_id: Order type ID to filter by
            start_date: Optional start date (YYYY-MM-DD format)
            end_date: Optional end date (YYYY-MM-DD format)
            patient_id: Optional patient ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of visits with enriched patient information
        """
        from app.models import Order, Encounter, Person, PersonName
        from sqlalchemy.orm import aliased

        # Create aliases for Person and PersonName tables
        PatientPerson = aliased(Person)
        PatientPersonName = aliased(PersonName)

        # Use a single query with joins to get all data efficiently
        query = (
            db.query(
                self.model,
                # Patient information
                PatientPerson.person_id.label("patient_person_id"),
                PatientPerson.uuid.label("patient_uuid"),
                PatientPerson.gender.label("patient_gender"),
                PatientPerson.birthdate.label("patient_birthdate"),
                # Patient name
                PatientPersonName.given_name.label("patient_given_name"),
                PatientPersonName.family_name.label("patient_family_name"),
                PatientPersonName.prefix.label("patient_prefix"),
                PatientPersonName.middle_name.label("patient_middle_name"),
                PatientPersonName.family_name2.label("patient_family_name2"),
                PatientPersonName.family_name_suffix.label(
                    "patient_family_name_suffix"
                ),
            )
            .join(Encounter, self.model.visit_id == Encounter.visit_id)
            .join(Order, Encounter.encounter_id == Order.encounter_id)
            # Join for patient information
            .outerjoin(
                PatientPerson,
                and_(
                    PatientPerson.person_id == self.model.patient_id,
                    PatientPerson.voided == False,  # noqa: E712
                ),
            )
            .outerjoin(
                PatientPersonName,
                and_(
                    PatientPersonName.person_id == self.model.patient_id,
                    PatientPersonName.preferred == True,  # noqa: E712
                    PatientPersonName.voided == False,  # noqa: E712
                ),
            )
            .filter(Order.order_type_id == order_type_id)
        )

        # Apply date range filter if provided
        if start_date and end_date:
            query = query.filter(
                and_(
                    self.model.date_started >= start_date,
                    self.model.date_started <= end_date,
                )
            )
        elif start_date:
            query = query.filter(self.model.date_started >= start_date)
        elif end_date:
            query = query.filter(self.model.date_started <= end_date)

        # Apply patient filter if provided
        if patient_id:
            query = query.filter(self.model.patient_id == patient_id)

        results = (
            query.order_by(self.model.date_started.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        # Transform results into enriched visit dictionaries
        enriched_visits = []
        for row in results:
            visit = row[0]  # The Visit object is first in the tuple

            # Build patient name
            patient_name_parts = []
            if row.patient_prefix:
                patient_name_parts.append(row.patient_prefix)
            if row.patient_given_name:
                patient_name_parts.append(row.patient_given_name)
            if row.patient_middle_name:
                patient_name_parts.append(row.patient_middle_name)
            if row.patient_family_name:
                patient_name_parts.append(row.patient_family_name)
            if row.patient_family_name2:
                patient_name_parts.append(row.patient_family_name2)
            if row.patient_family_name_suffix:
                patient_name_parts.append(row.patient_family_name_suffix)
            patient_name = " ".join(patient_name_parts) if patient_name_parts else None

            # Create enriched visit dictionary
            visit_dict = {
                "visit_id": visit.visit_id,
                "patient_id": visit.patient_id,
                "visit_type_id": visit.visit_type_id,
                "date_started": visit.date_started,
                "date_stopped": visit.date_stopped,
                "indication_concept_id": visit.indication_concept_id,
                "location_id": visit.location_id,
                "creator": visit.creator,
                "date_created": visit.date_created,
                "changed_by": visit.changed_by,
                "date_changed": visit.date_changed,
                "voided": visit.voided,
                "voided_by": visit.voided_by,
                "date_voided": visit.date_voided,
                "void_reason": visit.void_reason,
                "uuid": visit.uuid,
                # Enriched patient information
                "patient_info": {
                    "person_id": row.patient_person_id,
                    "uuid": row.patient_uuid,
                    "name": patient_name,
                    "gender": row.patient_gender,
                    "birthdate": row.patient_birthdate,
                }
                if row.patient_person_id
                else None,
            }

            enriched_visits.append(visit_dict)

        return enriched_visits

    def stop_visit(
        self,
        db: Session,
        visit_id: int,
        stopped_by: int,
        date_stopped: Optional[str] = None,
    ) -> Optional[Visit]:
        """
        Stop a visit by setting the date_stopped field.

        Args:
            db: Database session
            visit_id: Visit ID
            stopped_by: User ID who stopped the visit
            date_stopped: Optional date when visit was stopped (defaults to now)

        Returns:
            Updated visit object if found, None otherwise

        Raises:
            Exception: If database operation fails
        """
        visit = self.get(db, visit_id)
        if not visit:
            return None

        from datetime import datetime

        visit.date_stopped = (
            datetime.fromisoformat(date_stopped) if date_stopped else datetime.utcnow()
        )
        visit.changed_by = stopped_by
        visit.date_changed = datetime.utcnow()

        try:
            db.commit()
            db.refresh(visit)
            return visit
        except Exception as e:
            db.rollback()
            raise e

    def void_visit(
        self,
        db: Session,
        visit_id: int,
        voided_by: int,
        void_reason: Optional[str] = None,
    ) -> Optional[Visit]:
        """
        Void a visit.

        Args:
            db: Database session
            visit_id: Visit ID
            voided_by: User ID who voided the visit
            void_reason: Optional reason for voiding

        Returns:
            Updated visit object if found, None otherwise

        Raises:
            Exception: If database operation fails
        """
        visit = self.get(db, visit_id)
        if not visit:
            return None

        from datetime import datetime

        visit.voided = True
        visit.voided_by = voided_by
        visit.date_voided = datetime.utcnow()
        visit.void_reason = void_reason
        visit.changed_by = voided_by
        visit.date_changed = datetime.utcnow()

        try:
            db.commit()
            db.refresh(visit)
            return visit
        except Exception as e:
            db.rollback()
            raise e

    def unvoid_visit(
        self, db: Session, visit_id: int, unvoided_by: int
    ) -> Optional[Visit]:
        """
        Unvoid a visit.

        Args:
            db: Database session
            visit_id: Visit ID
            unvoided_by: User ID who unvoided the visit

        Returns:
            Updated visit object if found, None otherwise

        Raises:
            Exception: If database operation fails
        """
        visit = self.get(db, visit_id)
        if not visit:
            return None

        from datetime import datetime

        visit.voided = False
        visit.voided_by = None
        visit.date_voided = None
        visit.void_reason = None
        visit.changed_by = unvoided_by
        visit.date_changed = datetime.utcnow()

        try:
            db.commit()
            db.refresh(visit)
            return visit
        except Exception as e:
            db.rollback()
            raise e

    def _set_default_values(self, obj_data: dict) -> None:
        """
        Set default values for new visit objects.

        Args:
            obj_data: Dictionary containing visit data
        """
        from datetime import datetime

        # Set default date_started if not provided
        if not obj_data.get("date_started"):
            obj_data["date_started"] = datetime.utcnow()

    def _set_audit_fields(self, db_obj: Visit, update_data: dict) -> None:
        """
        Set audit fields when updating visit objects.

        Args:
            db_obj: Visit object being updated
            update_data: Data being used for the update
        """
        from datetime import datetime

        # Set changed_by and date_changed if not already set
        if not hasattr(db_obj, "changed_by") or db_obj.changed_by is None:
            # Try to get from update_data, otherwise use creator
            db_obj.changed_by = update_data.get("changed_by", db_obj.creator)

        db_obj.date_changed = datetime.utcnow()
