"""
CRUD operations for diagnosis queries.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.sql.diagnosis_sql import (
    get_diagnoses_with_icd10_sql,
    get_diagnoses_by_visit_sql,
    get_diagnoses_count_sql,
)
from app.schemas.diagnosis import (
    DiagnosisObservation,
    DiagnosisResponse,
    VisitDiagnoses,
    ICD10Code,
    DiagnosisConcept,
    PatientInfo,
    EncounterInfo,
)


class DiagnosesCRUD:
    """
    CRUD operations for diagnosis queries.
    """

    def get_diagnoses(
        self, db: Session, skip: int = 0, limit: int = 100, **filters
    ) -> DiagnosisResponse:
        """
        Get diagnoses with ICD10 codes.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Additional filter parameters

        Returns:
            DiagnosisResponse with diagnoses and metadata
        """
        # Build WHERE clause
        where_conditions = []
        params = {"skip": skip, "limit": limit}

        if "visit_id" in filters:
            where_conditions.append("v.visit_id = :visit_id")
            params["visit_id"] = filters["visit_id"]

        if "patient_id" in filters:
            where_conditions.append("p.patient_id = :patient_id")
            params["patient_id"] = filters["patient_id"]

        if "encounter_id" in filters:
            where_conditions.append("e.encounter_id = :encounter_id")
            params["encounter_id"] = filters["encounter_id"]

        if "concept_id" in filters:
            where_conditions.append("c.concept_id = :concept_id")
            params["concept_id"] = filters["concept_id"]

        if "has_icd10" in filters and filters["has_icd10"]:
            where_conditions.append("crt.code IS NOT NULL")

        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"

        # Get diagnoses
        sql = get_diagnoses_with_icd10_sql().format(where_clause=where_clause)
        result = db.execute(text(sql), params)
        diagnoses = self._process_diagnosis_results(result)

        # Get total count
        count_sql = get_diagnoses_count_sql().format(where_clause=where_clause)
        count_result = db.execute(text(count_sql), params)
        total_count = count_result.scalar()

        return DiagnosisResponse(
            diagnoses=diagnoses, total_count=total_count, skip=skip, limit=limit
        )

    def get_diagnoses_by_visit(
        self, db: Session, visit_id: int, skip: int = 0, limit: int = 100
    ) -> VisitDiagnoses:
        """
        Get diagnoses for a specific visit.

        Args:
            db: Database session
            visit_id: ID of the visit
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            VisitDiagnoses with visit info and diagnoses
        """
        sql = get_diagnoses_by_visit_sql()
        params = {"visit_id": visit_id, "skip": skip, "limit": limit}

        result = db.execute(text(sql), params)
        diagnoses = self._process_diagnosis_results(result)

        # Get visit and patient info from first diagnosis if available
        visit_info = None
        patient_info = None

        if diagnoses:
            first_diagnosis = diagnoses[0]
            visit_info = {
                "visit_id": first_diagnosis.encounter.encounter_id,  # This would need to be visit_id
                "visit_uuid": "",  # Would need to be populated from visit table
            }
            patient_info = first_diagnosis.patient

        return VisitDiagnoses(
            visit_id=visit_id,
            visit_uuid="",  # Would need to be populated
            patient=patient_info or PatientInfo(patient_id=0, uuid="", name="Unknown"),
            diagnoses=diagnoses,
            total_count=len(diagnoses),
        )

    def _process_diagnosis_results(self, result) -> List[DiagnosisObservation]:
        """
        Process raw SQL results into DiagnosisObservation objects.
        """
        diagnoses = []

        for row in result:
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

            patient_name = (
                " ".join(patient_name_parts) if patient_name_parts else "Unknown"
            )

            # Build ICD10 codes
            icd10_codes = []
            if row.icd10_code:
                icd10_codes.append(
                    ICD10Code(
                        code=row.icd10_code,
                        name=row.icd10_name,
                        version=row.icd10_version,
                        description=row.icd10_description,
                    )
                )

            # Build diagnosis concept
            concept = DiagnosisConcept(
                concept_id=row.concept_id,
                uuid=row.concept_uuid,
                name=row.diagnosis_name,
                short_name=row.concept_short_name,
                description=row.concept_description,
                icd10_codes=icd10_codes if icd10_codes else None,
            )

            # Build patient info
            patient = PatientInfo(
                patient_id=row.patient_id,
                uuid=row.patient_uuid,
                name=patient_name,
                gender=row.patient_gender,
                birthdate=row.patient_birthdate,
            )

            # Build encounter info
            encounter = EncounterInfo(
                encounter_id=row.encounter_id,
                uuid=row.encounter_uuid,
                encounter_datetime=row.encounter_datetime,
                encounter_type=row.encounter_type,
                location_id=row.location_id,
            )

            # Build diagnosis observation
            diagnosis = DiagnosisObservation(
                obs_id=row.obs_id,
                uuid=row.obs_uuid,
                obs_datetime=row.obs_datetime,
                concept=concept,
                patient=patient,
                encounter=encounter,
                comments=row.comments,
                status=row.status,
                interpretation=row.interpretation,
            )

            diagnoses.append(diagnosis)

        return diagnoses
