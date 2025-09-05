from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from .base import BaseCRUD
from app.models import Encounter
from app.schemas import EncounterCreate, EncounterUpdate, EncounterReplace


class EncountersCRUD(BaseCRUD[Encounter]):
    """
    CRUD operations for Encounter entities.
    
    Provides encounter-specific database operations including filtering
    by patient, type, location, visit, and date ranges.
    """
    
    def __init__(self):
        """Initialize with the Encounter model."""
        super().__init__(Encounter)
    
    def _set_default_values(self, obj_data: dict) -> None:
        """Set encounter-specific default values."""
        obj_data['voided'] = False
    
    def _set_audit_fields(self, db_obj: Encounter, update_data: dict) -> None:
        """Set encounter-specific audit fields."""
        db_obj.changed_by = update_data.get('changed_by', db_obj.changed_by)
        db_obj.date_changed = datetime.utcnow()
    
    # Entity-specific methods
    def get_encounters_by_patient(self, db: Session, patient_id: int, skip: int = 0, limit: int = 100) -> List[Encounter]:
        """
        Get encounters for a specific patient.
        
        Args:
            db: Database session
            patient_id: ID of the patient
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of encounters for the specified patient
        """
        return db.query(Encounter).filter(
            and_(Encounter.patient_id == patient_id, Encounter.voided == False)
        ).offset(skip).limit(limit).all()
    
    def get_encounters_by_type(self, db: Session, encounter_type: int, skip: int = 0, limit: int = 100) -> List[Encounter]:
        """
        Get encounters for a specific encounter type.
        
        Args:
            db: Database session
            encounter_type: ID of the encounter type
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of encounters with the specified type
        """
        return db.query(Encounter).filter(
            and_(Encounter.encounter_type == encounter_type, Encounter.voided == False)
        ).offset(skip).limit(limit).all()
    
    def get_encounters_by_location(self, db: Session, location_id: int, skip: int = 0, limit: int = 100) -> List[Encounter]:
        """
        Get encounters for a specific location.
        
        Args:
            db: Database session
            location_id: ID of the location
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of encounters at the specified location
        """
        return db.query(Encounter).filter(
            and_(Encounter.location_id == location_id, Encounter.voided == False)
        ).offset(skip).limit(limit).all()
    
    def get_encounters_by_visit(self, db: Session, visit_id: int, skip: int = 0, limit: int = 100) -> List[Encounter]:
        """
        Get encounters for a specific visit.
        
        Args:
            db: Database session
            visit_id: ID of the visit
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of encounters for the specified visit
        """
        return db.query(Encounter).filter(
            and_(Encounter.visit_id == visit_id, Encounter.voided == False)
        ).offset(skip).limit(limit).all()
    
    def get_encounters_by_creator(self, db: Session, creator: int, skip: int = 0, limit: int = 100) -> List[Encounter]:
        """
        Get encounters created by a specific user.
        
        Args:
            db: Database session
            creator: ID of the user who created the encounters
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of encounters created by the specified user
        """
        return db.query(Encounter).filter(
            and_(Encounter.creator == creator, Encounter.voided == False)
        ).offset(skip).limit(limit).all()
    
    def get_encounters_by_date_range(self, db: Session, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100) -> List[Encounter]:
        """
        Get encounters within a date range.
        
        Args:
            db: Database session
            start_date: Start date for the range
            end_date: End date for the range
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of encounters within the specified date range
        """
        return db.query(Encounter).filter(
            and_(
                Encounter.voided == False,
                Encounter.encounter_datetime >= start_date,
                Encounter.encounter_datetime <= end_date
            )
        ).offset(skip).limit(limit).all()
    
    def get_active_encounters(self, db: Session, skip: int = 0, limit: int = 100) -> List[Encounter]:
        """
        Get only active (non-voided) encounters.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active encounters
        """
        return db.query(Encounter).filter(
            Encounter.voided == False
        ).offset(skip).limit(limit).all()
    
    def get_voided_encounters(self, db: Session, skip: int = 0, limit: int = 100) -> List[Encounter]:
        """
        Get only voided encounters.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of voided encounters
        """
        return db.query(Encounter).filter(
            Encounter.voided == True
        ).offset(skip).limit(limit).all()
    
    def void_encounter(self, db: Session, encounter_id: int, voided_by: int, reason: str = None) -> Optional[Encounter]:
        """
        Void an encounter.
        
        Args:
            db: Database session
            encounter_id: ID of the encounter to void
            voided_by: ID of the user voiding the encounter
            reason: Optional reason for voiding
            
        Returns:
            The voided encounter if found, None otherwise
        """
        db_encounter = self.get(db, encounter_id)
        if not db_encounter:
            return None
        
        db_encounter.voided = True
        db_encounter.voided_by = voided_by
        db_encounter.date_voided = datetime.utcnow()
        if reason:
            db_encounter.void_reason = reason
        
        try:
            db.commit()
            db.refresh(db_encounter)
            return db_encounter
        except Exception as e:
            db.rollback()
            raise e
    
    def unvoid_encounter(self, db: Session, encounter_id: int, unvoided_by: int) -> Optional[Encounter]:
        """
        Unvoid an encounter.
        
        Args:
            db: Database session
            encounter_id: ID of the encounter to unvoid
            unvoided_by: ID of the user unvoiding the encounter
            
        Returns:
            The unvoided encounter if found, None otherwise
        """
        db_encounter = self.get(db, encounter_id)
        if not db_encounter:
            return None
        
        db_encounter.voided = False
        db_encounter.voided_by = None
        db_encounter.date_voided = None
        db_encounter.void_reason = None
        
        try:
            db.commit()
            db.refresh(db_encounter)
            return db_encounter
        except Exception as e:
            db.rollback()
            raise e