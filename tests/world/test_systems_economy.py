from __future__ import annotations

from townlet.world.systems import economy


class FakeEconomyService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple, dict]] = []

    def update_basket_metrics(self) -> None:
        self.calls.append(("update_basket_metrics", (), {}))

    def restock_economy(self) -> None:
        self.calls.append(("restock_economy", (), {}))

    def utility_online(self, utility: str) -> bool:
        self.calls.append(("utility_online", (utility,), {}))
        return utility == "power"

    def economy_settings(self) -> dict[str, float]:
        self.calls.append(("economy_settings", (), {}))
        return {"price": 1.0}

    def active_price_spikes(self) -> dict[str, dict[str, object]]:
        self.calls.append(("active_price_spikes", (), {}))
        return {"event": {}}

    def utility_snapshot(self) -> dict[str, bool]:
        self.calls.append(("utility_snapshot", (), {}))
        return {"power": True}


def test_economy_wrappers_delegate() -> None:
    service = FakeEconomyService()

    economy.update_basket_metrics(service)
    economy.restock(service)
    assert economy.utility_online(service, "power") is True
    assert economy.economy_settings(service) == {"price": 1.0}
    assert economy.active_price_spikes(service) == {"event": {}}
    assert economy.utility_snapshot(service) == {"power": True}

    names = [name for name, _, _ in service.calls]
    assert names == [
        "update_basket_metrics",
        "restock_economy",
        "utility_online",
        "economy_settings",
        "active_price_spikes",
        "utility_snapshot",
    ]
