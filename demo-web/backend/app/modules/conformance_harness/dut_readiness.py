"""DUT readiness bootstrap payload for conformance harness."""


def check_dut_readiness() -> dict:
    return {
        "status": "not-ready",
        "checks": [],
        "spec_reference": "TS 103 989 section 4.2.2",
    }
