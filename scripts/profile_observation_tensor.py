"""Profile observation tensor dimensions for a given config."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean

import numpy as np

from townlet.config import load_config
from townlet.observations.builder import ObservationBuilder
from townlet.world import AgentSnapshot, WorldState


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Profile Townlet observation tensors")
    parser.add_argument("config", type=Path, help="Simulation config path")
    parser.add_argument("--agents", type=int, default=4, help="Number of synthetic agents (default: 4)")
    parser.add_argument("--ticks", type=int, default=50, help="Ticks to simulate for profiling (default: 50)")
    parser.add_argument("--output", type=Path, help="Optional JSON output file")
    return parser.parse_args()


def bootstrap_world(config_path: Path, agent_count: int) -> tuple[WorldState, ObservationBuilder]:
    config = load_config(config_path)
    world = WorldState.from_config(config)
    builder = ObservationBuilder(config)

    for index in range(agent_count):
        agent_id = f"agent-{index}"
        world.agents[agent_id] = AgentSnapshot(
            agent_id=agent_id,
            position=(index, 0),
            needs={"hunger": 0.5, "hygiene": 0.6, "energy": 0.7},
            wallet=5.0,
        )
    return world, builder


def profile(world: WorldState, builder: ObservationBuilder, ticks: int) -> dict[str, object]:
    feature_dims: list[int] = []
    map_shapes: set[tuple[int, int, int]] = set()
    trust_means: list[float] = []

    for tick in range(ticks):
        world.tick = tick
        batch = builder.build_batch(world, terminated={})
        for obs in batch.values():
            features = obs["features"]
            feature_dims.append(int(features.shape[0]))
            map_shape = obs["metadata"].get("map_shape")
            if map_shape:
                map_shapes.add(tuple(map_shape))
            trust_indices = [idx for name, idx in builder._feature_index.items() if name.endswith("trust_mean")]
            for idx in trust_indices:
                if idx < len(features):
                    trust_means.append(float(features[idx]))
        world._apply_need_decay()

    return {
        "ticks": ticks,
        "agents": len(world.agents),
        "feature_dim": {
            "min": min(feature_dims) if feature_dims else 0,
            "max": max(feature_dims) if feature_dims else 0,
            "mean": mean(feature_dims) if feature_dims else 0,
        },
        "map_shapes": sorted(map_shapes),
        "trust_mean_avg": mean(trust_means) if trust_means else 0.0,
    }


def main() -> None:
    args = parse_args()
    world, builder = bootstrap_world(args.config, args.agents)
    summary = profile(world, builder, args.ticks)

    if args.output:
        args.output.write_text(json.dumps(summary, indent=2))
    else:
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
