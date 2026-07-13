"""
Conformance tests: TS 103 988 section 5 (generic aspects and common data types).
"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import oran


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    return TestClient(app)


def test_section5_clause5_service_summaries_expose_type_catalogs() -> None:
    client = _client()

    a1p = client.get("/api/oran/services/A1-P")
    a1ei = client.get("/api/oran/services/A1-EI")

    assert a1p.status_code == 200
    assert a1ei.status_code == 200

    a1p_catalog = a1p.json()["summary"]["type_definition_catalog"]
    a1ei_catalog = a1ei.json()["summary"]["type_definition_catalog"]

    assert a1p_catalog["source_reference"] == "TS 103 988 section 5.2"
    assert a1ei_catalog["source_reference"] == "TS 103 988 section 5.2"
    assert a1p_catalog["types"]["common"] == "1.0.0"
    assert a1ei_catalog["types"]["UEGeoandVel"] == "3.0.1"


def test_section5_clause5_1_rejects_invalid_policy_encoding_attribute() -> None:
    client = _client()

    response = client.put(
        "/api/oran/a1/policytypes/default/policies/section5-encoding-bad",
        json={
            "scope": {
                "scope_type": "cell",
                "scope_value": "001",
                "amfRegionId": "ZZ",
            },
            "policy_statements": [{"id": "stmt-bad-encoding", "action": "allow"}],
        },
    )

    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/problem+json")
    assert "amfRegionId" in response.json()["detail"]["detail"]


def test_section5_clause5_2_uses_type_definition_status_enrichment_path() -> None:
    client = _client()

    response = client.get(
        "/api/oran/resolve-specs",
        params=[("selected", "TS_103_989"), ("selected", "TS_103_988")],
    )

    assert response.status_code == 200
    payload = response.json()
    assert "specs" in payload
    assert any(spec["spec_type"] == "TS_103_988" for spec in payload["specs"])
