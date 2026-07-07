# TS 103 983 Section 6 Protocol Message Evidence

Run ID: `ts103983-section6-20260707113814`
Source document: `ORAN/docs/ts_103983v040000p.pdf`
Scope: Section 6 signalling procedures (policy and EI)

## Procedure Coverage Signals

- Policy type status query procedure is exercised via interface API checks in `tests/interface/api/test_oran_a1_policy_api.py`.
- Policy type status notify procedure is exercised with callback contract assertions in `tests/interface/api/test_oran_a1_policy_api.py`.
- EI type status query procedure is exercised via interface API checks in `tests/interface/api/test_oran_a1_ei_api.py`.
- EI type status notify procedure is exercised with callback contract assertions in `tests/interface/api/test_oran_a1_ei_api.py`.
- Existing policy lifecycle/status and EI job/status/result procedures are exercised by conformance suites:
  - `tests/conformance/test_a1_policy_conformance_4_2_1.py`
  - `tests/conformance/test_a1_policy_conformance_4_2_2.py`
  - `tests/conformance/test_ei_job_operations.py`
  - `tests/conformance/test_execution_evidence.py`
  - `tests/conformance/test_simulator_capabilities.py`

## Artifact Links

- JUnit XML: `ORAN/docs/coverage/evidence/ts103983-section6-20260707113814/pytest_junit.xml`
- Run config snapshot: `ORAN/docs/coverage/evidence/ts103983-section6-20260707113814/run_config_snapshot.json`
