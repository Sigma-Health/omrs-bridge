from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from app.config import get_database_url
import asyncio
from typing import AsyncGenerator

# Convert MySQL URL to async format
def get_async_database_url():
    """Convert MySQL URL to async format for aiomysql"""
    url = get_database_url()
    if url.startswith('mysql://'):
        return url.replace('mysql://', 'mysql+aiomysql://', 1)
    return url

# Create async database engine with optimized settings
async_engine = create_async_engine(
    get_async_database_url(),
    poolclass=QueuePool,
    pool_size=20,  # Number of connections to maintain
    max_overflow=30,  # Additional connections when pool is full
    pool_pre_ping=True,  # Validate connections before use
    pool_recycle=3600,  # Recycle connections every hour
    echo=False,  # Set to True for SQL debugging
    # Performance optimizations
    pool_reset_on_return='commit',  # Reset connection state
    connect_args={
        "charset": "utf8mb4",
        "autocommit": False,
        "sql_mode": "STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO"
    }
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevent expired object access issues
    autocommit=False,
    autoflush=False
)

# Create Base class for models
Base = declarative_base()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Async dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Connection pool monitoring
async def get_pool_status():
    """Get connection pool status for monitoring"""
    pool = async_engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": pool.invalid()
    }


# Health check for database
async def check_db_health():
    """Check database connectivity and pool health"""
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
            pool_status = await get_pool_status()
            return {
                "status": "healthy",
                "pool": pool_status
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        } 