"""CLI to capture Townlet rollout trajectories into replay samples."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

from townlet.config.loader import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.policy.replay import ReplaySample, frames_to_replay_sample
from townlet.policy.behavior import AgentIntent, BehaviorController
from townlet.world.grid import AgentSnapshot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture rollout trajectories as replay samples.")
    parser.add_argument("config", type=Path, help="Simulation config path")
    parser.add_argument(
        "--ticks",
        type=int,
        default=100,
        help="Number of ticks to simulate before saving frames.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Directory to store replay samples (NPZ + JSON metadata).",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="rollout_sample",
        help="Filename prefix for generated samples.",
    )
    parser.add_argument(
        "--auto-seed-agents",
        action="store_true",
        help="Populate the world with placeholder agents if the scenario lacks agent definitions.",
    )
    parser.add_argument(
        "--agent-id",
        type=str,
        default=None,
        help="Only export frames for the specified agent id.",
    )
    parser.add_argument(
        "--compress",
        action="store_true",
        help="Use numpy.savez_compressed for output NPZ files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    loop = SimulationLoop(config)
    scenario_config: Dict[str, Any] | None = getattr(config, "scenario", None)
    if scenario_config:
        _apply_scenario(loop, scenario_config)
    elif args.auto_seed_agents and not loop.world.agents:
        loop.world.register_object("stove_1", "stove")
        loop.world.agents["alice"] = AgentSnapshot(
            "alice",
            (0, 0),
            {"hunger": 0.3, "hygiene": 0.4, "energy": 0.5},
            wallet=2.0,
        )
        loop.world.agents["bob"] = AgentSnapshot(
            "bob",
            (1, 0),
            {"hunger": 0.6, "hygiene": 0.7, "energy": 0.8},
            wallet=3.0,
        )
    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    total_ticks = int(scenario_config.get("ticks", args.ticks) if scenario_config else args.ticks)
    for _ in range(max(0, total_ticks)):
        loop.step()

    frames = loop.policy.collect_trajectory(clear=True)
    if args.agent_id is not None:
        frames = [frame for frame in frames if frame.get("agent_id") == args.agent_id]

    by_agent: dict[str, List[dict[str, object]]] = {}
    for frame in frames:
        agent_id = frame.get("agent_id", "unknown")
        by_agent.setdefault(agent_id, []).append(frame)

    manifest_entries = []
    metrics_map: Dict[str, Dict[str, float]] = {}
    for index, (agent_id, agent_frames) in enumerate(by_agent.items(), start=1):
        if not agent_frames:
            continue
        sample: ReplaySample = frames_to_replay_sample(agent_frames)
        stem = f"{args.prefix}_{agent_id}_{index:03d}"
        sample_path = output_dir / f"{stem}.npz"
        save_fn = np.savez_compressed if args.compress else np.savez
        save_fn(
            sample_path,
            map=sample.map,
            features=sample.features,
            actions=sample.actions,
            old_log_probs=sample.old_log_probs,
            value_preds=sample.value_preds,
            rewards=sample.rewards,
            dones=sample.dones,
        )
        meta_path = output_dir / f"{stem}.json"
        meta = sample.metadata.copy()
        meta.update({"agent_id": agent_id, "frame_count": len(agent_frames)})
        sample_metrics = _compute_sample_metrics(sample)
        metrics_map[sample_path.name] = sample_metrics
        meta["metrics"] = sample_metrics
        meta_path.write_text(json.dumps(meta, indent=2))
        manifest_entries.append({"sample": str(sample_path.name), "meta": str(meta_path.name)})

    manifest_path = output_dir / f"{args.prefix}_manifest.json"
    manifest_path.write_text(json.dumps(manifest_entries, indent=2))
    metrics_path = output_dir / f"{args.prefix}_metrics.json"
    metrics_path.write_text(json.dumps(metrics_map, indent=2))
    print(f"Captured {len(manifest_entries)} replay samples to {output_dir}")


def _compute_sample_metrics(sample: ReplaySample) -> Dict[str, float]:
    metrics: Dict[str, float] = {}
    rewards = sample.rewards
    metrics["timesteps"] = float(rewards.shape[0])
    metrics["reward_sum"] = float(np.sum(rewards))
    metrics["reward_mean"] = float(np.mean(rewards)) if rewards.size else 0.0
    metrics["log_prob_mean"] = float(np.mean(sample.old_log_probs)) if sample.old_log_probs.size else 0.0
    metrics["value_pred_last"] = float(sample.value_preds[-1]) if sample.value_preds.size else 0.0

    names = sample.metadata.get("feature_names")
    if isinstance(names, list):
        features = sample.features
        if features.ndim == 1:
            features = features[np.newaxis, :]

        def add_stats(feature_name: str) -> None:
            if feature_name in names:
                idx = names.index(feature_name)
                column = features[:, idx]
                metrics[f"{feature_name}_mean"] = float(np.mean(column))
                metrics[f"{feature_name}_max"] = float(np.max(column))

        add_stats("rivalry_max")
        add_stats("rivalry_avoid_count")
        reward_idx = names.index("reward_total") if "reward_total" in names else None
        if reward_idx is not None:
            metrics["reward_feature_mean"] = float(np.mean(features[:, reward_idx]))
        lateness_idx = names.index("lateness_counter") if "lateness_counter" in names else None
        if lateness_idx is not None:
            metrics["lateness_mean"] = float(np.mean(features[:, lateness_idx]))

    # Action distribution
    action_ids = sample.actions.astype(int)
    action_counts = np.bincount(action_ids, minlength=int(action_ids.max() + 1)) if action_ids.size else np.array([])
    total_actions = float(np.sum(action_counts)) if action_counts.size else 0.0
    metrics["action_nonzero"] = float(np.count_nonzero(action_counts)) if action_counts.size else 0.0
    metrics["action_total"] = total_actions
    if total_actions > 0:
        probs = action_counts / total_actions
        metrics["action_entropy"] = float(-np.sum(np.where(probs > 0, probs * np.log(np.clip(probs, 1e-8, None)), 0.0)))
    else:
        metrics["action_entropy"] = 0.0

    action_lookup_meta = sample.metadata.get("action_lookup")
    kind_counts: Dict[str, float] = {}
    blocked_total = 0.0
    if isinstance(action_lookup_meta, dict):
        id_to_payload: Dict[int, Dict[str, Any]] = {}
        for key, value in action_lookup_meta.items():
            if isinstance(value, int):
                action_id = value
                payload_str = key
            else:
                try:
                    action_id = int(key)
                    payload_str = value
                except (TypeError, ValueError):
                    continue
            try:
                payload = json.loads(payload_str)
            except json.JSONDecodeError:
                payload = {"raw": payload_str}
            id_to_payload[action_id] = payload

        for action_id, count in enumerate(action_counts):
            if count == 0:
                continue
            payload = id_to_payload.get(action_id, {})
            kind = payload.get("kind", "unknown")
            kind_counts[kind] = kind_counts.get(kind, 0.0) + float(count)
            if payload.get("blocked"):
                blocked_total += float(count)

    for kind, count in kind_counts.items():
        metrics[f"action_{kind}_count"] = count
    metrics["action_blocked_ratio"] = float(blocked_total / total_actions) if total_actions else 0.0

    return metrics


class ScenarioBehavior(BehaviorController):
    """Simple behavior controller driven by scenario schedules."""

    def __init__(self, config, schedules: Dict[str, List[AgentIntent]]) -> None:
        self.config = config
        self._schedules = schedules
        self._indices: Dict[str, int] = {agent_id: 0 for agent_id in schedules}

    def decide(self, world, agent_id):  # type: ignore[override]
        seq = self._schedules.get(agent_id)
        if not seq:
            return AgentIntent(kind="wait")
        idx = self._indices.setdefault(agent_id, 0)
        intent = seq[idx % len(seq)]
        self._indices[agent_id] = idx + 1
        return intent


def _apply_scenario(loop: SimulationLoop, scenario: Dict[str, Any]) -> None:
    objects = scenario.get("objects", [])
    for obj in objects:
        loop.world.register_object(obj["id"], obj["type"])

    schedules: Dict[str, List[AgentIntent]] = {}
    for agent in scenario.get("agents", []):
        agent_id = agent["id"]
        position = tuple(agent.get("position", (0, 0)))  # type: ignore[arg-type]
        needs = dict(agent.get("needs", {}))
        snapshot = AgentSnapshot(
            agent_id,
            position,
            needs,
            wallet=float(agent.get("wallet", 0.0)),
        )
        if agent.get("job"):
            snapshot.job_id = agent["job"]
        loop.world.agents[agent_id] = snapshot

        schedule_entries = agent.get("schedule", [])
        intents: List[AgentIntent] = []
        for entry in schedule_entries:
            data = dict(entry)
            if "object" in data and "object_id" not in data:
                data["object_id"] = data.pop("object")
            if "affordance" in data and "affordance_id" not in data:
                data["affordance_id"] = data.pop("affordance")
            intent = AgentIntent(
                kind=data.get("kind", "wait"),
                object_id=data.get("object_id"),
                affordance_id=data.get("affordance_id"),
                blocked=bool(data.get("blocked", False)),
                position=tuple(data["position"]) if data.get("position") else None,
            )
            intents.append(intent)
        if intents:
            schedules[agent_id] = intents

    if schedules:
        loop.policy.behavior = ScenarioBehavior(loop.config, schedules)


if __name__ == "__main__":
    main()
