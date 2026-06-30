"""Near-RT RIC simulator skeleton."""


class NearRtRicSimulator:
    def __init__(self) -> None:
        self.mode = "stub"

    def status(self) -> dict:
        return {"module": "near_rt_ric_simulator", "mode": self.mode}
