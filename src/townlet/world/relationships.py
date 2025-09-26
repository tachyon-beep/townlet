"""Relationship ledger for Phase 4 social systems."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Tuple


def _clamp(value: float, *, low: float, high: float) -> float:
    return max(low, min(high, value))


@dataclass
class RelationshipParameters:
    """Tuning knobs for relationship tie evolution."""

    max_edges: int = 6
    trust_decay: float = 0.0
    familiarity_decay: float = 0.0
    rivalry_decay: float = 0.01


@dataclass
class RelationshipTie:
    trust: float = 0.0
    familiarity: float = 0.0
    rivalry: float = 0.0

    def as_dict(self) -> Dict[str, float]:
        return {
            "trust": self.trust,
            "familiarity": self.familiarity,
            "rivalry": self.rivalry,
        }


EvictionHook = Callable[[str, str, str], None]


class RelationshipLedger:
    """Maintains multi-dimensional ties for a single agent."""

    def __init__(
        self,
        *,
        owner_id: str,
        params: RelationshipParameters | None = None,
        eviction_hook: EvictionHook | None = None,
    ) -> None:
        self.params = params or RelationshipParameters()
        self.owner_id = owner_id
        self._eviction_hook: EvictionHook | None = eviction_hook
        self._ties: Dict[str, RelationshipTie] = {}

    def apply_delta(
        self,
        other_id: str,
        *,
        trust: float = 0.0,
        familiarity: float = 0.0,
        rivalry: float = 0.0,
    ) -> RelationshipTie:
        tie = self._ties.get(other_id)
        if tie is None:
            tie = RelationshipTie()
            self._ties[other_id] = tie
        tie.trust = _clamp(tie.trust + trust, low=-1.0, high=1.0)
        tie.familiarity = _clamp(tie.familiarity + familiarity, low=-1.0, high=1.0)
        tie.rivalry = _clamp(tie.rivalry + rivalry, low=0.0, high=1.0)
        self._prune_if_needed(reason="capacity")
        return tie

    def tie_for(self, other_id: str) -> RelationshipTie | None:
        """Return the tie for ``other_id`` if it exists."""

        return self._ties.get(other_id)

    def decay(self) -> None:
        if not self._ties:
            return
        removes: List[str] = []
        for other_id, tie in self._ties.items():
            tie.trust = _decay_value(tie.trust, self.params.trust_decay)
            tie.familiarity = _decay_value(tie.familiarity, self.params.familiarity_decay)
            tie.rivalry = _decay_value(tie.rivalry, self.params.rivalry_decay, minimum=0.0)
            if tie.trust == 0.0 and tie.familiarity == 0.0 and tie.rivalry == 0.0:
                removes.append(other_id)
        for other_id in removes:
            self._emit_eviction(other_id, reason="decay")

    def snapshot(self) -> Dict[str, Dict[str, float]]:
        return {other_id: tie.as_dict() for other_id, tie in self._ties.items()}

    def inject(self, payload: Dict[str, Dict[str, float]]) -> None:
        self._ties.clear()
        for other_id, values in payload.items():
            tie = RelationshipTie(
                trust=_clamp(float(values.get("trust", 0.0)), low=-1.0, high=1.0),
                familiarity=_clamp(float(values.get("familiarity", 0.0)), low=-1.0, high=1.0),
                rivalry=_clamp(float(values.get("rivalry", 0.0)), low=0.0, high=1.0),
            )
            self._ties[str(other_id)] = tie
        self._prune_if_needed(reason="capacity")

    def set_eviction_hook(self, *, owner_id: str, hook: EvictionHook | None) -> None:
        self.owner_id = owner_id
        self._eviction_hook = hook

    def top_friends(self, limit: int) -> List[Tuple[str, RelationshipTie]]:
        if limit <= 0:
            return []
        candidates = sorted(
            self._ties.items(),
            key=lambda item: item[1].trust + item[1].familiarity,
            reverse=True,
        )
        return candidates[:limit]

    def top_rivals(self, limit: int) -> List[Tuple[str, RelationshipTie]]:
        if limit <= 0:
            return []
        candidates = sorted(
            self._ties.items(),
            key=lambda item: item[1].rivalry,
            reverse=True,
        )
        return candidates[:limit]

    def _prune_if_needed(self, *, reason: str) -> None:
        max_edges = self.params.max_edges
        if max_edges <= 0 or len(self._ties) <= max_edges:
            return
        ordered = sorted(
            self._ties.items(),
            key=lambda item: item[1].trust + item[1].familiarity,
            reverse=True,
        )
        to_remove = [other_id for other_id, _ in ordered[max_edges:]]
        for other_id in to_remove:
            self._emit_eviction(other_id, reason=reason)

    def _emit_eviction(self, other_id: str, *, reason: str) -> None:
        if other_id not in self._ties:
            return
        if self._eviction_hook is not None:
            self._eviction_hook(self.owner_id, other_id, reason)
        self._ties.pop(other_id, None)


def _decay_value(value: float, decay: float, *, minimum: float = -1.0) -> float:
    if decay <= 0.0:
        return value
    if value > 0:
        return max(0.0, value - decay)
    if value < 0:
        return min(0.0, value + decay)
    return 0.0


__all__ = [
    "RelationshipLedger",
    "RelationshipParameters",
    "RelationshipTie",
]
