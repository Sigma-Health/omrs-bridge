"""
Lab catalog schemas.
"""

from typing import List, Optional

from pydantic import BaseModel


class LabCatalogMember(BaseModel):
    """A single lab test concept within a catalog set."""

    concept_id: int
    uuid: str
    preferred_name: Optional[str] = None
    short_name: Optional[str] = None
    description: Optional[str] = None
    datatype_id: Optional[int] = None
    class_id: Optional[int] = None
    is_set: Optional[bool] = None
    retired: Optional[bool] = None
    sort_weight: Optional[int] = None


class LabCatalogResponse(BaseModel):
    """Lab catalog concept and all configured set members."""

    catalog_id: int
    catalog_uuid: str
    catalog_name: Optional[str] = None
    is_set: bool
    member_count: int
    members: List[LabCatalogMember]
