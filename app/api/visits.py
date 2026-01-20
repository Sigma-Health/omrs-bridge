from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Path,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_api_key
from app.crud import visits
from app.schemas import (
    VisitCreate,
    VisitUpdate,
    VisitReplace,
    VisitResponse,
    VisitUpdateResponse,
)
from app.utils import validate_uuid

router = APIRouter(tags=["visits"])


@router.post("/", response_model=VisitResponse)
async def create_visit(
    visit_create: VisitCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Create a new visit
    """
    try:
        return visits.create(db, visit_create)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create visit: {str(e)}",
        )


@router.get("/", response_model=List[VisitResponse])
async def list_visits(
    skip: int = Query(
        0,
        ge=0,
        description="Number of records to skip",
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Number of records to return",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    List visits with pagination
    """
    return visits.list(db, skip=skip, limit=limit)


@router.get("/active", response_model=List[VisitResponse])
async def list_active_visits(
    patient_id: Optional[int] = Query(
        None,
        description="Filter by patient ID",
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Number of records to skip",
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Number of records to return",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    List active visits (not voided and not stopped)
    """
    return visits.get_active_visits(
        db,
        patient_id=patient_id,
        skip=skip,
        limit=limit,
    )


@router.get("/completed", response_model=List[VisitResponse])
async def list_completed_visits(
    patient_id: Optional[int] = Query(
        None,
        description="Filter by patient ID",
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Number of records to skip",
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Number of records to return",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    List completed visits (not voided and with date_stopped)
    """
    return visits.get_completed_visits(
        db,
        patient_id=patient_id,
        skip=skip,
        limit=limit,
    )


@router.get("/voided", response_model=List[VisitResponse])
async def list_voided_visits(
    patient_id: Optional[int] = Query(
        None,
        description="Filter by patient ID",
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Number of records to skip",
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Number of records to return",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    List voided visits
    """
    return visits.get_voided_visits(
        db,
        patient_id=patient_id,
        skip=skip,
        limit=limit,
    )


@router.get("/patient/{patient_id}", response_model=List[VisitResponse])
async def get_visits_by_patient(
    patient_id: int = Path(..., description="Patient ID"),
    skip: int = Query(
        0,
        ge=0,
        description="Number of records to skip",
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Number of records to return",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get all visits for a specific patient
    """
    return visits.get_by_patient(
        db,
        patient_id=patient_id,
        skip=skip,
        limit=limit,
    )


@router.get("/type/{visit_type_id}", response_model=List[VisitResponse])
async def get_visits_by_type(
    visit_type_id: int = Path(..., description="Visit type ID"),
    skip: int = Query(
        0,
        ge=0,
        description="Number of records to skip",
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Number of records to return",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get visits by visit type
    """
    return visits.get_by_visit_type(
        db,
        visit_type_id=visit_type_id,
        skip=skip,
        limit=limit,
    )


@router.get("/location/{location_id}", response_model=List[VisitResponse])
async def get_visits_by_location(
    location_id: int = Path(..., description="Location ID"),
    skip: int = Query(
        0,
        ge=0,
        description="Number of records to skip",
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Number of records to return",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get visits by location
    """
    return visits.get_by_location(
        db,
        location_id=location_id,
        skip=skip,
        limit=limit,
    )


@router.get("/date-range", response_model=List[VisitResponse])
async def get_visits_by_date_range(
    start_date: str = Query(
        ...,
        description="Start date (YYYY-MM-DD format)",
    ),
    end_date: str = Query(
        ...,
        description="End date (YYYY-MM-DD format)",
    ),
    patient_id: Optional[int] = Query(
        None,
        description="Filter by patient ID",
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Number of records to skip",
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Number of records to return",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get visits within a date range
    """
    return visits.get_by_date_range(
        db,
        start_date=start_date,
        end_date=end_date,
        patient_id=patient_id,
        skip=skip,
        limit=limit,
    )


@router.get("/with-order-type/{order_type_id}", response_model=List[VisitResponse])
async def get_visits_with_order_type_enriched(
    order_type_id: int = Path(..., description="Order type ID"),
    start_date: Optional[str] = Query(
        None,
        description="Start date (YYYY-MM-DD format)",
    ),
    end_date: Optional[str] = Query(
        None,
        description="End date (YYYY-MM-DD format)",
    ),
    patient_id: Optional[int] = Query(
        None,
        description="Filter by patient ID",
    ),
    location_id: Optional[int] = Query(
        None,
        description="Filter by location ID",
    ),
    days: Optional[int] = Query(
        None,
        ge=1,
        description="Number of days to look back from today (e.g., 1 for today, 2 for today and yesterday)",
    ),
    skip: int = Query(
        0,
        ge=0,
        description="Number of records to skip",
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
        description="Number of records to return",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get visits that have orders of a particular order type.
    This endpoint returns visits with patient details (name, gender, birthdate)
    You can filter by date range, patient ID, location ID, or number of days.
    """
    return visits.get_visits_with_order_type_and_patient_info(
        db,
        order_type_id=order_type_id,
        start_date=start_date,
        end_date=end_date,
        patient_id=patient_id,
        location_id=location_id,
        days=days,
        skip=skip,
        limit=limit,
    )


@router.get("/{visit_id}", response_model=VisitResponse)
async def get_visit(
    visit_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get visit by ID
    """
    visit = visits.get(db, visit_id)
    if not visit:
        raise HTTPException(
            status_code=404,
            detail="Visit not found",
        )
    return visit


@router.get("/uuid/{uuid}", response_model=VisitResponse)
async def get_visit_by_uuid(
    uuid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get visit by UUID
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    visit = visits.get_by_uuid(db, uuid)
    if not visit:
        raise HTTPException(
            status_code=404,
            detail="Visit not found",
        )
    return visit


@router.patch(
    "/{visit_id}",
    response_model=VisitUpdateResponse,
)
async def update_visit_partial(
    visit_id: int,
    visit_update: VisitUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update visit partially (PATCH)
    """
    try:
        updated_visit = visits.update_partial(
            db,
            visit_id,
            visit_update,
        )
        if not updated_visit:
            raise HTTPException(
                status_code=404,
                detail="Visit not found",
            )

        # Get updated fields for response
        original_visit = visits.get(db, visit_id)
        updated_fields = visits.get_updated_fields(
            original_visit,
            updated_visit,
        )

        return VisitUpdateResponse(
            success=True,
            message="Visit updated successfully",
            visit_id=visit_id,
            updated_fields=updated_fields,
            visit=updated_visit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update visit: {str(e)}",
        )


@router.patch(
    "/uuid/{uuid}",
    response_model=VisitUpdateResponse,
)
async def update_visit_partial_by_uuid(
    uuid: str,
    visit_update: VisitUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update visit partially by UUID (PATCH)
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    try:
        updated_visit = visits.update_partial_by_uuid(
            db,
            uuid,
            visit_update,
        )
        if not updated_visit:
            raise HTTPException(
                status_code=404,
                detail="Visit not found",
            )

        # Get updated fields for response
        original_visit = visits.get_by_uuid(db, uuid)
        updated_fields = visits.get_updated_fields(
            original_visit,
            updated_visit,
        )

        return VisitUpdateResponse(
            success=True,
            message="Visit updated successfully",
            visit_id=updated_visit.visit_id,
            updated_fields=updated_fields,
            visit=updated_visit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update visit: {str(e)}",
        )


@router.put(
    "/{visit_id}",
    response_model=VisitUpdateResponse,
)
async def update_visit_full(
    visit_id: int,
    visit_replace: VisitReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update visit completely (PUT)
    """
    try:
        updated_visit = visits.update_full(
            db,
            visit_id,
            visit_replace,
        )
        if not updated_visit:
            raise HTTPException(
                status_code=404,
                detail="Visit not found",
            )

        # Get updated fields for response
        original_visit = visits.get(db, visit_id)
        updated_fields = visits.get_updated_fields(
            original_visit,
            updated_visit,
        )

        return VisitUpdateResponse(
            success=True,
            message="Visit updated successfully",
            visit_id=visit_id,
            updated_fields=updated_fields,
            visit=updated_visit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update visit: {str(e)}",
        )


@router.put(
    "/uuid/{uuid}",
    response_model=VisitUpdateResponse,
)
async def update_visit_full_by_uuid(
    uuid: str,
    visit_replace: VisitReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update visit completely by UUID (PUT)
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    try:
        updated_visit = visits.update_full_by_uuid(
            db,
            uuid,
            visit_replace,
        )
        if not updated_visit:
            raise HTTPException(
                status_code=404,
                detail="Visit not found",
            )

        # Get updated fields for response
        original_visit = visits.get_by_uuid(db, uuid)
        updated_fields = visits.get_updated_fields(
            original_visit,
            updated_visit,
        )

        return VisitUpdateResponse(
            success=True,
            message="Visit updated successfully",
            visit_id=updated_visit.visit_id,
            updated_fields=updated_fields,
            visit=updated_visit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update visit: {str(e)}",
        )


@router.post("/{visit_id}/stop", response_model=VisitResponse)
async def stop_visit(
    visit_id: int,
    stopped_by: int = Query(
        ...,
        description="ID of the user stopping the visit",
    ),
    date_stopped: Optional[str] = Query(
        None,
        description="Date when visit was stopped (YYYY-MM-DDTHH:MM:SS format, defaults to now)",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Stop a visit by setting the date_stopped field
    """
    try:
        stopped_visit = visits.stop_visit(
            db,
            visit_id,
            stopped_by,
            date_stopped,
        )
        if not stopped_visit:
            raise HTTPException(status_code=404, detail="Visit not found")
        return stopped_visit
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to stop visit: {str(e)}",
        )


@router.post("/{visit_id}/void", response_model=VisitResponse)
async def void_visit(
    visit_id: int,
    voided_by: int = Query(
        ...,
        description="ID of the user voiding the visit",
    ),
    void_reason: Optional[str] = Query(
        None,
        description="Reason for voiding the visit",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Void a visit
    """
    try:
        voided_visit = visits.void_visit(
            db,
            visit_id,
            voided_by,
            void_reason,
        )
        if not voided_visit:
            raise HTTPException(status_code=404, detail="Visit not found")
        return voided_visit
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to void visit: {str(e)}",
        )


@router.post("/{visit_id}/unvoid", response_model=VisitResponse)
async def unvoid_visit(
    visit_id: int,
    unvoided_by: int = Query(
        ...,
        description="ID of the user unvoiding the visit",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Unvoid a visit
    """
    try:
        unvoided_visit = visits.unvoid_visit(
            db,
            visit_id,
            unvoided_by,
        )
        if not unvoided_visit:
            raise HTTPException(status_code=404, detail="Visit not found")
        return unvoided_visit
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to unvoid visit: {str(e)}",
        )
