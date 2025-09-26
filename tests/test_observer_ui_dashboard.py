from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.console.handlers import create_console_router
from townlet_ui.dashboard import render_snapshot, run_dashboard, _build_map_panel
from townlet_ui.telemetry import TelemetryClient


def make_loop() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    world = loop.world
    if not world.agents:
        from townlet.world.grid import AgentSnapshot

        world.agents["alice"] = AgentSnapshot(
            agent_id="alice",
            position=(0, 0),
            needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
            wallet=1.0,
        )
        world.agents["bob"] = AgentSnapshot(
            agent_id="bob",
            position=(1, 0),
            needs={"hunger": 0.6, "hygiene": 0.4, "energy": 0.5},
            wallet=1.2,
        )
        world._assign_jobs_to_agents()  # type: ignore[attr-defined]
        world.update_relationship("alice", "bob", trust=0.2, familiarity=0.1)
    return loop


def test_render_snapshot_produces_panels() -> None:
    loop = make_loop()
    router = create_console_router(loop.telemetry, loop.world)
    for _ in range(3):
        loop.step()
    loop.world.update_relationship("alice", "bob", trust=0.1, familiarity=0.05, rivalry=0.02)
    loop.step()
    snapshot = TelemetryClient().from_console(router)

    panels = list(render_snapshot(snapshot, tick=loop.tick, refreshed="00:00:00"))
    assert panels
    panel_titles = [getattr(p, "title", "") for p in panels]
    assert any((title or "").startswith("Employment") for title in panel_titles)
    assert any((title or "").startswith("Conflict") for title in panel_titles)
    assert any((title or "").startswith("Narrations") for title in panel_titles)
    assert any((title or "").startswith("Relationships") for title in panel_titles)
    assert any((title or "").startswith("Relationship Updates") for title in panel_titles)
    assert any("Legend" in (title or "") for title in panel_titles)


def test_run_dashboard_advances_loop(monkeypatch: pytest.MonkeyPatch) -> None:
    loop = make_loop()
    calls = {"sleep": 0}

    def fake_sleep(_seconds: float) -> None:
        calls["sleep"] += 1

    monkeypatch.setattr("townlet_ui.dashboard.time.sleep", fake_sleep)
    run_dashboard(loop, refresh_interval=0, max_ticks=2)
    assert calls["sleep"] == 2


def test_build_map_panel_produces_table() -> None:
    loop = make_loop()
    router = create_console_router(loop.telemetry, loop.world)
    for _ in range(2):
        loop.step()
    snapshot = TelemetryClient().from_console(router)
    obs_batch = loop.observations.build_batch(loop.world, terminated={})
    panel = _build_map_panel(loop, snapshot, obs_batch, focus_agent=None)
    assert panel is not None
    assert "Local Map" in (panel.title or "")
