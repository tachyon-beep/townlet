#!/usr/bin/env python
"""Capture scripted trajectories for behaviour cloning datasets."""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import numpy as np

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.policy.replay import frames_to_replay_sample
from townlet.policy.scripted import ScriptedPolicyAdapter, get_scripted_policy
from townlet.policy.scenario_utils import seed_default_agents


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture scripted trajectories for BC datasets")
    parser.add_argument("config", type=Path, help="Simulation config YAML")
    parser.add_argument("--scenario", type=str, default="idle", help="Scripted policy scenario name")
    parser.add_argument("--ticks", type=int, default=50, help="Number of ticks to simulate")
    parser.add_argument("--output", type=Path, required=True, help="Directory to write trajectories")
    parser.add_argument(
        "--tags",
        type=str,
        default="",
        help="Comma-separated tags to embed in metadata (defaults to scenario name)",
    )
    return parser.parse_args(argv)


def _build_frame(
    adapter: ScriptedPolicyAdapter,
    agent_id: str,
    observation: Dict[str, np.ndarray],
    reward: float,
    terminated: bool,
    trajectory_id: str,
) -> Dict[str, object]:
    observation_meta = dict(observation.get("metadata", {}) or {})
    frame_meta: Dict[str, object] = {
        **observation_meta,
        "agent_id": agent_id,
        "trajectory_id": trajectory_id,
    }
    map_shape = tuple(observation.get("map", np.zeros(0)).shape)
    frame_meta["map_shape"] = list(frame_meta.get("map_shape", map_shape))
    map_channels = frame_meta.get("map_channels", [])
    if isinstance(map_channels, tuple):
        frame_meta["map_channels"] = list(map_channels)

    action = adapter.last_actions.get(agent_id, {"kind": "wait"})
    return {
        "map": observation["map"],
        "features": observation["features"],
        "action_id": None,
        "action": action,
        "log_prob": 0.0,
        "rewards": [float(reward)],
        "dones": [bool(terminated)],
        "value_pred": 0.0,
        "metadata": frame_meta,
    }


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv)
    config = load_config(args.config)
    loop = SimulationLoop(config)
    scripted_policy = get_scripted_policy(args.scenario)
    adapter = ScriptedPolicyAdapter(scripted_policy)
    loop.policy = adapter  # type: ignore[attr-defined]

    if not loop.world.agents:
        seed_default_agents(loop)

    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    frames_by_agent: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    trajectory_prefix = scripted_policy.trajectory_prefix

    for _ in range(max(0, args.ticks)):
        artifacts = loop.step()
        for agent_id, observation in artifacts.observations.items():
            reward = float(artifacts.rewards.get(agent_id, 0.0))
            terminated = bool(adapter.last_terminated.get(agent_id, False))
            trajectory_id = f"{trajectory_prefix}_{agent_id}"
            frame = _build_frame(
                adapter,
                agent_id,
                observation,
                reward,
                terminated,
                trajectory_id,
            )
            frames_by_agent[agent_id].append(frame)

    tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
    if not tags:
        tags = [args.scenario]

    for agent_id, frames in frames_by_agent.items():
        if not frames:
            continue
        sample = frames_to_replay_sample(frames)
        reward_sum = float(np.sum(sample.rewards))
        metadata = sample.metadata
        metadata.setdefault("tags", tags)
        metadata.setdefault("scenario", args.scenario)
        metadata.setdefault("quality_metrics", {})
        metadata["quality_metrics"]["reward_sum"] = reward_sum
        metadata["quality_metrics"]["timesteps"] = metadata.get("timesteps", len(frames))

        stem = f"{args.scenario}_{agent_id}"
        npz_path = output_dir / f"{stem}.npz"
        json_path = output_dir / f"{stem}.json"
        np.savez(
            npz_path,
            map=sample.map,
            features=sample.features,
            actions=sample.actions,
            old_log_probs=sample.old_log_probs,
            value_preds=sample.value_preds,
            rewards=sample.rewards,
            dones=sample.dones,
        )
        json_path.write_text(json.dumps(metadata, indent=2))


if __name__ == "__main__":  # pragma: no cover
    main()
