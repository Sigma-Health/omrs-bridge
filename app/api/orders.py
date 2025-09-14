import logging
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Path,
)
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.auth import get_current_api_key
from app.crud import orders
from app.schemas import (
    OrderUpdate,
    OrderReplace,
    OrderResponse,
    OrderUpdateResponse,
    OrderConceptDetailsResponse,
)
from app.utils import validate_uuid

logger = logging.getLogger(__name__)

router = APIRouter(tags=["orders"])


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_create: OrderReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Create a new order
    """
    try:
        return orders.create(db, order_create)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create order: {str(e)}",
        )


@router.get("/", response_model=List[OrderResponse])
async def list_orders(
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
    List orders with pagination
    """
    return orders.list(
        db,
        skip=skip,
        limit=limit,
    )


@router.get("/active", response_model=List[OrderResponse])
async def list_active_orders(
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
    List active (non-voided) orders
    """
    return orders.get_active_orders(
        db,
        skip=skip,
        limit=limit,
    )


@router.get("/voided", response_model=List[OrderResponse])
async def list_voided_orders(
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
    List voided orders
    """
    return orders.get_voided_orders(
        db,
        skip=skip,
        limit=limit,
    )


@router.get("/patient/{patient_id}", response_model=List[OrderResponse])
async def get_orders_by_patient(
    patient_id: int,
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
    Get orders for a specific patient
    """
    return orders.get_orders_by_patient(
        db,
        patient_id=patient_id,
        skip=skip,
        limit=limit,
    )


@router.get("/urgency/{urgency}", response_model=List[OrderResponse])
async def get_orders_by_urgency(
    urgency: str = Path(
        ...,
        description="Urgency level: ROUTINE, STAT, ASAP, etc.",
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
    Get orders by urgency level
    """
    return orders.get_orders_by_urgency(
        db,
        urgency=urgency,
        skip=skip,
        limit=limit,
    )


@router.get("/orderer/{orderer_id}", response_model=List[OrderResponse])
async def get_orders_by_orderer(
    orderer_id: int,
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
    Get orders by orderer (provider)
    """
    return orders.get_orders_by_orderer(
        db,
        orderer=orderer_id,
        skip=skip,
        limit=limit,
    )


@router.get("/encounter/{encounter_id}", response_model=List[OrderResponse])
async def get_orders_by_encounter(
    encounter_id: int,
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
    Get orders for a specific encounter
    """
    return orders.get_orders_by_encounter(
        db,
        encounter_id=encounter_id,
        skip=skip,
        limit=limit,
    )


@router.get("/concept/{concept_id}", response_model=List[OrderResponse])
async def get_orders_by_concept(
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
    Get orders for a specific concept
    """
    return orders.get_orders_by_concept(
        db,
        concept_id=concept_id,
        skip=skip,
        limit=limit,
    )


@router.get("/type/{order_type_id}", response_model=List[OrderResponse])
async def get_orders_by_type(
    order_type_id: int,
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
    Get orders by order type
    """
    return orders.get_orders_by_type(
        db,
        order_type_id=order_type_id,
        skip=skip,
        limit=limit,
    )


@router.get("/status/{status}", response_model=List[OrderResponse])
async def get_orders_by_status(
    status: str = Path(
        ...,
        description="Fulfiller status",
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
    Get orders by fulfiller status
    """
    return orders.get_orders_by_status(
        db,
        status=status,
        skip=skip,
        limit=limit,
    )


@router.get("/action/{action}", response_model=List[OrderResponse])
async def get_orders_by_action(
    action: str = Path(
        ...,
        description="Order action: NEW, REVISE, DISCONTINUE, etc.",
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
    Get orders by order action
    """
    return orders.get_orders_by_action(
        db,
        action=action,
        skip=skip,
        limit=limit,
    )


@router.get("/number/{order_number}", response_model=OrderResponse)
async def get_order_by_number(
    order_number: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get order by order number
    """
    order = orders.get_by_order_number(db, order_number)
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )
    return order


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get order by ID
    """
    order = orders.get(db, order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )
    return order


@router.get("/{order_id}/enriched")
async def get_order_enriched(
    order_id: int = Path(..., description="Order ID"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get order by ID with enriched creator and patient information.
    This endpoint includes the names and UUIDs of both the creator and patient.
    """
    order_data = orders.get_order_with_person_info(db, order_id)
    if not order_data:
        raise HTTPException(status_code=404, detail="Order not found")
    return order_data


@router.get("/uuid/{uuid}", response_model=OrderResponse)
async def get_order_by_uuid(
    uuid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get order by UUID
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    order = orders.get_by_uuid(db, uuid)
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )
    return order


@router.patch("/{order_id}", response_model=OrderUpdateResponse)
async def update_order_partial(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update order partially (PATCH)
    """
    try:
        updated_order = orders.update_partial(
            db,
            order_id,
            order_update,
        )
        if not updated_order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        # Get updated fields for response
        original_order = orders.get(db, order_id)
        updated_fields = orders.get_updated_fields(
            original_order,
            updated_order,
        )

        return OrderUpdateResponse(
            order=updated_order,
            updated_fields=updated_fields,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update order: {str(e)}",
        )


@router.patch("/uuid/{uuid}", response_model=OrderUpdateResponse)
async def update_order_partial_by_uuid(
    uuid: str,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update order partially by UUID (PATCH)
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    try:
        updated_order = orders.update_partial_by_uuid(db, uuid, order_update)
        if not updated_order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        # Get updated fields for response
        original_order = orders.get_by_uuid(db, uuid)
        updated_fields = orders.get_updated_fields(
            original_order,
            updated_order,
        )

        return OrderUpdateResponse(
            order=updated_order,
            updated_fields=updated_fields,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update order: {str(e)}",
        )


@router.put("/{order_id}", response_model=OrderUpdateResponse)
async def update_order_full(
    order_id: int,
    order_replace: OrderReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update order completely (PUT)
    """
    try:
        updated_order = orders.update_full(
            db,
            order_id,
            order_replace,
        )
        if not updated_order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        # Get updated fields for response
        original_order = orders.get(db, order_id)
        updated_fields = orders.get_updated_fields(
            original_order,
            updated_order,
        )

        return OrderUpdateResponse(
            order=updated_order,
            updated_fields=updated_fields,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update order: {str(e)}",
        )


@router.put("/uuid/{uuid}", response_model=OrderUpdateResponse)
async def update_order_full_by_uuid(
    uuid: str,
    order_replace: OrderReplace,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Update order completely by UUID (PUT)
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    try:
        updated_order = orders.update_full_by_uuid(
            db,
            uuid,
            order_replace,
        )
        if not updated_order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        # Get updated fields for response
        original_order = orders.get_by_uuid(db, uuid)
        updated_fields = orders.get_updated_fields(
            original_order,
            updated_order,
        )

        return OrderUpdateResponse(
            order=updated_order,
            updated_fields=updated_fields,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update order: {str(e)}",
        )


@router.post("/{order_id}/void", response_model=OrderResponse)
async def void_order(
    order_id: int,
    voided_by: int = Query(
        ...,
        description="ID of the user voiding the order",
    ),
    reason: Optional[str] = Query(
        None,
        description="Reason for voiding",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Void an order
    """
    try:
        voided_order = orders.void_order(
            db,
            order_id,
            voided_by,
            reason,
        )
        if not voided_order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )
        return voided_order
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to void order: {str(e)}",
        )


@router.post("/{order_id}/unvoid", response_model=OrderResponse)
async def unvoid_order(
    order_id: int,
    unvoided_by: int = Query(
        ...,
        description="ID of the user unvoiding the order",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Unvoid an order
    """
    try:
        unvoided_order = orders.unvoid_order(
            db,
            order_id,
            unvoided_by,
        )
        if not unvoided_order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )
        return unvoided_order
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to unvoid order: {str(e)}",
        )


@router.get(
    "/type/{order_type_id}/visit/{visit_id}",
    response_model=List[OrderResponse],
)
async def get_orders_by_type_and_visit_id(
    order_type_id: int = Path(
        ...,
        description="Order type ID",
    ),
    visit_id: int = Path(
        ...,
        description="Visit ID",
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
    Get all orders of a specific order type for a particular visit (by visit ID)
    """
    try:
        orders_list = orders.get_orders_by_type_and_visit_id(
            db,
            order_type_id=order_type_id,
            visit_id=visit_id,
            skip=skip,
            limit=limit,
        )
        return orders_list
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get orders: {str(e)}",
        )


@router.get(
    "/type/{order_type_id}/visit/uuid/{visit_uuid}",
    response_model=List[OrderResponse],
)
async def get_orders_by_type_and_visit_uuid(
    order_type_id: int = Path(..., description="Order type ID"),
    visit_uuid: str = Path(..., description="Visit UUID"),
    skip: int = Query(0, ge=0, description="# of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="# of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get all orders of a specific order type for a particular visit
    Use visit UUID to get orders
    """
    try:
        # Validate UUID format
        if not validate_uuid(visit_uuid):
            raise HTTPException(
                status_code=400,
                detail="Invalid visit UUID format",
            )

        return orders.get_orders_by_type_and_visit_uuid(
            db,
            order_type_id=order_type_id,
            visit_uuid=visit_uuid,
            skip=skip,
            limit=limit,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get orders: {str(e)}",
        )


@router.get("/visit/{visit_id}", response_model=List[OrderResponse])
async def get_orders_by_visit_id(
    visit_id: int = Path(..., description="Visit ID"),
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
    Get all orders for a particular visit (by visit ID)
    """
    try:
        orders_list = orders.get_orders_by_visit_id(
            db,
            visit_id=visit_id,
            skip=skip,
            limit=limit,
        )
        return orders_list
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get orders: {str(e)}",
        )


@router.get(
    "/visit/uuid/{visit_uuid}",
    response_model=List[OrderResponse],
)
async def get_orders_by_visit_uuid(
    visit_uuid: str = Path(..., description="Visit UUID"),
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
    Get all orders for a particular visit (by visit UUID)
    """
    try:
        # Validate UUID format
        if not validate_uuid(visit_uuid):
            raise HTTPException(
                status_code=400,
                detail="Invalid visit UUID format",
            )

        orders_list = orders.get_orders_by_visit_uuid(
            db,
            visit_uuid=visit_uuid,
            skip=skip,
            limit=limit,
        )

        return orders_list
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting orders for visit UUID {visit_uuid}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get orders: {str(e)}",
        )


@router.get(
    "/order-concept-details",
    response_model=OrderConceptDetailsResponse,
    summary="Get comprehensive order and concept details",
    description="""
    Get detailed information about an order and its associated concept, 
    including orderer info, patient info, concept details, answers, and set members
    """,
    tags=["orders"],
)
async def get_order_and_concept_details(
    order_uuid: str = Query(
        ...,
        description="Order UUID",
        example="7683e916-f048-49bf-b9dc-3f218bba22f6",
    ),
    concept_uuid: str = Query(
        ...,
        description="Concept UUID",
        example="1643AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get comprehensive order and concept details by UUIDs.

    This endpoint provides:
    - Complete order information
    - Orderer details (provider + person info)
    - Patient details (person info)
    - Comprehensive concept details including:
      - Concept metadata (id, uuid, name, description, short_name)
      - Datatype information
      - Concept class information
      - Concept answers (if any)
      - Set members (if concept is a set) with their metadata
    """
    logger.info(
        f"API: Getting order and concept details for order_uuid={order_uuid}, concept_uuid={concept_uuid}"
    )
    try:
        # Validate UUID formats
        logger.info("Validating UUID formats")
        if not validate_uuid(order_uuid):
            logger.error(f"Invalid order UUID format: {order_uuid}")
            raise HTTPException(
                status_code=400,
                detail="Invalid order UUID format",
            )

        if not validate_uuid(concept_uuid):
            logger.error(f"Invalid concept UUID format: {concept_uuid}")
            raise HTTPException(
                status_code=400,
                detail="Invalid concept UUID format",
            )

        logger.info("UUID validation passed, calling CRUD method")

        # Get comprehensive order and concept details
        logger.info("Calling CRUD method get_order_and_concept_details_by_uuids")
        order_concept_details = orders.get_order_and_concept_details_by_uuids(
            db,
            order_uuid=order_uuid,
            concept_uuid=concept_uuid,
        )

        if not order_concept_details:
            logger.warning(
                f"CRUD method returned None for order_uuid={order_uuid}, concept_uuid={concept_uuid}"
            )
            raise HTTPException(
                status_code=404,
                detail="Order or concept not found",
            )

        logger.info(
            f"CRUD method returned data with {len(order_concept_details)} fields"
        )
        logger.info(f"Response keys: {list(order_concept_details.keys())}")

        # Try to serialize the response to check for validation issues
        try:
            from app.schemas import OrderConceptDetailsResponse

            # This will validate the response structure
            validated_response = OrderConceptDetailsResponse(**order_concept_details)
            logger.info("Response validation successful")
            return validated_response.dict()
        except Exception as validation_error:
            logger.error(f"Response validation failed: {validation_error}")
            logger.error(f"Response data: {order_concept_details}")
            raise HTTPException(
                status_code=422,
                detail=f"Response validation failed: {str(validation_error)}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error getting order and concept details for order_uuid={order_uuid}, concept_uuid={concept_uuid}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get order and concept details: {str(e)}",
        )
