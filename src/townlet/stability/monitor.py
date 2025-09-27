"""Monitors KPIs and promotion guardrails."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from typing import Optional

from townlet.config import SimulationConfig


class StabilityMonitor:
    """Tracks rolling metrics and canaries."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.latest_alert: str | None = None
        self.latest_alerts: list[str] = []
        self.last_queue_metrics: Optional[dict[str, int]] = None
        self.last_embedding_metrics: Optional[dict[str, float]] = None
        self.fail_threshold = config.stability.affordance_fail_threshold
        self.lateness_threshold = config.stability.lateness_threshold
        self._employment_enabled = config.employment.enforce_job_loop

        self._starvation_cfg = config.stability.starvation
        self._reward_cfg = config.stability.reward_variance
        self._option_cfg = config.stability.option_thrash

        self._starvation_streaks: dict[str, int] = {}
        self._starvation_active: set[str] = set()
        self._starvation_incidents: deque[tuple[int, str]] = deque()

        self._reward_samples: deque[tuple[int, float]] = deque()
        self._option_samples: deque[tuple[int, float]] = deque()

        self._latest_metrics: dict[str, object] = {
            "alerts": [],
            "thresholds": self._threshold_snapshot(),
        }

    def track(
        self,
        *,
        tick: int,
        rewards: dict[str, float],
        terminated: dict[str, bool],
        queue_metrics: dict[str, int] | None = None,
        embedding_metrics: dict[str, float] | None = None,
        job_snapshot: dict[str, dict[str, object]] | None = None,
        events: Iterable[dict[str, object]] | None = None,
        employment_metrics: dict[str, object] | None = None,
        hunger_levels: dict[str, float] | None = None,
        option_switch_counts: dict[str, int] | None = None,
    ) -> None:
        self.last_queue_metrics = queue_metrics
        self.last_embedding_metrics = embedding_metrics
        alerts: list[str] = []

        if embedding_metrics and embedding_metrics.get("reuse_warning"):
            alerts.append("embedding_reuse_warning")

        fail_count = 0
        if events is not None:
            fail_count = sum(1 for e in events if e.get("event") == "affordance_fail")
        if self.fail_threshold >= 0 and fail_count > self.fail_threshold:
            alerts.append("affordance_failures_exceeded")

        if job_snapshot is not None and self.lateness_threshold >= 0:
            lateness_total = 0
            for agent_info in job_snapshot.values():
                if self._employment_enabled:
                    late_value = agent_info.get("late_ticks_today", 0)
                else:
                    late_value = agent_info.get("lateness_counter", 0)
                lateness_total += int(late_value)
            if lateness_total > self.lateness_threshold:
                alerts.append("lateness_spike")

        if employment_metrics is not None:
            pending = int(employment_metrics.get("pending_count", 0))
            limit = int(employment_metrics.get("queue_limit", 0))
            if limit and pending > limit:
                alerts.append("employment_exit_queue_overflow")
            elif pending and not alerts:
                alerts.append("employment_exit_backlog")

        starvation_incidents = self._update_starvation_state(
            tick=tick,
            hunger_levels=hunger_levels,
            terminated=terminated,
        )
        if (
            starvation_incidents > self._starvation_cfg.max_incidents
            and self._starvation_cfg.max_incidents >= 0
        ):
            alerts.append("starvation_spike")

        option_rate = self._update_option_samples(
            tick=tick,
            option_switch_counts=option_switch_counts,
            active_agent_count=len(hunger_levels or {}),
        )
        if (
            option_rate is not None
            and option_rate > self._option_cfg.max_switch_rate
            and len(self._option_samples) >= self._option_cfg.min_samples
        ):
            alerts.append("option_thrash_detected")

        reward_variance, reward_mean, reward_sample_count = self._update_reward_samples(
            tick=tick,
            rewards=rewards,
        )
        if (
            reward_variance is not None
            and reward_variance > self._reward_cfg.max_variance
            and len(self._reward_samples) >= self._reward_cfg.min_samples
        ):
            alerts.append("reward_variance_spike")

        self.latest_alerts = alerts
        self.latest_alert = alerts[0] if alerts else None

        self._latest_metrics = {
            "starvation_incidents": starvation_incidents,
            "starvation_window_ticks": self._starvation_cfg.window_ticks,
            "option_switch_rate": option_rate,
            "option_samples": len(self._option_samples),
            "reward_variance": reward_variance,
            "reward_mean": reward_mean,
            "reward_samples": reward_sample_count,
            "alerts": list(alerts),
            "thresholds": self._threshold_snapshot(),
        }

    def latest_metrics(self) -> dict[str, object]:
        return dict(self._latest_metrics)

    def export_state(self) -> dict[str, object]:
        return {
            "starvation_streaks": dict(self._starvation_streaks),
            "starvation_active": list(self._starvation_active),
            "starvation_incidents": [
                list(entry) for entry in self._starvation_incidents
            ],
            "reward_samples": [list(entry) for entry in self._reward_samples],
            "option_samples": [list(entry) for entry in self._option_samples],
            "latest_metrics": dict(self._latest_metrics),
        }

    def import_state(self, payload: dict[str, object]) -> None:
        streaks = payload.get("starvation_streaks", {})
        if isinstance(streaks, dict):
            self._starvation_streaks = {
                str(agent): int(value) for agent, value in streaks.items()
            }
        else:
            self._starvation_streaks = {}

        active = payload.get("starvation_active", [])
        if isinstance(active, list):
            self._starvation_active = {str(agent) for agent in active}
        else:
            self._starvation_active = set()

        incidents = payload.get("starvation_incidents", [])
        self._starvation_incidents = deque()
        if isinstance(incidents, list):
            for entry in incidents:
                if isinstance(entry, (list, tuple)) and len(entry) == 2:
                    tick, agent = entry
                    self._starvation_incidents.append((int(tick), str(agent)))

        reward_samples = payload.get("reward_samples", [])
        self._reward_samples = deque()
        if isinstance(reward_samples, list):
            for entry in reward_samples:
                if isinstance(entry, (list, tuple)) and len(entry) == 2:
                    tick, value = entry
                    self._reward_samples.append((int(tick), float(value)))

        option_samples = payload.get("option_samples", [])
        self._option_samples = deque()
        if isinstance(option_samples, list):
            for entry in option_samples:
                if isinstance(entry, (list, tuple)) and len(entry) == 2:
                    tick, value = entry
                    self._option_samples.append((int(tick), float(value)))

        metrics = payload.get("latest_metrics", {})
        self._latest_metrics = dict(metrics) if isinstance(metrics, dict) else {}
        if "thresholds" not in self._latest_metrics:
            self._latest_metrics["thresholds"] = self._threshold_snapshot()
        self.latest_alerts = list(self._latest_metrics.get("alerts", []))
        self.latest_alert = self.latest_alerts[0] if self.latest_alerts else None

    def reset_state(self) -> None:
        self._starvation_streaks.clear()
        self._starvation_active.clear()
        self._starvation_incidents.clear()
        self._reward_samples.clear()
        self._option_samples.clear()
        self._latest_metrics = {
            "alerts": [],
            "thresholds": self._threshold_snapshot(),
        }
        self.latest_alert = None
        self.latest_alerts = []

    def _update_starvation_state(
        self,
        *,
        tick: int,
        hunger_levels: dict[str, float] | None,
        terminated: dict[str, bool],
    ) -> int:
        cutoff = tick - self._starvation_cfg.window_ticks
        while self._starvation_incidents and self._starvation_incidents[0][0] <= cutoff:
            self._starvation_incidents.popleft()

        if hunger_levels is None:
            return len(self._starvation_incidents)

        for agent_id, hunger in hunger_levels.items():
            if hunger <= self._starvation_cfg.hunger_threshold:
                streak = self._starvation_streaks.get(agent_id, 0) + 1
                self._starvation_streaks[agent_id] = streak
                if (
                    streak >= self._starvation_cfg.min_duration_ticks
                    and agent_id not in self._starvation_active
                ):
                    self._starvation_incidents.append((tick, agent_id))
                    self._starvation_active.add(agent_id)
            else:
                self._starvation_streaks.pop(agent_id, None)
                self._starvation_active.discard(agent_id)

        for agent_id, was_terminated in terminated.items():
            if was_terminated:
                self._starvation_streaks.pop(agent_id, None)
                self._starvation_active.discard(agent_id)

        return len(self._starvation_incidents)

    def _update_reward_samples(
        self,
        *,
        tick: int,
        rewards: dict[str, float],
    ) -> tuple[float | None, float | None, int]:
        cutoff = tick - self._reward_cfg.window_ticks
        while self._reward_samples and self._reward_samples[0][0] <= cutoff:
            self._reward_samples.popleft()

        for value in rewards.values():
            self._reward_samples.append((tick, float(value)))

        if not self._reward_samples:
            return None, None, 0

        values = [sample[1] for sample in self._reward_samples]
        sample_count = len(values)
        if sample_count == 0:
            return None, None, 0
        mean = sum(values) / sample_count
        variance = sum((value - mean) ** 2 for value in values) / sample_count
        return variance, mean, sample_count

    def _threshold_snapshot(self) -> dict[str, object]:
        return {
            "affordance_fail_threshold": self.fail_threshold,
            "lateness_threshold": self.lateness_threshold,
            "starvation": self._starvation_cfg.model_dump(),
            "reward_variance": self._reward_cfg.model_dump(),
            "option_thrash": self._option_cfg.model_dump(),
        }

    def _update_option_samples(
        self,
        *,
        tick: int,
        option_switch_counts: dict[str, int] | None,
        active_agent_count: int,
    ) -> float | None:
        cutoff = tick - self._option_cfg.window_ticks
        while self._option_samples and self._option_samples[0][0] <= cutoff:
            self._option_samples.popleft()

        if option_switch_counts is not None:
            total_switches = float(sum(option_switch_counts.values()))
            agents_considered = active_agent_count or len(option_switch_counts)
            if agents_considered <= 0:
                agents_considered = 1
            rate = total_switches / float(agents_considered)
            self._option_samples.append((tick, rate))

        if not self._option_samples:
            return None

        rates = [sample[1] for sample in self._option_samples]
        return sum(rates) / len(rates)
