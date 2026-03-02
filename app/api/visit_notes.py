"""
Combined visit notes API endpoint (physical exam + chief complaints).
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_api_key
from app.crud.physical_exam import physical_exam, PhysicalExamError
from app.crud.chief_complaint import chief_complaint, ChiefComplaintError
from app.schemas.physical_exam import PhysicalExamReadResponse
from app.schemas.visit_notes import VisitNotesResponse

router = APIRouter()


@router.get("/visit/{visit_id}", response_model=VisitNotesResponse)
async def get_visit_notes_by_id(
    visit_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Retrieve combined physical examination notes and chief complaints for a visit by visit ID.
    """
    try:
        exam = physical_exam.get_exam_notes_by_visit(
            db, visit_id=visit_id, visit_uuid=None
        )
        complaints = chief_complaint.get_complaints_by_visit(db, visit_id=visit_id)
        return VisitNotesResponse(
            physical_exam=PhysicalExamReadResponse(
                encounter_id=exam.encounter_id,
                encounter_uuid=exam.encounter_uuid,
                visit_id=exam.visit_id,
                observations=exam.observations,
            ),
            chief_complaints=complaints,
        )
    except (PhysicalExamError, ChiefComplaintError) as e:
        raise HTTPException(
            status_code=e.status, detail={"status": "error", "detail": e.code}
        )
    except Exception:
        raise HTTPException(
            status_code=400, detail={"status": "error", "detail": "unexpected_error"}
        )


@router.get("/visit/uuid/{visit_uuid}", response_model=VisitNotesResponse)
async def get_visit_notes_by_uuid(
    visit_uuid: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Retrieve combined physical examination notes and chief complaints for a visit by visit UUID.
    """
    try:
        exam = physical_exam.get_exam_notes_by_visit(
            db, visit_id=None, visit_uuid=visit_uuid
        )
        complaints = chief_complaint.get_complaints_by_visit(db, visit_uuid=visit_uuid)
        return VisitNotesResponse(
            physical_exam=PhysicalExamReadResponse(
                encounter_id=exam.encounter_id,
                encounter_uuid=exam.encounter_uuid,
                visit_id=exam.visit_id,
                observations=exam.observations,
            ),
            chief_complaints=complaints,
        )
    except (PhysicalExamError, ChiefComplaintError) as e:
        raise HTTPException(
            status_code=e.status, detail={"status": "error", "detail": e.code}
        )
    except Exception:
        raise HTTPException(
            status_code=400, detail={"status": "error", "detail": "unexpected_error"}
        )
