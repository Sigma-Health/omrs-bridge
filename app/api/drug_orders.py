from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.auth import get_current_api_key
from app.crud import orders
from app.database import get_db
from app.schemas import DrugOrderCreateForVisit, OrderResponse
from app.utils import validate_uuid

router = APIRouter(tags=["drug-orders"])


@router.get("/visit/uuid/{visit_uuid}", response_model=List[OrderResponse])
async def list_drug_orders_by_visit_uuid(
    visit_uuid: str = Path(..., description="Visit UUID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """List drug orders for a visit UUID."""
    if not validate_uuid(visit_uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid visit UUID format",
        )

    try:
        return orders.get_orders_by_type_and_visit_uuidx(
            db=db,
            order_type_id=2,
            visit_uuid=visit_uuid,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get drug orders for visit UUID: {str(e)}",
        )


@router.post("/visit/uuid/{visit_uuid}", response_model=OrderResponse)
async def create_drug_order_for_visit_uuid(
    payload: DrugOrderCreateForVisit,
    visit_uuid: str = Path(..., description="Visit UUID"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Create a drug order for a visit UUID.

    This creates:
    1. An orders row with order_type_id=2
    2. A matching drug_order row with the same order_id
    """
    if not validate_uuid(visit_uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid visit UUID format",
        )

    try:
        return orders.create_drug_order_for_visit_uuid(
            db=db,
            visit_uuid=visit_uuid,
            payload=payload,
        )
    except LookupError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create drug order for visit UUID: {str(e)}",
        )
