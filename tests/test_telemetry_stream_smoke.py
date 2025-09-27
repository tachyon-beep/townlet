from __future__ import annotations

import json
from pathlib import Path

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet_ui.telemetry import TelemetryClient


def _ensure_agents(loop: SimulationLoop) -> None:
    world = loop.world
    if world.agents:
        return
    from townlet.world.grid import AgentSnapshot

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    world._assign_jobs_to_agents()  # type: ignore[attr-defined]


def test_file_transport_stream_smoke(tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.telemetry.transport.type = "file"
    config.telemetry.transport.file_path = tmp_path / "telemetry.jsonl"
    config.telemetry.transport.buffer.max_batch_size = 1
    config.telemetry.transport.buffer.flush_interval_ticks = 1

    loop = SimulationLoop(config)
    _ensure_agents(loop)

    for _ in range(3):
        loop.step()

    loop.telemetry.close()

    stream_path = config.telemetry.transport.file_path
    assert stream_path.exists()
    lines = [line for line in stream_path.read_text().splitlines() if line.strip()]
    assert lines, "telemetry stream should contain at least one payload"

    payload = json.loads(lines[-1])
    snapshot = TelemetryClient().parse_snapshot(payload)

    assert snapshot.schema_version.startswith("0.8")
    assert snapshot.transport.last_success_tick is None or snapshot.transport.last_success_tick >= 1
    assert snapshot.transport.dropped_messages == 0
