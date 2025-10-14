from __future__ import annotations

from types import SimpleNamespace

from townlet.world.events import EventDispatcher
from townlet.world.rng import RngStreamManager
from townlet.world.state import WorldState
from townlet.world.systems import SystemContext, default_systems


def _make_world() -> WorldState:
    return WorldState(config=SimpleNamespace(name="test"))


def test_default_systems_iterable() -> None:
    world = _make_world()
    ctx = SystemContext(
        state=world,
        rng=RngStreamManager.from_seed(123),
        events=EventDispatcher(),
    )

    systems = default_systems()
    assert len(systems) == 6
    for system in systems:
        system(ctx)  # placeholders are no-ops for now
