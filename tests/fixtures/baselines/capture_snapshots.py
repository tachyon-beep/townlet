#!/usr/bin/env python3
"""Capture pickle-based snapshots for WP5 Phase 0.1 baseline.

This script runs a simulation and captures snapshots at specific ticks to
establish a baseline for RNG migration compatibility testing.
"""
from pathlib import Path

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.snapshots import SnapshotManager, snapshot_from_world

SNAPSHOT_TICKS = [10, 25, 50]
OUTPUT_DIR = Path("tests/fixtures/baselines/snapshots")


def main() -> None:
    """Capture baseline snapshots."""
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Create simulation loop
    loop = SimulationLoop(config)
    snapshot_mgr = SnapshotManager(OUTPUT_DIR)

    print(f"Capturing baseline snapshots at ticks: {SNAPSHOT_TICKS}")
    print(f"Output directory: {OUTPUT_DIR}")

    # Run simulation and capture snapshots
    for tick_target in SNAPSHOT_TICKS:
        print(f"\nRunning to tick {tick_target}...")
        while loop.tick < tick_target:
            loop.step()

        # Capture snapshot using snapshot_from_world
        print(f"Capturing snapshot at tick {loop.tick}...")
        rng_streams = {
            "world": loop._rng_world,
            "events": loop._rng_events,
            "policy": loop._rng_policy,
        }
        snapshot = snapshot_from_world(
            config=loop.config,
            world=loop.world,
            lifecycle=loop.lifecycle,
            telemetry=loop.telemetry,
            perturbations=loop.perturbations,
            stability=loop.stability,
            promotion=loop.promotion,
            rng_streams=rng_streams,
        )

        # Save snapshot
        saved_path = snapshot_mgr.save(snapshot)
        print(f"  ✓ Snapshot saved to {saved_path}")

    print("\n✓ All baseline snapshots captured successfully")
    print(f"\nSnapshot locations:")
    for file in sorted(OUTPUT_DIR.glob("snapshot-*.json")):
        print(f"  - {file}")


if __name__ == "__main__":
    main()
