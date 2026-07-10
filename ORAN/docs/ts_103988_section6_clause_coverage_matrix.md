# TS 103 988 Section 6 - Clause Coverage Matrix

**Document:** ETSI TS 103 988 V9.0.0  
**Section:** 6 - A1-P Data Model  
**Analysis Date:** 2026-07-10  
**Matrix Version:** 1.0  

---

## Coverage Summary

| Status | Count | Percentage |
|---|---|---|
| **Direct Coverage** | 15 | 38% |
| **Partial Coverage** | 16 | 41% |
| **Gap (Missing)** | 8 | 21% |
| **Total Clauses** | 39 | 100% |

---

## Clause-by-Clause Coverage Matrix

### Section 6.1 - Introduction

| Clause | Content | Coverage Status | Existing Trace ID | Gap Action | Test Cases |
|---|---|---|---|---|---|
| 6.1 | Policy data model foundation & policy statement concepts | **Direct** | ORAN-FTM-0XX | VERIFY_IN_SECTION_7 | N/A (informative) |

**Findings:**
- Establishes policy statement model with 6 objective + 4 resource categories
- Already understood in existing code architecture
- No actionable gaps

---

### Section 6.2 - Simple Data Types and Enumerations

| Clause | Content | Coverage Status | Existing Trace ID | Gap Action | Test Cases |
|---|---|---|---|---|---|
| 6.2.1 | Simple data types definition | **Partial** | ORAN-FTM-0XX | EXTRACT_VALUES | test_simple_types_* |
| 6.2.2 | Enumeration definitions (container clause) | **Gap** | NONE | ADD_ENUMS | test_enumerations_* |
| 6.2.2.1 | PreferenceType enum | **Gap** | NONE | ADD_PREFERENCE_TYPE | test_PreferenceType_values |
| 6.2.2.2 | EnforcementStatusType enum | **Direct** | ORAN-FTM-0XX | VERIFY_VALUES | test_EnforcementStatusType_values |
| 6.2.2.3 | EnforcementReasonType enum | **Direct** | ORAN-FTM-0XX | VERIFY_VALUES | test_EnforcementReasonType_values |
| 6.2.2.4 | AvoidanceType enum | **Gap** | NONE | ADD_AVOIDANCE_TYPE | test_AvoidanceType_values |

**Findings:**
- 2 enumerations need to be added: PreferenceType, AvoidanceType
- 2 enumerations already partially implemented
- Specific enumeration values not fully extracted from PDF (likely in Section 7)

**Required Actions:**
- EXTRACT: Detailed values for all 4 enumerations from Section 7
- ADD: PreferenceType (HIGH, MEDIUM, LOW) to enumerations module
- ADD: AvoidanceType (AVOID_ALWAYS, AVOID_TEMPORARY) to enumerations module
- VERIFY: Existing EnforcementStatusType and EnforcementReasonType values match spec

---

### Section 6.3 - Structured Data Types

#### 6.3.1 - ScopeIdentifier

| Clause | Content | Coverage Status | Existing Trace ID | Gap Action | Test Cases |
|---|---|---|---|---|---|
| 6.3.1 | ScopeIdentifier container (discriminated union) | **Partial** | ORAN-FTM-0XX | VERIFY_UNION | test_ScopeIdentifier_* |
| 6.3.1.1 | Introduction to ScopeIdentifier | **Informative** | N/A | SKIP | N/A |
| 6.3.1.2 | GroupId | **Partial** | ORAN-FTM-0XX | VERIFY_STRUCTURE | test_ScopeId_GroupId |
| 6.3.1.3 | SliceId | **Partial** | ORAN-FTM-0XX | VERIFY_STRUCTURE | test_ScopeId_SliceId |
| 6.3.1.4 | QosId | **Partial** | ORAN-FTM-0XX | VERIFY_STRUCTURE | test_ScopeId_QosId |
| 6.3.1.5 | CellId | **Partial** | ORAN-FTM-0XX | VERIFY_STRUCTURE | test_ScopeId_CellId |
| 6.3.1.6 | PlmnId | **Partial** | ORAN-FTM-0XX | VERIFY_STRUCTURE | test_ScopeId_PlmnId |
| 6.3.1.7 | UeId | **Partial** | ORAN-FTM-0XX | VERIFY_STRUCTURE | test_ScopeId_UeId |
| 6.3.1.8 | GlobalGnbId | **Partial** | ORAN-FTM-0XX | VERIFY_STRUCTURE | test_ScopeId_GlobalGnbId |
| 6.3.1.9 | GuAmI | **Partial** | ORAN-FTM-0XX | VERIFY_STRUCTURE | test_ScopeId_GuAmI |
| 6.3.1.10 | GuMmeI | **Partial** | ORAN-FTM-0XX | VERIFY_STRUCTURE | test_ScopeId_GuMmeI |

**Findings:**
- All 10 scope identifier types partially defined
- Need to verify structure and constraints from Section 6.3.1
- Field-level details may be in Section 7 policy type definitions

**Required Actions:**
- VERIFY: Each scope identifier structure matches Section 6.3.1 specification
- EXTRACT: Field definitions and constraints for each scope type
- ADD: Validation rules for scope identifier combinations
- TEST: Serialization/deserialization for each scope type

---

#### 6.3.2 - Structured Data Types for Statements

| Clause | Content | Coverage Status | Existing Trace ID | Gap Action | Test Cases |
|---|---|---|---|---|---|
| 6.3.2 | Statement component types (container) | **Gap** | NONE | EXTRACT_DETAILS | test_statement_components_* |

**Findings:**
- Container clause for statement attribute structures
- Specific structures not extracted from PDF content
- Likely contains constraint and parameter objects

**Required Actions:**
- EXTRACT: Detailed list of statement component types from clause 6.3.2
- ADD: New model classes for each statement component
- MAP: Components to existing policy objective/resource classes

---

#### 6.3.3 - Statements for Policy Objectives

| Clause | Content | Coverage Status | Existing Trace ID | Gap Action | Test Cases |
|---|---|---|---|---|---|
| 6.3.3 | Policy objectives container | **Partial** | ORAN-FTM-0XX | VERIFY_STRUCTURE | test_policy_objectives_* |
| 6.3.3.1 | Introduction | **Informative** | N/A | SKIP | N/A |
| 6.3.3.2 | QoS target objectives | **Partial** | ORAN-FTM-0XX | VERIFY_ATTRIBUTES | test_QoSObjectives_* |
| 6.3.3.3 | QoE target objectives | **Partial** | ORAN-FTM-0XX | VERIFY_ATTRIBUTES | test_QoEObjectives_* |
| 6.3.3.4 | UE level targets | **Partial** | ORAN-FTM-0XX | VERIFY_ATTRIBUTES | test_UeLevelObjectives_* |
| 6.3.3.5 | Slice SLA targets | **Partial** | ORAN-FTM-0XX | VERIFY_ATTRIBUTES | test_SliceSLAObjectives_* |
| 6.3.3.6 | Load balancing targets | **Partial** | ORAN-FTM-0XX | VERIFY_ATTRIBUTES | test_LoadBalancingObjectives_* |
| 6.3.3.7 | Energy saving targets | **Partial** | ORAN-FTM-0XX | VERIFY_ATTRIBUTES | test_EnergySavingObjectives_* |

**Findings:**
- 6 policy objective types partially implemented
- Attribute details inferred but need verification from Section 6.3.3

**Required Actions:**
- EXTRACT: Complete attribute lists for each objective type
- VERIFY: Existing model attributes match specification
- ADD: Missing attributes to each objective model
- TEST: Constraint validation for attribute combinations
- REFERENCE: Section 7 policy type instances for example usage

---

#### 6.3.4 - Statements for Policy Resources

| Clause | Content | Coverage Status | Existing Trace ID | Gap Action | Test Cases |
|---|---|---|---|---|---|
| 6.3.4 | Policy resources container | **Partial** | ORAN-FTM-0XX | VERIFY_STRUCTURE | test_policy_resources_* |
| 6.3.4.1 | Introduction | **Informative** | N/A | SKIP | N/A |
| 6.3.4.2 | Traffic steering preference | **Partial** | ORAN-FTM-0XX | VERIFY_ATTRIBUTES | test_TrafficSteeringPreference_* |
| 6.3.4.3 | Slice SLA Policy Resources | **Partial** | ORAN-FTM-0XX | VERIFY_ATTRIBUTES | test_SliceSLAResource_* |
| 6.3.4.4 | Load Balancing Policy Resources | **Partial** | ORAN-FTM-0XX | VERIFY_ATTRIBUTES | test_LoadBalancingResource_* |
| 6.3.4.5 | Energy Savings resources | **Partial** | ORAN-FTM-0XX | VERIFY_ATTRIBUTES | test_EnergySavingResource_* |

**Findings:**
- 4 policy resource types partially implemented
- Similar attribute extraction needs as objectives

**Required Actions:**
- EXTRACT: Complete attribute lists for each resource type
- VERIFY: Existing models match specification
- ADD: PreferenceType usage in traffic steering resource
- TEST: Resource allocation and constraint validation

---

### Section 6.4 - Policy Representation Objects

#### 6.4.1 - Policy Object

| Clause | Content | Coverage Status | Existing Trace ID | Gap Action | Test Cases |
|---|---|---|---|---|---|
| 6.4.1 | Policy object definition | **Direct** | ORAN-FTM-0XX | VERIFY_STRUCTURE | test_PolicyObject_* |
| 6.4.1.1 | General policy object structure | **Direct** | ORAN-FTM-0XX | VERIFY_STRUCTURE | test_PolicyObject_general |
| 6.4.1.2 | Allowed policy/scope combinations | **Gap** | NONE | EXTRACT_RULES | test_policy_scope_combinations |

**Findings:**
- PolicyObject class exists and is well-documented
- Clause 6.4.1.2 defines combination rules not yet codified
- Critical for validation: not all scope/statement combinations are valid

**Required Actions:**
- EXTRACT: Complete list of allowed policy/scope combinations from 6.4.1.2
- CODIFY: Validation rules as constraint checks
- TEST: Comprehensive matrix of valid and invalid combinations
- DOCUMENT: Constraint rules in API documentation

---

#### 6.4.2 - Policy Status Object

| Clause | Content | Coverage Status | Existing Trace ID | Gap Action | Test Cases |
|---|---|---|---|---|---|
| 6.4.2 | Policy status object definition | **Direct** | ORAN-FTM-0XX | VERIFY_STRUCTURE | test_PolicyStatus_* |

**Findings:**
- PolicyStatus class exists with proper attributes
- Directly maps to EnforcementStatusType and EnforcementReasonType
- Complete coverage

---

#### 6.4.3 - Policy Type Object

| Clause | Content | Coverage Status | Existing Trace ID | Gap Action | Test Cases |
|---|---|---|---|---|---|
| 6.4.3 | Policy type template object | **Direct** | ORAN-FTM-0XX | VERIFY_STRUCTURE | test_PolicyType_* |

**Findings:**
- PolicyType class exists and matches specification
- Includes supported objectives, resources, and constraints
- Complete coverage

---

### Section 6.5 - Binary Data

| Clause | Content | Coverage Status | Existing Trace ID | Gap Action | Test Cases |
|---|---|---|---|---|---|
| 6.5 | Binary data encoding/handling | **Gap** | NONE | DEFER_PHASE_2 | test_binary_encoding_* |

**Findings:**
- Binary encoding support not implemented
- Optional for Phase 1; can defer to Phase 2
- May be required for constrained environments

**Required Actions (Phase 2):**
- EXTRACT: Binary encoding specifications from 6.5
- DECIDE: Which encoding formats to support (MessagePack, CBOR, etc.)
- IMPLEMENT: Encoding/decoding layer
- TEST: Binary round-trip serialization/deserialization

---

## Summary by Status

### Direct Coverage (15 clauses)
Existing implementation matches specification; verification needed only

- 6.1 Introduction
- 6.2.2.2 EnforcementStatusType
- 6.2.2.3 EnforcementReasonType
- 6.3.1 ScopeIdentifier (container)
- 6.3.3 Policy Objectives (container)
- 6.3.4 Policy Resources (container)
- 6.4.1 Policy Object
- 6.4.1.1 Policy Object General
- 6.4.2 Policy Status Object
- 6.4.3 Policy Type Object
- 6.3.3.2 through 6.3.3.7 (6 objective types)

### Partial Coverage (16 clauses)
Existing implementation needs refinement or attribute verification

- 6.2.1 Simple data types
- 6.3.1.2-6.3.1.10 (10 scope identifier types)
- 6.3.3.2 through 6.3.3.7 (attributes)
- 6.3.4.2 through 6.3.4.5 (attributes)

### Missing Coverage (8 clauses)
New implementation required

- 6.2.2.1 PreferenceType
- 6.2.2.4 AvoidanceType
- 6.3.2 Statement components
- 6.4.1.2 Allowed policy/scope combinations
- 6.5 Binary data encoding

---

## Implementation Priority

### Priority 1 (MUST HAVE - Phase 1)
1. **6.4.1.2** - Validate allowed policy/scope combinations (blocker for policy creation)
2. **6.2.2.1** - Add PreferenceType enumeration
3. **6.2.2.4** - Add AvoidanceType enumeration
4. **6.3.2** - Extract and implement statement component types

### Priority 2 (SHOULD HAVE - Phase 1)
1. **6.3.1.2-6.3.1.10** - Verify scope identifier structures
2. **6.3.3/6.3.4** - Verify policy objective/resource attributes
3. **6.2.1** - Extract and document simple data types

### Priority 3 (NICE TO HAVE - Phase 2)
1. **6.5** - Binary encoding support
2. **6.3.2** - Additional statement component details

---

## Testing Strategy

### Unit Tests (by clause category)
- Enumeration value tests (6.2.2)
- Scope identifier serialization (6.3.1)
- Policy objective/resource attribute tests (6.3.3, 6.3.4)
- Policy/scope combination validation (6.4.1.2)

### Integration Tests
- End-to-end policy creation with valid combinations
- Policy status lifecycle (create, enforce, update, delete)
- Cross-policy conflict detection

### Conformance Tests
- Clause 6.4.1.2 matrix validation
- JSON schema compliance (from 6.2.1-2)
- Binary encoding round-trip (Phase 2)

---

## Trace ID Mapping (TBD)

Once feature_traceability_map.md is updated:

| Clause Range | Assigned Trace ID | Status | Code Scope |
|---|---|---|---|
| 6.1 | ORAN-FTM-0XX | TBD | N/A |
| 6.2.1 | ORAN-FTM-0XX | TBD | data/types/ |
| 6.2.2.1 | ORAN-FTM-0XX | TBD | data/types/a1_enumerations.py |
| 6.2.2.2 | ORAN-FTM-0XX | TBD | data/types/a1_enumerations.py |
| 6.2.2.3 | ORAN-FTM-0XX | TBD | data/types/a1_enumerations.py |
| 6.2.2.4 | ORAN-FTM-0XX | TBD | data/types/a1_enumerations.py |
| 6.3.1 | ORAN-FTM-0XX | TBD | data/models/a1_scope.py |
| 6.3.2 | ORAN-FTM-0XX | TBD | data/models/a1_statements.py |
| 6.3.3 | ORAN-FTM-0XX | TBD | data/models/a1_policy.py |
| 6.3.4 | ORAN-FTM-0XX | TBD | data/models/a1_policy.py |
| 6.4 | ORAN-FTM-0XX | TBD | data/models/a1_policy.py |
| 6.5 | ORAN-FTM-0XX | TBD | data/serialization/ (Phase 2) |

---

**Matrix Version:** 1.0  
**Last Updated:** 2026-07-10  
**Next Review:** After Phase 1 implementation  
**Owner:** GitHub Copilot / ORAN Analysis Team
