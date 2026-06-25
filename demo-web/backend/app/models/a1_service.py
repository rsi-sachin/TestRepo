"""
A1 service models and role definitions.

These models capture the service boundary introduced by TS 103 987 section 5.1:
- A1-P: policy management
- A1-EI: enrichment information
- Consumer/producer roles
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.oran import SpecType


class A1ServiceType(str, Enum):
    """Supported A1 services in this tool."""

    A1_P = "A1-P"
    A1_EI = "A1-EI"
    A1_ML = "A1-ML"


class A1RoleType(str, Enum):
    """Protocol roles for A1 service interactions."""

    CONSUMER = "consumer"
    PRODUCER = "producer"


class A1ServiceRole(BaseModel):
    """Role metadata for a service participant."""

    role_type: A1RoleType = Field(..., description="Consumer or producer role")
    label: str = Field(..., description="Human-readable role label")
    description: Optional[str] = Field(None, description="Role description")


class A1ServiceDefinition(BaseModel):
    """Definition of a supported A1 service."""

    service_type: A1ServiceType = Field(..., description="A1 service identifier")
    name: str = Field(..., description="Human-readable service name")
    description: str = Field(..., description="Service description")
    consumer_role: A1ServiceRole = Field(..., description="Service consumer role")
    producer_role: A1ServiceRole = Field(..., description="Service producer role")
    supported_specs: List[SpecType] = Field(default_factory=list, description="Related ETSI specs")
    resource_domains: List[str] = Field(default_factory=list, description="Resource domains owned by the producer")
    default_catalog_name: str = Field(..., description="Suggested catalog name for this service")
    supported: bool = Field(default=True, description="Whether the service is enabled in this tool")


class A1ServiceRegistryResponse(BaseModel):
    """API payload for listing supported A1 services."""

    services: List[A1ServiceDefinition] = Field(default_factory=list)