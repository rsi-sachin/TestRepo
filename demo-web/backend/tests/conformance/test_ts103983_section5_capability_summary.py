"""
Conformance tests: TS 103 983 section 5 top-level A1 capability summary.
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import oran


def test_section_5_service_capabilities_include_explicit_a1_ml_scope_decision() -> None:
    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    client = TestClient(app)

    a1p = client.get("/api/oran/services/A1-P")
    a1ei = client.get("/api/oran/services/A1-EI")

    assert a1p.status_code == 200
    assert a1ei.status_code == 200

    a1p_ml = a1p.json()["summary"]["a1_ml_support"]
    a1ei_ml = a1ei.json()["summary"]["a1_ml_support"]

    assert a1p_ml["status"] == "out_of_scope"
    assert a1ei_ml["status"] == "out_of_scope"
    assert a1p_ml["reference"] == "TS 103 983 section 5"
    assert a1ei_ml["reference"] == "TS 103 983 section 5"
