from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.auth import get_current_api_key
from app.crud import orders
from app.schemas import (
    OrderUpdate, OrderReplace, OrderResponse, OrderUpdateResponse, ErrorResponse
)
from app.models import Order
from app.utils import validate_uuid

router = APIRouter(tags=["orders"])


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_create: OrderReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Create a new order
    """
    try:
        new_order = orders.create(db, order_create)
        return new_order
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create order: {str(e)}")


@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    List orders with pagination
    """
    orders_list = orders.list(db, skip=skip, limit=limit)
    return orders_list


@router.get("/active", response_model=List[OrderResponse])
async def list_active_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    List active (non-voided) orders
    """
    orders_list = orders.get_active_orders(db, skip=skip, limit=limit)
    return orders_list


@router.get("/voided", response_model=List[OrderResponse])
async def list_voided_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    List voided orders
    """
    orders_list = orders.get_voided_orders(db, skip=skip, limit=limit)
    return orders_list


@router.get("/patient/{patient_id}", response_model=List[OrderResponse])
async def get_orders_by_patient(
    patient_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get orders for a specific patient
    """
    orders_list = orders.get_orders_by_patient(db, patient_id=patient_id, skip=skip, limit=limit)
    return orders_list


@router.get("/urgency/{urgency}", response_model=List[OrderResponse])
async def get_orders_by_urgency(
    urgency: str = Path(..., description="Urgency level: ROUTINE, STAT, ASAP, etc."),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get orders by urgency level
    """
    orders_list = orders.get_orders_by_urgency(db, urgency=urgency, skip=skip, limit=limit)
    return orders_list


@router.get("/orderer/{orderer_id}", response_model=List[OrderResponse])
async def get_orders_by_orderer(
    orderer_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get orders by orderer (provider)
    """
    orders_list = orders.get_orders_by_orderer(db, orderer=orderer_id, skip=skip, limit=limit)
    return orders_list


@router.get("/encounter/{encounter_id}", response_model=List[OrderResponse])
async def get_orders_by_encounter(
    encounter_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get orders for a specific encounter
    """
    orders_list = orders.get_orders_by_encounter(db, encounter_id=encounter_id, skip=skip, limit=limit)
    return orders_list


@router.get("/concept/{concept_id}", response_model=List[OrderResponse])
async def get_orders_by_concept(
    concept_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get orders for a specific concept
    """
    orders_list = orders.get_orders_by_concept(db, concept_id=concept_id, skip=skip, limit=limit)
    return orders_list


@router.get("/type/{order_type_id}", response_model=List[OrderResponse])
async def get_orders_by_type(
    order_type_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get orders by order type
    """
    orders_list = orders.get_orders_by_type(db, order_type_id=order_type_id, skip=skip, limit=limit)
    return orders_list


@router.get("/status/{status}", response_model=List[OrderResponse])
async def get_orders_by_status(
    status: str = Path(..., description="Fulfiller status"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get orders by fulfiller status
    """
    orders_list = orders.get_orders_by_status(db, status=status, skip=skip, limit=limit)
    return orders_list


@router.get("/action/{action}", response_model=List[OrderResponse])
async def get_orders_by_action(
    action: str = Path(..., description="Order action: NEW, REVISE, DISCONTINUE, etc."),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get orders by order action
    """
    orders_list = orders.get_orders_by_action(db, action=action, skip=skip, limit=limit)
    return orders_list


@router.get("/number/{order_number}", response_model=OrderResponse)
async def get_order_by_number(
    order_number: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get order by order number
    """
    order = orders.get_by_order_number(db, order_number)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get order by ID
    """
    order = orders.get(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/uuid/{uuid}", response_model=OrderResponse)
async def get_order_by_uuid(
    uuid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Get order by UUID
    """
    if not validate_uuid(uuid):
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    order = orders.get_by_uuid(db, uuid)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.patch("/{order_id}", response_model=OrderUpdateResponse)
async def update_order_partial(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Update order partially (PATCH)
    """
    try:
        updated_order = orders.update_partial(db, order_id, order_update)
        if not updated_order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Get updated fields for response
        original_order = orders.get(db, order_id)
        updated_fields = orders.get_updated_fields(original_order, updated_order)
        
        return OrderUpdateResponse(
            order=updated_order,
            updated_fields=updated_fields
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update order: {str(e)}")


@router.patch("/uuid/{uuid}", response_model=OrderUpdateResponse)
async def update_order_partial_by_uuid(
    uuid: str,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Update order partially by UUID (PATCH)
    """
    if not validate_uuid(uuid):
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    try:
        updated_order = orders.update_partial_by_uuid(db, uuid, order_update)
        if not updated_order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Get updated fields for response
        original_order = orders.get_by_uuid(db, uuid)
        updated_fields = orders.get_updated_fields(original_order, updated_order)
        
        return OrderUpdateResponse(
            order=updated_order,
            updated_fields=updated_fields
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update order: {str(e)}")


@router.put("/{order_id}", response_model=OrderUpdateResponse)
async def update_order_full(
    order_id: int,
    order_replace: OrderReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Update order completely (PUT)
    """
    try:
        updated_order = orders.update_full(db, order_id, order_replace)
        if not updated_order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Get updated fields for response
        original_order = orders.get(db, order_id)
        updated_fields = orders.get_updated_fields(original_order, updated_order)
        
        return OrderUpdateResponse(
            order=updated_order,
            updated_fields=updated_fields
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update order: {str(e)}")


@router.put("/uuid/{uuid}", response_model=OrderUpdateResponse)
async def update_order_full_by_uuid(
    uuid: str,
    order_replace: OrderReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Update order completely by UUID (PUT)
    """
    if not validate_uuid(uuid):
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    try:
        updated_order = orders.update_full_by_uuid(db, uuid, order_replace)
        if not updated_order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Get updated fields for response
        original_order = orders.get_by_uuid(db, uuid)
        updated_fields = orders.get_updated_fields(original_order, updated_order)
        
        return OrderUpdateResponse(
            order=updated_order,
            updated_fields=updated_fields
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update order: {str(e)}")


@router.post("/{order_id}/void", response_model=OrderResponse)
async def void_order(
    order_id: int,
    voided_by: int = Query(..., description="ID of the user voiding the order"),
    reason: Optional[str] = Query(None, description="Reason for voiding"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Void an order
    """
    try:
        voided_order = orders.void_order(db, order_id, voided_by, reason)
        if not voided_order:
            raise HTTPException(status_code=404, detail="Order not found")
        return voided_order
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to void order: {str(e)}")


@router.post("/{order_id}/unvoid", response_model=OrderResponse)
async def unvoid_order(
    order_id: int,
    unvoided_by: int = Query(..., description="ID of the user unvoiding the order"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key)
):
    """
    Unvoid an order
    """
    try:
        unvoided_order = orders.unvoid_order(db, order_id, unvoided_by)
        if not unvoided_order:
            raise HTTPException(status_code=404, detail="Order not found")
        return unvoided_order
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to unvoid order: {str(e)}")