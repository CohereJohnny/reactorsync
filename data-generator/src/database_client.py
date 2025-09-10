"""
Database Client for Data Generator

Handles database operations for the synthetic data generation service.
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime
import asyncpg
import json
import structlog

logger = structlog.get_logger()

class DatabaseClient:
    """Async database client for data generator operations"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection_pool = None
    
    async def initialize(self):
        """Initialize database connection pool"""
        try:
            self.connection_pool = await asyncpg.create_pool(
                self.database_url,
                min_size=2,
                max_size=10,
                command_timeout=30
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error("Failed to initialize database pool", error=str(e))
            raise
    
    async def health_check(self) -> Dict[str, bool]:
        """Check database connectivity"""
        try:
            if not self.connection_pool:
                await self.initialize()
            
            async with self.connection_pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                return {"healthy": True, "test_query": result == 1}
                
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def get_reactors(self) -> List[Dict]:
        """Get list of reactors from database"""
        try:
            if not self.connection_pool:
                await self.initialize()
            
            async with self.connection_pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT id, name, type, latitude, longitude, status, health_score
                    FROM reactors
                    ORDER BY id
                """)
                
                return [
                    {
                        "id": row["id"],
                        "name": row["name"],
                        "type": row["type"],
                        "latitude": row["latitude"],
                        "longitude": row["longitude"],
                        "status": row["status"],
                        "health_score": row["health_score"]
                    }
                    for row in rows
                ]
                
        except Exception as e:
            logger.error("Error loading reactors", error=str(e))
            raise
    
    async def insert_telemetry_batch(self, readings: List[Dict]) -> int:
        """
        Insert batch of telemetry readings into database
        
        Args:
            readings: List of telemetry dictionaries
            
        Returns:
            Number of successfully inserted readings
        """
        try:
            if not self.connection_pool:
                await self.initialize()
            
            async with self.connection_pool.acquire() as conn:
                # Prepare data for batch insert
                values = [
                    (
                        reading["reactor_id"],
                        reading["timestamp"],
                        reading["neutron_flux"],
                        reading["core_temperature"],
                        reading["pressure"],
                        reading["vibration"],
                        reading["tritium_level"]
                    )
                    for reading in readings
                ]
                
                # Batch insert
                result = await conn.executemany("""
                    INSERT INTO telemetry (
                        reactor_id, timestamp, neutron_flux, core_temperature,
                        pressure, vibration, tritium_level
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, values)
                
                logger.debug("Telemetry batch inserted", count=len(values))
                return len(values)
                
        except Exception as e:
            logger.error("Error inserting telemetry batch", error=str(e))
            return 0
    
    async def update_reactor_health(self, reactor_id: int, health_score: float):
        """Update reactor health score and status"""
        try:
            if not self.connection_pool:
                await self.initialize()
            
            # Determine status based on health score
            if health_score >= 90:
                status = "healthy"
            elif health_score >= 70:
                status = "warning"
            else:
                status = "unhealthy"
            
            async with self.connection_pool.acquire() as conn:
                await conn.execute("""
                    UPDATE reactors 
                    SET health_score = $1, status = $2, updated_at = NOW()
                    WHERE id = $3
                """, health_score, status, reactor_id)
                
                logger.debug(
                    "Reactor health updated",
                    reactor_id=reactor_id,
                    health_score=health_score,
                    status=status
                )
                
        except Exception as e:
            logger.error(
                "Error updating reactor health",
                reactor_id=reactor_id,
                error=str(e)
            )
    
    async def create_fault(self, fault_data: Dict):
        """Create a fault record in the database"""
        try:
            if not self.connection_pool:
                await self.initialize()
            
            async with self.connection_pool.acquire() as conn:
                # Check if similar fault already exists (avoid duplicates)
                existing = await conn.fetchrow("""
                    SELECT id FROM faults 
                    WHERE reactor_id = $1 
                    AND fault_type = $2 
                    AND resolved = false
                    AND timestamp > NOW() - INTERVAL '1 hour'
                """, fault_data["reactor_id"], fault_data["fault_type"])
                
                if existing:
                    logger.debug(
                        "Similar fault already exists, skipping",
                        reactor_id=fault_data["reactor_id"],
                        fault_type=fault_data["fault_type"]
                    )
                    return
                
                # Insert new fault
                await conn.execute("""
                    INSERT INTO faults (
                        reactor_id, fault_type, severity, description, timestamp
                    ) VALUES ($1, $2, $3, $4, $5)
                """,
                    fault_data["reactor_id"],
                    fault_data["fault_type"],
                    fault_data["severity"],
                    fault_data["description"],
                    fault_data["timestamp"]
                )
                
                logger.warning(
                    "Fault created",
                    reactor_id=fault_data["reactor_id"],
                    fault_type=fault_data["fault_type"],
                    severity=fault_data["severity"]
                )
                
        except Exception as e:
            logger.error("Error creating fault", error=str(e))
    
    async def get_statistics(self) -> Dict:
        """Get database statistics for monitoring"""
        try:
            if not self.connection_pool:
                await self.initialize()
            
            async with self.connection_pool.acquire() as conn:
                # Get telemetry count
                telemetry_count = await conn.fetchval("SELECT COUNT(*) FROM telemetry")
                
                # Get recent telemetry (last hour)
                recent_count = await conn.fetchval("""
                    SELECT COUNT(*) FROM telemetry 
                    WHERE created_at > NOW() - INTERVAL '1 hour'
                """)
                
                # Get fault counts
                active_faults = await conn.fetchval("""
                    SELECT COUNT(*) FROM faults WHERE resolved = false
                """)
                
                return {
                    "total_telemetry_records": telemetry_count,
                    "recent_telemetry_records": recent_count,
                    "active_faults": active_faults,
                    "connection_pool_size": self.connection_pool._queue.qsize() if self.connection_pool else 0
                }
                
        except Exception as e:
            logger.error("Error getting statistics", error=str(e))
            return {}
    
    async def cleanup_old_data(self, days_to_keep: int = 7):
        """Clean up old telemetry data to manage storage"""
        try:
            if not self.connection_pool:
                await self.initialize()
            
            async with self.connection_pool.acquire() as conn:
                deleted_count = await conn.fetchval("""
                    DELETE FROM telemetry 
                    WHERE created_at < NOW() - INTERVAL '%s days'
                    RETURNING COUNT(*)
                """, days_to_keep)
                
                if deleted_count and deleted_count > 0:
                    logger.info("Old telemetry data cleaned up", deleted_count=deleted_count)
                
                return deleted_count or 0
                
        except Exception as e:
            logger.error("Error cleaning up old data", error=str(e))
            return 0
    
    async def close(self):
        """Close database connections"""
        try:
            if self.connection_pool:
                await self.connection_pool.close()
                logger.info("Database connection pool closed")
        except Exception as e:
            logger.error("Error closing database pool", error=str(e))
