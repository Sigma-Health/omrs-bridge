"""
Vitals API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.auth import get_current_api_key
from app.crud import vitals, observations
from app.schemas import (
    VitalsResponse,
    VisitVitals,
    VitalsGroupedResponse,
    ErrorResponse,
    VitalCreate,
    VitalUpdate,
    VitalReplace,
    VitalUpdateResponse,
    VitalSign,
)
from app.models import Obs
from app.utils import validate_uuid

router = APIRouter()


def _obs_to_vital_sign(db: Session, obs: Obs) -> VitalSign:
    """
    Convert an Obs model to a VitalSign schema.
    Fetches concept name and other details from the database.
    """
    # Get concept name
    concept_name_query = """
    SELECT name FROM concept_name 
    WHERE concept_id = :concept_id 
    AND locale = 'en' 
    AND concept_name_type = 'FULLY_SPECIFIED' 
    AND voided = 0
    LIMIT 1
    """
    concept_result = db.execute(text(concept_name_query), {"concept_id": obs.concept_id})
    concept_row = concept_result.fetchone()
    concept_name = concept_row[0] if concept_row else "Unknown"
    
    # Get coded value name if applicable
    value_coded_name = None
    if obs.value_coded:
        coded_name_query = """
        SELECT name FROM concept_name 
        WHERE concept_id = :concept_id 
        AND locale = 'en' 
        AND concept_name_type = 'FULLY_SPECIFIED' 
        AND voided = 0
        LIMIT 1
        """
        coded_result = db.execute(text(coded_name_query), {"concept_id": obs.value_coded})
        coded_row = coded_result.fetchone()
        value_coded_name = coded_row[0] if coded_row else None
    
    # Get encounter and visit info
    encounter_query = """
    SELECT e.encounter_id, e.uuid, e.encounter_datetime, v.uuid as visit_uuid
    FROM encounter e
    INNER JOIN visit v ON e.visit_id = v.visit_id
    WHERE e.encounter_id = :encounter_id
    LIMIT 1
    """
    encounter_result = db.execute(text(encounter_query), {"encounter_id": obs.encounter_id})
    encounter_row = encounter_result.fetchone()
    
    encounter_id = obs.encounter_id
    encounter_uuid = encounter_row[1] if encounter_row else ""
    encounter_datetime = encounter_row[2] if encounter_row else None
    visit_uuid = encounter_row[3] if encounter_row else ""
    
    # Get patient info
    patient_query = """
    SELECT p.patient_id, pt.uuid, 
           CONCAT_WS(' ', pn.prefix, pn.given_name, pn.middle_name, pn.family_name) as name
    FROM patient p
    INNER JOIN person pt ON p.patient_id = pt.person_id
    LEFT JOIN person_name pn ON pt.person_id = pn.person_id AND pn.preferred = 1 AND pn.voided = 0
    WHERE p.patient_id = (SELECT patient_id FROM encounter WHERE encounter_id = :encounter_id)
    LIMIT 1
    """
    patient_result = db.execute(text(patient_query), {"encounter_id": obs.encounter_id})
    patient_row = patient_result.fetchone()
    
    patient_id = patient_row[0] if patient_row else 0
    patient_uuid = patient_row[1] if patient_row else ""
    patient_name = patient_row[2] if patient_row else "Unknown"
    
    return VitalSign(
        obs_id=obs.obs_id,
        uuid=obs.uuid,
        obs_datetime=obs.obs_datetime,
        concept_id=obs.concept_id,
        concept_name=concept_name,
        value_numeric=obs.value_numeric,
        value_text=obs.value_text,
        value_coded=obs.value_coded,
        value_coded_name=value_coded_name,
        value_datetime=obs.value_datetime,
        comments=obs.comments,
        status=obs.status,
        interpretation=obs.interpretation,
        patient_id=patient_id,
        patient_uuid=patient_uuid,
        patient_name=patient_name,
        encounter_id=encounter_id,
        encounter_uuid=encounter_uuid,
        encounter_datetime=encounter_datetime,
        visit_uuid=visit_uuid,
    )


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


@router.post("/", response_model=VitalSign)
async def create_vital(
    vital_create: VitalCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Create a new vital sign observation.
    
    Creates a new observation record for a vital sign measurement.
    At least one value field (value_numeric, value_text, value_coded, or value_datetime) must be provided.
    """
    try:
        # Validate that at least one value is provided
        if not any([
            vital_create.value_numeric is not None,
            vital_create.value_text is not None,
            vital_create.value_coded is not None,
            vital_create.value_datetime is not None,
        ]):
            raise HTTPException(
                status_code=400,
                detail="At least one value field (value_numeric, value_text, value_coded, or value_datetime) must be provided",
            )
        
        # Convert VitalCreate to ObsCreate
        from app.schemas import ObsCreate
        
        obs_create = ObsCreate(
            person_id=vital_create.person_id,
            concept_id=vital_create.concept_id,
            encounter_id=vital_create.encounter_id,
            creator=vital_create.creator,
            value_numeric=vital_create.value_numeric,
            value_text=vital_create.value_text,
            value_coded=vital_create.value_coded,
            value_datetime=vital_create.value_datetime,
            obs_datetime=vital_create.obs_datetime,
            location_id=vital_create.location_id,
            obs_group_id=vital_create.obs_group_id,
            order_id=vital_create.order_id,
            comments=vital_create.comments,
            status=vital_create.status,
            interpretation=vital_create.interpretation,
            value_modifier=vital_create.value_modifier,
            form_namespace_and_path=vital_create.form_namespace_and_path,
        )
        
        # Create the observation
        created_obs = observations.create(db, obs_create)
        
        # Convert to VitalSign for response
        return _obs_to_vital_sign(db, created_obs)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create vital: {str(e)}",
        )


@router.patch("/{obs_id}", response_model=VitalUpdateResponse)
async def update_vital_partial(
    obs_id: int,
    vital_update: VitalUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update a vital sign observation partially (PATCH).
    
    Updates only the provided fields of an existing vital sign observation.
    """
    try:
        # Convert VitalUpdate to ObsUpdate
        from app.schemas import ObsUpdate
        
        obs_update = ObsUpdate(
            value_numeric=vital_update.value_numeric,
            value_text=vital_update.value_text,
            value_coded=vital_update.value_coded,
            value_datetime=vital_update.value_datetime,
            obs_datetime=vital_update.obs_datetime,
            comments=vital_update.comments,
            status=vital_update.status,
            interpretation=vital_update.interpretation,
            value_modifier=vital_update.value_modifier,
        )
        
        # Update the observation
        updated_obs = observations.update_partial(db, obs_id, obs_update)
        if not updated_obs:
            raise HTTPException(
                status_code=404,
                detail="Vital not found",
            )
        
        # Get updated fields
        original_obs = observations.get(db, obs_id)
        updated_fields = observations.get_updated_fields(original_obs, updated_obs)
        
        # Convert to VitalSign for response
        vital_sign = _obs_to_vital_sign(db, updated_obs)
        
        return VitalUpdateResponse(
            success=True,
            message="Vital updated successfully",
            obs_id=obs_id,
            updated_fields=updated_fields,
            vital=vital_sign,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update vital: {str(e)}",
        )


@router.patch("/uuid/{uuid}", response_model=VitalUpdateResponse)
async def update_vital_partial_by_uuid(
    uuid: str,
    vital_update: VitalUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update a vital sign observation partially by UUID (PATCH).
    
    Updates only the provided fields of an existing vital sign observation.
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )
    
    try:
        # Convert VitalUpdate to ObsUpdate
        from app.schemas import ObsUpdate
        
        obs_update = ObsUpdate(
            value_numeric=vital_update.value_numeric,
            value_text=vital_update.value_text,
            value_coded=vital_update.value_coded,
            value_datetime=vital_update.value_datetime,
            obs_datetime=vital_update.obs_datetime,
            comments=vital_update.comments,
            status=vital_update.status,
            interpretation=vital_update.interpretation,
            value_modifier=vital_update.value_modifier,
        )
        
        # Update the observation
        updated_obs = observations.update_partial_by_uuid(db, uuid, obs_update)
        if not updated_obs:
            raise HTTPException(
                status_code=404,
                detail="Vital not found",
            )
        
        # Get updated fields
        original_obs = observations.get_by_uuid(db, uuid)
        updated_fields = observations.get_updated_fields(original_obs, updated_obs)
        
        # Convert to VitalSign for response
        vital_sign = _obs_to_vital_sign(db, updated_obs)
        
        return VitalUpdateResponse(
            success=True,
            message="Vital updated successfully",
            obs_id=updated_obs.obs_id,
            updated_fields=updated_fields,
            vital=vital_sign,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update vital: {str(e)}",
        )


@router.put("/{obs_id}", response_model=VitalUpdateResponse)
async def update_vital_full(
    obs_id: int,
    vital_replace: VitalReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update a vital sign observation completely (PUT).
    
    Replaces all fields of an existing vital sign observation.
    """
    try:
        # Validate that at least one value is provided
        if not any([
            vital_replace.value_numeric is not None,
            vital_replace.value_text is not None,
            vital_replace.value_coded is not None,
            vital_replace.value_datetime is not None,
        ]):
            raise HTTPException(
                status_code=400,
                detail="At least one value field (value_numeric, value_text, value_coded, or value_datetime) must be provided",
            )
        
        # Convert VitalReplace to ObsReplace
        from app.schemas import ObsReplace
        
        # Get the existing obs to preserve UUID
        existing_obs = observations.get(db, obs_id)
        if not existing_obs:
            raise HTTPException(
                status_code=404,
                detail="Vital not found",
            )
        
        obs_replace = ObsReplace(
            person_id=vital_replace.person_id,
            concept_id=vital_replace.concept_id,
            encounter_id=vital_replace.encounter_id,
            creator=vital_replace.creator,
            uuid=existing_obs.uuid,
            value_numeric=vital_replace.value_numeric,
            value_text=vital_replace.value_text,
            value_coded=vital_replace.value_coded,
            value_datetime=vital_replace.value_datetime,
            obs_datetime=vital_replace.obs_datetime,
            location_id=vital_replace.location_id,
            obs_group_id=vital_replace.obs_group_id,
            order_id=vital_replace.order_id,
            comments=vital_replace.comments,
            status=vital_replace.status,
            interpretation=vital_replace.interpretation,
            value_modifier=vital_replace.value_modifier,
            form_namespace_and_path=vital_replace.form_namespace_and_path,
        )
        
        # Update the observation
        updated_obs = observations.update_full(db, obs_id, obs_replace)
        if not updated_obs:
            raise HTTPException(
                status_code=404,
                detail="Vital not found",
            )
        
        # Get updated fields
        updated_fields = observations.get_updated_fields(existing_obs, updated_obs)
        
        # Convert to VitalSign for response
        vital_sign = _obs_to_vital_sign(db, updated_obs)
        
        return VitalUpdateResponse(
            success=True,
            message="Vital updated successfully",
            obs_id=obs_id,
            updated_fields=updated_fields,
            vital=vital_sign,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update vital: {str(e)}",
        )


@router.put("/uuid/{uuid}", response_model=VitalUpdateResponse)
async def update_vital_full_by_uuid(
    uuid: str,
    vital_replace: VitalReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update a vital sign observation completely by UUID (PUT).
    
    Replaces all fields of an existing vital sign observation.
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )
    
    try:
        # Validate that at least one value is provided
        if not any([
            vital_replace.value_numeric is not None,
            vital_replace.value_text is not None,
            vital_replace.value_coded is not None,
            vital_replace.value_datetime is not None,
        ]):
            raise HTTPException(
                status_code=400,
                detail="At least one value field (value_numeric, value_text, value_coded, or value_datetime) must be provided",
            )
        
        # Convert VitalReplace to ObsReplace
        from app.schemas import ObsReplace
        
        # Get the existing obs to preserve UUID
        existing_obs = observations.get_by_uuid(db, uuid)
        if not existing_obs:
            raise HTTPException(
                status_code=404,
                detail="Vital not found",
            )
        
        obs_replace = ObsReplace(
            person_id=vital_replace.person_id,
            concept_id=vital_replace.concept_id,
            encounter_id=vital_replace.encounter_id,
            creator=vital_replace.creator,
            uuid=uuid,
            value_numeric=vital_replace.value_numeric,
            value_text=vital_replace.value_text,
            value_coded=vital_replace.value_coded,
            value_datetime=vital_replace.value_datetime,
            obs_datetime=vital_replace.obs_datetime,
            location_id=vital_replace.location_id,
            obs_group_id=vital_replace.obs_group_id,
            order_id=vital_replace.order_id,
            comments=vital_replace.comments,
            status=vital_replace.status,
            interpretation=vital_replace.interpretation,
            value_modifier=vital_replace.value_modifier,
            form_namespace_and_path=vital_replace.form_namespace_and_path,
        )
        
        # Update the observation
        updated_obs = observations.update_full_by_uuid(db, uuid, obs_replace)
        if not updated_obs:
            raise HTTPException(
                status_code=404,
                detail="Vital not found",
            )
        
        # Get updated fields
        updated_fields = observations.get_updated_fields(existing_obs, updated_obs)
        
        # Convert to VitalSign for response
        vital_sign = _obs_to_vital_sign(db, updated_obs)
        
        return VitalUpdateResponse(
            success=True,
            message="Vital updated successfully",
            obs_id=updated_obs.obs_id,
            updated_fields=updated_fields,
            vital=vital_sign,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update vital: {str(e)}",
        )
