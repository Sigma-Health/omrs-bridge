"""
CRUD operations for vitals/observations queries.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import get_vital_signs_concept_ids, settings
from app.models.encounter import Encounter
from app.models.encounter_provider import EncounterProvider
from app.models.obs import Obs
from app.models.visit import Visit
from app.sql.vitals_sql import (
    get_vitals_by_visit_sql,
    get_vitals_by_visit_uuid_sql,
    get_vitals_count_by_visit_sql,
    get_vitals_grouped_by_type_sql,
)
from app.sql.vitals_simple_sql import (
    get_vitals_simple_by_visit_sql,
    get_vitals_simple_count_by_visit_sql,
)
from app.sql.vitals_targeted_sql import (
    get_vitals_targeted_by_visit_sql,
    get_vitals_targeted_count_by_visit_sql,
)
from app.sql.vitals_comprehensive_sql import (
    get_vitals_comprehensive_by_visit_sql,
    get_vitals_comprehensive_count_by_visit_sql,
)
from app.schemas.vitals import (
    VitalSign,
    VitalsResponse,
    VisitVitals,
    VitalsGroupedResponse,
    VitalsByType,
    PatientVitalsInfo,
    EncounterVitalsInfo,
    VisitVitalCreate,
    VisitVitalCreateResponse,
    VitalMeasurementCreate,
)


class VitalsError(Exception):
    """Raised for known vitals business-rule violations."""

    def __init__(self, code: str, status: int = 404):
        self.code = code
        self.status = status
        super().__init__(code)


class VitalsCRUD:
    """
    CRUD operations for vitals queries.
    """

    def _resolve_visit(
        self, db: Session, visit_id: Optional[int], visit_uuid: Optional[str]
    ) -> Visit:
        if visit_id:
            visit = (
                db.query(Visit)
                .filter(Visit.visit_id == visit_id, Visit.voided == False)
                .first()
            )
        elif visit_uuid:
            visit = (
                db.query(Visit)
                .filter(Visit.uuid == visit_uuid, Visit.voided == False)
                .first()
            )
        else:
            raise VitalsError("visit_identifier_required", status=400)

        if not visit:
            raise VitalsError("visit_not_found")

        return visit

    def _assert_visit_active(self, visit: Visit) -> None:
        if visit.date_stopped is not None:
            raise VitalsError("visit_not_active")

    def _get_or_create_encounter(
        self, db: Session, visit: Visit, creator: int, location_id: Optional[int]
    ) -> Tuple[Encounter, bool]:
        existing = (
            db.query(Encounter)
            .filter(
                Encounter.visit_id == visit.visit_id,
                Encounter.encounter_type == settings.consultation_encounter_type_id,
                Encounter.voided == False,
            )
            .order_by(Encounter.encounter_datetime.desc(), Encounter.encounter_id.desc())
            .first()
        )

        if existing:
            return existing, False

        now = datetime.utcnow()
        encounter = Encounter(
            encounter_type=settings.consultation_encounter_type_id,
            patient_id=visit.patient_id,
            location_id=location_id or visit.location_id,
            encounter_datetime=now,
            creator=creator,
            date_created=now,
            voided=False,
            visit_id=visit.visit_id,
            uuid=str(uuid.uuid4()),
        )
        db.add(encounter)
        db.flush()
        return encounter, True

    def _link_provider(
        self,
        db: Session,
        encounter: Encounter,
        provider_id: int,
        encounter_role_id: int,
        creator: int,
    ) -> None:
        now = datetime.utcnow()
        encounter_provider = EncounterProvider(
            encounter_id=encounter.encounter_id,
            provider_id=provider_id,
            encounter_role_id=encounter_role_id,
            creator=creator,
            date_created=now,
            voided=False,
            uuid=str(uuid.uuid4()),
        )
        db.add(encounter_provider)
        db.flush()

    def _create_vital_obs(
        self,
        db: Session,
        encounter: Encounter,
        payload: VisitVitalCreate,
        vital: VitalMeasurementCreate,
        visit_location_id: Optional[int],
    ) -> Obs:
        now = datetime.utcnow()
        obs = Obs(
            person_id=encounter.patient_id,
            concept_id=vital.concept_id,
            encounter_id=encounter.encounter_id,
            order_id=vital.order_id,
            obs_datetime=vital.obs_datetime or now,
            location_id=vital.location_id or payload.location_id or visit_location_id,
            obs_group_id=vital.obs_group_id,
            value_coded=vital.value_coded,
            value_datetime=vital.value_datetime,
            value_numeric=vital.value_numeric,
            value_modifier=vital.value_modifier,
            value_text=vital.value_text,
            comments=vital.comments,
            creator=payload.creator,
            date_created=now,
            voided=False,
            uuid=str(uuid.uuid4()),
            form_namespace_and_path=vital.form_namespace_and_path,
            status=vital.status or "FINAL",
            interpretation=vital.interpretation,
        )
        db.add(obs)
        db.flush()
        return obs

    def _hydrate_obs(self, db: Session, obs: Obs) -> VitalSign:
        row = db.execute(
            text(
                "SELECT "
                "  cn.name AS concept_name, "
                "  coded_cn.name AS value_coded_name, "
                "  e.uuid AS encounter_uuid, "
                "  e.encounter_datetime AS encounter_datetime, "
                "  v.uuid AS visit_uuid, "
                "  p.patient_id AS patient_id, "
                "  pt.uuid AS patient_uuid, "
                "  CONCAT_WS(' ', patient_name.prefix, patient_name.given_name, patient_name.middle_name, patient_name.family_name) AS patient_name, "
                "  CONCAT_WS(' ', creator_name.given_name, creator_name.family_name) AS creator_name "
                "FROM obs o "
                "LEFT JOIN concept_name cn "
                "  ON cn.concept_id = o.concept_id "
                "  AND cn.locale = 'en' "
                "  AND cn.concept_name_type = 'FULLY_SPECIFIED' "
                "  AND cn.voided = 0 "
                "LEFT JOIN concept_name coded_cn "
                "  ON coded_cn.concept_id = o.value_coded "
                "  AND coded_cn.locale = 'en' "
                "  AND coded_cn.concept_name_type = 'FULLY_SPECIFIED' "
                "  AND coded_cn.voided = 0 "
                "LEFT JOIN encounter e ON e.encounter_id = o.encounter_id "
                "LEFT JOIN visit v ON v.visit_id = e.visit_id "
                "LEFT JOIN patient p ON p.patient_id = e.patient_id "
                "LEFT JOIN person pt ON pt.person_id = p.patient_id "
                "LEFT JOIN person_name patient_name "
                "  ON patient_name.person_id = p.patient_id "
                "  AND patient_name.preferred = 1 AND patient_name.voided = 0 "
                "LEFT JOIN users u ON u.user_id = o.creator "
                "LEFT JOIN person_name creator_name "
                "  ON creator_name.person_id = u.person_id "
                "  AND creator_name.preferred = 1 AND creator_name.voided = 0 "
                "WHERE o.obs_id = :obs_id"
            ),
            {"obs_id": obs.obs_id},
        ).fetchone()

        return VitalSign(
            obs_id=obs.obs_id,
            uuid=obs.uuid,
            obs_datetime=obs.obs_datetime,
            concept_id=obs.concept_id,
            concept_name=row.concept_name if row and row.concept_name else "Unknown",
            value_numeric=obs.value_numeric,
            value_text=obs.value_text,
            value_coded=obs.value_coded,
            value_coded_name=row.value_coded_name if row else None,
            value_datetime=obs.value_datetime,
            comments=obs.comments,
            status=obs.status,
            interpretation=obs.interpretation,
            patient_id=row.patient_id if row else obs.person_id,
            patient_uuid=row.patient_uuid if row else "",
            patient_name=row.patient_name if row and row.patient_name else "Unknown",
            encounter_id=obs.encounter_id,
            encounter_uuid=row.encounter_uuid if row else "",
            encounter_datetime=row.encounter_datetime if row else None,
            visit_uuid=row.visit_uuid if row else "",
            creator_id=obs.creator,
            creator_name=row.creator_name if row else None,
        )

    def create_vitals_for_visit(
        self,
        db: Session,
        payload: VisitVitalCreate,
        visit_id: Optional[int] = None,
        visit_uuid: Optional[str] = None,
    ) -> VisitVitalCreateResponse:
        visit = self._resolve_visit(db, visit_id, visit_uuid)
        self._assert_visit_active(visit)
        encounter, created = self._get_or_create_encounter(
            db, visit, payload.creator, payload.location_id
        )

        if payload.provider_id:
            already_linked = (
                db.query(EncounterProvider)
                .filter(
                    EncounterProvider.encounter_id == encounter.encounter_id,
                    EncounterProvider.provider_id == payload.provider_id,
                    EncounterProvider.voided == False,
                )
                .first()
            )
            if not already_linked:
                self._link_provider(
                    db,
                    encounter,
                    payload.provider_id,
                    payload.encounter_role_id
                    or settings.consultation_encounter_role_id,
                    payload.creator,
                )

        obs_list = [
            self._create_vital_obs(db, encounter, payload, vital, visit.location_id)
            for vital in payload.vitals
        ]

        db.commit()
        db.refresh(encounter)
        for obs in obs_list:
            db.refresh(obs)

        return VisitVitalCreateResponse(
            encounter_id=encounter.encounter_id,
            encounter_uuid=encounter.uuid,
            visit_id=visit.visit_id,
            visit_uuid=visit.uuid,
            created=created,
            vitals=[self._hydrate_obs(db, obs) for obs in obs_list],
        )

    def get_vitals_by_visit(
        self, db: Session, visit_id: int, skip: int = 0, limit: int = 100
    ) -> VisitVitals:
        """
        Get vitals for a specific visit.

        Args:
            db: Database session
            visit_id: ID of the visit
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            VisitVitals with visit info and vitals
        """
        concept_ids = get_vital_signs_concept_ids()
        params = {"visit_id": visit_id, "skip": skip, "limit": limit}

        result = db.execute(
            text(get_vitals_comprehensive_by_visit_sql(concept_ids)), params
        )
        vitals = self._process_vitals_results(result)

        if not vitals:
            result = db.execute(
                text(get_vitals_targeted_by_visit_sql(concept_ids)), params
            )
            vitals = self._process_vitals_results(result)

        if not vitals:
            result = db.execute(text(get_vitals_by_visit_sql(concept_ids)), params)
            vitals = self._process_vitals_results(result)

        if not vitals:
            result = db.execute(
                text(get_vitals_simple_by_visit_sql(concept_ids)), params
            )
            vitals = self._process_vitals_results(result)

        patient_info = None
        encounter_info = None

        if vitals:
            first_vital = vitals[0]
            patient_info = PatientVitalsInfo(
                patient_id=getattr(first_vital, "patient_id", 0),
                uuid=getattr(first_vital, "patient_uuid", ""),
                name=getattr(first_vital, "patient_name", "Unknown"),
            )
            encounter_info = EncounterVitalsInfo(
                encounter_id=getattr(first_vital, "encounter_id", 0),
                uuid=getattr(first_vital, "encounter_uuid", ""),
                encounter_datetime=getattr(first_vital, "encounter_datetime", None),
            )

        count_result = db.execute(
            text(get_vitals_comprehensive_count_by_visit_sql(concept_ids)),
            {"visit_id": visit_id},
        )
        total_count = count_result.scalar()

        if total_count == 0:
            count_result = db.execute(
                text(get_vitals_targeted_count_by_visit_sql(concept_ids)),
                {"visit_id": visit_id},
            )
            total_count = count_result.scalar()

        if total_count == 0:
            count_result = db.execute(
                text(get_vitals_count_by_visit_sql(concept_ids)),
                {"visit_id": visit_id},
            )
            total_count = count_result.scalar()

        if total_count == 0:
            count_result = db.execute(
                text(get_vitals_simple_count_by_visit_sql(concept_ids)),
                {"visit_id": visit_id},
            )
            total_count = count_result.scalar()

        return VisitVitals(
            visit_id=visit_id,
            visit_uuid=getattr(vitals[0], "visit_uuid", "") if vitals else "",
            patient=patient_info
            or PatientVitalsInfo(patient_id=0, uuid="", name="Unknown"),
            encounter=encounter_info
            or EncounterVitalsInfo(
                encounter_id=0,
                uuid="",
                encounter_datetime=None,
            ),
            vitals=vitals,
            total_count=total_count,
        )

    def get_vitals_by_visit_uuid(
        self, db: Session, visit_uuid: str, skip: int = 0, limit: int = 100
    ) -> VisitVitals:
        """
        Get vitals for a specific visit by visit UUID.

        Args:
            db: Database session
            visit_uuid: UUID of the visit
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            VisitVitals with visit info and vitals
        """
        # First get the visit_id from the UUID
        visit_query = """
        SELECT visit_id FROM visit WHERE uuid = :visit_uuid AND voided = 0
        """
        result = db.execute(text(visit_query), {"visit_uuid": visit_uuid})
        visit_row = result.fetchone()

        if not visit_row:
            raise ValueError(f"Visit with UUID {visit_uuid} not found")

        visit_id = visit_row[0]

        # Use the existing method with visit_id
        return self.get_vitals_by_visit(
            db=db, visit_id=visit_id, skip=skip, limit=limit
        )

    def get_vitals_grouped_by_type(
        self, db: Session, visit_id: int, skip: int = 0, limit: int = 100
    ) -> VitalsGroupedResponse:
        """
        Get vitals grouped by concept type for a specific visit.

        Args:
            db: Database session
            visit_id: ID of the visit
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            VitalsGroupedResponse with vitals grouped by type
        """
        concept_ids = get_vital_signs_concept_ids()
        params = {"visit_id": visit_id, "skip": skip, "limit": limit}

        result = db.execute(text(get_vitals_grouped_by_type_sql(concept_ids)), params)
        vitals = self._process_vitals_results(result)

        # Group vitals by concept name
        vitals_by_type = {}
        for vital in vitals:
            concept_name = vital.concept_name
            if concept_name not in vitals_by_type:
                vitals_by_type[concept_name] = []
            vitals_by_type[concept_name].append(vital)

        # Convert to VitalsByType objects
        vitals_by_type_list = []
        for concept_name, vital_list in vitals_by_type.items():
            vitals_by_type_list.append(
                VitalsByType(
                    vital_type=concept_name,
                    concept_id=vital_list[0].concept_id,
                    vitals=vital_list,
                )
            )

        # Get visit and patient info from first vital if available
        patient_info = None
        encounter_info = None

        if vitals:
            first_vital = vitals[0]
            patient_info = PatientVitalsInfo(
                patient_id=0,  # Would need to be populated from query
                uuid="",
                name="Unknown",
            )
            encounter_info = EncounterVitalsInfo(
                encounter_id=0,
                uuid="",
                encounter_datetime=first_vital.obs_datetime,
            )

        count_result = db.execute(
            text(get_vitals_count_by_visit_sql(concept_ids)), {"visit_id": visit_id}
        )
        total_count = count_result.scalar()

        return VitalsGroupedResponse(
            visit_id=visit_id,
            visit_uuid=getattr(vitals[0], "visit_uuid", "") if vitals else "",
            patient=patient_info
            or PatientVitalsInfo(patient_id=0, uuid="", name="Unknown"),
            encounter=encounter_info
            or EncounterVitalsInfo(
                encounter_id=0,
                uuid="",
                encounter_datetime=None,
            ),
            vitals_by_type=vitals_by_type_list,
            total_count=total_count,
        )

    def _process_vitals_results(self, result) -> List[VitalSign]:
        """
        Process raw SQL results into VitalSign objects.
        """
        vitals = []

        for row in result:
            # Build patient name from components
            patient_name_parts = []
            if hasattr(row, "patient_prefix") and row.patient_prefix:
                patient_name_parts.append(row.patient_prefix)
            if hasattr(row, "patient_given_name") and row.patient_given_name:
                patient_name_parts.append(row.patient_given_name)
            if hasattr(row, "patient_middle_name") and row.patient_middle_name:
                patient_name_parts.append(row.patient_middle_name)
            if hasattr(row, "patient_family_name") and row.patient_family_name:
                patient_name_parts.append(row.patient_family_name)
            if hasattr(row, "patient_family_name2") and row.patient_family_name2:
                patient_name_parts.append(row.patient_family_name2)
            if (
                hasattr(row, "patient_family_name_suffix")
                and row.patient_family_name_suffix
            ):
                patient_name_parts.append(row.patient_family_name_suffix)

            patient_name = (
                " ".join(patient_name_parts) if patient_name_parts else "Unknown"
            )

            # Build vital sign with additional context
            vital = VitalSign(
                obs_id=row.obs_id,
                uuid=row.obs_uuid,
                obs_datetime=row.obs_datetime,
                concept_id=row.concept_id,
                concept_name=row.concept_name,
                value_numeric=row.value_numeric,
                value_text=row.value_text,
                value_coded=row.value_coded,
                value_coded_name=row.value_coded_name,
                value_datetime=row.value_datetime,
                comments=row.comments,
                status=row.status,
                interpretation=row.interpretation,
                # Additional context fields
                patient_id=getattr(row, "patient_id", 0),
                patient_uuid=getattr(row, "patient_uuid", ""),
                patient_name=patient_name,
                encounter_id=getattr(row, "encounter_id", 0),
                encounter_uuid=getattr(row, "encounter_uuid", ""),
                encounter_datetime=getattr(row, "encounter_datetime", None),
                visit_uuid=getattr(row, "visit_uuid", ""),
                creator_id=getattr(row, "creator_id", None),
                creator_name=getattr(row, "creator_name", None),
            )

            vitals.append(vital)

        return vitals
