from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import oran


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    return TestClient(app)


def test_section5_interface_policy_invalid_encoding_maps_to_400_problem_details() -> None:
    client = _client()

    response = client.put(
        "/api/oran/a1/policytypes/default/policies/fault-invalid-encoding",
        json={
            "scope": {
                "scope_type": "cell",
                "scope_value": "001",
                "amfRegionId": "ZZ",
            },
            "policy_statements": [{"id": "stmt-fault", "action": "allow"}],
        },
    )

    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["detail"]["title"] == "Invalid Policy Request"


def test_section5_interface_ei_invalid_identifier_maps_to_400_problem_details() -> None:
    client = _client()

    response = client.put(
        "/api/oran/a1/eitypes/default/eijobs/fault-invalid-eitype",
        json={
            "eiTypeId": "default bad",
            "jobDefinition": {"workload": "x"},
            "jobResultUri": "https://example.com/result",
        },
    )

    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["detail"]["title"] == "Invalid EI Job Request"
