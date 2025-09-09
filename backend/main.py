"""
ReactorSync Backend - FastAPI Application
Main entry point for the nuclear reactor management API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
import os
from contextlib import asynccontextmanager

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting ReactorSync backend")
    yield
    # Shutdown
    logger.info("Shutting down ReactorSync backend")


# Create FastAPI application
app = FastAPI(
    title="ReactorSync API",
    description="AI-enabled Nuclear Reactor Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Frontend development
        "http://frontend:3000",   # Docker container
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "service": "reactorsync-backend",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "ReactorSync Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Basic reactor endpoint (placeholder for now)
@app.get("/reactors")
async def list_reactors():
    """List all reactors - placeholder implementation"""
    return {
        "reactors": [
            {
                "id": 1,
                "name": "Bruce-A Unit 1",
                "type": "CANDU",
                "location": {"lat": 44.3167, "lng": -81.6000},
                "status": "healthy",
                "health_score": 95.2
            },
            {
                "id": 2,
                "name": "Darlington Unit 2", 
                "type": "CANDU",
                "location": {"lat": 43.8833, "lng": -78.7167},
                "status": "warning",
                "health_score": 78.5
            }
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("BACKEND_PORT", 8000))
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )
