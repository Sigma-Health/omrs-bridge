from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.auth import get_current_api_key
from app.crud import observations
from app.schemas import (
    ObsCreate, ObsUpdate, ObsReplace, ObsResponse, ObsUpdateResponse, ErrorResponse
)

router = APIRouter()


@router.post("/", response_model=ObsResponse)
async def create_observation(
    obs_create: ObsCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Create a new observation
    """
    try:
        new_obs = observations.create(db, obs_create)
        return new_obs
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create observation: {str(e)}")


@router.get("/", response_model=List[ObsResponse])
async def list_observations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    List observations with pagination
    """
    observations_list = observations.list(db, skip=skip, limit=limit)
    return observations_list


@router.get("/active", response_model=List[ObsResponse])
async def list_active_observations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    List active (non-voided) observations
    """
    observations_list = observations.get_active_obs(db, skip=skip, limit=limit)
    return observations_list


@router.get("/voided", response_model=List[ObsResponse])
async def list_voided_observations(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    List voided observations
    """
    observations_list = observations.get_voided_obs(db, skip=skip, limit=limit)
    return observations_list


@router.get("/person/{person_id}", response_model=List[ObsResponse])
async def get_observations_by_person(
    person_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get observations for a specific person
    """
    observations_list = observations.get_obs_by_person(db, person_id=person_id, skip=skip, limit=limit)
    return observations_list


@router.get("/encounter/{encounter_id}", response_model=List[ObsResponse])
async def get_observations_by_encounter(
    encounter_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get observations for a specific encounter
    """
    observations_list = observations.get_obs_by_encounter(db, encounter_id=encounter_id, skip=skip, limit=limit)
    return observations_list


@router.get("/concept/{concept_id}", response_model=List[ObsResponse])
async def get_observations_by_concept(
    concept_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get observations for a specific concept
    """
    observations_list = observations.get_obs_by_concept(db, concept_id=concept_id, skip=skip, limit=limit)
    return observations_list


@router.get("/order/{order_id}", response_model=List[ObsResponse])
async def get_observations_by_order(
    order_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get observations for a specific order
    """
    observations_list = observations.get_obs_by_order(db, order_id=order_id, skip=skip, limit=limit)
    return observations_list


@router.get("/value-type/{value_type}", response_model=List[ObsResponse])
async def get_observations_by_value_type(
    value_type: str = Path(..., description="Value type: coded, numeric, text, datetime"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get observations by value type
    """
    observations_list = observations.get_obs_by_value_type(db, value_type=value_type, skip=skip, limit=limit)
    return observations_list


@router.get("/status/{status}", response_model=List[ObsResponse])
async def get_observations_by_status(
    status: str = Path(..., description="Status: FINAL, PRELIMINARY, etc."),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get observations by status
    """
    observations_list = observations.get_obs_by_status(db, status=status, skip=skip, limit=limit)
    return observations_list


@router.get("/{obs_id}", response_model=ObsResponse)
async def get_observation(
    obs_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get observation by ID
    """
    obs = observations.get(db, obs_id)
    if not obs:
        raise HTTPException(status_code=404, detail="Observation not found")
    return obs


@router.get("/uuid/{uuid}", response_model=ObsResponse)
async def get_observation_by_uuid(
    uuid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get observation by UUID
    """
    obs = observations.get_by_uuid(db, uuid)
    if not obs:
        raise HTTPException(status_code=404, detail="Observation not found")
    return obs


@router.patch("/{obs_id}", response_model=ObsUpdateResponse)
async def update_observation_partial(
    obs_id: int,
    obs_update: ObsUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Update observation partially (PATCH)
    """
    try:
        updated_obs = observations.update_partial(db, obs_id, obs_update)
        if not updated_obs:
            raise HTTPException(status_code=404, detail="Observation not found")
        
        # Get updated fields for response
        original_obs = observations.get(db, obs_id)
        updated_fields = observations.get_updated_fields(original_obs, updated_obs)
        
        return ObsUpdateResponse(
            obs=updated_obs,
            updated_fields=updated_fields
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update observation: {str(e)}")


@router.patch("/uuid/{uuid}", response_model=ObsUpdateResponse)
async def update_observation_partial_by_uuid(
    uuid: str,
    obs_update: ObsUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Update observation partially by UUID (PATCH)
    """
    try:
        updated_obs = observations.update_partial_by_uuid(db, uuid, obs_update)
        if not updated_obs:
            raise HTTPException(status_code=404, detail="Observation not found")
        
        # Get updated fields for response
        original_obs = observations.get_by_uuid(db, uuid)
        updated_fields = observations.get_updated_fields(original_obs, updated_obs)
        
        return ObsUpdateResponse(
            obs=updated_obs,
            updated_fields=updated_fields
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update observation: {str(e)}")


@router.put("/{obs_id}", response_model=ObsUpdateResponse)
async def update_observation_full(
    obs_id: int,
    obs_replace: ObsReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Update observation completely (PUT)
    """
    try:
        updated_obs = observations.update_full(db, obs_id, obs_replace)
        if not updated_obs:
            raise HTTPException(status_code=404, detail="Observation not found")
        
        # Get updated fields for response
        original_obs = observations.get(db, obs_id)
        updated_fields = observations.get_updated_fields(original_obs, updated_obs)
        
        return ObsUpdateResponse(
            obs=updated_obs,
            updated_fields=updated_fields
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update observation: {str(e)}")


@router.put("/uuid/{uuid}", response_model=ObsUpdateResponse)
async def update_observation_full_by_uuid(
    uuid: str,
    obs_replace: ObsReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Update observation completely by UUID (PUT)
    """
    try:
        updated_obs = observations.update_full_by_uuid(db, uuid, obs_replace)
        if not updated_obs:
            raise HTTPException(status_code=404, detail="Observation not found")
        
        # Get updated fields for response
        original_obs = observations.get_by_uuid(db, uuid)
        updated_fields = observations.get_updated_fields(original_obs, updated_obs)
        
        return ObsUpdateResponse(
            obs=updated_obs,
            updated_fields=updated_fields
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update observation: {str(e)}")


@router.post("/{obs_id}/void", response_model=ObsResponse)
async def void_observation(
    obs_id: int,
    voided_by: int = Path(..., description="ID of the user voiding the observation"),
    reason: Optional[str] = Query(None, description="Reason for voiding"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Void an observation
    """
    try:
        voided_obs = observations.void_obs(db, obs_id, voided_by, reason)
        if not voided_obs:
            raise HTTPException(status_code=404, detail="Observation not found")
        return voided_obs
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to void observation: {str(e)}")


@router.post("/{obs_id}/unvoid", response_model=ObsResponse)
async def unvoid_observation(
    obs_id: int,
    unvoided_by: int = Path(..., description="ID of the user unvoiding the observation"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Unvoid an observation
    """
    try:
        unvoided_obs = observations.unvoid_obs(db, obs_id, unvoided_by)
        if not unvoided_obs:
            raise HTTPException(status_code=404, detail="Observation not found")
        return unvoided_obs
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to unvoid observation: {str(e)}")