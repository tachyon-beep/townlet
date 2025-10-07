from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from townlet.runtime.loop import SimulationLoop


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Townlet simulation loop.")
    parser.add_argument("config", type=Path, help="YAML file selecting world/policy/telemetry providers.")
    parser.add_argument("--ticks", type=int, default=10, help="Number of ticks to execute.")
    parser.add_argument("--seed", type=int, help="Optional RNG seed passed to the world reset.")
    return parser.parse_args()


def load_runtime_config(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise SystemExit("Configuration file must contain a mapping")
    return data


def main() -> None:
    args = parse_args()
    config = load_runtime_config(args.config)
    loop = SimulationLoop(
        world_cfg=config.get("world"),
        policy_cfg=config.get("policy"),
        telemetry_cfg=config.get("telemetry"),
    )
    loop.run(args.ticks, seed=args.seed)


if __name__ == "__main__":
    main()
