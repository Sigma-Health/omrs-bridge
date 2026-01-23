import logging
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Path,
)
from sqlalchemy.orm import Session

from app.auth import get_current_api_key
from app.database import get_db
from app.crud import drugs
from app.services.search_index import trigger_search_index_update
from app.schemas import (
    DrugCreate,
    DrugReplace,
    DrugUpdate,
    DrugResponse,
    DrugUpdateResponse,
)
from app.utils import validate_uuid


logger = logging.getLogger(__name__)

router = APIRouter(tags=["drugs"])


@router.post("/", response_model=DrugResponse)
async def create_drug(
    drug_create: DrugCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Create a new drug with the minimal required fields.
    """
    try:
        created_drug = drugs.create(db, drug_create)

        # Attempt to update the OpenMRS search index; failure should not block the response.
        status_text: Optional[str] = None
        try:
            result = await trigger_search_index_update(
                resource="drug",
                uuid=created_drug.uuid,
                async_mode=False,
            )
            status_text = result.status_text()
            if not result.success:
                logger.warning(
                    "Search index update returned failure for drug %s: %s",
                    getattr(created_drug, "uuid", "unknown"),
                    result.message,
                )
        except Exception as exc:  # pragma: no cover - defensive logging
            status_text = f"failed: {exc}"
            logger.warning(
                "Search index update invocation failed for drug %s: %s",
                getattr(created_drug, "uuid", "unknown"),
                exc,
            )

        response_payload = DrugResponse.model_validate(
            created_drug,
            from_attributes=True,
        )
        if status_text:
            response_payload.search_index_update_status = status_text

        return response_payload
    except Exception as exc:
        logger.error("Failed to create drug: %s", exc)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create drug: {exc}",
        )


@router.get("/", response_model=List[DrugResponse])
async def list_drugs(
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
    List drugs with pagination.
    """
    return drugs.list(
        db,
        skip=skip,
        limit=limit,
    )


@router.get("/active", response_model=List[DrugResponse])
async def list_active_drugs(
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
    List active (non-retired) drugs.
    """
    return drugs.get_active_drugs(
        db,
        skip=skip,
        limit=limit,
    )


@router.get("/retired", response_model=List[DrugResponse])
async def list_retired_drugs(
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
    List retired drugs.
    """
    return drugs.get_retired_drugs(
        db,
        skip=skip,
        limit=limit,
    )


@router.get("/search", response_model=List[DrugResponse])
async def search_drugs(
    name: str = Query(
        ...,
        description="Search term for the drug name",
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
    Search drugs by name.
    """
    return drugs.search_drugs(
        db,
        name=name,
        skip=skip,
        limit=limit,
    )


@router.get("/concept/{concept_id}", response_model=List[DrugResponse])
async def get_drugs_by_concept(
    concept_id: int,
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
    Get drugs associated with a specific concept.
    """
    return drugs.get_drugs_by_concept(
        db,
        concept_id=concept_id,
        skip=skip,
        limit=limit,
    )


@router.get("/creator/{creator}", response_model=List[DrugResponse])
async def get_drugs_by_creator(
    creator: int = Path(..., description="Creator (user) ID"),
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
    Get drugs created by a specific user.
    """
    return drugs.get_drugs_by_creator(
        db,
        creator=creator,
        skip=skip,
        limit=limit,
    )


@router.get("/{drug_id}", response_model=DrugResponse)
async def get_drug(
    drug_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get drug by ID.
    """
    drug = drugs.get(db, drug_id)
    if not drug:
        raise HTTPException(
            status_code=404,
            detail="Drug not found",
        )
    return drug


@router.get("/uuid/{uuid}", response_model=DrugResponse)
async def get_drug_by_uuid(
    uuid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get drug by UUID.
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    drug = drugs.get_by_uuid(db, uuid)
    if not drug:
        raise HTTPException(
            status_code=404,
            detail="Drug not found",
        )
    return drug


@router.patch("/{drug_id}", response_model=DrugUpdateResponse)
async def update_drug_partial(
    drug_id: int,
    drug_update: DrugUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Partially update a drug (PATCH).
    """
    update_data = drug_update.dict(exclude_unset=True)

    try:
        updated_drug = drugs.update_partial(
            db,
            drug_id,
            drug_update,
        )
        if not updated_drug:
            raise HTTPException(
                status_code=404,
                detail="Drug not found",
            )

        updated_fields = list(update_data.keys())

        return DrugUpdateResponse(
            success=True,
            message="Drug updated successfully",
            drug_id=updated_drug.drug_id,
            updated_fields=updated_fields,
            drug=updated_drug,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to partially update drug %s: %s", drug_id, exc)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update drug: {exc}",
        )


@router.patch("/uuid/{uuid}", response_model=DrugUpdateResponse)
async def update_drug_partial_by_uuid(
    uuid: str,
    drug_update: DrugUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Partially update a drug by UUID (PATCH).
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    update_data = drug_update.dict(exclude_unset=True)

    try:
        updated_drug = drugs.update_partial_by_uuid(
            db,
            uuid,
            drug_update,
        )
        if not updated_drug:
            raise HTTPException(
                status_code=404,
                detail="Drug not found",
            )

        updated_fields = list(update_data.keys())

        return DrugUpdateResponse(
            success=True,
            message="Drug updated successfully",
            drug_id=updated_drug.drug_id,
            updated_fields=updated_fields,
            drug=updated_drug,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to partially update drug %s: %s", uuid, exc)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update drug: {exc}",
        )


@router.put("/{drug_id}", response_model=DrugUpdateResponse)
async def update_drug_full(
    drug_id: int,
    drug_replace: DrugReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Replace a drug completely (PUT).
    """
    try:
        updated_drug = drugs.update_full(
            db,
            drug_id,
            drug_replace,
        )
        if not updated_drug:
            raise HTTPException(
                status_code=404,
                detail="Drug not found",
            )

        updated_fields = list(drug_replace.dict().keys())

        return DrugUpdateResponse(
            success=True,
            message="Drug replaced successfully",
            drug_id=updated_drug.drug_id,
            updated_fields=updated_fields,
            drug=updated_drug,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to replace drug %s: %s", drug_id, exc)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to replace drug: {exc}",
        )


@router.put("/uuid/{uuid}", response_model=DrugUpdateResponse)
async def update_drug_full_by_uuid(
    uuid: str,
    drug_replace: DrugReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Replace a drug completely by UUID (PUT).
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    try:
        updated_drug = drugs.update_full_by_uuid(
            db,
            uuid,
            drug_replace,
        )
        if not updated_drug:
            raise HTTPException(
                status_code=404,
                detail="Drug not found",
            )

        updated_fields = list(drug_replace.dict().keys())

        return DrugUpdateResponse(
            success=True,
            message="Drug replaced successfully",
            drug_id=updated_drug.drug_id,
            updated_fields=updated_fields,
            drug=updated_drug,
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to replace drug %s: %s", uuid, exc)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to replace drug: {exc}",
        )


@router.post("/{drug_id}/retire", response_model=DrugResponse)
async def retire_drug(
    drug_id: int,
    retired_by: int = Query(
        ...,
        description="ID of the user retiring the drug",
    ),
    reason: Optional[str] = Query(
        None,
        description="Optional reason for retirement",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Retire a drug by ID.
    """
    try:
        retired = drugs.retire_drug(
            db,
            drug_id,
            retired_by=retired_by,
            reason=reason,
        )
        if not retired:
            raise HTTPException(
                status_code=404,
                detail="Drug not found",
            )
        return retired
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to retire drug %s: %s", drug_id, exc)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to retire drug: {exc}",
        )


@router.post("/{drug_id}/unretire", response_model=DrugResponse)
async def unretire_drug(
    drug_id: int,
    unretired_by: Optional[int] = Query(
        None,
        description="ID of the user unretiring the drug",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Unretire a drug by ID.
    """
    try:
        unretired = drugs.unretire_drug(
            db,
            drug_id,
            unretired_by=unretired_by,
        )
        if not unretired:
            raise HTTPException(
                status_code=404,
                detail="Drug not found",
            )
        return unretired
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to unretire drug %s: %s", drug_id, exc)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to unretire drug: {exc}",
        )


@router.post("/uuid/{uuid}/retire", response_model=DrugResponse)
async def retire_drug_by_uuid(
    uuid: str,
    retired_by: int = Query(
        ...,
        description="ID of the user retiring the drug",
    ),
    reason: Optional[str] = Query(
        None,
        description="Optional reason for retirement",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Retire a drug by UUID.
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    try:
        retired = drugs.retire_drug_by_uuid(
            db,
            uuid,
            retired_by=retired_by,
            reason=reason,
        )
        if not retired:
            raise HTTPException(
                status_code=404,
                detail="Drug not found",
            )
        return retired
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to retire drug %s: %s", uuid, exc)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to retire drug: {exc}",
        )


@router.post("/uuid/{uuid}/unretire", response_model=DrugResponse)
async def unretire_drug_by_uuid(
    uuid: str,
    unretired_by: Optional[int] = Query(
        None,
        description="ID of the user unretiring the drug",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Unretire a drug by UUID.
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    try:
        unretired = drugs.unretire_drug_by_uuid(
            db,
            uuid,
            unretired_by=unretired_by,
        )
        if not unretired:
            raise HTTPException(
                status_code=404,
                detail="Drug not found",
            )
        return unretired
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Failed to unretire drug %s: %s", uuid, exc)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to unretire drug: {exc}",
        )
