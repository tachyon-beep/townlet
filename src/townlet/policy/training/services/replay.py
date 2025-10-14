"""Replay dataset service (torch-free).

This service handles replay dataset management, batch summarization, and
manifest resolution. All operations are torch-free and importable without
PyTorch installed.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from townlet.config import SimulationConfig
    from townlet.policy.replay import ReplayBatch, ReplayDataset, ReplayDatasetConfig, ReplaySample

# Default manifest location (relative to repo root)
DEFAULT_REPLAY_MANIFEST = Path("docs/samples/replay_manifest.json")


class ReplayDatasetService:
    """Torch-free replay dataset service.

    Provides utilities for loading, summarizing, and building replay datasets
    without requiring PyTorch. Handles manifest resolution and batch statistics.

    Example:
        service = ReplayDatasetService(config)
        dataset = service.build_dataset(manifest_path)
        summary = service.summarize_dataset(dataset)
    """

    def __init__(self, config: SimulationConfig) -> None:
        """Initialize replay dataset service.

        Args:
            config: Simulation configuration.
        """
        self.config = config

    def summarize_sample(
        self,
        sample_path: Path,
        meta_path: Path | None = None,
    ) -> dict[str, float]:
        """Load a replay sample and return conflict-aware statistics.

        Args:
            sample_path: Path to replay sample NPZ file.
            meta_path: Optional path to metadata JSON file.

        Returns:
            Dictionary with batch statistics including conflict metrics.
        """
        from townlet.policy.replay import build_batch, load_replay_sample

        sample: ReplaySample = load_replay_sample(sample_path, meta_path)
        batch = build_batch([sample])
        summary = self.summarize_batch(batch, batch_index=1)
        return summary

    def summarize_batch(
        self,
        batch: ReplayBatch,
        batch_index: int = 1,
    ) -> dict[str, float]:
        """Summarize a replay batch with conflict statistics.

        Args:
            batch: Replay batch to summarize.
            batch_index: Batch number for reporting.

        Returns:
            Dictionary with batch size, feature dim, and conflict stats.
        """
        summary = {
            "batch": float(batch_index),
            "batch_size": float(batch.features.shape[0]),
            "feature_dim": float(batch.features.shape[1]),
        }
        # Add conflict statistics with "conflict." prefix
        for key, value in batch.conflict_stats().items():
            summary[f"conflict.{key}"] = value
        return summary

    def summarize_dataset(
        self,
        dataset: ReplayDataset | Iterable[ReplayBatch],
    ) -> dict[str, float]:
        """Summarize all batches in a replay dataset.

        Args:
            dataset: Replay dataset or iterable of batches.

        Returns:
            Summary of the last batch processed.

        Raises:
            ValueError: If dataset yields no batches.
        """
        summary: dict[str, float] = {}
        for idx, batch in enumerate(dataset, start=1):
            summary = self.summarize_batch(batch, batch_index=idx)
            print(f"Replay batch {idx}:", summary)

        if not summary:
            raise ValueError("Replay dataset yielded no batches")

        return summary

    def summarize_batch_pairs(
        self,
        pairs: Iterable[tuple[Path, Path | None]],
    ) -> dict[str, float]:
        """Summarize multiple replay sample pairs as a batch.

        Args:
            pairs: Iterable of (sample_path, meta_path) tuples.

        Returns:
            Summary of the combined batch.

        Raises:
            ValueError: If no pairs provided.
        """
        entries = list(pairs)
        if not entries:
            raise ValueError("Replay batch requires at least one entry")

        from townlet.policy.replay import ReplayDataset, ReplayDatasetConfig

        config = ReplayDatasetConfig(entries=entries, batch_size=len(entries))
        dataset = ReplayDataset(config)
        return self.summarize_dataset(dataset)

    def build_dataset(
        self,
        config: ReplayDatasetConfig | Path | str | None = None,
    ) -> ReplayDataset:
        """Build a replay dataset from configuration or manifest path.

        Args:
            config: ReplayDatasetConfig, manifest path, or None (uses default).

        Returns:
            Constructed replay dataset.

        Raises:
            FileNotFoundError: If manifest cannot be located.
        """
        from townlet.policy.replay import ReplayDataset, ReplayDatasetConfig

        if isinstance(config, ReplayDatasetConfig):
            dataset_config = config
        else:
            manifest_path = self.resolve_manifest(config)
            dataset_config = ReplayDatasetConfig.from_manifest(manifest_path)

        return ReplayDataset(dataset_config)

    def resolve_manifest(
        self,
        manifest: Path | str | None,
    ) -> Path:
        """Resolve replay manifest path from various sources.

        Searches in order:
        1. Provided manifest argument (absolute or relative to cwd)
        2. config.training.replay_manifest
        3. Default manifest (docs/samples/replay_manifest.json)

        Args:
            manifest: Manifest path or None.

        Returns:
            Resolved manifest path.

        Raises:
            FileNotFoundError: If manifest cannot be located.
        """
        candidates: list[Path] = []

        # Add provided manifest and config manifest
        for value in (manifest, getattr(self.config.training, "replay_manifest", None)):
            if value:
                path = Path(value)
                candidates.append(path)
                candidates.append(Path.cwd() / path)

        # Add default manifest (relative to repo root)
        # __file__ is at src/townlet/policy/training/services/replay.py
        # parents[5] gives us the repo root (above src/)
        repo_root = Path(__file__).resolve().parents[5]
        candidates.append(repo_root / DEFAULT_REPLAY_MANIFEST)
        candidates.append(Path.cwd() / DEFAULT_REPLAY_MANIFEST)

        # Try each candidate, return first that exists
        checked: set[str] = set()
        for candidate in candidates:
            expanded = candidate.expanduser()
            resolved = expanded.resolve(strict=False)
            key = str(resolved)

            if key in checked:
                continue
            checked.add(key)

            if resolved.exists():
                return resolved

        raise FileNotFoundError(
            "Replay manifest not provided and default manifest could not be located"
        )


__all__ = ["ReplayDatasetService"]
