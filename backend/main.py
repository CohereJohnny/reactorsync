"""
ReactorSync Backend - FastAPI Application
Main entry point for the nuclear reactor management API
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from models.base import get_db
from services.database_service import DatabaseService
from repositories import ReactorRepository, TelemetryRepository, FaultRepository
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
    db_health = DatabaseService.health_check()
    
    return {
        "status": "healthy" if db_health.get("database_connected") else "unhealthy",
        "service": "reactorsync-backend",
        "version": "1.0.0",
        "database": db_health
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


# Reactor endpoints
@app.get("/reactors")
async def list_reactors(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    reactor_type: str = None,
    sort_by: str = "name",
    sort_order: str = "asc",
    db: Session = Depends(get_db)
):
    """List all reactors with filtering and pagination"""
    try:
        reactor_repo = ReactorRepository(db)
        
        # Convert string filters to enums if provided
        from models.reactor import ReactorStatus, ReactorType
        status_filter = ReactorStatus(status) if status else None
        type_filter = ReactorType(reactor_type) if reactor_type else None
        
        reactors = reactor_repo.get_all(
            skip=skip,
            limit=limit,
            status_filter=status_filter,
            reactor_type_filter=type_filter,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return {
            "reactors": [reactor.to_dict() for reactor in reactors],
            "total": len(reactors),
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error("Error listing reactors", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve reactors: {str(e)}")


@app.get("/reactors/{reactor_id}")
async def get_reactor(reactor_id: int, db: Session = Depends(get_db)):
    """Get specific reactor by ID"""
    try:
        reactor_repo = ReactorRepository(db)
        reactor = reactor_repo.get_by_id(reactor_id)
        
        if not reactor:
            raise HTTPException(status_code=404, detail="Reactor not found")
        
        return reactor.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error retrieving reactor", reactor_id=reactor_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve reactor: {str(e)}")


@app.get("/telemetry/{reactor_id}")
async def get_telemetry(
    reactor_id: int,
    start_time: str = None,
    end_time: str = None,
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """Get telemetry data for a specific reactor"""
    try:
        from datetime import datetime
        
        # Parse time parameters
        start_dt = datetime.fromisoformat(start_time) if start_time else None
        end_dt = datetime.fromisoformat(end_time) if end_time else None
        
        telemetry_repo = TelemetryRepository(db)
        telemetry_data = telemetry_repo.get_by_reactor(
            reactor_id=reactor_id,
            start_time=start_dt,
            end_time=end_dt,
            limit=limit
        )
        
        return {
            "reactor_id": reactor_id,
            "telemetry": [data.to_dict() for data in telemetry_data],
            "count": len(telemetry_data),
            "start_time": start_time,
            "end_time": end_time
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid time format: {str(e)}")
    except Exception as e:
        logger.error("Error retrieving telemetry", reactor_id=reactor_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve telemetry: {str(e)}")


@app.get("/reactors/{reactor_id}/faults")
async def get_reactor_faults(reactor_id: int, db: Session = Depends(get_db)):
    """Get faults for a specific reactor"""
    try:
        fault_repo = FaultRepository(db)
        fault_summary = fault_repo.get_reactor_fault_summary(reactor_id)
        
        return fault_summary
        
    except Exception as e:
        logger.error("Error retrieving reactor faults", reactor_id=reactor_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to retrieve faults: {str(e)}")


@app.post("/admin/initialize-data")
async def initialize_sample_data():
    """Initialize sample data for development and demo (admin endpoint)"""
    result = DatabaseService.initialize_sample_data()
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result


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
