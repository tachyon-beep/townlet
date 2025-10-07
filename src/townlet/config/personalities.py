"""Personality assignment configuration and helpers."""

from __future__ import annotations

import hashlib
import random

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, model_validator


class PersonalityAssignmentConfig(BaseModel):
    """Configure personality profile distribution and overrides."""

    distribution: dict[str, float] = Field(default_factory=lambda: {"balanced": 1.0})
    overrides: dict[str, str] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow")

    _cumulative_weights: list[tuple[str, float]] = PrivateAttr(default_factory=list)

    @model_validator(mode="after")
    def _normalise(self) -> PersonalityAssignmentConfig:

        normalized: dict[str, float] = {}
        for name, weight in self.distribution.items():
            key = str(name).lower()
            value = float(weight)
            if value < 0.0:
                raise ValueError("Personality distribution weight must be non-negative")
            normalized[key] = normalized.get(key, 0.0) + value

        total = sum(normalized.values())
        if total <= 0.0:
            raise ValueError("Personality distribution must sum to a positive value")

        cleaned_overrides: dict[str, str] = {}
        for agent_id, profile in self.overrides.items():
            if profile is None:
                continue
            profile_key = str(profile).lower()
            cleaned_overrides[str(agent_id)] = profile_key

        cumulative = 0.0
        cumulative_weights: list[tuple[str, float]] = []
        for key, value in sorted(normalized.items()):
            cumulative += value / total
            cumulative_weights.append((key, min(cumulative, 1.0)))

        object.__setattr__(self, "distribution", normalized)
        object.__setattr__(self, "overrides", cleaned_overrides)
        self._cumulative_weights = cumulative_weights
        return self

    def resolve(self, agent_id: str, *, seed: int | None) -> str:
        """Resolve a personality profile for ``agent_id`` using optional seed."""

        override = self.overrides.get(agent_id)
        if override:
            return override
        if not self._cumulative_weights:
            return "balanced"
        base = f"{seed}:{agent_id}" if seed is not None else agent_id
        digest = hashlib.sha256(base.encode("utf-8")).digest()
        rng = random.Random(int.from_bytes(digest[:8], "big", signed=False))
        value = rng.random()
        for name, threshold in self._cumulative_weights:
            if value <= threshold:
                return name
        return self._cumulative_weights[-1][0]

    def available_profiles(self) -> tuple[str, ...]:
        """Return the list of profile keys available after normalisation."""

        if not self._cumulative_weights:
            return ("balanced",)
        return tuple(name for name, _ in self._cumulative_weights)


__all__ = ["PersonalityAssignmentConfig"]
