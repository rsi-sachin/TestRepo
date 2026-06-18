"""
Execution models - Request/response schemas for demo execution
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional, List
from datetime import datetime
from enum import Enum


class ExecutionStatus(str, Enum):
    """Execution status enum"""
    QUEUED = "queued"
    STARTING = "starting"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionRequest(BaseModel):
    """Request to execute a demo"""
    demo_id: str = Field(..., description="Demo ID to execute")
    parameters: Dict[str, str] = Field(default_factory=dict, description="Runtime parameters")
    
    class Config:
        json_schema_extra = {
            "example": {
                "demo_id": "sip-001",
                "parameters": {
                    "threads": "10",
                    "loops": "100"
                }
            }
        }


class ExecutionResult(BaseModel):
    """Result of demo execution"""
    execution_id: str = Field(..., description="Unique execution ID")
    demo_id: str
    status: ExecutionStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    
    # Statistics
    total_attempts: int = 0
    successful: int = 0
    failed: int = 0
    success_rate: float = 0.0
    
    # Output
    output_log: Optional[str] = None
    jtl_file: Optional[str] = None
    error_message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "execution_id": "exec-123456",
                "demo_id": "sip-001",
                "status": "completed",
                "started_at": "2026-05-14T13:30:00Z",
                "completed_at": "2026-05-14T13:32:15Z",
                "duration_seconds": 135.5,
                "total_attempts": 100,
                "successful": 98,
                "failed": 2,
                "success_rate": 98.0,
                "jtl_file": "runs/exec-123456.jtl"
            }
        }


class SipMessage(BaseModel):
    """SIP message for call flow visualization"""
    timestamp: str = Field(..., description="Message timestamp")
    type: str = Field(..., description="'request' or 'response'")
    method: Optional[str] = Field(None, description="SIP method (INVITE, ACK, BYE, etc.)")
    response_code: Optional[str] = Field(None, description="Response code (200, 404, etc.)")
    response_text: Optional[str] = Field(None, description="Response text (OK, Not Found, etc.)")
    from_actor: str = Field(..., description="Source actor (UE, P-CSCF, S-CSCF, HSS, etc.)")
    to_actor: str = Field(..., description="Destination actor")
    call_id: str = Field(..., description="SIP Call-ID header")
    label: Optional[str] = Field(None, description="JMeter sampler label")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "1234567890",
                "type": "request",
                "method": "INVITE",
                "response_code": None,
                "response_text": None,
                "from_actor": "UE",
                "to_actor": "P-CSCF",
                "call_id": "call-123@example.com",
                "label": "SIP Client"
            }
        }
