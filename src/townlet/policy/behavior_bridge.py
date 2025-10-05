"""Behaviour and anneal blending bridge for policy runtime."""

from __future__ import annotations

import random
from collections.abc import Callable
from dataclasses import dataclass, field

from townlet.policy.behavior import AgentIntent, BehaviorController
from townlet.world.grid import WorldState


@dataclass
class BehaviorBridge:
    """Encapsulates behaviour selection, anneal blending, and option commits."""

    behavior: BehaviorController
    option_commit_ticks: int
    anneal_seed: int = 8675309
    _anneal_rng: random.Random = field(init=False, repr=False)
    _anneal_ratio: float | None = field(init=False, default=None)
    _anneal_blend_enabled: bool = field(init=False, default=False)
    _policy_action_provider: (
        Callable[[WorldState, str, AgentIntent], AgentIntent | None] | None
    ) = field(init=False, default=None, repr=False)
    _ctx_reset_callback: Callable[[str], None] | None = field(init=False, default=None)
    _option_commit_until: dict[str, int] = field(init=False, default_factory=dict)
    _option_committed_intent: dict[str, AgentIntent] = field(
        init=False, default_factory=dict
    )
    _possessed_agents: set[str] = field(init=False, default_factory=set)
    _last_option: dict[str, str] = field(init=False, default_factory=dict)
    _option_switch_counts: dict[str, int] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        self._anneal_rng = random.Random(self.anneal_seed)
        self.option_commit_ticks = max(0, int(self.option_commit_ticks))

    # ------------------------------------------------------------------
    # Configuration and callbacks
    # ------------------------------------------------------------------
    def seed_anneal_rng(self, seed: int) -> None:
        self._anneal_rng.seed(seed)

    def set_anneal_ratio(self, ratio: float | None) -> None:
        if ratio is None:
            self._anneal_ratio = None
        else:
            self._anneal_ratio = max(0.0, min(1.0, float(ratio)))

    def current_anneal_ratio(self) -> float | None:
        return self._anneal_ratio

    def enable_anneal_blend(self, enabled: bool) -> None:
        self._anneal_blend_enabled = bool(enabled)

    def register_ctx_reset_callback(self, callback: Callable[[str], None] | None) -> None:
        self._ctx_reset_callback = callback

    def set_policy_action_provider(
        self, provider: Callable[[WorldState, str, AgentIntent], AgentIntent | None]
    ) -> None:
        self._policy_action_provider = provider

    # ------------------------------------------------------------------
    # Possession helpers
    # ------------------------------------------------------------------
    def acquire_possession(self, agent_id: str) -> bool:
        if agent_id in self._possessed_agents:
            return False
        self._possessed_agents.add(agent_id)
        self.clear_commit_state(agent_id)
        if self._ctx_reset_callback is not None:
            self._ctx_reset_callback(agent_id)
        return True

    def release_possession(self, agent_id: str) -> bool:
        if agent_id not in self._possessed_agents:
            return False
        self._possessed_agents.discard(agent_id)
        return True

    def is_possessed(self, agent_id: str) -> bool:
        return agent_id in self._possessed_agents

    def possessed_agents(self) -> list[str]:
        return sorted(self._possessed_agents)

    # ------------------------------------------------------------------
    # Decision pipeline
    # ------------------------------------------------------------------
    def decide_agent(
        self,
        world: WorldState,
        agent_id: str,
        tick: int,
        guardrail_fn: Callable[[WorldState, str, AgentIntent], AgentIntent],
    ) -> tuple[AgentIntent, bool]:
        scripted = self.behavior.decide(world, agent_id)
        blended = self._select_intent_with_blend(world, agent_id, scripted)
        guarded = guardrail_fn(world, agent_id, blended)
        intent, enforced = self._enforce_option_commit(agent_id, tick, guarded)
        self._record_option(agent_id, intent)
        return intent, enforced

    def update_transition_entry(
        self,
        agent_id: str,
        tick: int,
        entry: dict[str, object],
        commit_enforced: bool,
    ) -> None:
        commit_until = self._option_commit_until.get(agent_id)
        if commit_until is not None and commit_until > tick:
            entry["option_commit_remaining"] = commit_until - tick
            committed = self._option_committed_intent.get(agent_id)
            if committed is not None:
                entry["option_commit_kind"] = committed.kind
            entry["option_commit_enforced"] = bool(commit_enforced)
        else:
            entry.pop("option_commit_remaining", None)
            entry.pop("option_commit_kind", None)
            entry.pop("option_commit_enforced", None)

    def consume_option_switch_counts(self) -> dict[str, int]:
        snapshot = dict(self._option_switch_counts)
        self._option_switch_counts.clear()
        return snapshot

    def mark_termination(self, agent_id: str) -> None:
        self._last_option.pop(agent_id, None)
        self._option_switch_counts.pop(agent_id, None)
        self.clear_commit_state(agent_id)

    def clear_commit_state(self, agent_id: str) -> None:
        self._option_commit_until.pop(agent_id, None)
        self._option_committed_intent.pop(agent_id, None)

    def reset_state(self) -> None:
        self._option_commit_until.clear()
        self._option_committed_intent.clear()
        self._last_option.clear()
        self._option_switch_counts.clear()
        self._possessed_agents.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _select_intent_with_blend(
        self,
        world: WorldState,
        agent_id: str,
        scripted: AgentIntent,
    ) -> AgentIntent:
        if not self._anneal_blend_enabled or not self._anneal_ratio:
            return scripted
        alt_intent: AgentIntent | None = None
        if self._policy_action_provider is not None:
            try:
                alt_intent = self._policy_action_provider(world, agent_id, scripted)
            except Exception:  # pragma: no cover - defensive provider behaviour
                alt_intent = None
        if alt_intent is None:
            return scripted
        ratio = float(self._anneal_ratio)
        if ratio >= 1.0:
            return alt_intent
        if ratio <= 0.0:
            return scripted
        if self._anneal_rng.random() < ratio:
            return alt_intent
        return scripted

    def _enforce_option_commit(
        self, agent_id: str, tick: int, intent: AgentIntent
    ) -> tuple[AgentIntent, bool]:
        commit_until = self._option_commit_until.get(agent_id)
        committed = self._option_committed_intent.get(agent_id)
        commit_active = commit_until is not None and commit_until > tick
        enforced = False

        if commit_active and committed is not None:
            if not self._intents_match(intent, committed):
                intent = self._clone_intent(committed)
                enforced = True
            return intent, enforced

        self.clear_commit_state(agent_id)

        if self.option_commit_ticks > 0 and intent.kind != "wait":
            self._option_commit_until[agent_id] = tick + self.option_commit_ticks
            self._option_committed_intent[agent_id] = self._clone_intent(intent)
        return intent, enforced

    def _record_option(self, agent_id: str, intent: AgentIntent) -> None:
        new_option = intent.kind
        previous_option = self._last_option.get(agent_id)
        if new_option != "wait":
            if previous_option not in (None, "wait") and previous_option != new_option:
                self._option_switch_counts[agent_id] = (
                    self._option_switch_counts.get(agent_id, 0) + 1
                )
            self._last_option[agent_id] = new_option
        else:
            self._last_option[agent_id] = new_option

    @staticmethod
    def _clone_intent(intent: AgentIntent) -> AgentIntent:
        clone = AgentIntent(
            kind=intent.kind,
            object_id=intent.object_id,
            affordance_id=intent.affordance_id,
            blocked=intent.blocked,
            position=intent.position,
            target_agent=intent.target_agent,
            quality=intent.quality,
        )
        return clone

    @staticmethod
    def _intents_match(lhs: AgentIntent, rhs: AgentIntent) -> bool:
        return (
            lhs.kind == rhs.kind
            and lhs.object_id == rhs.object_id
            and lhs.affordance_id == rhs.affordance_id
            and lhs.position == rhs.position
            and lhs.target_agent == rhs.target_agent
            and lhs.quality == rhs.quality
        )

