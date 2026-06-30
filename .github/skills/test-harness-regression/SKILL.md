---
name: test-harness-regression
description: "Generate and organize unit/component/module/interface/feature/e2e tests from a commit or change summary, including memory, load, stress, and parameter-passing perspectives with regression mapping."
argument-hint: "commit hash or change summary + scope"
user-invocable: true
domain: quality-engineering
versions: ["v1"]
---

# Test Harness Regression Skill

## Purpose
Create or modify tests from a commit/change summary and organize them for targeted regression runs.

This skill operationalizes the TODO testing intent from ORAN/TODO.md (Traceability and Quality Follow-up) and expands it into a reusable workflow:
- Add unit and module-level tests for changed services/routes/models.
- Add API/interface coverage for impacted endpoints and flows.
- Add regression-oriented structure so changed files/functions map to specific test subsets.

## Use When
- User asks to add tests for a commit, PR, or plain-language change summary.
- Existing functionality changed and regression selection should be deterministic.
- Coverage must include both functional and non-functional perspectives.

## Required Inputs
- One of:
  - commit hash, or
  - diff summary, or
  - change summary by module/file/function.
- Optional:
  - risk priority (high/medium/low),
  - test budget (smoke/full),
  - target framework constraints.

## Test Perspective Matrix
Always consider these perspectives when selecting/authoring tests:
- Functional correctness: happy path and negative path.
- Parameter passing: boundary values, null/empty, malformed, type mismatch.
- Memory behavior: leaks, growth under repetition, cleanup/finalizers.
- Load behavior: steady-state moderate concurrency.
- Stress behavior: burst/spike, resource saturation, timeout behavior.
- Interface contract: request/response schema, status codes, backward compatibility.
- Module integration: service-to-service collaboration and failure propagation.
- Feature/e2e flow: user-visible end-to-end workflows.
- Fault behavior: retries, partial failures, external dependency errors.

## Specification Reference Rule
- For every new or modified test case, include an explicit specification reference in the test case itself.
- Prefer an assertion message, test name, docstring, or test metadata field that names the governing spec and section(s).
- If a test case spans multiple source sections, include all relevant section references in the same test case.
- Apply this rule to any test added or updated as part of the current change, including ORAN conformance and simulator smoke tests.

## Test Taxonomy and Structure
Prefer this hierarchy (adapt to language/project conventions):

```text
tests/
  unit/
    <module_or_class>/
  component/
    <component_or_adapter>/
  module/
    <module_name>/
  interface/
    api/
    cli/
    websocket/
  feature/
    <feature_name>/
  e2e/
    <journey_name>/
  nonfunctional/
    memory/
    load/
    stress/
    parameter/
    fault/
    concurrency/
  regression/
    impact-map.yaml
    selectors.md
```

## Regression Mapping Rules
Maintain a machine-readable map for targeted regression:
- File: tests/regression/impact-map.yaml
- Map each changed source artifact to relevant test selectors.
- Prefer stable selectors:
  - pytest markers/node ids,
  - JUnit tags/class names,
  - Playwright project/test tags.

Example mapping model:

```yaml
changed_artifacts:
  backend/app/services/a1_policy_service.py:
    tests:
      - tests/unit/services/test_a1_policy_service.py::TestValidation
      - tests/module/oran/test_service_selection_flow.py::test_policy_path
    perspectives: [functional, parameter, fault]
  backend/app/api/oran.py:
    tests:
      - tests/interface/api/test_oran_services_api.py::test_list_services
      - tests/feature/test_generate_from_selection.py::test_metadata_propagation
    perspectives: [interface, module, e2e]
```

## Execution Workflow
1. Parse change input.
- Extract changed files/functions/modules and classify risk.

2. Build impact matrix.
- For each artifact, define required test levels and perspectives.

3. Add/update tests by level.
- unit/component/module/interface/feature/e2e as applicable.

4. Add non-functional coverage.
- memory/load/stress/parameter/fault/concurrency where risk indicates.

5. Update regression assets.
- Create/update tests/regression/impact-map.yaml.
- Create/update tests/regression/selectors.md with runnable commands.

6. Validate quickly.
- Run targeted smoke subset for changed artifacts first.
- Then run broader suite if requested.

## Output Contract
Return:
- Added/updated test files.
- Updated regression map and selectors.
- Coverage summary by level and perspective.
- Gaps that need manual follow-up.

## Guardrails
- Do not overfit tests to implementation internals; focus observable behavior.
- Keep tests deterministic and fast by default; isolate heavy stress cases.
- Reuse existing fixtures/factories before adding new ones.
- Keep compatibility with existing test runner conventions in the repo.
