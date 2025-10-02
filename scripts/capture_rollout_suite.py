"""Run rollout capture across a suite of configs."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List

from townlet.config.loader import load_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run capture_rollout across multiple configs.")
    parser.add_argument(
        "configs",
        nargs="+",
        type=Path,
        help="List of simulation config paths.",
    )
    parser.add_argument(
        "--ticks",
        type=int,
        default=100,
        help="Number of ticks per capture run.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("captures"),
        help="Root directory to store capture outputs.",
    )
    parser.add_argument(
        "--auto-seed-agents",
        action="store_true",
        help="Pass --auto-seed-agents to capture_rollout.",
    )
    parser.add_argument(
        "--agent-filter",
        type=str,
        default=None,
        help="Only export trajectories for the specified agent id.",
    )
    parser.add_argument(
        "--compress",
        action="store_true",
        help="Compress NPZ outputs using numpy savez_compressed.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=1,
        help="Number of times to retry capture on failure.",
    )
    return parser.parse_args()


def run_capture(
    config: Path,
    ticks: int,
    output: Path,
    auto_seed: bool,
    agent_filter: str | None,
    compress: bool,
    retries: int,
) -> None:
    load_config(config)  # validation only
    output.mkdir(parents=True, exist_ok=True)
    cmd: List[str] = [
        sys.executable,
        "scripts/capture_rollout.py",
        str(config),
        "--ticks",
        str(ticks),
        "--output",
        str(output),
    ]
    if auto_seed:
        cmd.append("--auto-seed-agents")
    if agent_filter:
        cmd.extend(["--agent-id", agent_filter])
    if compress:
        cmd.append("--compress")
    attempts = 0
    while attempts < max(1, retries):
        try:
            subprocess.run(cmd, check=True)
            return
        except subprocess.CalledProcessError:
            attempts += 1
            if attempts >= max(1, retries):
                raise


def main() -> None:
    args = parse_args()
    for config in args.configs:
        scenario_name = config.stem
        output_dir = args.output_root / scenario_name
        run_capture(
            config=config,
            ticks=args.ticks,
            output=output_dir,
            auto_seed=args.auto_seed_agents,
            agent_filter=args.agent_filter,
            compress=args.compress,
            retries=args.retries,
        )


if __name__ == "__main__":
    main()
