from app.modules.o1_interface.service import O1InterfaceService


def test_o1_interface_smoke_health():
    service = O1InterfaceService()
    response = service.health()
    assert response["module"] == "o1_interface"
    assert response["status"] == "stub"
