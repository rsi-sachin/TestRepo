import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "backend"))

from app.modules.simulators.near_rt_ric.simulator import NearRtRicSimulator


SPEC_REFERENCE = "ORAN/Feature_Plan.md sections 2, 3, and 4"


def test_near_rt_ric_simulator_smoke_status():
    simulator = NearRtRicSimulator()

    payload = simulator.status()

    assert payload["module"] == "near_rt_ric_simulator", SPEC_REFERENCE
    assert payload["mode"] == "stub", SPEC_REFERENCE