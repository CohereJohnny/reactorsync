"""
Main Data Generator Service

Coordinates synthetic telemetry data generation and streaming for ReactorSync.
"""

import asyncio
import time
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from nuclear_physics import TelemetryGenerator, AnomalyGenerator
from kafka_producer import TelemetryProducer
from database_client import DatabaseClient
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

class ReactorDataGenerator:
    """Main service for generating and streaming reactor telemetry data"""
    
    def __init__(
        self,
        kafka_servers: str = "localhost:9092",
        database_url: str = "postgresql://reactorsync:reactorsync@localhost:5432/reactorsync",
        generation_interval: int = 60  # seconds
    ):
        self.kafka_servers = kafka_servers
        self.database_url = database_url
        self.generation_interval = generation_interval
        
        # Initialize components
        self.telemetry_generator = TelemetryGenerator()
        self.kafka_producer = TelemetryProducer(kafka_servers)
        self.database_client = DatabaseClient(database_url)
        
        # State tracking
        self.is_running = False
        self.reactors = []
        self.generation_stats = {
            "total_readings": 0,
            "successful_kafka": 0,
            "successful_db": 0,
            "errors": 0,
            "start_time": None
        }
    
    async def initialize(self):
        """Initialize the data generator service"""
        try:
            logger.info("Initializing ReactorSync Data Generator")
            
            # Load reactor list from database
            await self.load_reactors()
            
            # Verify Kafka connectivity
            kafka_health = self.kafka_producer.health_check()
            if not kafka_health["healthy"]:
                raise Exception(f"Kafka not healthy: {kafka_health.get('error')}")
            
            # Verify database connectivity
            db_health = await self.database_client.health_check()
            if not db_health["healthy"]:
                raise Exception(f"Database not healthy: {db_health.get('error')}")
            
            logger.info(
                "Data generator initialized",
                reactor_count=len(self.reactors),
                kafka_brokers=kafka_health.get("brokers_available"),
                generation_interval=self.generation_interval
            )
            
        except Exception as e:
            logger.error("Failed to initialize data generator", error=str(e))
            raise
    
    async def load_reactors(self):
        """Load reactor list from database"""
        try:
            self.reactors = await self.database_client.get_reactors()
            logger.info("Reactors loaded", count=len(self.reactors))
        except Exception as e:
            logger.error("Failed to load reactors", error=str(e))
            raise
    
    async def generate_telemetry_cycle(self):
        """Generate one cycle of telemetry data for all reactors"""
        timestamp = datetime.utcnow()
        readings = []
        
        for reactor in self.reactors:
            try:
                # Generate telemetry reading
                reading = self.telemetry_generator.generate_reading(
                    reactor_id=reactor["id"],
                    reactor_type=reactor["type"],
                    timestamp=timestamp
                )
                
                readings.append(reading)
                self.generation_stats["total_readings"] += 1
                
            except Exception as e:
                logger.error(
                    "Error generating telemetry",
                    reactor_id=reactor["id"],
                    error=str(e)
                )
                self.generation_stats["errors"] += 1
        
        # Send to Kafka
        await self.send_to_kafka(readings)
        
        # Store in database
        await self.store_in_database(readings)
        
        # Update health scores
        await self.update_health_scores(readings)
        
        logger.info(
            "Telemetry cycle complete",
            readings_generated=len(readings),
            timestamp=timestamp.isoformat()
        )
    
    async def send_to_kafka(self, readings: List[Dict]):
        """Send telemetry readings to Kafka"""
        try:
            success_count = self.kafka_producer.send_batch_telemetry(readings)
            self.generation_stats["successful_kafka"] += success_count
            
            if success_count < len(readings):
                logger.warning(
                    "Some Kafka messages failed",
                    successful=success_count,
                    total=len(readings)
                )
                
        except Exception as e:
            logger.error("Error sending to Kafka", error=str(e))
            self.generation_stats["errors"] += len(readings)
    
    async def store_in_database(self, readings: List[Dict]):
        """Store telemetry readings in database"""
        try:
            success_count = await self.database_client.insert_telemetry_batch(readings)
            self.generation_stats["successful_db"] += success_count
            
            if success_count < len(readings):
                logger.warning(
                    "Some database inserts failed",
                    successful=success_count,
                    total=len(readings)
                )
                
        except Exception as e:
            logger.error("Error storing in database", error=str(e))
            self.generation_stats["errors"] += len(readings)
    
    async def update_health_scores(self, readings: List[Dict]):
        """Update reactor health scores based on telemetry"""
        try:
            for reading in readings:
                # Calculate health score
                health_score = self.telemetry_generator.physics_engine.calculate_health_score(reading)
                
                # Update in database
                await self.database_client.update_reactor_health(
                    reading["reactor_id"],
                    health_score
                )
                
                # Check for anomalies and generate faults
                await self.check_for_faults(reading, health_score)
                
        except Exception as e:
            logger.error("Error updating health scores", error=str(e))
    
    async def check_for_faults(self, reading: Dict, health_score: float):
        """Check telemetry for faults and create fault records"""
        try:
            # Check if health score indicates a problem
            if health_score < 90:
                severity = "red" if health_score < 70 else "yellow"
                
                # Determine fault type based on telemetry
                fault_type = self.determine_fault_type(reading)
                
                if fault_type:
                    fault_data = {
                        "reactor_id": reading["reactor_id"],
                        "fault_type": fault_type,
                        "severity": severity,
                        "description": f"Automated detection: {fault_type} (health score: {health_score:.1f})",
                        "timestamp": reading["timestamp"]
                    }
                    
                    # Send alert to Kafka
                    self.kafka_producer.send_alert(fault_data)
                    
                    # Store fault in database
                    await self.database_client.create_fault(fault_data)
                    
        except Exception as e:
            logger.error("Error checking for faults", error=str(e))
    
    def determine_fault_type(self, reading: Dict) -> Optional[str]:
        """Determine fault type based on telemetry values"""
        # Check each metric against normal ranges
        if reading.get("core_temperature", 0) > 320:
            return "temperature_spike"
        elif reading.get("pressure", 0) < 10:
            return "pressure_drop"
        elif reading.get("vibration", 0) > 5:
            return "vibration_high"
        elif reading.get("neutron_flux", 0) > 1.5e13:
            return "flux_instability"
        elif reading.get("tritium_level", 0) > 1000:
            return "tritium_high"
        
        return None
    
    async def inject_anomaly(
        self,
        reactor_id: int,
        anomaly_type: str,
        severity: str = "yellow",
        duration_minutes: int = 30
    ):
        """
        Inject an anomaly for demo purposes
        
        Args:
            reactor_id: Target reactor ID
            anomaly_type: Type of anomaly to inject
            severity: Severity level (yellow/red)
            duration_minutes: Duration of the anomaly
        """
        try:
            self.telemetry_generator.inject_anomaly(
                reactor_id=reactor_id,
                anomaly_type=anomaly_type,
                severity=severity,
                duration_minutes=duration_minutes
            )
            
            logger.warning(
                "Anomaly injected",
                reactor_id=reactor_id,
                anomaly_type=anomaly_type,
                severity=severity,
                duration_minutes=duration_minutes
            )
            
            return True
            
        except Exception as e:
            logger.error("Error injecting anomaly", error=str(e))
            return False
    
    async def clear_anomaly(self, reactor_id: int):
        """Clear any active anomaly for a reactor"""
        try:
            self.telemetry_generator.clear_anomaly(reactor_id)
            logger.info("Anomaly cleared", reactor_id=reactor_id)
            return True
        except Exception as e:
            logger.error("Error clearing anomaly", error=str(e))
            return False
    
    async def run(self):
        """Main data generation loop"""
        try:
            await self.initialize()
            
            self.is_running = True
            self.generation_stats["start_time"] = datetime.utcnow()
            
            logger.info("Starting data generation loop")
            
            while self.is_running:
                cycle_start = time.time()
                
                # Generate telemetry for all reactors
                await self.generate_telemetry_cycle()
                
                # Update anomaly states
                self.telemetry_generator.update_anomalies()
                
                # Calculate sleep time to maintain interval
                cycle_duration = time.time() - cycle_start
                sleep_time = max(0, self.generation_interval - cycle_duration)
                
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                else:
                    logger.warning(
                        "Generation cycle took longer than interval",
                        cycle_duration=cycle_duration,
                        interval=self.generation_interval
                    )
                
        except Exception as e:
            logger.error("Data generation loop failed", error=str(e))
            raise
        finally:
            await self.cleanup()
    
    async def stop(self):
        """Stop the data generation loop"""
        self.is_running = False
        logger.info("Data generation stop requested")
    
    async def cleanup(self):
        """Clean up resources"""
        try:
            if self.kafka_producer:
                self.kafka_producer.close()
            
            if self.database_client:
                await self.database_client.close()
            
            logger.info("Data generator cleanup completed")
            
        except Exception as e:
            logger.error("Error during cleanup", error=str(e))
    
    def get_statistics(self) -> Dict:
        """Get data generation statistics"""
        runtime = None
        if self.generation_stats["start_time"]:
            runtime = (datetime.utcnow() - self.generation_stats["start_time"]).total_seconds()
        
        return {
            **self.generation_stats,
            "runtime_seconds": runtime,
            "reactors_monitored": len(self.reactors),
            "active_anomalies": self.telemetry_generator.get_active_anomalies(),
            "is_running": self.is_running
        }

# Main entry point
async def main():
    """Main entry point for the data generator service"""
    # Get configuration from environment
    kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    database_url = os.getenv("DATABASE_URL", "postgresql://reactorsync:reactorsync@localhost:5432/reactorsync")
    generation_interval = int(os.getenv("GENERATION_INTERVAL", "60"))
    
    generator = ReactorDataGenerator(
        kafka_servers=kafka_servers,
        database_url=database_url,
        generation_interval=generation_interval
    )
    
    try:
        await generator.run()
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
        await generator.stop()
    except Exception as e:
        logger.error("Data generator failed", error=str(e))
        raise

if __name__ == "__main__":
    asyncio.run(main())
