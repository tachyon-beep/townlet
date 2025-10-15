"""Employment loop smoke test runner for R2 mitigation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.core.utils import telemetry_provider_name
from townlet.telemetry.fallback import is_stub_telemetry


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Townlet employment smoke test.")
    parser.add_argument("config", type=Path, help="Base config file")
    parser.add_argument(
        "--ticks",
        type=int,
        default=1000,
        help="Number of ticks to run.",
    )
    parser.add_argument(
        "--enforce-job-loop",
        action="store_true",
        help="Enable employment.enforce_job_loop flag during the run.",
    )
    parser.add_argument(
        "--metrics-output",
        type=Path,
        default=Path("employment_smoke_metrics.json"),
        help="Where to write summary metrics.",
    )
    return parser.parse_args()


def run_smoke(config_path: Path, ticks: int, enforce: bool) -> dict[str, Any]:
    config = load_config(config_path)
    if enforce:
        config.employment.enforce_job_loop = True

    loop = SimulationLoop(config=config)
    alerts: list[dict[str, Any]] = []
    employment_events: list[dict[str, Any]] = []
    conflict_events: list[dict[str, Any]] = []
    telemetry_stub = is_stub_telemetry(loop.telemetry, telemetry_provider_name(loop))

    for _ in range(ticks):
        loop.step()
        latest_alert = loop.stability.latest_alert
        if latest_alert:
            alerts.append({"tick": loop.tick, "alert": latest_alert})
        for event in loop.telemetry.latest_events():
            event_name = event.get("event", "")
            if event_name.startswith("employment_"):
                employment_events.append(event)
            elif event_name == "queue_conflict":
                conflict_events.append(event)

    employment_metrics = loop.telemetry.latest_employment_metrics()
    conflict_snapshot = loop.telemetry.latest_conflict_snapshot()
    queue_metrics = loop.telemetry.latest_queue_metrics()
    summary = {
        "ticks": loop.tick,
        "enforce_job_loop": config.employment.enforce_job_loop,
        "alerts": alerts,
        "employment_metrics": employment_metrics,
        "employment_events": employment_events,
        "conflict_snapshot": conflict_snapshot,
        "conflict_events": conflict_events,
        "queue_metrics": queue_metrics,
    }
    if telemetry_stub:
        summary["telemetry_warning"] = "Telemetry stub active; conflict metrics may be incomplete."
    return summary


def main() -> None:
    args = parse_args()
    results = run_smoke(args.config, ticks=args.ticks, enforce=args.enforce_job_loop)
    args.metrics_output.write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
