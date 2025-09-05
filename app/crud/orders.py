from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from .base import BaseCRUD
from app.models import Order
from app.schemas import OrderUpdate, OrderReplace


class OrdersCRUD(BaseCRUD[Order]):
    """
    CRUD operations for Order entities.
    
    Provides order-specific database operations including filtering
    by patient, urgency, orderer, and other criteria.
    """
    
    def __init__(self):
        """Initialize with the Order model."""
        super().__init__(Order)
    
    def _set_default_values(self, obj_data: dict) -> None:
        """Set order-specific default values."""
        obj_data['voided'] = False
        obj_data['urgency'] = obj_data.get('urgency', 'ROUTINE')
        obj_data['order_action'] = obj_data.get('order_action', 'NEW')
    
    def _set_audit_fields(self, db_obj: Order, update_data: dict) -> None:
        """Set order-specific audit fields."""
        # Orders don't have specific audit fields like changed_by/date_changed
        # They use the standard voided/voided_by/date_voided pattern
        pass
    
    # Entity-specific methods
    def get_by_order_number(self, db: Session, order_number: str) -> Optional[Order]:
        """
        Get order by order number.
        
        Args:
            db: Database session
            order_number: Order number to search for
            
        Returns:
            The order if found, None otherwise
        """
        return db.query(Order).filter(Order.order_number == order_number).first()
    
    def get_orders_by_patient(self, db: Session, patient_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Get orders for a specific patient.
        
        Args:
            db: Database session
            patient_id: ID of the patient
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of orders for the specified patient
        """
        return db.query(Order).filter(
            and_(Order.patient_id == patient_id, Order.voided == False)
        ).offset(skip).limit(limit).all()
    
    def get_orders_by_urgency(self, db: Session, urgency: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Get orders by urgency level.
        
        Args:
            db: Database session
            urgency: Urgency level ('ROUTINE', 'STAT', 'ASAP', etc.)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of orders with the specified urgency
        """
        return db.query(Order).filter(
            and_(Order.urgency == urgency, Order.voided == False)
        ).offset(skip).limit(limit).all()
    
    def get_orders_by_orderer(self, db: Session, orderer: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Get orders by orderer (provider).
        
        Args:
            db: Database session
            orderer: ID of the provider who ordered
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of orders by the specified orderer
        """
        return db.query(Order).filter(
            and_(Order.orderer == orderer, Order.voided == False)
        ).offset(skip).limit(limit).all()
    
    def get_orders_by_encounter(self, db: Session, encounter_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Get orders for a specific encounter.
        
        Args:
            db: Database session
            encounter_id: ID of the encounter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of orders for the specified encounter
        """
        return db.query(Order).filter(
            and_(Order.encounter_id == encounter_id, Order.voided == False)
        ).offset(skip).limit(limit).all()
    
    def get_orders_by_concept(self, db: Session, concept_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Get orders for a specific concept.
        
        Args:
            db: Database session
            concept_id: ID of the concept
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of orders for the specified concept
        """
        return db.query(Order).filter(
            and_(Order.concept_id == concept_id, Order.voided == False)
        ).offset(skip).limit(limit).all()
    
    def get_orders_by_type(self, db: Session, order_type_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Get orders by order type.
        
        Args:
            db: Database session
            order_type_id: ID of the order type
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of orders with the specified type
        """
        return db.query(Order).filter(
            and_(Order.order_type_id == order_type_id, Order.voided == False)
        ).offset(skip).limit(limit).all()
    
    def get_active_orders(self, db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Get only active (non-voided) orders.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of active orders
        """
        return db.query(Order).filter(
            Order.voided == False
        ).offset(skip).limit(limit).all()
    
    def get_voided_orders(self, db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Get only voided orders.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of voided orders
        """
        return db.query(Order).filter(
            Order.voided == True
        ).offset(skip).limit(limit).all()
    
    def void_order(self, db: Session, order_id: int, voided_by: int, reason: str = None) -> Optional[Order]:
        """
        Void an order.
        
        Args:
            db: Database session
            order_id: ID of the order to void
            voided_by: ID of the user voiding the order
            reason: Optional reason for voiding
            
        Returns:
            The voided order if found, None otherwise
        """
        db_order = self.get(db, order_id)
        if not db_order:
            return None
        
        db_order.voided = True
        db_order.voided_by = voided_by
        db_order.date_voided = datetime.utcnow()
        if reason:
            db_order.void_reason = reason
        
        try:
            db.commit()
            db.refresh(db_order)
            return db_order
        except Exception as e:
            db.rollback()
            raise e
    
    def unvoid_order(self, db: Session, order_id: int, unvoided_by: int) -> Optional[Order]:
        """
        Unvoid an order.
        
        Args:
            db: Database session
            order_id: ID of the order to unvoid
            unvoided_by: ID of the user unvoiding the order
            
        Returns:
            The unvoided order if found, None otherwise
        """
        db_order = self.get(db, order_id)
        if not db_order:
            return None
        
        db_order.voided = False
        db_order.voided_by = None
        db_order.date_voided = None
        db_order.void_reason = None
        
        try:
            db.commit()
            db.refresh(db_order)
            return db_order
        except Exception as e:
            db.rollback()
            raise e
    
    def get_orders_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Get orders by fulfiller status.
        
        Args:
            db: Database session
            status: Fulfiller status to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of orders with the specified fulfiller status
        """
        return db.query(Order).filter(
            and_(Order.fulfiller_status == status, Order.voided == False)
        ).offset(skip).limit(limit).all()
    
    def get_orders_by_action(self, db: Session, action: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """
        Get orders by order action.
        
        Args:
            db: Database session
            action: Order action to filter by ('NEW', 'REVISE', 'DISCONTINUE', etc.)
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of orders with the specified action
        """
        return db.query(Order).filter(
            and_(Order.order_action == action, Order.voided == False)
        ).offset(skip).limit(limit).all()