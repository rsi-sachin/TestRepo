# Phase 1 Steps 4-6 Implementation Guide

**Overview:** Completing the remaining Phase 1 tasks (3-4 hours each)

---

## Step 4: Extract Statement Components (3-4 hours)

**Source:** TS 103 988 clause 6.3.2 (Structured data types for statements)

**Task:** Create `demo-web/backend/app/data/models/a1_statement_components.py`

### Components to Define

From section 6.3.2, extract these types:

| Component | Purpose | Fields |
|---|---|---|
| RangeConstraint | Numeric range with min/max/step | minValue, maxValue, stepValue |
| MeasurementUnit | Unit of measurement | type (bytes, percentage, sec, etc.), scale |
| PolicyState | Policy activation state | active, inactive, transient |
| ConstraintType | Constraint specification | op (LT, LE, EQ, GE, GT, NE), value |
| ResourcePolicy | Resource-level directive | resourceId, actions[], constraints[] |

### Implementation Pattern

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional, List

class MeasurementUnitType(str, Enum):
    """Measurement unit types from TS 103 988 6.3.2"""
    BYTES = "bytes"
    KILOBYTES = "kilobytes"
    MEGABYTES = "megabytes"
    PERCENTAGE = "percentage"
    SECONDS = "seconds"
    # ... add more from spec

class RangeConstraint(BaseModel):
    """Range constraint for numeric policy values"""
    min_value: Optional[float] = Field(None, description="Minimum value")
    max_value: Optional[float] = Field(None, description="Maximum value")
    step_value: Optional[float] = Field(None, description="Step size")
```

### Reference Documents
- Section 6.3.2 directly defines each component
- Table 6.3.2-1 shows data types and constraints
- Check figure 6.3.2-1 for component relationships

---

## Step 5: Verify Scope Identifier Attributes (2-3 hours)

**Source:** TS 103 988 clause 6.3.1 (Scope identifiers)

**Task:** Complete `demo-web/backend/app/data/models/a1_scope_identifiers.py`

### Scope Types to Define

From section 6.3.1, define these 10 scope types:

| Scope Type | Table | Attributes | Validation |
|---|---|---|---|
| UeId | 6.3.1-1 | ueIdentifier, plmn | Must be valid UE identifier |
| GroupId | 6.3.1-2 | groupIdentifier | String format |
| SliceId | 6.3.1-3 | sst, sd | SST is required, SD optional |
| QosId | 6.3.1-4 | qosClassIdentifier | 0-9 range |
| CellId | 6.3.1-5 | cellIdentifier, plmn | Cell reference format |
| PlmnId | 6.3.1-6 | mcc, mnc | Mobile country/network code |
| GlobalGnbId | 6.3.1-7 | plmn, gnbId | gNB identifier |
| GuAmI | 6.3.1-8 | plmn, amfId | AMF identifier |
| GuMmeI | 6.3.1-9 | plmn, mmeId | MME identifier |
| TaiList | 6.3.1-10 | trackingAreaId[] | List of TA identifiers |

### Implementation Pattern

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List

class SliceIdentifier(BaseModel):
    """Network Slice Identifier from TS 103 988 6.3.1"""
    sst: int = Field(..., ge=0, le=255, description="Slice Service Type")
    sd: Optional[str] = Field(None, description="Slice Differentiator (optional)")
    
    @validator('sd')
    def validate_sd_format(cls, v):
        if v and len(v) > 3:
            raise ValueError("SD must be 3 characters or less")
        return v

class CellIdentifier(BaseModel):
    """Cell Identifier from TS 103 988 6.3.1"""
    cell_id: str = Field(..., description="Cell identifier")
    plmn_id: str = Field(..., description="PLMN identifier")
```

### Reference Documents
- Section 6.3.1 table and descriptions
- Figure 6.3.1-1 shows identifier relationships
- Clause 6.1 provides context for scope definitions

---

## Step 6: Create Extended Test Suite (2-3 hours)

**Task:** Add integration and conformance tests

### Test Categories

#### 6.1: Policy Creation Workflows (30+ tests)

Test full policy creation scenarios:

```python
def test_qos_policy_ue_creation():
    """Test creating QoS policy targeting specific UE"""
    policy = {
        'scope': {'ueId': 'ue-123', 'qosId': 'qos-1'},
        'policy_statements': [{'qosObjectives': {...}}]
    }
    # Validate scope + statement combination
    assert validate_policy_scope('QoSTarget', 
                                 {'ueId': True, 'qosId': True, ...})

def test_slice_sla_policy_creation():
    """Test creating Slice SLA policy"""
    policy = {
        'scope': {'sliceId': 'slice-1'},
        'policy_statements': [{'sliceSlaObjectives': {...}}]
    }
    # Validate scope requirements
    assert validate_policy_scope('SliceSLATarget',
                                 {'sliceId': True, ...})
```

#### 6.2: Statement Component Validation (20+ tests)

Test statement component constraints:

```python
def test_qos_range_constraint():
    """Test QoS objective with range constraint"""
    constraint = RangeConstraint(
        min_value=0.0,
        max_value=100.0,
        step_value=10.0
    )
    # Validate constraint application
    assert validate_range_constraint(50.0, constraint)
    assert not validate_range_constraint(150.0, constraint)
```

#### 6.3: Scope Attribute Validation (30+ tests)

Test scope identifier attributes:

```python
def test_slice_identifier_validation():
    """Test slice identifier with required/optional fields"""
    slice_id = SliceIdentifier(sst=1, sd='001')
    # Validate SST required, SD optional
    assert slice_id.sst == 1
    assert slice_id.sd == '001'

def test_cell_identifier_plmn_validation():
    """Test cell identifier requires PLMN"""
    # Should fail - PLMN is required
    with pytest.raises(ValidationError):
        CellIdentifier(cell_id='cell-1')  # Missing plmn_id
```

#### 6.4: Cross-Policy Validation (10+ tests)

Test combinations across multiple policies:

```python
def test_qos_and_tsp_combined():
    """Test QoS + TSP policies for same scope"""
    qos_scope = {'ueId': True, 'qosId': True}
    tsp_scope = {'ueId': True, 'sliceId': False}
    # Both should be valid for same UE
    assert validate_policy_scope('QoSTarget', qos_scope)
    assert validate_policy_scope('TrafficSteeringPreference', tsp_scope)
```

### Test File Organization

```
tests/unit/models/
├── test_policy_scope_validator.py  (Already exists - 41 tests)
├── test_statement_components.py    (New - 20+ tests)
├── test_scope_identifiers.py       (New - 30+ tests)
└── test_policy_workflows.py        (New - 30+ integration tests)
```

### Test Fixtures to Create

```python
@pytest.fixture
def qos_policy_scope():
    """Valid QoS policy scope"""
    return {'ueId': True, 'qosId': True, 'sliceId': False, 
            'groupId': False, 'cellId': False}

@pytest.fixture
def slice_identifier():
    """Valid slice identifier"""
    return SliceIdentifier(sst=1, sd='001')

@pytest.fixture
def range_constraint():
    """Valid range constraint"""
    return RangeConstraint(min_value=0, max_value=100, step_value=10)
```

---

## Implementation Order

**Recommended sequence:**

1. **Step 4 (Statement Components)** - 3-4 hours
   - Simpler than scope identifiers
   - Can be done independently
   - Good starting point

2. **Step 5 (Scope Identifiers)** - 2-3 hours
   - Required for complete validation
   - Depends on understanding from Step 4
   - More complex attributes

3. **Step 6 (Tests)** - 2-3 hours
   - Write after Steps 4 & 5
   - Validates all three components together
   - Final quality assurance

**Total Estimated Time:** 7-10 hours

---

## Key Files to Monitor

| File | Purpose | Status |
|---|---|---|
| a1_policy_models.py | Policy enums & models | ✅ Complete |
| a1_policy_validator.py | Scope validation | ✅ Complete |
| a1_statement_components.py | Statement types | ⏳ Create |
| a1_scope_identifiers.py | Scope definitions | ⏳ Complete |
| test_*.py | Test coverage | ⏳ Expand |

---

## Testing Commands

```bash
# Run all Phase 1 tests
cd demo-web/backend
python -m pytest tests/unit/models/ -v

# Run specific test file
python -m pytest tests/unit/models/test_policy_scope_validator.py -v

# Run with coverage report
python -m pytest tests/unit/models/ --cov=app.models --cov=app.data

# Run specific test class
python -m pytest tests/unit/models/test_policy_scope_validator.py::TestQoSTargetCombinations -v
```

---

## Validation Checklist

After completing each step, verify:

- [ ] New files created in correct locations
- [ ] Code follows project style (PEP 8, Pydantic patterns)
- [ ] Comprehensive docstrings added
- [ ] Type hints for all functions/methods
- [ ] Tests written before code completion
- [ ] 100% of tests pass
- [ ] No import errors or circular dependencies
- [ ] Specification compliance verified
- [ ] Edge cases covered in tests

---

## Next Phase

After Phase 1 completion:

**Phase 2:** Binary encoding support (4-6 hours, optional)
- Implement binary/JSON-based serialization
- Add encoding/decoding tests
- Document binary format mappings

---

## Resources

- **TS 103 988 V9.0.0:** Section 6 (A1-P Data Model)
- **Implementation Gap Analysis:** `ORAN/docs/ts_103988_section6_gap_analysis.md`
- **Allowed Combinations Reference:** `ORAN/docs/section_6_4_1_2_allowed_combinations.md`
- **Current Test Results:** Test suite passes 41/41 tests
