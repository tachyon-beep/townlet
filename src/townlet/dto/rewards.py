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
    """Complete reward breakdown for an agent.

    Contains both aggregate fields (homeostasis, work, social, shaping)
    and explicit component fields (survival, needs_penalty, wage, etc.)
    for maximum flexibility.
    """

    # Identifiers
    agent_id: str
    tick: int
    total: float

    # Optional detailed components list
    components: list[RewardComponent] = Field(default_factory=list)

    # ===== AGGREGATES (High-level) =====
    homeostasis: float = 0.0  # survival - needs_penalty
    shaping: float = 0.0      # (unused, future expansion)
    work: float = 0.0         # wage + punctuality
    social: float = 0.0       # social_bonus + social_penalty + social_avoidance

    # ===== EXPLICIT COMPONENTS (Detailed) =====
    # Survival & Needs
    survival: float = 0.0
    needs_penalty: float = 0.0

    # Employment
    wage: float = 0.0
    punctuality: float = 0.0

    # Social (detailed)
    social_bonus: float = 0.0
    social_penalty: float = 0.0
    social_avoidance: float = 0.0

    # Penalties & Adjustments
    terminal_penalty: float = 0.0
    clip_adjustment: float = 0.0

    # ===== METADATA =====
    needs: dict[str, float] = Field(default_factory=dict)
    guardrail_active: bool = False
    clipped: bool = False


__all__ = ["RewardBreakdown", "RewardComponent"]
