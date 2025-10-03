"""Torch-based policy/value networks for Townlet PPO."""

from __future__ import annotations

from dataclasses import dataclass

try:
    import torch
    import torch.nn as nn
except ModuleNotFoundError:  # pragma: no cover - environment guard
    torch = None  # type: ignore[assignment]
    nn = None  # type: ignore[assignment]


def torch_available() -> bool:
    """Return True if PyTorch is available in the runtime."""
    return torch is not None


class TorchNotAvailableError(RuntimeError):
    """Raised when a Torch-dependent component is used without PyTorch."""


@dataclass
class ConflictAwarePolicyConfig:
    feature_dim: int
    map_shape: tuple[int, int, int]
    action_dim: int
    hidden_dim: int = 256


if torch_available():

    class ConflictAwarePolicyNetwork(nn.Module):
        """Simple convolution + MLP network producing policy logits and value."""

        def __init__(self, cfg: ConflictAwarePolicyConfig) -> None:
            super().__init__()
            channels, height, width = cfg.map_shape
            flat_map = channels * height * width
            self.map_encoder = nn.Sequential(
                nn.Flatten(),
                nn.Linear(flat_map, cfg.hidden_dim),
                nn.ReLU(),
            )
            self.feature_encoder = nn.Sequential(
                nn.Linear(cfg.feature_dim, cfg.hidden_dim),
                nn.ReLU(),
            )
            combined_dim = cfg.hidden_dim * 2
            self.shared = nn.Sequential(
                nn.Linear(combined_dim, cfg.hidden_dim),
                nn.ReLU(),
            )
            self.policy_head = nn.Linear(cfg.hidden_dim, cfg.action_dim)
            self.value_head = nn.Linear(cfg.hidden_dim, 1)

        def forward(
            self, map_tensor: torch.Tensor, features: torch.Tensor
        ) -> tuple[torch.Tensor, torch.Tensor]:  # type: ignore[override]
            encoded_map = self.map_encoder(map_tensor)
            encoded_features = self.feature_encoder(features)
            hidden = torch.cat([encoded_map, encoded_features], dim=-1)
            hidden = self.shared(hidden)
            logits = self.policy_head(hidden)
            value = self.value_head(hidden).squeeze(-1)
            return logits, value

else:

    class ConflictAwarePolicyNetwork:  # type: ignore[too-few-public-methods,misc]
        """Placeholder that raises if PyTorch is unavailable."""

        def __init__(self, cfg: ConflictAwarePolicyConfig) -> None:  # noqa: D401
            raise TorchNotAvailableError(
                "PyTorch is required to build ConflictAwarePolicyNetwork. "
                "Install torch (pip install torch) or use the replay-only workflow."
            )

        def __call__(self, *args: object, **kwargs: object) -> None:
            raise TorchNotAvailableError(
                "PyTorch is required to call ConflictAwarePolicyNetwork."
            )
