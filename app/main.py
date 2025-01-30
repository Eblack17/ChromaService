from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .core.config import get_settings
from .core.middleware import RateLimitMiddleware
from .agents.routes import router as agents_router
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="""
    ChromaPages AI Customer Service API
    
    This API provides access to AI-powered customer service agents specialized in ChromaPages support.
    
    Rate Limits:
    - Free tier: 20 requests/minute, 100 requests/hour
    - Pro tier: 60 requests/minute, 1000 requests/hour
    - Enterprise tier: 120 requests/minute, 5000 requests/hour
    
    All endpoints return rate limit information in the response headers:
    - X-RateLimit-Limit-Minute: Maximum requests per minute
    - X-RateLimit-Remaining-Minute: Remaining requests for the current minute
    - X-RateLimit-Limit-Hour: Maximum requests per hour
    - X-RateLimit-Remaining-Hour: Remaining requests for the current hour
    """
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Include agent routes
app.include_router(agents_router, prefix="/api/agents", tags=["agents"])

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to ChromaPages AI Customer Service System",
        "version": settings.APP_VERSION,
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "version": settings.APP_VERSION
    }

@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info("Starting ChromaPages AI Customer Service API")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Debug mode: {settings.DEBUG}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler."""
    logger.info("Shutting down ChromaPages AI Customer Service API")

# Import and include routers here as they are developed
# Example:
# from .agents.routes import router as agents_router
# app.include_router(agents_router, prefix="/agents", tags=["agents"]) 