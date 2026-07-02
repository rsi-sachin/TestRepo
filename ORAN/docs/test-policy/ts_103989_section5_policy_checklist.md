# Test Policy Checklist: TS 103 989 Section 5

Document ID: TPC-20260701-01
Version: 1.0
Status: Draft
Owner: ORAN A1 test engineering
Effective Date: 2026-07-01
Applies To: demo-web/backend A1-P and A1-EI section-5 coverage

## 1. Purpose
Define fail-closed controls for section-5 test creation, execution evidence capture, validation, and triage.

## 2. Scope
In scope:
- TS 103 989 section 5.2.1 to 5.2.6
- TS 103 989 section 5.3.1 to 5.3.6
- A1-P policy operation evidence and A1-EI job operation evidence

Out of scope:
- O1 and E2 protocol conformance outside section 5
- Performance certification sign-off thresholds for release governance

## 3. Normative Inputs
- Source requirements: ORAN/docs/ts_103989v040200p.pdf section 5
- Interface specs: ORAN/docs/feature_traceability_map.md
- Implementation plan: ORAN/docs/section_5_trace_mapped_implementation_plan.md
- Environment baseline: demo-web/backend pytest harness

## 4. Requirement Registry
| Requirement ID | Statement (MUST/SHALL) | Priority | Source Section | Notes |
|---|---|---|---|---|
| ORAN-FTM-001 | A1 policy type/query and operation behavior MUST be validated with deterministic status and evidence. | Critical | 5.2.1 to 5.2.5 | Backed by policy conformance and API tests |
| ORAN-FTM-002 | Notification paths MUST log and validate callback outcomes for success and failure responses. | Critical | 5.2.6 | Includes callback status validation and warning evidence |
| ORAN-FTM-003 | EI type and EI job lifecycle operations MUST be covered for create/query/update/delete/status. | Critical | 5.3.1 to 5.3.6 | Backed by EI service, conformance, and API tests |
| ORAN-FTM-004 | Section-5 clause coverage matrix MUST be maintained and unresolved actions MUST keep gate closed. | High | 5.2 and 5.3 | Enforced by coverage and verification summary artifacts |

## 5. Traceability Matrix
| Requirement ID | Test Case ID | Test Type | Preconditions | Observable Evidence | Pass Criteria | Negative Case Required (Y/N) |
|---|---|---|---|---|---|---|
| ORAN-FTM-001 | TC-S5-POL-001 | Conformance + Interface | A1 policy simulator initialized | Deterministic status and ProblemDetails payload | Status and payload checks pass | Y |
| ORAN-FTM-002 | TC-S5-NOT-001 | Unit + Conformance | Callback endpoint target configured | Warning log for non-2xx and timeout handling behavior | Expected warning/exception behavior observed | Y |
| ORAN-FTM-003 | TC-S5-EI-001 | Unit + Conformance + Interface | EI default type available | EI job lifecycle state transitions and summary verdict | Full lifecycle assertions pass | Y |
| ORAN-FTM-004 | TC-S5-GATE-001 | Governance | Coverage artifact generation complete | Coverage matrix and verification summary show no unresolved required actions | completion_gate_status is pass | Y |

## 6. Creation Gate (Fail-Closed)
Checklist:
- [x] Every in-scope Requirement ID is mapped to at least one test case.
- [x] Every Critical requirement has positive and negative coverage intent documented.
- [x] Test assumptions are listed in this checklist and in section-5 artifacts.
- [x] Required documents are referenced by path and section.
- [x] Test data strategy uses synthetic payloads and deterministic IDs.

Gate outcome:
- Current status: PASS (checklist instantiated and populated)

## 7. Execution Gate (Fail-Closed)
Required runtime evidence per run:
- [x] Run metadata (pytest command and timestamp)
- [x] Input parameters and fixtures captured in test code
- [x] Message and callback evidence asserted in tests
- [x] Validation evidence in pytest output
- [x] Deterministic verdict and reason in report artifacts

Gate outcome:
- Current status: PENDING re-evaluation after targeted run attachment

## 8. Validation Gate (Fail-Closed)
Post-run checks:
- [ ] Clause matrix has no unresolved mandatory add/modify actions
- [x] No unmapped executed tests in this checklist scope
- [x] No ambiguous verdict fields in generated summary
- [x] Negative tests executed for callback and unknown-resource paths
- [x] Evidence artifacts retained under ORAN/docs/test-policy and ORAN/docs/coverage

Gate outcome:
- Current status: FAIL until clause matrix unresolved actions are zero

## 9. Failure Triage Gate (Fail-Closed)
Mandatory failure fields:
- [x] Failure ID format defined in verification summary when failures occur
- [x] Requirement ID linkage defined in traceability matrix
- [x] Test case linkage defined in traceability matrix
- [x] Evidence artifact references standardized in verification summary
- [x] Root cause categories defined (Spec, Code, Test, Env, Data)
- [x] Corrective action and retest requirement defined

Closure conditions:
- [ ] Fix verified by retest evidence
- [ ] Requirement impact updated for any failed case
- [ ] Regression scope re-executed when failures are present

## 10. Exception Handling
Exceptions are time-boxed and require engineering plus quality approval.
Expired exceptions automatically force fail status.

## 11. Roles and Accountability
| Activity | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Requirement curation | ORAN feature owner | ORAN technical lead | QA lead | Team |
| Test generation | Backend test engineer | QA lead | Feature owner | Team |
| Test execution | Backend test engineer | QA lead | Dev lead | Team |
| Validation sign-off | QA lead | ORAN technical lead | Feature owner | Team |
| Failure triage closure | Dev lead | QA lead | Feature owner | Team |

## 12. Artifacts and Retention
| Artifact | Location | Retention | Integrity Control |
|---|---|---|---|
| Traceability matrix | ORAN/docs/feature_traceability_map.md | Project lifetime | Git history |
| Clause coverage matrix | ORAN/docs/coverage/ts_103989_section5_clause_coverage_matrix.md | Project lifetime | Git history |
| Verification summary | ORAN/docs/coverage/ts_103989_section5_verification_run_summary.md | Project lifetime | Git history |
| Test policy report | ORAN/docs/test-policy/ts_103989_section5_test_policy_report.md | Project lifetime | Git history |

## 13. Automated Enforcement Rules
- Rule 1: Block closure when any mandatory clause has action add or modify.
- Rule 2: Block validation when required evidence artifacts are missing.
- Rule 3: Block closure when failure triage records are incomplete.
- Rule 4: Block release when Critical requirement coverage is incomplete.

## 14. Sign-off
Prepared by: GitHub Copilot dry-run workflow
Reviewed by: Pending
Approved by: Pending
Approval date: Pending

## 15. Change Log
| Version | Date | Author | Change Summary |
|---|---|---|---|
| 1.0 | 2026-07-01 | GitHub Copilot | Instantiated section-5 checklist from template and mapped ORAN-FTM requirements |
