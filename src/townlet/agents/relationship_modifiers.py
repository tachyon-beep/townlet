"""Relationship delta adjustment helpers respecting personality flags."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from townlet.agents.models import Personality

RelationshipEvent = Literal[
    "generic",
    "chat_success",
    "chat_failure",
    "queue_polite",
    "conflict",
]


@dataclass(frozen=True)
class RelationshipDelta:
    """Represents trust/familiarity/rivalry deltas for a single event."""

    trust: float = 0.0
    familiarity: float = 0.0
    rivalry: float = 0.0


def apply_personality_modifiers(
    *,
    delta: RelationshipDelta,
    personality: Personality,
    event: RelationshipEvent,
    enabled: bool,
) -> RelationshipDelta:
    """Adjust ``delta`` based on personality traits when enabled.

    When ``enabled`` is ``False`` the input delta is returned unchanged so tests
    can assert parity with the pre-personality behaviour. This hook allows the
    relationship system to opt-in once the feature flag is flipped.
    """

    if not enabled:
        return delta

    trust = delta.trust
    familiarity = delta.familiarity
    rivalry = delta.rivalry

    trust = _apply_forgiveness(trust, personality.forgiveness)
    familiarity = _apply_forgiveness(familiarity, personality.forgiveness)
    rivalry = _apply_forgiveness(rivalry, personality.forgiveness)

    if event == "chat_success":
        familiarity = _apply_extroversion(familiarity, personality.extroversion)
    if event == "conflict":
        rivalry = _apply_ambition(rivalry, personality.ambition)

    return RelationshipDelta(
        trust=_clamp(trust, -1.0, 1.0),
        familiarity=_clamp(familiarity, -1.0, 1.0),
        rivalry=_clamp(rivalry, -1.0, 1.0),
    )


def _apply_forgiveness(value: float, forgiveness: float) -> float:
    if value >= 0.0:
        return value
    forgiveness = _clamp(forgiveness, -1.0, 1.0)
    if forgiveness >= 0.0:
        multiplier = 1.0 - 0.5 * forgiveness
    else:
        multiplier = 1.0 + 0.5 * abs(forgiveness)
    return value * multiplier


def _apply_extroversion(value: float, extroversion: float) -> float:
    extroversion = _clamp(extroversion, -1.0, 1.0)
    return value + 0.02 * extroversion


def _apply_ambition(value: float, ambition: float) -> float:
    if value <= 0.0:
        return value
    ambition = _clamp(ambition, -1.0, 1.0)
    multiplier = 1.0 + 0.3 * ambition
    if multiplier < 0.0:
        multiplier = 0.0
    return value * multiplier


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


__all__ = [
    "RelationshipEvent",
    "RelationshipDelta",
    "apply_personality_modifiers",
]
