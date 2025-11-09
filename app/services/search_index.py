"""
Utilities for interacting with OpenMRS search index endpoints.
"""

from __future__ import annotations

import logging
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def _post_search_index_update(payload: dict) -> bool:
    """
    Internal helper for posting to the search index update endpoint.
    Returns True when the request is accepted by OpenMRS.
    """
    base_url = settings.openmrs_base_url.rstrip("/")
    endpoint = f"{base_url}/ws/rest/v1/searchindexupdate"

    auth: Optional[httpx.BasicAuth] = None
    if settings.openmrs_rest_username and settings.openmrs_rest_password:
        auth = httpx.BasicAuth(
            settings.openmrs_rest_username,
            settings.openmrs_rest_password,
        )

    try:
        async with httpx.AsyncClient(
            timeout=settings.openmrs_rest_timeout_seconds,
            verify=settings.openmrs_rest_verify_ssl,
        ) as client:
            response = await client.post(endpoint, json=payload, auth=auth)
    except httpx.RequestError as exc:
        logger.error("Failed to trigger search index update: %s", exc)
        return False

    if response.status_code >= 400:
        logger.error(
            "Search index update request failed: %s - %s",
            response.status_code,
            response.text,
        )
        return False

    logger.info(
        "Search index update request accepted with status %s",
        response.status_code,
    )
    return True


async def trigger_search_index_update(
    resource: str,
    uuid: str,
    async_mode: bool = False,
) -> bool:
    """
    Trigger a search index update for a given OpenMRS resource.

    Args:
        resource: Name of the resource (e.g., "drug").
        uuid: UUID of the resource to index.
        async_mode: Whether the OpenMRS endpoint should process asynchronously.

    Returns:
        True if the request was successfully accepted by OpenMRS, False otherwise.
    """
    if not uuid:
        logger.warning(
            "Search index update skipped: missing UUID for resource '%s'", resource
        )
        return False

    payload = {"resource": resource, "uuid": uuid, "async": async_mode}
    return await _post_search_index_update(payload)


async def trigger_full_search_index_rebuild(async_mode: bool = True) -> bool:
    """
    Trigger a full search index rebuild in OpenMRS.

    Args:
        async_mode: Whether the rebuild should be executed asynchronously on the OpenMRS side.

    Returns:
        True if the request was accepted, False otherwise.
    """
    payload = {"async": async_mode}
    return await _post_search_index_update(payload)
