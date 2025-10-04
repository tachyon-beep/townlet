"""Run a headless Townlet simulation loop for debugging."""
from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from townlet.config.loader import load_config
from townlet.core.sim_loop import SimulationLoop


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Townlet simulation loop.")
    parser.add_argument("config", type=Path, help="Path to the simulation configuration YAML.")
    parser.add_argument(
        "--ticks",
        type=int,
        default=1_000,
        help="Number of simulation ticks to execute before exiting.",
    )
    parser.add_argument(
        "--stream-telemetry",
        action="store_true",
        help="Stream telemetry payloads to stdout (default: discard telemetry).",
    )
    parser.add_argument(
        "--telemetry-path",
        type=Path,
        help="Write telemetry payloads to this file when stdout streaming is disabled.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    if args.stream_telemetry and args.telemetry_path is not None:
        raise SystemExit("--stream-telemetry cannot be combined with --telemetry-path")

    if not args.stream_telemetry:
        target_path = Path(os.devnull) if args.telemetry_path is None else args.telemetry_path
        transport = config.telemetry.transport.model_copy(
            update={"type": "file", "file_path": target_path}
        )
        telemetry_cfg = config.telemetry.model_copy(update={"transport": transport})
        config = config.model_copy(update={"telemetry": telemetry_cfg})
        if target_path != Path(os.devnull):
            target_path.parent.mkdir(parents=True, exist_ok=True)
            print(f"Telemetry stream written to {target_path}")

    loop = SimulationLoop(config=config)
    start = time.perf_counter()
    try:
        loop.run_for(args.ticks)
    finally:
        try:
            loop.telemetry.close()
        except Exception:  # pragma: no cover - shutdown guard
            pass
    duration = time.perf_counter() - start
    ticks = loop.tick
    if ticks:
        elapsed = duration if duration > 0 else 1e-9
        print(
            f"Completed {ticks} ticks in {duration:.3f}s "
            f"({ticks / elapsed:.1f} ticks/sec)"
        )
    else:
        print("Simulation completed without advancing ticks")


if __name__ == "__main__":
    main()
