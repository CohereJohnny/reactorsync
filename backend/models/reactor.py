"""
Reactor SQLAlchemy model
"""

from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, func
from sqlalchemy.orm import relationship
from .base import Base
import enum

class ReactorStatus(enum.Enum):
    """Reactor operational status"""
    healthy = "healthy"
    warning = "warning" 
    unhealthy = "unhealthy"

class ReactorType(enum.Enum):
    """Reactor type classification"""
    CANDU = "CANDU"
    SMR = "SMR"
    PWR = "PWR"
    BWR = "BWR"

class Reactor(Base):
    """
    Nuclear reactor model
    
    Represents a nuclear reactor facility with its basic information,
    location, operational status, and health metrics.
    """
    __tablename__ = "reactors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    type = Column(Enum(ReactorType), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(Enum(ReactorStatus), nullable=False, default=ReactorStatus.healthy)
    health_score = Column(Float, nullable=False, default=100.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    telemetry = relationship("Telemetry", back_populates="reactor", cascade="all, delete-orphan")
    faults = relationship("Fault", back_populates="reactor", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Reactor(id={self.id}, name='{self.name}', type={self.type.value}, status={self.status.value})>"

    def to_dict(self):
        """Convert reactor to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "location": {
                "lat": self.latitude,
                "lng": self.longitude
            },
            "status": self.status.value,
            "health_score": self.health_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    def update_health_score(self, score: float):
        """Update health score and set appropriate status"""
        self.health_score = max(0.0, min(100.0, score))
        
        if self.health_score >= 90:
            self.status = ReactorStatus.healthy
        elif self.health_score >= 70:
            self.status = ReactorStatus.warning
        else:
            self.status = ReactorStatus.unhealthy

    @property
    def location_dict(self):
        """Get location as dictionary"""
        return {"lat": self.latitude, "lng": self.longitude}

    @classmethod
    def create_from_dict(cls, data: dict):
        """Create reactor from dictionary data"""
        location = data.get("location", {})
        return cls(
            name=data["name"],
            type=ReactorType(data["type"]),
            latitude=location.get("lat", 0.0),
            longitude=location.get("lng", 0.0),
            status=ReactorStatus(data.get("status", "healthy")),
            health_score=data.get("health_score", 100.0)
        )
