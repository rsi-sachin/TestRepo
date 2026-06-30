from app.modules.e2_interface.service import E2InterfaceService


def test_e2_interface_smoke_health():
    service = E2InterfaceService()
    response = service.health()
    assert response["module"] == "e2_interface"
    assert response["status"] == "stub"
