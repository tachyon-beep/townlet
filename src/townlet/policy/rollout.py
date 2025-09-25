"""Rollout buffer scaffolding for future live PPO integration."""
from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from townlet.policy.metrics import compute_sample_metrics
from townlet.policy.replay import ReplaySample, frames_to_replay_sample
from townlet.policy.replay_buffer import InMemoryReplayDataset, InMemoryReplayDatasetConfig


@dataclass
class AgentRollout:
    agent_id: str
    frames: list[dict[str, object]] = field(default_factory=list)

    def append(self, frame: dict[str, object]) -> None:
        self.frames.append(frame)

    def to_replay_sample(self) -> ReplaySample:
        return frames_to_replay_sample(self.frames)


class RolloutBuffer:
    """Collects trajectory frames and exposes helpers to save or replay them."""

    def __init__(self) -> None:
        self._frames: list[dict[str, object]] = []
        self._tick_count = 0
        self._queue_conflict_count = 0
        self._queue_conflict_intensity = 0.0

    def record_events(self, events: Iterable[dict[str, object]]) -> None:
        for event in events:
            if event.get("event") == "queue_conflict":
                self._queue_conflict_count += 1
                intensity = event.get("intensity")
                try:
                    self._queue_conflict_intensity += float(intensity)
                except (TypeError, ValueError):
                    continue

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

    def build_dataset(
        self,
        batch_size: int = 1,
        drop_last: bool = False,
    ) -> InMemoryReplayDataset:
        if not self._frames:
            raise ValueError("Rollout buffer contains no frames; cannot build dataset")
        samples = []
        for sample in self.to_samples().values():
            metrics = sample.metadata.get("metrics")
            if not isinstance(metrics, dict) or not metrics:
                sample.metadata["metrics"] = compute_sample_metrics(sample)
            samples.append(sample)
        config = InMemoryReplayDatasetConfig(
            entries=samples,
            batch_size=batch_size,
            drop_last=drop_last,
            rollout_ticks=self._tick_count,
        )
        dataset = InMemoryReplayDataset(config)
        dataset.baseline_metrics = self._aggregate_metrics(samples)
        dataset.queue_conflict_count = self._queue_conflict_count
        dataset.queue_conflict_intensity_sum = self._queue_conflict_intensity
        return dataset

    def is_empty(self) -> bool:
        return not self._frames

    def set_tick_count(self, ticks: int) -> None:
        self._tick_count = max(0, int(ticks))

    def _aggregate_metrics(self, samples: list[ReplaySample]) -> dict[str, float]:
        metrics_sources: list[dict[str, float]] = []
        for sample in samples:
            metrics = sample.metadata.get("metrics")
            if isinstance(metrics, dict) and metrics:
                metrics_sources.append(dict(metrics))

        if not metrics_sources:
            return {}

        totals: dict[str, float] = {}
        counts: dict[str, int] = {}
        for metrics in metrics_sources:
            for key, value in metrics.items():
                if not isinstance(value, (int, float)):
                    continue
                totals[key] = totals.get(key, 0.0) + float(value)
                counts[key] = counts.get(key, 0) + 1

        if not totals:
            return {}

        sample_count = float(len(metrics_sources))
        aggregate: dict[str, float] = {"sample_count": sample_count}
        for key, total in totals.items():
            occurrences = counts.get(key, 0)
            if occurrences == 0:
                continue
            if key.endswith("_sum") or key.endswith("_total"):
                aggregate[key] = total
                aggregate[f"{key}_mean"] = total / sample_count if sample_count else 0.0
            else:
                aggregate[key] = total / occurrences
        return aggregate
