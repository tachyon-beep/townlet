from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config.loader import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.observations.builder import ObservationBuilder


@pytest.fixture()
def short_loop() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    loop.world.agents.clear()
    return loop


def test_telemetry_publish_uses_adapter(short_loop: SimulationLoop) -> None:
    loop = short_loop
    telemetry = loop.telemetry
    telemetry._ingest_loop_tick(  # type: ignore[attr-defined]
        tick=loop.tick,
        world=loop.world,
        rewards={},
        events=[],
        policy_snapshot={},
        kpi_history=False,
        reward_breakdown={},
        stability_inputs={},
        perturbations={},
        policy_identity={},
        possessed_agents=[],
        social_events=[],
        runtime_variant="facade",
    )

    assert telemetry.latest_queue_metrics() is not None
    assert telemetry._latest_relationship_snapshot is not None  # type: ignore[attr-defined]
    assert telemetry._latest_relationship_summary is not None  # type: ignore[attr-defined]


def test_policy_observations_via_adapter(short_loop: SimulationLoop) -> None:
    loop = short_loop
    builder = ObservationBuilder(loop.config)
    batch = builder.build_batch(loop.world_adapter, terminated={})
    assert isinstance(batch, dict)
    loop.close()
