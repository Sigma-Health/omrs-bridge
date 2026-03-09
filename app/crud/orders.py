import logging
import uuid
import secrets

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, aliased
from sqlalchemy import and_, select
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

    def _generate_order_number(self, db: Session) -> str:
        """
        Generate a unique fallback order number when not provided.
        Format: ORD-<10_HEX_CHARS>
        """
        for _ in range(10):
            candidate = f"ORD-{secrets.token_hex(5).upper()}"
            exists = db.query(Order.order_id).filter(Order.order_number == candidate).first()
            if not exists:
                return candidate
        # Extremely unlikely fallback
        return f"ORD-{uuid.uuid4().hex[:12].upper()}"

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

    def create_for_visit_uuid(self, db: Session, visit_uuid: str, payload: Any) -> Order:
        """
        Create an order by visit UUID.

        Behavior:
        - Resolve visit by UUID
        - Reuse existing unvoided encounter for that visit with encounter_type=1
        - If none exists, create encounter_type=1 and use it
        - Create order linked to that encounter
        """
        from app.models import Visit, Encounter

        visit = (
            db.query(Visit)
            .filter(and_(Visit.uuid == visit_uuid, Visit.voided == False))  # noqa: E712
            .first()
        )
        if not visit:
            raise LookupError("Visit not found")

        if not visit.patient_id:
            raise ValueError("Visit has no patient_id")

        now = datetime.utcnow()
        encounter = (
            db.query(Encounter)
            .filter(
                and_(
                    Encounter.visit_id == visit.visit_id,
                    Encounter.encounter_type == 1,
                    Encounter.voided == False,  # noqa: E712
                )
            )
            .order_by(Encounter.encounter_datetime.desc(), Encounter.encounter_id.desc())
            .first()
        )

        try:
            if not encounter:
                encounter = Encounter(
                    encounter_type=1,
                    patient_id=visit.patient_id,
                    location_id=visit.location_id,
                    encounter_datetime=payload.date_activated or now,
                    creator=payload.creator,
                    date_created=now,
                    voided=False,
                    visit_id=visit.visit_id,
                    uuid=str(uuid.uuid4()),
                )
                db.add(encounter)
                db.flush()

            obj_data = payload.dict(exclude_unset=True)
            obj_data["encounter_id"] = encounter.encounter_id
            obj_data["patient_id"] = visit.patient_id
            obj_data["uuid"] = str(uuid.uuid4())
            obj_data["date_created"] = now

            if not obj_data.get("date_activated"):
                obj_data["date_activated"] = now
            if not obj_data.get("order_number"):
                obj_data["order_number"] = self._generate_order_number(db)

            self._set_default_values(obj_data)

            db_order = Order(**obj_data)
            db.add(db_order)
            db.commit()
            db.refresh(db_order)
            return db_order
        except Exception:
            db.rollback()
            raise

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
        self,
        db: Session,
        order_id: int,
        voided_by: int,
        reason: str = None,
        force: bool = False,
    ) -> Optional[Order]:
        """
        Void an order.

        Args:
            db: Database session
            order_id: ID of the order to void
            voided_by: ID of the user voiding the order
            reason: Optional reason for voiding

        Args:
            force: If True, bypass visit active-status validation.

        Returns:
            The voided order if found, None otherwise
        """
        from app.models import Encounter, Visit

        db_order = self.get(db, order_id)
        if not db_order:
            return None

        if not force:
            encounter = None
            if db_order.encounter_id is not None:
                encounter = (
                    db.query(Encounter)
                    .filter(Encounter.encounter_id == db_order.encounter_id)
                    .first()
                )

            visit = None
            if encounter and encounter.visit_id is not None:
                visit = db.query(Visit).filter(Visit.visit_id == encounter.visit_id).first()

            # Standard void only allowed for active visits.
            # Active = not voided and date_stopped is null.
            if not visit:
                raise ValueError(
                    "Order cannot be voided because visit context could not be resolved. Use force void if intended."
                )
            if visit.voided or visit.date_stopped is not None:
                raise ValueError(
                    "Order can only be voided for active visits. Use force void to bypass this check."
                )

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

        # Create aliases for Person tables to join them multiple times
        OrdererPerson = aliased(Person)
        PatientPerson = aliased(Person)
        # Create alias for SHORT concept name
        ShortConceptName = aliased(ConceptName)

        orderer_name_subquery = (
            select(
                func.concat_ws(
                    " ",
                    PersonName.prefix,
                    PersonName.given_name,
                    PersonName.middle_name,
                    PersonName.family_name,
                    PersonName.family_name2,
                    PersonName.family_name_suffix,
                )
            )
            .where(
                and_(
                    PersonName.person_id == Provider.person_id,
                    PersonName.voided == False,  # noqa: E712
                )
            )
            .order_by(
                PersonName.preferred.desc(),
                PersonName.date_created.desc(),
                PersonName.person_name_id.desc(),
            )
            .limit(1)
            .correlate(Provider)
            .scalar_subquery()
        )

        patient_name_subquery = (
            select(
                func.concat_ws(
                    " ",
                    PersonName.prefix,
                    PersonName.given_name,
                    PersonName.middle_name,
                    PersonName.family_name,
                    PersonName.family_name2,
                    PersonName.family_name_suffix,
                )
            )
            .where(
                and_(
                    PersonName.person_id == Order.patient_id,
                    PersonName.voided == False,  # noqa: E712
                )
            )
            .order_by(
                PersonName.preferred.desc(),
                PersonName.date_created.desc(),
                PersonName.person_name_id.desc(),
            )
            .limit(1)
            .correlate(Order)
            .scalar_subquery()
        )

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
                # Deterministic names
                orderer_name_subquery.label("orderer_name"),
                # Patient information
                PatientPerson.person_id.label("patient_person_id"),
                PatientPerson.uuid.label("patient_uuid"),
                PatientPerson.gender.label("patient_gender"),
                PatientPerson.birthdate.label("patient_birthdate"),
                patient_name_subquery.label("patient_name"),
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
            # Join for patient information
            .outerjoin(
                PatientPerson,
                and_(
                    PatientPerson.person_id == Order.patient_id,
                    PatientPerson.voided == False,  # noqa: E712
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

            orderer_name = row.orderer_name or row.provider_name
            patient_name = row.patient_name

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
    ) -> List[Dict[str, Any]]:
        """
        Get all orders for a visit by visit UUID with enriched information.

        Args:
            db: Database session
            visit_uuid: Visit UUID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of all orders for the specified visit with enriched details
        """
        from app.models import (
            Encounter,
            Visit,
            Person,
            PersonName,
            Provider,
            Concept,
            ConceptName,
            DrugOrder,
            Drug,
        )

        # Create aliases for Person tables to join them multiple times
        OrdererPerson = aliased(Person)
        PatientPerson = aliased(Person)
        CreatorPerson = aliased(Person)
        # Create alias for SHORT concept name
        ShortConceptName = aliased(ConceptName)
        # Create alias for route concept name
        RouteConceptName = aliased(ConceptName)

        orderer_name_subquery = (
            select(
                func.concat_ws(
                    " ",
                    PersonName.prefix,
                    PersonName.given_name,
                    PersonName.middle_name,
                    PersonName.family_name,
                    PersonName.family_name2,
                    PersonName.family_name_suffix,
                )
            )
            .where(
                and_(
                    PersonName.person_id == Provider.person_id,
                    PersonName.voided == False,  # noqa: E712
                )
            )
            .order_by(
                PersonName.preferred.desc(),
                PersonName.date_created.desc(),
                PersonName.person_name_id.desc(),
            )
            .limit(1)
            .correlate(Provider)
            .scalar_subquery()
        )

        patient_name_subquery = (
            select(
                func.concat_ws(
                    " ",
                    PersonName.prefix,
                    PersonName.given_name,
                    PersonName.middle_name,
                    PersonName.family_name,
                    PersonName.family_name2,
                    PersonName.family_name_suffix,
                )
            )
            .where(
                and_(
                    PersonName.person_id == Order.patient_id,
                    PersonName.voided == False,  # noqa: E712
                )
            )
            .order_by(
                PersonName.preferred.desc(),
                PersonName.date_created.desc(),
                PersonName.person_name_id.desc(),
            )
            .limit(1)
            .correlate(Order)
            .scalar_subquery()
        )

        creator_name_subquery = (
            select(
                func.concat_ws(
                    " ",
                    PersonName.prefix,
                    PersonName.given_name,
                    PersonName.middle_name,
                    PersonName.family_name,
                    PersonName.family_name2,
                    PersonName.family_name_suffix,
                )
            )
            .where(
                and_(
                    PersonName.person_id == Order.creator,
                    PersonName.voided == False,  # noqa: E712
                )
            )
            .order_by(
                PersonName.preferred.desc(),
                PersonName.date_created.desc(),
                PersonName.person_name_id.desc(),
            )
            .limit(1)
            .correlate(Order)
            .scalar_subquery()
        )

        try:
            # First, let's check if the visit exists
            visit = db.query(Visit).filter(Visit.uuid == visit_uuid).first()
            if not visit:
                return []

            # Build enriched query
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
                    orderer_name_subquery.label("orderer_name"),
                    # Patient information
                    PatientPerson.person_id.label("patient_person_id"),
                    PatientPerson.uuid.label("patient_uuid"),
                    PatientPerson.gender.label("patient_gender"),
                    PatientPerson.birthdate.label("patient_birthdate"),
                    patient_name_subquery.label("patient_name"),
                    # Creator information
                    CreatorPerson.person_id.label("creator_person_id"),
                    CreatorPerson.uuid.label("creator_uuid"),
                    CreatorPerson.gender.label("creator_gender"),
                    CreatorPerson.birthdate.label("creator_birthdate"),
                    creator_name_subquery.label("creator_name"),
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
                    # Drug order information
                    DrugOrder.dose.label("drug_dose"),
                    DrugOrder.quantity.label("drug_quantity"),
                    DrugOrder.frequency.label("drug_frequency"),
                    DrugOrder.route.label("drug_route"),
                    DrugOrder.dose_units.label("drug_dose_units"),
                    DrugOrder.quantity_units.label("drug_quantity_units"),
                    DrugOrder.dosing_instructions.label("drug_dosing_instructions"),
                    DrugOrder.as_needed.label("drug_as_needed"),
                    DrugOrder.as_needed_condition.label("drug_as_needed_condition"),
                    DrugOrder.duration.label("drug_duration"),
                    DrugOrder.duration_units.label("drug_duration_units"),
                    DrugOrder.num_refills.label("drug_num_refills"),
                    # Drug information
                    Drug.name.label("drug_name"),
                    # Route concept name
                    RouteConceptName.name.label("route_name"),
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
                # Join for patient information
                .outerjoin(
                    PatientPerson,
                    and_(
                        PatientPerson.person_id == Order.patient_id,
                        PatientPerson.voided == False,  # noqa: E712
                    ),
                )
                # Join for creator information
                .outerjoin(
                    CreatorPerson,
                    and_(
                        CreatorPerson.person_id == Order.creator,
                        CreatorPerson.voided == False,  # noqa: E712
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
                # Join for drug order information (only for drug orders)
                .outerjoin(DrugOrder, DrugOrder.order_id == Order.order_id)
                # Join for drug information
                .outerjoin(
                    Drug,
                    and_(
                        Drug.drug_id == DrugOrder.drug_inventory_id,
                        Drug.retired == False,  # noqa: E712
                    ),
                )
                # Join for route concept name
                .outerjoin(
                    RouteConceptName,
                    and_(
                        RouteConceptName.concept_id == DrugOrder.route,
                        RouteConceptName.locale == "en",
                        RouteConceptName.concept_name_type == "FULLY_SPECIFIED",
                        RouteConceptName.voided == False,  # noqa: E712
                    ),
                )
                .filter(and_(Visit.uuid == visit_uuid, Order.voided == False))  # noqa: E712
                .offset(skip)
                .limit(limit)
            )

            results = query.all()

            # Transform results into enriched order dictionaries
            enriched_orders = []
            for row in results:
                order = row[0]  # The Order object is first in the tuple

                orderer_name = row.orderer_name or row.provider_name
                patient_name = row.patient_name
                creator_name = row.creator_name

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
                    # Add concept_name and concept_uuid directly
                    "concept_name": row.concept_name,
                    "concept_uuid": row.concept_uuid,
                    # Enriched creator information
                    "creator_info": {
                        "person_id": row.creator_person_id,
                        "uuid": row.creator_uuid,
                        "name": creator_name,
                        "gender": row.creator_gender,
                        "birthdate": row.creator_birthdate,
                    }
                    if row.creator_person_id
                    else None,
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
                    # Drug order information (only for order_type_id=2)
                    "drug_order_info": {
                        "dose": row.drug_dose,
                        "quantity": row.drug_quantity,
                        "frequency": row.drug_frequency,
                        "route": row.drug_route,
                        "dose_units": row.drug_dose_units,
                        "quantity_units": row.drug_quantity_units,
                        "dosing_instructions": row.drug_dosing_instructions,
                        "as_needed": row.drug_as_needed,
                        "as_needed_condition": row.drug_as_needed_condition,
                        "duration": row.drug_duration,
                        "duration_units": row.drug_duration_units,
                        "num_refills": row.drug_num_refills,
                        "drug_name": row.drug_name,
                        "route_name": row.route_name,
                    }
                    if order.order_type_id == 2 and row.drug_dose is not None
                    else None,
                }

                enriched_orders.append(order_dict)

            return enriched_orders

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
