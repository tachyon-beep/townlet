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
    config.telemetry.diff_enabled = False

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
    snapshot = TelemetryClient().parse_payload(payload)

    assert snapshot.schema_version.startswith("0.9")
    assert snapshot.transport.last_success_tick is None or snapshot.transport.last_success_tick >= 1
    assert snapshot.transport.dropped_messages == 0


def test_file_transport_diff_stream(tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.telemetry.transport.type = "file"
    config.telemetry.transport.file_path = tmp_path / "telemetry_diff.jsonl"
    config.telemetry.transport.buffer.max_batch_size = 1
    config.telemetry.transport.buffer.flush_interval_ticks = 1
    config.telemetry.diff_enabled = True

    loop = SimulationLoop(config)
    _ensure_agents(loop)

    for _ in range(3):
        loop.step()

    loop.telemetry.close()

    stream_path = config.telemetry.transport.file_path
    lines = [json.loads(line) for line in stream_path.read_text().splitlines() if line.strip()]
    assert len(lines) >= 2
    assert lines[0].get("payload_type") == "snapshot"
    assert any(line.get("payload_type") == "diff" for line in lines[1:])

    client = TelemetryClient()
    for payload in lines:
        snapshot = client.parse_payload(payload)

    assert snapshot.schema_version.startswith("0.9")
    assert snapshot.transport.dropped_messages >= 0
