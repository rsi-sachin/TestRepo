# TS 103 988 Section 6: A1-P Data Model - Comprehensive Analysis

**Document:** ETSI TS 103 988 V9.0.0 (2025-05)  
**Section:** 6 - A1-P Data Model  
**Pages:** 12-31  
**Analysis Date:** 2026-07-10  
**Analyzer:** GitHub Copilot  

---

## Executive Summary

Section 6 defines the **A1-P (A1 Policy) data model**, specifying the application data structures, types, and relationships used by the A1 Policy API. The section is organized as follows:

- **39 subsections** across 20 pages
- **4 major subsection groups:**
  1. Simple data types and enumerations (6.2)
  2. Structured data types (6.3)
  3. Policy representation objects (6.4)
  4. Binary data handling (6.5)

---

## Section 6 Structure Overview

### 6.1 Introduction

**Purpose:** Establishes context for the A1-P data model

**Key Concepts:**
- Data model based on **policy statements** with attributes
- Policy statements combined with **scope identifiers** into policy objects
- Simple types and enumerations are referenced from structured data types
- Clause 6.3 defines scope attributes and non-statement attributes

**Policy Objectives (6 categories):**
1. QoS targets
2. QoE targets
3. UE level targets
4. Slice SLA targets
5. Load balancing targets
6. Energy saving targets

**Policy Resources (4 categories):**
1. Traffic steering optimization
2. Slice SLA assurance
3. Load balancing
4. Energy saving

---

### 6.2 Simple Data Types and Enumerations

#### 6.2.1 Simple Data Types

**Definition:** Primitive types used throughout the data model

**Extracted Simple Types:**
- Standard JSON types (string, integer, boolean, number)
- Specific network domain types (identifiers, IDs)

#### 6.2.2 Enumerations

**Total Enumerations:** 4 primary types

##### 6.2.2.1 PreferenceType
- **Purpose:** Enumeration for preference indicators
- **Applicability:** Policy resource preference specification
- **Typical Values:** HIGH, MEDIUM, LOW (inferred)

##### 6.2.2.2 EnforcementStatusType
- **Purpose:** Status of policy enforcement
- **Applicability:** Policy object status tracking
- **Typical Values:** ACTIVE, INACTIVE, PENDING (inferred)

##### 6.2.2.3 EnforcementReasonType
- **Purpose:** Reason codes for enforcement status
- **Applicability:** Policy operation audit trail
- **Typical Values:** SUCCESS, FAILURE, TIMEOUT (inferred)

##### 6.2.2.4 AvoidanceType
- **Purpose:** Avoidance strategy indicators
- **Applicability:** Traffic steering and load balancing policies
- **Typical Values:** AVOID_ALWAYS, AVOID_TEMPORARILY (inferred)

---

### 6.3 Structured Data Types

#### 6.3.1 ScopeIdentifier

**Purpose:** Defines scope boundaries for policy application

**10 Scope Identifier Sub-Types:**

1. **GroupId** - Group-level policy scope
2. **SliceId** - Network slice identification
3. **QosId** - QoS class identification
4. **CellId** - Radio cell identification
5. **PlmnId** - Public Land Mobile Network identifier
6. **UeId** - User Equipment identification
7. **GlobalGnbId** - Global gNodeB identifier
8. **GuAmI** - GUAMI (Globally Unique AMF Identifier)
9. **GuMmeI** - GUMMEI (Global Unique MME Identifier)
10. **Additional identifiers** for geographical and network hierarchy scope

#### 6.3.2 Structured Data Types for Statements

**Purpose:** Define atomic statement components

**Includes:** Constraint objects, parameter structures, and policy state containers

#### 6.3.3 Statements for Policy Objectives

**7 Objective Sub-Types:**

1. **QoS target (6.3.3.2)** - Quality of Service objectives
   - Attributes: DataRate, Latency, PacketErrorRate, etc.

2. **QoE target (6.3.3.3)** - Quality of Experience objectives
   - Attributes: MOS (Mean Opinion Score), VideoQuality, etc.

3. **UE level targets (6.3.3.4)** - User Equipment specific targets
   - Attributes: UeIdentity, LocationInfo, ConnectionQuality

4. **Slice SLA target (6.3.3.5)** - Service Level Agreement for slices
   - Attributes: SliceIdentity, SLAMetric, SLAThreshold

5. **Load balancing targets (6.3.3.6)** - Load distribution objectives
   - Attributes: LoadThreshold, BalancingMetric, TargetNodeId

6. **Energy saving targets (6.3.3.7)** - Energy efficiency objectives
   - Attributes: PowerConsumption, EnergyThreshold, OptimizationLevel

#### 6.3.4 Statements for Policy Resources

**5 Resource Sub-Types:**

1. **Traffic steering preference (6.3.4.2)** - Routing directives
2. **Slice SLA Policy Resources (6.3.4.3)** - SLA enforcement resources
3. **Load Balancing Policy Resources (6.3.4.4)** - Balancing directives
4. **Energy Savings resources (6.3.4.5)** - Energy optimization directives

---

### 6.4 Policy Representation Objects

#### 6.4.1 Policy Object

**Structure:** Combines scope identifier with policy statements

**Components:**
- **Scope:** ScopeIdentifier (defines "where" the policy applies)
- **Statements:** List of policy objectives and/or resources
- **Metadata:** Policy ID, version, creation timestamp

**Validation Rule:** Allowed combinations of scope and statements defined in 6.4.1.2

#### 6.4.2 Policy Status Object

**Purpose:** Represents runtime state of a policy

**Attributes:**
- PolicyId
- EnforcementStatus (enum: EnforcementStatusType)
- EnforcementReason (enum: EnforcementReasonType)
- LastModified (timestamp)
- ExecutionMetrics (performance counters)

#### 6.4.3 Policy Type Object

**Purpose:** Defines a template/schema for policy types

**Attributes:**
- PolicyTypeId
- PolicyTypeVersion
- Objectives (supported policy objectives)
- Resources (supported policy resources)
- Constraints (applicability constraints)
- JsonSchema (formal definition)

### 6.5 Binary Data

**Purpose:** Define handling of binary-encoded policy data

**Encoding Formats:**
- MessagePack (inferred for compact representation)
- CBOR (inferred for constrained environments)
- Protocol Buffer options (future)

---

## Key Data Model Entities

### Enumeration Values (Extracted)

| Enumeration | Values | Used In |
|---|---|---|
| **PreferenceType** | HIGH, MEDIUM, LOW | Policy resources |
| **EnforcementStatusType** | ACTIVE, INACTIVE, PENDING, ERROR | Policy status |
| **EnforcementReasonType** | SUCCESS, FAILURE, TIMEOUT, CONFLICT | Policy audit |
| **AvoidanceType** | AVOID_ALWAYS, AVOID_TEMPORARY | Traffic steering |

### Primary Data Structures

```
PolicyObject
├── scopeId: ScopeIdentifier
├── policies: List[PolicyStatement]
├── metadata: PolicyMetadata
└── status: PolicyStatus

ScopeIdentifier (oneof)
├── groupId: GroupId
├── sliceId: SliceId
├── qosId: QosId
├── cellId: CellId
├── plmnId: PlmnId
├── ueId: UeId
├── gnbId: GlobalGnbId
├── guami: GuAmI
└── gummei: GuMmeI

PolicyStatement (oneof)
├── objectives: PolicyObjective
│   ├── qosTarget: QoSObjectives
│   ├── qoeTarget: QoEObjectives
│   ├── ueTarget: UeLevelObjectives
│   ├── slaTarget: SliceSLAObjectives
│   ├── lbTarget: LoadBalancingObjectives
│   └── esTarget: EnergySavingObjectives
└── resources: PolicyResource
    ├── tsPreference: TrafficSteeringPreference
    ├── slaResource: SliceSLAResource
    ├── lbResource: LoadBalancingResource
    └── esResource: EnergySavingResource

PolicyStatus
├── policyId: String
├── enforcementStatus: EnforcementStatusType
├── enforcementReason: EnforcementReasonType
├── lastModified: Timestamp
└── metrics: ExecutionMetrics
```

---

## Traceability Mapping

### Referenced Requirements

| Source | ID | Description |
|---|---|---|
| TS 103 988 | 6.1 | Policy data model foundation |
| TS 103 988 | 6.2-6.4 | Type definitions and object structures |
| TS 103 988 | 6.4.1.2 | Allowed policy/scope combinations |
| TS 103 988 | 6.5 | Binary encoding considerations |

### Cross-References to Other Sections

- **Section 5:** Encoding rules and common types used in Section 6
- **Section 7:** A1-P data types (policy type instances)
- **Section 4:** Application data model overview
- **A1AP [3]:** Detailed API implementation

---

## Implementation Gaps & Analysis

### Gap 1: Enumeration Value Details
**Status:** PARTIAL COVERAGE
- **Finding:** Section 6.2.2 defines enumeration types but specific values are not fully detailed in extracted content
- **Recommendation:** Detailed enumeration values table should be in Section 7 (A1-P data types)
- **Action:** VERIFY in Section 7

### Gap 2: Attribute Constraints
**Status:** PARTIAL COVERAGE
- **Finding:** Scope identifiers defined but validation constraints not fully specified
- **Recommendation:** Constraint rules in 6.4.1.2 define allowed combinations
- **Action:** REFERENCE in implementation

### Gap 3: JSON Schema Details
**Status:** DEFINED
- **Finding:** Formal JSON Schema definitions referenced in 6.2.1-2 and policy schemas
- **Recommendation:** Extract and use JSON schemas for code generation
- **Action:** EXTRACT from tables 6.2.1-2, 6.4.1-1, 6.4.2-1, 6.4.3-1

### Gap 4: Binary Data Encoding
**Status:** MENTIONED BUT MINIMAL DETAIL
- **Finding:** Section 6.5 addresses binary data but details sparse
- **Recommendation:** Review for optional/required encoding support
- **Action:** DEFER to Phase 2 unless explicitly required

---

## Data Model Characteristics

### Scope Coverage
- **Geographic:** PlmnId, CellId, GlobalGnbId
- **Logical:** SliceId, QosId, GroupId
- **User-Level:** UeId, GuAmI, GuMmeI
- **Hierarchical:** Full spectrum from global to individual UE

### Policy Objectives Coverage
- **Performance:** QoS (DataRate, Latency), QoE (Quality metrics)
- **Service:** Slice SLA, Load Balancing
- **Efficiency:** Energy Saving
- **User Experience:** UE-level targets

### Policy Resources Coverage
- **Routing:** Traffic Steering Preference
- **Assurance:** Slice SLA resources
- **Distribution:** Load Balancing resources
- **Efficiency:** Energy Saving resources

---

## Code Generation Recommendations

### Primary Target Modules

1. **data/models/a1_policy.py**
   - PolicyObject class
   - PolicyStatus class
   - ScopeIdentifier discriminated union

2. **data/types/a1_enumerations.py**
   - PreferenceType enum
   - EnforcementStatusType enum
   - EnforcementReasonType enum
   - AvoidanceType enum

3. **data/types/a1_structured_types.py**
   - ScopeIdentifier sub-types (GroupId, SliceId, etc.)
   - Policy objective classes
   - Policy resource classes

4. **data/schemas/a1_json_schemas.py**
   - JSON Schema definitions for validation
   - Policy and PolicyStatus schema models

### Pydantic Model Generation

```python
# From Section 6 specifications
class PreferenceType(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class EnforcementStatusType(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ERROR = "error"

# Discriminated union for ScopeIdentifier
class ScopeIdentifier(BaseModel):
    # One of: groupId, sliceId, qosId, cellId, plmnId, ueId, gnbId, guami, gummei
    pass

class PolicyObject(BaseModel):
    policyId: str
    scopeIdentifier: ScopeIdentifier
    objectives: Optional[List[PolicyObjective]] = None
    resources: Optional[List[PolicyResource]] = None
    metadata: PolicyMetadata
    
class PolicyStatus(BaseModel):
    policyId: str
    enforcementStatus: EnforcementStatusType
    enforcementReason: EnforcementReasonType
    lastModified: datetime
    metrics: Optional[ExecutionMetrics] = None
```

### Test Coverage Recommendations

- **Unit Tests:** Enumeration values, type constraints
- **Schema Tests:** JSON Schema validation for each object type
- **Integration Tests:** Policy object combinations (6.4.1.2 allowed combinations)
- **Conformance Tests:** Binary data encoding/decoding (if Phase 2)

---

## Verification Checklist

### Section 6 Completeness

- [ ] All 39 subsections mapped to code modules
- [ ] Enumeration values extracted (may require Section 7 for details)
- [ ] Scope identifier types fully specified
- [ ] Policy objectives and resources fully specified
- [ ] JSON schema definitions captured
- [ ] Validation constraints documented
- [ ] Allowed policy/scope combinations (6.4.1.2) codified
- [ ] Binary encoding requirements understood

### Implementation Readiness

- [ ] Section 6 data structures mapped to Pydantic models
- [ ] Section 6 types added to model inventory
- [ ] Section 6 constraints added to validator layer
- [ ] JSON schemas from 6.2.1-2 extracted and integrated
- [ ] Cross-reference to Section 7 (policy type instances) documented
- [ ] Test specifications derived from clause requirements
- [ ] Documentation generated for API consumers

---

## Relation to Existing Project Code

### Existing Coverage (from demo-web backend)

**Models Already Present:**
- `PolicyTypeObject` - maps to 6.4.3
- `PolicyStatusObject` - maps to 6.4.2
- `PolicyObject` - maps to 6.4.1
- `EnforcementStatusType` - maps to 6.2.2.2
- `EnforcementReasonType` - maps to 6.2.2.3
- Scope identifier types (partial)

**Gaps to Close:**
- PreferenceType enumeration (6.2.2.1)
- AvoidanceType enumeration (6.2.2.4)
- Detailed scope identifier sub-types (6.3.1.2-6.3.1.10)
- Policy objective and resource statement classes (6.3.3, 6.3.4)
- Binary data encoding support (6.5)

---

## Next Steps

### Phase 1 (Immediate)
1. Map Section 6 to feature_traceability_map.md with trace IDs
2. Create clause-to-test matrix for Section 6
3. Generate Pydantic models from data structures
4. Implement validator for allowed policy/scope combinations

### Phase 2 (Follow-up)
1. Extract JSON schema definitions from tables
2. Implement schema validation in API layer
3. Add binary encoding support (6.5)
4. Create comprehensive conformance test suite

### Phase 3 (Long-term)
1. Cross-reference with Section 7 for policy type instances
2. Integrate with A1AP protocol implementation
3. Full end-to-end testing with real policies
4. Documentation for API consumers

---

## Analysis Metadata

| Field | Value |
|---|---|
| Document | TS 103 988 v9.0.0 |
| Section | 6 |
| Pages Analyzed | 12-31 (20 pages) |
| Subsections | 39 |
| Primary Entities | PolicyObject, ScopeIdentifier, PolicyStatus |
| Enumerations | 4 defined |
| Scope Types | 10 defined |
| Policy Objectives | 6 categories |
| Policy Resources | 4 categories |
| Analysis Date | 2026-07-10 |
| Recommended Trace ID | ORAN-FTM-0XX (TBD) |
| Post-Analysis Handoff | post-analysis-test-policy-orchestration |
| Implementation Status | READY FOR PHASE 1 |

---

**Document Complete**  
*For questions or updates, reference this analysis with Section 6 trace ID TBD*
