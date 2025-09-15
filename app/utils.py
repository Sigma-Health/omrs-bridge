import re
from typing import Optional


def validate_uuid(uuid_string: str) -> bool:
    """
    Validate UUID format - supports both standard UUID and OpenMRS formats:
    - Standard UUID: 8-4-4-4-12 format
    - OpenMRS UUID: 36 characters without hyphens
    """
    # Standard UUID format with hyphens
    standard_uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
    )

    # OpenMRS UUID format without hyphens (36 characters)
    openmrs_uuid_pattern = re.compile(r"^[0-9a-f]{36}$", re.IGNORECASE)

    return bool(
        standard_uuid_pattern.match(uuid_string)
        or openmrs_uuid_pattern.match(uuid_string)
    )


def format_uuid(uuid_string: str) -> Optional[str]:
    """
    Format UUID string to standard format (lowercase)
    Returns None if invalid format
    """
    if validate_uuid(uuid_string):
        return uuid_string.lower()
    return None


def extract_uuid_from_string(text: str) -> Optional[str]:
    """
    Extract UUID from a string that might contain other text
    Supports both standard UUID and OpenMRS UUID formats
    """
    # Try standard UUID format first
    standard_uuid_pattern = re.compile(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.IGNORECASE
    )
    match = standard_uuid_pattern.search(text)
    if match:
        return match.group(0).lower()

    # Try OpenMRS UUID format (36 characters without hyphens)
    openmrs_uuid_pattern = re.compile(r"[0-9a-f]{36}", re.IGNORECASE)
    match = openmrs_uuid_pattern.search(text)
    return match.group(0).lower() if match else None
