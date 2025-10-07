# isort: skip_file
"""Behaviour cloning utilities shim.

Exports BC training utilities from the PyTorch backend when available, while
preserving importability in environments without Torch.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from townlet.policy.models import torch_available, TorchNotAvailableError


if torch_available():  # pragma: no cover - exercised in ML-enabled envs
    # Re-export concrete implementations from the backend package
    from townlet.policy.backends.pytorch.bc import (
        BCTrainer,
        BCTrainingConfig,
        BCTrajectoryDataset,
        evaluate_bc_policy,
        load_bc_samples,
    )
else:  # pragma: no cover
    # Minimal types and helpers to keep imports working without Torch
    @dataclass
    class BCTrainingConfig:
        learning_rate: float = 1e-3
        batch_size: int = 64
        epochs: int = 5
        weight_decay: float = 0.0
        device: str = "cpu"

    class BCTrajectoryDataset:  # type: ignore[misc]
        def __init__(self, *_: Any, **__: Any) -> None:
            raise TorchNotAvailableError("PyTorch required for BC dataset")

    class BCTrainer:  # type: ignore[misc]
        def __init__(self, *_: Any, **__: Any) -> None:
            raise TorchNotAvailableError("PyTorch required for BC training")

        def fit(self, *_args: Any, **_kwargs: Any) -> Mapping[str, float]:
            raise TorchNotAvailableError("PyTorch required for BC training")

        def evaluate(self, *_args: Any, **_kwargs: Any) -> Mapping[str, float]:
            raise TorchNotAvailableError("PyTorch required for BC training")

    def evaluate_bc_policy(*_args: Any, **_kwargs: Any) -> Mapping[str, float]:  # type: ignore[misc]
        raise TorchNotAvailableError("PyTorch required for BC evaluation")

    # load_bc_samples does not require Torch; keep a lightweight version here
    def load_bc_samples(manifest_path: Path):  # type: ignore[misc]
        from townlet.policy.replay import load_replay_sample

        manifest_data = json.loads(manifest_path.read_text())
        manifest_dir = manifest_path.parent
        if not isinstance(manifest_data, list):
            raise ValueError("BC manifest must be a list")
        samples = []
        for entry in manifest_data:
            if not isinstance(entry, Mapping):
                continue
            sample_spec = Path(entry.get("sample", ""))
            meta_spec = Path(entry.get("meta", ""))

            sample_path = None
            for candidate in (
                sample_spec if sample_spec.is_absolute() else manifest_dir / sample_spec,
                sample_spec,
            ):
                if candidate and Path(candidate).exists():
                    sample_path = Path(candidate)
                    break

            meta_path = None
            for candidate in (
                meta_spec if meta_spec.is_absolute() else manifest_dir / meta_spec,
                meta_spec,
            ):
                if candidate and Path(candidate).exists():
                    meta_path = Path(candidate)
                    break

            if sample_path is None or meta_path is None:
                continue
            samples.append(load_replay_sample(sample_path, meta_path))
        if not samples:
            raise ValueError("BC manifest contained no valid samples")
        return samples

__all__ = [
    "BCTrainer",
    "BCTrainingConfig",
    "BCTrajectoryDataset",
    "evaluate_bc_policy",
    "load_bc_samples",
]
