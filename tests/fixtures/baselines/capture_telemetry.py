#!/usr/bin/env python3
"""Capture telemetry event stream for WP5 Phase 0.1 baseline.

This script runs a simulation and captures telemetry events to establish
a baseline for stability analyzer behavior characterization.
"""
from pathlib import Path

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop

TICKS = 100
OUTPUT_FILE = Path("tests/fixtures/baselines/telemetry/events.jsonl")


def main() -> None:
    """Capture baseline telemetry stream."""
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))

    # Use stdout telemetry provider
    config.runtime.telemetry.provider = "stdout"

    # Ensure output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print(f"Capturing telemetry baseline for {TICKS} ticks", flush=True)
    print(f"Output file: {OUTPUT_FILE}", flush=True)

    # Create and run simulation
    # We'll redirect stdout to the file at the bash level
    loop = SimulationLoop(config)

    print(f"Running simulation...", flush=True)
    for _ in range(TICKS):
        loop.step()

    # Ensure telemetry is flushed
    if hasattr(loop.telemetry, "stop"):
        loop.telemetry.stop()

    print(f"Telemetry baseline captured successfully", flush=True)


if __name__ == "__main__":
    main()
