from __future__ import annotations

from types import SimpleNamespace

from townlet.world.events import EventDispatcher
from townlet.world.rng import RngStreamManager
from townlet.world.systems import SystemContext, economy


def _make_context(state: object) -> SystemContext:
    return SystemContext(
        state=state,  # type: ignore[arg-type]
        rng=RngStreamManager.from_seed(321),
        events=EventDispatcher(),
    )


def test_step_updates_basket_metrics() -> None:
    calls: list[str] = []

    class DummyService:
        def update_basket_metrics(self) -> None:
            calls.append("update")

    state = SimpleNamespace(_economy_service=DummyService())

    economy.step(_make_context(state))

    assert calls == ["update"]


def test_step_falls_back_to_legacy() -> None:
    calls: list[str] = []

    class LegacyState:
        def __init__(self) -> None:
            self._economy_service = None

        def _update_basket_metrics(self) -> None:
            calls.append("legacy")

    state = LegacyState()

    economy.step(_make_context(state))

    assert calls == ["legacy"]
