"""Utilities for replaying observation/telemetry samples."""

from __future__ import annotations

import json
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import yaml

REQUIRED_CONFLICT_FEATURES: tuple[str, ...] = ("rivalry_max", "rivalry_avoid_count")
STEP_ARRAY_FIELDS: tuple[str, ...] = ("actions", "old_log_probs", "rewards", "dones")
TRAINING_ARRAY_FIELDS: tuple[str, ...] = (*STEP_ARRAY_FIELDS, "value_preds")


@dataclass
class ReplaySample:
    """Container for observation samples used in training replays."""

    map: np.ndarray
    features: np.ndarray
    actions: np.ndarray
    old_log_probs: np.ndarray
    value_preds: np.ndarray
    rewards: np.ndarray
    dones: np.ndarray
    metadata: dict[str, Any]

    def __post_init__(self) -> None:
        timesteps = None
        for field_name in TRAINING_ARRAY_FIELDS:
            value = getattr(self, field_name)
            if not isinstance(value, np.ndarray):
                raise TypeError(f"ReplaySample.{field_name} must be a numpy array")
            if value.ndim == 0:
                setattr(self, field_name, value.reshape(1))
            elif value.ndim > 2:
                raise ValueError(
                    f"ReplaySample.{field_name} must be 1D or 2D, got shape {value.shape}"
                )
            if field_name in STEP_ARRAY_FIELDS:
                step_len = getattr(self, field_name).shape[0]
                if timesteps is None:
                    timesteps = step_len
                elif step_len != timesteps:
                    raise ValueError(
                        "ReplaySample training arrays must share timestep length; "
                        f"expected {timesteps}, got {step_len} for {field_name}"
                    )
        if timesteps is None:
            raise ValueError("ReplaySample requires at least one timestep array")

        if self.map.ndim == 3:
            self.map = np.expand_dims(self.map, axis=0)
        elif self.map.ndim != 4:
            raise ValueError(
                "ReplaySample.map must have shape (channels, H, W) or (timesteps, channels, H, W)"
            )
        if self.map.shape[0] != timesteps:
            raise ValueError(
                "ReplaySample.map timestep count must match training arrays; "
                f"expected {timesteps}, got {self.map.shape[0]}"
            )

        if self.features.ndim == 1:
            self.features = np.expand_dims(self.features, axis=0)
        elif self.features.ndim != 2:
            raise ValueError(
                "ReplaySample.features must have shape (feature_dim,) or (timesteps, feature_dim)"
            )
        if self.features.shape[0] != timesteps:
            raise ValueError(
                "ReplaySample.features timestep count must match training arrays; "
                f"expected {timesteps}, got {self.features.shape[0]}"
            )

        value_steps = self.value_preds.shape[0]
        if value_steps not in {timesteps, timesteps + 1}:
            raise ValueError(
                "ReplaySample.value_preds must have length matching timesteps or timesteps + 1; "
                f"got {value_steps} for {timesteps} step(s)"
            )
        self.metadata.setdefault("training_arrays", list(TRAINING_ARRAY_FIELDS))
        self.metadata.setdefault("timesteps", int(timesteps))
        self.metadata.setdefault("value_pred_steps", int(value_steps))

    @property
    def feature_names(self) -> list[str] | None:
        names = self.metadata.get("feature_names")
        if isinstance(names, list):
            return list(names)
        return None

    def conflict_stats(self) -> dict[str, float]:
        names = self.feature_names
        if not names:
            return {}
        stats: dict[str, float] = {}
        for key in REQUIRED_CONFLICT_FEATURES:
            if key in names:
                index = names.index(key)
                column = self.features[..., index]
                stats[key] = float(np.mean(column))
        return stats


def _ensure_conflict_features(metadata: dict[str, Any]) -> None:
    names = metadata.get("feature_names")
    if not isinstance(names, list):
        raise ValueError("Replay sample metadata missing feature_names list")
    missing = [
        feature for feature in REQUIRED_CONFLICT_FEATURES if feature not in names
    ]
    if missing:
        raise ValueError(f"Replay sample missing conflict feature(s): {missing}")


def load_replay_sample(
    sample_path: Path, meta_path: Path | None = None
) -> ReplaySample:
    """Load observation tensors and metadata for replay-driven training scaffolds."""
    if not sample_path.exists():
        raise FileNotFoundError(sample_path)
    payload = np.load(sample_path)
    if "map" not in payload or "features" not in payload:
        raise ValueError(f"Replay sample {sample_path} missing required arrays")
    missing_training = [key for key in TRAINING_ARRAY_FIELDS if key not in payload]
    if missing_training:
        raise ValueError(
            f"Replay sample {sample_path} missing training array(s): {missing_training}"
        )
    map_tensor = payload["map"]
    features = payload["features"]
    actions = payload["actions"]
    old_log_probs = payload["old_log_probs"]
    value_preds = payload["value_preds"]
    rewards = payload["rewards"]
    dones = payload["dones"]

    metadata: dict[str, Any] = {}
    resolved_meta = meta_path or sample_path.with_suffix(".json")
    if resolved_meta.exists():
        metadata = json.loads(resolved_meta.read_text())
    _ensure_conflict_features(metadata)
    return ReplaySample(
        map=map_tensor,
        features=features,
        actions=actions,
        old_log_probs=old_log_probs,
        value_preds=value_preds,
        rewards=rewards,
        dones=dones,
        metadata=metadata,
    )


@dataclass
class ReplayBatch:
    """Mini-batch representation composed from replay samples."""

    maps: np.ndarray
    features: np.ndarray
    actions: np.ndarray
    old_log_probs: np.ndarray
    value_preds: np.ndarray
    rewards: np.ndarray
    dones: np.ndarray
    metadata: dict[str, Any]

    def __post_init__(self) -> None:
        if self.maps.ndim == 4:
            self.maps = self.maps[:, np.newaxis, ...]
        elif self.maps.ndim != 5:
            raise ValueError(
                "maps must have shape (batch, channels, height, width) or "
                "(batch, timesteps, channels, height, width)"
            )

        if self.features.ndim == 2:
            self.features = self.features[:, np.newaxis, :]
        elif self.features.ndim != 3:
            raise ValueError(
                "features must have shape (batch, feature_dim) or (batch, timesteps, feature_dim)"
            )

        for field_name in STEP_ARRAY_FIELDS:
            array = getattr(self, field_name)
            if array.ndim == 1:
                array = array[:, np.newaxis]
            elif array.ndim != 2:
                raise ValueError(
                    f"{field_name} must have shape (batch, timesteps) after stacking"
                )
            setattr(self, field_name, array)

        if self.value_preds.ndim == 1:
            self.value_preds = self.value_preds[:, np.newaxis]
        elif self.value_preds.ndim != 2:
            raise ValueError(
                "value_preds must have shape (batch, timesteps) or (batch, timesteps + 1)"
            )

        if self.maps.shape[0] != self.features.shape[0]:
            raise ValueError("map and feature batch sizes must match")
        batch_size = self.maps.shape[0]
        for field_name in TRAINING_ARRAY_FIELDS:
            array = getattr(self, field_name)
            if array.shape[0] != batch_size:
                raise ValueError(
                    f"{field_name} batch size mismatch: expected {batch_size}, got {array.shape[0]}"
                )
        timestep_length = self.actions.shape[1]
        for field_name in STEP_ARRAY_FIELDS:
            array = getattr(self, field_name)
            expected = timestep_length
            current = array.shape[1]
            if current != expected:
                raise ValueError(
                    f"{field_name} timestep mismatch: expected {expected}, got {current}"
                )
        value_steps = self.value_preds.shape[1]
        if value_steps not in {timestep_length, timestep_length + 1}:
            raise ValueError(
                "value_preds must have length matching timesteps or timesteps + 1 in batch"
            )

    def conflict_stats(self) -> dict[str, float]:
        names = self.metadata.get("feature_names")
        if not isinstance(names, list):
            return {}
        stats: dict[str, float] = {}
        for key in REQUIRED_CONFLICT_FEATURES:
            if key in names:
                idx = names.index(key)
                column = self.features[..., idx]
                values = column.reshape(-1)
                stats[f"{key}_mean"] = float(np.mean(values))
                stats[f"{key}_max"] = float(np.max(values))
        return stats


def build_batch(samples: Sequence[ReplaySample]) -> ReplayBatch:
    """Stack multiple replay samples into a batch for training consumers."""
    if not samples:
        raise ValueError("at least one sample required to build batch")
    maps = np.stack([sample.map for sample in samples], axis=0)
    features = np.stack([sample.features for sample in samples], axis=0)
    actions = np.stack([sample.actions for sample in samples], axis=0)
    old_log_probs = np.stack([sample.old_log_probs for sample in samples], axis=0)
    value_preds = np.stack([sample.value_preds for sample in samples], axis=0)
    rewards = np.stack([sample.rewards for sample in samples], axis=0)
    dones = np.stack([sample.dones for sample in samples], axis=0)
    metadata = {
        "feature_names": samples[0].metadata.get("feature_names"),
        "map_shape": samples[0].metadata.get("map_shape"),
        "training_arrays": samples[0].metadata.get(
            "training_arrays", list(TRAINING_ARRAY_FIELDS)
        ),
        "timesteps": samples[0].metadata.get("timesteps"),
        "value_pred_steps": samples[0].metadata.get("value_pred_steps"),
        "metrics": [sample.metadata.get("metrics") for sample in samples],
    }
    return ReplayBatch(
        maps=maps,
        features=features,
        actions=actions,
        old_log_probs=old_log_probs,
        value_preds=value_preds,
        rewards=rewards,
        dones=dones,
        metadata=metadata,
    )


@dataclass
class ReplayDatasetConfig:
    """Configuration for building replay datasets."""

    entries: list[tuple[Path, Path | None]]
    batch_size: int = 1
    shuffle: bool = False
    seed: int | None = None
    drop_last: bool = False
    streaming: bool = False
    metrics_map: dict[str, dict[str, float]] | None = None
    label: str | None = None

    @classmethod
    def from_manifest(
        cls,
        manifest_path: Path,
        batch_size: int = 1,
        shuffle: bool = False,
        seed: int | None = None,
        drop_last: bool = False,
        streaming: bool = False,
    ) -> ReplayDatasetConfig:
        entries = _load_manifest(manifest_path)
        return cls(
            entries=entries,
            batch_size=batch_size,
            shuffle=shuffle,
            seed=seed,
            drop_last=drop_last,
            streaming=streaming,
            label=manifest_path.stem,
        )

    @classmethod
    def from_capture_dir(
        cls,
        capture_dir: Path,
        batch_size: int = 1,
        shuffle: bool = False,
        seed: int | None = None,
        drop_last: bool = False,
        streaming: bool = False,
    ) -> ReplayDatasetConfig:
        manifest_path = capture_dir / "rollout_sample_manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(manifest_path)
        entries = _load_manifest(manifest_path)
        metrics_path = capture_dir / "rollout_sample_metrics.json"
        metrics_map = None
        if metrics_path.exists():
            payload = json.loads(metrics_path.read_text())
            if isinstance(payload, dict):
                metrics_map = payload.get("samples") or {}
            else:
                metrics_map = payload
        return cls(
            entries=entries,
            batch_size=batch_size,
            shuffle=shuffle,
            seed=seed,
            drop_last=drop_last,
            streaming=streaming,
            metrics_map=metrics_map,
            label=capture_dir.name,
        )


def _resolve_manifest_path(path_spec: Path, base: Path) -> Path:
    """Resolve manifest path specs that may be absolute or repo-relative."""

    candidates = []
    if path_spec.is_absolute():
        candidates.append(path_spec)
    else:
        candidates.append(base / path_spec)
        candidates.append(Path.cwd() / path_spec)
        candidates.append(path_spec)
    for candidate in candidates:
        candidate_path = Path(candidate)
        if candidate_path.exists():
            return candidate_path
    return (base / path_spec).resolve()


def _load_manifest(manifest_path: Path) -> list[tuple[Path, Path | None]]:
    if not manifest_path.exists():
        raise FileNotFoundError(manifest_path)
    data: Any
    text = manifest_path.read_text()
    if manifest_path.suffix.lower() in {".json", ".jsonl"}:
        data = json.loads(text)
    else:
        data = yaml.safe_load(text)
    if isinstance(data, dict):
        samples = data.get("samples")
        if not isinstance(samples, list):
            raise ValueError("Replay manifest payload missing 'samples' list")
        manifest_entries = samples
    elif isinstance(data, list):
        manifest_entries = data
    else:
        raise ValueError("Replay manifest must be a list or mapping with 'samples'")
    entries: list[tuple[Path, Path | None]] = []
    base = manifest_path.parent
    for item in manifest_entries:
        if isinstance(item, str):
            sample_spec = Path(item)
            sample = _resolve_manifest_path(sample_spec, base)
            meta = sample.with_suffix(".json")
        elif isinstance(item, dict):
            if "sample" not in item:
                raise ValueError("Manifest entry missing 'sample' field")
            sample_spec = Path(item["sample"])
            sample = _resolve_manifest_path(sample_spec, base)
            meta_value = item.get("meta")
            if meta_value:
                meta_spec = Path(meta_value)
                meta = _resolve_manifest_path(meta_spec, base)
            else:
                meta = None
        else:
            raise ValueError("Manifest entry must be string or mapping")
        entries.append((sample.resolve(), meta.resolve() if meta else None))
    if not entries:
        raise ValueError("Replay manifest contains no entries")
    return entries


class ReplayDataset:
    """Iterable dataset producing conflict-aware replay batches."""

    def __init__(self, config: ReplayDatasetConfig) -> None:
        if config.batch_size <= 0:
            raise ValueError("batch_size must be positive")
        self.config = config
        self._entries = config.entries
        self._rng = np.random.default_rng(config.seed) if config.shuffle else None
        self._streaming = config.streaming
        self._cached_samples: list[ReplaySample] | None = None
        self._buckets: list[list[int]] | None = None  # indices grouped by shape signature
        self.metrics_map = config.metrics_map or {}
        if self._streaming:
            # In streaming mode, we don’t cache samples globally. We still want
            # to batch by homogeneous shapes, so build signature buckets by
            # peeking each entry once.
            signatures: dict[tuple, list[int]] = {}
            for idx, (sample_path, meta_path) in enumerate(self._entries):
                s = load_replay_sample(sample_path, meta_path)
                sig = (
                    tuple(s.map.shape),
                    tuple(s.features.shape),
                    tuple(getattr(s, f).shape for f in TRAINING_ARRAY_FIELDS),
                )
                signatures.setdefault(sig, []).append(idx)
                self._ensure_sample_metrics(s, (sample_path, meta_path))
            # Deterministic order by signature
            self._buckets = [signatures[key] for key in sorted(signatures.keys())]
        else:
            self._cached_samples = [
                load_replay_sample(sample, meta) for sample, meta in self._entries
            ]
            for sample, entry in zip(self._cached_samples, self._entries):
                self._ensure_sample_metrics(sample, entry)
            # Build buckets based on cached sample shapes
            signatures: dict[tuple, list[int]] = {}
            for idx, s in enumerate(self._cached_samples):
                sig = (
                    tuple(s.map.shape),
                    tuple(s.features.shape),
                    tuple(getattr(s, f).shape for f in TRAINING_ARRAY_FIELDS),
                )
                signatures.setdefault(sig, []).append(idx)
            self._buckets = [signatures[key] for key in sorted(signatures.keys())]
        self.baseline_metrics = self._aggregate_metrics()

    def _ensure_homogeneous(self, samples: Sequence[ReplaySample]) -> None:
        # Retained for backward-compatibility, but unused after bucketing.
        # Bucketing guarantees homogeneity per batch.
        return

    def __len__(self) -> int:
        if not self._buckets:
            return 0
        batch_size = self.config.batch_size
        total = 0
        for bucket in self._buckets:
            count = len(bucket)
            full, rem = divmod(count, batch_size)
            if rem and not self.config.drop_last:
                full += 1
            total += full
        return total

    def __iter__(self) -> Iterator[ReplayBatch]:
        if not self._buckets:
            return
        for bucket in self._buckets:
            indices = list(bucket)
            if self._rng is not None:
                self._rng.shuffle(indices)
            for start in range(0, len(indices), self.config.batch_size):
                batch_indices = indices[start : start + self.config.batch_size]
                if len(batch_indices) < self.config.batch_size and self.config.drop_last:
                    continue
                samples = [self._fetch_sample(index) for index in batch_indices]
                yield build_batch(samples)

    def _fetch_sample(self, index: int) -> ReplaySample:
        if self._cached_samples is not None:
            return self._cached_samples[index]
        sample = load_replay_sample(*self._entries[index])
        self._ensure_sample_metrics(sample, self._entries[index])
        return sample

    def _ensure_sample_metrics(
        self, sample: ReplaySample, entry: tuple[Path, Path | None]
    ) -> None:
        existing = sample.metadata.get("metrics")
        if isinstance(existing, dict) and existing:
            return
        metrics = self.metrics_map.get(entry[0].name)
        if metrics is not None:
            sample.metadata["metrics"] = metrics

    def _aggregate_metrics(self) -> dict[str, float]:
        metrics_sources: list[dict[str, float]] = []
        if self.metrics_map:
            metrics_sources = [dict(values) for values in self.metrics_map.values()]
        elif self._cached_samples is not None:
            for sample in self._cached_samples:
                sample_metrics = sample.metadata.get("metrics")
                if isinstance(sample_metrics, dict) and sample_metrics:
                    metrics_sources.append(dict(sample_metrics))

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


def frames_to_replay_sample(frames: Sequence[dict[str, Any]]) -> ReplaySample:
    """Convert collected trajectory frames into a replay sample."""

    if not frames:
        raise ValueError("frames sequence cannot be empty")

    # TODO(WP3 Stage 5): drop this legacy export translator once external replay
    # payloads move to native DTO artefacts.

    timesteps = len(frames)
    map_seq = np.stack(
        [np.asarray(frame["map"], dtype=np.float32) for frame in frames], axis=0
    )
    feature_seq = np.stack(
        [np.asarray(frame["features"], dtype=np.float32) for frame in frames], axis=0
    )

    raw_lookup = (
        dict(frames[0].get("action_lookup", {}))
        if frames[0].get("action_lookup")
        else {}
    )
    action_lookup: dict[str, int]
    if raw_lookup and all(isinstance(key, int) for key in raw_lookup):
        action_lookup = {value: int(key) for key, value in raw_lookup.items()}
    else:
        action_lookup = raw_lookup
    action_ids: list[int] = []
    for frame in frames:
        if frame.get("action_id") is not None:
            action_ids.append(int(frame["action_id"]))
        else:
            action = frame.get("action") or {}
            try:
                key = json.dumps(action, sort_keys=True)
            except TypeError:
                key = str(action)
            if key not in action_lookup:
                action_lookup[key] = len(action_lookup)
            action_ids.append(action_lookup[key])

    actions = np.asarray(action_ids, dtype=np.int64)

    log_probs = np.asarray(
        [float(frame.get("log_prob", 0.0)) for frame in frames], dtype=np.float32
    )

    rewards = np.asarray(
        [float((frame.get("rewards") or [0.0])[-1]) for frame in frames],
        dtype=np.float32,
    )
    dones = np.asarray(
        [bool((frame.get("dones") or [False])[-1]) for frame in frames], dtype=np.bool_
    )

    value_preds_seq = np.asarray(
        [float(frame.get("value_pred", 0.0)) for frame in frames], dtype=np.float32
    )
    if value_preds_seq.size:
        value_preds = np.concatenate([value_preds_seq, [value_preds_seq[-1]]])
    else:
        value_preds = np.zeros(1, dtype=np.float32)

    metadata = dict(frames[-1].get("metadata", {}))
    metadata.update(
        {
            "training_arrays": list(TRAINING_ARRAY_FIELDS),
            "timesteps": timesteps,
            "value_pred_steps": len(value_preds),
            "action_lookup": action_lookup,
            "action_dim": int(actions.max() + 1) if actions.size else 1,
        }
    )

    return ReplaySample(
        map=map_seq,
        features=feature_seq,
        actions=actions,
        old_log_probs=log_probs,
        value_preds=value_preds,
        rewards=rewards,
        dones=dones,
        metadata=metadata,
    )
