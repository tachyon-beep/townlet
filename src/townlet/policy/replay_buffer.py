"""In-memory replay dataset used for rollout captures."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Sequence

from townlet.policy.replay import ReplayBatch, ReplaySample, build_batch


@dataclass
class InMemoryReplayDatasetConfig:
    entries: Sequence[ReplaySample]
    batch_size: int = 1
    drop_last: bool = False
    rollout_ticks: int = 0
    label: str | None = None


class InMemoryReplayDataset:
    def __init__(self, config: InMemoryReplayDatasetConfig) -> None:
        if config.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        self.config = config
        self.samples = list(config.entries)
        if not self.samples:
            raise ValueError("In-memory dataset requires samples")
        self.batch_size = config.batch_size
        self._validate_shapes()
        self.rollout_ticks = int(config.rollout_ticks)
        self.label = config.label
        self.queue_conflict_count = 0
        self.queue_conflict_intensity_sum = 0.0
        self.shared_meal_count = 0
        self.late_help_count = 0
        self.shift_takeover_count = 0
        self.chat_success_count = 0
        self.chat_failure_count = 0
        self.chat_quality_mean = 0.0

    def _validate_shapes(self) -> None:
        base = self.samples[0]
        for sample in self.samples[1:]:
            if sample.map.shape != base.map.shape or sample.features.shape != base.features.shape:
                raise ValueError("In-memory samples have mismatched shapes")

    def __iter__(self) -> Iterator[ReplayBatch]:
        for start in range(0, len(self.samples), self.batch_size):
            chunk = self.samples[start : start + self.batch_size]
            if len(chunk) < self.batch_size and self.config.drop_last:
                continue
            yield build_batch(chunk)

    def __len__(self) -> int:
        total = len(self.samples)
        batches, remainder = divmod(total, self.batch_size)
        if remainder and not self.config.drop_last:
            batches += 1
        return batches
