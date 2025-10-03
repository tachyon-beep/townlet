"""Run a headless Townlet simulation loop for debugging."""
from __future__ import annotations

import argparse
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    loop = SimulationLoop(config=config)
    for _ in loop.run(max_ticks=args.ticks):
        pass


if __name__ == "__main__":
    main()
