"""Monitors KPIs and promotion guardrails."""
from __future__ import annotations

from typing import Dict, Optional, Iterable

from townlet.config import SimulationConfig


class StabilityMonitor:
    """Tracks rolling metrics and canaries."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.latest_alert: str | None = None
        self.last_queue_metrics: Optional[Dict[str, int]] = None
        self.last_embedding_metrics: Optional[Dict[str, float]] = None
        self.fail_threshold = config.stability.affordance_fail_threshold
        self.lateness_threshold = config.stability.lateness_threshold
        self._employment_enabled = config.employment.enforce_job_loop

    def track(
        self,
        *,
        tick: int,
        rewards: Dict[str, float],
        terminated: Dict[str, bool],
        queue_metrics: Dict[str, int] | None = None,
        embedding_metrics: Dict[str, float] | None = None,
        job_snapshot: Dict[str, Dict[str, object]] | None = None,
        events: Iterable[Dict[str, object]] | None = None,
        employment_metrics: Dict[str, object] | None = None,
    ) -> None:
        # TODO(@townlet): Implement canary thresholds (lateness, starvation, option thrash).
        self.last_queue_metrics = queue_metrics
        self.last_embedding_metrics = embedding_metrics
        alert: str | None = None
        if embedding_metrics and embedding_metrics.get("reuse_warning"):
            alert = "embedding_reuse_warning"

        fail_count = 0
        if events is not None:
            fail_count = sum(1 for e in events if e.get("event") == "affordance_fail")
        if self.fail_threshold >= 0 and fail_count > self.fail_threshold:
            alert = "affordance_failures_exceeded"

        if job_snapshot is not None and self.lateness_threshold >= 0:
            lateness_total = 0
            for agent_info in job_snapshot.values():
                if self._employment_enabled:
                    late_value = agent_info.get("late_ticks_today", 0)
                else:
                    late_value = agent_info.get("lateness_counter", 0)
                lateness_total += int(late_value)
            if lateness_total > self.lateness_threshold:
                alert = "lateness_spike"

        if employment_metrics is not None:
            pending = int(employment_metrics.get("pending_count", 0))
            limit = int(employment_metrics.get("queue_limit", 0))
            if limit and pending > limit:
                alert = "employment_exit_queue_overflow"
            elif pending and not alert:
                # Bubble mild alert if backlog exists but below limit.
                alert = "employment_exit_backlog"

        self.latest_alert = alert
        _ = tick, rewards, terminated
