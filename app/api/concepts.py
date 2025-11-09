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
from app.crud import concepts
from app.services.search_index import trigger_search_index_update
from app.schemas import (
    ConceptUpdate,
    ConceptReplace,
    ConceptResponse,
    ConceptUpdateResponse,
)
from app.utils import validate_uuid

router = APIRouter(tags=["concepts"])


@router.post("/", response_model=ConceptResponse)
async def create_concept(
    concept_create: ConceptReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Create a new concept
    """
    try:
        created_concept = concepts.create(db, concept_create)

        status_text: Optional[str] = None
        try:
            result = await trigger_search_index_update(
                resource="concept",
                uuid=created_concept.uuid,
                async_mode=False,
            )
            status_text = result.status_text()
            if not result.success:
                logger.warning(
                    "Search index update returned failure for concept %s: %s",
                    getattr(created_concept, "uuid", "unknown"),
                    result.message,
                )
        except Exception as exc:  # pragma: no cover - defensive logging
            status_text = f"failed: {exc}"
            logger.warning(
                "Search index update invocation failed for concept %s: %s",
                getattr(created_concept, "uuid", "unknown"),
                exc,
            )

        response_payload = ConceptResponse.model_validate(
            created_concept,
            from_attributes=True,
        )
        if status_text:
            response_payload.search_index_update_status = status_text

        return response_payload
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create concept {str(e)}",
        )


@router.get("/", response_model=List[ConceptResponse])
async def list_concepts(
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
    locale: Optional[str] = Query(
        None,
        description="Locale code to filter concept names",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    List concepts with pagination
    """
    return concepts.list(db, skip=skip, limit=limit, locale=locale)


@router.get("/active", response_model=List[ConceptResponse])
async def list_active_concepts(
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
    locale: Optional[str] = Query(
        None,
        description="Locale code to filter concept names",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    List active (non-retired) concepts
    """
    return concepts.get_active_concepts(
        db,
        skip=skip,
        limit=limit,
        locale=locale,
    )


@router.get("/retired", response_model=List[ConceptResponse])
async def list_retired_concepts(
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
    locale: Optional[str] = Query(
        None,
        description="Locale code to filter concept names",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    List retired concepts
    """
    return concepts.get_retired_concepts(
        db,
        skip=skip,
        limit=limit,
        locale=locale,
    )


@router.get("/search", response_model=List[ConceptResponse])
async def search_concepts(
    name: str = Query(
        ...,
        description="Search term for concept name or description",
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
    locale: Optional[str] = Query(
        None,
        description="Locale code to filter concept names",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Search concepts by name or description
    """
    return concepts.search_concepts(
        db,
        name=name,
        skip=skip,
        limit=limit,
        locale=locale,
    )


@router.get(
    "/class/{concept_class}",
    response_model=List[ConceptResponse],
)
async def get_concepts_by_class(
    concept_class: str = Path(..., description="Concept class"),
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
    locale: Optional[str] = Query(
        None,
        description="Locale code to filter concept names",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get concepts by class
    """
    return concepts.get_concepts_by_class(
        db,
        class_identifier=concept_class,
        skip=skip,
        limit=limit,
        locale=locale,
    )


@router.get(
    "/datatype/{datatype}",
    response_model=List[ConceptResponse],
)
async def get_concepts_by_datatype(
    datatype: str = Path(..., description="Concept datatype"),
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
    locale: Optional[str] = Query(
        None,
        description="Locale code to filter concept names",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get concepts by datatype
    """
    return concepts.get_concepts_by_datatype(
        db,
        datatype=datatype,
        skip=skip,
        limit=limit,
        locale=locale,
    )


@router.get(
    "/short-name/{short_name}",
    response_model=ConceptResponse,
)
async def get_concept_by_short_name(
    short_name: str = Path(
        ...,
        description="Concept short name",
    ),
    locale: Optional[str] = Query(
        None,
        description="Locale code to filter concept names",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get concept by short name
    """
    concept = concepts.get_by_short_name(db, short_name, locale=locale)
    if not concept:
        raise HTTPException(
            status_code=404,
            detail="Concept not found",
        )
    return concept


@router.get("/{concept_id}", response_model=ConceptResponse)
async def get_concept(
    concept_id: int,
    locale: Optional[str] = Query(
        None,
        description="Locale code to filter concept names",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get concept by ID
    """
    concept = concepts.get(db, concept_id, locale=locale)
    if not concept:
        raise HTTPException(
            status_code=404,
            detail="Concept not found",
        )
    return concept


@router.get("/uuid/{uuid}", response_model=ConceptResponse)
async def get_concept_by_uuid(
    uuid: str,
    locale: Optional[str] = Query(
        None,
        description="Locale code to filter concept names",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get concept by UUID
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    concept = concepts.get_by_uuid(db, uuid, locale=locale)
    if not concept:
        raise HTTPException(
            status_code=404,
            detail="Concept not found",
        )
    return concept


@router.patch(
    "/{concept_id}",
    response_model=ConceptUpdateResponse,
)
async def update_concept_partial(
    concept_id: int,
    concept_update: ConceptUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update concept partially (PATCH)
    """
    try:
        updated_concept = concepts.update_partial(
            db,
            concept_id,
            concept_update,
        )
        if not updated_concept:
            raise HTTPException(
                status_code=404,
                detail="Concept not found",
            )

        # Get updated fields for response
        original_concept = concepts.get(db, concept_id)
        updated_fields = concepts.get_updated_fields(
            original_concept,
            updated_concept,
        )

        response_payload = ConceptUpdateResponse(
            concept=updated_concept,
            updated_fields=updated_fields,
        )

        try:
            result = await trigger_search_index_update(
                resource="concept",
                uuid=updated_concept.uuid,
                async_mode=False,
            )
            response_payload.search_index_update_status = result.status_text()
            if not result.success:
                logger.warning(
                    "Search index update returned failure for concept %s: %s",
                    getattr(updated_concept, "uuid", "unknown"),
                    result.message,
                )
        except Exception as exc:  # pragma: no cover - defensive logging
            response_payload.search_index_update_status = f"failed: {exc}"
            logger.warning(
                "Search index update invocation failed for concept %s: %s",
                getattr(updated_concept, "uuid", "unknown"),
                exc,
            )

        return response_payload
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update concept {str(e)}",
        )


@router.patch(
    "/uuid/{uuid}",
    response_model=ConceptUpdateResponse,
)
async def update_concept_partial_by_uuid(
    uuid: str,
    concept_update: ConceptUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update concept partially by UUID (PATCH)
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    try:
        updated_concept = concepts.update_partial_by_uuid(
            db,
            uuid,
            concept_update,
        )
        if not updated_concept:
            raise HTTPException(
                status_code=404,
                detail="Concept not found",
            )

        # Get updated fields for response
        original_concept = concepts.get_by_uuid(db, uuid)
        updated_fields = concepts.get_updated_fields(
            original_concept,
            updated_concept,
        )

        response_payload = ConceptUpdateResponse(
            concept=updated_concept,
            updated_fields=updated_fields,
        )

        try:
            result = await trigger_search_index_update(
                resource="concept",
                uuid=updated_concept.uuid,
                async_mode=False,
            )
            response_payload.search_index_update_status = result.status_text()
            if not result.success:
                logger.warning(
                    "Search index update returned failure for concept %s: %s",
                    getattr(updated_concept, "uuid", "unknown"),
                    result.message,
                )
        except Exception as exc:  # pragma: no cover - defensive logging
            response_payload.search_index_update_status = f"failed: {exc}"
            logger.warning(
                "Search index update invocation failed for concept %s: %s",
                getattr(updated_concept, "uuid", "unknown"),
                exc,
            )

        return response_payload
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update concept {str(e)}",
        )


@router.put(
    "/{concept_id}",
    response_model=ConceptUpdateResponse,
)
async def update_concept_full(
    concept_id: int,
    concept_replace: ConceptReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update concept completely (PUT)
    """
    try:
        updated_concept = concepts.update_full(
            db,
            concept_id,
            concept_replace,
        )
        if not updated_concept:
            raise HTTPException(
                status_code=404,
                detail="Concept not found",
            )

        # Get updated fields for response
        original_concept = concepts.get(db, concept_id)
        updated_fields = concepts.get_updated_fields(
            original_concept,
            updated_concept,
        )

        response_payload = ConceptUpdateResponse(
            concept=updated_concept,
            updated_fields=updated_fields,
        )

        try:
            result = await trigger_search_index_update(
                resource="concept",
                uuid=updated_concept.uuid,
                async_mode=False,
            )
            response_payload.search_index_update_status = result.status_text()
            if not result.success:
                logger.warning(
                    "Search index update returned failure for concept %s: %s",
                    getattr(updated_concept, "uuid", "unknown"),
                    result.message,
                )
        except Exception as exc:  # pragma: no cover - defensive logging
            response_payload.search_index_update_status = f"failed: {exc}"
            logger.warning(
                "Search index update invocation failed for concept %s: %s",
                getattr(updated_concept, "uuid", "unknown"),
                exc,
            )

        return response_payload
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update concept {str(e)}",
        )


@router.put(
    "/uuid/{uuid}",
    response_model=ConceptUpdateResponse,
)
async def update_concept_full_by_uuid(
    uuid: str,
    concept_replace: ConceptReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update concept completely by UUID (PUT)
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    try:
        updated_concept = concepts.update_full_by_uuid(
            db,
            uuid,
            concept_replace,
        )
        if not updated_concept:
            raise HTTPException(
                status_code=404,
                detail="Concept not found",
            )

        # Get updated fields for response
        original_concept = concepts.get_by_uuid(db, uuid)
        updated_fields = concepts.get_updated_fields(
            original_concept,
            updated_concept,
        )

        response_payload = ConceptUpdateResponse(
            concept=updated_concept,
            updated_fields=updated_fields,
        )

        try:
            result = await trigger_search_index_update(
                resource="concept",
                uuid=updated_concept.uuid,
                async_mode=False,
            )
            response_payload.search_index_update_status = result.status_text()
            if not result.success:
                logger.warning(
                    "Search index update returned failure for concept %s: %s",
                    getattr(updated_concept, "uuid", "unknown"),
                    result.message,
                )
        except Exception as exc:  # pragma: no cover - defensive logging
            response_payload.search_index_update_status = f"failed: {exc}"
            logger.warning(
                "Search index update invocation failed for concept %s: %s",
                getattr(updated_concept, "uuid", "unknown"),
                exc,
            )

        return response_payload
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update concept {str(e)}",
        )


@router.post("/{concept_id}/retire", response_model=ConceptResponse)
async def retire_concept(
    concept_id: int,
    retired_by: int = Query(
        ...,
        description="ID of the user retiring the concept",
    ),
    reason: Optional[str] = Query(
        None,
        description="Reason for retirement",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Retire a concept
    """
    try:
        retired_concept = concepts.retire_concept(
            db,
            concept_id,
            retired_by,
            reason,
        )
        if not retired_concept:
            raise HTTPException(status_code=404, detail="Concept not found")
        return retired_concept
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to retire concept {str(e)}",
        )


@router.post("/{concept_id}/unretire", response_model=ConceptResponse)
async def unretire_concept(
    concept_id: int,
    unretired_by: int = Query(
        ...,
        description="ID of the user unretiring the concept",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Unretire a concept
    """
    try:
        unretired_concept = concepts.unretire_concept(
            db,
            concept_id,
            unretired_by,
        )
        if not unretired_concept:
            raise HTTPException(status_code=404, detail="Concept not found")
        return unretired_concept
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to unretire concept {str(e)}",
        )
