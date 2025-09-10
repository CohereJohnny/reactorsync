"""
Nuclear Physics Models for Synthetic Data Generation

This module contains physics-informed models for generating realistic
nuclear reactor telemetry data based on actual nuclear physics principles.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import math

@dataclass
class ReactorProfile:
    """Nuclear reactor operational profile"""
    reactor_type: str  # CANDU, SMR, PWR, BWR
    thermal_power: float  # MW
    base_neutron_flux: float  # n/cm²/s
    base_temperature: float  # °C
    base_pressure: float  # MPa
    control_rod_position: float  # 0-100%
    coolant_flow_rate: float  # kg/s

class NuclearPhysicsEngine:
    """Physics-informed nuclear reactor simulation engine"""
    
    def __init__(self):
        self.reactor_profiles = {
            "CANDU": ReactorProfile(
                reactor_type="CANDU",
                thermal_power=3100,  # MW
                base_neutron_flux=1.2e13,
                base_temperature=285,  # °C
                base_pressure=12.5,  # MPa
                control_rod_position=50.0,
                coolant_flow_rate=28000  # kg/s
            ),
            "SMR": ReactorProfile(
                reactor_type="SMR", 
                thermal_power=300,  # MW
                base_neutron_flux=0.8e13,
                base_temperature=295,  # °C
                base_pressure=11.0,  # MPa
                control_rod_position=45.0,
                coolant_flow_rate=8000  # kg/s
            )
        }
    
    def generate_neutron_flux(
        self,
        profile: ReactorProfile,
        time_step: int,
        anomaly_factor: float = 1.0
    ) -> float:
        """
        Generate realistic neutron flux based on reactor physics
        
        Args:
            profile: Reactor operational profile
            time_step: Current time step in simulation
            anomaly_factor: Multiplier for anomaly injection
        """
        # Base flux with control rod influence
        base_flux = profile.base_neutron_flux
        rod_influence = (100 - profile.control_rod_position) / 100.0
        
        # Add realistic fluctuations (±5%)
        time_variation = 0.05 * math.sin(time_step * 0.1) + 0.02 * math.sin(time_step * 0.03)
        noise = np.random.normal(0, 0.02)  # 2% random noise
        
        # Combine factors
        flux = base_flux * rod_influence * (1 + time_variation + noise) * anomaly_factor
        
        # Physical limits (reactor can't exceed critical flux)
        max_flux = profile.base_neutron_flux * 1.3
        return max(0, min(flux, max_flux))
    
    def generate_core_temperature(
        self,
        profile: ReactorProfile,
        neutron_flux: float,
        time_step: int,
        anomaly_factor: float = 1.0
    ) -> float:
        """
        Generate core temperature based on neutron flux and heat transfer
        
        Temperature correlates with neutron flux due to fission heating
        """
        # Temperature is related to power (proportional to neutron flux)
        flux_ratio = neutron_flux / profile.base_neutron_flux
        base_temp_rise = 25 * flux_ratio  # Temperature rise above coolant temp
        
        # Coolant inlet temperature (varies seasonally)
        coolant_temp = 260 + 5 * math.sin(time_step * 0.001)  # Seasonal variation
        
        # Heat transfer dynamics (thermal lag)
        thermal_lag = 0.1 * math.sin(time_step * 0.05)
        
        # Random thermal fluctuations
        thermal_noise = np.random.normal(0, 2.0)
        
        # Calculate core temperature
        core_temp = (coolant_temp + base_temp_rise + thermal_lag + thermal_noise) * anomaly_factor
        
        # Physical limits (fuel melting point ~2800°C, but operational limit much lower)
        return max(200, min(core_temp, 400))
    
    def generate_pressure(
        self,
        profile: ReactorProfile,
        temperature: float,
        time_step: int,
        anomaly_factor: float = 1.0
    ) -> float:
        """
        Generate primary circuit pressure based on temperature and pumps
        
        Pressure correlates with temperature via ideal gas law principles
        """
        # Base pressure from profile
        base_pressure = profile.base_pressure
        
        # Temperature influence (higher temp = higher pressure)
        temp_ratio = temperature / profile.base_temperature
        pressure_rise = base_pressure * 0.1 * (temp_ratio - 1)
        
        # Pump pressure variations
        pump_cycle = 0.5 * math.sin(time_step * 0.2)  # Pump cycling
        
        # Random pressure fluctuations
        pressure_noise = np.random.normal(0, 0.2)
        
        # Calculate pressure
        pressure = (base_pressure + pressure_rise + pump_cycle + pressure_noise) * anomaly_factor
        
        # Physical limits (system pressure relief valves)
        return max(8.0, min(pressure, 18.0))
    
    def generate_vibration(
        self,
        profile: ReactorProfile,
        time_step: int,
        anomaly_factor: float = 1.0
    ) -> float:
        """
        Generate vibration levels from pumps, turbines, and mechanical systems
        """
        # Base vibration from pumps and turbines
        base_vibration = 1.8 + 0.3 * (profile.thermal_power / 3100)  # Scale with power
        
        # Mechanical harmonics
        pump_vibration = 0.3 * math.sin(time_step * 0.8)  # Pump frequency
        turbine_vibration = 0.2 * math.sin(time_step * 1.2)  # Turbine frequency
        
        # Random mechanical noise
        mechanical_noise = np.random.normal(0, 0.1)
        
        # Calculate total vibration
        vibration = (base_vibration + pump_vibration + turbine_vibration + mechanical_noise) * anomaly_factor
        
        # Physical limits (excessive vibration would trigger shutdowns)
        return max(0, min(vibration, 15.0))
    
    def generate_tritium_level(
        self,
        profile: ReactorProfile,
        neutron_flux: float,
        time_step: int,
        anomaly_factor: float = 1.0
    ) -> float:
        """
        Generate tritium levels based on neutron activation of heavy water
        
        Tritium production correlates with neutron flux in heavy water reactors
        """
        # Tritium production rate (proportional to neutron flux)
        flux_ratio = neutron_flux / profile.base_neutron_flux
        base_tritium = 450 * flux_ratio  # pCi/L
        
        # Tritium decay (half-life ~12.3 years, negligible over hours)
        # But purification system removes tritium
        purification_cycle = -50 * math.sin(time_step * 0.05)  # Purification effect
        
        # Random variations
        tritium_noise = np.random.normal(0, 25)
        
        # Calculate tritium level
        tritium = (base_tritium + purification_cycle + tritium_noise) * anomaly_factor
        
        # Physical limits (regulatory limits and measurement ranges)
        return max(0, min(tritium, 2000))
    
    def generate_telemetry_reading(
        self,
        reactor_id: int,
        reactor_type: str,
        timestamp: datetime,
        time_step: int,
        anomalies: Optional[Dict[str, float]] = None
    ) -> Dict[str, float]:
        """
        Generate a complete telemetry reading for a reactor
        
        Args:
            reactor_id: Reactor identifier
            reactor_type: Type of reactor (CANDU, SMR, etc.)
            timestamp: Timestamp for the reading
            time_step: Current simulation time step
            anomalies: Optional anomaly factors for each metric
        """
        profile = self.reactor_profiles.get(reactor_type, self.reactor_profiles["CANDU"])
        anomalies = anomalies or {}
        
        # Generate correlated telemetry data
        neutron_flux = self.generate_neutron_flux(
            profile, time_step, anomalies.get("neutron_flux", 1.0)
        )
        
        core_temperature = self.generate_core_temperature(
            profile, neutron_flux, time_step, anomalies.get("core_temperature", 1.0)
        )
        
        pressure = self.generate_pressure(
            profile, core_temperature, time_step, anomalies.get("pressure", 1.0)
        )
        
        vibration = self.generate_vibration(
            profile, time_step, anomalies.get("vibration", 1.0)
        )
        
        tritium_level = self.generate_tritium_level(
            profile, neutron_flux, time_step, anomalies.get("tritium_level", 1.0)
        )
        
        return {
            "reactor_id": reactor_id,
            "timestamp": timestamp,
            "neutron_flux": neutron_flux,
            "core_temperature": core_temperature,
            "pressure": pressure,
            "vibration": vibration,
            "tritium_level": tritium_level
        }
    
    def calculate_health_score(self, telemetry: Dict[str, float]) -> float:
        """
        Calculate reactor health score based on telemetry values
        
        Args:
            telemetry: Dictionary containing telemetry values
        """
        # Define normal ranges and weights
        normal_ranges = {
            "neutron_flux": (1.0e13, 1.5e13, 0.25),      # (min, max, weight)
            "core_temperature": (260, 320, 0.30),         # Temperature is critical
            "pressure": (10, 15, 0.20),
            "vibration": (0, 5, 0.15),
            "tritium_level": (0, 1000, 0.10)
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for metric, (min_val, max_val, weight) in normal_ranges.items():
            value = telemetry.get(metric)
            if value is not None:
                # Calculate score for this metric (0-100)
                if min_val <= value <= max_val:
                    metric_score = 100.0
                else:
                    # Deduct points based on how far outside normal range
                    if value < min_val:
                        deviation = (min_val - value) / min_val
                    else:
                        deviation = (value - max_val) / max_val
                    
                    # More severe deviations get lower scores
                    metric_score = max(0, 100 - (deviation * 100))
                
                total_score += metric_score * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 100.0

class AnomalyGenerator:
    """Generator for various types of nuclear reactor anomalies"""
    
    @staticmethod
    def temperature_spike(severity: str = "yellow") -> Dict[str, float]:
        """Generate temperature spike anomaly"""
        if severity == "red":
            return {"core_temperature": 1.15}  # 15% increase
        else:
            return {"core_temperature": 1.08}  # 8% increase
    
    @staticmethod
    def pressure_drop(severity: str = "yellow") -> Dict[str, float]:
        """Generate pressure drop anomaly"""
        if severity == "red":
            return {"pressure": 0.75}  # 25% decrease
        else:
            return {"pressure": 0.85}  # 15% decrease
    
    @staticmethod
    def vibration_increase(severity: str = "yellow") -> Dict[str, float]:
        """Generate vibration increase anomaly"""
        if severity == "red":
            return {"vibration": 2.5}  # 150% increase
        else:
            return {"vibration": 1.8}  # 80% increase
    
    @staticmethod
    def flux_instability(severity: str = "yellow") -> Dict[str, float]:
        """Generate neutron flux instability"""
        if severity == "red":
            return {"neutron_flux": 1.25}  # 25% increase
        else:
            return {"neutron_flux": 1.12}  # 12% increase
    
    @staticmethod
    def coolant_leak(severity: str = "yellow") -> Dict[str, float]:
        """Generate coolant leak (affects multiple parameters)"""
        if severity == "red":
            return {
                "pressure": 0.70,         # Pressure drops
                "core_temperature": 1.12,  # Temperature rises
                "vibration": 1.6          # Vibration increases
            }
        else:
            return {
                "pressure": 0.80,
                "core_temperature": 1.06,
                "vibration": 1.3
            }
    
    @staticmethod
    def pump_failure(severity: str = "yellow") -> Dict[str, float]:
        """Generate pump failure anomaly"""
        if severity == "red":
            return {
                "pressure": 0.65,    # Significant pressure drop
                "vibration": 3.0     # High vibration from failing pump
            }
        else:
            return {
                "pressure": 0.85,
                "vibration": 2.2
            }
    
    @staticmethod
    def get_anomaly_types() -> List[str]:
        """Get list of available anomaly types"""
        return [
            "temperature_spike",
            "pressure_drop", 
            "vibration_increase",
            "flux_instability",
            "coolant_leak",
            "pump_failure"
        ]
    
    @classmethod
    def generate_anomaly(cls, anomaly_type: str, severity: str = "yellow") -> Dict[str, float]:
        """
        Generate anomaly factors for a specific type
        
        Args:
            anomaly_type: Type of anomaly to generate
            severity: Severity level (yellow/red)
        """
        generators = {
            "temperature_spike": cls.temperature_spike,
            "pressure_drop": cls.pressure_drop,
            "vibration_increase": cls.vibration_increase,
            "flux_instability": cls.flux_instability,
            "coolant_leak": cls.coolant_leak,
            "pump_failure": cls.pump_failure
        }
        
        generator = generators.get(anomaly_type)
        if not generator:
            raise ValueError(f"Unknown anomaly type: {anomaly_type}")
        
        return generator(severity)

class TelemetryGenerator:
    """High-level telemetry generation coordinator"""
    
    def __init__(self):
        self.physics_engine = NuclearPhysicsEngine()
        self.anomaly_generator = AnomalyGenerator()
        self.time_step = 0
        self.active_anomalies = {}  # reactor_id -> anomaly_factors
    
    def generate_reading(
        self,
        reactor_id: int,
        reactor_type: str,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, float]:
        """Generate a telemetry reading for a reactor"""
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        # Get any active anomalies for this reactor
        anomalies = self.active_anomalies.get(reactor_id, {})
        
        # Generate the reading
        reading = self.physics_engine.generate_telemetry_reading(
            reactor_id=reactor_id,
            reactor_type=reactor_type,
            timestamp=timestamp,
            time_step=self.time_step,
            anomalies=anomalies
        )
        
        self.time_step += 1
        return reading
    
    def inject_anomaly(
        self,
        reactor_id: int,
        anomaly_type: str,
        severity: str = "yellow",
        duration_minutes: int = 30
    ):
        """
        Inject an anomaly into a reactor's data generation
        
        Args:
            reactor_id: Target reactor
            anomaly_type: Type of anomaly
            severity: Severity level
            duration_minutes: How long the anomaly lasts
        """
        anomaly_factors = self.anomaly_generator.generate_anomaly(anomaly_type, severity)
        
        # Store anomaly with expiration
        self.active_anomalies[reactor_id] = {
            "factors": anomaly_factors,
            "expires_at": datetime.utcnow() + timedelta(minutes=duration_minutes),
            "type": anomaly_type,
            "severity": severity
        }
    
    def clear_anomaly(self, reactor_id: int):
        """Clear any active anomaly for a reactor"""
        self.active_anomalies.pop(reactor_id, None)
    
    def update_anomalies(self):
        """Remove expired anomalies"""
        now = datetime.utcnow()
        expired = [
            reactor_id for reactor_id, anomaly in self.active_anomalies.items()
            if anomaly["expires_at"] < now
        ]
        
        for reactor_id in expired:
            self.active_anomalies.pop(reactor_id)
    
    def get_active_anomalies(self) -> Dict[int, Dict]:
        """Get currently active anomalies"""
        self.update_anomalies()
        return {
            reactor_id: {
                "type": anomaly["type"],
                "severity": anomaly["severity"],
                "expires_at": anomaly["expires_at"].isoformat()
            }
            for reactor_id, anomaly in self.active_anomalies.items()
        }
