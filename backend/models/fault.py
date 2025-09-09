"""
Fault SQLAlchemy model
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from .base import Base
import enum

class FaultSeverity(enum.Enum):
    """Fault severity levels"""
    yellow = "yellow"
    red = "red"

class Fault(Base):
    """
    Reactor fault/incident model
    
    Tracks faults, anomalies, and incidents that occur in nuclear reactors
    for monitoring, analysis, and regulatory compliance.
    """
    __tablename__ = "faults"

    id = Column(Integer, primary_key=True, index=True)
    reactor_id = Column(Integer, ForeignKey("reactors.id", ondelete="CASCADE"), nullable=False, index=True)
    fault_type = Column(String(255), nullable=False, index=True)
    severity = Column(Enum(FaultSeverity), nullable=False)
    description = Column(Text)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    resolved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True))

    # Relationships
    reactor = relationship("Reactor", back_populates="faults")

    def __repr__(self):
        return f"<Fault(id={self.id}, type='{self.fault_type}', severity={self.severity.value}, resolved={self.resolved})>"

    def to_dict(self):
        """Convert fault to dictionary for API responses"""
        return {
            "id": self.id,
            "reactor_id": self.reactor_id,
            "fault_type": self.fault_type,
            "severity": self.severity.value,
            "description": self.description,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "resolved": self.resolved,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }

    @classmethod
    def create_from_dict(cls, data: dict):
        """Create fault from dictionary data"""
        return cls(
            reactor_id=data["reactor_id"],
            fault_type=data["fault_type"],
            severity=FaultSeverity(data["severity"]),
            description=data.get("description"),
            timestamp=data["timestamp"],
            resolved=data.get("resolved", False)
        )

    def resolve(self):
        """Mark fault as resolved"""
        self.resolved = True
        self.resolved_at = func.now()

    def get_health_impact(self):
        """Get the health score impact of this fault"""
        if self.resolved:
            return 0
        
        # Red faults have higher impact than yellow
        if self.severity == FaultSeverity.red:
            return 25  # Major impact
        else:
            return 10  # Minor impact

    @property
    def is_critical(self):
        """Check if fault is critical (red severity and unresolved)"""
        return self.severity == FaultSeverity.red and not self.resolved

    @property
    def duration_hours(self):
        """Get fault duration in hours"""
        if self.resolved and self.resolved_at:
            end_time = self.resolved_at
        else:
            end_time = func.now()
        
        duration = end_time - self.timestamp
        return duration.total_seconds() / 3600 if duration else 0

    @classmethod
    def get_common_fault_types(cls):
        """Get list of common fault types for validation"""
        return [
            "temperature_spike",
            "pressure_anomaly", 
            "vibration_high",
            "flux_instability",
            "coolant_leak",
            "pump_failure",
            "sensor_malfunction",
            "control_rod_stuck",
            "tritium_high"
        ]
