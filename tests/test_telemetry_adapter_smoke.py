from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config.loader import load_config
from townlet.core.sim_loop import SimulationLoop


@pytest.fixture()
def short_loop() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    loop.world.agents.clear()
    return loop


def test_telemetry_publish_uses_adapter(short_loop: SimulationLoop) -> None:
    loop = short_loop
    loop.run_for_ticks(1)
    telemetry = loop.telemetry
    adapter = loop.world_adapter

    telemetry.emit_event(
        "loop.tick",
        {
            "tick": loop.tick,
            "world": adapter,
            "observations": {},
            "rewards": {},
            "events": [],
            "policy_snapshot": {},
            "kpi_history": False,
            "reward_breakdown": {},
            "stability_inputs": {},
            "perturbations": {},
            "policy_identity": {},
            "possessed_agents": [],
            "social_events": [],
        },
    )

    assert telemetry._latest_queue_metrics is not None  # type: ignore[attr-defined]
    assert telemetry._latest_relationship_snapshot is not None  # type: ignore[attr-defined]
    assert telemetry._latest_relationship_summary is not None  # type: ignore[attr-defined]


def test_policy_observations_via_adapter(short_loop: SimulationLoop) -> None:
    loop = short_loop
    builder = loop.observations
    batch = builder.build_batch(loop.world_adapter, terminated={})
    assert isinstance(batch, dict)
    loop.close()
