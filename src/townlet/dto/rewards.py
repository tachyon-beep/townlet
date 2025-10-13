"""Reward computation DTOs."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RewardComponent(BaseModel):
    """Individual component of agent reward."""

    name: str
    value: float
    weight: float = 1.0
    enabled: bool = True


class RewardBreakdown(BaseModel):
    """Complete reward breakdown for an agent."""

    agent_id: str
    tick: int
    total: float
    components: list[RewardComponent] = Field(default_factory=list)

    # Component values (for quick access)
    homeostasis: float = 0.0
    shaping: float = 0.0
    work: float = 0.0
    social: float = 0.0

    # Metadata
    needs: dict[str, float] = Field(default_factory=dict)
    guardrail_active: bool = False
    clipped: bool = False


__all__ = ["RewardBreakdown", "RewardComponent"]
