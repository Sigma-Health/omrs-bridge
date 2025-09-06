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
from app.crud import order_types
from app.schemas import (
    OrderTypeCreate,
    OrderTypeUpdate,
    OrderTypeReplace,
    OrderTypeResponse,
    OrderTypeUpdateResponse,
)
from app.utils import validate_uuid

router = APIRouter(tags=["order-types"])


@router.post("/", response_model=OrderTypeResponse)
async def create_order_type(
    order_type_create: OrderTypeCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Create a new order type
    """
    try:
        return order_types.create(db, order_type_create)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create order type: {str(e)}",
        )


@router.get("/", response_model=List[OrderTypeResponse])
async def list_order_types(
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
    List order types with pagination
    """
    return order_types.list(db, skip=skip, limit=limit)


@router.get("/active", response_model=List[OrderTypeResponse])
async def list_active_order_types(
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
    List active (non-retired) order types
    """
    return order_types.get_active_order_types(
        db,
        skip=skip,
        limit=limit,
    )


@router.get("/retired", response_model=List[OrderTypeResponse])
async def list_retired_order_types(
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
    List retired order types
    """
    return order_types.get_retired_order_types(
        db,
        skip=skip,
        limit=limit,
    )


@router.get("/search", response_model=List[OrderTypeResponse])
async def search_order_types(
    search_term: str = Query(
        ...,
        description="Search term for order type name or description",
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
    Search order types by name or description
    """
    return order_types.search_order_types(
        db,
        search_term=search_term,
        skip=skip,
        limit=limit,
    )


@router.get("/java-class/{java_class_name}", response_model=List[OrderTypeResponse])
async def get_order_types_by_java_class(
    java_class_name: str = Path(..., description="Java class name"),
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
    Get order types by Java class name
    """
    return order_types.get_by_java_class(
        db,
        java_class_name=java_class_name,
        skip=skip,
        limit=limit,
    )


@router.get("/parent/{parent_id}", response_model=List[OrderTypeResponse])
async def get_order_types_by_parent(
    parent_id: int = Path(..., description="Parent order type ID"),
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
    Get child order types by parent ID
    """
    return order_types.get_by_parent(
        db,
        parent_id=parent_id,
        skip=skip,
        limit=limit,
    )


@router.get("/root", response_model=List[OrderTypeResponse])
async def get_root_order_types(
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
    Get root order types (no parent)
    """
    return order_types.get_root_order_types(
        db,
        skip=skip,
        limit=limit,
    )


@router.get("/name/{name}", response_model=OrderTypeResponse)
async def get_order_type_by_name(
    name: str = Path(
        ...,
        description="Order type name",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get order type by name
    """
    order_type = order_types.get_by_name(db, name)
    if not order_type:
        raise HTTPException(
            status_code=404,
            detail="Order type not found",
        )
    return order_type


@router.get("/{order_type_id}", response_model=OrderTypeResponse)
async def get_order_type(
    order_type_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get order type by ID
    """
    order_type = order_types.get(db, order_type_id)
    if not order_type:
        raise HTTPException(
            status_code=404,
            detail="Order type not found",
        )
    return order_type


@router.get("/uuid/{uuid}", response_model=OrderTypeResponse)
async def get_order_type_by_uuid(
    uuid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get order type by UUID
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    order_type = order_types.get_by_uuid(db, uuid)
    if not order_type:
        raise HTTPException(
            status_code=404,
            detail="Order type not found",
        )
    return order_type


@router.patch(
    "/{order_type_id}",
    response_model=OrderTypeUpdateResponse,
)
async def update_order_type_partial(
    order_type_id: int,
    order_type_update: OrderTypeUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update order type partially (PATCH)
    """
    try:
        updated_order_type = order_types.update_partial(
            db,
            order_type_id,
            order_type_update,
        )
        if not updated_order_type:
            raise HTTPException(
                status_code=404,
                detail="Order type not found",
            )

        # Get updated fields for response
        original_order_type = order_types.get(db, order_type_id)
        updated_fields = order_types.get_updated_fields(
            original_order_type,
            updated_order_type,
        )

        return OrderTypeUpdateResponse(
            success=True,
            message="Order type updated successfully",
            order_type_id=order_type_id,
            updated_fields=updated_fields,
            order_type=updated_order_type,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update order type: {str(e)}",
        )


@router.patch(
    "/uuid/{uuid}",
    response_model=OrderTypeUpdateResponse,
)
async def update_order_type_partial_by_uuid(
    uuid: str,
    order_type_update: OrderTypeUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update order type partially by UUID (PATCH)
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    try:
        updated_order_type = order_types.update_partial_by_uuid(
            db,
            uuid,
            order_type_update,
        )
        if not updated_order_type:
            raise HTTPException(
                status_code=404,
                detail="Order type not found",
            )

        # Get updated fields for response
        original_order_type = order_types.get_by_uuid(db, uuid)
        updated_fields = order_types.get_updated_fields(
            original_order_type,
            updated_order_type,
        )

        return OrderTypeUpdateResponse(
            success=True,
            message="Order type updated successfully",
            order_type_id=updated_order_type.order_type_id,
            updated_fields=updated_fields,
            order_type=updated_order_type,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update order type: {str(e)}",
        )


@router.put(
    "/{order_type_id}",
    response_model=OrderTypeUpdateResponse,
)
async def update_order_type_full(
    order_type_id: int,
    order_type_replace: OrderTypeReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update order type completely (PUT)
    """
    try:
        updated_order_type = order_types.update_full(
            db,
            order_type_id,
            order_type_replace,
        )
        if not updated_order_type:
            raise HTTPException(
                status_code=404,
                detail="Order type not found",
            )

        # Get updated fields for response
        original_order_type = order_types.get(db, order_type_id)
        updated_fields = order_types.get_updated_fields(
            original_order_type,
            updated_order_type,
        )

        return OrderTypeUpdateResponse(
            success=True,
            message="Order type updated successfully",
            order_type_id=order_type_id,
            updated_fields=updated_fields,
            order_type=updated_order_type,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update order type: {str(e)}",
        )


@router.put(
    "/uuid/{uuid}",
    response_model=OrderTypeUpdateResponse,
)
async def update_order_type_full_by_uuid(
    uuid: str,
    order_type_replace: OrderTypeReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update order type completely by UUID (PUT)
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    try:
        updated_order_type = order_types.update_full_by_uuid(
            db,
            uuid,
            order_type_replace,
        )
        if not updated_order_type:
            raise HTTPException(
                status_code=404,
                detail="Order type not found",
            )

        # Get updated fields for response
        original_order_type = order_types.get_by_uuid(db, uuid)
        updated_fields = order_types.get_updated_fields(
            original_order_type,
            updated_order_type,
        )

        return OrderTypeUpdateResponse(
            success=True,
            message="Order type updated successfully",
            order_type_id=updated_order_type.order_type_id,
            updated_fields=updated_fields,
            order_type=updated_order_type,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update order type: {str(e)}",
        )


@router.post("/{order_type_id}/retire", response_model=OrderTypeResponse)
async def retire_order_type(
    order_type_id: int,
    retired_by: int = Query(
        ...,
        description="ID of the user retiring the order type",
    ),
    retire_reason: Optional[str] = Query(
        None,
        description="Reason for retirement",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Retire an order type
    """
    try:
        retired_order_type = order_types.retire_order_type(
            db,
            order_type_id,
            retired_by,
            retire_reason,
        )
        if not retired_order_type:
            raise HTTPException(status_code=404, detail="Order type not found")
        return retired_order_type
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to retire order type: {str(e)}",
        )


@router.post("/{order_type_id}/unretire", response_model=OrderTypeResponse)
async def unretire_order_type(
    order_type_id: int,
    unretired_by: int = Query(
        ...,
        description="ID of the user unretiring the order type",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Unretire an order type
    """
    try:
        unretired_order_type = order_types.unretire_order_type(
            db,
            order_type_id,
            unretired_by,
        )
        if not unretired_order_type:
            raise HTTPException(status_code=404, detail="Order type not found")
        return unretired_order_type
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to unretire order type: {str(e)}",
        )
