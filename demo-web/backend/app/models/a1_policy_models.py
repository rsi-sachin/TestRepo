"""
A1 policy models aligned with TS 103 987 clause 5.2.2 and TS 103 988 Section 6.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, AnyHttpUrl


# Enumerations from TS 103 988 Section 6.2.2

class EnforcementStatusType(str, Enum):
    """Policy enforcement status type (TS 103 988 6.2.2.2)"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ERROR = "error"


class EnforcementReasonType(str, Enum):
    """Policy enforcement reason type (TS 103 988 6.2.2.3)"""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    CONFLICT = "conflict"
    NOT_APPLICABLE = "not_applicable"


class PreferenceType(str, Enum):
    """Preference indicator for policy resource selection (TS 103 988 6.2.2.1)"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AvoidanceType(str, Enum):
    """Avoidance strategy indicator (TS 103 988 6.2.2.4)"""
    AVOID_ALWAYS = "avoid_always"
    AVOID_TEMPORARY = "avoid_temporary"
    CONDITIONAL_AVOID = "conditional_avoid"


class ProblemDetails(BaseModel):
    """Structured error response payload for 4xx/5xx responses."""

    type: str = Field(default="about:blank", description="Problem type URI")
    title: str = Field(..., description="Short, human-readable problem summary")
    status: int = Field(..., description="HTTP status code")
    detail: str = Field(..., description="Human-readable error detail")
    instance: Optional[str] = Field(default=None, description="Request-specific instance URI")


class PolicyTypeObject(BaseModel):
    """Policy type definition with schemas for policy and policy status validation."""

    policy_type_id: str = Field(..., min_length=1, description="Policy type identifier")
    policy_schema: Dict[str, Any] = Field(default_factory=dict, description="JSON schema for PolicyObject")
    policy_status_schema: Dict[str, Any] = Field(
        default_factory=dict,
        description="JSON schema for PolicyStatusObject",
    )
    supports_policy_creation: bool = Field(
        default=True,
        description="Whether this policy type currently supports policy creation",
    )


class PolicyTypeStatusObject(BaseModel):
    """JSON representation of policy type availability status."""

    policy_type_id: str = Field(..., min_length=1, description="Policy type identifier")
    policy_type_status: str = Field(..., min_length=1, description="Current policy type status")
    status_reason: Optional[str] = Field(default=None, description="Optional reason for status")


class PolicyObject(BaseModel):
    """JSON representation of an A1 policy."""

    scope: Dict[str, Any] = Field(default_factory=dict, description="Scope identifier and associated fields")
    policy_statements: List[Dict[str, Any]] = Field(
        ...,
        min_length=1,
        description="At least one policy statement",
    )


class PolicyStatusObject(BaseModel):
    """JSON representation of policy enforcement status."""

    policy_id: str = Field(..., min_length=1, description="Policy identifier")
    enforcement_status: EnforcementStatusType = Field(
        ...,
        description="Current policy enforcement status (TS 103 988 6.2.2.2)"
    )
    enforcement_reason: Optional[EnforcementReasonType] = Field(
        default=None,
        description="Reason for enforcement status (TS 103 988 6.2.2.3)"
    )
    feedback: Dict[str, Any] = Field(default_factory=dict, description="Additional policy feedback")


class CreateOrReplacePolicyRequest(BaseModel):
    """Request body for create/replace policy operations."""

    policy: PolicyObject = Field(..., description="Policy payload")
    notification_destination: AnyHttpUrl = Field(
        ...,
        description="Callback URI for policy status/feedback notifications",
    )
