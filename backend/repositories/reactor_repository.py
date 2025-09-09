"""
Reactor Repository - Data access layer for reactor operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from models.reactor import Reactor, ReactorStatus, ReactorType
from models.telemetry import Telemetry
from models.fault import Fault
import structlog

logger = structlog.get_logger()

class ReactorRepository:
    """Repository for reactor data access operations"""
    
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status_filter: Optional[ReactorStatus] = None,
        reactor_type_filter: Optional[ReactorType] = None,
        sort_by: str = "name",
        sort_order: str = "asc"
    ) -> List[Reactor]:
        """
        Get all reactors with optional filtering and pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            status_filter: Filter by reactor status
            reactor_type_filter: Filter by reactor type
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)
        """
        query = self.db.query(Reactor)
        
        # Apply filters
        if status_filter:
            query = query.filter(Reactor.status == status_filter)
        
        if reactor_type_filter:
            query = query.filter(Reactor.type == reactor_type_filter)
        
        # Apply sorting
        sort_column = getattr(Reactor, sort_by, Reactor.name)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        return query.offset(skip).limit(limit).all()

    def get_by_id(self, reactor_id: int) -> Optional[Reactor]:
        """Get reactor by ID"""
        return self.db.query(Reactor).filter(Reactor.id == reactor_id).first()

    def get_by_name(self, name: str) -> Optional[Reactor]:
        """Get reactor by name"""
        return self.db.query(Reactor).filter(Reactor.name == name).first()

    def create(self, reactor_data: Dict[str, Any]) -> Reactor:
        """
        Create a new reactor
        
        Args:
            reactor_data: Dictionary containing reactor information
        
        Returns:
            Created reactor instance
        """
        reactor = Reactor.create_from_dict(reactor_data)
        self.db.add(reactor)
        self.db.commit()
        self.db.refresh(reactor)
        
        logger.info("Reactor created", reactor_id=reactor.id, name=reactor.name)
        return reactor

    def update(self, reactor_id: int, update_data: Dict[str, Any]) -> Optional[Reactor]:
        """
        Update reactor information
        
        Args:
            reactor_id: ID of reactor to update
            update_data: Dictionary containing fields to update
        
        Returns:
            Updated reactor instance or None if not found
        """
        reactor = self.get_by_id(reactor_id)
        if not reactor:
            return None
        
        # Update allowed fields
        allowed_fields = ['name', 'type', 'latitude', 'longitude', 'status', 'health_score']
        for field, value in update_data.items():
            if field in allowed_fields and hasattr(reactor, field):
                if field == 'type' and isinstance(value, str):
                    value = ReactorType(value)
                elif field == 'status' and isinstance(value, str):
                    value = ReactorStatus(value)
                
                setattr(reactor, field, value)
        
        self.db.commit()
        self.db.refresh(reactor)
        
        logger.info("Reactor updated", reactor_id=reactor.id, fields=list(update_data.keys()))
        return reactor

    def delete(self, reactor_id: int) -> bool:
        """
        Delete a reactor
        
        Args:
            reactor_id: ID of reactor to delete
        
        Returns:
            True if deleted, False if not found
        """
        reactor = self.get_by_id(reactor_id)
        if not reactor:
            return False
        
        self.db.delete(reactor)
        self.db.commit()
        
        logger.info("Reactor deleted", reactor_id=reactor_id)
        return True

    def search(self, search_term: str) -> List[Reactor]:
        """
        Search reactors by name or location
        
        Args:
            search_term: Term to search for
        
        Returns:
            List of matching reactors
        """
        return self.db.query(Reactor).filter(
            or_(
                Reactor.name.ilike(f"%{search_term}%"),
                Reactor.type.has_value(search_term.upper())
            )
        ).all()

    def get_by_status(self, status: ReactorStatus) -> List[Reactor]:
        """Get all reactors with specific status"""
        return self.db.query(Reactor).filter(Reactor.status == status).all()

    def get_unhealthy_reactors(self, health_threshold: float = 80.0) -> List[Reactor]:
        """Get reactors with health score below threshold"""
        return self.db.query(Reactor).filter(
            Reactor.health_score < health_threshold
        ).order_by(asc(Reactor.health_score)).all()

    def update_health_score(self, reactor_id: int, new_score: float) -> Optional[Reactor]:
        """
        Update reactor health score and status
        
        Args:
            reactor_id: ID of reactor to update
            new_score: New health score (0-100)
        
        Returns:
            Updated reactor or None if not found
        """
        reactor = self.get_by_id(reactor_id)
        if not reactor:
            return None
        
        reactor.update_health_score(new_score)
        self.db.commit()
        self.db.refresh(reactor)
        
        logger.info("Reactor health score updated", 
                   reactor_id=reactor_id, 
                   new_score=new_score, 
                   new_status=reactor.status.value)
        return reactor

    def get_statistics(self) -> Dict[str, Any]:
        """Get reactor fleet statistics"""
        total = self.db.query(Reactor).count()
        healthy = self.db.query(Reactor).filter(Reactor.status == ReactorStatus.healthy).count()
        warning = self.db.query(Reactor).filter(Reactor.status == ReactorStatus.warning).count()
        unhealthy = self.db.query(Reactor).filter(Reactor.status == ReactorStatus.unhealthy).count()
        
        avg_health = self.db.query(func.avg(Reactor.health_score)).scalar() or 0.0
        
        return {
            "total_reactors": total,
            "healthy": healthy,
            "warning": warning,
            "unhealthy": unhealthy,
            "average_health_score": round(avg_health, 2),
            "health_distribution": {
                "healthy": round((healthy / total * 100) if total > 0 else 0, 1),
                "warning": round((warning / total * 100) if total > 0 else 0, 1),
                "unhealthy": round((unhealthy / total * 100) if total > 0 else 0, 1)
            }
        }
