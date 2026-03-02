"""
Physical examination notes API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_api_key
from app.crud.physical_exam import physical_exam, PhysicalExamError
from app.schemas.physical_exam import (
    PhysicalExamCreate,
    PhysicalExamResponse,
    ExamNoteUpdate,
    ExamNoteVoid,
)
from app.schemas.vitals import VitalSign

router = APIRouter()


@router.get("/visit/{visit_id}", response_model=PhysicalExamResponse)
async def get_physical_exam_notes_by_visit_id(
    visit_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Retrieve physical examination notes for a visit by visit ID.

    Returns the consultation encounter and all physical exam observations recorded for it.
    If no consultation encounter exists, returns an empty observations list.
    """
    try:
        return physical_exam.get_exam_notes_by_visit(
            db, visit_id=visit_id, visit_uuid=None
        )
    except PhysicalExamError as e:
        raise HTTPException(
            status_code=e.status, detail={"status": "error", "detail": e.code}
        )
    except Exception:
        raise HTTPException(
            status_code=400, detail={"status": "error", "detail": "unexpected_error"}
        )


@router.get("/visit/uuid/{visit_uuid}", response_model=PhysicalExamResponse)
async def get_physical_exam_notes_by_visit_uuid(
    visit_uuid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Retrieve physical examination notes for a visit by visit UUID.

    Returns the consultation encounter and all physical exam observations recorded for it.
    If no consultation encounter exists, returns an empty observations list.
    """
    try:
        return physical_exam.get_exam_notes_by_visit(
            db, visit_id=None, visit_uuid=visit_uuid
        )
    except PhysicalExamError as e:
        raise HTTPException(
            status_code=e.status, detail={"status": "error", "detail": e.code}
        )
    except Exception:
        raise HTTPException(
            status_code=400, detail={"status": "error", "detail": "unexpected_error"}
        )


@router.get("/{obs_id}", response_model=VitalSign)
async def get_physical_exam_note(
    obs_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Retrieve a single physical examination note by obs_id.
    """
    try:
        return physical_exam.get_exam_note(db, obs_id)
    except PhysicalExamError as e:
        raise HTTPException(
            status_code=e.status, detail={"status": "error", "detail": e.code}
        )
    except Exception:
        raise HTTPException(
            status_code=400, detail={"status": "error", "detail": "unexpected_error"}
        )


@router.patch("/{obs_id}", response_model=VitalSign)
async def update_physical_exam_note(
    obs_id: int,
    payload: ExamNoteUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Partially update a physical examination note by obs_id.

    Only provided fields are updated (value_text, comments, obs_datetime).
    """
    try:
        return physical_exam.update_exam_note(db, obs_id, payload)
    except PhysicalExamError as e:
        raise HTTPException(
            status_code=e.status, detail={"status": "error", "detail": e.code}
        )
    except Exception:
        raise HTTPException(
            status_code=400, detail={"status": "error", "detail": "unexpected_error"}
        )


@router.delete("/{obs_id}", status_code=204)
async def delete_physical_exam_note(
    obs_id: int,
    payload: ExamNoteVoid = ExamNoteVoid(),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Void a physical examination note by obs_id.

    The record is not deleted from the database — it is marked as voided.
    Accepts an optional body with void_reason and voided_by.
    Returns 204 No Content on success, 404 if not found or already voided.
    """
    try:
        physical_exam.delete_exam_note(db, obs_id, payload)
        return Response(status_code=204)
    except PhysicalExamError as e:
        raise HTTPException(
            status_code=e.status, detail={"status": "error", "detail": e.code}
        )
    except Exception:
        raise HTTPException(
            status_code=400, detail={"status": "error", "detail": "unexpected_error"}
        )


@router.post("/", response_model=PhysicalExamResponse)
async def create_physical_exam_notes(
    payload: PhysicalExamCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Create physical examination notes for a visit.

    - Resolves the visit by visit_id or visit_uuid
    - Reuses an existing consultation encounter for the visit if one exists,
      otherwise creates a new one
    - Creates one obs record per note entry using the configured
      PHYSICAL_EXAM_CONCEPT_ID (or a per-note override)
    - Returns the encounter details and all created observations
    """
    try:
        return physical_exam.create_exam_notes(db, payload)
    except PhysicalExamError as e:
        raise HTTPException(
            status_code=e.status, detail={"status": "error", "detail": e.code}
        )
    except Exception:
        raise HTTPException(
            status_code=400, detail={"status": "error", "detail": "unexpected_error"}
        )
