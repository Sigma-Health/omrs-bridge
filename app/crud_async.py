from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from app.models import Order, Obs
from app.schemas import OrderUpdate, OrderReplace, ObsUpdate, ObsReplace
from typing import Optional, List
from datetime import datetime
import asyncio


# ============================================================================
# ASYNC ORDER CRUD OPERATIONS
# ============================================================================

async def get_order_async(db: AsyncSession, order_id: int) -> Optional[Order]:
    """Get order by ID asynchronously"""
    result = await db.execute(select(Order).where(Order.order_id == order_id))
    return result.scalar_one_or_none()


async def get_order_by_uuid_async(db: AsyncSession, uuid: str) -> Optional[Order]:
    """Get order by UUID asynchronously"""
    result = await db.execute(select(Order).where(Order.uuid == uuid))
    return result.scalar_one_or_none()


async def update_order_partial_async(db: AsyncSession, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
    """Update order partially (PATCH) by ID asynchronously"""
    db_order = await get_order_async(db, order_id)
    if not db_order:
        return None
    
    # Get update data, excluding None values
    update_data = order_update.dict(exclude_unset=True)
    
    if not update_data:
        return db_order
    
    # Update fields
    for field, value in update_data.items():
        if hasattr(db_order, field):
            setattr(db_order, field, value)
    
    try:
        await db.commit()
        await db.refresh(db_order)
        return db_order
    except Exception as e:
        await db.rollback()
        raise e


async def update_order_partial_by_uuid_async(db: AsyncSession, uuid: str, order_update: OrderUpdate) -> Optional[Order]:
    """Update order partially (PATCH) by UUID asynchronously"""
    db_order = await get_order_by_uuid_async(db, uuid)
    if not db_order:
        return None
    
    # Get update data, excluding None values
    update_data = order_update.dict(exclude_unset=True)
    
    if not update_data:
        return db_order
    
    # Update fields
    for field, value in update_data.items():
        if hasattr(db_order, field):
            setattr(db_order, field, value)
    
    try:
        await db.commit()
        await db.refresh(db_order)
        return db_order
    except Exception as e:
        await db.rollback()
        raise e


async def list_orders_async(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Order]:
    """List orders with pagination asynchronously"""
    result = await db.execute(
        select(Order)
        .offset(skip)
        .limit(limit)
        .order_by(Order.order_id.desc())
    )
    return result.scalars().all()


async def get_orders_by_patient_async(db: AsyncSession, patient_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
    """Get orders for a specific patient asynchronously"""
    result = await db.execute(
        select(Order)
        .where(and_(Order.patient_id == patient_id, Order.voided == False))
        .offset(skip)
        .limit(limit)
        .order_by(Order.date_created.desc())
    )
    return result.scalars().all()


# ============================================================================
# ASYNC OBSERVATION (OBS) CRUD OPERATIONS
# ============================================================================

async def get_obs_async(db: AsyncSession, obs_id: int) -> Optional[Obs]:
    """Get observation by ID asynchronously"""
    result = await db.execute(select(Obs).where(Obs.obs_id == obs_id))
    return result.scalar_one_or_none()


async def get_obs_by_uuid_async(db: AsyncSession, uuid: str) -> Optional[Obs]:
    """Get observation by UUID asynchronously"""
    result = await db.execute(select(Obs).where(Obs.uuid == uuid))
    return result.scalar_one_or_none()


async def update_obs_partial_async(db: AsyncSession, obs_id: int, obs_update: ObsUpdate) -> Optional[Obs]:
    """Update observation partially (PATCH) by ID asynchronously"""
    db_obs = await get_obs_async(db, obs_id)
    if not db_obs:
        return None
    
    # Get update data, excluding None values
    update_data = obs_update.dict(exclude_unset=True)
    
    if not update_data:
        return db_obs
    
    # Update fields
    for field, value in update_data.items():
        if hasattr(db_obs, field):
            setattr(db_obs, field, value)
    
    try:
        await db.commit()
        await db.refresh(db_obs)
        return db_obs
    except Exception as e:
        await db.rollback()
        raise e


async def update_obs_partial_by_uuid_async(db: AsyncSession, uuid: str, obs_update: ObsUpdate) -> Optional[Obs]:
    """Update observation partially (PATCH) by UUID asynchronously"""
    db_obs = await get_obs_by_uuid_async(db, uuid)
    if not db_obs:
        return None
    
    # Get update data, excluding None values
    update_data = obs_update.dict(exclude_unset=True)
    
    if not update_data:
        return db_obs
    
    # Update fields
    for field, value in update_data.items():
        if hasattr(db_obs, field):
            setattr(db_obs, field, value)
    
    try:
        await db.commit()
        await db.refresh(db_obs)
        return db_obs
    except Exception as e:
        await db.rollback()
        raise e


async def list_obs_async(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Obs]:
    """List observations with pagination asynchronously"""
    result = await db.execute(
        select(Obs)
        .offset(skip)
        .limit(limit)
        .order_by(Obs.obs_id.desc())
    )
    return result.scalars().all()


async def get_obs_by_person_async(db: AsyncSession, person_id: int, skip: int = 0, limit: int = 100) -> List[Obs]:
    """Get observations for a specific person asynchronously"""
    result = await db.execute(
        select(Obs)
        .where(and_(Obs.person_id == person_id, Obs.voided == False))
        .offset(skip)
        .limit(limit)
        .order_by(Obs.obs_datetime.desc())
    )
    return result.scalars().all()


async def get_obs_by_encounter_async(db: AsyncSession, encounter_id: int, skip: int = 0, limit: int = 100) -> List[Obs]:
    """Get observations for a specific encounter asynchronously"""
    result = await db.execute(
        select(Obs)
        .where(and_(Obs.encounter_id == encounter_id, Obs.voided == False))
        .offset(skip)
        .limit(limit)
        .order_by(Obs.obs_datetime.desc())
    )
    return result.scalars().all()


async def get_obs_by_concept_async(db: AsyncSession, concept_id: int, skip: int = 0, limit: int = 100) -> List[Obs]:
    """Get observations for a specific concept asynchronously"""
    result = await db.execute(
        select(Obs)
        .where(and_(Obs.concept_id == concept_id, Obs.voided == False))
        .offset(skip)
        .limit(limit)
        .order_by(Obs.obs_datetime.desc())
    )
    return result.scalars().all()


async def get_obs_by_order_async(db: AsyncSession, order_id: int, skip: int = 0, limit: int = 100) -> List[Obs]:
    """Get observations for a specific order asynchronously"""
    result = await db.execute(
        select(Obs)
        .where(and_(Obs.order_id == order_id, Obs.voided == False))
        .offset(skip)
        .limit(limit)
        .order_by(Obs.obs_datetime.desc())
    )
    return result.scalars().all()


# ============================================================================
# BULK OPERATIONS FOR BETTER PERFORMANCE
# ============================================================================

async def get_obs_bulk_async(db: AsyncSession, uuids: List[str]) -> List[Obs]:
    """Get multiple observations by UUIDs in a single query"""
    result = await db.execute(
        select(Obs).where(Obs.uuid.in_(uuids))
    )
    return result.scalars().all()


async def update_obs_bulk_async(db: AsyncSession, updates: List[tuple]) -> List[Obs]:
    """Update multiple observations in bulk"""
    updated_obs = []
    
    for uuid, update_data in updates:
        db_obs = await get_obs_by_uuid_async(db, uuid)
        if db_obs:
            for field, value in update_data.items():
                if hasattr(db_obs, field):
                    setattr(db_obs, field, value)
            updated_obs.append(db_obs)
    
    if updated_obs:
        try:
            await db.commit()
            for obs in updated_obs:
                await db.refresh(obs)
        except Exception as e:
            await db.rollback()
            raise e
    
    return updated_obs


# ============================================================================
# PERFORMANCE MONITORING
# ============================================================================

async def get_database_stats_async(db: AsyncSession):
    """Get database statistics for monitoring"""
    # Count orders
    result = await db.execute(select(func.count(Order.order_id)))
    order_count = result.scalar()
    
    # Count observations
    result = await db.execute(select(func.count(Obs.obs_id)))
    obs_count = result.scalar()
    
    # Count non-voided records
    result = await db.execute(select(func.count(Order.order_id)).where(Order.voided == False))
    active_orders = result.scalar()
    
    result = await db.execute(select(func.count(Obs.obs_id)).where(Obs.voided == False))
    active_obs = result.scalar()
    
    return {
        "total_orders": order_count,
        "total_observations": obs_count,
        "active_orders": active_orders,
        "active_observations": active_obs,
        "timestamp": datetime.now().isoformat()
    } 