import re
from typing import Optional


def validate_uuid(uuid_string: str) -> bool:
    """
    Validate UUID format (8-4-4-4-12 format)
    Example: 6000e165-57fd-4ad3-af48-0df1a6b157a9
    """
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(uuid_string))


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
    """
    uuid_pattern = re.compile(
        r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
        re.IGNORECASE
    )
    match = uuid_pattern.search(text)
    return match.group(0).lower() if match else None 