"""
Lab API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.auth import get_current_api_key
from app.crud import concepts
from app.database import get_db
from app.schemas import (
    LabCatalogMember,
    LabCatalogResponse,
)

router = APIRouter(tags=["labs"])


def _resolve_member_short_name(member) -> str | None:
    """
    Resolve short name for a concept.
    Prefer ConceptName rows with concept_name_type=SHORT, fallback to concept.short_name.
    """
    short_candidates = [
        name
        for name in getattr(member, "names", [])
        if not name.voided and (name.concept_name_type or "").upper() == "SHORT"
    ]
    preferred = next((name for name in short_candidates if name.locale_preferred), None)
    if preferred and preferred.name:
        return preferred.name
    if short_candidates and short_candidates[0].name:
        return short_candidates[0].name
    return member.short_name


@router.get("/catalog/{catalog_id}", response_model=LabCatalogResponse)
async def get_lab_catalog(
    catalog_id: int = Path(..., description="Lab catalog concept_id"),
    locale: str | None = Query(
        None,
        description="Optional locale filter for concept names",
    ),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get a lab catalog concept and its set members.

    A valid catalog must be a concept with is_set=1.
    """
    try:
        result = concepts.get_lab_catalog(
            db=db,
            catalog_id=catalog_id,
            locale=locale,
        )
        if not result:
            raise HTTPException(status_code=404, detail="Catalog concept not found")

        catalog = result["catalog"]
        member_sort = result["member_sort"]
        members = result["members"]

        response_members = [
            LabCatalogMember(
                concept_id=member.concept_id,
                uuid=member.uuid,
                preferred_name=member.preferred_name,
                short_name=_resolve_member_short_name(member),
                description=member.description,
                datatype_id=member.datatype_id,
                class_id=member.class_id,
                is_set=member.is_set,
                retired=member.retired,
                sort_weight=member_sort.get(member.concept_id),
            )
            for member in members
        ]

        return LabCatalogResponse(
            catalog_id=catalog.concept_id,
            catalog_uuid=catalog.uuid,
            catalog_name=catalog.preferred_name,
            is_set=bool(catalog.is_set),
            member_count=len(response_members),
            members=response_members,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get lab catalog: {str(exc)}",
        )
