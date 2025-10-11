from __future__ import annotations

from pathlib import Path

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop, TickArtifacts
from townlet.world.dto.observation import DTO_SCHEMA_VERSION, ObservationEnvelope


def test_simulation_loop_modular_smoke_emits_console_events() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)

    loop.telemetry.queue_console_command({"name": "snapshot"})

    first = loop.step()
    second = loop.step()

    for artifact in (first, second):
        assert isinstance(artifact, TickArtifacts)
        assert isinstance(artifact.envelope, ObservationEnvelope)
        assert artifact.envelope.schema_version == DTO_SCHEMA_VERSION
        assert isinstance(artifact.rewards, dict)

    results = loop.telemetry.latest_console_results()
    assert results, "console result expected after snapshot command"
    latest = results[-1]
    assert latest["status"] in {"ok", "error"}
    assert isinstance(latest.get("result"), dict)
    tick_value = latest.get("tick")
    assert isinstance(tick_value, int)
    assert 0 < tick_value <= loop.tick
