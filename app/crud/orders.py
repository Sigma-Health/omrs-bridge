import logging

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from .base import BaseCRUD
from app.models import Order


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

    def get_orders_by_type_and_visit_uuidx(
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
        from app.models import Encounter, Visit, Person, PersonName, Provider, Concept
        from sqlalchemy.orm import aliased

        # Create aliases for Person and PersonName tables to join them multiple times
        OrdererPerson = aliased(Person)
        OrdererPersonName = aliased(PersonName)
        PatientPerson = aliased(Person)
        PatientPersonName = aliased(PersonName)

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
                    OrdererPersonName.person_id == Provider.person_id,
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
            }

            enriched_orders.append(order_dict)

        return enriched_orders

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
        from sqlalchemy.orm import aliased

        # Create aliases for Person and PersonName tables to join them multiple times
        OrdererPerson = aliased(Person)
        OrdererPersonName = aliased(PersonName)
        PatientPerson = aliased(Person)
        PatientPersonName = aliased(PersonName)

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
                Concept.short_name.label("concept_short_name"),
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

    def get_orders_by_type_and_visit_uuid_paginated(
        self,
        db: Session,
        order_type_id: int,
        visit_uuid: str,
        skip: int = 0,
        limit: int = 100,
    ) -> Dict[str, Any]:
        """
        Get orders by order type and visit UUID with pagination metadata.

        Args:
            db: Database session
            order_type_id: Order type ID to filter by
            visit_uuid: Visit UUID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Dictionary with paginated orders and metadata
        """
        from app.models import Encounter, Visit, Person, PersonName, Provider
        from sqlalchemy.orm import aliased

        # Create aliases for Person and PersonName tables to join them multiple times
        OrdererPerson = aliased(Person)
        OrdererPersonName = aliased(PersonName)
        PatientPerson = aliased(Person)
        PatientPersonName = aliased(PersonName)

        # Base query for counting total records
        base_query = (
            db.query(Order)
            .join(Encounter, Order.encounter_id == Encounter.encounter_id)
            .join(Visit, Encounter.visit_id == Visit.visit_id)
            .filter(
                and_(
                    Order.order_type_id == order_type_id,
                    Visit.uuid == visit_uuid,
                    Order.voided == False,  # noqa: E712
                )
            )
        )

        # Get total count
        total = base_query.count()

        # Main query with joins for enriched data
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
            }

            enriched_orders.append(order_dict)

        # Calculate pagination metadata
        page = (skip // limit) + 1 if limit > 0 else 1
        pages = (total + limit - 1) // limit if limit > 0 else 1
        has_next = skip + limit < total
        has_prev = skip > 0

        return {
            "data": enriched_orders,
            "meta": {
                "total": total,
                "page": page,
                "per_page": limit,
                "pages": pages,
                "has_next": has_next,
                "has_prev": has_prev,
            },
        }

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

    def get_order_with_person_info(
        self, db: Session, order_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get order with creator and patient information.

        Args:
            db: Database session
            order_id: Order ID to retrieve

        Returns:
            Dictionary with order data and enriched person information
        """
        # Get the order
        order = db.query(Order).filter(Order.order_id == order_id).first()
        if not order:
            return None

        # Get creator information
        creator_info = self._get_person_info(db, order.creator)

        # Get patient information
        patient_info = self._get_person_info(db, order.patient_id)

        # Convert order to dict and add enriched information
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
            "creator_info": creator_info,
            "patient_info": patient_info,
        }

        return order_dict

    def _get_person_info(self, db: Session, person_id: int) -> Optional[Dict[str, Any]]:
        """
        Get person information including name and UUID.

        Args:
            db: Database session
            person_id: Person ID to retrieve information for

        Returns:
            Dictionary with person information or None if not found
        """
        from app.models import Person, PersonName

        # Get person record
        person = db.query(Person).filter(Person.person_id == person_id).first()
        if not person:
            return None

        # Get all names for this person (not just preferred)
        # Note: Using PersonName.voided == False instead of not PersonName.voided
        # because SQLAlchemy translates 'not PersonName.voided' to 'false = 1' in some DB configs
        all_names = (
            db.query(PersonName)
            .filter(
                and_(
                    PersonName.person_id == person_id,
                    PersonName.voided == False,  # noqa: E712
                )
            )
            .all()
        )

        # Get preferred name
        preferred_name = (
            db.query(PersonName)
            .filter(
                and_(
                    PersonName.person_id == person_id,
                    PersonName.preferred == True,  # noqa: E712
                    PersonName.voided == False,  # noqa: E712
                )
            )
            .first()
        )

        if not preferred_name and all_names:
            # If no preferred name, use the first non-voided name
            preferred_name = all_names[0]

        # Build name string
        name_parts = []
        if preferred_name:
            if preferred_name.prefix:
                name_parts.append(preferred_name.prefix)
            if preferred_name.given_name:
                name_parts.append(preferred_name.given_name)
            if preferred_name.middle_name:
                name_parts.append(preferred_name.middle_name)
            if preferred_name.family_name:
                name_parts.append(preferred_name.family_name)
            if preferred_name.family_name2:
                name_parts.append(preferred_name.family_name2)
            if preferred_name.family_name_suffix:
                name_parts.append(preferred_name.family_name_suffix)

        full_name = " ".join(name_parts) if name_parts else None

        return {
            "person_id": person.person_id,
            "uuid": person.uuid,
            "name": full_name,
            "gender": person.gender,
            "birthdate": person.birthdate,
        }

    def get_order_and_concept_details_by_uuids(
        self,
        db: Session,
        order_uuid: str,
        concept_uuid: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive order and concept details by UUIDs.

        Args:
            db: Database session
            order_uuid: Order UUID
            concept_uuid: Concept UUID

        Returns:
            Dictionary containing order details, orderer info, patient info,
            and comprehensive concept details including set members and answers
        """
        import logging

        logger = logging.getLogger(__name__)

        logger.info(
            "Starting get_order_and_concept_details_by_uuids with order_uuid=%s, concept_uuid=%s",
            order_uuid,
            concept_uuid,
        )

        from app.models import (
            Person,
            PersonName,
            Provider,
        )
        from sqlalchemy.orm import aliased
        from sqlalchemy import func

        # Create aliases for Person and PersonName tables
        OrdererPerson = aliased(Person)
        OrdererPersonName = aliased(PersonName)
        PatientPerson = aliased(Person)
        PatientPersonName = aliased(PersonName)

        # Main query to get order with enriched orderer and patient info
        query = (
            db.query(
                Order,
                # Provider information
                Provider.provider_id.label("provider_id"),
                Provider.name.label("provider_name"),
                Provider.identifier.label("provider_identifier"),
                Provider.uuid.label("provider_uuid"),
                # Orderer person information
                OrdererPerson.person_id.label("orderer_person_id"),
                OrdererPerson.uuid.label("orderer_person_uuid"),
                OrdererPerson.gender.label("orderer_gender"),
                OrdererPerson.birthdate.label("orderer_birthdate"),
                # Orderer person name information
                OrdererPersonName.given_name.label("orderer_given_name"),
                OrdererPersonName.middle_name.label("orderer_middle_name"),
                OrdererPersonName.family_name.label("orderer_family_name"),
                OrdererPersonName.family_name2.label("orderer_family_name2"),
                OrdererPersonName.family_name_suffix.label(
                    "orderer_family_name_suffix"
                ),
                # Patient person information
                PatientPerson.person_id.label("patient_person_id"),
                PatientPerson.uuid.label("patient_person_uuid"),
                PatientPerson.gender.label("patient_gender"),
                PatientPerson.birthdate.label("patient_birthdate"),
                # Patient person name information
                PatientPersonName.given_name.label("patient_given_name"),
                PatientPersonName.middle_name.label("patient_middle_name"),
                PatientPersonName.family_name.label("patient_family_name"),
                PatientPersonName.family_name2.label("patient_family_name2"),
                PatientPersonName.family_name_suffix.label(
                    "patient_family_name_suffix"
                ),
            )
            .outerjoin(Provider, Order.orderer == Provider.provider_id)
            .outerjoin(OrdererPerson, Provider.person_id == OrdererPerson.person_id)
            .outerjoin(
                OrdererPersonName,
                and_(
                    OrdererPersonName.person_id == OrdererPerson.person_id,
                    OrdererPersonName.preferred,
                    not OrdererPersonName.voided,
                ),
            )
            .outerjoin(PatientPerson, Order.patient_id == PatientPerson.person_id)
            .outerjoin(
                PatientPersonName,
                and_(
                    PatientPersonName.person_id == PatientPerson.person_id,
                    PatientPersonName.preferred,
                    not PatientPersonName.voided,
                ),
            )
            .filter(func.lower(Order.uuid) == func.lower(order_uuid))
            .filter(not Order.voided)
        )

        logger.info(f"Executing main order query for order_uuid={order_uuid}")
        logger.info(f"Query SQL: {query}")
        result = query.first()
        if not result:
            logger.warning(f"No order found for order_uuid={order_uuid}")
            return None

        logger.info(
            f"Found order: ID={result[0].order_id}, concept_id={result[0].concept_id}"
        )
        order = result[0]

        # Build orderer info
        orderer_info = None
        if result.provider_id:
            orderer_name_parts = []
            if result.orderer_given_name:
                orderer_name_parts.append(result.orderer_given_name)
            if result.orderer_middle_name:
                orderer_name_parts.append(result.orderer_middle_name)
            if result.orderer_family_name:
                orderer_name_parts.append(result.orderer_family_name)
            if result.orderer_family_name2:
                orderer_name_parts.append(result.orderer_family_name2)
            if result.orderer_family_name_suffix:
                orderer_name_parts.append(result.orderer_family_name_suffix)

            orderer_name = " ".join(orderer_name_parts) if orderer_name_parts else None

            orderer_info = {
                "person_id": result.orderer_person_id,
                "uuid": result.orderer_person_uuid,
                "name": orderer_name,
                "gender": result.orderer_gender,
                "birthdate": result.orderer_birthdate,
                "provider_id": result.provider_id,
                "provider_name": result.provider_name,
                "provider_identifier": result.provider_identifier,
                "provider_uuid": result.provider_uuid,
            }

        # Build patient info
        patient_info = None
        if result.patient_person_id:
            patient_name_parts = []
            if result.patient_given_name:
                patient_name_parts.append(result.patient_given_name)
            if result.patient_middle_name:
                patient_name_parts.append(result.patient_middle_name)
            if result.patient_family_name:
                patient_name_parts.append(result.patient_family_name)
            if result.patient_family_name2:
                patient_name_parts.append(result.patient_family_name2)
            if result.patient_family_name_suffix:
                patient_name_parts.append(result.patient_family_name_suffix)

            patient_name = " ".join(patient_name_parts) if patient_name_parts else None

            patient_info = {
                "person_id": result.patient_person_id,
                "uuid": result.patient_person_uuid,
                "name": patient_name,
                "gender": result.patient_gender,
                "birthdate": result.patient_birthdate,
            }

        # Get comprehensive concept details
        logger.info(
            f"Getting comprehensive concept details for concept_uuid={concept_uuid}"
        )
        concept_details = self._get_comprehensive_concept_details(db, concept_uuid)
        if concept_details:
            logger.info(
                f"Found concept details: concept_id={concept_details.get('concept_id')}, name={concept_details.get('name')}"
            )
        else:
            logger.warning(f"No concept details found for concept_uuid={concept_uuid}")

        # Build the complete response
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
            "orderer_info": orderer_info,
            "patient_info": patient_info,
            "concept_details": concept_details,
        }

        logger.info(f"Successfully built order_dict with {len(order_dict)} fields")
        return order_dict

    def _get_comprehensive_concept_details(
        self, db: Session, concept_uuid: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive concept details including datatype, class, answers, and set members.

        Args:
            db: Database session
            concept_uuid: Concept UUID

        Returns:
            Dictionary containing comprehensive concept information
        """
        import logging

        logger = logging.getLogger(__name__)

        logger.info(
            f"Getting comprehensive concept details for concept_uuid={concept_uuid}"
        )
        from app.models import (
            Concept,
            ConceptName,
            ConceptDatatype,
            ConceptClass,
        )
        from sqlalchemy import func

        # Get main concept with datatype and class information
        concept_query = (
            db.query(
                Concept,
                ConceptDatatype.concept_datatype_id.label("datatype_id"),
                ConceptDatatype.name.label("datatype_name"),
                ConceptDatatype.hl7_abbreviation.label("datatype_hl7_abbreviation"),
                ConceptDatatype.description.label("datatype_description"),
                ConceptDatatype.uuid.label("datatype_uuid"),
                ConceptClass.concept_class_id.label("class_id"),
                ConceptClass.name.label("class_name"),
                ConceptClass.description.label("class_description"),
                ConceptClass.uuid.label("class_uuid"),
                ConceptName.name.label("concept_name"),
                ConceptName.locale.label("concept_name_locale"),
                ConceptName.locale_preferred.label("concept_name_locale_preferred"),
                ConceptName.concept_name_type.label("concept_name_type"),
            )
            .outerjoin(
                ConceptDatatype,
                Concept.datatype_id == ConceptDatatype.concept_datatype_id,
            )
            .outerjoin(ConceptClass, Concept.class_id == ConceptClass.concept_class_id)
            .outerjoin(
                ConceptName,
                and_(
                    ConceptName.concept_id == Concept.concept_id,
                    ConceptName.locale == "en",
                    ConceptName.concept_name_type == "FULLY_SPECIFIED",
                    not ConceptName.voided,
                ),
            )
            .filter(func.lower(Concept.uuid) == func.lower(concept_uuid))
            .filter(not Concept.retired)
        )

        logger.info(f"Executing concept query for concept_uuid={concept_uuid}")
        logger.info(f"Concept query SQL: {concept_query}")
        concept_result = concept_query.first()
        if not concept_result:
            logger.warning(f"No concept found for concept_uuid={concept_uuid}")
            return None

        logger.info(
            f"Found concept: ID={concept_result[0].concept_id}, is_set={concept_result[0].is_set}"
        )
        concept = concept_result[0]

        # Build datatype info
        datatype_info = None
        if concept_result.datatype_id:
            datatype_info = {
                "concept_datatype_id": concept_result.datatype_id,
                "name": concept_result.datatype_name,
                "hl7_abbreviation": concept_result.datatype_hl7_abbreviation,
                "description": concept_result.datatype_description,
                "uuid": concept_result.datatype_uuid,
            }

        # Build class info
        class_info = None
        if concept_result.class_id:
            class_info = {
                "concept_class_id": concept_result.class_id,
                "name": concept_result.class_name,
                "description": concept_result.class_description,
                "uuid": concept_result.class_uuid,
            }

        # Get concept answers if any
        logger.info(f"Getting concept answers for concept_id={concept.concept_id}")
        try:
            answers = self._get_concept_answers(db, concept.concept_id)
            logger.info(f"Found {len(answers) if answers else 0} concept answers")
        except Exception as e:
            logger.error(f"Error getting concept answers: {e}")
            answers = None

        # Get set members if concept is a set
        set_members = None
        if concept.is_set:
            logger.info(f"Getting set members for concept_id={concept.concept_id}")
            try:
                set_members = self._get_concept_set_members(db, concept.concept_id)
                logger.info(
                    f"Found {len(set_members) if set_members else 0} set members"
                )
            except Exception as e:
                logger.error(f"Error getting set members: {e}")
                set_members = None

        return {
            "concept_id": concept.concept_id,
            "uuid": concept.uuid,
            "name": concept_result.concept_name,
            "description": concept.description,
            "short_name": concept.short_name,
            "datatype": datatype_info,
            "concept_class": class_info,
            "is_set": concept.is_set,
            "answers": answers,
            "set_members": set_members,
        }

    def _get_concept_answers(
        self, db: Session, concept_id: int
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get concept answers with their details.

        Args:
            db: Database session
            concept_id: Concept ID

        Returns:
            List of concept answer dictionaries
        """
        from app.models import (
            ConceptAnswer,
            Concept,
            ConceptName,
            ConceptDatatype,
            ConceptClass,
        )

        answers_query = (
            db.query(
                ConceptAnswer.answer_concept.label("answer_concept_id"),
                Concept.uuid.label("answer_uuid"),
                ConceptName.name.label("answer_name"),
                Concept.description.label("answer_description"),
                ConceptDatatype.concept_datatype_id.label("answer_datatype_id"),
                ConceptDatatype.name.label("answer_datatype_name"),
                ConceptDatatype.hl7_abbreviation.label(
                    "answer_datatype_hl7_abbreviation"
                ),
                ConceptDatatype.description.label("answer_datatype_description"),
                ConceptDatatype.uuid.label("answer_datatype_uuid"),
                ConceptClass.concept_class_id.label("answer_class_id"),
                ConceptClass.name.label("answer_class_name"),
                ConceptClass.description.label("answer_class_description"),
                ConceptClass.uuid.label("answer_class_uuid"),
            )
            .join(Concept, ConceptAnswer.answer_concept == Concept.concept_id)
            .outerjoin(
                ConceptName,
                and_(
                    ConceptName.concept_id == Concept.concept_id,
                    ConceptName.locale == "en",
                    ConceptName.concept_name_type == "FULLY_SPECIFIED",
                    not ConceptName.voided,
                ),
            )
            .outerjoin(
                ConceptDatatype,
                Concept.datatype_id == ConceptDatatype.concept_datatype_id,
            )
            .outerjoin(ConceptClass, Concept.class_id == ConceptClass.concept_class_id)
            .filter(ConceptAnswer.concept_id == concept_id)
            .filter(not Concept.retired)
        )

        answers = []
        for result in answers_query.all():
            answer_datatype = None
            if result.answer_datatype_id:
                answer_datatype = {
                    "concept_datatype_id": result.answer_datatype_id,
                    "name": result.answer_datatype_name,
                    "hl7_abbreviation": result.answer_datatype_hl7_abbreviation,
                    "description": result.answer_datatype_description,
                    "uuid": result.answer_datatype_uuid,
                }

            answer_class = None
            if result.answer_class_id:
                answer_class = {
                    "concept_class_id": result.answer_class_id,
                    "name": result.answer_class_name,
                    "description": result.answer_class_description,
                    "uuid": result.answer_class_uuid,
                }

            answers.append(
                {
                    "concept_id": result.answer_concept_id,
                    "uuid": result.answer_uuid,
                    "name": result.answer_name,
                    "description": result.answer_description,
                    "datatype": answer_datatype,
                    "concept_class": answer_class,
                }
            )

        return answers if answers else None

    def _get_concept_set_members(
        self, db: Session, concept_id: int
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get concept set members with their details.

        Args:
            db: Database session
            concept_id: Concept ID

        Returns:
            List of concept set member dictionaries
        """
        from app.models import (
            ConceptSet,
            Concept,
            ConceptName,
            ConceptDatatype,
            ConceptClass,
        )

        set_members_query = (
            db.query(
                ConceptSet.concept_set.label("member_concept_id"),
                Concept.uuid.label("member_uuid"),
                ConceptName.name.label("member_name"),
                Concept.description.label("member_description"),
                ConceptDatatype.concept_datatype_id.label("member_datatype_id"),
                ConceptDatatype.name.label("member_datatype_name"),
                ConceptDatatype.hl7_abbreviation.label(
                    "member_datatype_hl7_abbreviation"
                ),
                ConceptDatatype.description.label("member_datatype_description"),
                ConceptDatatype.uuid.label("member_datatype_uuid"),
                ConceptClass.concept_class_id.label("member_class_id"),
                ConceptClass.name.label("member_class_name"),
                ConceptClass.description.label("member_class_description"),
                ConceptClass.uuid.label("member_class_uuid"),
                ConceptSet.sort_weight.label("member_sort_weight"),
            )
            .join(Concept, ConceptSet.concept_set == Concept.concept_id)
            .outerjoin(
                ConceptName,
                and_(
                    ConceptName.concept_id == Concept.concept_id,
                    ConceptName.locale == "en",
                    ConceptName.concept_name_type == "FULLY_SPECIFIED",
                    not ConceptName.voided,
                ),
            )
            .outerjoin(
                ConceptDatatype,
                Concept.datatype_id == ConceptDatatype.concept_datatype_id,
            )
            .outerjoin(ConceptClass, Concept.class_id == ConceptClass.concept_class_id)
            .filter(ConceptSet.concept_id == concept_id)
            .filter(not Concept.retired)
            .order_by(ConceptSet.sort_weight)
        )

        set_members = []
        for result in set_members_query.all():
            member_datatype = None
            if result.member_datatype_id:
                member_datatype = {
                    "concept_datatype_id": result.member_datatype_id,
                    "name": result.member_datatype_name,
                    "hl7_abbreviation": result.member_datatype_hl7_abbreviation,
                    "description": result.member_datatype_description,
                    "uuid": result.member_datatype_uuid,
                }

            member_class = None
            if result.member_class_id:
                member_class = {
                    "concept_class_id": result.member_class_id,
                    "name": result.member_class_name,
                    "description": result.member_class_description,
                    "uuid": result.member_class_uuid,
                }

            # Get answers for this set member
            member_answers = self._get_concept_answers(db, result.member_concept_id)

            set_members.append(
                {
                    "concept_id": result.member_concept_id,
                    "uuid": result.member_uuid,
                    "name": result.member_name,
                    "description": result.member_description,
                    "datatype": member_datatype,
                    "concept_class": member_class,
                    "answers": member_answers,
                    "sort_weight": result.member_sort_weight,
                }
            )

        return set_members if set_members else None


# Create instance
orders_crud = OrdersCRUD()
