"""
Info Sources Simulator

Simulates external information sources that provide enrichment data to Non-RT RIC.
Generates deterministic EI job results and status notifications for A1-EI consumers.

Phase A: Deterministic result generation and notification delivery.
Phase B: Configurable result schemas and latency patterns.
"""

import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from uuid import uuid4
import random


logger = logging.getLogger(__name__)


class InfoSourceSimulator:
    """
    Deterministic information source simulator for A1-EI job result delivery.
    
    Responsibilities:
    - Generate deterministic EI job results for specific EI types
    - Send result notifications to Non-RT RIC callback URIs
    - Track result generation history for observability
    
    Phase A: Supports ORAN_UEGeoandVel_3.0.1 EI type with synthetic UE location data.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize info source simulator.
        
        Args:
            config: Simulator configuration (mode, seed, latency, etc.)
        """
        self.config = config or {}
        self.mode = self.config.get("mode", "deterministic")
        self.seed = self.config.get("seed", 42)
        self.latency_ms = self.config.get("latency_ms", 0.0)
        self.result_generation_strategy = self.config.get("result_generation_strategy", "synthetic")
        
        # Initialize random with seed for reproducibility
        random.seed(self.seed)
        
        # Track generated results
        self.generated_results: Dict[str, Dict[str, Any]] = {}
        self.notification_history: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized InfoSourceSimulator: mode={self.mode}, seed={self.seed}")
    
    async def generate_result_for_ei_job(
        self, 
        ei_type_id: str,
        ei_job_id: str,
        job_definition: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a deterministic EI result for a job.
        
        Args:
            ei_type_id: EI type identifier (e.g., "ORAN_UEGeoandVel_3.0.1")
            ei_job_id: EI job identifier
            job_definition: Optional job definition for context
            
        Returns:
            Generated result payload
        """
        if self.latency_ms > 0:
            await asyncio.sleep(self.latency_ms / 1000.0)
        
        result = None
        
        if ei_type_id == "ORAN_UEGeoandVel_3.0.1":
            result = self._generate_uegeoandvel_result(ei_job_id, job_definition)
        else:
            logger.warning(f"Unsupported EI type for result generation: {ei_type_id}")
            result = self._generate_generic_result(ei_job_id)
        
        # Track result
        self.generated_results[ei_job_id] = {
            "ei_type_id": ei_type_id,
            "result": result,
            "generated_at": datetime.utcnow().isoformat(),
        }
        
        return result
    
    def _generate_uegeoandvel_result(
        self, 
        ei_job_id: str,
        job_definition: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate deterministic UE geo-location and velocity result.
        
        Returns an array of UE location/velocity observations per TS 103 988 §9.2.1.3.4.
        """
        # Default to 3 synthetic observations if not specified
        num_observations = 3
        
        # Adjust based on job definition if provided
        if job_definition and isinstance(job_definition, dict):
            constraints = job_definition.get("jobDefinition", {}).get("constraints", {})
            reporting_amount = constraints.get("reportingAmount", 3)
            num_observations = min(reporting_amount, 10)  # Cap at 10
        
        observations = []
        base_lat = 59.3293  # Stockholm latitude (deterministic seed point)
        base_lon = 18.0686  # Stockholm longitude
        
        for i in range(num_observations):
            # Deterministic variation based on seed
            lat_offset = (i * 0.0001) % 0.01
            lon_offset = (i * 0.00015) % 0.01
            
            # Point location observation with altitude uncertainty (§9.2.1.3.4)
            observation = {
                "location": {
                    "pointAltitudeUncertainty": {
                        "point": {
                            "latitude": base_lat + lat_offset,
                            "longitude": base_lon + lon_offset,
                            "altitude": 50 + (i * 5)
                        },
                        "uncertainty": {
                            "uncertaintyAltitude": 10.0,
                            "uncertaintyRadius": 20.0 + (i * 2.0)
                        }
                    }
                },
                "velocity": {
                    "hVelocity": {
                        "bearing": (i * 45) % 360,  # Deterministic bearing
                        "horizontalSpeed": 5 + (i * 0.5)
                    }
                },
                "timestamp": (datetime.utcnow().timestamp() + i) * 1000,  # ms
                "confidence": 95 - (i * 2)  # Deterministic confidence decay
            }
            observations.append(observation)
        
        return observations
    
    def _generate_generic_result(self, ei_job_id: str) -> Dict[str, Any]:
        """Generate a generic EI result for unknown EI types."""
        return {
            "ei_job_id": ei_job_id,
            "data": "synthetic result",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def send_result_notification(
        self, 
        destination_uri: str,
        ei_job_id: str,
        result: Dict[str, Any] | List[Dict[str, Any]]
    ) -> bool:
        """
        Send EI result notification to Non-RT RIC callback URI.
        
        Args:
            destination_uri: Callback URI for result delivery
            ei_job_id: EI job identifier
            result: EI result payload
            
        Returns:
            Success flag
        """
        if self.latency_ms > 0:
            await asyncio.sleep(self.latency_ms / 1000.0)
        
        # Simulate delivery (Phase A: just log)
        notification = {
            "ei_job_id": ei_job_id,
            "destination": destination_uri,
            "result_summary": {
                "type": "array" if isinstance(result, list) else "object",
                "size": len(result) if isinstance(result, list) else len(str(result))
            },
            "delivered_at": datetime.utcnow().isoformat(),
        }
        
        self.notification_history.append(notification)
        
        logger.info(
            f"Sent EI result notification for job {ei_job_id} "
            f"to {destination_uri}"
        )
        
        return True
    
    async def send_status_notification(
        self, 
        destination_uri: str,
        ei_job_id: str,
        status: str,
        status_reason: Optional[str] = None
    ) -> bool:
        """
        Send EI job status notification to Non-RT RIC callback URI.
        
        Args:
            destination_uri: Callback URI for status delivery
            ei_job_id: EI job identifier
            status: Status value (STARTED, COMPLETED, FAILED, etc.)
            status_reason: Optional reason string
            
        Returns:
            Success flag
        """
        if self.latency_ms > 0:
            await asyncio.sleep(self.latency_ms / 1000.0)
        
        notification = {
            "ei_job_id": ei_job_id,
            "destination": destination_uri,
            "status": status,
            "status_reason": status_reason or f"Job transitioned to {status}",
            "sent_at": datetime.utcnow().isoformat(),
        }
        
        self.notification_history.append(notification)
        
        logger.info(
            f"Sent EI status notification for job {ei_job_id}: {status}"
        )
        
        return True
    
    def reset(self) -> None:
        """Reset simulator state for next test run."""
        self.generated_results.clear()
        self.notification_history.clear()
        logger.info("InfoSourceSimulator state reset")
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get current state summary for observability."""
        return {
            "mode": self.mode,
            "seed": self.seed,
            "total_results_generated": len(self.generated_results),
            "total_notifications_sent": len(self.notification_history),
            "supported_ei_types": ["ORAN_UEGeoandVel_3.0.1"],
            "generation_strategy": self.result_generation_strategy,
        }
    
    def get_notification_history(self) -> List[Dict[str, Any]]:
        """Get history of sent notifications."""
        return list(self.notification_history)
