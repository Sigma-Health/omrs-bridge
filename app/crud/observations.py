from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from .base import BaseCRUD
from app.models import Obs
from app.schemas import ObsCreate, ObsUpdate, ObsReplace


class ObservationsCRUD(BaseCRUD[Obs]):
    """
    CRUD operations for Observation entities.
    
    Provides observation-specific database operations including filtering
    by person, encounter, concept, and order.
    """
    
    def __init__(self):
        """Initialize with the Obs model."""
        super().__init__(Obs)
    
    def _set_default_values(self, obj_data: dict) -> None:
        """Set observation-specific default values."""
        obj_data['voided'] = False
    
    def _set_audit_fields(self, db_obj: Obs, update_data: dict) -> None:
        """Set observation-specific audit fields."""
        # Observations don't have specific audit fields like changed_by/date_changed
        # They use the standard voided/voided_by/date_voided pattern
        pass
    
    # Entity-specific methods
    def get_obs_by_person(self, db: Session, person_id: int, skip: int = 0, limit: int = 100) -> List[Obs]:
        """
        Get observations for a specific person.
        
        Args:
            db: Database session
            person_id: ID of the person
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of observations for the specified person
        """
        return db.query(Obs).filter(
            and_(Obs.person_id == person_id, Obs.voided == False)
        ).offset(skip).limit(limit).all()
    
    def get_obs_by_encounter(self, db: Session, encounter_id: int, skip: int = 0, limit: int = 100) -> List[Obs]:
        """
        Get observations for a specific encounter.
        
        Args:
            db: Database session
            encounter_id: ID of the encounter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of observations for the specified encounter
        """
        return db.query(Obs).filter(
            and_(Obs.encounter_id == encounter_id, Obs.voided == False)
        ).offset(skip).limit(limit).all()
    
    def get_obs_by_concept(self, db: Session, concept_id: int, skip: int = 0, limit: int = 100) -> List[Obs]:
        """
        Get observations for a specific concept.
        
        Args:
            db: Database session
            concept_id: ID of the concept
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of observations for the specified concept
        """
        return db.query(Obs).filter(
            and_(Obs.concept_id == concept_id, Obs.voided == False)
        ).offset(skip).limit(limit).all()
    
    def get_obs_by_order(self, db: Session, order_id: int, skip: int = 0, limit: int = 100) -> List[Obs]:
        """
        Get observations for a specific order.
        
        Args:
            db: Database session
            order_id: ID of the order
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of observations for the specified order
        """
        return db.query(Obs).filter(
            and_(Obs.order_id == order_id, Obs.voided == False)
        ).offset(skip).limit(limit).all()
    
    def get_active_obs(self, db: Session, skip: int = 0, limit: int = 100) -> List[Obs]:
        """
        Get only active (non-voided) observations.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active observations
        """
        return db.query(Obs).filter(
            Obs.voided == False
        ).offset(skip).limit(limit).all()
    
    def get_voided_obs(self, db: Session, skip: int = 0, limit: int = 100) -> List[Obs]:
        """
        Get only voided observations.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of voided observations
        """
        return db.query(Obs).filter(
            Obs.voided == True
        ).offset(skip).limit(limit).all()
    
    def void_obs(self, db: Session, obs_id: int, voided_by: int, reason: str = None) -> Optional[Obs]:
        """
        Void an observation.
        
        Args:
            db: Database session
            obs_id: ID of the observation to void
            voided_by: ID of the user voiding the observation
            reason: Optional reason for voiding
            
        Returns:
            The voided observation if found, None otherwise
        """
        db_obs = self.get(db, obs_id)
        if not db_obs:
            return None
        
        db_obs.voided = True
        db_obs.voided_by = voided_by
        db_obs.date_voided = datetime.utcnow()
        if reason:
            db_obs.void_reason = reason
        
        try:
            db.commit()
            db.refresh(db_obs)
            return db_obs
        except Exception as e:
            db.rollback()
            raise e
    
    def unvoid_obs(self, db: Session, obs_id: int, unvoided_by: int) -> Optional[Obs]:
        """
        Unvoid an observation.
        
        Args:
            db: Database session
            obs_id: ID of the observation to unvoid
            unvoided_by: ID of the user unvoiding the observation
            
        Returns:
            The unvoided observation if found, None otherwise
        """
        db_obs = self.get(db, obs_id)
        if not db_obs:
            return None
        
        db_obs.voided = False
        db_obs.voided_by = None
        db_obs.date_voided = None
        db_obs.void_reason = None
        
        try:
            db.commit()
            db.refresh(db_obs)
            return db_obs
        except Exception as e:
            db.rollback()
            raise e
    
    def get_obs_by_value_type(self, db: Session, value_type: str, skip: int = 0, limit: int = 100) -> List[Obs]:
        """
        Get observations by value type (coded, numeric, text, datetime, etc.).
        
        Args:
            db: Database session
            value_type: Type of value to filter by ('coded', 'numeric', 'text', 'datetime')
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of observations with the specified value type
        """
        if value_type == 'coded':
            return db.query(Obs).filter(
                and_(Obs.value_coded.isnot(None), Obs.voided == False)
            ).offset(skip).limit(limit).all()
        elif value_type == 'numeric':
            return db.query(Obs).filter(
                and_(Obs.value_numeric.isnot(None), Obs.voided == False)
            ).offset(skip).limit(limit).all()
        elif value_type == 'text':
            return db.query(Obs).filter(
                and_(Obs.value_text.isnot(None), Obs.voided == False)
            ).offset(skip).limit(limit).all()
        elif value_type == 'datetime':
            return db.query(Obs).filter(
                and_(Obs.value_datetime.isnot(None), Obs.voided == False)
            ).offset(skip).limit(limit).all()
        else:
            return []
    
    def get_obs_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Obs]:
        """
        Get observations by status.
        
        Args:
            db: Database session
            status: Status to filter by ('FINAL', 'PRELIMINARY', etc.)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of observations with the specified status
        """
        return db.query(Obs).filter(
            and_(Obs.status == status, Obs.voided == False)
        ).offset(skip).limit(limit).all()