from __future__ import annotations

import pytest

from townlet.agents import (
    Personality,
    RelationshipDelta,
    apply_personality_modifiers,
)


def test_modifiers_disabled_returns_baseline() -> None:
    personality = Personality(extroversion=0.8, forgiveness=0.5, ambition=0.7)
    delta = RelationshipDelta(trust=-0.2, familiarity=0.1, rivalry=0.05)
    adjusted = apply_personality_modifiers(
        delta=delta,
        personality=personality,
        event="conflict",
        enabled=False,
    )
    assert adjusted == delta


def test_forgiveness_scales_negative_values() -> None:
    personality = Personality(extroversion=0.0, forgiveness=1.0, ambition=0.0)
    delta = RelationshipDelta(trust=-0.4, familiarity=-0.2, rivalry=-0.1)
    adjusted = apply_personality_modifiers(
        delta=delta,
        personality=personality,
        event="generic",
        enabled=True,
    )
    assert adjusted.trust == pytest.approx(-0.2)
    assert adjusted.familiarity == pytest.approx(-0.1)
    assert adjusted.rivalry == pytest.approx(-0.05)


def test_extroversion_adds_chat_bonus() -> None:
    personality = Personality(extroversion=1.0, forgiveness=0.0, ambition=0.0)
    delta = RelationshipDelta(familiarity=0.05)
    adjusted = apply_personality_modifiers(
        delta=delta,
        personality=personality,
        event="chat_success",
        enabled=True,
    )
    assert adjusted.familiarity == pytest.approx(0.07)


def test_ambition_scales_conflict_rivalry() -> None:
    personality = Personality(extroversion=0.0, forgiveness=0.0, ambition=1.0)
    delta = RelationshipDelta(rivalry=0.2)
    adjusted = apply_personality_modifiers(
        delta=delta,
        personality=personality,
        event="conflict",
        enabled=True,
    )
    assert adjusted.rivalry == pytest.approx(0.26)


def test_unforgiving_agent_intensifies_negative_hits() -> None:
    personality = Personality(extroversion=0.0, forgiveness=-1.0, ambition=0.0)
    delta = RelationshipDelta(trust=-0.2)
    adjusted = apply_personality_modifiers(
        delta=delta,
        personality=personality,
        event="generic",
        enabled=True,
    )
    assert adjusted.trust == pytest.approx(-0.3)
