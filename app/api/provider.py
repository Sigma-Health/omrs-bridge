"""
Provider API endpoints.
"""

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
from app.crud import providers
from app.schemas import (
    ProviderResponse,
    ProviderListResponse,
)
from app.utils import validate_uuid

router = APIRouter(tags=["providers"])


@router.get("/", response_model=ProviderListResponse)
async def list_providers(
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
    List providers with person and name information.
    """
    try:
        return providers.list_with_details(db, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to list providers: {str(e)}",
        )


@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(
    provider_id: int = Path(..., description="Provider ID"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get provider by ID with person and name information.
    """
    try:
        provider = providers.get_with_details(db, provider_id)
        if not provider:
            raise HTTPException(
                status_code=404,
                detail="Provider not found",
            )
        return provider
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get provider: {str(e)}",
        )


@router.get("/uuid/{uuid}", response_model=ProviderResponse)
async def get_provider_by_uuid(
    uuid: str = Path(..., description="Provider UUID"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get provider by UUID with person and name information.
    """
    if not validate_uuid(uuid):
        raise HTTPException(
            status_code=400,
            detail="Invalid UUID format",
        )

    try:
        provider = providers.get_by_uuid_with_details(db, uuid)
        if not provider:
            raise HTTPException(
                status_code=404,
                detail="Provider not found",
            )
        return provider
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get provider: {str(e)}",
        )

