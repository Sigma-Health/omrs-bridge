import logging
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_api_key
from app.config import settings
from app.database import get_db
from app.schemas import SearchIndexAvailabilityResponse

logger = logging.getLogger(__name__)


router = APIRouter(tags=["system"])


@router.get(
    "/search-index/availability",
    response_model=SearchIndexAvailabilityResponse,
    summary="Check OpenMRS search index endpoint availability",
    description="""
    Performs a lightweight `OPTIONS` request against the OpenMRS search index rebuild endpoint
    to verify connectivity and authentication requirements without triggering a rebuild.
    """,
)
async def check_search_index_availability(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
) -> SearchIndexAvailabilityResponse:
    """
    Check whether the OpenMRS search index rebuild endpoint is reachable.

    Returns diagnostic metadata including status code, reason phrase, and whether authentication
    is required. Any response other than HTTP 404 and 5xx is treated as "available".
    """

    # Ensure base URL is configured
    base_url = settings.openmrs_base_url.rstrip("/")
    target_url = f"{base_url}/ws/rest/v1/searchIndex/rebuild"

    auth: Optional[httpx.BasicAuth] = None
    if settings.openmrs_rest_username and settings.openmrs_rest_password:
        auth = httpx.BasicAuth(
            settings.openmrs_rest_username,
            settings.openmrs_rest_password,
        )

    try:
        async with httpx.AsyncClient(
            timeout=settings.openmrs_rest_timeout_seconds
        ) as client:
            response = await client.options(target_url, auth=auth)
    except httpx.RequestError as exc:
        logger.error("Failed to reach OpenMRS search index endpoint: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"Unable to reach OpenMRS search index endpoint: {exc}",
        ) from exc

    status_code = response.status_code
    reason = response.reason_phrase
    requires_auth = status_code == 401
    allowed_header = response.headers.get("Allow")
    allowed_methods = (
        [method.strip() for method in allowed_header.split(",")]
        if allowed_header
        else None
    )

    # Treat anything other than 404 and 5xx as "available"
    available = status_code not in {404} and status_code < 500

    message = None
    if status_code == 404:
        message = "Endpoint not found (404)."
    elif status_code >= 500:
        message = "OpenMRS returned a server error."
    elif status_code == 401:
        message = "Authentication required (401)."
    elif status_code == 405:
        message = (
            "Endpoint reachable; method not allowed (405) indicates POST is required."
        )

    return SearchIndexAvailabilityResponse(
        available=available,
        status_code=status_code,
        reason=reason,
        requires_authentication=requires_auth,
        allowed_methods=allowed_methods,
        message=message,
    )
