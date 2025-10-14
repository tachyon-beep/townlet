from __future__ import annotations

from pathlib import Path

import pytest

from townlet.config.loader import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world.observations.service import WorldObservationService


@pytest.fixture()
def short_loop() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    loop.world.agents.clear()
    return loop


def test_telemetry_publish_uses_adapter(short_loop: SimulationLoop) -> None:
    loop = short_loop
    telemetry = loop.telemetry
    loop.step()

    assert telemetry.latest_queue_metrics() is not None
    assert telemetry._latest_relationship_snapshot is not None  # type: ignore[attr-defined]
    assert telemetry._latest_relationship_summary is not None  # type: ignore[attr-defined]


def test_policy_observations_via_adapter(short_loop: SimulationLoop) -> None:
    loop = short_loop
    service = WorldObservationService(config=loop.config)
    batch = service.build_batch(loop.world_adapter, terminated={})
    assert isinstance(batch, dict)
    loop.close()
