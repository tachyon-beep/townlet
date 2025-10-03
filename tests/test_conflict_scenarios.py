from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import random

import pytest

from townlet.config.loader import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.policy.scenario_utils import apply_scenario
from townlet.world.queue_manager import QueueManager


def _run_scenario(config_path: str, ticks: int) -> SimulationLoop:
    config = load_config(Path(config_path))
    loop = SimulationLoop(config)
    scenario = getattr(config, "scenario", None)
    assert scenario is not None, "scenario config required for test"
    apply_scenario(loop, scenario)
    # Disable transport IO for deterministic tests
    loop.telemetry._transport_client = SimpleNamespace(  # type: ignore[attr-defined]
        send=lambda payload: None,
        close=lambda: None,
    )
    for _ in range(ticks):
        loop.step()
    return loop


def test_queue_conflict_scenario_produces_alerts() -> None:
    loop = _run_scenario("configs/scenarios/queue_conflict.yaml", ticks=80)
    conflict = loop.telemetry.latest_conflict_snapshot()
    queues = conflict.get("queues", {})
    assert queues.get("ghost_step_events", 0) > 0
    history = conflict.get("queue_history", [])
    assert history
    latest = history[-1]
    assert {"tick", "delta", "totals"} <= set(latest)
    alerts = loop.telemetry.latest_stability_alerts()
    assert alerts
    assert any(
        alert in {"queue_fairness_pressure", "rivalry_spike"} for alert in alerts
    )


def test_rivalry_decay_scenario_tracks_events() -> None:
    loop = _run_scenario("configs/scenarios/rivalry_decay.yaml", ticks=60)
    conflict = loop.telemetry.latest_conflict_snapshot()
    rivalry_events = conflict.get("rivalry_events", [])
    assert rivalry_events
    intensities = [event.get("intensity", 0.0) for event in rivalry_events]
    assert any(value > 0 for value in intensities)
    alerts = loop.telemetry.latest_stability_alerts()
    assert "rivalry_spike" in alerts


@pytest.mark.parametrize("seed", [13, 29, 47])
def test_queue_manager_randomised_regression(seed: int) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    manager = QueueManager(config)
    object_id = "kiosk"
    agents = ["a", "b", "c", "d"]
    rng = random.Random(seed)
    active_tracker: dict[str, str | None] = {object_id: None}

    for tick in range(50):
        manager.on_tick(tick)
        agent = rng.choice(agents)
        action = rng.random()
        if action < 0.5:
            granted = manager.request_access(object_id, agent, tick)
            snapshot = manager.queue_snapshot(object_id)
            assert snapshot.count(agent) <= 1
            if granted:
                active_tracker[object_id] = agent
        elif action < 0.75:
            manager.record_blocked_attempt(object_id)
        else:
            holder = manager.active_agent(object_id)
            if holder is not None:
                manager.release(object_id, holder, tick, success=rng.random() < 0.5)
                active_tracker[object_id] = None
        metrics = manager.metrics()
        for value in metrics.values():
            assert value >= 0

    final_queue = manager.queue_snapshot(object_id)
    assert len(final_queue) == len(set(final_queue))
