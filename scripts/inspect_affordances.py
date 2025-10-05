"""Inspect affordance runtime state from configs or snapshots."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.core.utils import is_stub_telemetry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect affordance runtime state from a snapshot or config",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--snapshot", type=Path, help="Snapshot JSON path to inspect")
    group.add_argument("--config", type=Path, help="Simulation config to load")
    parser.add_argument(
        "--ticks",
        type=int,
        default=0,
        help="Ticks to advance when loading a config (default: 0)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of a human summary",
    )
    return parser.parse_args()


def _normalise_running_payload(running: dict[str, Any]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for object_id, state in running.items():
        try:
            payload[object_id] = asdict(state)
        except TypeError:
            payload[object_id] = dict(state)
    return payload


def inspect_snapshot(path: Path) -> dict[str, Any]:
    document = json.loads(path.read_text())
    state_payload = document.get("state", document)
    affordances = state_payload.get("affordances", {}) or {}
    queues = state_payload.get("queues", {}) or {}
    active_reservations = queues.get("active", {}) or {}
    return {
        "source": "snapshot",
        "path": str(path.resolve()),
        "tick": state_payload.get("tick", 0),
        "runtime": {
            "instrumentation": None,
            "running_count": len(affordances),
            "running": _normalise_running_payload(affordances),
            "active_reservations": dict(active_reservations),
        },
    }


def inspect_config(path: Path, ticks: int) -> dict[str, Any]:
    config = load_config(path)
    loop = SimulationLoop(config)

    class _NullTransport:
        def send(self, payload: bytes) -> None:  # pragma: no cover - simple sink
            return None

        def close(self) -> None:  # pragma: no cover - simple sink
            return None

    telemetry = loop.telemetry
    is_stub = is_stub_telemetry(telemetry)
    if hasattr(telemetry, "stop_worker"):
        telemetry.stop_worker(wait=True)  # type: ignore[attr-defined]
    if not is_stub and hasattr(telemetry, "_transport_client"):
        telemetry._transport_client = _NullTransport()  # type: ignore[attr-defined]
    for _ in range(max(0, int(ticks))):
        with contextlib.redirect_stdout(io.StringIO()):
            loop.step()
    if hasattr(telemetry, "stop_worker"):
        telemetry.stop_worker(wait=True)  # type: ignore[attr-defined]
    running = loop.world.running_affordances_snapshot()
    report = {
        "source": "config",
        "config": str(path.resolve()),
        "config_id": config.config_id,
        "tick": loop.tick,
        "runtime": {
            "instrumentation": config.affordances.runtime.instrumentation,
            "running_count": len(running),
            "running": _normalise_running_payload(running),
            "active_reservations": loop.world.active_reservations,
        },
    }
    if is_stub:
        report["telemetry_warning"] = "Telemetry stub active; transport metrics unavailable."
    return report


def render_text(report: dict[str, Any]) -> str:
    runtime = report["runtime"]
    lines = [f"Source      : {report['source']}"]
    if report["source"] == "config":
        lines.append(f"Config ID   : {report['config_id']}")
        lines.append(f"Tick        : {report['tick']}")
        lines.append(f"Instrumentation: {runtime.get('instrumentation', 'off')}")
    else:
        lines.append(f"Snapshot tick: {report['tick']}")
    lines.append(f"Running count: {runtime['running_count']}")
    running = runtime.get("running", {})
    if running:
        lines.append("Running affordances:")
        for object_id, state in running.items():
            agent = state.get("agent_id")
            affordance = state.get("affordance_id")
            duration = state.get("duration_remaining")
            lines.append(f"  - {object_id}: agent={agent} affordance={affordance} duration_remaining={duration}")
    else:
        lines.append("No active affordances")
    reservations = runtime.get("active_reservations", {})
    if reservations:
        lines.append("Active reservations:")
        for object_id, agent_id in reservations.items():
            lines.append(f"  - {object_id}: {agent_id}")
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    if args.snapshot:
        report = inspect_snapshot(Path(args.snapshot))
    else:
        report = inspect_config(Path(args.config), args.ticks)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render_text(report))


if __name__ == "__main__":
    main()
