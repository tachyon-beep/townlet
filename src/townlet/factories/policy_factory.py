"""Factory helpers for policy backends."""

from __future__ import annotations

import importlib
from typing import Any, cast

from townlet.factories._utils import extract_provider
from townlet.factories.registry import resolve
from townlet.ports.policy import PolicyBackend
from townlet.ports.world import WorldRuntime


def create_policy(cfg: Any, world: WorldRuntime | None = None) -> PolicyBackend:
    """Create a policy backend from configuration.

    When ``world`` is provided the factory will bind the resulting policy to it if the
    policy exposes an optional ``bind_world`` helper. This keeps the composition root
    free from adapter-specific handshakes.
    """

    importlib.import_module("townlet.adapters.policy_scripted")
    importlib.import_module("townlet.testing.dummies")
    provider, options = extract_provider(cfg, "policy", "scripted")
    factory = resolve("policy", provider)
    policy = cast(PolicyBackend, factory(cfg=cfg, **dict(options)))
    maybe_bind = getattr(policy, "bind_world", None)
    if world is not None and callable(maybe_bind):
        maybe_bind(world)
    return policy


__all__ = ["create_policy"]
