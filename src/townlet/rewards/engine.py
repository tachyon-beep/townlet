"""Reward calculation guardrails and aggregation."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import ClassVar

from townlet.agents.models import PersonalityProfile, PersonalityProfiles
from townlet.config import SimulationConfig
from townlet.world.grid import WorldState
from townlet.world.observation import agent_context as observation_agent_context


class RewardEngine:
    """Compute per-agent rewards with clipping and guardrails."""

    _REWARD_BIAS_COMPONENTS: ClassVar[dict[str, tuple[str, ...]]] = {
        "social": ("social_bonus", "social_penalty", "social_avoidance"),
        "employment": ("wage", "punctuality"),
        "survival": ("survival",),
    }

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self._termination_block: dict[str, int] = {}
        self._episode_totals: dict[str, float] = {}
        self._latest_breakdown: dict[str, dict[str, float]] = {}
        self._reward_scaling_enabled = config.reward_personality_scaling_enabled()
        self._profile_cache: dict[str, PersonalityProfile] = {}

    def compute(
        self,
        world: WorldState,
        terminated: dict[str, bool],
        reasons: Mapping[str, str] | None = None,
    ) -> dict[str, float]:
        rewards: dict[str, float] = {}
        clip_cfg = self.config.rewards.clip
        clip_value = clip_cfg.clip_per_tick
        block_window = int(clip_cfg.no_positive_within_death_ticks)
        weights = self.config.rewards.needs_weights
        survival_tick = self.config.rewards.survival_tick
        current_tick = int(getattr(world, "tick", 0))
        reason_map = dict(reasons or {})

        self._prune_termination_blocks(current_tick, block_window)
        self._reset_episode_totals(terminated, world)

        chat_events = list(self._consume_chat_events(world))
        avoidance_events = list(self._consume_avoidance_events(world))
        self._latest_social_events = []
        social_bonus: dict[str, float] = {}
        social_penalty: dict[str, float] = {}
        avoidance_bonus: dict[str, float] = {}
        if self._social_stage_value() >= 1:
            social_bonus, social_penalty = self._compute_chat_rewards(
                world, chat_events
            )
        if self._social_stage_value() >= 2:
            avoidance_bonus = self._compute_avoidance_rewards(world, avoidance_events)

        wage_rate = float(self.config.rewards.wage_rate)
        punctuality_bonus = float(self.config.rewards.punctuality_bonus)

        breakdowns: dict[str, dict[str, float]] = {}

        for agent_id, snapshot in world.agents.items():
            components: dict[str, float] = {}
            total = survival_tick
            components["survival"] = survival_tick

            needs_penalty = 0.0
            for need, value in snapshot.needs.items():
                weight = getattr(weights, need, 0.0)
                deficit = 1.0 - float(value)
                needs_penalty += weight * max(0.0, deficit) ** 2
            total -= needs_penalty
            components["needs_penalty"] = -needs_penalty

            social_value = social_bonus.get(agent_id, 0.0)
            penalty_value = social_penalty.get(agent_id, 0.0)
            avoidance_value = avoidance_bonus.get(agent_id, 0.0)
            total += social_value + penalty_value + avoidance_value
            components["social_bonus"] = social_value
            components["social_penalty"] = penalty_value
            components["social_avoidance"] = avoidance_value
            components["social"] = social_value + penalty_value + avoidance_value

            wage_value = self._compute_wage_bonus(agent_id, world, wage_rate)
            total += wage_value
            components["wage"] = wage_value

            punctuality_value = self._compute_punctuality_bonus(
                agent_id, world, punctuality_bonus
            )
            total += punctuality_value
            components["punctuality"] = punctuality_value

            profile = self._profile_for(snapshot)
            if profile is not None and profile.reward_bias:
                total += self._apply_reward_biases(components, profile.reward_bias)

            penalty_value = self._compute_terminal_penalty(
                agent_id, terminated, reason_map
            )
            total += penalty_value
            components["terminal_penalty"] = penalty_value

            pre_guard_total = total

            if terminated.get(agent_id):
                self._termination_block[agent_id] = current_tick

            if terminated.get(agent_id) or self._is_blocked(
                agent_id, current_tick, block_window
            ):
                if total > 0.0:
                    total = 0.0

            guard_adjust = total - pre_guard_total

            post_tick_clip = max(min(total, clip_value), -clip_value)
            tick_clip_adjust = post_tick_clip - total
            total = post_tick_clip

            cumulative = self._episode_totals.get(agent_id, 0.0) + total
            episode_cap = float(self.config.rewards.clip.clip_per_episode)
            episode_clip_adjust = 0.0
            if episode_cap > 0:
                cumulative = max(min(cumulative, episode_cap), -episode_cap)
                # Adjust total so cumulative stays within bounds.
                new_total = cumulative - self._episode_totals.get(agent_id, 0.0)
                episode_clip_adjust = new_total - total
                total = new_total
            self._episode_totals[agent_id] = cumulative

            rewards[agent_id] = total
            components["clip_adjustment"] = (
                guard_adjust + tick_clip_adjust + episode_clip_adjust
            )
            components["total"] = total
            breakdowns[agent_id] = components

        self._latest_breakdown = breakdowns
        self._latest_social_events = self._prepare_social_event_log(
            chat_events, avoidance_events
        )
        return rewards

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _consume_chat_events(self, world: WorldState) -> Iterable[dict[str, object]]:
        consumer = getattr(world, "consume_chat_events", None)
        if callable(consumer):
            return consumer()
        return []

    def _consume_avoidance_events(
        self, world: WorldState
    ) -> Iterable[dict[str, object]]:
        consumer = getattr(world, "consume_relationship_avoidance_events", None)
        if callable(consumer):
            return consumer()
        return []

    def _social_stage_value(self) -> int:
        stage = getattr(self.config.features.stages, "social_rewards", "OFF")
        order = {"OFF": 0, "C1": 1, "C2": 2, "C3": 3}
        return order.get(stage, 0)

    def _profile_for(self, snapshot) -> PersonalityProfile | None:
        if not self._reward_scaling_enabled:
            return None
        name = getattr(snapshot, "personality_profile", None)
        if not name:
            return None
        key = str(name).strip().lower()
        if not key:
            return None
        profile = self._profile_cache.get(key)
        if profile is None:
            try:
                profile = PersonalityProfiles.get(key)
            except KeyError:
                return None
            self._profile_cache[key] = profile
        return profile

    def _apply_reward_biases(
        self,
        components: dict[str, float],
        biases: Mapping[str, float],
    ) -> float:
        total_delta = 0.0

        def _scale(value: float, factor: float) -> float:
            if factor <= 0.0:
                return value
            if value >= 0.0:
                return value * factor
            return value / factor

        for key, raw_factor in biases.items():
            try:
                factor = float(raw_factor)
            except (TypeError, ValueError):
                continue
            if factor == 1.0:
                continue
            targets = self._REWARD_BIAS_COMPONENTS.get(key, (key,))
            for name in targets:
                if name not in components:
                    continue
                baseline = components[name]
                adjusted = _scale(baseline, factor)
                components[name] = adjusted
                total_delta += adjusted - baseline
            if any(name.startswith("social_") for name in targets) or key == "social":
                components["social"] = (
                    components.get("social_bonus", 0.0)
                    + components.get("social_penalty", 0.0)
                    + components.get("social_avoidance", 0.0)
                )
        return total_delta

    def _compute_chat_rewards(
        self,
        world: WorldState,
        events: Iterable[dict[str, object]],
    ) -> tuple[dict[str, float], dict[str, float]]:
        bonus: dict[str, float] = {}
        penalties: dict[str, float] = {}
        social_cfg = self.config.rewards.social
        base = float(social_cfg.C1_chat_base)
        coeff_trust = float(social_cfg.C1_coeff_trust)
        coeff_fam = float(social_cfg.C1_coeff_fam)

        for event in events:
            if event.get("event") != "chat_success":
                if event.get("event") == "chat_failure":
                    speaker = str(event.get("speaker")) if event.get("speaker") else None
                    listener = str(event.get("listener")) if event.get("listener") else None
                    if not speaker or not listener:
                        continue
                    penalty = -0.5 * base
                    penalties[speaker] = penalties.get(speaker, 0.0) + penalty
                    penalties[listener] = penalties.get(listener, 0.0) + penalty * 0.5
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
                bonus[subject] = bonus.get(subject, 0.0) + reward

        return bonus, penalties

    def _compute_avoidance_rewards(
        self,
        world: WorldState,
        events: Iterable[dict[str, object]],
    ) -> dict[str, float]:
        rewards: dict[str, float] = {}
        reward_value = float(self.config.rewards.social.C2_avoid_conflict)
        if reward_value == 0.0:
            return rewards
        for event in events:
            agent_id = str(event.get("agent")) if event.get("agent") else None
            if not agent_id or agent_id not in world.agents:
                continue
            rewards[agent_id] = rewards.get(agent_id, 0.0) + reward_value
        return rewards

    def _prepare_social_event_log(
        self,
        chat_events: Iterable[dict[str, object]],
        avoidance_events: Iterable[dict[str, object]],
    ) -> list[dict[str, object]]:
        log: list[dict[str, object]] = []
        for event in chat_events:
            etype = str(event.get("event", "chat"))
            if etype not in {"chat_success", "chat_failure"}:
                continue
            log.append(
                {
                    "type": etype,
                    "speaker": event.get("speaker"),
                    "listener": event.get("listener"),
                    "quality": event.get("quality"),
                }
            )
        for event in avoidance_events:
            log.append(
                {
                    "type": "rivalry_avoidance",
                    "agent": event.get("agent"),
                    "object": event.get("object_id"),
                    "reason": event.get("reason"),
                }
            )
        return log

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

    def _compute_wage_bonus(
        self,
        agent_id: str,
        world: WorldState,
        wage_rate: float,
    ) -> float:
        if wage_rate <= 0.0:
            return 0.0
        ctx = observation_agent_context(world, agent_id)
        wages_paid = float(ctx.get("wages_paid", 0.0))
        wages_withheld = float(ctx.get("wages_withheld", 0.0))
        return wages_paid - wages_withheld

    def _compute_punctuality_bonus(
        self,
        agent_id: str,
        world: WorldState,
        bonus_rate: float,
    ) -> float:
        if bonus_rate <= 0.0:
            return 0.0
        ctx = observation_agent_context(world, agent_id)
        punctuality = float(ctx.get("punctuality_bonus", 0.0))
        return bonus_rate * punctuality

    def _compute_terminal_penalty(
        self,
        agent_id: str,
        terminated: Mapping[str, bool],
        reasons: Mapping[str, str],
    ) -> float:
        if not terminated.get(agent_id):
            return 0.0
        reason = reasons.get(agent_id)
        if reason == "faint":
            return float(self.config.rewards.faint_penalty)
        if reason == "eviction":
            return float(self.config.rewards.eviction_penalty)
        return 0.0

    def _reset_episode_totals(
        self, terminated: dict[str, bool], world: WorldState
    ) -> None:
        for agent_id, is_terminated in terminated.items():
            if is_terminated:
                self._episode_totals.pop(agent_id, None)
        # Remove stale entries for agents no longer present.
        missing = set(self._episode_totals) - set(world.agents)
        for agent_id in missing:
            self._episode_totals.pop(agent_id, None)

    def latest_reward_breakdown(self) -> dict[str, dict[str, float]]:
        return {
            agent: dict(components)
            for agent, components in self._latest_breakdown.items()
        }

    def latest_social_events(self) -> list[dict[str, object]]:
        return [dict(event) for event in self._latest_social_events]
