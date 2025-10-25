"""
Vitals API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app.database import get_db
from app.auth import get_current_api_key
from app.crud import vitals
from app.schemas import (
    VitalsResponse,
    VisitVitals,
    VitalsGroupedResponse,
    ErrorResponse,
)

router = APIRouter()


@router.get("/visit/{visit_id}", response_model=VisitVitals)
async def get_vitals_by_visit_id(
    visit_id: int = Path(..., description="Visit ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get vitals for a specific visit by visit ID.

    Returns vital signs and measurements for the specified visit including:
    - Blood pressure, temperature, pulse, weight, height, etc.
    - Patient and encounter information
    - Timestamps and values for each vital sign
    """
    try:
        result = vitals.get_vitals_by_visit(
            db=db, visit_id=visit_id, skip=skip, limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get vitals for visit {visit_id}: {str(e)}",
        )


@router.get("/visit/uuid/{visit_uuid}", response_model=VisitVitals)
async def get_vitals_by_visit_uuid(
    visit_uuid: str = Path(..., description="Visit UUID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get vitals for a specific visit by visit UUID.

    Returns vital signs and measurements for the specified visit including:
    - Blood pressure, temperature, pulse, weight, height, etc.
    - Patient and encounter information
    - Timestamps and values for each vital sign
    """
    try:
        result = vitals.get_vitals_by_visit_uuid(
            db=db, visit_uuid=visit_uuid, skip=skip, limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get vitals for visit UUID {visit_uuid}: {str(e)}",
        )


@router.get("/visit/{visit_id}/grouped", response_model=VitalsGroupedResponse)
async def get_vitals_grouped_by_type(
    visit_id: int = Path(..., description="Visit ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get vitals grouped by type for a specific visit.

    Returns vital signs organized by concept type (e.g., Blood Pressure, Temperature, etc.):
    - Each vital type contains all measurements of that type
    - Useful for displaying vitals in organized sections
    - Includes patient and encounter information
    """
    try:
        result = vitals.get_vitals_grouped_by_type(
            db=db, visit_id=visit_id, skip=skip, limit=limit
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get grouped vitals for visit {visit_id}: {str(e)}",
        )


@router.get("/visit/uuid/{visit_uuid}/grouped", response_model=VitalsGroupedResponse)
async def get_vitals_grouped_by_type_uuid(
    visit_uuid: str = Path(..., description="Visit UUID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get vitals grouped by type for a specific visit by UUID.

    Returns vital signs organized by concept type (e.g., Blood Pressure, Temperature, etc.):
    - Each vital type contains all measurements of that type
    - Useful for displaying vitals in organized sections
    - Includes patient and encounter information
    """
    try:
        # First get the visit_id from the UUID
        visit_query = """
        SELECT visit_id FROM visit WHERE uuid = :visit_uuid AND voided = 0
        """
        result = db.execute(text(visit_query), {"visit_uuid": visit_uuid})
        visit_row = result.fetchone()

        if not visit_row:
            raise HTTPException(
                status_code=404, detail=f"Visit with UUID {visit_uuid} not found"
            )

        visit_id = visit_row[0]

        # Use the existing method with visit_id
        result = vitals.get_vitals_grouped_by_type(
            db=db, visit_id=visit_id, skip=skip, limit=limit
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get grouped vitals for visit UUID {visit_uuid}: {str(e)}",
        )
