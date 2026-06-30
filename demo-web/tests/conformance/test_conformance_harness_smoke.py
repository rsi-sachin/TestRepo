from app.modules.conformance_harness.dut_readiness import check_dut_readiness
from app.modules.conformance_harness.evidence_collector import collect_execution_evidence
from app.modules.conformance_harness.simulator_verifier import verify_simulator_capability


def test_conformance_harness_smoke_functions_return_stub_payloads():
    readiness = check_dut_readiness()
    capability = verify_simulator_capability()
    evidence = collect_execution_evidence()

    assert readiness["status"] == "stub"
    assert capability["status"] == "stub"
    assert evidence["status"] == "stub"
