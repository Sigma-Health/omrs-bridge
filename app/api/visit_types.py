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
from app.crud import visit_types
from app.schemas import (
    VisitTypeCreate,
    VisitTypeUpdate,
    VisitTypeReplace,
    VisitTypeResponse,
    VisitTypeUpdateResponse,
)
from app.utils import validate_uuid

router = APIRouter(tags=["visit-types"])


@router.post("/", response_model=VisitTypeResponse)
async def create_visit_type(
    visit_type_create: VisitTypeCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Create a new visit type
    """
    try:
        return visit_types.create(db, visit_type_create)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create visit type: {str(e)}",
        )


@router.get("/", response_model=List[VisitTypeResponse])
async def list_visit_types(
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
    List visit types with pagination
    """
    return visit_types.list(db, skip=skip, limit=limit)


@router.get("/active", response_model=List[VisitTypeResponse])
async def list_active_visit_types(
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
    List active (non-retired) visit types
    """
    return visit_types.get_active_visit_types(
        db,
        skip=skip,
        limit=limit,
    )


@router.get("/retired", response_model=List[VisitTypeResponse])
async def list_retired_visit_types(
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
    List retired visit types
    """
    return visit_types.get_retired_visit_types(
        db,
        skip=skip,
        limit=limit,
    )


@router.get("/search", response_model=List[VisitTypeResponse])
async def search_visit_types(
    search_term: str = Query(
        ...,
        description="Search term for visit type name or description",
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
    Search visit types by name or description
    """
    return visit_types.search_visit_types(
        db,
        search_term=search_term,
        skip=skip,
        limit=limit,
    )


@router.get("/name/{name}", response_model=VisitTypeResponse)
async def get_visit_type_by_name(
    name: str = Path(
        ...,
        description="Visit type name",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get visit type by name
    """
    visit_type = visit_types.get_by_name(db, name)
    if not visit_type:
        raise HTTPException(
            status_code=404,
            detail="Visit type not found",
        )
    return visit_type


@router.get("/{visit_type_id}", response_model=VisitTypeResponse)
async def get_visit_type(
    visit_type_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get visit type by ID
    """
    visit_type = visit_types.get(db, visit_type_id)
    if not visit_type:
        raise HTTPException(
            status_code=404,
            detail="Visit type not found",
        )
    return visit_type


@router.get("/uuid/{uuid}", response_model=VisitTypeResponse)
async def get_visit_type_by_uuid(
    uuid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get visit type by UUID
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    visit_type = visit_types.get_by_uuid(db, uuid)
    if not visit_type:
        raise HTTPException(
            status_code=404,
            detail="Visit type not found",
        )
    return visit_type


@router.patch(
    "/{visit_type_id}",
    response_model=VisitTypeUpdateResponse,
)
async def update_visit_type_partial(
    visit_type_id: int,
    visit_type_update: VisitTypeUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update visit type partially (PATCH)
    """
    try:
        updated_visit_type = visit_types.update_partial(
            db,
            visit_type_id,
            visit_type_update,
        )
        if not updated_visit_type:
            raise HTTPException(
                status_code=404,
                detail="Visit type not found",
            )

        # Get updated fields for response
        original_visit_type = visit_types.get(db, visit_type_id)
        updated_fields = visit_types.get_updated_fields(
            original_visit_type,
            updated_visit_type,
        )

        return VisitTypeUpdateResponse(
            success=True,
            message="Visit type updated successfully",
            visit_type_id=visit_type_id,
            updated_fields=updated_fields,
            visit_type=updated_visit_type,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update visit type: {str(e)}",
        )


@router.patch(
    "/uuid/{uuid}",
    response_model=VisitTypeUpdateResponse,
)
async def update_visit_type_partial_by_uuid(
    uuid: str,
    visit_type_update: VisitTypeUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update visit type partially by UUID (PATCH)
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    try:
        updated_visit_type = visit_types.update_partial_by_uuid(
            db,
            uuid,
            visit_type_update,
        )
        if not updated_visit_type:
            raise HTTPException(
                status_code=404,
                detail="Visit type not found",
            )

        # Get updated fields for response
        original_visit_type = visit_types.get_by_uuid(db, uuid)
        updated_fields = visit_types.get_updated_fields(
            original_visit_type,
            updated_visit_type,
        )

        return VisitTypeUpdateResponse(
            success=True,
            message="Visit type updated successfully",
            visit_type_id=updated_visit_type.visit_type_id,
            updated_fields=updated_fields,
            visit_type=updated_visit_type,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update visit type: {str(e)}",
        )


@router.put(
    "/{visit_type_id}",
    response_model=VisitTypeUpdateResponse,
)
async def update_visit_type_full(
    visit_type_id: int,
    visit_type_replace: VisitTypeReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update visit type completely (PUT)
    """
    try:
        updated_visit_type = visit_types.update_full(
            db,
            visit_type_id,
            visit_type_replace,
        )
        if not updated_visit_type:
            raise HTTPException(
                status_code=404,
                detail="Visit type not found",
            )

        # Get updated fields for response
        original_visit_type = visit_types.get(db, visit_type_id)
        updated_fields = visit_types.get_updated_fields(
            original_visit_type,
            updated_visit_type,
        )

        return VisitTypeUpdateResponse(
            success=True,
            message="Visit type updated successfully",
            visit_type_id=visit_type_id,
            updated_fields=updated_fields,
            visit_type=updated_visit_type,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update visit type: {str(e)}",
        )


@router.put(
    "/uuid/{uuid}",
    response_model=VisitTypeUpdateResponse,
)
async def update_visit_type_full_by_uuid(
    uuid: str,
    visit_type_replace: VisitTypeReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update visit type completely by UUID (PUT)
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    try:
        updated_visit_type = visit_types.update_full_by_uuid(
            db,
            uuid,
            visit_type_replace,
        )
        if not updated_visit_type:
            raise HTTPException(
                status_code=404,
                detail="Visit type not found",
            )

        # Get updated fields for response
        original_visit_type = visit_types.get_by_uuid(db, uuid)
        updated_fields = visit_types.get_updated_fields(
            original_visit_type,
            updated_visit_type,
        )

        return VisitTypeUpdateResponse(
            success=True,
            message="Visit type updated successfully",
            visit_type_id=updated_visit_type.visit_type_id,
            updated_fields=updated_fields,
            visit_type=updated_visit_type,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update visit type: {str(e)}",
        )


@router.post("/{visit_type_id}/retire", response_model=VisitTypeResponse)
async def retire_visit_type(
    visit_type_id: int,
    retired_by: int = Query(
        ...,
        description="ID of the user retiring the visit type",
    ),
    retire_reason: Optional[str] = Query(
        None,
        description="Reason for retirement",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Retire a visit type
    """
    try:
        retired_visit_type = visit_types.retire_visit_type(
            db,
            visit_type_id,
            retired_by,
            retire_reason,
        )
        if not retired_visit_type:
            raise HTTPException(status_code=404, detail="Visit type not found")
        return retired_visit_type
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to retire visit type: {str(e)}",
        )


@router.post("/{visit_type_id}/unretire", response_model=VisitTypeResponse)
async def unretire_visit_type(
    visit_type_id: int,
    unretired_by: int = Query(
        ...,
        description="ID of the user unretiring the visit type",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Unretire a visit type
    """
    try:
        unretired_visit_type = visit_types.unretire_visit_type(
            db,
            visit_type_id,
            unretired_by,
        )
        if not unretired_visit_type:
            raise HTTPException(status_code=404, detail="Visit type not found")
        return unretired_visit_type
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to unretire visit type: {str(e)}",
        )

