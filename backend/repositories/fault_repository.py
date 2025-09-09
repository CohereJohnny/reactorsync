"""
Fault Repository - Data access layer for fault operations
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from models.fault import Fault, FaultSeverity
from models.reactor import Reactor
import structlog

logger = structlog.get_logger()

class FaultRepository:
    """Repository for fault data access operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        reactor_id: Optional[int] = None,
        severity: Optional[FaultSeverity] = None,
        resolved: Optional[bool] = None,
        sort_by: str = "timestamp",
        sort_order: str = "desc"
    ) -> List[Fault]:
        """
        Get all faults with optional filtering and pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            reactor_id: Filter by reactor ID
            severity: Filter by fault severity
            resolved: Filter by resolution status
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
        """
        query = self.db.query(Fault)
        
        # Apply filters
        if reactor_id:
            query = query.filter(Fault.reactor_id == reactor_id)
        
        if severity:
            query = query.filter(Fault.severity == severity)
        
        if resolved is not None:
            query = query.filter(Fault.resolved == resolved)
        
        # Apply sorting
        sort_column = getattr(Fault, sort_by, Fault.timestamp)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        return query.offset(skip).limit(limit).all()

    def get_by_id(self, fault_id: int) -> Optional[Fault]:
        """Get fault by ID"""
        return self.db.query(Fault).filter(Fault.id == fault_id).first()

    def create(self, fault_data: Dict[str, Any]) -> Fault:
        """
        Create a new fault record
        
        Args:
            fault_data: Dictionary containing fault information
        """
        fault = Fault.create_from_dict(fault_data)
        self.db.add(fault)
        self.db.commit()
        self.db.refresh(fault)
        
        logger.warning("Fault created", 
                      fault_id=fault.id,
                      reactor_id=fault.reactor_id,
                      fault_type=fault.fault_type,
                      severity=fault.severity.value)
        return fault

    def resolve_fault(self, fault_id: int) -> Optional[Fault]:
        """
        Mark a fault as resolved
        
        Args:
            fault_id: ID of fault to resolve
        """
        fault = self.get_by_id(fault_id)
        if not fault:
            return None
        
        fault.resolve()
        self.db.commit()
        self.db.refresh(fault)
        
        logger.info("Fault resolved", 
                   fault_id=fault_id,
                   fault_type=fault.fault_type,
                   duration_hours=fault.duration_hours)
        return fault

    def get_active_faults(self, reactor_id: Optional[int] = None) -> List[Fault]:
        """
        Get all unresolved faults
        
        Args:
            reactor_id: Optional filter by reactor ID
        """
        query = self.db.query(Fault).filter(Fault.resolved == False)
        
        if reactor_id:
            query = query.filter(Fault.reactor_id == reactor_id)
        
        return query.order_by(desc(Fault.timestamp)).all()

    def get_critical_faults(self, reactor_id: Optional[int] = None) -> List[Fault]:
        """
        Get all critical (red severity, unresolved) faults
        
        Args:
            reactor_id: Optional filter by reactor ID
        """
        query = self.db.query(Fault).filter(
            and_(
                Fault.severity == FaultSeverity.red,
                Fault.resolved == False
            )
        )
        
        if reactor_id:
            query = query.filter(Fault.reactor_id == reactor_id)
        
        return query.order_by(desc(Fault.timestamp)).all()

    def get_recent_faults(
        self,
        reactor_id: Optional[int] = None,
        hours_back: int = 24
    ) -> List[Fault]:
        """
        Get faults from recent time period
        
        Args:
            reactor_id: Optional filter by reactor ID
            hours_back: Number of hours to look back
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        query = self.db.query(Fault).filter(Fault.timestamp >= cutoff_time)
        
        if reactor_id:
            query = query.filter(Fault.reactor_id == reactor_id)
        
        return query.order_by(desc(Fault.timestamp)).all()

    def get_fault_statistics(
        self,
        reactor_id: Optional[int] = None,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get fault statistics for analysis
        
        Args:
            reactor_id: Optional filter by reactor ID
            days_back: Number of days to analyze
        """
        cutoff_time = datetime.utcnow() - timedelta(days=days_back)
        
        query = self.db.query(Fault).filter(Fault.timestamp >= cutoff_time)
        
        if reactor_id:
            query = query.filter(Fault.reactor_id == reactor_id)
        
        total_faults = query.count()
        resolved_faults = query.filter(Fault.resolved == True).count()
        critical_faults = query.filter(Fault.severity == FaultSeverity.red).count()
        
        # Get fault type distribution
        fault_types = self.db.query(
            Fault.fault_type,
            func.count(Fault.id).label('count')
        ).filter(Fault.timestamp >= cutoff_time)
        
        if reactor_id:
            fault_types = fault_types.filter(Fault.reactor_id == reactor_id)
        
        fault_type_stats = {
            result.fault_type: result.count 
            for result in fault_types.group_by(Fault.fault_type).all()
        }
        
        # Calculate average resolution time
        avg_resolution_query = self.db.query(
            func.avg(
                func.extract('epoch', Fault.resolved_at - Fault.timestamp) / 3600
            ).label('avg_hours')
        ).filter(
            and_(
                Fault.resolved == True,
                Fault.timestamp >= cutoff_time
            )
        )
        
        if reactor_id:
            avg_resolution_query = avg_resolution_query.filter(Fault.reactor_id == reactor_id)
        
        avg_resolution_hours = avg_resolution_query.scalar() or 0.0
        
        return {
            "total_faults": total_faults,
            "resolved_faults": resolved_faults,
            "active_faults": total_faults - resolved_faults,
            "critical_faults": critical_faults,
            "resolution_rate": round((resolved_faults / total_faults * 100) if total_faults > 0 else 0, 1),
            "avg_resolution_hours": round(avg_resolution_hours, 2),
            "fault_types": fault_type_stats,
            "analysis_period_days": days_back
        }

    def get_reactor_fault_summary(self, reactor_id: int) -> Dict[str, Any]:
        """
        Get comprehensive fault summary for a reactor
        
        Args:
            reactor_id: ID of the reactor
        """
        active_faults = self.get_active_faults(reactor_id)
        critical_faults = self.get_critical_faults(reactor_id)
        recent_faults = self.get_recent_faults(reactor_id, hours_back=24)
        
        return {
            "reactor_id": reactor_id,
            "active_fault_count": len(active_faults),
            "critical_fault_count": len(critical_faults),
            "recent_fault_count": len(recent_faults),
            "active_faults": [fault.to_dict() for fault in active_faults[:5]],  # Latest 5
            "critical_faults": [fault.to_dict() for fault in critical_faults],
            "has_critical_issues": len(critical_faults) > 0
        }

    def cleanup_old_resolved_faults(self, days_to_keep: int = 90) -> int:
        """
        Clean up old resolved faults
        
        Args:
            days_to_keep: Number of days to keep resolved faults
            
        Returns:
            Number of faults deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        deleted_count = self.db.query(Fault).filter(
            and_(
                Fault.resolved == True,
                Fault.resolved_at < cutoff_date
            )
        ).delete()
        
        self.db.commit()
        
        logger.info("Old resolved faults cleaned up", 
                   deleted_count=deleted_count,
                   cutoff_date=cutoff_date.isoformat())
        
        return deleted_count
