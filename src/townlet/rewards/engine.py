"""Reward calculation guardrails and aggregation."""
from __future__ import annotations

from typing import Dict, Iterable

from townlet.config import SimulationConfig
from townlet.world.grid import WorldState


class RewardEngine:
    """Compute per-agent rewards with clipping and guardrails."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self._termination_block: Dict[str, int] = {}

    def compute(self, world: WorldState, terminated: Dict[str, bool]) -> Dict[str, float]:
        rewards: Dict[str, float] = {}
        clip_cfg = self.config.rewards.clip
        clip_value = clip_cfg.clip_per_tick
        block_window = int(clip_cfg.no_positive_within_death_ticks)
        weights = self.config.rewards.needs_weights
        survival_tick = self.config.rewards.survival_tick
        current_tick = int(getattr(world, "tick", 0))

        self._prune_termination_blocks(current_tick, block_window)

        social_rewards: Dict[str, float] = {}
        chat_events = self._consume_chat_events(world)
        if self._social_rewards_enabled():
            social_rewards = self._compute_chat_rewards(world, chat_events)

        for agent_id, snapshot in world.agents.items():
            total = survival_tick
            for need, value in snapshot.needs.items():
                weight = getattr(weights, need, 0.0)
                deficit = 1.0 - float(value)
                total -= weight * max(0.0, deficit) ** 2

            total += social_rewards.get(agent_id, 0.0)

            if terminated.get(agent_id):
                self._termination_block[agent_id] = current_tick

            if terminated.get(agent_id) or self._is_blocked(agent_id, current_tick, block_window):
                if total > 0.0:
                    total = 0.0

            total = max(min(total, clip_value), -clip_value)
            rewards[agent_id] = total
        return rewards

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _consume_chat_events(self, world: WorldState) -> Iterable[dict[str, object]]:
        consumer = getattr(world, "consume_chat_events", None)
        if callable(consumer):
            return consumer()
        return []

    def _social_rewards_enabled(self) -> bool:
        stage = getattr(self.config.features.stages, "social_rewards", "OFF")
        return stage in {"C1", "C2", "C3"}

    def _compute_chat_rewards(
        self,
        world: WorldState,
        events: Iterable[dict[str, object]],
    ) -> Dict[str, float]:
        rewards: Dict[str, float] = {}
        social_cfg = self.config.rewards.social
        base = float(social_cfg.C1_chat_base)
        coeff_trust = float(social_cfg.C1_coeff_trust)
        coeff_fam = float(social_cfg.C1_coeff_fam)

        for event in events:
            if event.get("event") != "chat_success":
                continue
            speaker = str(event.get("speaker")) if event.get("speaker") else None
            listener = str(event.get("listener")) if event.get("listener") else None
            if not speaker or not listener:
                continue
            quality = event.get("quality", 1.0)
            try:
                quality_factor = max(0.0, min(1.0, float(quality)))
            except (TypeError, ValueError):
                quality_factor = 1.0

            for subject, target in ((speaker, listener), (listener, speaker)):
                snapshot = world.agents.get(subject)
                if snapshot is None:
                    continue
                if self._needs_override(snapshot):
                    continue
                tie = world.relationship_tie(subject, target)
                trust = tie.trust if tie is not None else 0.0
                familiarity = tie.familiarity if tie is not None else 0.0
                reward = base + coeff_trust * trust + coeff_fam * familiarity
                if quality_factor != 1.0:
                    reward *= quality_factor
                rewards[subject] = rewards.get(subject, 0.0) + reward

        return rewards

    def _needs_override(self, snapshot) -> bool:
        for value in snapshot.needs.values():
            try:
                deficit = 1.0 - float(value)
            except (TypeError, ValueError):
                continue
            if deficit > 0.85:
                return True
        return False

    def _is_blocked(self, agent_id: str, tick: int, window: int) -> bool:
        if window < 0:
            return False
        start = self._termination_block.get(agent_id)
        if start is None:
            return False
        return (tick - start) <= window

    def _prune_termination_blocks(self, tick: int, window: int) -> None:
        if window < 0:
            self._termination_block.clear()
            return
        expired = [
            agent_id
            for agent_id, start in self._termination_block.items()
            if tick - start > window
        ]
        for agent_id in expired:
            self._termination_block.pop(agent_id, None)
