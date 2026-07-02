# TS 103 983 Section 4 Clause Coverage Matrix

Document: `ORAN/docs/ts_103983v040000p.pdf` (v4.0.0)
Scope: Section 4 (4.1 to 4.4)
Trace context: ORAN-FTM-005 (planned ingestion includes TS 103 983 principles), ORAN-FTM-011 (frontend workflow), ORAN-FTM-015 (section 4 conformance principles coverage), plus `ORAN/docs/traceability/matrix_*.md` entries for O1/E2/info-source topology mapping

## Matrix

| Clause | Clause intent | Existing implementation evidence | Existing tests | Coverage status | Action |
|---|---|---|---|---|---|
| 4.1.1 A1 architecture (general) | Define A1 as interface between Non-RT RIC and Near-RT RIC | `demo-web/backend/app/services/a1_service_registry.py`; `demo-web/backend/app/api/oran.py` service-scoped A1 flows | Indirect coverage through A1 policy/EI API and conformance suites | Partial | Add explicit architecture contract tests asserting role/interface boundaries from TS 103 983 section 4.1.1 |
| 4.1.2 Role of A1 in O-RAN architecture | Position A1 among SMO, O1, E2, internal/external information sources | `ORAN/docs/figure_4_1_2_1_oran_entities.json`; skeleton modules for `o1_interface`, `e2_interface`, `simulators/info_sources` | Direct topology-contract tests in `demo-web/backend/tests/conformance/test_ts103983_section4_topology_contracts.py` validate required entities/interfaces, MVP profile alignment, O1/E2 semantic validator contracts, and deterministic module health/status behavior | Covered | Extend from contract/stub validation to integration-level message-flow simulation when O1/E2 implementations evolve |
| 4.1.3.1 A1-P service architecture | Policy guidance from Non-RT RIC, policy lifecycle/feedback loop | `demo-web/backend/app/services/a1_policy_service.py`; `demo-web/backend/app/api/oran.py`; `demo-web/backend/app/services/a1_service_registry.py` | Strong policy unit/interface/conformance coverage in existing A1-P suites | Covered | Keep regression mapping current; no immediate add/modify needed |
| 4.1.3.2 A1-EI service architecture | EI discovery/request/delivery and EI job lifecycle semantics | `demo-web/backend/app/services/a1_enrichment_service.py`; `demo-web/backend/app/api/oran.py`; `demo-web/backend/app/services/a1_service_registry.py` | Strong EI unit/interface/conformance coverage including result delivery | Covered | Keep strict payload/status/result validations aligned with latest protocol work |
| 4.1.3.3 A1-ML service architecture | AI/ML model training message exchange support over A1 | Service type enum includes A1-ML in model metadata, but no A1-ML operational backend module/route | No A1-ML tests detected | Missing | Define explicit A1-ML scope decision (out-of-scope vs planned), then add trace row + baseline tests if in-scope |
| 4.2 A1 interface general principles (open/multi-vendor/extensible) | Ensure implementation-independence and extensibility of A1 services and data types | Service registry abstraction and spec discovery support extensibility (`demo-web/backend/app/services/oran_spec_discovery_service.py`) | Direct section-4 tests now assert architecture/capability exposure, but extensibility/backward-compatibility is not yet explicitly asserted | Partial | Add explicit extensibility and compatibility assertions for service/data-type evolution |
| 4.2 Policy and EI ownership rules | Policies managed by Non-RT RIC; EI jobs managed by Near-RT RIC; Non-RT RIC delivers EI while enabled | Ownership semantics encoded in A1-P/A1-EI service APIs and role metadata | Direct lifecycle checks in `demo-web/backend/tests/conformance/test_ts103983_section4_principles.py` validate policy and EI job create/update/status/delete flows | Covered | Keep lifecycle assertions in regression and extend with callback delivery assertions if scope expands |
| 4.3 Specification objectives | Multi-vendor interconnection, policy granularity, status/feedback, EI support, AI/ML exchange | A1-P and A1-EI objectives implemented; upload/spec-selection pipeline includes TS 103 983 | No objective-level acceptance matrix for TS 103 983 section 4.3 | Partial | Add objective-to-test acceptance matrix and map each objective to executable checks |
| 4.4 A1 interface capabilities | Capability set for policy transfer, status/feedback, EI discovery/request/delivery, AI/ML training exchanges | A1-P and A1-EI capabilities implemented in API/services and harness flows | Direct section-4 tests now validate unknown-resource error contracts (`application/problem+json`) and core capability endpoints for policy/EI flows; no A1-ML capability tests | Partial | Add capability row for A1-ML or document explicit exclusion in release scope |

## Summary

- covered: 4
- partial: 4
- missing: 1

## Key Gaps

1. O1/E2/info-source coverage is currently contract-level and stub-level; full integration message-flow behavior is not yet implemented.
2. A1-ML capability (sections 4.1.3.3, 4.4) is not implemented as an executable backend feature.
3. Section 4.2 extensibility/backward-compatibility principles still need explicit conformance assertions.

## Recommended Next Steps

1. Add integration-oriented O1/E2 path tests that simulate management and control exchanges beyond validator-level checks.
2. Add explicit conformance tests for section 4.2 extensibility and backward-compatible service/data-type growth.
3. Decide A1-ML scope (planned vs out-of-scope) and either implement baseline tests or mark explicit exclusion in traceability/coverage artifacts.