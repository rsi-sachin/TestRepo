"""
Demo model - Pydantic schemas for API
Maps to Java Demo.java from desktop app
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional
from enum import Enum


class DemoStatus(str, Enum):
    """Demo execution status"""
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Demo(BaseModel):
    """Demo scenario definition - maps to Java Demo.java"""
    id: str = Field(..., description="Unique demo identifier")
    title: str = Field(..., description="Display title")
    description: str = Field(..., description="Detailed description")
    expected_outcome: str = Field(..., alias="expectedOutcome", description="Expected test outcome")
    protocol: str = Field(..., description="Protocol (SIP_IMS, DIAMETER, RADIUS)")
    complexity: str = Field(..., description="Complexity level (BASIC/INTERMEDIATE/ADVANCED)")
    jmx_path: str = Field(..., alias="jmxPath", description="Path to JMeter JMX file")
    default_params: Dict[str, str] = Field(default_factory=dict, alias="defaultParams", description="Default parameters")
    
    class Config:
        populate_by_name = True  # Allow both camelCase and snake_case
        json_schema_extra = {
            "example": {
                "id": "sip-001",
                "title": "VoLTE Call Setup",
                "description": "Demonstrates basic VoLTE call establishment",
                "expectedOutcome": "Successful call setup with 200 OK",
                "protocol": "SIP_IMS",
                "complexity": "BASIC",
                "jmxPath": "C:/TTS/docs/sip/reference_tests/test1.jmx",
                "defaultParams": {
                    "threads": "1",
                    "loops": "1"
                }
            }
        }


class DemoConfig(BaseModel):
    """Runtime configuration for demo execution"""
    demo_id: str
    parameters: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "demo_id": "sip-001",
                "parameters": {
                    "threads": "5",
                    "loops": "10",
                    "server_ip": "192.168.1.100"
                }
            }
        }
