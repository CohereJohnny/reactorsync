"""
Kafka Producer for ReactorSync Telemetry Data

Handles streaming telemetry data to Kafka topics for real-time processing.
"""

import json
import time
from typing import Dict, List, Optional
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError
import structlog

logger = structlog.get_logger()

class TelemetryProducer:
    """Kafka producer for telemetry data streaming"""
    
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic_prefix: str = "reactorsync"
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic_prefix = topic_prefix
        self.producer = None
        self._initialize_producer()
    
    def _initialize_producer(self):
        """Initialize Kafka producer with proper configuration"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                key_serializer=lambda k: str(k).encode('utf-8'),
                acks='all',  # Wait for all replicas to acknowledge
                retries=3,
                batch_size=16384,
                linger_ms=10,  # Small delay to batch messages
                buffer_memory=33554432,
                max_block_ms=60000,
                request_timeout_ms=30000
            )
            logger.info("Kafka producer initialized", servers=self.bootstrap_servers)
        except Exception as e:
            logger.error("Failed to initialize Kafka producer", error=str(e))
            raise
    
    def get_telemetry_topic(self) -> str:
        """Get the telemetry topic name"""
        return f"{self.topic_prefix}.telemetry"
    
    def get_alerts_topic(self) -> str:
        """Get the alerts topic name"""
        return f"{self.topic_prefix}.alerts"
    
    def send_telemetry(self, telemetry_data: Dict) -> bool:
        """
        Send telemetry data to Kafka
        
        Args:
            telemetry_data: Dictionary containing telemetry information
        """
        try:
            if not self.producer:
                self._initialize_producer()
            
            topic = self.get_telemetry_topic()
            key = str(telemetry_data.get("reactor_id"))
            
            # Add metadata
            message = {
                **telemetry_data,
                "producer_timestamp": datetime.utcnow().isoformat(),
                "source": "synthetic_generator"
            }
            
            # Send message
            future = self.producer.send(topic, key=key, value=message)
            
            # Wait for confirmation (with timeout)
            record_metadata = future.get(timeout=10)
            
            logger.debug(
                "Telemetry sent to Kafka",
                reactor_id=telemetry_data.get("reactor_id"),
                topic=record_metadata.topic,
                partition=record_metadata.partition,
                offset=record_metadata.offset
            )
            
            return True
            
        except KafkaError as e:
            logger.error("Kafka error sending telemetry", error=str(e))
            return False
        except Exception as e:
            logger.error("Unexpected error sending telemetry", error=str(e))
            return False
    
    def send_alert(self, alert_data: Dict) -> bool:
        """
        Send alert/fault data to Kafka
        
        Args:
            alert_data: Dictionary containing alert information
        """
        try:
            if not self.producer:
                self._initialize_producer()
            
            topic = self.get_alerts_topic()
            key = str(alert_data.get("reactor_id"))
            
            # Add metadata
            message = {
                **alert_data,
                "producer_timestamp": datetime.utcnow().isoformat(),
                "source": "anomaly_detector"
            }
            
            # Send message
            future = self.producer.send(topic, key=key, value=message)
            record_metadata = future.get(timeout=10)
            
            logger.warning(
                "Alert sent to Kafka",
                reactor_id=alert_data.get("reactor_id"),
                alert_type=alert_data.get("fault_type"),
                severity=alert_data.get("severity"),
                topic=record_metadata.topic,
                partition=record_metadata.partition
            )
            
            return True
            
        except Exception as e:
            logger.error("Error sending alert", error=str(e))
            return False
    
    def send_batch_telemetry(self, telemetry_batch: List[Dict]) -> int:
        """
        Send multiple telemetry readings in batch
        
        Args:
            telemetry_batch: List of telemetry dictionaries
            
        Returns:
            Number of successfully sent messages
        """
        success_count = 0
        
        for telemetry in telemetry_batch:
            if self.send_telemetry(telemetry):
                success_count += 1
        
        # Flush producer to ensure all messages are sent
        try:
            self.producer.flush(timeout=30)
        except Exception as e:
            logger.error("Error flushing producer", error=str(e))
        
        logger.info(
            "Batch telemetry sent",
            total=len(telemetry_batch),
            successful=success_count,
            failed=len(telemetry_batch) - success_count
        )
        
        return success_count
    
    def health_check(self) -> Dict[str, bool]:
        """Check producer health and Kafka connectivity"""
        try:
            if not self.producer:
                return {"healthy": False, "error": "Producer not initialized"}
            
            # Try to get topic metadata (tests connectivity)
            metadata = self.producer.list_topics(timeout=5)
            
            return {
                "healthy": True,
                "topics_available": len(metadata.topics),
                "brokers_available": len(metadata.brokers)
            }
            
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    def close(self):
        """Close the producer and clean up resources"""
        if self.producer:
            try:
                self.producer.flush(timeout=10)
                self.producer.close(timeout=10)
                logger.info("Kafka producer closed")
            except Exception as e:
                logger.error("Error closing producer", error=str(e))
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
