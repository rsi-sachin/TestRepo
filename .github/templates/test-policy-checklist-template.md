# Test Policy Checklist Template

Document ID: TPC-<YYYYMMDD>-<NN>
Version: 1.0
Status: Draft|Approved|Superseded
Owner: <team_or_role>
Effective Date: <YYYY-MM-DD>
Applies To: <repo/module/service>

## 1. Purpose
Define strict, auditable controls for creating, executing, validating tests, and triaging failures.

## 2. Scope
In scope:
- Test design and generation
- Test execution and evidence collection
- Test validation and compliance checks
- Test failure triage and closure

Out of scope:
- <explicit exclusions>

## 3. Normative Inputs
- Source requirements: <path_or_doc>
- Interface spec(s): <path_or_doc>
- Schema(s): <path_or_doc>
- Environment baseline: <path_or_doc>

## 4. Requirement Registry
| Requirement ID | Statement (MUST/SHALL) | Priority | Source Section | Notes |
|---|---|---|---|---|
| REQ-001 | | Critical | | |
| REQ-002 | | High | | |

## 5. Traceability Matrix
| Requirement ID | Test Case ID | Test Type | Preconditions | Observable Evidence | Pass Criteria | Negative Case Required (Y/N) |
|---|---|---|---|---|---|---|
| REQ-001 | TC-001 | Unit|Component|Integration|E2E | | | | Y |

## 6. Creation Gate (Fail-Closed)
Checklist (all MUST be true):
- [ ] Every in-scope Requirement ID is mapped to at least one test case.
- [ ] Every Critical requirement has positive and negative coverage.
- [ ] All test assumptions are explicitly listed and approved.
- [ ] Required schemas/contracts are referenced by exact version.
- [ ] Test data strategy is documented (synthetic/real/masked).

Gate outcome:
- PASS only if all checks are true.
- FAIL if any check is false.

## 7. Execution Gate (Fail-Closed)
Required runtime evidence per test run:
- [ ] Run metadata: runId, commit SHA, branch, environment, timestamp.
- [ ] Input config snapshot and parameter values.
- [ ] Protocol/message evidence (requests, responses, headers, payloads).
- [ ] Validation evidence (schema checks, assertions, comparator outputs).
- [ ] Deterministic verdict with reason code.

Gate outcome:
- PASS only if all required evidence exists and is parseable.
- FAIL if any evidence element is missing.

## 8. Validation Gate (Fail-Closed)
Post-run compliance checks:
- [ ] Requirement coverage percentage = <threshold, default 100% for Critical>.
- [ ] No unmapped executed tests.
- [ ] No ambiguous verdicts.
- [ ] Negative tests executed for all flagged requirements.
- [ ] Evidence retention policy applied.

Gate outcome:
- PASS only if compliance score >= <threshold>.
- FAIL otherwise.

## 9. Failure Triage Gate (Fail-Closed)
Mandatory fields for each failure record:
- [ ] Failure ID
- [ ] Linked Requirement ID(s)
- [ ] Linked Test Case ID
- [ ] Evidence artifact references
- [ ] Root cause category (Spec|Code|Test|Env|Data)
- [ ] Corrective action
- [ ] Retest plan and success criterion

Closure conditions:
- [ ] Fix verified by retest evidence.
- [ ] Requirement impact updated.
- [ ] Regression scope assessed and executed.

## 10. Exception Handling
Exception policy:
- Overrides are time-boxed and require dual approval.
- Every override must include risk acceptance note and expiry date.
- Expired overrides automatically fail gates.

## 11. Roles and Accountability
| Activity | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| Requirement curation | | | | |
| Test generation | | | | |
| Test execution | | | | |
| Validation sign-off | | | | |
| Failure triage closure | | | | |

## 12. Artifacts and Retention
| Artifact | Location | Retention | Integrity Control |
|---|---|---|---|
| Traceability matrix | | | |
| Run logs | | | |
| Validation report | | | |
| Failure records | | | |

## 13. Automated Enforcement Rules
Machine-enforceable checks:
- Rule 1: Block run if any in-scope Requirement ID has zero mapped test cases.
- Rule 2: Block validation if required evidence schema fails.
- Rule 3: Block closure if failure record lacks linked Requirement IDs.
- Rule 4: Block release if Critical requirement coverage is below threshold.

## 14. Sign-off
Prepared by: <name/role>
Reviewed by: <name/role>
Approved by: <name/role>
Approval date: <YYYY-MM-DD>

## 15. Change Log
| Version | Date | Author | Change Summary |
|---|---|---|---|
| 1.0 | <YYYY-MM-DD> | | Initial template |
