"""
Patient history API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.auth import get_current_api_key
from app.crud.patient_history import patient_history, PatientHistoryError
from app.database import get_db
from app.schemas.patient_history import (
    HistoryType,
    PatientHistoryResponse,
    PatientHistorySummaryResponse,
)
from app.utils import validate_uuid

router = APIRouter(tags=["patient-history"])


@router.get("/patient/{patient_uuid}", response_model=PatientHistoryResponse)
async def get_patient_history(
    patient_uuid: str = Path(..., description="Patient UUID"),
    type: HistoryType = Query(
        "all",
        description="History type to return: all, complaint, examination, orders, treatments",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """Get patient history grouped by visit."""
    if not validate_uuid(patient_uuid):
        raise HTTPException(status_code=400, detail="Invalid patient UUID format")

    try:
        return patient_history.get_history(
            db=db,
            patient_uuid=patient_uuid,
            requested_type=type,
        )
    except PatientHistoryError as e:
        raise HTTPException(status_code=e.status, detail=e.code)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get patient history: {str(e)}",
        )


@router.get("/patient/{patient_uuid}/summary", response_model=PatientHistorySummaryResponse)
async def get_patient_history_summary(
    patient_uuid: str = Path(..., description="Patient UUID"),
    max_items_per_category: int = Query(
        3,
        ge=1,
        le=20,
        description="Maximum number of recent items to include for each history category",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """Get a high-level summary of patient history grouped by visit."""
    if not validate_uuid(patient_uuid):
        raise HTTPException(status_code=400, detail="Invalid patient UUID format")

    try:
        return patient_history.get_history_summary(
            db=db,
            patient_uuid=patient_uuid,
            max_items_per_category=max_items_per_category,
        )
    except PatientHistoryError as e:
        raise HTTPException(status_code=e.status, detail=e.code)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get patient history summary: {str(e)}",
        )
