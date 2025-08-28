from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth import get_current_api_key
from app.crud import (
    get_order, 
    get_order_by_uuid,
    update_order_partial, 
    update_order_partial_by_uuid,
    update_order_full,
    update_order_full_by_uuid,
    get_updated_fields
)
from app.schemas import (
    OrderUpdate, 
    OrderReplace, 
    OrderResponse, 
    OrderUpdateResponse,
    ErrorResponse
)
from app.models import Order
from app.utils import validate_uuid

router = APIRouter(tags=["orders"])


@router.patch(
    "/{uuid}",
    response_model=OrderUpdateResponse,
    summary="Update order partially",
    description="Update specific fields of an order using UUID (PATCH method)"
)
async def update_order_partial_endpoint(
    uuid: str,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Update an order partially using PATCH method.
    
    - **uuid**: The UUID of the order to update
    - **order_update**: The fields to update (only provided fields will be updated)
    
    Returns the updated order information.
    """
    # Validate UUID format
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: {uuid}. Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        )
    
    # Get original order for comparison
    original_order = get_order_by_uuid(db, uuid)
    if not original_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with UUID {uuid} not found"
        )
    
    # Update the order
    updated_order = update_order_partial_by_uuid(db, uuid, order_update)
    if not updated_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with UUID {uuid} not found"
        )
    
    # Get list of updated fields
    updated_fields = get_updated_fields(original_order, updated_order)
    
    return OrderUpdateResponse(
        success=True,
        message=f"Order {uuid} updated successfully",
        order_id=updated_order.order_id,
        updated_fields=updated_fields,
        order=OrderResponse.from_orm(updated_order)
    )


@router.put(
    "/{uuid}",
    response_model=OrderUpdateResponse,
    summary="Replace order completely",
    description="Replace all fields of an order using UUID (PUT method)"
)
async def update_order_full_endpoint(
    uuid: str,
    order_replace: OrderReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Replace an order completely using PUT method.
    
    - **uuid**: The UUID of the order to replace
    - **order_replace**: Complete order data (all required fields must be provided)
    
    Returns the updated order information.
    """
    # Validate UUID format
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: {uuid}. Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        )
    
    # Get original order for comparison
    original_order = get_order_by_uuid(db, uuid)
    if not original_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with UUID {uuid} not found"
        )
    
    # Update the order
    updated_order = update_order_full_by_uuid(db, uuid, order_replace)
    if not updated_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with UUID {uuid} not found"
        )
    
    # Get list of updated fields
    updated_fields = get_updated_fields(original_order, updated_order)
    
    return OrderUpdateResponse(
        success=True,
        message=f"Order {uuid} replaced successfully",
        order_id=updated_order.order_id,
        updated_fields=updated_fields,
        order=OrderResponse.from_orm(updated_order)
    )


@router.get(
    "/{uuid}",
    response_model=OrderResponse,
    summary="Get order by UUID",
    description="Retrieve an order by its UUID"
)
async def get_order_endpoint(
    uuid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get an order by its UUID.
    
    - **uuid**: The UUID of the order to retrieve
    
    Returns the order information.
    """
    # Validate UUID format
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid UUID format: {uuid}. Expected format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        )
    
    order = get_order_by_uuid(db, uuid)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with UUID {uuid} not found"
        )
    
    return OrderResponse.from_orm(order)


@router.get(
    "/",
    response_model=List[OrderResponse],
    summary="List orders",
    description="Retrieve a list of orders with pagination"
)
async def list_orders_endpoint(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    List orders with pagination.
    
    - **skip**: Number of orders to skip (for pagination)
    - **limit**: Maximum number of orders to return
    
    Returns a list of orders.
    """
    from app.crud import list_orders
    orders = list_orders(db, skip=skip, limit=limit)
    return [OrderResponse.from_orm(order) for order in orders] 