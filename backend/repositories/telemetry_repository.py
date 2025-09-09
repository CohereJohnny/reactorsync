"""
Telemetry Repository - Data access layer for telemetry operations
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from models.telemetry import Telemetry
from models.reactor import Reactor
import structlog

logger = structlog.get_logger()

class TelemetryRepository:
    """Repository for telemetry data access operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_by_reactor(
        self,
        reactor_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Telemetry]:
        """
        Get telemetry data for a specific reactor
        
        Args:
            reactor_id: ID of the reactor
            start_time: Start of time range
            end_time: End of time range
            limit: Maximum number of records
        """
        query = self.db.query(Telemetry).filter(Telemetry.reactor_id == reactor_id)
        
        if start_time:
            query = query.filter(Telemetry.timestamp >= start_time)
        
        if end_time:
            query = query.filter(Telemetry.timestamp <= end_time)
        
        return query.order_by(desc(Telemetry.timestamp)).limit(limit).all()

    def get_latest(self, reactor_id: int) -> Optional[Telemetry]:
        """Get the most recent telemetry reading for a reactor"""
        return self.db.query(Telemetry).filter(
            Telemetry.reactor_id == reactor_id
        ).order_by(desc(Telemetry.timestamp)).first()

    def create(self, telemetry_data: Dict[str, Any]) -> Telemetry:
        """
        Create a new telemetry record
        
        Args:
            telemetry_data: Dictionary containing telemetry information
        """
        telemetry = Telemetry.create_from_dict(telemetry_data)
        self.db.add(telemetry)
        self.db.commit()
        self.db.refresh(telemetry)
        
        logger.debug("Telemetry record created", 
                    reactor_id=telemetry.reactor_id, 
                    timestamp=telemetry.timestamp)
        return telemetry

    def create_batch(self, telemetry_records: List[Dict[str, Any]]) -> List[Telemetry]:
        """
        Create multiple telemetry records in batch
        
        Args:
            telemetry_records: List of telemetry dictionaries
        """
        telemetry_objects = [Telemetry.create_from_dict(data) for data in telemetry_records]
        self.db.add_all(telemetry_objects)
        self.db.commit()
        
        logger.info("Batch telemetry created", count=len(telemetry_objects))
        return telemetry_objects

    def get_aggregated_data(
        self,
        reactor_id: int,
        start_time: datetime,
        end_time: datetime,
        interval_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Get aggregated telemetry data over time intervals
        
        Args:
            reactor_id: ID of the reactor
            start_time: Start of time range
            end_time: End of time range
            interval_minutes: Aggregation interval in minutes
        """
        # Create time buckets for aggregation
        interval = f"{interval_minutes} minutes"
        
        query = self.db.query(
            func.date_trunc('hour', Telemetry.timestamp).label('time_bucket'),
            func.avg(Telemetry.neutron_flux).label('avg_neutron_flux'),
            func.avg(Telemetry.core_temperature).label('avg_core_temperature'),
            func.avg(Telemetry.pressure).label('avg_pressure'),
            func.avg(Telemetry.vibration).label('avg_vibration'),
            func.avg(Telemetry.tritium_level).label('avg_tritium_level'),
            func.min(Telemetry.neutron_flux).label('min_neutron_flux'),
            func.max(Telemetry.neutron_flux).label('max_neutron_flux'),
            func.count(Telemetry.id).label('sample_count')
        ).filter(
            and_(
                Telemetry.reactor_id == reactor_id,
                Telemetry.timestamp >= start_time,
                Telemetry.timestamp <= end_time
            )
        ).group_by('time_bucket').order_by('time_bucket')
        
        results = query.all()
        
        return [
            {
                "timestamp": result.time_bucket.isoformat(),
                "avg_neutron_flux": result.avg_neutron_flux,
                "avg_core_temperature": result.avg_core_temperature,
                "avg_pressure": result.avg_pressure,
                "avg_vibration": result.avg_vibration,
                "avg_tritium_level": result.avg_tritium_level,
                "min_neutron_flux": result.min_neutron_flux,
                "max_neutron_flux": result.max_neutron_flux,
                "sample_count": result.sample_count
            }
            for result in results
        ]

    def get_anomalies(
        self,
        reactor_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Telemetry]:
        """
        Get telemetry readings that are outside normal ranges
        
        Args:
            reactor_id: ID of the reactor
            start_time: Start of time range
            end_time: End of time range
        """
        query = self.db.query(Telemetry).filter(Telemetry.reactor_id == reactor_id)
        
        if start_time:
            query = query.filter(Telemetry.timestamp >= start_time)
        if end_time:
            query = query.filter(Telemetry.timestamp <= end_time)
        
        # Filter for readings outside normal ranges
        anomaly_conditions = or_(
            Telemetry.neutron_flux < 1.0e13,
            Telemetry.neutron_flux > 1.5e13,
            Telemetry.core_temperature < 260,
            Telemetry.core_temperature > 320,
            Telemetry.pressure < 10,
            Telemetry.pressure > 15,
            Telemetry.vibration > 5,
            Telemetry.tritium_level > 1000
        )
        
        return query.filter(anomaly_conditions).order_by(desc(Telemetry.timestamp)).all()

    def calculate_reactor_health(self, reactor_id: int, hours_back: int = 24) -> float:
        """
        Calculate reactor health score based on recent telemetry
        
        Args:
            reactor_id: ID of the reactor
            hours_back: Number of hours to look back
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        recent_telemetry = self.db.query(Telemetry).filter(
            and_(
                Telemetry.reactor_id == reactor_id,
                Telemetry.timestamp >= cutoff_time
            )
        ).all()
        
        if not recent_telemetry:
            return 100.0  # No data means assume healthy
        
        total_score = 0.0
        for reading in recent_telemetry:
            total_score += reading.calculate_health_contribution()
        
        return total_score / len(recent_telemetry)

    def delete_old_data(self, days_to_keep: int = 30) -> int:
        """
        Delete telemetry data older than specified days
        
        Args:
            days_to_keep: Number of days of data to retain
            
        Returns:
            Number of records deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        deleted_count = self.db.query(Telemetry).filter(
            Telemetry.timestamp < cutoff_date
        ).delete()
        
        self.db.commit()
        
        logger.info("Old telemetry data cleaned up", 
                   deleted_count=deleted_count, 
                   cutoff_date=cutoff_date.isoformat())
        
        return deleted_count
