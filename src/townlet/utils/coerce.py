"""Helpers for coercing untyped payload values into numeric primitives."""

from __future__ import annotations

from typing import SupportsFloat, SupportsInt


def coerce_int(value: object, *, default: int = 0) -> int:
    """Best-effort conversion mirroring snapshot/telemetry semantics."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return default
    if isinstance(value, SupportsInt):
        try:
            return int(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return default
    return default


def coerce_float(value: object, *, default: float | None = None) -> float:
    """Convert dynamic inputs to float, optionally returning a default."""
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            if default is not None:
                return default
            raise
    if isinstance(value, SupportsFloat):
        try:
            return float(value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            if default is not None:
                return default
            raise
    if default is not None:
        return default
    raise TypeError("value is not numeric")
