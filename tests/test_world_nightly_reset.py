from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world.agents.nightly_reset import NightlyResetService
from townlet.world.grid import AgentSnapshot, WorldState


def _setup_world() -> WorldState:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.agents.clear()
    world.tick = 0
    return world


def test_apply_nightly_reset_returns_agents_home() -> None:
    world = _setup_world()
    snapshot = AgentSnapshot(
        agent_id="alice",
        position=(5, 5),
        needs={"hunger": 0.2, "hygiene": 0.3, "energy": 0.4},
        wallet=1.0,
        home_position=(5, 5),
    )
    world.agents[snapshot.agent_id] = snapshot
    world._assign_job_if_missing(snapshot)
    world._sync_agent_spawn(snapshot)

    snapshot.position = (6, 6)
    snapshot.needs["hunger"] = 0.1
    snapshot.needs["hygiene"] = 0.1
    snapshot.needs["energy"] = 0.1

    world.tick = 1439
    world.drain_events()

    world.apply_nightly_reset()
    events = world.drain_events()

    assert snapshot.position == snapshot.home_position
    assert snapshot.needs["hunger"] >= 0.5
    assert snapshot.needs["hygiene"] >= 0.5
    assert snapshot.needs["energy"] >= 0.5
    assert snapshot.shift_state == "pre_shift"
    assert any(event.get("event") == "agent_nightly_reset" for event in events)


def test_apply_nightly_reset_calls_service(monkeypatch: pytest.MonkeyPatch) -> None:
    world = _setup_world()
    captured: list[int] = []

    def fake_apply(self: NightlyResetService, tick: int) -> list[str]:
        captured.append(tick)
        return ["delegated"]

    monkeypatch.setattr(NightlyResetService, "apply", fake_apply)
    world.tick = 99

    result = world.apply_nightly_reset()

    assert captured == [99]
    assert result == ["delegated"]


def test_simulation_loop_triggers_nightly_reset() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.observations_config.hybrid.time_ticks_per_day = 3
    loop = SimulationLoop(config)
    loop.world.agents.clear()

    snapshot = AgentSnapshot(
        agent_id="alice",
        position=(4, 4),
        needs={"hunger": 0.2, "hygiene": 0.7, "energy": 0.7},
        wallet=0.0,
        home_position=(4, 4),
    )
    loop.world.agents[snapshot.agent_id] = snapshot
    loop.world._assign_job_if_missing(snapshot)
    loop.world._sync_agent_spawn(snapshot)

    snapshot.position = (7, 7)
    snapshot.needs["hunger"] = 0.2

    for _ in range(3):
        loop.step()

    assert snapshot.position == snapshot.home_position
    assert snapshot.needs["hunger"] >= 0.5
