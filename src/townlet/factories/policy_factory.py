"""Factory helpers for policy backends."""

from __future__ import annotations

import importlib
from typing import Any

from townlet.factories._utils import extract_provider
from townlet.factories.registry import resolve
from townlet.ports.policy import PolicyBackend


def create_policy(cfg: Any) -> PolicyBackend:
    """Create a policy backend from configuration."""

    importlib.import_module("townlet.adapters.policy_scripted")
    importlib.import_module("townlet.testing.dummies")
    provider, options = extract_provider(cfg, "policy", "scripted")
    factory = resolve("policy", provider)
    policy = factory(cfg=cfg, **dict(options))
    return policy  # type: ignore[return-value]


__all__ = ["create_policy"]
