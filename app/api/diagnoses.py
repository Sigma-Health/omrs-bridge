"""
Diagnosis API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.auth import get_current_api_key
from app.crud import diagnoses
from app.schemas import DiagnosisResponse, VisitDiagnoses, ErrorResponse

router = APIRouter()


@router.get("/", response_model=DiagnosisResponse)
async def get_diagnoses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    visit_id: Optional[int] = Query(None, description="Filter by visit ID"),
    visit_uuid: Optional[str] = Query(None, description="Filter by visit UUID"),
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    encounter_id: Optional[int] = Query(None, description="Filter by encounter ID"),
    concept_id: Optional[int] = Query(None, description="Filter by concept ID"),
    has_reference_codes: Optional[bool] = Query(
        None, description="Filter for diagnoses with reference codes"
    ),
    source_name: Optional[str] = Query(
        None, description="Filter by reference source name (e.g., 'ICD-10', 'CIEL', 'IMO-ProblemIT')"
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get diagnoses with reference codes (ICD10, CIEL, IMO, etc.).

    Supports filtering by:
    - visit_id: Get diagnoses for a specific visit by ID
    - visit_uuid: Get diagnoses for a specific visit by UUID
    - patient_id: Get diagnoses for a specific patient
    - encounter_id: Get diagnoses for a specific encounter
    - concept_id: Get diagnoses for a specific concept
    - has_reference_codes: Filter for diagnoses that have reference codes
    - source_name: Filter by reference source name (e.g., 'ICD-10', 'CIEL', 'IMO-ProblemIT')
    """
    try:
        # Build filters
        filters = {}
        if visit_id is not None:
            filters["visit_id"] = visit_id
        if visit_uuid is not None:
            filters["visit_uuid"] = visit_uuid
        if patient_id is not None:
            filters["patient_id"] = patient_id
        if encounter_id is not None:
            filters["encounter_id"] = encounter_id
        if concept_id is not None:
            filters["concept_id"] = concept_id
        if has_reference_codes is not None:
            filters["has_reference_codes"] = has_reference_codes
        if source_name is not None:
            filters["source_name"] = source_name

        result = diagnoses.get_diagnoses(db=db, skip=skip, limit=limit, **filters)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to get diagnoses: {str(e)}"
        )


@router.get("/visit/{visit_id}", response_model=VisitDiagnoses)
async def get_diagnoses_by_visit_id(
    visit_id: int = Path(..., description="Visit ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get diagnoses for a specific visit by visit ID.
    """
    try:
        result = diagnoses.get_diagnoses_by_visit(
            db=db, visit_id=visit_id, skip=skip, limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get diagnoses for visit {visit_id}: {str(e)}",
        )


@router.get("/visit/uuid/{visit_uuid}", response_model=VisitDiagnoses)
async def get_diagnoses_by_visit_uuid(
    visit_uuid: str = Path(..., description="Visit UUID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get diagnoses for a specific visit by visit UUID.
    """
    try:
        result = diagnoses.get_diagnoses_by_visit_uuid(
            db=db, visit_uuid=visit_uuid, skip=skip, limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get diagnoses for visit UUID {visit_uuid}: {str(e)}",
        )


@router.get("/patient/{patient_id}", response_model=DiagnosisResponse)
async def get_diagnoses_by_patient(
    patient_id: int = Path(..., description="Patient ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get diagnoses for a specific patient with ICD10 codes.
    """
    try:
        result = diagnoses.get_diagnoses(
            db=db, skip=skip, limit=limit, patient_id=patient_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get diagnoses for patient {patient_id}: {str(e)}",
        )


@router.get("/encounter/{encounter_id}", response_model=DiagnosisResponse)
async def get_diagnoses_by_encounter(
    encounter_id: int = Path(..., description="Encounter ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get diagnoses for a specific encounter with ICD10 codes.
    """
    try:
        result = diagnoses.get_diagnoses(
            db=db, skip=skip, limit=limit, encounter_id=encounter_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get diagnoses for encounter {encounter_id}: {str(e)}",
        )
