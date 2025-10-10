from __future__ import annotations

from types import SimpleNamespace

from townlet.world.events import EventDispatcher
from townlet.world.rng import RngStreamManager
from townlet.world.systems import SystemContext, relationships


def _make_context(state: object) -> SystemContext:
    return SystemContext(
        state=state,  # type: ignore[arg-type]
        rng=RngStreamManager.from_seed(111),
        events=EventDispatcher(),
    )


def test_step_invokes_relationship_decay() -> None:
    called: list[str] = []

    class DummyRelationships:
        def decay(self) -> None:
            called.append("decay")

    state = SimpleNamespace(_relationships=DummyRelationships())

    relationships.step(_make_context(state))

    assert called == ["decay"]


def test_step_falls_back_to_legacy() -> None:
    called: list[str] = []

    class LegacyState:
        def __init__(self) -> None:
            self._relationships = None

        def relationship_decay(self) -> None:
            called.append("legacy")

    relationships.step(_make_context(LegacyState()))

    assert called == ["legacy"]
