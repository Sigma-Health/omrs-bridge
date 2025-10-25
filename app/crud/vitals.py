"""
CRUD operations for vitals/observations queries.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.sql.vitals_sql import (
    get_vitals_by_visit_sql,
    get_vitals_by_visit_uuid_sql,
    get_vitals_count_by_visit_sql,
    get_vitals_grouped_by_type_sql,
)
from app.schemas.vitals import (
    VitalSign,
    VitalsResponse,
    VisitVitals,
    VitalsGroupedResponse,
    VitalsByType,
    PatientVitalsInfo,
    EncounterVitalsInfo,
)


class VitalsCRUD:
    """
    CRUD operations for vitals queries.
    """

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
        sql = get_vitals_by_visit_sql()
        params = {"visit_id": visit_id, "skip": skip, "limit": limit}

        result = db.execute(text(sql), params)
        vitals = self._process_vitals_results(result)

        # Get visit and patient info from first vital if available
        visit_info = None
        patient_info = None
        encounter_info = None

        if vitals:
            first_vital = vitals[0]
            # Extract visit info from the first vital's encounter
            visit_info = {
                "visit_id": visit_id,
                "visit_uuid": first_vital.obs_datetime,  # This would need to be visit_uuid from query
            }
            patient_info = PatientVitalsInfo(
                patient_id=first_vital.obs_id,  # This would need to be patient_id from query
                uuid="",  # Would need to be populated from query
                name="Unknown",  # Would need to be populated from query
            )
            encounter_info = EncounterVitalsInfo(
                encounter_id=0,  # Would need to be populated from query
                uuid="",
                encounter_datetime=first_vital.obs_datetime,
            )

        # Get total count
        count_sql = get_vitals_count_by_visit_sql()
        count_result = db.execute(text(count_sql), {"visit_id": visit_id})
        total_count = count_result.scalar()

        return VisitVitals(
            visit_id=visit_id,
            visit_uuid="",  # Would need to be populated
            patient=patient_info
            or PatientVitalsInfo(patient_id=0, uuid="", name="Unknown"),
            encounter=encounter_info
            or EncounterVitalsInfo(
                encounter_id=0,
                uuid="",
                encounter_datetime=first_vital.obs_datetime if vitals else None,
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
        sql = get_vitals_grouped_by_type_sql()
        params = {"visit_id": visit_id, "skip": skip, "limit": limit}

        result = db.execute(text(sql), params)
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

        # Get total count
        count_sql = get_vitals_count_by_visit_sql()
        count_result = db.execute(text(count_sql), {"visit_id": visit_id})
        total_count = count_result.scalar()

        return VitalsGroupedResponse(
            visit_id=visit_id,
            visit_uuid="",  # Would need to be populated
            patient=patient_info
            or PatientVitalsInfo(patient_id=0, uuid="", name="Unknown"),
            encounter=encounter_info
            or EncounterVitalsInfo(
                encounter_id=0,
                uuid="",
                encounter_datetime=vitals[0].obs_datetime if vitals else None,
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
            # Build vital sign
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
            )

            vitals.append(vital)

        return vitals
