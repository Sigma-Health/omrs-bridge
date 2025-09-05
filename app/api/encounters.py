from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_api_key
from app.crud import encounters
from app.schemas import (
    EncounterCreate,
    EncounterUpdate,
    EncounterReplace,
    EncounterResponse,
    EncounterUpdateResponse,
)

router = APIRouter()


@router.post("/", response_model=EncounterResponse)
async def create_encounter_endpoint(
    encounter_create: EncounterCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Create a new encounter
    """
    try:
        return encounters.create(db, encounter_create)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create encounter: {str(e)}",
        )


@router.get("/", response_model=List[EncounterResponse])
async def list_encounters_endpoint(
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
    List encounters with pagination
    """
    return encounters.list(
        db,
        skip=skip,
        limit=limit,
    )


@router.get("/active", response_model=List[EncounterResponse])
async def list_active_encounters_endpoint(
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
    List active (non-voided) encounters
    """
    encounters_list = encounters.get_active_encounters(db, skip=skip, limit=limit)
    return encounters_list


@router.get("/voided", response_model=List[EncounterResponse])
async def list_voided_encounters_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    List voided encounters
    """
    encounters_list = encounters.get_voided_encounters(db, skip=skip, limit=limit)
    return encounters_list


@router.get("/patient/{patient_id}", response_model=List[EncounterResponse])
async def get_encounters_by_patient_endpoint(
    patient_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get encounters for a specific patient
    """
    encounters_list = encounters.get_encounters_by_patient(
        db, patient_id=patient_id, skip=skip, limit=limit
    )
    return encounters_list


@router.get("/type/{encounter_type}", response_model=List[EncounterResponse])
async def get_encounters_by_type_endpoint(
    encounter_type: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get encounters for a specific encounter type
    """
    encounters_list = encounters.get_encounters_by_type(
        db, encounter_type=encounter_type, skip=skip, limit=limit
    )
    return encounters_list


@router.get("/location/{location_id}", response_model=List[EncounterResponse])
async def get_encounters_by_location_endpoint(
    location_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get encounters for a specific location
    """
    encounters_list = encounters.get_encounters_by_location(
        db, location_id=location_id, skip=skip, limit=limit
    )
    return encounters_list


@router.get("/visit/{visit_id}", response_model=List[EncounterResponse])
async def get_encounters_by_visit_endpoint(
    visit_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get encounters for a specific visit
    """
    encounters_list = encounters.get_encounters_by_visit(
        db, visit_id=visit_id, skip=skip, limit=limit
    )
    return encounters_list


@router.get("/creator/{creator_id}", response_model=List[EncounterResponse])
async def get_encounters_by_creator_endpoint(
    creator_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get encounters created by a specific user
    """
    encounters_list = encounters.get_encounters_by_creator(
        db, creator=creator_id, skip=skip, limit=limit
    )
    return encounters_list


@router.get("/date-range", response_model=List[EncounterResponse])
async def get_encounters_by_date_range_endpoint(
    start_date: datetime = Query(..., description="Start date for the range"),
    end_date: datetime = Query(..., description="End date for the range"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get encounters within a date range
    """
    encounters_list = encounters.get_encounters_by_date_range(
        db, start_date=start_date, end_date=end_date, skip=skip, limit=limit
    )
    return encounters_list


@router.get("/{encounter_id}", response_model=EncounterResponse)
async def get_encounter_endpoint(
    encounter_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get encounter by ID
    """
    encounter = encounters.get(db, encounter_id)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return encounter


@router.get("/uuid/{uuid}", response_model=EncounterResponse)
async def get_encounter_by_uuid_endpoint(
    uuid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get encounter by UUID
    """
    encounter = encounters.get_by_uuid(db, uuid)
    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")
    return encounter


@router.patch("/{encounter_id}", response_model=EncounterUpdateResponse)
async def update_encounter_partial_endpoint(
    encounter_id: int,
    encounter_update: EncounterUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update encounter partially (PATCH)
    """
    try:
        updated_encounter = encounters.update_partial(
            db, encounter_id, encounter_update
        )
        if not updated_encounter:
            raise HTTPException(status_code=404, detail="Encounter not found")

        # Get updated fields for response
        original_encounter = encounters.get(db, encounter_id)
        updated_fields = encounters.get_updated_fields(
            original_encounter, updated_encounter
        )

        return EncounterUpdateResponse(
            encounter=updated_encounter, updated_fields=updated_fields
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to update encounter: {str(e)}"
        )


@router.patch("/uuid/{uuid}", response_model=EncounterUpdateResponse)
async def update_encounter_partial_by_uuid_endpoint(
    uuid: str,
    encounter_update: EncounterUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update encounter partially by UUID (PATCH)
    """
    try:
        updated_encounter = encounters.update_partial_by_uuid(
            db, uuid, encounter_update
        )
        if not updated_encounter:
            raise HTTPException(status_code=404, detail="Encounter not found")

        # Get updated fields for response
        original_encounter = encounters.get_by_uuid(db, uuid)
        updated_fields = encounters.get_updated_fields(
            original_encounter, updated_encounter
        )

        return EncounterUpdateResponse(
            encounter=updated_encounter, updated_fields=updated_fields
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to update encounter: {str(e)}"
        )


@router.put("/{encounter_id}", response_model=EncounterUpdateResponse)
async def update_encounter_full_endpoint(
    encounter_id: int,
    encounter_replace: EncounterReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update encounter completely (PUT)
    """
    try:
        updated_encounter = encounters.update_full(db, encounter_id, encounter_replace)
        if not updated_encounter:
            raise HTTPException(status_code=404, detail="Encounter not found")

        # Get updated fields for response
        original_encounter = encounters.get(db, encounter_id)
        updated_fields = encounters.get_updated_fields(
            original_encounter, updated_encounter
        )

        return EncounterUpdateResponse(
            encounter=updated_encounter, updated_fields=updated_fields
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to update encounter: {str(e)}"
        )


@router.put("/uuid/{uuid}", response_model=EncounterUpdateResponse)
async def update_encounter_full_by_uuid_endpoint(
    uuid: str,
    encounter_replace: EncounterReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update encounter completely by UUID (PUT)
    """
    try:
        updated_encounter = encounters.update_full_by_uuid(db, uuid, encounter_replace)
        if not updated_encounter:
            raise HTTPException(status_code=404, detail="Encounter not found")

        # Get updated fields for response
        original_encounter = encounters.get_by_uuid(db, uuid)
        updated_fields = encounters.get_updated_fields(
            original_encounter, updated_encounter
        )

        return EncounterUpdateResponse(
            encounter=updated_encounter, updated_fields=updated_fields
        )
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to update encounter: {str(e)}"
        )


@router.post("/{encounter_id}/void", response_model=EncounterResponse)
async def void_encounter_endpoint(
    encounter_id: int,
    voided_by: int = Query(..., description="ID of the user voiding the encounter"),
    reason: Optional[str] = Query(None, description="Reason for voiding"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Void an encounter
    """
    try:
        voided_encounter = encounters.void_encounter(
            db, encounter_id, voided_by, reason
        )
        if not voided_encounter:
            raise HTTPException(status_code=404, detail="Encounter not found")
        return voided_encounter
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to void encounter: {str(e)}"
        )


@router.post("/{encounter_id}/unvoid", response_model=EncounterResponse)
async def unvoid_encounter_endpoint(
    encounter_id: int,
    unvoided_by: int = Query(..., description="ID of the user unvoiding the encounter"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Unvoid an encounter
    """
    try:
        unvoided_encounter = encounters.unvoid_encounter(db, encounter_id, unvoided_by)
        if not unvoided_encounter:
            raise HTTPException(status_code=404, detail="Encounter not found")
        return unvoided_encounter
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to unvoid encounter: {str(e)}"
        )
