"""
CRUD operations for chief complaint notes.
"""

import uuid
from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.encounter import Encounter
from app.models.encounter_provider import EncounterProvider
from app.models.obs import Obs
from app.models.visit import Visit
from app.schemas.chief_complaint import (
    ChiefComplaintCreate,
    ChiefComplaintUpdate,
    ChiefComplaintVoid,
    ChiefComplaintObsItem,
    ChiefComplaintGroupResponse,
    ChiefComplaintVisitResponse,
)
from app.config import settings


class ChiefComplaintError(Exception):
    """Raised for known chief complaint business-rule violations."""

    def __init__(self, code: str, status: int = 404):
        self.code = code
        self.status = status
        super().__init__(code)


class ChiefComplaintCRUD:
    """CRUD for chief complaint obs groups."""

    # ------------------------------------------------------------------
    # Helpers shared with physical exam pattern
    # ------------------------------------------------------------------

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
            raise ChiefComplaintError("visit_identifier_required", status=400)

        if not visit:
            raise ChiefComplaintError("visit_not_found")
        return visit

    def _assert_visit_active(self, visit: Visit) -> None:
        if visit.date_stopped is not None:
            raise ChiefComplaintError("visit_not_active")

    def _get_or_create_encounter(
        self, db: Session, visit: Visit, creator: int, location_id: int
    ) -> Tuple[Encounter, bool]:
        existing = (
            db.query(Encounter)
            .filter(
                Encounter.visit_id == visit.visit_id,
                Encounter.encounter_type == settings.consultation_encounter_type_id,
                Encounter.voided == False,
            )
            .first()
        )
        if existing:
            return existing, False

        now = datetime.utcnow()
        encounter = Encounter(
            encounter_type=settings.consultation_encounter_type_id,
            patient_id=visit.patient_id,
            location_id=location_id,
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
        already_linked = (
            db.query(EncounterProvider)
            .filter(
                EncounterProvider.encounter_id == encounter.encounter_id,
                EncounterProvider.provider_id == provider_id,
                EncounterProvider.voided == False,
            )
            .first()
        )
        if already_linked:
            return

        now = datetime.utcnow()
        ep = EncounterProvider(
            encounter_id=encounter.encounter_id,
            provider_id=provider_id,
            encounter_role_id=encounter_role_id,
            creator=creator,
            date_created=now,
            voided=False,
            uuid=str(uuid.uuid4()),
        )
        db.add(ep)
        db.flush()

    def _make_obs(
        self,
        db: Session,
        encounter: Encounter,
        concept_id: int,
        creator: int,
        location_id: int,
        obs_datetime: datetime,
        obs_group_id: Optional[int] = None,
        value_coded: Optional[int] = None,
        value_text: Optional[str] = None,
        value_numeric: Optional[float] = None,
        comments: Optional[str] = None,
        form_namespace_and_path: Optional[str] = None,
    ) -> Obs:
        obs = Obs(
            person_id=encounter.patient_id,
            concept_id=concept_id,
            encounter_id=encounter.encounter_id,
            obs_datetime=obs_datetime,
            location_id=location_id,
            obs_group_id=obs_group_id,
            value_coded=value_coded,
            value_text=value_text,
            value_numeric=value_numeric,
            comments=comments,
            creator=creator,
            date_created=datetime.utcnow(),
            voided=False,
            status="FINAL",
            uuid=str(uuid.uuid4()),
            form_namespace_and_path=form_namespace_and_path,
        )
        db.add(obs)
        db.flush()
        return obs

    def _concept_name(self, db: Session, concept_id: Optional[int]) -> Optional[str]:
        if concept_id is None:
            return None
        row = db.execute(
            text(
                "SELECT name FROM concept_name "
                "WHERE concept_id = :cid AND locale = 'en' "
                "AND concept_name_type = 'FULLY_SPECIFIED' AND voided = 0 LIMIT 1"
            ),
            {"cid": concept_id},
        ).fetchone()
        return row[0] if row else None

    def _encounter_uuid(self, db: Session, encounter_id: int) -> str:
        row = db.execute(
            text("SELECT uuid FROM encounter WHERE encounter_id = :eid LIMIT 1"),
            {"eid": encounter_id},
        ).fetchone()
        return row[0] if row else ""

    def _creator_name(self, db: Session, creator_id: Optional[int]) -> Optional[str]:
        if creator_id is None:
            return None
        row = db.execute(
            text(
                "SELECT CONCAT_WS(' ', pn.given_name, pn.family_name) "
                "FROM users u "
                "LEFT JOIN person_name pn "
                "  ON pn.person_id = u.person_id "
                "  AND pn.preferred = 1 "
                "  AND pn.voided = 0 "
                "WHERE u.user_id = :uid "
                "LIMIT 1"
            ),
            {"uid": creator_id},
        ).fetchone()
        return row[0] if row and row[0] else None

    def _obs_to_item(self, db: Session, obs: Obs) -> ChiefComplaintObsItem:
        return ChiefComplaintObsItem(
            obs_id=obs.obs_id,
            uuid=obs.uuid,
            concept_id=obs.concept_id,
            concept_name=self._concept_name(db, obs.concept_id),
            value_coded=obs.value_coded,
            value_coded_name=self._concept_name(db, obs.value_coded),
            value_text=obs.value_text,
            value_numeric=obs.value_numeric,
            obs_datetime=obs.obs_datetime,
            comments=obs.comments,
            creator_id=obs.creator,
            creator_name=self._creator_name(db, obs.creator),
        )

    def _hydrate_group(
        self, db: Session, group_obs: Obs, encounter: Encounter, visit: Visit
    ) -> ChiefComplaintGroupResponse:
        """Build a ChiefComplaintGroupResponse from a group obs and its children."""
        children = (
            db.query(Obs)
            .filter(Obs.obs_group_id == group_obs.obs_id, Obs.voided == False)
            .all()
        )

        complaint_obs = None
        duration_obs = None
        duration_unit_obs = None
        hpi_obs = None

        for child in children:
            if child.concept_id in (
                settings.cc_coded_concept_id,
                settings.cc_text_concept_id,
            ):
                complaint_obs = self._obs_to_item(db, child)
            elif child.concept_id == settings.cc_duration_concept_id:
                duration_obs = self._obs_to_item(db, child)
            elif child.concept_id == settings.cc_duration_unit_concept_id:
                duration_unit_obs = self._obs_to_item(db, child)

        hpi_obs_record = (
            db.query(Obs)
            .filter(
                Obs.encounter_id == group_obs.encounter_id,
                Obs.concept_id == settings.cc_hpi_concept_id,
                Obs.obs_group_id == None,
                Obs.voided == False,
            )
            .order_by(Obs.obs_datetime.desc())
            .first()
        )
        if hpi_obs_record:
            hpi_obs = self._obs_to_item(db, hpi_obs_record)

        enc_uuid = self._encounter_uuid(db, encounter.encounter_id)

        return ChiefComplaintGroupResponse(
            group_obs_id=group_obs.obs_id,
            group_uuid=group_obs.uuid,
            encounter_id=encounter.encounter_id,
            encounter_uuid=enc_uuid,
            visit_id=visit.visit_id,
            obs_datetime=group_obs.obs_datetime,
            complaint=complaint_obs,
            duration=duration_obs,
            duration_unit=duration_unit_obs,
            hpi=hpi_obs,
        )

    # ------------------------------------------------------------------
    # Public CRUD methods
    # ------------------------------------------------------------------

    def create_complaint(
        self, db: Session, payload: ChiefComplaintCreate
    ) -> ChiefComplaintGroupResponse:
        visit = self._resolve_visit(db, payload.visit_id, payload.visit_uuid)
        self._assert_visit_active(visit)
        encounter, _ = self._get_or_create_encounter(
            db, visit, payload.creator, payload.location_id
        )

        if payload.provider_id:
            self._link_provider(
                db,
                encounter,
                payload.provider_id,
                payload.encounter_role_id or settings.consultation_encounter_role_id,
                payload.creator,
            )

        c = payload.complaint
        obs_dt = c.obs_datetime or payload.obs_datetime or datetime.utcnow()

        group = self._make_obs(
            db,
            encounter,
            settings.cc_group_concept_id,
            payload.creator,
            payload.location_id,
            obs_dt,
            form_namespace_and_path=settings.cc_form_group,
        )

        complaint_concept_id = (
            settings.cc_coded_concept_id
            if c.value_coded
            else settings.cc_text_concept_id
        )
        self._make_obs(
            db,
            encounter,
            complaint_concept_id,
            payload.creator,
            payload.location_id,
            obs_dt,
            obs_group_id=group.obs_id,
            value_coded=c.value_coded,
            value_text=c.value_text,
            comments=c.comments,
            form_namespace_and_path=settings.cc_form_complaint,
        )

        if c.duration_value is not None:
            self._make_obs(
                db,
                encounter,
                settings.cc_duration_concept_id,
                payload.creator,
                payload.location_id,
                obs_dt,
                obs_group_id=group.obs_id,
                value_numeric=c.duration_value,
                form_namespace_and_path=settings.cc_form_duration,
            )
            self._make_obs(
                db,
                encounter,
                settings.cc_duration_unit_concept_id,
                payload.creator,
                payload.location_id,
                obs_dt,
                obs_group_id=group.obs_id,
                value_coded=c.duration_unit_coded,
                form_namespace_and_path=settings.cc_form_duration_unit,
            )

        if payload.hpi:
            self._make_obs(
                db,
                encounter,
                settings.cc_hpi_concept_id,
                payload.creator,
                payload.location_id,
                obs_dt,
                value_text=payload.hpi,
                form_namespace_and_path=settings.cc_form_hpi,
            )

        db.commit()
        db.refresh(group)

        return self._hydrate_group(db, group, encounter, visit)

    def get_complaints_by_visit(
        self,
        db: Session,
        visit_id: Optional[int] = None,
        visit_uuid: Optional[str] = None,
    ) -> ChiefComplaintVisitResponse:
        visit = self._resolve_visit(db, visit_id, visit_uuid)

        encounter = (
            db.query(Encounter)
            .filter(
                Encounter.visit_id == visit.visit_id,
                Encounter.encounter_type == settings.consultation_encounter_type_id,
                Encounter.voided == False,
            )
            .first()
        )

        if not encounter:
            return ChiefComplaintVisitResponse(
                encounter_id=0,
                encounter_uuid="",
                visit_id=visit.visit_id,
                complaints=[],
            )

        groups = (
            db.query(Obs)
            .filter(
                Obs.encounter_id == encounter.encounter_id,
                Obs.concept_id == settings.cc_group_concept_id,
                Obs.obs_group_id == None,
                Obs.voided == False,
            )
            .order_by(Obs.obs_datetime.desc())
            .all()
        )

        complaints = [self._hydrate_group(db, g, encounter, visit) for g in groups]
        enc_uuid = self._encounter_uuid(db, encounter.encounter_id)

        return ChiefComplaintVisitResponse(
            encounter_id=encounter.encounter_id,
            encounter_uuid=enc_uuid,
            visit_id=visit.visit_id,
            complaints=complaints,
        )

    def get_complaint_group(
        self, db: Session, group_obs_id: int
    ) -> ChiefComplaintGroupResponse:
        group_obs = (
            db.query(Obs)
            .filter(
                Obs.obs_id == group_obs_id,
                Obs.concept_id == settings.cc_group_concept_id,
                Obs.voided == False,
            )
            .first()
        )
        if not group_obs:
            raise ChiefComplaintError("complaint_group_not_found")

        encounter = (
            db.query(Encounter)
            .filter(Encounter.encounter_id == group_obs.encounter_id)
            .first()
        )
        if not encounter:
            raise ChiefComplaintError("encounter_not_found")

        visit = db.query(Visit).filter(Visit.visit_id == encounter.visit_id).first()
        if not visit:
            raise ChiefComplaintError("visit_not_found")

        return self._hydrate_group(db, group_obs, encounter, visit)

    def update_complaint_group(
        self, db: Session, group_obs_id: int, payload: ChiefComplaintUpdate
    ) -> ChiefComplaintGroupResponse:
        group_obs = (
            db.query(Obs)
            .filter(
                Obs.obs_id == group_obs_id,
                Obs.concept_id == settings.cc_group_concept_id,
                Obs.voided == False,
            )
            .first()
        )
        if not group_obs:
            raise ChiefComplaintError("complaint_group_not_found")

        encounter = (
            db.query(Encounter)
            .filter(Encounter.encounter_id == group_obs.encounter_id)
            .first()
        )
        if encounter and encounter.visit_id:
            visit = db.query(Visit).filter(Visit.visit_id == encounter.visit_id).first()
            if visit:
                self._assert_visit_active(visit)

        children = (
            db.query(Obs)
            .filter(Obs.obs_group_id == group_obs_id, Obs.voided == False)
            .all()
        )

        now = datetime.utcnow()

        for child in children:
            if child.concept_id in (
                settings.cc_coded_concept_id,
                settings.cc_text_concept_id,
            ):
                if payload.value_coded is not None:
                    child.concept_id = settings.cc_coded_concept_id
                    child.value_coded = payload.value_coded
                    child.value_text = None
                elif payload.value_text is not None:
                    child.concept_id = settings.cc_text_concept_id
                    child.value_text = payload.value_text
                    child.value_coded = None
                if payload.comments is not None:
                    child.comments = payload.comments
                if payload.obs_datetime is not None:
                    child.obs_datetime = payload.obs_datetime
                if payload.editor is not None:
                    child.changed_by = payload.editor
                    child.date_changed = now

            elif child.concept_id == settings.cc_duration_concept_id:
                if payload.duration_value is not None:
                    child.value_numeric = payload.duration_value
                if payload.obs_datetime is not None:
                    child.obs_datetime = payload.obs_datetime
                if payload.editor is not None:
                    child.changed_by = payload.editor
                    child.date_changed = now

            elif child.concept_id == settings.cc_duration_unit_concept_id:
                if payload.duration_unit_coded is not None:
                    child.value_coded = payload.duration_unit_coded
                if payload.obs_datetime is not None:
                    child.obs_datetime = payload.obs_datetime
                if payload.editor is not None:
                    child.changed_by = payload.editor
                    child.date_changed = now

        if payload.obs_datetime is not None:
            group_obs.obs_datetime = payload.obs_datetime
        if payload.editor is not None:
            group_obs.changed_by = payload.editor
            group_obs.date_changed = now

        if payload.hpi is not None and encounter:
            hpi_obs = (
                db.query(Obs)
                .filter(
                    Obs.encounter_id == group_obs.encounter_id,
                    Obs.concept_id == settings.cc_hpi_concept_id,
                    Obs.obs_group_id == None,
                    Obs.voided == False,
                )
                .first()
            )
            if hpi_obs:
                hpi_obs.value_text = payload.hpi
                if payload.editor is not None:
                    hpi_obs.changed_by = payload.editor
                    hpi_obs.date_changed = now

        db.commit()
        db.refresh(group_obs)

        encounter = (
            db.query(Encounter)
            .filter(Encounter.encounter_id == group_obs.encounter_id)
            .first()
        )
        visit = db.query(Visit).filter(Visit.visit_id == encounter.visit_id).first()

        return self._hydrate_group(db, group_obs, encounter, visit)

    def delete_complaint_group(
        self, db: Session, group_obs_id: int, payload: ChiefComplaintVoid
    ) -> None:
        group_obs = (
            db.query(Obs)
            .filter(
                Obs.obs_id == group_obs_id,
                Obs.concept_id == settings.cc_group_concept_id,
                Obs.voided == False,
            )
            .first()
        )
        if not group_obs:
            raise ChiefComplaintError("complaint_group_not_found")

        encounter = (
            db.query(Encounter)
            .filter(Encounter.encounter_id == group_obs.encounter_id)
            .first()
        )
        if encounter and encounter.visit_id:
            visit = db.query(Visit).filter(Visit.visit_id == encounter.visit_id).first()
            if visit:
                self._assert_visit_active(visit)

        children = (
            db.query(Obs)
            .filter(Obs.obs_group_id == group_obs_id, Obs.voided == False)
            .all()
        )

        now = datetime.utcnow()
        for child in children:
            child.voided = True
            child.date_voided = now
            if payload.void_reason is not None:
                child.void_reason = payload.void_reason
            if payload.voided_by is not None:
                child.voided_by = payload.voided_by

        group_obs.voided = True
        group_obs.date_voided = now
        if payload.void_reason is not None:
            group_obs.void_reason = payload.void_reason
        if payload.voided_by is not None:
            group_obs.voided_by = payload.voided_by

        hpi_obs = (
            db.query(Obs)
            .filter(
                Obs.encounter_id == group_obs.encounter_id,
                Obs.concept_id == settings.cc_hpi_concept_id,
                Obs.obs_group_id == None,
                Obs.voided == False,
            )
            .first()
        )
        if hpi_obs:
            hpi_obs.voided = True
            hpi_obs.date_voided = now
            if payload.void_reason is not None:
                hpi_obs.void_reason = payload.void_reason
            if payload.voided_by is not None:
                hpi_obs.voided_by = payload.voided_by

        db.commit()


chief_complaint = ChiefComplaintCRUD()
