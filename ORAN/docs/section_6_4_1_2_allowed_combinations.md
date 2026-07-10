# Section 6.4.1.2 & Section 7: Policy/Scope Allowed Combinations

**Source:** TS 103 988 v9.0.0 (Clause 6.4.1.2 + Section 7 Policy Type Definitions)  
**Extracted:** 2026-07-10  
**Purpose:** Define allowed combinations of policy statements with scope identifiers  

---

## Key Finding from Clause 6.4.1.2

**Clause 6.4.1.2 Statement:**
> "A Statement can be applied together with a ScopeIdentifier containing different combinations of identifiers attributes. **Not all combinations are relevant** and **different combinations are relevant for different policy types** (see clause 7)."

**Critical Implication:**
- Clause 6.4.1.2 does NOT enumerate the combinations
- Combinations are defined in **Section 7 (Policy Type Definitions)**
- Each policy type (7.2.1 through 7.2.9) specifies its own allowed scope combinations
- Validation rule: Must check against specific policy type

---

## Policy Types and Their Scope Combinations

### Overview
Section 7 defines **9 policy types** with specific allowed combinations:

| # | Policy Type | Objectives | Resources | Scope Combinations |
|---|---|---|---|---|
| 1 | QoS target (7.2.1) | qosObjectives | tspResources | QoS-specific scopes |
| 2 | QoE target (7.2.2) | qoeObjectives | tspResources | QoE-specific scopes |
| 3 | Traffic steering (7.2.3) | (none) | tspResources | Steering-specific scopes |
| 4 | QoS + TSP (7.2.4) | qosObjectives | tspResources | Combined scopes |
| 5 | QoE + TSP (7.2.5) | qoeObjectives | tspResources | Combined scopes |
| 6 | UE level target (7.2.6) | ueLevelObjectives | (optional resources) | UE-specific scopes |
| 7 | Slice SLA target (7.2.7) | sliceSlaObjectives | slaSlaResources | Slice-specific scopes |
| 8 | Load balancing (7.2.8) | (none) | lbResources | Load-specific scopes |
| 9 | Energy Saving (7.2.9) | esObjectives | esResources | Energy-specific scopes |

---

## Extracted Combination Patterns

### Pattern 1: QoS Objectives (7.2.1)
**From Section 7.2.1.2.2:**
- **Statement:** qosObjectives
- **Optional Resources:** tspResources
- **Scope Patterns:** "A QoS statement can be applied together with ScopeIdentifier containing different combinations..."
- **Table Reference:** "Table 7.2.1.2.2-1: Allowed combinations of qosObjectives statement with ScopeIdentifier"
- **JSON Schema:** Contains `"required": ["scope", "qosObjectives"]`

### Pattern 2: Slice SLA Objectives (7.2.7)
**From Section 7.2.7.2.2:**
- **Statement:** sliceSlaObjectives
- **Optional Resources:** slaSlaResources
- **Scope Patterns:** "The sliceSlaObjectives statement can be applied together with ScopeIdentifier containing..."
- **Table Reference:** "Table 7.2.7.2.2-1: Allowed combinations of sliceSlaObjectives statement with ScopeIdentifier"
- **JSON Schema:** Contains `"required": ["scope", "sliceSlaObjectives"]`

### Pattern 3: UE Level Objectives (7.2.6)
**From Section 7.2.6.2.2:**
- **Statement:** ueLevelObjectives
- **Optional Resources:** (varies)
- **Scope Patterns:** "A UE level statement can be applied together with scope identifiers containing different..."

### Pattern 4: Load Balancing Resources (7.2.8)
**From Section 7.2.8.2.2:**
- **Statement:** (objectives only, no specific objective type)
- **Resources:** lbResources
- **Scope Patterns:** "ScopeIdentifier is used to designate a cell from which load needs to be transferred..."
- **Special Note:** "When ScopeIdentifier contains taiList or cellIdList, and esResources is present, the cells indicated in esResources should be a subset of the cells implied by the ScopeIdentifier"

### Pattern 5: Energy Saving (7.2.9)
**From Section 7.2.9.2.2:**
- **Statement:** esObjectives
- **Resources:** esResources
- **Scope Patterns:** "NOTE 2: When ScopeIdentifier contains taiList or cellIdList..."

---

## Detailed Combination Rules (By Policy Type)

### Policy Type 7.2.1: QoS Target
**Allowed Scope/Objective Combinations:**
- PLMN-level QoS policies
- Slice-level QoS policies
- Cell-level QoS policies
- UE-level QoS policies (specific UE ID)
- Group-level QoS policies
- *(See Table 7.2.1.2.2-1 for complete matrix)*

**Resources:**
- Optional: Traffic Steering Preference (tspResources)

**Example Use Cases:**
- QoS target for all UEs in a slice
- QoS target for specific UE
- QoS target for specific cell group

---

### Policy Type 7.2.2: QoE Target
**Pattern:** Similar to QoS (7.2.1)
**Key Difference:** Focused on user experience metrics instead of network metrics

**Resources:**
- Optional: Traffic Steering Preference (tspResources)

---

### Policy Type 7.2.3: Traffic Steering Preferences
**Allowed Scope/Resource Combinations:**
- Steering directives for specific cells
- Steering directives for specific UEs
- Steering directives for UE groups
- Steering directives for slices
- *(See Table 7.2.3.2.2-1)*

**Note:** Traffic steering is often used **as a resource** with other objectives (QoS, QoE)

---

### Policy Type 7.2.4: QoS Optimization with Resource Directive
**Combined Pattern:**
- Combines QoS objectives with traffic steering resources
- Tells network: "Achieve this QoS by steering traffic this way"

**Allowed Scopes:** Intersection of QoS (7.2.1) and TSP (7.2.3) scopes

---

### Policy Type 7.2.5: QoE Optimization with Resource Directive
**Combined Pattern:**
- Combines QoE objectives with traffic steering resources
- Similar to 7.2.4 but for QoE metrics

---

### Policy Type 7.2.6: UE Level Target
**Allowed Scope/Objective Combinations:**
- MUST include UE identifier (UeId, GuAmI, etc.)
- May include supplementary scopes (slice, cell, group)
- UE-specific objectives (not shared with other UEs)
- *(See Table 7.2.6.2.2-1)*

**Key Constraint:** UE-level policies apply to individual users, not groups

---

### Policy Type 7.2.7: Slice SLA Target
**Allowed Scope/Objective Combinations:**
- MUST include Slice identifier (SliceId with SST/SD)
- May include cell-level restrictions
- Slice-level SLA metrics
- *(See Table 7.2.7.2.2-1)*

**Key Constraint:** SLA targets apply to slices, providing service guarantees

**Resources:**
- Optional: Slice SLA Resources (slaSlaResources)

---

### Policy Type 7.2.8: Load Balancing
**Allowed Scope/Resource Combinations:**
- Source scope: Cell(s) from which load should be transferred
- Destination scope: Cell(s) to which load should be transferred
- Load balancing metrics in resources

**Scope Structure:**
- `"ScopeIdentifier is used to designate a cell from which load needs to be transferred to other cells"`
- Pattern: Source cell group → Destination cell group(s)

**Constraints:**
- When cellIdList is used in ScopeIdentifier
- Cells in lbResources should match ScopeIdentifier cells
- Coordination with energy saving policies

---

### Policy Type 7.2.9: Energy Saving
**Allowed Scope/Resource Combinations:**
- Cell-level energy optimization
- Cell group energy optimization
- Slice-level energy efficiency targets

**Resources:** Energy Saving resources (esResources)

**Constraints:**
- taiList (Tracking Area): Geographic grouping
- cellIdList: Specific cell list
- When combined with load balancing, coordinate cell targeting

---

## Scope Identifier Usage Patterns

### By Scope Type (Which Policy Types Use Which Scopes)

| Scope Type | Policy Types | Constraints |
|---|---|---|
| **PlmnId** | All types | Network-wide policies |
| **SliceId** | 7.2.1, 7.2.2, 7.2.4, 7.2.5, 7.2.7 | Slice-scoped policies |
| **GroupId** | 7.2.1, 7.2.2, 7.2.3, 7.2.4, 7.2.5 | Group-level steering |
| **CellId** | 7.2.1, 7.2.2, 7.2.8, 7.2.9 | Cell-level optimization |
| **QosId** | 7.2.1, 7.2.4 | QoS class specific |
| **UeId** | 7.2.1, 7.2.2, 7.2.3, 7.2.6 | User-specific policies |
| **GlobalGnbId** | 7.2.8, 7.2.9 | gNodeB-level operations |
| **GuAmI** | 7.2.6 | User-equipment to AMF |
| **GuMmeI** | 7.2.6 (legacy) | Legacy 4G equivalent |

---

## JSON Schema Pattern

Each policy type includes JSON schemas in Section 7 that formally define combinations:

```json
{
  "type": "object",
  "properties": {
    "scope": { "$ref": "#/$defs/ScopeIdentifier" },
    "qosObjectives": { "$ref": "#/$defs/QosObjectives" },
    "tspResources": { "$ref": "#/$defs/TrafficSteeringPreference" }
  },
  "required": ["scope", "qosObjectives"],
  "additionalProperties": false
}
```

**Key Patterns:**
- `"required"` field lists mandatory attributes
- Optional resources listed but not required
- Scopes are always required
- Objectives vary by policy type

---

## Implementation Requirements for Clause 6.4.1.2

### Validator Architecture

```python
class PolicyScopeValidator:
    # Define allowed combinations by policy type
    POLICY_COMBINATIONS = {
        'QoSTarget': {
            'objectives': ['qosObjectives'],
            'resources': ['tspResources'],
            'scopes': [
                ['plmnId'],
                ['plmnId', 'sliceId'],
                ['plmnId', 'groupId'],
                ['plmnId', 'cellId'],
                ['plmnId', 'ueId'],
                # ... see Table 7.2.1.2.2-1 for complete list
            ]
        },
        'SliceSLATarget': {
            'objectives': ['sliceSlaObjectives'],
            'resources': ['slaSlaResources'],
            'scopes': [
                ['plmnId', 'sliceId'],
                ['plmnId', 'sliceId', 'cellId'],
                # ... see Table 7.2.7.2.2-1 for complete list
            ]
        },
        # ... 9 policy types total
    }
    
    @staticmethod
    def validate(policy_object):
        """Validate policy/scope combination"""
        # 1. Check policy type is known
        # 2. Check objectives match policy type
        # 3. Check resources are appropriate
        # 4. Check scope combination is allowed
```

### Test Cases Required

- **Valid Combinations:** 30+ test cases (all combinations from all tables)
- **Invalid Combinations:** 20+ error cases (scope with wrong objectives)
- **Edge Cases:** Boundary conditions per scope type

---

## Tables to Extract (From Section 7)

These tables contain the authoritative allowed combinations and must be transcribed:

| Table | Policy Type | Content |
|---|---|---|
| 7.2.1.2.2-1 | QoS target | Allowed combinations of qosObjectives with ScopeIdentifier |
| 7.2.2.2.2-1 | QoE target | Allowed combinations of qoeObjectives with ScopeIdentifier |
| 7.2.3.2.2-1 | Traffic steering | Allowed combinations of tspResources with ScopeIdentifier |
| 7.2.4.2.2-1 | QoS + TSP | Allowed combinations of combined objectives/resources |
| 7.2.5.2.2-1 | QoE + TSP | Allowed combinations of combined objectives/resources |
| 7.2.6.2.2-1 | UE level | Allowed combinations of ueLevelObjectives with ScopeIdentifier |
| 7.2.7.2.2-1 | Slice SLA | Allowed combinations of sliceSlaObjectives with ScopeIdentifier |
| 7.2.8.2.2-1 | Load balancing | Allowed combinations of lbResources with ScopeIdentifier |
| 7.2.9.2.2-1 | Energy Saving | Allowed combinations of esObjectives/esResources |

---

## Next Actions

### Priority 1: Extract Tables
**Action:** Extract actual combination tables from Section 7.2.X.2.2
**File:** Create `ORAN/docs/section_7_combination_tables.md`
**Effort:** 2-3 hours (manual or enhanced PDF parsing)

### Priority 2: Implement Validator
**Action:** Create PolicyScopeValidator with all combinations
**File:** `demo-web/backend/app/models/validators/a1_policy_validator.py`
**Effort:** 2-4 hours (based on table extraction)

### Priority 3: Create Tests
**Action:** Generate 50+ test cases from tables
**File:** `demo-web/backend/tests/unit/models/test_policy_scope_combinations.py`
**Effort:** 2-3 hours

---

## Summary

**Clause 6.4.1.2 Key Point:**
- Clause 6.4.1.2 is **informative** (refers to Section 7)
- The **actual allowed combinations are in Section 7**, not Section 6
- Each of 9 policy types has its own combination table
- Validator must check against policy-type-specific rules

**Critical Difference:**
- NOT a single global mapping of scope→policy
- Rather, 9 separate mappings (one per policy type)
- Policy type determines what scopes are valid

**Validation Logic:**
```
1. Identify policy type (QoS, QoE, SLA, UE-level, etc.)
2. Look up policy type's allowed combinations (Table 7.2.X.2.2-1)
3. Verify provided scope matches one of allowed combinations
4. Verify objectives/resources match policy type definition
5. Pass validation or return specific error
```

---

**Status:** Immediate analysis complete  
**Recommendation:** Proceed to extraction of Section 7 combination tables (Priority 1)
