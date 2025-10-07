"""Core configuration helpers shared across domain modules."""

from __future__ import annotations

from collections.abc import Mapping

from pydantic import BaseModel, ConfigDict, model_validator


class IntRange(BaseModel):
    """Helper schema describing inclusive integer ranges."""

    min: int
    max: int

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    def _coerce(cls, value: object) -> dict[str, int]:  # noqa: N805
        if isinstance(value, Mapping):
            lo = int(value.get("min", 0))
            hi = int(value.get("max", value.get("min", 0)))
            return {"min": lo, "max": hi}
        if isinstance(value, (list, tuple)):
            items = list(value)
            if len(items) != 2:
                raise ValueError("Range list must contain exactly two values")
            return {"min": int(items[0]), "max": int(items[1])}
        if isinstance(value, int):
            return {"min": value, "max": value}
        raise TypeError(f"Unsupported range value: {value!r}")

    @model_validator(mode="after")
    def _validate_bounds(self) -> IntRange:
        if self.max < self.min:
            raise ValueError("Range max must be >= min")
        return self


class FloatRange(BaseModel):
    """Helper schema describing inclusive float ranges."""

    min: float
    max: float

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    def _coerce(cls, value: object) -> dict[str, float]:  # noqa: N805
        if isinstance(value, Mapping):
            lo = float(value.get("min", 0.0))
            hi = float(value.get("max", value.get("min", 0.0)))
            return {"min": lo, "max": hi}
        if isinstance(value, (list, tuple)):
            items = list(value)
            if len(items) != 2:
                raise ValueError("Float range list must contain exactly two values")
            return {"min": float(items[0]), "max": float(items[1])}
        if isinstance(value, (int, float)):
            val = float(value)
            return {"min": val, "max": val}
        raise TypeError(f"Unsupported float range value: {value!r}")

    @model_validator(mode="after")
    def _validate_bounds(self) -> FloatRange:
        if self.max < self.min:
            raise ValueError("Float range max must be >= min")
        return self


__all__ = ["FloatRange", "IntRange"]

