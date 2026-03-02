"""
CRUD operations for physical examination notes.
"""

import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.encounter import Encounter
from app.models.encounter_provider import EncounterProvider
from app.models.obs import Obs
from app.models.visit import Visit
from app.schemas.physical_exam import (
    PhysicalExamCreate,
    ExamNoteInput,
    ExamNoteUpdate,
    PhysicalExamResponse,
)
from app.schemas.vitals import VitalSign
from app.config import settings


class PhysicalExamCRUD:
    """CRUD for creating physical examination notes."""

    def _resolve_visit(
        self, db: Session, visit_id: Optional[int], visit_uuid: Optional[str]
    ) -> Visit:
        """Resolve and return the Visit, raising ValueError if not found."""
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
            raise ValueError("Either visit_id or visit_uuid must be provided")

        if not visit:
            identifier = visit_id or visit_uuid
            raise ValueError(f"Visit {identifier} not found")

        return visit

    def _assert_visit_active(self, visit: Visit) -> None:
        """Raise ValueError if the visit has been stopped."""
        if visit.date_stopped is not None:
            raise ValueError(f"Visit {visit.visit_id} is no longer active")

    def _get_or_create_encounter(
        self, db: Session, visit: Visit, creator: int, location_id: int
    ) -> Tuple[Encounter, bool]:
        """
        Return (encounter, created).
        Reuses an existing unvoided consultation encounter for the visit if one exists.
        """
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
        """Insert an encounter_provider row linking the provider to the encounter."""
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

    def _create_obs(
        self,
        db: Session,
        encounter: Encounter,
        note: ExamNoteInput,
        creator: int,
        location_id: int,
    ) -> Obs:
        """Insert a single obs record for an examination note."""
        concept_id = (
            note.concept_id if note.concept_id else settings.physical_exam_concept_id
        )
        now = datetime.utcnow()
        obs = Obs(
            person_id=encounter.patient_id,
            concept_id=concept_id,
            encounter_id=encounter.encounter_id,
            obs_datetime=note.obs_datetime or now,
            location_id=location_id,
            value_text=note.value_text,
            comments=note.comments,
            creator=creator,
            date_created=now,
            voided=False,
            status="FINAL",
            uuid=str(uuid.uuid4()),
        )
        db.add(obs)
        db.flush()
        return obs

    def _hydrate_obs(self, db: Session, obs: Obs, encounter: Encounter) -> VitalSign:
        """Fetch concept name and creator name, then build a VitalSign response."""
        concept_row = db.execute(
            text(
                "SELECT cn.name FROM concept_name cn "
                "WHERE cn.concept_id = :cid AND cn.locale = 'en' "
                "AND cn.concept_name_type = 'FULLY_SPECIFIED' AND cn.voided = 0 LIMIT 1"
            ),
            {"cid": obs.concept_id},
        ).fetchone()
        concept_name = concept_row[0] if concept_row else "Unknown"

        creator_row = db.execute(
            text(
                "SELECT CONCAT_WS(' ', pn.given_name, pn.family_name) "
                "FROM users u "
                "LEFT JOIN person_name pn ON u.person_id = pn.person_id "
                "    AND pn.preferred = 1 AND pn.voided = 0 "
                "WHERE u.user_id = :uid LIMIT 1"
            ),
            {"uid": obs.creator},
        ).fetchone()
        creator_name = creator_row[0] if creator_row else None

        encounter_uuid_row = db.execute(
            text("SELECT uuid FROM encounter WHERE encounter_id = :eid LIMIT 1"),
            {"eid": encounter.encounter_id},
        ).fetchone()
        encounter_uuid = encounter_uuid_row[0] if encounter_uuid_row else ""

        visit_uuid_row = db.execute(
            text("SELECT uuid FROM visit WHERE visit_id = :vid LIMIT 1"),
            {"vid": encounter.visit_id},
        ).fetchone()
        visit_uuid = visit_uuid_row[0] if visit_uuid_row else ""

        return VitalSign(
            obs_id=obs.obs_id,
            uuid=obs.uuid,
            obs_datetime=obs.obs_datetime,
            concept_id=obs.concept_id,
            concept_name=concept_name,
            value_text=obs.value_text,
            comments=obs.comments,
            status=obs.status,
            encounter_id=encounter.encounter_id,
            encounter_uuid=encounter_uuid,
            encounter_datetime=encounter.encounter_datetime,
            patient_id=encounter.patient_id,
            visit_uuid=visit_uuid,
            creator_id=obs.creator,
            creator_name=creator_name,
        )

    def create_exam_notes(self, db: Session, payload: PhysicalExamCreate):
        """
        Main entry point. Resolves visit, gets/creates encounter,
        creates all obs records, returns PhysicalExamResponse data.
        """
        visit = self._resolve_visit(db, payload.visit_id, payload.visit_uuid)
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
                    payload.encounter_role_id or 1,
                    payload.creator,
                )

        obs_list: List[Obs] = []
        for note in payload.notes:
            obs = self._create_obs(
                db, encounter, note, payload.creator, payload.location_id
            )
            obs_list.append(obs)

        db.commit()
        db.refresh(encounter)
        for obs in obs_list:
            db.refresh(obs)

        observations = [self._hydrate_obs(db, obs, encounter) for obs in obs_list]

        return PhysicalExamResponse(
            encounter_id=encounter.encounter_id,
            encounter_uuid=encounter.uuid,
            visit_id=visit.visit_id,
            created=created,
            observations=observations,
        )

    def get_exam_notes_by_visit(
        self, db: Session, visit_id: Optional[int], visit_uuid: Optional[str]
    ) -> PhysicalExamResponse:
        """
        Retrieve physical examination notes for a visit.
        Returns the consultation encounter and all obs matching PHYSICAL_EXAM_CONCEPT_ID.
        """
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
            return PhysicalExamResponse(
                encounter_id=0,
                encounter_uuid="",
                visit_id=visit.visit_id,
                created=False,
                observations=[],
            )

        obs_list = (
            db.query(Obs)
            .filter(
                Obs.encounter_id == encounter.encounter_id,
                Obs.concept_id == settings.physical_exam_concept_id,
                Obs.voided == False,
            )
            .order_by(Obs.obs_datetime.desc())
            .all()
        )

        observations = [self._hydrate_obs(db, obs, encounter) for obs in obs_list]

        return PhysicalExamResponse(
            encounter_id=encounter.encounter_id,
            encounter_uuid=encounter.uuid,
            visit_id=visit.visit_id,
            created=False,
            observations=observations,
        )

    def get_exam_note(self, db: Session, obs_id: int) -> VitalSign:
        """
        Retrieve a single physical exam obs by obs_id.
        Raises ValueError if not found or voided.
        """
        obs = db.query(Obs).filter(Obs.obs_id == obs_id, Obs.voided == False).first()
        if not obs:
            raise ValueError(f"Physical exam note {obs_id} not found")

        encounter = (
            db.query(Encounter)
            .filter(Encounter.encounter_id == obs.encounter_id)
            .first()
        )
        if not encounter:
            raise ValueError(f"Encounter for obs {obs_id} not found")

        return self._hydrate_obs(db, obs, encounter)

    def update_exam_note(
        self, db: Session, obs_id: int, payload: ExamNoteUpdate
    ) -> VitalSign:
        """
        Partially update a physical exam obs. Only provided fields are changed.
        Raises ValueError if not found or voided.
        """
        obs = db.query(Obs).filter(Obs.obs_id == obs_id, Obs.voided == False).first()
        if not obs:
            raise ValueError(f"Physical exam note {obs_id} not found")

        encounter = (
            db.query(Encounter)
            .filter(Encounter.encounter_id == obs.encounter_id)
            .first()
        )
        if encounter and encounter.visit_id:
            visit = db.query(Visit).filter(Visit.visit_id == encounter.visit_id).first()
            if visit:
                self._assert_visit_active(visit)

        if payload.value_text is not None:
            obs.value_text = payload.value_text
        if payload.comments is not None:
            obs.comments = payload.comments
        if payload.obs_datetime is not None:
            obs.obs_datetime = payload.obs_datetime

        db.commit()
        db.refresh(obs)

        if not encounter:
            encounter = (
                db.query(Encounter)
                .filter(Encounter.encounter_id == obs.encounter_id)
                .first()
            )

        return self._hydrate_obs(db, obs, encounter)

    def delete_exam_note(self, db: Session, obs_id: int) -> dict:
        """
        Void a physical exam obs by obs_id.
        Raises ValueError if not found or already voided.
        """
        obs = db.query(Obs).filter(Obs.obs_id == obs_id, Obs.voided == False).first()
        if not obs:
            raise ValueError(f"Physical exam note {obs_id} not found")

        encounter = (
            db.query(Encounter)
            .filter(Encounter.encounter_id == obs.encounter_id)
            .first()
        )
        if encounter and encounter.visit_id:
            visit = db.query(Visit).filter(Visit.visit_id == encounter.visit_id).first()
            if visit:
                self._assert_visit_active(visit)

        obs.voided = True
        obs.date_voided = datetime.utcnow()
        db.commit()

        return {
            "success": True,
            "obs_id": obs_id,
            "message": "Physical exam note voided successfully",
        }


physical_exam = PhysicalExamCRUD()
