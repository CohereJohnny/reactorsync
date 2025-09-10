"""
Test configuration and fixtures for ReactorSync backend tests
"""

import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from models.base import Base
from models import Reactor, Telemetry, Fault, KnowledgeBase

# Test database URL - use in-memory SQLite for fast tests
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def test_engine():
    """Create test database engine"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    return engine

@pytest.fixture(scope="function")
def test_db_session(test_engine):
    """Create test database session"""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def sample_reactor_data():
    """Sample reactor data for testing"""
    return {
        "name": "Test Reactor 1",
        "type": "CANDU",
        "location": {"lat": 44.0, "lng": -81.0},
        "status": "healthy",
        "health_score": 95.0
    }

@pytest.fixture
def sample_telemetry_data():
    """Sample telemetry data for testing"""
    from datetime import datetime
    return {
        "reactor_id": 1,
        "timestamp": datetime.utcnow(),
        "neutron_flux": 1.2e13,
        "core_temperature": 285.5,
        "pressure": 12.3,
        "vibration": 2.1,
        "tritium_level": 450.0
    }

@pytest.fixture
def sample_fault_data():
    """Sample fault data for testing"""
    from datetime import datetime
    return {
        "reactor_id": 1,
        "fault_type": "temperature_spike",
        "severity": "yellow",
        "description": "Core temperature exceeded normal range",
        "timestamp": datetime.utcnow(),
        "resolved": False
    }
