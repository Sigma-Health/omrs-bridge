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

    def get_orders_by_type_and_visit_uuid(
        self,
        db: Session,
        order_type_id: int,
        visit_uuid: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Order]:
        """
        Get orders by order type and visit UUID.

        Args:
            db: Database session
            order_type_id: Order type ID to filter by
            visit_uuid: Visit UUID to filter by
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
                    Visit.uuid == visit_uuid,
                    Order.voided == False,  # noqa: E712
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

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

        logger.info(f"Getting orders for visit UUID: {visit_uuid}")

        try:
            # First, let's check if the visit exists
            visit = db.query(Visit).filter(Visit.uuid == visit_uuid).first()
            if not visit:
                logger.warning(f"Visit with UUID {visit_uuid} not found")
                return []

            logger.info(
                f"Found visit: ID={visit.visit_id}, patient_id={visit.patient_id}"
            )

            # Check encounters for this visit
            encounters = (
                db.query(Encounter).filter(Encounter.visit_id == visit.visit_id).all()
            )
            logger.info(
                f"Found {len(encounters)} encounters for visit {visit.visit_id}"
            )

            for encounter in encounters:
                logger.info(
                    f"Encounter: ID={encounter.encounter_id}, type={encounter.encounter_type}, voided={encounter.voided}"
                )

            # Now check orders for these encounters
            encounter_ids = [e.encounter_id for e in encounters]
            if encounter_ids:
                orders_query = db.query(Order).filter(
                    Order.encounter_id.in_(encounter_ids)
                )
                all_orders = orders_query.all()
                logger.info(
                    f"Found {len(all_orders)} total orders for encounters {encounter_ids}"
                )

                for order in all_orders:
                    logger.info(
                        f"Order: ID={order.order_id}, encounter_id={order.encounter_id}, voided={order.voided}, order_type_id={order.order_type_id}"
                    )
            else:
                logger.warning("No encounters found, so no orders to check")
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

            # Log the SQL query
            logger.info(f"Executing query: {query}")

            result = query.offset(skip).limit(limit).all()
            logger.info(f"Query returned {len(result)} orders")

            return result

        except Exception as e:
            logger.error(f"Error getting orders for visit UUID {visit_uuid}: {str(e)}")
            logger.exception("Full traceback:")
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

        logger.info(f"Getting person info for person_id: {person_id}")

        # Get person record
        person = db.query(Person).filter(Person.person_id == person_id).first()
        if not person:
            logger.warning(f"Person with ID {person_id} not found")
            return None

        logger.info(
            f"Found person: ID={person.person_id}, UUID={person.uuid}, gender={person.gender}"
        )

        # Debug: Try raw SQL first
        from sqlalchemy import text

        raw_sql = text(
            "SELECT * FROM person_name WHERE person_id = :person_id AND voided = 0"
        )
        raw_result = db.execute(raw_sql, {"person_id": person_id}).fetchall()
        logger.info(f"Raw SQL found {len(raw_result)} names for person {person_id}")
        for row in raw_result:
            logger.info(f"Raw SQL row: {dict(row._mapping)}")

        # Get all names for this person (not just preferred)
        query = db.query(PersonName).filter(
            and_(
                PersonName.person_id == person_id,
                not PersonName.voided,
            )
        )
        logger.info(f"SQLAlchemy query: {query}")
        all_names = query.all()

        logger.info(f"Found {len(all_names)} names for person {person_id}")
        for name in all_names:
            logger.info(
                f"Name: ID={name.person_name_id}, preferred={name.preferred} (type: {type(name.preferred)}), given={name.given_name}, family={name.family_name}"
            )

        # Get preferred name - try different approaches
        preferred_name = (
            db.query(PersonName)
            .filter(
                and_(
                    PersonName.person_id == person_id,
                    PersonName.preferred == True,  # noqa: E712
                    not PersonName.voided,
                )
            )
            .first()
        )

        if not preferred_name:
            # Try with integer comparison
            preferred_name = (
                db.query(PersonName)
                .filter(
                    and_(
                        PersonName.person_id == person_id,
                        PersonName.preferred == 1,
                        not PersonName.voided,
                    )
                )
                .first()
            )
            logger.info(
                f"Tried integer comparison for preferred name, found: {preferred_name is not None}"
            )

        if not preferred_name and all_names:
            # If no preferred name, use the first non-voided name
            preferred_name = all_names[0]
            logger.info(
                f"No preferred name found, using first name: {preferred_name.given_name} {preferred_name.family_name}"
            )

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
        logger.info(f"Built full name: '{full_name}'")

        return {
            "person_id": person.person_id,
            "uuid": person.uuid,
            "name": full_name,
            "gender": person.gender,
            "birthdate": person.birthdate,
        }

    def get_orders_by_visit_uuid_with_person_info(
        self, db: Session, visit_uuid: str, skip: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all orders for a visit by visit UUID with enriched creator and patient information.

        Args:
            db: Database session
            visit_uuid: Visit UUID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of orders with enriched person information
        """
        from app.models import Encounter, Visit

        logger.info(f"Getting orders with person info for visit UUID: {visit_uuid}")

        try:
            # First, let's check if the visit exists
            visit = db.query(Visit).filter(Visit.uuid == visit_uuid).first()
            if not visit:
                logger.warning(f"Visit with UUID {visit_uuid} not found")
                return []

            logger.info(
                f"Found visit: ID={visit.visit_id}, patient_id={visit.patient_id}"
            )

            # Get orders using the same logic as the regular method
            query = (
                db.query(Order)
                .join(Encounter, Order.encounter_id == Encounter.encounter_id)
                .join(Visit, Encounter.visit_id == Visit.visit_id)
                .filter(and_(Visit.uuid == visit_uuid, Order.voided == False))  # noqa: E712
            )

            orders_list = query.offset(skip).limit(limit).all()
            logger.info(
                f"Found {len(orders_list)} orders, now enriching with person info"
            )

            # Enrich each order with person information
            enriched_orders = []
            for order in orders_list:
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

                enriched_orders.append(order_dict)

            logger.info(f"Returning {len(enriched_orders)} enriched orders")
            return enriched_orders

        except Exception as e:
            logger.error(
                f"Error getting orders with person info for visit UUID {visit_uuid}: {str(e)}"
            )
            logger.exception("Full traceback:")
            raise


# Create instance
orders_crud = OrdersCRUD()
