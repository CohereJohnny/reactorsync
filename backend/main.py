"""
ReactorSync Backend - FastAPI Application
Main entry point for the nuclear reactor management API
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import asyncio
import json
from typing import List, Dict
from datetime import datetime
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

# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.reactor_subscriptions: Dict[int, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept a WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("WebSocket client connected", total_connections=len(self.active_connections))
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from reactor subscriptions
        for reactor_id, connections in self.reactor_subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)
        
        logger.info("WebSocket client disconnected", total_connections=len(self.active_connections))
    
    def subscribe_to_reactor(self, websocket: WebSocket, reactor_id: int):
        """Subscribe a WebSocket to reactor updates"""
        if reactor_id not in self.reactor_subscriptions:
            self.reactor_subscriptions[reactor_id] = []
        
        if websocket not in self.reactor_subscriptions[reactor_id]:
            self.reactor_subscriptions[reactor_id].append(websocket)
        
        logger.debug("Client subscribed to reactor", reactor_id=reactor_id)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message, default=str))
            except Exception:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_to_reactor_subscribers(self, reactor_id: int, message: dict):
        """Broadcast message to clients subscribed to a specific reactor"""
        if reactor_id not in self.reactor_subscriptions:
            return
        
        connections = self.reactor_subscriptions[reactor_id].copy()
        disconnected = []
        
        for connection in connections:
            try:
                await connection.send_text(json.dumps(message, default=str))
            except Exception:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

# Global connection manager
websocket_manager = ConnectionManager()


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


# WebSocket endpoints
@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    """WebSocket endpoint for real-time telemetry updates"""
    await websocket_manager.connect(websocket)
    
    try:
        while True:
            # Wait for client messages (subscription requests)
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "subscribe_reactor":
                reactor_id = message.get("reactor_id")
                if reactor_id:
                    websocket_manager.subscribe_to_reactor(websocket, reactor_id)
                    await websocket.send_text(json.dumps({
                        "type": "subscription_confirmed",
                        "reactor_id": reactor_id
                    }))
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
        websocket_manager.disconnect(websocket)


@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket endpoint for real-time alert/fault updates"""
    await websocket_manager.connect(websocket)
    
    try:
        while True:
            # Keep connection alive and handle client messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("action") == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket alerts error", error=str(e))
        websocket_manager.disconnect(websocket)


# Admin endpoints for anomaly injection
@app.post("/admin/inject-anomaly")
async def inject_anomaly(
    reactor_id: int,
    anomaly_type: str,
    severity: str = "yellow",
    duration_minutes: int = 30
):
    """Inject an anomaly for demo purposes"""
    # This will be connected to the data generator service
    # For now, return success
    
    # Broadcast anomaly injection to WebSocket clients
    await websocket_manager.broadcast_to_reactor_subscribers(reactor_id, {
        "type": "anomaly_injected",
        "reactor_id": reactor_id,
        "anomaly_type": anomaly_type,
        "severity": severity,
        "duration_minutes": duration_minutes,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return {
        "status": "success",
        "message": f"Anomaly '{anomaly_type}' injected into reactor {reactor_id}",
        "reactor_id": reactor_id,
        "anomaly_type": anomaly_type,
        "severity": severity,
        "duration_minutes": duration_minutes
    }


@app.post("/admin/clear-anomaly")
async def clear_anomaly(reactor_id: int):
    """Clear any active anomaly for a reactor"""
    # Broadcast anomaly clearing to WebSocket clients
    await websocket_manager.broadcast_to_reactor_subscribers(reactor_id, {
        "type": "anomaly_cleared",
        "reactor_id": reactor_id,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return {
        "status": "success",
        "message": f"Anomaly cleared for reactor {reactor_id}",
        "reactor_id": reactor_id
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
