"""Rivalry state helpers used by conflict intro scaffolding.

These utilities intentionally stay decoupled from the world grid so we can unit
 test rivalry increments/decay behaviour in isolation before wiring into the
 main simulation loop.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field


def _clamp(value: float, *, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass
class RivalryParameters:
    """Tuning knobs for rivalry evolution.

    The defaults align with the conceptual design placeholder values and are
    expected to be replaced with config-backed settings during integration.
    """

    increment_per_conflict: float = 0.15
    decay_per_tick: float = 0.01
    min_value: float = 0.0
    max_value: float = 1.0
    avoid_threshold: float = 0.7
    eviction_threshold: float = 0.05
    max_edges: int = 6


@dataclass
class RivalryLedger:
    """Maintains rivalry scores against other agents for a single actor."""

    owner_id: str
    params: RivalryParameters = field(default_factory=RivalryParameters)
    eviction_hook: Callable[[str, str, str], None] | None = None
    _scores: dict[str, float] = field(default_factory=dict)

    def apply_conflict(self, other_id: str, *, intensity: float = 1.0) -> float:
        """Increase rivalry against `other_id` based on the conflict intensity."""
        delta = self.params.increment_per_conflict * intensity
        updated = _clamp(
            self._scores.get(other_id, 0.0) + delta,
            low=self.params.min_value,
            high=self.params.max_value,
        )
        self._scores[other_id] = updated
        evicted: list[str] = []
        if self.params.max_edges > 0 and len(self._scores) > self.params.max_edges:
            # Drop weakest edges to keep the ledger bounded.
            weakest = sorted(
                self._scores.items(),
                key=lambda item: item[1],
                reverse=True,
            )[self.params.max_edges :]
            for other, _ in weakest:
                if self._scores.pop(other, None) is not None:
                    evicted.append(other)
        for other in evicted:
            self._emit_eviction(other, reason="capacity")
        return updated

    def decay(self, ticks: int = 1) -> None:
        """Apply passive decay across all rivalry edges."""
        if ticks <= 0 or not self._scores:
            return
        decay_amount = self.params.decay_per_tick * float(ticks)
        for other_id, value in list(self._scores.items()):
            updated = _clamp(
                value - decay_amount,
                low=self.params.min_value,
                high=self.params.max_value,
            )
            if updated <= self.params.eviction_threshold:
                if self._scores.pop(other_id, None) is not None:
                    self._emit_eviction(other_id, reason="decay")
            else:
                self._scores[other_id] = updated

    def inject(self, pairs: Iterable[tuple[str, float]]) -> None:
        """Seed rivalry scores from persisted state for round-tripping tests."""
        for other_id, value in pairs:
            self._scores[other_id] = _clamp(
                value,
                low=self.params.min_value,
                high=self.params.max_value,
            )

    def score_for(self, other_id: str) -> float:
        return self._scores.get(other_id, 0.0)

    def should_avoid(self, other_id: str) -> bool:
        """Return True when rivalry exceeds the avoidance threshold."""
        return self._scores.get(other_id, 0.0) >= self.params.avoid_threshold

    def top_rivals(self, limit: int) -> list[tuple[str, float]]:
        """Return the strongest rivalry edges sorted descending."""
        if limit <= 0:
            return []
        sorted_edges = sorted(
            self._scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )
        return sorted_edges[:limit]

    def remove(self, other_id: str, *, reason: str = "removed") -> None:
        if other_id not in self._scores:
            return
        self._scores.pop(other_id, None)
        self._emit_eviction(other_id, reason=reason)

    def encode_features(self, limit: int) -> list[float]:
        """Encode rivalry magnitudes into a fixed-width list for observations."""
        features: list[float] = []
        for _, value in self.top_rivals(limit):
            features.append(value)
        while len(features) < limit:
            features.append(0.0)
        return features

    def snapshot(self) -> dict[str, float]:
        """Return a copy of rivalry scores for telemetry serialization."""
        return dict(self._scores)

    def _emit_eviction(self, other_id: str, *, reason: str) -> None:
        if self.eviction_hook is None:
            return
        self.eviction_hook(self.owner_id, other_id, reason)
