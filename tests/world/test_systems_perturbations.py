from __future__ import annotations

from townlet.world.systems import perturbations


class FakePerturbationService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []

    def apply_price_spike(self, event_id: str, *, magnitude: float, targets=None) -> None:
        self.calls.append(("apply_price_spike", (event_id,), {"magnitude": magnitude, "targets": targets}))

    def clear_price_spike(self, event_id: str) -> None:
        self.calls.append(("clear_price_spike", (event_id,), {}))

    def apply_utility_outage(self, event_id: str, utility: str) -> None:
        self.calls.append(("apply_utility_outage", (event_id, utility), {}))

    def clear_utility_outage(self, event_id: str, utility: str) -> None:
        self.calls.append(("clear_utility_outage", (event_id, utility), {}))

    def apply_arranged_meet(self, *, location=None, targets=None) -> None:
        self.calls.append(("apply_arranged_meet", (), {"location": location, "targets": targets}))


def test_perturbation_wrappers_delegate() -> None:
    service = FakePerturbationService()

    perturbations.apply_price_spike(service, "spike", magnitude=2.0, targets=["alice"])
    perturbations.clear_price_spike(service, "spike")
    perturbations.apply_utility_outage(service, "outage", "power")
    perturbations.clear_utility_outage(service, "outage", "power")
    perturbations.apply_arranged_meet(service, location="park", targets=["alice"])

    names = [name for name, _, _ in service.calls]
    assert names == [
        "apply_price_spike",
        "clear_price_spike",
        "apply_utility_outage",
        "clear_utility_outage",
        "apply_arranged_meet",
    ]
