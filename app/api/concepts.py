from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.auth import get_current_api_key
from app.crud import (
    create_concept, get_concept, get_concept_by_uuid, update_concept_partial, update_concept_partial_by_uuid,
    update_concept_full, update_concept_full_by_uuid, get_updated_concept_fields,
    list_concepts, get_concepts_by_datatype, get_concepts_by_class, get_concepts_by_creator,
    search_concepts_by_name, get_active_concepts, get_retired_concepts
)
from app.schemas import (
    ConceptCreate, ConceptUpdate, ConceptReplace, ConceptResponse, ConceptUpdateResponse, ErrorResponse
)

router = APIRouter()


@router.post("/", response_model=ConceptResponse)
async def create_concept_endpoint(
    concept_create: ConceptCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Create a new concept
    """
    try:
        new_concept = create_concept(db, concept_create)
        return new_concept
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create concept: {str(e)}")


@router.get("/", response_model=List[ConceptResponse])
async def list_concepts_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    List concepts with pagination
    """
    concepts_list = list_concepts(db, skip=skip, limit=limit)
    return concepts_list


@router.get("/active", response_model=List[ConceptResponse])
async def list_active_concepts_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    List only active (non-retired) concepts
    """
    concepts_list = get_active_concepts(db, skip=skip, limit=limit)
    return concepts_list


@router.get("/retired", response_model=List[ConceptResponse])
async def list_retired_concepts_endpoint(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    List only retired concepts
    """
    concepts_list = get_retired_concepts(db, skip=skip, limit=limit)
    return concepts_list


@router.get("/search", response_model=List[ConceptResponse])
async def search_concepts_endpoint(
    name: str = Query(..., description="Search term for concept name or description"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Search concepts by name or description
    """
    concepts_list = search_concepts_by_name(db, name, skip=skip, limit=limit)
    return concepts_list


@router.get("/datatype/{datatype_id}", response_model=List[ConceptResponse])
async def get_concepts_by_datatype_endpoint(
    datatype_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get concepts for a specific datatype
    """
    concepts_list = get_concepts_by_datatype(db, datatype_id, skip=skip, limit=limit)
    return concepts_list


@router.get("/class/{class_id}", response_model=List[ConceptResponse])
async def get_concepts_by_class_endpoint(
    class_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get concepts for a specific class
    """
    concepts_list = get_concepts_by_class(db, class_id, skip=skip, limit=limit)
    return concepts_list


@router.get("/creator/{creator}", response_model=List[ConceptResponse])
async def get_concepts_by_creator_endpoint(
    creator: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get concepts created by a specific user
    """
    concepts_list = get_concepts_by_creator(db, creator, skip=skip, limit=limit)
    return concepts_list


@router.get("/{uuid}", response_model=ConceptResponse)
async def get_concept_endpoint(
    uuid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get concept by UUID
    """
    concept = get_concept_by_uuid(db, uuid)
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")
    return concept


@router.patch("/{uuid}", response_model=ConceptUpdateResponse)
async def update_concept_partial_endpoint(
    uuid: str,
    concept_update: ConceptUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Update concept partially (PATCH) by UUID
    Only updates provided fields
    """
    # Get original concept for comparison
    original_concept = get_concept_by_uuid(db, uuid)
    if not original_concept:
        raise HTTPException(status_code=404, detail="Concept not found")
    
    # Update concept
    updated_concept = update_concept_partial_by_uuid(db, uuid, concept_update)
    if not updated_concept:
        raise HTTPException(status_code=404, detail="Concept not found")
    
    # Get updated fields
    updated_fields = get_updated_concept_fields(original_concept, updated_concept)
    
    return ConceptUpdateResponse(
        success=True,
        message=f"Concept {uuid} updated successfully",
        concept_id=updated_concept.concept_id,
        updated_fields=updated_fields,
        concept=updated_concept
    )


@router.put("/{uuid}", response_model=ConceptUpdateResponse)
async def replace_concept_endpoint(
    uuid: str,
    concept_replace: ConceptReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Replace concept completely (PUT) by UUID
    Updates all fields with provided values
    """
    # Get original concept for comparison
    original_concept = get_concept_by_uuid(db, uuid)
    if not original_concept:
        raise HTTPException(status_code=404, detail="Concept not found")
    
    # Replace concept
    updated_concept = update_concept_full_by_uuid(db, uuid, concept_replace)
    if not updated_concept:
        raise HTTPException(status_code=404, detail="Concept not found")
    
    # Get updated fields
    updated_fields = get_updated_concept_fields(original_concept, updated_concept)
    
    return ConceptUpdateResponse(
        success=True,
        message=f"Concept {uuid} replaced successfully",
        concept_id=updated_concept.concept_id,
        updated_fields=updated_fields,
        concept=updated_concept
    ) 