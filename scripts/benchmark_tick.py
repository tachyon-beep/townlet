"""Simple benchmark to estimate average tick duration."""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark simulation tick duration")
    parser.add_argument("config", type=Path, help="Config file path")
    parser.add_argument("--ticks", type=int, default=2000, help="Tick count to run")
    parser.add_argument("--enforce-job-loop", action="store_true")
    return parser.parse_args()


def benchmark(config_path: Path, ticks: int, enforce: bool) -> float:
    if ticks <= 0:
        raise ValueError("ticks must be positive for benchmarking")
    config = load_config(config_path)
    config.employment.enforce_job_loop = enforce
    loop = SimulationLoop(config)
    start = time.perf_counter()
    loop.run_for(ticks)
    duration = time.perf_counter() - start
    return duration / ticks


def main() -> None:
    args = parse_args()
    avg = benchmark(args.config, args.ticks, args.enforce_job_loop)
    print(f"average_tick_seconds={avg:.6f}")


if __name__ == "__main__":
    main()
