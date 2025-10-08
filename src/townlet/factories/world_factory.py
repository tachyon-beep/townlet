"""Factory helpers for world runtimes."""

from __future__ import annotations

import importlib
from typing import Any

from townlet.factories._utils import extract_provider
from townlet.factories.registry import resolve
from townlet.ports.world import WorldRuntime


def create_world(cfg: Any) -> WorldRuntime:
    """Create a world runtime from configuration."""

    importlib.import_module("townlet.adapters.world_default")
    importlib.import_module("townlet.testing.dummies")
    provider, options = extract_provider(cfg, "world", "default")
    factory = resolve("world", provider)
    world = factory(cfg=cfg, **dict(options))
    return world  # type: ignore[return-value]


__all__ = ["create_world"]
