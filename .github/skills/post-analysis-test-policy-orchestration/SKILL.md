---
name: post-analysis-test-policy-orchestration
description: "Launch post-analysis test planning and gap closure workflow. Uses Test Policy Orchestrator to derive required tests from recent analysis/commits, and enforces clause-by-clause coverage matrix + missing test creation for test specifications."
argument-hint: "analysis artifact path or commit/change summary + source document path"
user-invocable: true
domain: quality-engineering
versions: ["v2"]
configuration:
  output-path-convention:
    test_policy_orchestrator_report: "ORAN/docs/test-policy/<document_id>_<section_scope>_test_policy_report.md"
    clause_coverage_matrix: "ORAN/docs/coverage/<document_id>_<section_scope>_clause_coverage_matrix.md"
    verification_run_summary: "ORAN/docs/coverage/<document_id>_<section_scope>_verification_run_summary.md"
  completion-gate:
    fail-closed: true
    gates: ["creation", "execution", "validation", "triage"]
    criteria:
      - "No clause entries with action=add remain unless matching tests were created in this run"
      - "No clause entries with action=modify remain unless matching tests were updated in this run"
      - "Residual uncovered clauses must be explicitly listed under residual_risks with follow-up owners"
      - "Execution evidence must include run metadata fields: runId, commit SHA, branch, environment"
      - "Execution evidence must include config snapshot and protocol/message evidence artifact references"
      - "Completion gate is PASS only when all fail-closed gates pass"
  optional-modes:
    auto-commit:
      enabled-by-default: false
      allowed-values: ["off", "on"]
      commit-message-template: "tests: close clause coverage gaps for <document_id> <section_scope>"
orchestrates:
  - document-cross-reference-analysis
  - document-analysis-a1tp
  - test-harness-regression
agent-requirements:
  mandatory-agent: "Test Policy Orchestrator"
---

# Post-Analysis Test Policy Orchestration Skill

## Purpose
Run immediately after technical document analysis to convert analysis output into concrete test requirements and implementation-ready test work.

This workflow ensures:
- Recent code and test impact is derived from analysis outputs and/or commit diffs.
- The `Test Policy Orchestrator` agent is used to identify required tests.
- If the analyzed document is a test specification, a clause-by-clause coverage matrix is produced and missing tests are added for uncovered clauses.
- Decisions are persisted as auditable artifacts using normalized document and scope placeholders.

## Use When
- A technical analysis skill has completed and implementation/testing should continue.
- User asks to derive tests from recent analysis-driven code changes.
- The source doc is a test specification.

## Required Inputs
- At least one of:
  - analysis artifact path (for example, `<docs_root>/<analysis_artifact>.md`), or
  - commit hash/change summary generated after analysis.
- Source document path and section scope if available.

## Detection Rules

Treat document as a **test specification** when any of these are true:
- File name or reference includes `test specification`, `conformance`, `interoperability`, `validation`, or `compliance`.
- Analysis output contains clause/test-case style headings (`5.x`, `6.x`, `test scenarios`, `test methodology`, `expected result`).
- Source references primarily target conformance/interoperability test clauses.

## Mandatory Workflow

1. Validate prerequisites.
- Confirm technical analysis has completed and produced trace-mapped output.
- Confirm `ORAN/docs/feature_traceability_map.md` is available.

2. Build recent change input.
- Collect changed files/functions from analysis output and/or git diff.
- Produce concise change summary for test planning.

3. Invoke `Test Policy Orchestrator` agent (mandatory).
- Call `runSubagent` with exact agent name: `Test Policy Orchestrator`.
- Prompt must include:
  - recent change summary,
  - impacted modules/files,
  - required test perspectives (unit/component/module/interface/feature/e2e + memory/load/stress/parameter/fault),
  - expected output format (test inventory + priorities + gaps).

4. Generate/refresh required test plan artifacts.
- Create or update a test recommendation plan tied to trace IDs.
- Include mapping from changed code scope to required test suites.
- Persist artifacts using the output path convention in this skill configuration.

5. Instantiate or refresh policy checklist (mandatory).
- Ensure a checklist instance exists (do not rely on template-only state).
- Checklist must include requirement registry, traceability matrix, and explicit gate statuses.

6. If source is a test specification, enforce clause coverage.
- Produce a clause-by-clause coverage matrix:
  - clause id,
  - current coverage (existing tests),
  - missing coverage,
  - planned/new tests.
- Add missing tests for uncovered clauses using existing repo test conventions.
- Clause actions are constrained to: `none|add|modify`.

7. Validate and report.
- Run targeted tests for touched files first.
- Report added tests, modified tests, uncovered residual gaps, and next actions.
- Persist execution evidence artifacts (minimum):
  - run metadata (`runId`, `commit SHA`, `branch`, `environment`),
  - config snapshot artifact,
  - protocol/message evidence artifact,
  - test execution artifact (for example junit/xml or equivalent).
- Apply fail-closed completion gate before marking workflow complete.

8. Optional auto-commit mode.
- If `auto-commit=on` is explicitly provided by user/request context:
  - stage only files created/updated by this workflow,
  - commit with configured template,
  - include generated artifact paths and clause gap closure summary in commit body.
- If `auto-commit=off` (default), do not create a commit.

## Required Outputs

- `test_policy_orchestrator_report`: Required tests from agent output.
- `clause_coverage_matrix`: Mandatory when source is a test specification.
- `missing_tests_added`: Explicit list of new/updated tests.
- `verification_run_summary`: Targeted execution result.
- `residual_risks`: Any remaining uncovered clauses or unimplemented test perspectives.
- `artifact_paths`: Paths used for persisted report/matrix/verification artifacts.
- `completion_gate_status`: `pass|fail` with reason when fail-closed criteria block completion.
- `gate_statuses`: Explicit per-gate outcome (`creation|execution|validation|triage`).

## Output Format Contract

```yaml
test_policy_orchestrator_report:
  agent: "Test Policy Orchestrator"
  required_tests: []
  priorities: []

clause_coverage_matrix:
  source_document: "<source_document_path>"
  clauses:
    - clause: "<clause_id>"
      covered_by: ["<test_path>::<test_name>"]
      gaps: []
      action: "none|add|modify"

missing_tests_added:
  - path: "<workspace_test_path>"
    reason: "Uncovered or partial clause coverage"

verification_run_summary:
  command: "pytest ..."
  result: "pass|fail|partial"
  metadata:
    run_id: "<run_id>"
    commit_sha: "<commit_sha>"
    branch: "<branch_name>"
    environment: "<environment_descriptor>"
  evidence_artifacts:
    config_snapshot: "<path>"
    protocol_message_evidence: "<path>"
    execution_log: "<path>"

artifact_paths:
  test_policy_orchestrator_report: "ORAN/docs/test-policy/<document_id>_<section_scope>_test_policy_report.md"
  clause_coverage_matrix: "ORAN/docs/coverage/<document_id>_<section_scope>_clause_coverage_matrix.md"
  verification_run_summary: "ORAN/docs/coverage/<document_id>_<section_scope>_verification_run_summary.md"

gate_statuses:
  creation: "pass|fail"
  execution: "pass|fail"
  validation: "pass|fail"
  triage: "pass|fail"

completion_gate_status:
  status: "pass|fail"
  reason: "Populate when fail"

residual_risks:
  - "Any remaining uncovered clauses or test perspectives"
```

## Guardrails

- Always use the exact agent name `Test Policy Orchestrator`.
- Do not skip clause matrix generation when source is a test specification.
- Do not mark completion if uncovered clauses remain without explicit follow-up.
- Enforce fail-closed completion gate before finishing workflow.
- Keep all generated test work aligned to `ORAN/docs/feature_traceability_map.md` and mapped trace IDs.
- Do not report `completion_gate_status: pass` unless all four gates are pass.
- If clause actions are all `none` but execution evidence artifacts are missing, keep status fail.
- Avoid duplicating contradictory status fields in output artifacts.

## Output Artifact Path Convention

Use normalized file-safe placeholders:
- `document_id`: lowercase identifier derived from source document
- `section_scope`: compact scope derived from analyzed clause/range

Required artifact destinations:
- test policy report: `ORAN/docs/test-policy/<document_id>_<section_scope>_test_policy_report.md`
- clause coverage matrix: `ORAN/docs/coverage/<document_id>_<section_scope>_clause_coverage_matrix.md`
- verification summary: `ORAN/docs/coverage/<document_id>_<section_scope>_verification_run_summary.md`
