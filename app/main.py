import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.orders import router as orders_router
from app.api.observations import router as observations_router
from app.api.concepts import router as concepts_router
from app.api.diagnoses import router as diagnoses_router
from app.api.encounters import router as encounters_router
from app.api.order_types import router as order_types_router
from app.api.drugs import router as drugs_router
from app.api.system import router as system_router
from app.api.visits import router as visits_router
from app.api.vitals import router as vitals_router
from app.config import settings
from app.auth import generate_api_key


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="OpenMRS Bridge API",
    description="FastAPI service for connecting with OpenMRS database and providing REST API endpoints",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Limit to only the allowed origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc)
            if getattr(settings, "debug", False)
            else "An unexpected error occurred",
        },
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "OpenMRS Bridge API",
        "version": "1.0.0",
    }


# API key generation endpoint (for development/testing)
@app.post("/generate-api-key", tags=["admin"])
async def generate_new_api_key():
    """Generate a new API key for testing"""
    api_key = generate_api_key()
    return {
        "api_key": api_key,
        "message": "Add this key to your API_KEYS environment variable",
    }


# Include routers
app.include_router(
    orders_router,
    prefix="/api/v1/orders",
    tags=["orders"],
)
app.include_router(
    observations_router,
    prefix="/api/v1/observations",
    tags=["observations"],
)
app.include_router(
    concepts_router,
    prefix="/api/v1/concepts",
    tags=["concepts"],
)
app.include_router(
    diagnoses_router,
    prefix="/api/v1/diagnoses",
    tags=["diagnoses"],
)
app.include_router(
    encounters_router,
    prefix="/api/v1/encounters",
    tags=["encounters"],
)
app.include_router(
    order_types_router,
    prefix="/api/v1/order-types",
    tags=["order-types"],
)
app.include_router(
    visits_router,
    prefix="/api/v1/visits",
    tags=["visits"],
)
app.include_router(
    vitals_router,
    prefix="/api/v1/vitals",
    tags=["vitals"],
)
app.include_router(
    drugs_router,
    prefix="/api/v1/drugs",
    tags=["drugs"],
)
app.include_router(
    system_router,
    prefix="/api/v1/system",
    tags=["system"],
)


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "OpenMRS Bridge API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
