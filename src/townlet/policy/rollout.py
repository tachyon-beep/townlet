"""Rollout buffer scaffolding for future live PPO integration."""
from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from townlet.policy.metrics import compute_sample_metrics
from townlet.policy.replay import ReplaySample, frames_to_replay_sample


@dataclass
class AgentRollout:
    agent_id: str
    frames: list[dict[str, object]] = field(default_factory=list)

    def append(self, frame: dict[str, object]) -> None:
        self.frames.append(frame)

    def to_replay_sample(self) -> ReplaySample:
        return frames_to_replay_sample(self.frames)


class RolloutBuffer:
    """Collects trajectory frames and exposes helpers to save them."""

    def __init__(self) -> None:
        self._frames: list[dict[str, object]] = []

    def extend(self, frames: Iterable[dict[str, object]]) -> None:
        for frame in frames:
            self._frames.append(frame)

    def __len__(self) -> int:
        return len(self._frames)

    def by_agent(self) -> dict[str, AgentRollout]:
        grouped: dict[str, AgentRollout] = {}
        for frame in self._frames:
            agent_id = str(frame.get("agent_id", "unknown"))
            grouped.setdefault(agent_id, AgentRollout(agent_id)).append(frame)
        return grouped

    def to_samples(self) -> dict[str, ReplaySample]:
        return {
            agent_id: rollout.to_replay_sample()
            for agent_id, rollout in self.by_agent().items()
        }

    def save(self, output_dir: Path, prefix: str = "rollout_sample", compress: bool = True) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        save_fn = np.savez_compressed if compress else np.savez

        manifest_entries: list[dict[str, str]] = []
        metrics_map: dict[str, dict[str, float]] = {}
        for index, (agent_id, rollout) in enumerate(self.by_agent().items(), start=1):
            sample = rollout.to_replay_sample()
            stem = f"{prefix}_{agent_id}_{index:03d}"
            sample_path = output_dir / f"{stem}.npz"
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
            meta.update({"agent_id": agent_id, "frame_count": len(rollout.frames)})
            sample_metrics = compute_sample_metrics(sample)
            meta["metrics"] = sample_metrics
            metrics_map[sample_path.name] = sample_metrics
            meta_path.write_text(json.dumps(meta, indent=2))
            manifest_entries.append({"sample": sample_path.name, "meta": meta_path.name})

        manifest_path = output_dir / f"{prefix}_manifest.json"
        manifest_path.write_text(json.dumps(manifest_entries, indent=2))
        metrics_path = output_dir / f"{prefix}_metrics.json"
        metrics_path.write_text(json.dumps(metrics_map, indent=2))

    def is_empty(self) -> bool:
        return not self._frames
