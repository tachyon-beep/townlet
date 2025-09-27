"""Behaviour cloning utilities."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence

import json
import numpy as np

from townlet.policy.models import (
    ConflictAwarePolicyConfig,
    ConflictAwarePolicyNetwork,
    TorchNotAvailableError,
    torch_available,
)
from townlet.policy.replay import ReplaySample, load_replay_sample

if torch_available():  # pragma: no branch
    import torch
    from torch import nn
    from torch.utils.data import DataLoader, Dataset
else:  # pragma: no cover
    torch = None  # type: ignore
    nn = None  # type: ignore
    DataLoader = object  # type: ignore
    Dataset = object  # type: ignore


@dataclass
class BCTrainingConfig:
    learning_rate: float = 1e-3
    batch_size: int = 64
    epochs: int = 5
    weight_decay: float = 0.0
    device: str = "cpu"


@dataclass
class BCDatasetConfig:
    manifest: Path


class BCTrajectoryDataset(Dataset):  # type: ignore[misc]
    """Torch dataset flattening replay samples for behaviour cloning."""

    def __init__(self, samples: Sequence[ReplaySample]) -> None:
        if not torch_available():  # pragma: no cover - guard
            raise TorchNotAvailableError("PyTorch required for BC training")
        maps: List[np.ndarray] = []
        features: List[np.ndarray] = []
        actions: List[int] = []
        for sample in samples:
            for idx in range(sample.actions.shape[0]):
                map_frame = sample.map[idx]
                if map_frame.ndim == 3:  # (H, W, C)
                    map_frame = np.transpose(map_frame, (2, 0, 1))
                elif map_frame.ndim == 4:  # (C, H, W, ?) unexpected
                    map_frame = map_frame.squeeze()
                maps.append(map_frame.astype(np.float32))
                features.append(sample.features[idx].astype(np.float32))
                actions.append(int(sample.actions[idx]))
        if not maps:
            raise ValueError("BC dataset requires at least one frame")
        self._maps = np.stack(maps, axis=0)
        self._features = np.stack(features, axis=0)
        self._actions = np.asarray(actions, dtype=np.int64)
        self.map_shape = tuple(self._maps.shape[1:])
        self.feature_dim = int(self._features.shape[1])
        self.action_dim = int(np.max(self._actions)) + 1 if self._actions.size else 1

    def __len__(self) -> int:
        return self._actions.shape[0]

    def __getitem__(self, index: int):  # type: ignore[override]
        map_tensor = torch.from_numpy(self._maps[index]).float()
        feature_tensor = torch.from_numpy(self._features[index]).float()
        action_tensor = torch.tensor(self._actions[index], dtype=torch.long)
        return map_tensor, feature_tensor, action_tensor


def load_bc_samples(manifest_path: Path) -> List[ReplaySample]:
    manifest_data = json.loads(manifest_path.read_text())
    manifest_dir = manifest_path.parent
    if not isinstance(manifest_data, list):
        raise ValueError("BC manifest must be a list")
    samples: List[ReplaySample] = []
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


class BCTrainer:
    """Lightweight supervised trainer for behaviour cloning."""

    def __init__(self, config: BCTrainingConfig, policy_config: ConflictAwarePolicyConfig) -> None:
        if not torch_available():  # pragma: no cover - guard
            raise TorchNotAvailableError("PyTorch required for BC training")
        self.config = config
        self.policy_config = policy_config
        self.device = torch.device(config.device)
        self.model = ConflictAwarePolicyNetwork(policy_config).to(self.device)
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=config.learning_rate,
            weight_decay=config.weight_decay,
        )

    def fit(self, dataset: BCTrajectoryDataset) -> Mapping[str, float]:
        loader = DataLoader(dataset, batch_size=self.config.batch_size, shuffle=True)
        self.model.train()
        last_loss = 0.0
        for _ in range(self.config.epochs):
            for map_batch, feature_batch, action_batch in loader:
                map_batch = map_batch.to(self.device)
                feature_batch = feature_batch.to(self.device)
                action_batch = action_batch.to(self.device)
                logits, _ = self.model(map_batch, feature_batch)
                loss = self.criterion(logits, action_batch)
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                last_loss = float(loss.item())
        accuracy = self.evaluate(dataset)["accuracy"]
        return {"loss": last_loss, "accuracy": accuracy}

    def evaluate(self, dataset: BCTrajectoryDataset) -> Mapping[str, float]:
        loader = DataLoader(dataset, batch_size=self.config.batch_size, shuffle=False)
        self.model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for map_batch, feature_batch, action_batch in loader:
                map_batch = map_batch.to(self.device)
                feature_batch = feature_batch.to(self.device)
                action_batch = action_batch.to(self.device)
                logits, _ = self.model(map_batch, feature_batch)
                preds = logits.argmax(dim=-1)
                correct += int((preds == action_batch).sum().item())
                total += int(action_batch.shape[0])
        accuracy = float(correct / total) if total else 0.0
        return {"accuracy": accuracy, "samples": float(total)}


def evaluate_bc_policy(
    model: ConflictAwarePolicyNetwork,
    dataset: BCTrajectoryDataset,
    device: str = "cpu",
) -> Mapping[str, float]:
    if not torch_available():  # pragma: no cover
        raise TorchNotAvailableError("PyTorch required for BC evaluation")
    loader = DataLoader(dataset, batch_size=128, shuffle=False)
    model.eval()
    device_obj = torch.device(device)
    model.to(device_obj)
    correct = 0
    total = 0
    with torch.no_grad():
        for map_batch, feature_batch, action_batch in loader:
            map_batch = map_batch.to(device_obj)
            feature_batch = feature_batch.to(device_obj)
            action_batch = action_batch.to(device_obj)
            logits, _ = model(map_batch, feature_batch)
            preds = logits.argmax(dim=-1)
            correct += int((preds == action_batch).sum().item())
            total += int(action_batch.shape[0])
    return {"accuracy": float(correct / total) if total else 0.0, "samples": float(total)}
