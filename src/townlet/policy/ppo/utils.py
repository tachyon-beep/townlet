"""Shim to defer PPO utils import until ML extras are available.

This preserves the legacy import path ``townlet.policy.ppo.utils`` while
avoiding hard failures during test collection on environments without Torch.
Consumers should import these utilities only when PyTorch is installed.
"""

from __future__ import annotations

from townlet.policy.models import torch_available

if torch_available():  # pragma: no cover - exercised in ML-enabled envs
    # Re-export real implementations from the backend package
    from townlet.policy.backends.pytorch.ppo_utils import *  # noqa: F403
else:  # pragma: no cover
    # Provide a helpful import-time error for direct usages in non-ML envs.
    raise ModuleNotFoundError(
        "townlet.policy.ppo.utils requires the optional 'ml' extra (PyTorch)."
    )
