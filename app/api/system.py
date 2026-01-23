import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_api_key
from app.database import get_db
from app.schemas import (
    SearchIndexRebuildRequest,
    SearchIndexRebuildResponse,
)
from app.services.search_index import trigger_full_search_index_rebuild

logger = logging.getLogger(__name__)

router = APIRouter(tags=["system"])


@router.post(
    "/search-index/rebuild",
    response_model=SearchIndexRebuildResponse,
    summary="Trigger full OpenMRS search index rebuild",
    description=(
        "Requests a full rebuild of the OpenMRS search index by calling "
        "`POST /ws/rest/v1/searchindexupdate` with no resource/uuid. "
        "By default the rebuild runs asynchronously on the OpenMRS side."
    ),
)
async def rebuild_search_index(
    payload: SearchIndexRebuildRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
) -> SearchIndexRebuildResponse:
    """
    Kick off a full search index rebuild in OpenMRS.

    Returns a payload describing whether OpenMRS accepted the request along with any
    diagnostic message. The API will raise a 502 error if the request fails due to
    connectivity issues.
    """

    result = await trigger_full_search_index_rebuild(async_mode=payload.async_mode)
    if not result.success:
        # Return detailed message so clients can re-run manually.
        logger.warning("Full search index rebuild failed: %s", result.message)
        raise HTTPException(
            status_code=502,
            detail=result.message or "Failed to trigger search index rebuild",
        )

    return SearchIndexRebuildResponse(
        success=True,
        message="Search index rebuild request accepted.",
    )
