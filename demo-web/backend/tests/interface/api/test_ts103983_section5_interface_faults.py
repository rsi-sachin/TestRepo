from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import oran


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    return TestClient(app)


def test_section5_interface_policy_missing_type_maps_to_404_problem_details() -> None:
    client = _client()

    response = client.put(
        "/api/oran/a1/policytypes/unknown/policies/p1",
        json={
            "scope": {"scope_type": "cell", "scope_value": "001"},
            "policy_statements": [{"id": "stmt-1", "action": "allow"}],
        },
    )

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["detail"]["title"] == "Policy Type Not Found"


def test_section5_interface_ei_type_mismatch_maps_to_400_problem_details() -> None:
    client = _client()

    response = client.put(
        "/api/oran/a1/eitypes/default/eijobs/ei-type-mismatch",
        json={
            "eiTypeId": "alt",
            "jobDefinition": {"workload": "x"},
            "jobResultUri": "https://example.com/result",
        },
    )

    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["detail"]["title"] == "Invalid EI Job Request"
