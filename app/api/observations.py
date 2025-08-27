from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.auth import get_current_api_key
from app.crud import (
    create_obs, get_obs, get_obs_by_uuid, update_obs_partial, update_obs_partial_by_uuid,
    update_obs_full, update_obs_full_by_uuid, get_updated_obs_fields,
    list_obs, get_obs_by_person, get_obs_by_encounter, get_obs_by_concept, get_obs_by_order
)
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
        new_obs = create_obs(db, obs_create)
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
    obs_list = list_obs(db, skip=skip, limit=limit)
    return obs_list


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
    obs_list = get_obs_by_person(db, person_id, skip=skip, limit=limit)
    return obs_list


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
    obs_list = get_obs_by_encounter(db, encounter_id, skip=skip, limit=limit)
    return obs_list


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
    obs_list = get_obs_by_concept(db, concept_id, skip=skip, limit=limit)
    return obs_list


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
    obs_list = get_obs_by_order(db, order_id, skip=skip, limit=limit)
    return obs_list


@router.get("/{uuid}", response_model=ObsResponse)
async def get_observation(
    uuid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get observation by UUID
    """
    obs = get_obs_by_uuid(db, uuid)
    if not obs:
        raise HTTPException(status_code=404, detail="Observation not found")
    return obs


@router.patch("/{uuid}", response_model=ObsUpdateResponse)
async def update_observation_partial(
    uuid: str,
    obs_update: ObsUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Update observation partially (PATCH) by UUID
    Only updates provided fields
    """
    # Get original observation for comparison
    original_obs = get_obs_by_uuid(db, uuid)
    if not original_obs:
        raise HTTPException(status_code=404, detail="Observation not found")
    
    # Update observation
    updated_obs = update_obs_partial_by_uuid(db, uuid, obs_update)
    if not updated_obs:
        raise HTTPException(status_code=404, detail="Observation not found")
    
    # Get updated fields
    updated_fields = get_updated_obs_fields(original_obs, updated_obs)
    
    return ObsUpdateResponse(
        success=True,
        message=f"Observation {uuid} updated successfully",
        obs_id=updated_obs.obs_id,
        updated_fields=updated_fields,
        obs=updated_obs
    )


@router.put("/{uuid}", response_model=ObsUpdateResponse)
async def replace_observation(
    uuid: str,
    obs_replace: ObsReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Replace observation completely (PUT) by UUID
    Updates all fields with provided values
    """
    # Get original observation for comparison
    original_obs = get_obs_by_uuid(db, uuid)
    if not original_obs:
        raise HTTPException(status_code=404, detail="Observation not found")
    
    # Replace observation
    updated_obs = update_obs_full_by_uuid(db, uuid, obs_replace)
    if not updated_obs:
        raise HTTPException(status_code=404, detail="Observation not found")
    
    # Get updated fields
    updated_fields = get_updated_obs_fields(original_obs, updated_obs)
    
    return ObsUpdateResponse(
        success=True,
        message=f"Observation {uuid} replaced successfully",
        obs_id=updated_obs.obs_id,
        updated_fields=updated_fields,
        obs=updated_obs
    ) 