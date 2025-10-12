"""In-memory replay dataset used for rollout captures."""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from townlet.policy.replay import (
    TRAINING_ARRAY_FIELDS,
    ReplayBatch,
    ReplaySample,
    build_batch,
)


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
        # Only enforce global shape homogeneity when we intend to stack
        # multiple samples in the same batch. For batch_size == 1 we allow
        # variable-length trajectories (different timestep counts) and rely
        # on per-sample batching.
        # Build homogeneity buckets to allow mixed-length trajectories to be
        # batched safely. If all samples share shapes, we keep a single bucket
        # and fast-path iteration.
        self._buckets = self._build_buckets(self.samples)
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

    def _signature(self, sample: ReplaySample) -> tuple:
        return (
            tuple(sample.map.shape),
            tuple(sample.features.shape),
            tuple(getattr(sample, field).shape for field in TRAINING_ARRAY_FIELDS),
        )

    def _build_buckets(self, samples: list[ReplaySample]) -> list[list[ReplaySample]]:
        buckets: dict[tuple, list[ReplaySample]] = {}
        for s in samples:
            buckets.setdefault(self._signature(s), []).append(s)
        # Keep deterministic ordering by signature
        return [buckets[key] for key in sorted(buckets.keys())]

    def __iter__(self) -> Iterator[ReplayBatch]:
        for bucket in self._buckets:
            if not bucket:
                continue
            for start in range(0, len(bucket), self.batch_size):
                chunk = bucket[start : start + self.batch_size]
                if len(chunk) < self.batch_size and self.config.drop_last:
                    continue
                yield build_batch(chunk)

    def __len__(self) -> int:
        total_batches = 0
        for bucket in self._buckets:
            total = len(bucket)
            batches, remainder = divmod(total, self.batch_size)
            if remainder and not self.config.drop_last:
                batches += 1
            total_batches += batches
        return total_batches
