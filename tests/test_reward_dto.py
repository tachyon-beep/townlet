"""Tests for Reward DTO validation and serialization."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from townlet.dto.rewards import RewardBreakdown, RewardComponent


def test_reward_breakdown_dto_construction() -> None:
    """Validate RewardBreakdown DTO construction and validation."""
    # Valid construction
    breakdown = RewardBreakdown(
        agent_id="alice",
        tick=100,
        total=0.13,
        survival=0.01,
        needs_penalty=-0.05,
        wage=0.1,
        punctuality=0.05,
        social=0.02,
        needs={"hunger": 0.8, "hygiene": 0.9, "energy": 0.85},
    )

    assert breakdown.agent_id == "alice"
    assert breakdown.tick == 100
    assert breakdown.total == 0.13
    assert breakdown.survival == 0.01
    assert breakdown.wage == 0.1
    assert breakdown.needs == {"hunger": 0.8, "hygiene": 0.9, "energy": 0.85}

    # Aggregates computed (not automatically - must be set explicitly)
    # These should be set by engine, not auto-computed
    assert breakdown.homeostasis == 0.0  # Default
    assert breakdown.work == 0.0  # Default


def test_reward_breakdown_dto_validation() -> None:
    """Validate DTO type enforcement."""
    # Invalid tick type
    with pytest.raises(ValidationError) as exc_info:
        RewardBreakdown(
            agent_id="alice",
            tick="not_an_int",  # ❌ Should be int
            total=0.05,
        )

    assert "tick" in str(exc_info.value)

    # Invalid total type
    with pytest.raises(ValidationError):
        RewardBreakdown(
            agent_id="alice",
            tick=100,
            total="not_a_float",  # ❌ Should be float
        )


def test_reward_breakdown_dto_serialization() -> None:
    """Validate DTO serialization round-trip."""
    breakdown = RewardBreakdown(
        agent_id="alice",
        tick=100,
        total=0.13,
        survival=0.01,
        wage=0.1,
        needs={"hunger": 0.8},
    )

    # Serialize
    dumped = breakdown.model_dump()
    assert isinstance(dumped, dict)
    assert dumped["agent_id"] == "alice"
    assert dumped["survival"] == 0.01
    assert dumped["wage"] == 0.1

    # Deserialize
    restored = RewardBreakdown.model_validate(dumped)
    assert restored.agent_id == "alice"
    assert restored.total == 0.13
    assert restored.survival == 0.01


def test_reward_breakdown_dto_components_list() -> None:
    """Validate optional components list."""
    breakdown = RewardBreakdown(
        agent_id="alice",
        tick=100,
        total=0.13,
        components=[
            RewardComponent(name="survival", value=0.01),
            RewardComponent(name="wage", value=0.1),
            RewardComponent(name="punctuality", value=0.05),
        ],
    )

    assert len(breakdown.components) == 3
    assert breakdown.components[0].name == "survival"
    assert breakdown.components[1].value == 0.1


def test_reward_breakdown_dto_defaults() -> None:
    """Validate DTO field defaults."""
    # Minimal construction
    breakdown = RewardBreakdown(agent_id="alice", tick=100, total=0.05)

    # All optional fields default correctly
    assert breakdown.homeostasis == 0.0
    assert breakdown.social == 0.0
    assert breakdown.survival == 0.0
    assert breakdown.wage == 0.0
    assert breakdown.punctuality == 0.0
    assert breakdown.social_bonus == 0.0
    assert breakdown.social_penalty == 0.0
    assert breakdown.social_avoidance == 0.0
    assert breakdown.terminal_penalty == 0.0
    assert breakdown.clip_adjustment == 0.0
    assert breakdown.needs == {}
    assert breakdown.guardrail_active is False
    assert breakdown.clipped is False
    assert len(breakdown.components) == 0
