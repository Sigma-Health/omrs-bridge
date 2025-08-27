from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.api.orders import router as orders_router
from app.api.observations import router as observations_router
from app.config import settings
from app.auth import generate_api_key, get_current_api_key
from app.database_async import get_async_db, check_db_health, get_pool_status
from app.crud_async import get_database_stats_async
import logging
import time
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any

# Configure logging with performance tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Performance monitoring
request_times: Dict[str, list] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown"""
    # Startup
    logger.info("🚀 Starting OpenMRS Bridge API (Optimized)")
    
    # Check database health on startup
    db_health = await check_db_health()
    if db_health["status"] == "healthy":
        logger.info("✅ Database connection established")
        logger.info(f"📊 Pool status: {db_health['pool']}")
    else:
        logger.error(f"❌ Database connection failed: {db_health['error']}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down OpenMRS Bridge API")


# Create FastAPI app with optimizations
app = FastAPI(
    title="OpenMRS Bridge API (Optimized)",
    description="High-performance FastAPI service for OpenMRS database integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Performance middleware
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """Middleware to track request performance"""
    start_time = time.time()
    
    # Add request ID for tracking
    request_id = f"{request.method}_{request.url.path}"
    
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Track request times
    if request_id not in request_times:
        request_times[request_id] = []
    request_times[request_id].append(process_time)
    
    # Keep only last 100 requests for each endpoint
    if len(request_times[request_id]) > 100:
        request_times[request_id] = request_times[request_id][-100:]
    
    # Add performance headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id
    
    # Log slow requests
    if process_time > 1.0:  # Log requests taking more than 1 second
        logger.warning(f"🐌 Slow request: {request_id} took {process_time:.3f}s")
    
    return response


# Add CORS middleware with optimized settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Add GZip compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure properly for production
)


# Global exception handler with performance logging
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if getattr(settings, 'debug', False) else "An unexpected error occurred",
            "request_id": f"{request.method}_{request.url.path}"
        }
    )


# Enhanced health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Enhanced health check with performance metrics"""
    # Check database health
    db_health = await check_db_health()
    
    # Get performance metrics
    avg_response_times = {}
    for endpoint, times in request_times.items():
        if times:
            avg_response_times[endpoint] = sum(times) / len(times)
    
    return {
        "status": "healthy" if db_health["status"] == "healthy" else "degraded",
        "service": "OpenMRS Bridge API (Optimized)",
        "version": "2.0.0",
        "database": db_health,
        "performance": {
            "average_response_times": avg_response_times,
            "total_requests_tracked": sum(len(times) for times in request_times.values())
        },
        "timestamp": time.time()
    }


# Database statistics endpoint
@app.get("/stats", tags=["monitoring"])
async def get_stats(
    db=Depends(get_async_db),
    api_key: str = Depends(get_current_api_key)
):
    """Get database statistics and performance metrics"""
    try:
        # Get database stats
        db_stats = await get_database_stats_async(db)
        
        # Get connection pool status
        pool_status = await get_pool_status()
        
        # Calculate performance metrics
        performance_metrics = {}
        for endpoint, times in request_times.items():
            if times:
                performance_metrics[endpoint] = {
                    "average_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "request_count": len(times)
                }
        
        return {
            "database": db_stats,
            "connection_pool": pool_status,
            "performance": performance_metrics,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


# API key generation endpoint (for development/testing)
@app.post("/generate-api-key", tags=["admin"])
async def generate_new_api_key():
    """Generate a new API key for testing"""
    api_key = generate_api_key()
    return {
        "api_key": api_key,
        "message": "Add this key to your API_KEYS environment variable"
    }


# Include routers with optimized prefixes
app.include_router(orders_router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(observations_router, prefix="/api/v1/observations", tags=["observations"])


# Root endpoint with performance info
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information and performance metrics"""
    # Get basic performance metrics
    total_requests = sum(len(times) for times in request_times.values())
    avg_response_time = 0
    
    if total_requests > 0:
        all_times = [time for times in request_times.values() for time in times]
        avg_response_time = sum(all_times) / len(all_times)
    
    return {
        "message": "OpenMRS Bridge API (Optimized)",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health",
        "stats": "/stats",
        "performance": {
            "total_requests": total_requests,
            "average_response_time": f"{avg_response_time:.3f}s",
            "endpoints_tracked": len(request_times)
        }
    }


# Performance monitoring endpoint
@app.get("/performance", tags=["monitoring"])
async def get_performance_metrics():
    """Get detailed performance metrics"""
    metrics = {}
    
    for endpoint, times in request_times.items():
        if times:
            sorted_times = sorted(times)
            metrics[endpoint] = {
                "count": len(times),
                "average": sum(times) / len(times),
                "median": sorted_times[len(sorted_times) // 2],
                "min": min(times),
                "max": max(times),
                "p95": sorted_times[int(len(sorted_times) * 0.95)],
                "p99": sorted_times[int(len(sorted_times) * 0.99)]
            }
    
    return {
        "endpoints": metrics,
        "summary": {
            "total_requests": sum(len(times) for times in request_times.values()),
            "total_endpoints": len(request_times),
            "timestamp": time.time()
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_optimized:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        workers=1,  # Use multiple workers in production
        loop="asyncio",
        access_log=True
    ) 