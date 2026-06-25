from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import oran


def test_service_selection_metadata_for_a1_p_and_a1_ei() -> None:
    app = FastAPI()
    app.include_router(oran.router, prefix="/api/oran")
    client = TestClient(app)

    policy_response = client.get("/api/oran/services/A1-P")
    ei_response = client.get("/api/oran/services/A1-EI")

    assert policy_response.status_code == 200
    assert ei_response.status_code == 200

    policy_payload = policy_response.json()
    ei_payload = ei_response.json()

    assert policy_payload["service"]["service_type"] == "A1-P"
    assert ei_payload["service"]["service_type"] == "A1-EI"
    assert "catalog_context" in policy_payload
    assert "summary" in ei_payload
