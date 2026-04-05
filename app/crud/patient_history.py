"""
CRUD operations for patient history endpoints.
"""

from typing import Dict, List

from sqlalchemy.orm import Session

from app.crud.chief_complaint import chief_complaint
from app.crud.orders import orders_crud
from app.crud.physical_exam import physical_exam
from app.models.patient import Patient
from app.models.person import Person
from app.models.visit import Visit
from app.schemas.patient_history import (
    HistoryType,
    PatientHistoryCounts,
    PatientHistoryResponse,
    PatientHistorySummaryResponse,
    PatientHistoryVisitGroup,
)


class PatientHistoryError(Exception):
    """Raised for known patient history lookup failures."""

    def __init__(self, code: str, status: int = 404):
        self.code = code
        self.status = status
        super().__init__(code)


class PatientHistoryCRUD:
    """Read-only patient history aggregation by patient UUID."""

    def _resolve_patient(self, db: Session, patient_uuid: str) -> Person:
        person = (
            db.query(Person)
            .join(Patient, Patient.patient_id == Person.person_id)
            .filter(
                Person.uuid == patient_uuid,
                Person.voided == False,  # noqa: E712
                Patient.voided == False,  # noqa: E712
            )
            .first()
        )

        if not person:
            raise PatientHistoryError("patient_not_found")

        return person

    def _get_visits(self, db: Session, patient_id: int) -> List[Visit]:
        return (
            db.query(Visit)
            .filter(
                Visit.patient_id == patient_id,
                Visit.voided == False,  # noqa: E712
            )
            .order_by(Visit.date_started.desc(), Visit.visit_id.desc())
            .all()
        )

    def _build_visit_group(
        self, db: Session, visit: Visit, requested_type: HistoryType = "all"
    ) -> PatientHistoryVisitGroup:
        complaints = []
        examination_notes = []
        orders = []
        treatments = []

        if requested_type in ("all", "complaint"):
            complaints_response = chief_complaint.get_complaints_by_visit(
                db, visit_id=visit.visit_id
            )
            complaints = complaints_response.complaints

        if requested_type in ("all", "examination"):
            examination_response = physical_exam.get_exam_notes_by_visit(
                db, visit_id=visit.visit_id, visit_uuid=None
            )
            examination_notes = examination_response.observations

        if requested_type in ("all", "orders", "treatments"):
            visit_orders = orders_crud.get_orders_by_visit_uuid(
                db, visit_uuid=visit.uuid, skip=0, limit=1000
            )
            if requested_type in ("all", "orders"):
                orders = visit_orders
            if requested_type in ("all", "treatments"):
                treatments = [
                    order
                    for order in visit_orders
                    if order.get("order_type_id") == 2 or order.get("drug_order_info")
                ]

        return PatientHistoryVisitGroup(
            visit_id=visit.visit_id,
            visit_uuid=visit.uuid,
            visit_date_started=visit.date_started,
            visit_date_stopped=visit.date_stopped,
            complaints=complaints,
            examination_notes=examination_notes,
            orders=orders,
            treatments=treatments,
        )

    def _build_counts(self, visits: List[PatientHistoryVisitGroup]) -> PatientHistoryCounts:
        return PatientHistoryCounts(
            visits=len(visits),
            complaints=sum(len(visit.complaints) for visit in visits),
            examination_notes=sum(len(visit.examination_notes) for visit in visits),
            orders=sum(len(visit.orders) for visit in visits),
            treatments=sum(len(visit.treatments) for visit in visits),
        )

    def _visit_has_requested_history(
        self, visit: PatientHistoryVisitGroup, requested_type: HistoryType
    ) -> bool:
        if requested_type == "complaint":
            return bool(visit.complaints)
        if requested_type == "examination":
            return bool(visit.examination_notes)
        if requested_type == "orders":
            return bool(visit.orders)
        if requested_type == "treatments":
            return bool(visit.treatments)
        return bool(
            visit.complaints
            or visit.examination_notes
            or visit.orders
            or visit.treatments
        )

    def get_history(
        self, db: Session, patient_uuid: str, requested_type: HistoryType = "all"
    ) -> PatientHistoryResponse:
        person = self._resolve_patient(db, patient_uuid)
        visits = self._get_visits(db, person.person_id)
        visit_groups = [
            self._build_visit_group(db, visit, requested_type=requested_type)
            for visit in visits
        ]
        visit_groups = [
            visit
            for visit in visit_groups
            if self._visit_has_requested_history(visit, requested_type)
        ]

        return PatientHistoryResponse(
            patient_id=person.person_id,
            patient_uuid=person.uuid,
            requested_type=requested_type,
            counts=self._build_counts(visit_groups),
            visits=visit_groups,
        )

    def _limit_visit_groups_for_summary(
        self, visits: List[PatientHistoryVisitGroup], max_items_per_category: int
    ) -> List[PatientHistoryVisitGroup]:
        category_limits = {
            "complaints": max_items_per_category,
            "examination_notes": max_items_per_category,
            "orders": max_items_per_category,
            "treatments": max_items_per_category,
        }
        grouped: Dict[int, PatientHistoryVisitGroup] = {}

        for visit in visits:
            for category in category_limits:
                remaining = category_limits[category]
                if remaining <= 0:
                    continue

                items = getattr(visit, category)
                if not items:
                    continue

                selected_items = items[:remaining]
                category_limits[category] -= len(selected_items)

                if visit.visit_id not in grouped:
                    grouped[visit.visit_id] = PatientHistoryVisitGroup(
                        visit_id=visit.visit_id,
                        visit_uuid=visit.visit_uuid,
                        visit_date_started=visit.visit_date_started,
                        visit_date_stopped=visit.visit_date_stopped,
                        complaints=[],
                        examination_notes=[],
                        orders=[],
                        treatments=[],
                    )

                setattr(grouped[visit.visit_id], category, selected_items)

            if all(limit <= 0 for limit in category_limits.values()):
                break

        return [grouped[visit.visit_id] for visit in visits if visit.visit_id in grouped]

    def _build_summary_text(
        self,
        counts: PatientHistoryCounts,
        visits: List[PatientHistoryVisitGroup],
        max_items_per_category: int,
    ) -> str:
        fragments = [f"{counts.visits} visits on record"]

        if counts.complaints:
            complaint_names: List[str] = []
            for visit in visits:
                for complaint in visit.complaints:
                    label = None
                    if complaint.complaint:
                        label = (
                            complaint.complaint.value_coded_name
                            or complaint.complaint.value_text
                            or complaint.complaint.concept_name
                        )
                    if label:
                        complaint_names.append(label)
                    if len(complaint_names) >= max_items_per_category:
                        break
                if len(complaint_names) >= max_items_per_category:
                    break
            if complaint_names:
                fragments.append(f"recent complaints/HPI include {', '.join(complaint_names)}")

        if counts.orders:
            order_names: List[str] = []
            for visit in visits:
                for order in visit.orders:
                    label = (
                        order.concept_name
                        or (order.concept_info.name if order.concept_info else None)
                        or order.order_number
                    )
                    if label:
                        order_names.append(label)
                    if len(order_names) >= max_items_per_category:
                        break
                if len(order_names) >= max_items_per_category:
                    break
            if order_names:
                fragments.append(f"recent orders include {', '.join(order_names)}")

        if counts.treatments:
            treatment_names: List[str] = []
            for visit in visits:
                for treatment in visit.treatments:
                    label = None
                    if treatment.drug_order_info and treatment.drug_order_info.drug_info:
                        label = treatment.drug_order_info.drug_info.name
                    if not label:
                        label = treatment.concept_name or treatment.order_number
                    if label:
                        treatment_names.append(label)
                    if len(treatment_names) >= max_items_per_category:
                        break
                if len(treatment_names) >= max_items_per_category:
                    break
            if treatment_names:
                fragments.append(f"medications/treatments include {', '.join(treatment_names)}")

        return ". ".join(fragments) + "."

    def get_history_summary(
        self, db: Session, patient_uuid: str, max_items_per_category: int = 3
    ) -> PatientHistorySummaryResponse:
        history = self.get_history(db, patient_uuid=patient_uuid, requested_type="all")
        limited_visits = self._limit_visit_groups_for_summary(
            history.visits, max_items_per_category=max_items_per_category
        )
        counts = self._build_counts(history.visits)

        return PatientHistorySummaryResponse(
            patient_id=history.patient_id,
            patient_uuid=history.patient_uuid,
            summary=self._build_summary_text(
                counts=counts,
                visits=limited_visits,
                max_items_per_category=max_items_per_category,
            ),
            max_items_per_category=max_items_per_category,
            counts=counts,
            visits=limited_visits,
        )


patient_history = PatientHistoryCRUD()
