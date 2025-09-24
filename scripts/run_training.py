"""CLI entry point for training Townlet policies."""
from __future__ import annotations

import argparse
from pathlib import Path

from townlet.config.loader import load_config
from townlet.policy.runner import TrainingHarness


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Townlet PPO policies.")
    parser.add_argument(
        "config",
        type=Path,
        help="Path to the simulation configuration YAML.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    harness = TrainingHarness(config=config)
    harness.run()


if __name__ == "__main__":
    main()
