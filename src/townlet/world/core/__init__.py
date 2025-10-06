"""Core world abstractions and context façade."""

from __future__ import annotations

from .context import WorldContext
from .runtime_adapter import WorldRuntimeAdapter, ensure_world_adapter

__all__ = [
    "WorldContext",
    "WorldRuntimeAdapter",
    "ensure_world_adapter",
]
