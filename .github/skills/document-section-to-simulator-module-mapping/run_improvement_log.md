# Run Improvement Log

## 2026-06-18 - Initial ORAN Baseline

### Input Set
- ORAN/docs/Non_RT_RIC_A1_Interface_Design.md
- ORAN/docs/List 1 Module Names.md
- ORAN/TODO-F2-simulator-tdd.md

### What Worked
- Deterministic mapping from A1 framework roles to List-1 module pairs.
- Clear phase focus constraints captured (NEAR_RT_RIC primary simulator; A1-P/O1/E2 active).
- Function group extraction for route/service/runtime/persistence layers.

### Ambiguities
- O1 source granularity can be interpreted as aggregate ORAN_INT_INFO_SOURCE only, or aggregate plus individual module emitters.
- A1-EI role appears in architecture, but intentionally deferred for current phase.

### Rule Updates Planned
- Add explicit precedence for O1 source selection when both aggregate and sub-module events are present.
- Add tie-break rules for mixed-interface sections.

### Next Validation Set
- One section each for A1 policy lifecycle, O1 alarm lifecycle, and E2 event lifecycle.
- Compare auto mapping manifest against manual expected mapping before promoting rules v2.

## 2026-06-18 - A1 Policy Service Description (Section 5.2.2)

### Input Set
- ORAN/docs/ts_103987v040300p.pdf (Section 5.2.2.1-5.2.2.4)
- ORAN/docs/List 1 Module Names.md
- ORAN/TODO-F2-simulator-tdd.md

### What Worked
- URI/resource rules in 5.2.2.4 mapped directly to simulator route additions under /policytypes/{policyTypeId}/policies/{policyId}.
- Representation-object statements in 5.2.2.3 mapped cleanly to service-level structures (PolicyObject, PolicyStatusObject).
- Callback notificationDestination statement mapped to persisted callback subscription metadata.

### Ambiguities
- Producer-side notification callback endpoint path is implementation-specific in simulator context.
- A1TD schema strictness is referenced but not fully encoded yet.

### Rule Updates Planned
- Add explicit rule: when section includes resource identifiers, prioritize route-layer expansion before service heuristics.
- Add object-mapping rule for representation object lists to runtime/persistence fields.

### Next Validation Set
- Validate 5.2.4 service operation clauses against current status/notification route behavior and expected HTTP status codes.
