"""Core world abstractions and context façade."""

from __future__ import annotations

__all__ = [
    "WorldContext",
    "WorldRuntimeAdapter",
    "ensure_world_adapter",
]


def __getattr__(name: str) -> object:  # pragma: no cover - lazy import glue
    if name == "WorldContext":
        from .context import WorldContext as _WorldContext

        return _WorldContext
    if name in {"WorldRuntimeAdapter", "ensure_world_adapter"}:
        from .runtime_adapter import (
            WorldRuntimeAdapter as _WorldRuntimeAdapter,
        )
        from .runtime_adapter import (
            ensure_world_adapter as _ensure_world_adapter,
        )

        return {
            "WorldRuntimeAdapter": _WorldRuntimeAdapter,
            "ensure_world_adapter": _ensure_world_adapter,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:  # pragma: no cover - module reflection helper
    return sorted(__all__)
