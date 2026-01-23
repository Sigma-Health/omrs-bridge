import logging

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, aliased
from sqlalchemy import and_
from sqlalchemy.sql import func
from datetime import datetime

from .base import BaseCRUD
from app.models import Order

# Import SQL utilities
from app.sql.sql_utils import (
    execute_enriched_orders_query,
    process_raw_query_results,
    process_expanded_order_results,
)
from app.sql.orders_sql import (
    get_orders_with_enrichment_sql,
    get_single_order_with_expansion_sql,
)


logger = logging.getLogger(__name__)


class OrdersCRUD(BaseCRUD[Order]):
    """
    CRUD operations for Order entities.

    Provides order-specific database operations including filtering
    by patient, urgency, orderer, and other criteria.
    """

    def __init__(self):
        """Initialize with the Order model."""
        super().__init__(Order)

    def _set_default_values(self, obj_data: dict) -> None:
        """Set order-specific default values."""
        obj_data["voided"] = False
        obj_data["urgency"] = obj_data.get("urgency", "ROUTINE")
        obj_data["order_action"] = obj_data.get("order_action", "NEW")

    def _set_audit_fields(self, db_obj: Order, update_data: dict) -> None:
        """Set order-specific audit fields."""
        # Orders don't have specific audit fields like changed_by/date_changed
        # They use the standard voided/voided_by/date_voided pattern
        pass

    # Entity-specific methods
    def get_by_order_number(self, db: Session, order_number: str) -> Optional[Order]:
        """
        Get order by order number.

        Args:
            db: Database session
            order_number: Order number to search for

        Returns:
            The order if found, None otherwise
        """
        return db.query(Order).filter(Order.order_number == order_number).first()

    def get_orders_by_patient(
        self, db: Session, patient_id: int, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """
        Get orders for a specific patient.

        Args:
            db: Database session
            patient_id: ID of the patient
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of orders for the specified patient
        """
        return (
            db.query(Order)
            .filter(and_(Order.patient_id == patient_id, Order.voided == False))  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_orders_by_urgency(
        self, db: Session, urgency: str, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """
        Get orders by urgency level.

        Args:
            db: Database session
            urgency: Urgency level ('ROUTINE', 'STAT', 'ASAP', etc.)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of orders with the specified urgency
        """
        return (
            db.query(Order)
            .filter(and_(Order.urgency == urgency, Order.voided == False))  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_orders_by_orderer(
        self, db: Session, orderer: int, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """
        Get orders by orderer (provider).

        Args:
            db: Database session
            orderer: ID of the provider who ordered
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of orders by the specified orderer
        """
        return (
            db.query(Order)
            .filter(and_(Order.orderer == orderer, Order.voided == False))  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_orders_by_encounter(
        self, db: Session, encounter_id: int, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """
        Get orders for a specific encounter.

        Args:
            db: Database session
            encounter_id: ID of the encounter
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of orders for the specified encounter
        """
        return (
            db.query(Order)
            .filter(and_(Order.encounter_id == encounter_id, Order.voided == False))  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_orders_by_concept(
        self, db: Session, concept_id: int, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """
        Get orders for a specific concept.

        Args:
            db: Database session
            concept_id: ID of the concept
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of orders for the specified concept
        """
        return (
            db.query(Order)
            .filter(and_(Order.concept_id == concept_id, Order.voided == False))  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_orders_by_type(
        self, db: Session, order_type_id: int, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """
        Get orders by order type.

        Args:
            db: Database session
            order_type_id: ID of the order type
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of orders with the specified type
        """
        return (
            db.query(Order)
            .filter(and_(Order.order_type_id == order_type_id, Order.voided == False))  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_orders(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """
        Get only active (non-voided) orders.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of active orders
        """
        return (
            db.query(Order)
            .filter(Order.voided == False)  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_voided_orders(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """
        Get only voided orders.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of voided orders
        """
        return db.query(Order).filter(Order.voided).offset(skip).limit(limit).all()

    def void_order(
        self, db: Session, order_id: int, voided_by: int, reason: str = None
    ) -> Optional[Order]:
        """
        Void an order.

        Args:
            db: Database session
            order_id: ID of the order to void
            voided_by: ID of the user voiding the order
            reason: Optional reason for voiding

        Returns:
            The voided order if found, None otherwise
        """
        db_order = self.get(db, order_id)
        if not db_order:
            return None

        db_order.voided = True
        db_order.voided_by = voided_by
        db_order.date_voided = datetime.utcnow()
        if reason:
            db_order.void_reason = reason

        try:
            db.commit()
            db.refresh(db_order)
            return db_order
        except Exception as e:
            db.rollback()
            raise e

    def unvoid_order(
        self, db: Session, order_id: int, unvoided_by: int
    ) -> Optional[Order]:
        """
        Unvoid an order.

        Args:
            db: Database session
            order_id: ID of the order to unvoid
            unvoided_by: ID of the user unvoiding the order

        Returns:
            The unvoided order if found, None otherwise
        """
        db_order = self.get(db, order_id)
        if not db_order:
            return None

        db_order.voided = False
        db_order.voided_by = None
        db_order.date_voided = None
        db_order.void_reason = None

        try:
            db.commit()
            db.refresh(db_order)
            return db_order
        except Exception as e:
            db.rollback()
            raise e

    def get_orders_by_status(
        self, db: Session, status: str, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """
        Get orders by fulfiller status.

        Args:
            db: Database session
            status: Fulfiller status to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of orders with the specified fulfiller status
        """
        return (
            db.query(Order)
            .filter(and_(Order.fulfiller_status == status, Order.voided == False))  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_orders_by_action(
        self, db: Session, action: str, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """
        Get orders by order action.

        Args:
            db: Database session
            action: Order action to filter by ('NEW', 'REVISE', 'DISCONTINUE', etc.)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of orders with the specified action
        """
        return (
            db.query(Order)
            .filter(and_(Order.order_action == action, Order.voided == False))  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_orders_by_type_and_visit_id(
        self,
        db: Session,
        order_type_id: int,
        visit_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Order]:
        """
        Get orders by order type and visit ID.

        Args:
            db: Database session
            order_type_id: Order type ID to filter by
            visit_id: Visit ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of orders with the specified order type and visit
        """
        from app.models import Encounter, Visit

        return (
            db.query(Order)
            .join(Encounter, Order.encounter_id == Encounter.encounter_id)
            .join(Visit, Encounter.visit_id == Visit.visit_id)
            .filter(
                and_(
                    Order.order_type_id == order_type_id,
                    Visit.visit_id == visit_id,
                    Order.voided == False,  # noqa: E712
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_orders_by_type_and_visit_uuid(
        self,
        db: Session,
        order_type_id: int,
        visit_uuid: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get orders by order type and visit UUID.

        Args:
            db: Database session
            order_type_id: Order type ID to filter by
            visit_uuid: Visit UUID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of orders with concept details
        """
        from app.models import (
            Encounter,
            Visit,
            Person,
            PersonName,
            Provider,
            Concept,
            ConceptName,
        )

        # Create aliases for Person and PersonName tables to join them multiple times
        OrdererPerson = aliased(Person)
        OrdererPersonName = aliased(PersonName)
        PatientPerson = aliased(Person)
        PatientPersonName = aliased(PersonName)
        # Create alias for SHORT concept name
        ShortConceptName = aliased(ConceptName)

        query = (
            db.query(
                Order,
                # Provider information
                Provider.provider_id.label("provider_id"),
                Provider.name.label("provider_name"),
                Provider.identifier.label("provider_identifier"),
                Provider.uuid.label("provider_uuid"),
                # Orderer information
                OrdererPerson.person_id.label("orderer_person_id"),
                OrdererPerson.uuid.label("orderer_uuid"),
                OrdererPerson.gender.label("orderer_gender"),
                OrdererPerson.birthdate.label("orderer_birthdate"),
                # Orderer name
                OrdererPersonName.given_name.label("orderer_given_name"),
                OrdererPersonName.family_name.label("orderer_family_name"),
                OrdererPersonName.prefix.label("orderer_prefix"),
                OrdererPersonName.middle_name.label("orderer_middle_name"),
                OrdererPersonName.family_name2.label("orderer_family_name2"),
                OrdererPersonName.family_name_suffix.label(
                    "orderer_family_name_suffix"
                ),
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
                # Concept information
                Concept.concept_id.label("concept_id"),
                Concept.uuid.label("concept_uuid"),
                func.coalesce(ShortConceptName.name, Concept.short_name).label(
                    "concept_short_name"
                ),
                Concept.description.label("concept_description"),
                Concept.is_set.label("concept_is_set"),
                # Concept name information
                ConceptName.concept_name_id.label("concept_name_id"),
                ConceptName.name.label("concept_name"),
                ConceptName.locale.label("concept_name_locale"),
                ConceptName.locale_preferred.label("concept_name_locale_preferred"),
                ConceptName.concept_name_type.label("concept_name_type"),
            )
            .join(Encounter, Order.encounter_id == Encounter.encounter_id)
            .join(Visit, Encounter.visit_id == Visit.visit_id)
            # Join for orderer information through provider table
            .outerjoin(
                Provider,
                and_(
                    Provider.provider_id == Order.orderer,
                    Provider.retired == False,  # noqa: E712
                ),
            )
            .outerjoin(
                OrdererPerson,
                and_(
                    OrdererPerson.person_id == Provider.person_id,
                    OrdererPerson.voided == False,  # noqa: E712
                ),
            )
            .outerjoin(
                OrdererPersonName,
                and_(
                    OrdererPersonName.person_id == Order.orderer,
                    OrdererPersonName.preferred == True,  # noqa: E712
                    OrdererPersonName.voided == False,  # noqa: E712
                ),
            )
            # Join for patient information
            .outerjoin(
                PatientPerson,
                and_(
                    PatientPerson.person_id == Order.patient_id,
                    PatientPerson.voided == False,  # noqa: E712
                ),
            )
            .outerjoin(
                PatientPersonName,
                and_(
                    PatientPersonName.person_id == Order.patient_id,
                    PatientPersonName.preferred == True,  # noqa: E712
                    PatientPersonName.voided == False,  # noqa: E712
                ),
            )
            # Join for concept information
            .outerjoin(
                Concept,
                and_(
                    Concept.concept_id == Order.concept_id,
                    Concept.retired == False,  # noqa: E712
                ),
            )
            # Join for concept name information (English locale, FULLY_SPECIFIED type)
            .outerjoin(
                ConceptName,
                and_(
                    ConceptName.concept_id == Concept.concept_id,
                    ConceptName.locale == "en",  # Filter for English locale
                    ConceptName.concept_name_type
                    == "FULLY_SPECIFIED",  # Only FULLY_SPECIFIED names
                    ConceptName.voided == False,  # noqa: E712
                ),
            )
            # Join for SHORT concept name (to populate short_name field)
            .outerjoin(
                ShortConceptName,
                and_(
                    ShortConceptName.concept_id == Concept.concept_id,
                    ShortConceptName.locale == "en",
                    ShortConceptName.concept_name_type == "SHORT",
                    ShortConceptName.voided == False,  # noqa: E712
                ),
            )
            .filter(
                and_(
                    Order.order_type_id == order_type_id,
                    Visit.uuid == visit_uuid,
                    Order.voided == False,  # noqa: E712
                )
            )
            .offset(skip)
            .limit(limit)
        )

        results = query.all()

        # Transform results into enriched order dictionaries
        enriched_orders = []
        for row in results:
            order = row[0]  # The Order object is first in the tuple

            # Build orderer name - prefer person name, fallback to provider name
            orderer_name_parts = []
            if row.orderer_prefix:
                orderer_name_parts.append(row.orderer_prefix)
            if row.orderer_given_name:
                orderer_name_parts.append(row.orderer_given_name)
            if row.orderer_middle_name:
                orderer_name_parts.append(row.orderer_middle_name)
            if row.orderer_family_name:
                orderer_name_parts.append(row.orderer_family_name)
            if row.orderer_family_name2:
                orderer_name_parts.append(row.orderer_family_name2)
            if row.orderer_family_name_suffix:
                orderer_name_parts.append(row.orderer_family_name_suffix)

            # Use person name if available, otherwise use provider name
            if orderer_name_parts:
                orderer_name = " ".join(orderer_name_parts)
            elif row.provider_name:
                orderer_name = row.provider_name
            else:
                orderer_name = None

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

            # Create enriched order dictionary
            order_dict = {
                "order_id": order.order_id,
                "order_type_id": order.order_type_id,
                "concept_id": order.concept_id,
                "orderer": order.orderer,
                "encounter_id": order.encounter_id,
                "instructions": order.instructions,
                "date_activated": order.date_activated,
                "auto_expire_date": order.auto_expire_date,
                "date_stopped": order.date_stopped,
                "order_reason": order.order_reason,
                "order_reason_non_coded": order.order_reason_non_coded,
                "voided": order.voided,
                "voided_by": order.voided_by,
                "date_voided": order.date_voided,
                "void_reason": order.void_reason,
                "patient_id": order.patient_id,
                "accession_number": order.accession_number,
                "urgency": order.urgency,
                "order_number": order.order_number,
                "previous_order_id": order.previous_order_id,
                "order_action": order.order_action,
                "comment_to_fulfiller": order.comment_to_fulfiller,
                "care_setting": order.care_setting,
                "scheduled_date": order.scheduled_date,
                "order_group_id": order.order_group_id,
                "sort_weight": order.sort_weight,
                "fulfiller_comment": order.fulfiller_comment,
                "fulfiller_status": order.fulfiller_status,
                "form_namespace_and_path": order.form_namespace_and_path,
                "creator": order.creator,
                "date_created": order.date_created,
                "uuid": order.uuid,
                # Enriched orderer information
                "orderer_info": {
                    "provider_id": row.provider_id,
                    "provider_name": row.provider_name,
                    "provider_identifier": row.provider_identifier,
                    "provider_uuid": row.provider_uuid,
                    "person_id": row.orderer_person_id,
                    "person_uuid": row.orderer_uuid,
                    "name": orderer_name,
                    "gender": row.orderer_gender,
                    "birthdate": row.orderer_birthdate,
                }
                if row.provider_id
                else None,
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
                # Enriched concept information
                "concept_info": {
                    "concept_id": row.concept_id,
                    "uuid": row.concept_uuid,
                    "short_name": row.concept_short_name,
                    "description": row.concept_description,
                    "is_set": row.concept_is_set,
                    "name": row.concept_name,
                    "name_locale": row.concept_name_locale,
                    "name_locale_preferred": row.concept_name_locale_preferred,
                    "name_type": row.concept_name_type,
                }
                if row.concept_id
                else None,
            }

            enriched_orders.append(order_dict)

        return enriched_orders

    def get_orders_by_visit_id(
        self, db: Session, visit_id: int, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """
        Get all orders for a visit by visit ID.

        Args:
            db: Database session
            visit_id: Visit ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of all orders for the specified visit
        """
        from app.models import Encounter, Visit

        return (
            db.query(Order)
            .join(Encounter, Order.encounter_id == Encounter.encounter_id)
            .join(Visit, Encounter.visit_id == Visit.visit_id)
            .filter(and_(Visit.visit_id == visit_id, Order.voided == False))  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_orders_by_visit_uuid(
        self, db: Session, visit_uuid: str, skip: int = 0, limit: int = 100
    ) -> List[Order]:
        """
        Get all orders for a visit by visit UUID.

        Args:
            db: Database session
            visit_uuid: Visit UUID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of all orders for the specified visit
        """
        from app.models import Encounter, Visit

        try:
            # First, let's check if the visit exists
            visit = db.query(Visit).filter(Visit.uuid == visit_uuid).first()
            if not visit:
                return []

            # Check encounters for this visit
            encounters = (
                db.query(Encounter).filter(Encounter.visit_id == visit.visit_id).all()
            )

            # Now check orders for these encounters
            encounter_ids = [e.encounter_id for e in encounters]
            if not encounter_ids:
                return []

            # Now run the actual query
            # Note: Using Order.voided == False instead of not Order.voided
            # because SQLAlchemy translates 'not Order.voided' to 'false = 1' in some DB configs
            query = (
                db.query(Order)
                .join(Encounter, Order.encounter_id == Encounter.encounter_id)
                .join(Visit, Encounter.visit_id == Visit.visit_id)
                .filter(and_(Visit.uuid == visit_uuid, Order.voided == False))  # noqa: E712
            )

            result = query.offset(skip).limit(limit).all()
            return result

        except Exception as e:
            logger.error(f"Error getting orders for visit UUID {visit_uuid}: {str(e)}")
            raise

    def _determine_order_status(self, raw_data: Dict[str, Any]) -> str:
        """
        Determine order status based on order data.

        Args:
            raw_data: Raw order data

        Returns:
            Status string (ACTIVE, STOPPED, EXPIRED, etc.)
        """
        if raw_data.get("voided"):
            return "VOIDED"
        elif raw_data.get("date_stopped"):
            return "STOPPED"
        elif (
            raw_data.get("auto_expire_date")
            and raw_data.get("auto_expire_date") < datetime.now()
        ):
            return "EXPIRED"
        else:
            return "ACTIVE"

    def get_orders_by_type_and_visit_uuidx(
        self,
        db: Session,
        order_type_id: int,
        visit_uuid: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get orders by order type and visit UUID using raw SQL query.
        For drug orders (order_type_id=2), includes prescription and medication details.
        """
        from app.sql.orders_sql import get_drug_orders_with_enrichment_sql

        # Use drug-specific query for order_type_id=2 (drug/prescription orders)
        if order_type_id == 2:
            raw_sql = get_drug_orders_with_enrichment_sql()
        else:
            raw_sql = get_orders_with_enrichment_sql()

        # Define WHERE conditions
        where_conditions = {
            "order_type_id": order_type_id,
            "visit_uuid": visit_uuid,
            "voided": False,
        }

        # Execute raw SQL query
        result = execute_enriched_orders_query(
            db,
            raw_sql,
            where_conditions,
            skip,
            limit,
        )

        # Process results with drug order support
        if order_type_id == 2:
            from app.sql.sql_utils import process_drug_order_query_results

            return process_drug_order_query_results(result)
        else:
            return process_raw_query_results(result)

    # Old method definitions removed - now using app/sql modules
    # All SQL utilities moved to app/sql/sql_utils.py
    # All SQL queries moved to app/sql/orders_sql.py

    def get_orders_by_patient_id(
        self,
        db: Session,
        patient_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get orders by patient ID using reusable SQL components.
        """
        # Get the reusable SQL query
        raw_sql = get_orders_with_enrichment_sql()

        # Define WHERE conditions
        where_conditions = {"patient_id": patient_id, "voided": False}

        # Execute raw SQL query
        result = execute_enriched_orders_query(
            db, raw_sql, where_conditions, skip, limit
        )

        return process_raw_query_results(result)

    def get_orders_by_encounter_id(
        self,
        db: Session,
        encounter_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get orders by encounter ID using reusable SQL components.
        """
        # Get the reusable SQL query
        raw_sql = get_orders_with_enrichment_sql()

        # Define WHERE conditions
        where_conditions = {"encounter_id": encounter_id, "voided": False}

        # Execute raw SQL query
        result = execute_enriched_orders_query(
            db, raw_sql, where_conditions, skip, limit
        )

        return process_raw_query_results(result)

    def get_orders_by_date_range(
        self,
        db: Session,
        date_from: str,
        date_to: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get orders by date range using reusable SQL components.
        """
        # Get the reusable SQL query
        raw_sql = get_orders_with_enrichment_sql()

        # Define WHERE conditions
        where_conditions = {
            "date_activated_from": date_from,
            "date_activated_to": date_to,
            "voided": False,
        }

        # Execute raw SQL query
        result = execute_enriched_orders_query(
            db, raw_sql, where_conditions, skip, limit
        )

        return process_raw_query_results(result)

    def get_orders_by_custom_conditions(
        self,
        db: Session,
        conditions: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get orders by custom conditions using reusable SQL components.

        Args:
            db: Database session
            conditions: Dictionary of WHERE conditions (e.g., {"order_type_id": 4, "patient_id": 85})
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of enriched order dictionaries
        """
        # Get the reusable SQL query
        raw_sql = get_orders_with_enrichment_sql()

        # Add default voided condition if not provided
        if "voided" not in conditions:
            conditions["voided"] = False

        # Execute raw SQL query
        result = execute_enriched_orders_query(db, raw_sql, conditions, skip, limit)

        return process_raw_query_results(result)

    def get_single_order_with_expansion(
        self,
        db: Session,
        order_id: Optional[int] = None,
        order_uuid: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get a single order with expansion details.

        If the order's concept is_set=true (panel), includes set members (actual orders).
        If the order's concept is_set=false (regular), includes parent concept metadata.

        Args:
            db: Database session
            order_id: Order ID (optional)
            order_uuid: Order UUID (optional)

        Returns:
            Dictionary with order, set_members (if panel), and parent_concept (if regular)
        """
        if not order_id and not order_uuid:
            raise ValueError("Either order_id or order_uuid must be provided")

        logger.info(
            f"Getting order with expansion - order_id: {order_id}, order_uuid: {order_uuid}"
        )

        # Get the SQL query
        raw_sql = get_single_order_with_expansion_sql()

        # Define WHERE conditions
        where_conditions = {"voided": False}
        if order_id:
            where_conditions["order_id"] = order_id
        elif order_uuid:
            where_conditions["order_uuid"] = order_uuid

        logger.info(f"WHERE conditions: {where_conditions}")

        # First, let's check if the basic order exists
        from sqlalchemy import text

        if order_id:
            basic_query = text(
                "SELECT order_id, uuid, concept_id FROM orders WHERE order_id = :order_id AND voided = 0"
            )
            basic_result = db.execute(basic_query, {"order_id": order_id}).fetchone()
        elif order_uuid:
            basic_query = text(
                "SELECT order_id, uuid, concept_id FROM orders WHERE uuid = :order_uuid AND voided = 0"
            )
            basic_result = db.execute(
                basic_query, {"order_uuid": order_uuid}
            ).fetchone()

        if basic_result:
            logger.info(
                f"Basic order found: order_id={basic_result.order_id}, uuid={basic_result.uuid}, concept_id={basic_result.concept_id}"
            )
        else:
            logger.warning(
                "Basic order NOT found - this explains why expansion query returns no results"
            )
            return None

        # Execute query (no pagination for single order)
        result = execute_enriched_orders_query(db, raw_sql, where_conditions, 0, 1000)

        # Log raw result count
        rows = list(result)
        logger.info(f"Raw SQL result: {len(rows)} rows returned")

        if not rows:
            logger.warning(
                "Complex expansion query returned no rows - falling back to basic order + manual expansion"
            )
            # Fallback: get basic order and manually get expansion data
            return self._get_order_with_manual_expansion(db, basic_result)

        if rows:
            first_row = rows[0]
            logger.info(
                f"First row - order_id: {first_row.order_id}, concept_id: {first_row.concept_id}, is_set: {first_row.concept_is_set}"
            )
            logger.info(f"Set member concept_id: {first_row.set_member_concept_id}")
            logger.info(f"Parent concept_id: {first_row.parent_concept_id}")

            # Debug concept_set data
            self.debug_concept_set_data(db, first_row.concept_id)

        # Re-execute the query for processing (since we consumed it above)
        result_for_processing = execute_enriched_orders_query(
            db, raw_sql, where_conditions, 0, 1000
        )

        # Process results
        processed_result = process_expanded_order_results(result_for_processing)

        if processed_result:
            logger.info(
                f"Processed result - order_id: {processed_result['order']['order_id']}"
            )
            logger.info(
                f"Set members count: {len(processed_result['set_members']) if processed_result['set_members'] else 0}"
            )
            logger.info(
                f"Parent concept: {processed_result['parent_concept'] is not None}"
            )

        return processed_result

    def debug_concept_set_data(self, db: Session, concept_id: int):
        """
        Debug function to check concept_set table data for a given concept.
        """
        from sqlalchemy import text

        logger.info(f"Debugging concept_set data for concept_id: {concept_id}")

        # Check if concept is a panel (is_set=1)
        concept_query = text(
            "SELECT concept_id, uuid, short_name, is_set FROM concept WHERE concept_id = :concept_id"
        )
        concept_result = db.execute(
            concept_query, {"concept_id": concept_id}
        ).fetchone()

        if concept_result:
            logger.info(
                f"Concept: {concept_result.concept_id}, short_name: {concept_result.short_name}, is_set: {concept_result.is_set}"
            )

            if concept_result.is_set == 1:
                # Check concept_set table for this panel
                set_query = text("""
                    SELECT cs.concept_id, cs.concept_set, c.short_name as member_name 
                    FROM concept_set cs 
                    JOIN concept c ON cs.concept_id = c.concept_id 
                    WHERE cs.concept_set = :concept_id
                """)
                set_results = db.execute(
                    set_query, {"concept_id": concept_id}
                ).fetchall()

                logger.info(f"Found {len(set_results)} set members:")
                for row in set_results:
                    logger.info(
                        f"  Member concept_id: {row.concept_id}, name: {row.member_name}"
                    )

                # Check if there are orders for these member concepts
                if set_results:
                    member_concept_ids = [row.concept_id for row in set_results]
                    orders_query = text("""
                        SELECT o.order_id, o.concept_id, o.encounter_id, c.short_name as concept_name
                        FROM orders o 
                        JOIN concept c ON o.concept_id = c.concept_id
                        WHERE o.concept_id IN :member_concept_ids AND o.voided = 0
                    """)
                    orders_result = db.execute(
                        orders_query, {"member_concept_ids": tuple(member_concept_ids)}
                    ).fetchall()

                    logger.info(
                        f"Found {len(orders_result)} orders for member concepts:"
                    )
                    for row in orders_result:
                        logger.info(
                            f"  Order: {row.order_id}, concept: {row.concept_id} ({row.concept_name}), encounter: {row.encounter_id}"
                        )
            else:
                logger.info("Concept is not a panel (is_set=0)")
        else:
            logger.warning(f"Concept {concept_id} not found")

    def _get_order_with_manual_expansion(
        self, db: Session, basic_order
    ) -> Dict[str, Any]:
        """
        Fallback method to get order with manual expansion when complex query fails.
        """
        from sqlalchemy import text

        logger.info("Using manual expansion fallback")

        # Get the full order details using the simpler query
        order_query = text("""
            SELECT o.*, 
                   c.concept_id, c.uuid as concept_uuid, c.short_name as concept_short_name, 
                   c.description as concept_description, c.is_set as concept_is_set,
                   cn.name as concept_name
            FROM orders o
            LEFT JOIN concept c ON o.concept_id = c.concept_id AND c.retired = false
            LEFT JOIN concept_name cn ON cn.concept_id = c.concept_id 
                AND cn.locale = 'en' AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.voided = false
            WHERE o.order_id = :order_id AND o.voided = false
        """)

        order_result = db.execute(
            order_query, {"order_id": basic_order.order_id}
        ).fetchone()

        if not order_result:
            logger.error("Could not get order details even with simple query")
            return None

        # Build basic order dict
        order_dict = {
            "order_id": order_result.order_id,
            "order_type_id": order_result.order_type_id,
            "concept_id": order_result.concept_id,
            "orderer": order_result.orderer,
            "encounter_id": order_result.encounter_id,
            "instructions": order_result.instructions,
            "date_activated": order_result.date_activated,
            "auto_expire_date": order_result.auto_expire_date,
            "date_stopped": order_result.date_stopped,
            "order_reason": order_result.order_reason,
            "order_reason_non_coded": order_result.order_reason_non_coded,
            "creator": order_result.creator,
            "date_created": order_result.date_created,
            "voided": order_result.voided,
            "voided_by": order_result.voided_by,
            "date_voided": order_result.date_voided,
            "void_reason": order_result.void_reason,
            "patient_id": order_result.patient_id,
            "accession_number": order_result.accession_number,
            "uuid": order_result.uuid,
            "urgency": order_result.urgency,
            "order_number": order_result.order_number,
            "previous_order_id": order_result.previous_order_id,
            "order_action": order_result.order_action,
            "comment_to_fulfiller": order_result.comment_to_fulfiller,
            "care_setting": order_result.care_setting,
            "scheduled_date": order_result.scheduled_date,
            "order_group_id": order_result.order_group_id,
            "sort_weight": order_result.sort_weight,
            "fulfiller_comment": order_result.fulfiller_comment,
            "fulfiller_status": order_result.fulfiller_status,
            "form_namespace_and_path": order_result.form_namespace_and_path,
        }

        # Add concept info
        concept_info = {
            "concept_id": order_result.concept_id,
            "uuid": order_result.concept_uuid,
            "name": order_result.concept_name,
            "short_name": order_result.concept_short_name,
            "description": order_result.concept_description,
            "is_set": order_result.concept_is_set,
        }
        order_dict["concept_info"] = concept_info

        # Get set members if it's a panel
        set_members = []
        if order_result.concept_is_set == 1:
            logger.info("Getting set members manually")
            set_query = text("""
                SELECT cs.concept_id, c.uuid, c.short_name, c.description, c.is_set,
                       cn.name
                FROM concept_set cs
                JOIN concept c ON cs.concept_id = c.concept_id AND c.retired = false
                LEFT JOIN concept_name cn ON cn.concept_id = c.concept_id 
                    AND cn.locale = 'en' AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.voided = false
                WHERE cs.concept_set = :concept_id
            """)

            set_results = db.execute(
                set_query, {"concept_id": order_result.concept_id}
            ).fetchall()

            for row in set_results:
                set_member = {
                    "concept_id": row.concept_id,
                    "uuid": row.uuid,
                    "name": row.name,
                    "short_name": row.short_name,
                    "description": row.description,
                    "is_set": row.is_set,
                }
                set_members.append(set_member)

            logger.info(f"Found {len(set_members)} set members manually")

        return {
            "order": order_dict,
            "set_members": set_members if set_members else None,
            "parent_concept": None,  # TODO: implement if needed
        }


# Create instance
orders_crud = OrdersCRUD()

# Example usage of reusable components:
"""
# Example 1: Get orders by type and visit UUID
orders = orders_crud.get_orders_by_type_and_visit_uuidx(
    db=db,
    order_type_id=4,
    visit_uuid="a525f3e7-7077-425e-bc8b-ebe38ebfeff6",
    skip=0,
    limit=100
)

# Example 2: Get orders by patient ID
orders = orders_crud.get_orders_by_patient_id(
    db=db,
    patient_id=85,
    skip=0,
    limit=50
)

# Example 3: Get orders by encounter ID
orders = orders_crud.get_orders_by_encounter_id(
    db=db,
    encounter_id=147,
    skip=0,
    limit=100
)

# Example 4: Get orders by date range
orders = orders_crud.get_orders_by_date_range(
    db=db,
    date_from="2025-09-01",
    date_to="2025-09-30",
    skip=0,
    limit=200
)

# Example 5: Get orders by custom conditions
orders = orders_crud.get_orders_by_custom_conditions(
    db=db,
    conditions={
        "order_type_id": 4,
        "patient_id": 85,
        "orderer": 2
    },
    skip=0,
    limit=100
)

# Example 6: Direct usage of reusable components
sql_template = get_orders_with_enrichment_sql()
conditions = {"order_type_id": 4, "voided": False}
result = execute_enriched_orders_query(db, sql_template, conditions, 0, 100)
orders = process_raw_query_results(result)
"""
