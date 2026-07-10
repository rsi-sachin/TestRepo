from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import oran


def test_section5_e2e_services_surface_ts103988_catalog_and_encoding_contracts() -> None:
    oran.a1_policy_service._policies.clear()
    oran.a1_policy_service._policy_status.clear()
    oran.a1_policy_service._notification_destinations.clear()
    oran.a1_ei_service._ei_jobs.clear()
    oran.a1_ei_service._notification_destinations.clear()

    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    client = TestClient(app)

    a1p = client.get("/api/oran/services/A1-P")
    a1ei = client.get("/api/oran/services/A1-EI")

    assert a1p.status_code == 200
    assert a1ei.status_code == 200
    assert a1p.json()["summary"]["type_definition_catalog"]["source_reference"] == "TS 103 988 section 5.2"
    assert a1ei.json()["summary"]["type_definition_catalog"]["source_reference"] == "TS 103 988 section 5.2"

    invalid_policy = client.put(
        "/api/oran/a1/policytypes/default/policies/e2e-s5-invalid-encoding",
        json={
            "scope": {
                "scope_type": "cell",
                "scope_value": "001",
                "amfRegionId": "ZZ",
            },
            "policy_statements": [{"id": "stmt-e2e", "action": "allow"}],
        },
    )

    assert invalid_policy.status_code == 400
    assert invalid_policy.headers["content-type"].startswith("application/problem+json")
