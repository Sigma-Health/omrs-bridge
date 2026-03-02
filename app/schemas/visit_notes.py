"""
Schema for combined visit notes response (physical exam + chief complaints).
"""

from pydantic import BaseModel

from app.schemas.physical_exam import PhysicalExamReadResponse
from app.schemas.chief_complaint import ChiefComplaintVisitResponse


class VisitNotesResponse(BaseModel):
    """Combined physical examination notes and chief complaints for a visit."""

    physical_exam: PhysicalExamReadResponse
    chief_complaints: ChiefComplaintVisitResponse
