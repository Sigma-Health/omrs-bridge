"""
Chief complaint API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_api_key
from app.crud.chief_complaint import chief_complaint, ChiefComplaintError
from app.schemas.chief_complaint import (
    ChiefComplaintCreate,
    ChiefComplaintUpdate,
    ChiefComplaintVoid,
    ChiefComplaintGroupResponse,
    ChiefComplaintVisitResponse,
)

router = APIRouter()


@router.get("/visit/{visit_id}", response_model=ChiefComplaintVisitResponse)
async def get_complaints_by_visit_id(
    visit_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Retrieve all chief complaint groups for a visit by visit ID.
    """
    try:
        return chief_complaint.get_complaints_by_visit(db, visit_id=visit_id)
    except ChiefComplaintError as e:
        raise HTTPException(status_code=e.status, detail={"status": "error", "detail": e.code})
    except Exception:
        raise HTTPException(status_code=400, detail={"status": "error", "detail": "unexpected_error"})


@router.get("/visit/uuid/{visit_uuid}", response_model=ChiefComplaintVisitResponse)
async def get_complaints_by_visit_uuid(
    visit_uuid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Retrieve all chief complaint groups for a visit by visit UUID.
    """
    try:
        return chief_complaint.get_complaints_by_visit(db, visit_uuid=visit_uuid)
    except ChiefComplaintError as e:
        raise HTTPException(status_code=e.status, detail={"status": "error", "detail": e.code})
    except Exception:
        raise HTTPException(status_code=400, detail={"status": "error", "detail": "unexpected_error"})


@router.get("/{group_obs_id}", response_model=ChiefComplaintGroupResponse)
async def get_complaint_group(
    group_obs_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Retrieve a single chief complaint group by its obs group ID.
    """
    try:
        return chief_complaint.get_complaint_group(db, group_obs_id)
    except ChiefComplaintError as e:
        raise HTTPException(status_code=e.status, detail={"status": "error", "detail": e.code})
    except Exception:
        raise HTTPException(status_code=400, detail={"status": "error", "detail": "unexpected_error"})


@router.patch("/{group_obs_id}", response_model=ChiefComplaintGroupResponse)
async def update_complaint_group(
    group_obs_id: int,
    payload: ChiefComplaintUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Partially update a chief complaint group by its obs group ID.

    Only provided fields are updated. Operates on the group and all child obs.
    """
    try:
        return chief_complaint.update_complaint_group(db, group_obs_id, payload)
    except ChiefComplaintError as e:
        raise HTTPException(status_code=e.status, detail={"status": "error", "detail": e.code})
    except Exception:
        raise HTTPException(status_code=400, detail={"status": "error", "detail": "unexpected_error"})


@router.delete("/{group_obs_id}", status_code=204)
async def delete_complaint_group(
    group_obs_id: int,
    payload: ChiefComplaintVoid = ChiefComplaintVoid(),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Void a chief complaint group and all its child obs by group obs ID.

    Accepts an optional body with void_reason and voided_by.
    Returns 204 No Content on success.
    """
    try:
        chief_complaint.delete_complaint_group(db, group_obs_id, payload)
        return Response(status_code=204)
    except ChiefComplaintError as e:
        raise HTTPException(status_code=e.status, detail={"status": "error", "detail": e.code})
    except Exception:
        raise HTTPException(status_code=400, detail={"status": "error", "detail": "unexpected_error"})


@router.post("/", response_model=ChiefComplaintGroupResponse)
async def create_complaint(
    payload: ChiefComplaintCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Create a chief complaint for a visit.

    - Resolves the visit by visit_id or visit_uuid
    - Reuses or creates a consultation encounter
    - Creates an obs group (57422) containing:
        - Chief complaint coded (57385) or text (30201)
        - Duration value (11266) — optional
        - Duration unit (57386) — optional, required if duration_value is set
    - Optionally creates a History of Present Illness obs (16086) outside the group
    """
    try:
        return chief_complaint.create_complaint(db, payload)
    except ChiefComplaintError as e:
        raise HTTPException(status_code=e.status, detail={"status": "error", "detail": e.code})
    except Exception:
        raise HTTPException(status_code=400, detail={"status": "error", "detail": "unexpected_error"})
