"""Agent snapshot data structures."""

from __future__ import annotations

from dataclasses import dataclass, field

from townlet.agents.models import Personality

from .personality import (
    DEFAULT_PROFILE_NAME,
    default_personality,
    resolve_personality_profile,
)

_BASE_NEEDS: tuple[str, ...] = ("hunger", "hygiene", "energy")


@dataclass
class AgentSnapshot:
    """Minimal agent state shared across world subsystems."""

    agent_id: str
    position: tuple[int, int]
    needs: dict[str, float]
    wallet: float = 0.0
    home_position: tuple[int, int] | None = None
    origin_agent_id: str | None = None
    personality: Personality = field(default_factory=default_personality)
    personality_profile: str = DEFAULT_PROFILE_NAME
    inventory: dict[str, int] = field(default_factory=dict)
    job_id: str | None = None
    on_shift: bool = False
    lateness_counter: int = 0
    last_late_tick: int = -1
    shift_state: str = "pre_shift"
    late_ticks_today: int = 0
    attendance_ratio: float = 0.0
    absent_shifts_7d: int = 0
    wages_withheld: float = 0.0
    exit_pending: bool = False
    last_action_id: str = ""
    last_action_success: bool = False
    last_action_duration: int = 0
    episode_tick: int = 0

    def __post_init__(self) -> None:
        clamped: dict[str, float] = {}
        for key, value in self.needs.items():
            try:
                numeric = float(value)
            except (TypeError, ValueError):
                numeric = 0.0
            clamped[key] = max(0.0, min(1.0, numeric))
        for key in _BASE_NEEDS:
            clamped.setdefault(key, 0.5)
        self.needs = clamped
        if self.home_position is not None:
            x, y = int(self.home_position[0]), int(self.home_position[1])
            self.home_position = (x, y)
        if self.origin_agent_id is None:
            self.origin_agent_id = self.agent_id
        profile_name = (self.personality_profile or "").strip().lower()
        if profile_name:
            resolved_name, resolved = resolve_personality_profile(profile_name)
            self.personality_profile = resolved_name
            current_personality = getattr(self, "personality", None)
            if current_personality is None or current_personality == resolved:
                self.personality = resolved


__all__ = ["AgentSnapshot"]
