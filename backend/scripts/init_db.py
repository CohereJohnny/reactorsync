#!/usr/bin/env python3
"""
Database initialization script for ReactorSync

This script sets up the database schema and loads sample data.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from models.base import engine, Base
from services.database_service import DatabaseService
from sqlalchemy import text
import structlog

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

def create_extensions():
    """Create required PostgreSQL extensions"""
    try:
        with engine.connect() as conn:
            # Create pgvector extension
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            logger.info("pgvector extension created")
    except Exception as e:
        logger.error("Failed to create extensions", error=str(e))
        raise

def create_schema():
    """Create database schema from models"""
    try:
        # Import all models to ensure they're registered
        from models import Reactor, Telemetry, Fault, KnowledgeBase
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema created")
    except Exception as e:
        logger.error("Failed to create schema", error=str(e))
        raise

def load_sample_data():
    """Load sample data for development"""
    try:
        result = DatabaseService.initialize_sample_data()
        logger.info("Sample data loading result", result=result)
        return result
    except Exception as e:
        logger.error("Failed to load sample data", error=str(e))
        raise

def main():
    """Main initialization function"""
    logger.info("Starting database initialization")
    
    try:
        # Step 1: Create extensions
        logger.info("Creating PostgreSQL extensions...")
        create_extensions()
        
        # Step 2: Create schema
        logger.info("Creating database schema...")
        create_schema()
        
        # Step 3: Load sample data
        logger.info("Loading sample data...")
        sample_result = load_sample_data()
        
        # Step 4: Verify setup
        logger.info("Verifying database setup...")
        health_check = DatabaseService.health_check()
        
        if health_check["database_connected"]:
            logger.info("Database initialization completed successfully")
            print("✅ Database initialization completed successfully!")
            print(f"✅ Reactor count: {health_check.get('reactor_count', 0)}")
            print(f"✅ pgvector available: {health_check.get('pgvector_available', False)}")
        else:
            logger.error("Database health check failed after initialization")
            print("❌ Database initialization failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        print(f"❌ Database initialization failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
