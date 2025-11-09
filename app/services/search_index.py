"""
Utilities for interacting with OpenMRS search index endpoints.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SearchIndexResult:
    success: bool
    message: Optional[str] = None

    def status_text(self) -> Optional[str]:
        if self.success:
            return "success"
        if self.message:
            return f"failed: {self.message}"
        return "failed"


async def _post_search_index_update(payload: dict) -> SearchIndexResult:
    """
    Internal helper for posting to the search index update endpoint.
    Returns a SearchIndexResult describing success and message.
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
        logger.error(
            "Failed to trigger search index update: %s (endpoint=%s, username=%s, password=%s)",
            exc,
            endpoint,
            settings.openmrs_rest_username,
            settings.openmrs_rest_password,
        )
        return SearchIndexResult(
            success=False,
            message=f"connection error: {exc}",
        )

    if response.status_code >= 400:
        logger.error(
            "Search index update request failed: %s - %s (endpoint=%s, username=%s, password=%s)",
            response.status_code,
            response.text,
            endpoint,
            settings.openmrs_rest_username,
            settings.openmrs_rest_password,
        )
        return SearchIndexResult(
            success=False,
            message=f"{response.status_code} {response.text}",
        )

    logger.info(
        "Search index update request accepted with status %s",
        response.status_code,
    )
    return SearchIndexResult(success=True)


async def trigger_search_index_update(
    resource: str,
    uuid: str,
    async_mode: bool = False,
) -> SearchIndexResult:
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
        message = f"missing UUID for resource '{resource}'"
        logger.warning(
            "Search index update skipped: %s (endpoint=%s, username=%s, password=%s)",
            message,
            f"{settings.openmrs_base_url.rstrip('/')}/ws/rest/v1/searchindexupdate",
            settings.openmrs_rest_username,
            settings.openmrs_rest_password,
        )
        return SearchIndexResult(success=False, message=message)

    payload = {"resource": resource, "uuid": uuid, "async": async_mode}
    return await _post_search_index_update(payload)


async def trigger_full_search_index_rebuild(
    async_mode: bool = True,
) -> SearchIndexResult:
    """
    Trigger a full search index rebuild in OpenMRS.

    Args:
        async_mode: Whether the rebuild should be executed asynchronously on the OpenMRS side.

    Returns:
        True if the request was accepted, False otherwise.
    """
    payload = {"async": async_mode}
    return await _post_search_index_update(payload)
