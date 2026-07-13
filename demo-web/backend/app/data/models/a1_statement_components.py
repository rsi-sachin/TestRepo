"""
A1 Statement Components
Implements TS 103 988 clause 6.3.2 - Structured data types for policy statements

Defines component types used within policy statements including constraints,
measurement units, policy states, and resource-level directives.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class ComparisonOperator(str, Enum):
    """Comparison operators for constraint specifications (TS 103 988 6.3.2)"""
    LESS_THAN = "lt"           # <
    LESS_THAN_OR_EQUAL = "le"  # <=
    EQUAL = "eq"               # ==
    GREATER_THAN_OR_EQUAL = "ge"  # >=
    GREATER_THAN = "gt"        # >
    NOT_EQUAL = "ne"           # !=


class PolicyStateType(str, Enum):
    """Policy activation state (TS 103 988 6.3.2)"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRANSIENT = "transient"


class MeasurementUnitType(str, Enum):
    """Measurement unit types for policy values (TS 103 988 6.3.2)"""
    # Data volume units
    BYTES = "bytes"
    KILOBYTES = "kilobytes"
    MEGABYTES = "megabytes"
    GIGABYTES = "gigabytes"
    TERABYTES = "terabytes"
    
    # Data rate units
    BITS_PER_SECOND = "bps"
    KILOBITS_PER_SECOND = "kbps"
    MEGABITS_PER_SECOND = "mbps"
    GIGABITS_PER_SECOND = "gbps"
    
    # Time units
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    MICROSECONDS = "microseconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    
    # Percentage/ratio
    PERCENTAGE = "percentage"
    RATIO = "ratio"
    COUNT = "count"
    
    # Latency
    LATENCY_MS = "latency_ms"
    LATENCY_US = "latency_us"
    
    # Quality metrics
    PACKETS_PER_SECOND = "pps"
    FRAMES_PER_SECOND = "fps"
    DECIBELS = "db"


class RangeConstraint(BaseModel):
    """
    Numeric range constraint for policy values
    
    From TS 103 988 6.3.2 - defines valid value range with optional step
    """
    
    min_value: Optional[float] = Field(
        None,
        description="Minimum allowed value (inclusive)",
        title="Minimum Value"
    )
    max_value: Optional[float] = Field(
        None,
        description="Maximum allowed value (inclusive)",
        title="Maximum Value"
    )
    step_value: Optional[float] = Field(
        None,
        ge=0,
        description="Step size for valid values (e.g., 0.1, 1, 10)",
        title="Step Value"
    )

    @field_validator('max_value')
    @classmethod
    def validate_max_vs_min(cls, v, info):
        """Ensure max_value >= min_value if both specified"""
        if v is not None and info.data.get('min_value') is not None:
            if v < info.data['min_value']:
                raise ValueError("max_value must be >= min_value")
        return v

    def is_valid_value(self, value: float) -> bool:
        """Check if a value satisfies this range constraint"""
        if self.min_value is not None and value < self.min_value:
            return False
        if self.max_value is not None and value > self.max_value:
            return False
        if self.step_value is not None and self.step_value > 0:
            # Check if value is a valid step from min_value
            base = self.min_value or 0
            steps_from_base = (value - base) / self.step_value
            # Allow small floating point error
            if abs(steps_from_base - round(steps_from_base)) > 1e-9:
                return False
        return True


class MeasurementUnit(BaseModel):
    """
    Measurement unit specification
    
    From TS 103 988 6.3.2 - describes the unit of measurement for policy values
    """
    
    unit_type: MeasurementUnitType = Field(
        ...,
        description="The type of measurement unit",
        title="Unit Type"
    )
    scale: Optional[int] = Field(
        None,
        ge=0,
        description="Scale factor (e.g., 10^scale for metric prefixes)",
        title="Scale Factor"
    )
    custom_label: Optional[str] = Field(
        None,
        description="Custom label for the unit (e.g., 'packets/sec')",
        title="Custom Label"
    )

    def __str__(self) -> str:
        """String representation of measurement unit"""
        if self.custom_label:
            return self.custom_label
        return self.unit_type.value


class ConstraintSpecification(BaseModel):
    """
    Constraint specification for policy values
    
    From TS 103 988 6.3.2 - single constraint with operator and value
    """
    
    operator: ComparisonOperator = Field(
        ...,
        description="Comparison operator",
        title="Operator"
    )
    value: float = Field(
        ...,
        description="Constraint value to compare against",
        title="Value"
    )
    unit: Optional[MeasurementUnit] = Field(
        None,
        description="Unit of the constraint value",
        title="Unit"
    )

    def evaluate(self, test_value: float) -> bool:
        """Evaluate if a test value satisfies this constraint"""
        op = self.operator
        if op == ComparisonOperator.LESS_THAN:
            return test_value < self.value
        elif op == ComparisonOperator.LESS_THAN_OR_EQUAL:
            return test_value <= self.value
        elif op == ComparisonOperator.EQUAL:
            return abs(test_value - self.value) < 1e-9
        elif op == ComparisonOperator.GREATER_THAN_OR_EQUAL:
            return test_value >= self.value
        elif op == ComparisonOperator.GREATER_THAN:
            return test_value > self.value
        elif op == ComparisonOperator.NOT_EQUAL:
            return abs(test_value - self.value) >= 1e-9
        return False


class PolicyStatement(BaseModel):
    """
    Base policy statement with common attributes
    
    From TS 103 988 6.3.2 - represents a single policy directive
    """
    
    statement_id: Optional[str] = Field(
        None,
        description="Unique identifier for this policy statement",
        title="Statement ID"
    )
    state: PolicyStateType = Field(
        PolicyStateType.ACTIVE,
        description="Current activation state of this statement",
        title="State"
    )
    priority: Optional[int] = Field(
        None,
        ge=0,
        le=255,
        description="Priority level (0=lowest, 255=highest)",
        title="Priority"
    )
    constraints: Optional[List[ConstraintSpecification]] = Field(
        None,
        description="List of constraints applied to this statement",
        title="Constraints"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional metadata as key-value pairs",
        title="Metadata"
    )

    class Config:
        """Pydantic model configuration"""
        use_enum_values = False
        json_schema_extra = {
            "example": {
                "statement_id": "stmt-001",
                "state": "active",
                "priority": 100,
                "constraints": []
            }
        }


class QosObjective(PolicyStatement):
    """
    QoS Objective statement
    
    From TS 103 988 7.2.1 - specifies QoS requirements
    """
    
    downlink_bandwidth: Optional[float] = Field(
        None,
        ge=0,
        description="Downlink bandwidth requirement (in bps)",
        title="Downlink Bandwidth"
    )
    uplink_bandwidth: Optional[float] = Field(
        None,
        ge=0,
        description="Uplink bandwidth requirement (in bps)",
        title="Uplink Bandwidth"
    )
    max_latency: Optional[float] = Field(
        None,
        ge=0,
        description="Maximum latency requirement (in milliseconds)",
        title="Max Latency"
    )
    max_loss_rate: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Maximum packet loss rate (0-1 range)",
        title="Max Loss Rate"
    )
    min_throughput: Optional[float] = Field(
        None,
        ge=0,
        description="Minimum throughput requirement (in bps)",
        title="Min Throughput"
    )


class QoeObjective(PolicyStatement):
    """
    QoE (Quality of Experience) Objective statement
    
    From TS 103 988 7.2.2 - specifies user experience requirements
    """
    
    video_bitrate: Optional[float] = Field(
        None,
        ge=0,
        description="Target video bitrate (in bps)",
        title="Video Bitrate"
    )
    video_resolution: Optional[str] = Field(
        None,
        description="Target video resolution (e.g., '1920x1080')",
        title="Video Resolution"
    )
    audio_quality: Optional[str] = Field(
        None,
        description="Audio quality level (e.g., 'HD', 'Standard')",
        title="Audio Quality"
    )
    buffering_time: Optional[float] = Field(
        None,
        ge=0,
        description="Acceptable buffering time (in milliseconds)",
        title="Buffering Time"
    )
    startup_delay: Optional[float] = Field(
        None,
        ge=0,
        description="Acceptable startup delay (in milliseconds)",
        title="Startup Delay"
    )


class TrafficSteeringPreference(PolicyStatement):
    """
    Traffic Steering Preference statement
    
    From TS 103 988 7.2.3 - specifies preferred network routing
    """
    
    preferred_access_type: Optional[str] = Field(
        None,
        description="Preferred access technology (e.g., '5G_SA', '4G', 'WiFi')",
        title="Preferred Access Type"
    )
    preferred_network_slice: Optional[str] = Field(
        None,
        description="Preferred network slice ID",
        title="Preferred Slice"
    )
    avoid_access_type: Optional[str] = Field(
        None,
        description="Access type to avoid",
        title="Avoid Access Type"
    )
    geographic_preference: Optional[Dict[str, Any]] = Field(
        None,
        description="Geographic location preference",
        title="Geographic Preference"
    )


class UeLevelObjective(PolicyStatement):
    """
    UE-Level Objective statement
    
    From TS 103 988 7.2.6 - specifies UE-specific requirements
    """
    
    session_timeout: Optional[float] = Field(
        None,
        ge=0,
        description="Session timeout (in seconds)",
        title="Session Timeout"
    )
    max_concurrent_connections: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum concurrent connections for this UE",
        title="Max Concurrent Connections"
    )
    power_consumption_target: Optional[float] = Field(
        None,
        ge=0,
        description="Target power consumption (in watts)",
        title="Power Consumption Target"
    )


class SliceSlaObjective(PolicyStatement):
    """
    Slice-Level SLA Objective statement
    
    From TS 103 988 7.2.7 - specifies slice-level SLA requirements
    """
    
    availability: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Minimum availability (0-1 range, e.g., 0.999)",
        title="Availability"
    )
    latency_percentile: Optional[float] = Field(
        None,
        ge=0,
        description="Latency requirement (e.g., P99 latency in ms)",
        title="Latency Percentile"
    )
    throughput_commitment: Optional[float] = Field(
        None,
        ge=0,
        description="Committed throughput (in bps)",
        title="Throughput Commitment"
    )
    reliability: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Reliability requirement (0-1 range)",
        title="Reliability"
    )


class LoadBalancingObjective(PolicyStatement):
    """
    Load Balancing Objective statement
    
    From TS 103 988 7.2.8 - specifies load balancing strategy
    """
    
    max_load_percentage: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Maximum load percentage for cell (0-100)",
        title="Max Load Percentage"
    )
    target_load_percentage: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Target load percentage for optimal performance",
        title="Target Load Percentage"
    )
    load_balancing_type: Optional[str] = Field(
        None,
        description="Type of load balancing (e.g., 'RR', 'LeastLoaded')",
        title="Load Balancing Type"
    )


class EnergySavingObjective(PolicyStatement):
    """
    Energy Saving Objective statement
    
    From TS 103 988 7.2.9 - specifies energy efficiency requirements
    """
    
    power_saving_target: Optional[float] = Field(
        None,
        ge=0,
        le=100,
        description="Target power saving percentage (0-100)",
        title="Power Saving Target"
    )
    sleep_mode_duration: Optional[float] = Field(
        None,
        ge=0,
        description="Duration for sleep mode (in seconds)",
        title="Sleep Mode Duration"
    )
    renewable_energy_preference: Optional[bool] = Field(
        None,
        description="Prefer renewable energy sources if available",
        title="Renewable Energy Preference"
    )


class ResourceDirective(BaseModel):
    """
    Resource-level directive for policy enforcement
    
    From TS 103 988 6.3.2 - specifies how to apply policy at resource level
    """
    
    resource_id: str = Field(
        ...,
        description="Target resource identifier",
        title="Resource ID"
    )
    action: str = Field(
        ...,
        description="Action to apply (e.g., 'limit', 'prioritize', 'shape')",
        title="Action"
    )
    action_parameters: Optional[Dict[str, Any]] = Field(
        None,
        description="Parameters for the action",
        title="Action Parameters"
    )
    constraints: Optional[List[ConstraintSpecification]] = Field(
        None,
        description="Resource-level constraints",
        title="Constraints"
    )
    priority: Optional[int] = Field(
        None,
        ge=0,
        le=255,
        description="Priority for this resource directive",
        title="Priority"
    )


class StatementComponentFactory:
    """
    Factory for creating statement components from specification data
    """
    
    @staticmethod
    def create_range_constraint(
        min_val: Optional[float] = None,
        max_val: Optional[float] = None,
        step: Optional[float] = None
    ) -> RangeConstraint:
        """Create a RangeConstraint"""
        return RangeConstraint(
            min_value=min_val,
            max_value=max_val,
            step_value=step
        )
    
    @staticmethod
    def create_measurement_unit(
        unit_type: MeasurementUnitType,
        scale: Optional[int] = None,
        label: Optional[str] = None
    ) -> MeasurementUnit:
        """Create a MeasurementUnit"""
        return MeasurementUnit(
            unit_type=unit_type,
            scale=scale,
            custom_label=label
        )
    
    @staticmethod
    def create_constraint(
        operator: ComparisonOperator,
        value: float,
        unit: Optional[MeasurementUnit] = None
    ) -> ConstraintSpecification:
        """Create a ConstraintSpecification"""
        return ConstraintSpecification(
            operator=operator,
            value=value,
            unit=unit
        )
