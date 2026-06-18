"""
Traffic generation models
Maps to Java TrafficProfile, TrafficStats, ConformanceScenario
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from datetime import datetime
from enum import Enum


class ConformanceScenario(str, Enum):
    """3GPP Conformance Scenarios"""
    # SIP Protocol
    INVALID_SIP_URI = "CONF-SIP-001"
    MISSING_MANDATORY_HEADER = "CONF-SIP-002"
    INVALID_CSEQ_NUMBER = "CONF-SIP-003"
    MALFORMED_SDP_OFFER = "CONF-SIP-004"
    
    # Authentication
    INVALID_AUTH_HEADER = "CONF-AUTH-001"
    EXPIRED_NONCE = "CONF-AUTH-002"
    WRONG_CREDENTIALS = "CONF-AUTH-003"
    
    # Registration
    REGISTRATION_TIMEOUT = "CONF-REG-001"
    INVALID_CONTACT_HEADER = "CONF-REG-002"
    REGISTRATION_REJECTED = "CONF-REG-003"
    
    # Session Setup
    INVITE_TIMEOUT = "CONF-CALL-001"
    PRECONDITION_FAILURE = "CONF-CALL-002"
    RESOURCE_ALLOCATION_FAILURE = "CONF-CALL-003"
    INCOMPATIBLE_MEDIA = "CONF-CALL-004"
    
    # Call Termination
    BYE_TIMEOUT = "CONF-TERM-001"
    
    # Routing
    ROUTING_FAILURE_USER_NOT_FOUND = "CONF-ROUTE-001"
    ROUTING_FAILURE_NO_PATH = "CONF-ROUTE-002"
    
    # Emergency
    EMERGENCY_CALL_REJECTION = "CONF-EMERG-001"
    
    # No failure
    NONE = "CONF-NONE"


class TrafficProfile(BaseModel):
    """Traffic generation configuration"""
    concurrent_calls: int = Field(default=10, ge=1, le=1000, description="Number of concurrent threads")
    total_calls: int = Field(default=100, ge=1, le=100000, description="Total calls to generate")
    ramp_up_seconds: int = Field(default=10, ge=0, le=600, description="Ramp-up time")
    duration_seconds: int = Field(default=0, ge=0, description="Test duration (0 = run until complete)")
    
    failure_rate: float = Field(default=0.0, ge=0.0, le=100.0, description="Failure injection rate %")
    failure_scenario: ConformanceScenario = Field(default=ConformanceScenario.NONE, description="Conformance scenario")
    
    class Config:
        json_schema_extra = {
            "example": {
                "concurrent_calls": 50,
                "total_calls": 500,
                "ramp_up_seconds": 30,
                "duration_seconds": 120,
                "failure_rate": 15.0,
                "failure_scenario": "CONF-AUTH-002"
            }
        }


class NodeStats(BaseModel):
    """Per-node statistics"""
    node_name: str
    messages_per_second: int = 0
    total_messages: int = 0


class TrafficStats(BaseModel):
    """Real-time traffic statistics"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    elapsed_seconds: float = 0.0
    
    # Overall stats
    total_attempts: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    success_rate: float = 0.0
    failure_rate: float = 0.0
    
    # Performance
    avg_response_time_ms: float = 0.0
    calls_per_second: float = 0.0
    
    # Per-node stats
    node_stats: List[NodeStats] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-05-14T13:30:00Z",
                "elapsed_seconds": 45.5,
                "total_attempts": 450,
                "successful_calls": 425,
                "failed_calls": 25,
                "success_rate": 94.4,
                "failure_rate": 5.6,
                "avg_response_time_ms": 125.3,
                "calls_per_second": 9.89,
                "node_stats": [
                    {"node_name": "P-CSCF", "messages_per_second": 4, "total_messages": 180},
                    {"node_name": "S-CSCF", "messages_per_second": 3, "total_messages": 135}
                ]
            }
        }
