"""
Telemetry SQLAlchemy model
"""

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import relationship
from .base import Base

class Telemetry(Base):
    """
    Reactor telemetry data model
    
    Stores time-series telemetry data from nuclear reactors including
    neutron flux, temperature, pressure, vibration, and tritium levels.
    """
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    reactor_id = Column(Integer, ForeignKey("reactors.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Core telemetry metrics
    neutron_flux = Column(Float)  # n/cm²/s
    core_temperature = Column(Float)  # °C
    pressure = Column(Float)  # MPa
    vibration = Column(Float)  # mm/s
    tritium_level = Column(Float)  # pCi/L
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    reactor = relationship("Reactor", back_populates="telemetry")

    # Composite indexes for performance
    __table_args__ = (
        Index('ix_telemetry_reactor_timestamp', 'reactor_id', 'timestamp'),
        Index('ix_telemetry_timestamp_reactor', 'timestamp', 'reactor_id'),
    )

    def __repr__(self):
        return f"<Telemetry(reactor_id={self.reactor_id}, timestamp={self.timestamp})>"

    def to_dict(self):
        """Convert telemetry to dictionary for API responses"""
        return {
            "id": self.id,
            "reactor_id": self.reactor_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "neutron_flux": self.neutron_flux,
            "core_temperature": self.core_temperature,
            "pressure": self.pressure,
            "vibration": self.vibration,
            "tritium_level": self.tritium_level,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def create_from_dict(cls, data: dict):
        """Create telemetry from dictionary data"""
        return cls(
            reactor_id=data["reactor_id"],
            timestamp=data["timestamp"],
            neutron_flux=data.get("neutron_flux"),
            core_temperature=data.get("core_temperature"),
            pressure=data.get("pressure"),
            vibration=data.get("vibration"),
            tritium_level=data.get("tritium_level")
        )

    def is_within_normal_ranges(self):
        """Check if telemetry values are within normal operating ranges"""
        normal_ranges = {
            "neutron_flux": (1.0e13, 1.5e13),  # n/cm²/s
            "core_temperature": (260, 320),     # °C
            "pressure": (10, 15),               # MPa
            "vibration": (0, 5),                # mm/s
            "tritium_level": (0, 1000)          # pCi/L
        }
        
        issues = []
        
        for metric, (min_val, max_val) in normal_ranges.items():
            value = getattr(self, metric)
            if value is not None and not (min_val <= value <= max_val):
                issues.append({
                    "metric": metric,
                    "value": value,
                    "normal_range": [min_val, max_val],
                    "status": "high" if value > max_val else "low"
                })
        
        return len(issues) == 0, issues

    def calculate_health_contribution(self):
        """Calculate this telemetry reading's contribution to reactor health score"""
        is_normal, issues = self.is_within_normal_ranges()
        
        if is_normal:
            return 100.0
        
        # Deduct points based on severity of issues
        health_score = 100.0
        for issue in issues:
            if issue["status"] == "high":
                health_score -= 15  # High values are more concerning
            else:
                health_score -= 10  # Low values are less concerning
        
        return max(0.0, health_score)
