"""
Database Service - High-level database operations and connection management
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from contextlib import contextmanager
from models.base import SessionLocal, engine
from models.reactor import Reactor
from repositories import ReactorRepository, TelemetryRepository, FaultRepository, KnowledgeBaseRepository
import structlog

logger = structlog.get_logger()

class DatabaseService:
    """Service for managing database operations and connections"""
    
    @staticmethod
    @contextmanager
    def get_session():
        """Context manager for database sessions with automatic cleanup"""
        session = SessionLocal()
        try:
            yield session
        except SQLAlchemyError as e:
            session.rollback()
            logger.error("Database error", error=str(e))
            raise
        finally:
            session.close()

    @staticmethod
    def get_repositories(db_session: Session) -> Dict[str, Any]:
        """Get all repository instances for a database session"""
        return {
            "reactors": ReactorRepository(db_session),
            "telemetry": TelemetryRepository(db_session),
            "faults": FaultRepository(db_session),
            "knowledge_base": KnowledgeBaseRepository(db_session)
        }

    @staticmethod
    def health_check() -> Dict[str, Any]:
        """Check database connectivity and health"""
        try:
            with DatabaseService.get_session() as db:
                # Test basic connectivity
                db.execute(text("SELECT 1"))
                
                # Check pgvector extension
                result = db.execute(text("SELECT 1 FROM pg_extension WHERE extname='vector'")).fetchone()
                pgvector_available = result is not None
                
                # Get basic statistics
                reactor_count = db.query(Reactor).count()
                
                return {
                    "status": "healthy",
                    "database_connected": True,
                    "pgvector_available": pgvector_available,
                    "reactor_count": reactor_count,
                    "connection_pool": {
                        "size": getattr(engine.pool, 'size', lambda: 0)(),
                        "checked_in": getattr(engine.pool, 'checkedin', lambda: 0)(),
                        "checked_out": getattr(engine.pool, 'checkedout', lambda: 0)(),
                        "overflow": getattr(engine.pool, 'overflow', lambda: 0)(),
                    }
                }
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "database_connected": False,
                "error": str(e)
            }

    @staticmethod
    def initialize_sample_data() -> Dict[str, Any]:
        """Initialize sample data for development and demo"""
        try:
            with DatabaseService.get_session() as db:
                repos = DatabaseService.get_repositories(db)
                
                # Check if data already exists
                existing_reactors = repos["reactors"].get_all(limit=1)
                if existing_reactors:
                    return {
                        "status": "skipped",
                        "message": "Sample data already exists",
                        "reactor_count": len(repos["reactors"].get_all())
                    }
                
                # Sample reactor data
                sample_reactors = [
                    {
                        "name": "Bruce-A Unit 1",
                        "type": "CANDU",
                        "location": {"lat": 44.3167, "lng": -81.6000},
                        "status": "healthy",
                        "health_score": 95.2
                    },
                    {
                        "name": "Bruce-A Unit 2", 
                        "type": "CANDU",
                        "location": {"lat": 44.3167, "lng": -81.6000},
                        "status": "healthy",
                        "health_score": 92.8
                    },
                    {
                        "name": "Darlington Unit 1",
                        "type": "CANDU", 
                        "location": {"lat": 43.8833, "lng": -78.7167},
                        "status": "warning",
                        "health_score": 78.5
                    },
                    {
                        "name": "SMR Prototype Alpha",
                        "type": "SMR",
                        "location": {"lat": 45.4215, "lng": -75.6972},
                        "status": "healthy",
                        "health_score": 98.5
                    }
                ]
                
                # Create reactors
                created_reactors = []
                for reactor_data in sample_reactors:
                    reactor = repos["reactors"].create(reactor_data)
                    created_reactors.append(reactor)
                
                logger.info("Sample data initialized", reactor_count=len(created_reactors))
                
                return {
                    "status": "success",
                    "message": "Sample data initialized",
                    "reactor_count": len(created_reactors),
                    "reactors": [r.to_dict() for r in created_reactors]
                }
                
        except Exception as e:
            logger.error("Failed to initialize sample data", error=str(e))
            return {
                "status": "error",
                "message": f"Failed to initialize sample data: {str(e)}"
            }

    @staticmethod
    def reset_database() -> Dict[str, Any]:
        """Reset database to clean state (development only)"""
        try:
            with DatabaseService.get_session() as db:
                # Delete all data in reverse order of dependencies
                db.execute(text("TRUNCATE knowledge_base, faults, telemetry, reactors RESTART IDENTITY CASCADE"))
                db.commit()
                
                logger.warning("Database reset completed")
                
                return {
                    "status": "success",
                    "message": "Database reset completed"
                }
                
        except Exception as e:
            logger.error("Database reset failed", error=str(e))
            return {
                "status": "error", 
                "message": f"Database reset failed: {str(e)}"
            }

    @staticmethod
    def get_system_statistics() -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            with DatabaseService.get_session() as db:
                repos = DatabaseService.get_repositories(db)
                
                # Get statistics from all repositories
                reactor_stats = repos["reactors"].get_statistics()
                fault_stats = repos["faults"].get_fault_statistics()
                kb_stats = repos["knowledge_base"].get_statistics()
                
                return {
                    "reactors": reactor_stats,
                    "faults": fault_stats,
                    "knowledge_base": kb_stats,
                    "database": DatabaseService.health_check()
                }
                
        except Exception as e:
            logger.error("Failed to get system statistics", error=str(e))
            return {
                "error": f"Failed to get statistics: {str(e)}"
            }
