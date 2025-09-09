"""
Test SQLAlchemy models
"""

import pytest
from datetime import datetime
from models.reactor import Reactor, ReactorStatus, ReactorType
from models.telemetry import Telemetry
from models.fault import Fault, FaultSeverity
from models.knowledge_base import KnowledgeBase

class TestReactorModel:
    """Test Reactor model functionality"""
    
    def test_reactor_creation(self, test_db_session, sample_reactor_data):
        """Test reactor creation and basic properties"""
        reactor = Reactor.create_from_dict(sample_reactor_data)
        test_db_session.add(reactor)
        test_db_session.commit()
        
        assert reactor.id is not None
        assert reactor.name == "Test Reactor 1"
        assert reactor.type == ReactorType.CANDU
        assert reactor.status == ReactorStatus.healthy
        assert reactor.health_score == 95.0

    def test_reactor_to_dict(self, test_db_session, sample_reactor_data):
        """Test reactor dictionary serialization"""
        reactor = Reactor.create_from_dict(sample_reactor_data)
        test_db_session.add(reactor)
        test_db_session.commit()
        
        reactor_dict = reactor.to_dict()
        assert reactor_dict["name"] == "Test Reactor 1"
        assert reactor_dict["type"] == "CANDU"
        assert reactor_dict["status"] == "healthy"
        assert reactor_dict["location"]["lat"] == 44.0
        assert reactor_dict["location"]["lng"] == -81.0

    def test_health_score_update(self, test_db_session, sample_reactor_data):
        """Test health score update and status calculation"""
        reactor = Reactor.create_from_dict(sample_reactor_data)
        test_db_session.add(reactor)
        test_db_session.commit()
        
        # Test healthy range
        reactor.update_health_score(95.0)
        assert reactor.status == ReactorStatus.healthy
        
        # Test warning range
        reactor.update_health_score(75.0)
        assert reactor.status == ReactorStatus.warning
        
        # Test unhealthy range
        reactor.update_health_score(65.0)
        assert reactor.status == ReactorStatus.unhealthy

class TestTelemetryModel:
    """Test Telemetry model functionality"""
    
    def test_telemetry_creation(self, test_db_session, sample_reactor_data, sample_telemetry_data):
        """Test telemetry creation"""
        # Create reactor first
        reactor = Reactor.create_from_dict(sample_reactor_data)
        test_db_session.add(reactor)
        test_db_session.commit()
        
        # Update telemetry data with reactor ID
        sample_telemetry_data["reactor_id"] = reactor.id
        
        telemetry = Telemetry.create_from_dict(sample_telemetry_data)
        test_db_session.add(telemetry)
        test_db_session.commit()
        
        assert telemetry.id is not None
        assert telemetry.reactor_id == reactor.id
        assert telemetry.neutron_flux == 1.2e13

    def test_normal_ranges_validation(self, test_db_session, sample_reactor_data, sample_telemetry_data):
        """Test telemetry normal range validation"""
        # Create reactor first
        reactor = Reactor.create_from_dict(sample_reactor_data)
        test_db_session.add(reactor)
        test_db_session.commit()
        
        sample_telemetry_data["reactor_id"] = reactor.id
        telemetry = Telemetry.create_from_dict(sample_telemetry_data)
        
        is_normal, issues = telemetry.is_within_normal_ranges()
        assert is_normal == True
        assert len(issues) == 0

    def test_health_contribution(self, test_db_session, sample_reactor_data, sample_telemetry_data):
        """Test health contribution calculation"""
        # Create reactor first
        reactor = Reactor.create_from_dict(sample_reactor_data)
        test_db_session.add(reactor)
        test_db_session.commit()
        
        sample_telemetry_data["reactor_id"] = reactor.id
        telemetry = Telemetry.create_from_dict(sample_telemetry_data)
        
        health_contribution = telemetry.calculate_health_contribution()
        assert health_contribution == 100.0  # Normal values should give 100%

class TestFaultModel:
    """Test Fault model functionality"""
    
    def test_fault_creation(self, test_db_session, sample_reactor_data, sample_fault_data):
        """Test fault creation"""
        # Create reactor first
        reactor = Reactor.create_from_dict(sample_reactor_data)
        test_db_session.add(reactor)
        test_db_session.commit()
        
        sample_fault_data["reactor_id"] = reactor.id
        fault = Fault.create_from_dict(sample_fault_data)
        test_db_session.add(fault)
        test_db_session.commit()
        
        assert fault.id is not None
        assert fault.reactor_id == reactor.id
        assert fault.severity == FaultSeverity.yellow
        assert fault.resolved == False

    def test_fault_resolution(self, test_db_session, sample_reactor_data, sample_fault_data):
        """Test fault resolution"""
        # Create reactor first
        reactor = Reactor.create_from_dict(sample_reactor_data)
        test_db_session.add(reactor)
        test_db_session.commit()
        
        sample_fault_data["reactor_id"] = reactor.id
        fault = Fault.create_from_dict(sample_fault_data)
        test_db_session.add(fault)
        test_db_session.commit()
        
        # Resolve fault
        fault.resolve()
        test_db_session.commit()
        
        assert fault.resolved == True
        assert fault.resolved_at is not None

class TestKnowledgeBaseModel:
    """Test KnowledgeBase model functionality"""
    
    def test_knowledge_base_creation(self, test_db_session):
        """Test knowledge base document creation"""
        doc_data = {
            "document_name": "Test Manual",
            "content": "This is a test manual for nuclear reactor operations.",
            "metadata": {"document_type": "manual", "tags": ["test", "manual"]}
        }
        
        doc = KnowledgeBase.create_from_dict(doc_data)
        test_db_session.add(doc)
        test_db_session.commit()
        
        assert doc.id is not None
        assert doc.document_name == "Test Manual"
        assert doc.doc_metadata["document_type"] == "manual"

    def test_document_tagging(self, test_db_session):
        """Test document tag management"""
        doc_data = {
            "document_name": "Test Document",
            "content": "Test content",
            "metadata": {}
        }
        
        doc = KnowledgeBase.create_from_dict(doc_data)
        test_db_session.add(doc)
        test_db_session.commit()
        
        # Add tags
        doc.add_tag("nuclear")
        doc.add_tag("safety")
        doc.set_document_type("procedure")
        
        test_db_session.commit()
        
        assert "nuclear" in doc.get_tags()
        assert "safety" in doc.get_tags()
        assert doc.get_document_type() == "procedure"
