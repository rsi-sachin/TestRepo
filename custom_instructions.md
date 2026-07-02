# Custom Instructions

## Skill Invocation Rules

- When the user prompt matches or starts with:
  - "Use Test Harness skill to add unit/component/module/interface/feature and e2e tests for a given commit or change summary"
- Invoke skill: `test-harness-regression`.
- Treat commit hash, diff snippet, or plain-language summary as valid change input.
- Ensure test design explicitly covers these perspectives when applicable:
  - memory
  - load
  - stress
  - parameter passing
  - fault/error handling
  - interface contract compatibility
- Ensure tests are organized for regression selection and update:
  - `tests/regression/impact-map.yaml`
  - `tests/regression/selectors.md`

## Enforcement Note
- Do not skip skill invocation for matching prompts; use `test-harness-regression` first, then implement code changes.

## Branch Context Rules

- When the current git branch is `feature/ORAN_MVP_Py3_13` or matches `feature/ORAN_MVP_*`, do not use `demo-tool/TTS_TODO.md` for planning, task selection, prioritization, or status tracking.
- On `feature/ORAN_MVP_*` branches, treat `ORAN/TODO.md` as the authoritative TODO source unless the user explicitly asks to use `demo-tool/TTS_TODO.md`.

## ORAN Planning Reference

- Always refer to `ORAN/Feature_Plan.md` first for ORAN-related planning, scoping, and implementation decisions.
- Do not rely on alternate ORAN planning notes when `ORAN/Feature_Plan.md` is available.

## ORAN Test Case References

- For every new ORAN test case created or modified, include an explicit specification reference in the test case itself.
- Prefer a `spec_reference` field in the returned payload or test metadata, and keep it aligned with the exact source section(s).
- If a test case spans multiple source sections, include all relevant section references in the test name, metadata, or assertions.

## Pull Request URL Requests

- When the user asks to create or share a pull request URL, always also provide:
  - a proposed PR title
  - a concise PR summary suitable for the PR description or opening note
