"""Monitors KPIs and promotion guardrails - coordinator pattern.

DESIGN#3.1: Analyzer Extraction (WP5 Phase 3.1)

StabilityMonitor acts as a lightweight coordinator that delegates to
5 specialized analyzers:
- FairnessAnalyzer: Queue conflict detection
- RivalryTracker: High-intensity rivalry spikes
- RewardVarianceAnalyzer: Reward variance tracking
- OptionThrashDetector: Option switching monitoring
- StarvationDetector: Sustained hunger tracking

The monitor handles:
- Analyzer instantiation and configuration
- Delegation of track() to analyzers
- Aggregation of metrics and alerts
- Promotion window logic
- Legacy alert detection (embedding, affordance, lateness, employment)
- State export/import coordination
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from townlet.config import SimulationConfig
from townlet.stability.analyzers import (
    FairnessAnalyzer,
    OptionThrashDetector,
    RewardVarianceAnalyzer,
    RivalryTracker,
    StarvationDetector,
)
from townlet.utils.coerce import coerce_float, coerce_int


class StabilityMonitor:
    """Coordinates stability analyzers and tracks promotion guardrails."""

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.latest_alert: str | None = None
        self.latest_alerts: list[str] = []
        self.last_queue_metrics: dict[str, int] | None = None
        self.last_embedding_metrics: dict[str, float] | None = None
        self.fail_threshold = config.stability.affordance_fail_threshold
        self.lateness_threshold = config.stability.lateness_threshold
        self._employment_enabled = config.employment.enforce_job_loop

        # Instantiate analyzers
        self._fairness = FairnessAnalyzer(alert_limit=5)
        self._rivalry = RivalryTracker(
            alert_limit=5,
            intensity_threshold=config.conflict.rivalry.avoid_threshold,
        )
        self._starvation = StarvationDetector(
            hunger_threshold=config.stability.starvation.hunger_threshold,
            min_duration_ticks=config.stability.starvation.min_duration_ticks,
            window_ticks=config.stability.starvation.window_ticks,
            max_incidents=config.stability.starvation.max_incidents,
        )
        self._reward_variance = RewardVarianceAnalyzer(
            window_ticks=config.stability.reward_variance.window_ticks,
            max_variance=config.stability.reward_variance.max_variance,
            min_samples=config.stability.reward_variance.min_samples,
        )
        self._option_thrash = OptionThrashDetector(
            window_ticks=config.stability.option_thrash.window_ticks,
            max_thrash_rate=config.stability.option_thrash.max_switch_rate,
            min_samples=config.stability.option_thrash.min_samples,
        )

        # Promotion window state
        self._promotion_cfg = config.stability.promotion
        self._promotion_allowed_alerts = set(self._promotion_cfg.allowed_alerts)
        self._promotion_window_ticks = self._promotion_cfg.window_ticks
        self._promotion_window_start = 0
        self._promotion_window_failed = False
        self._promotion_pass_streak = 0
        self._promotion_candidate_ready = False
        self._promotion_last_result: str | None = None
        self._promotion_last_evaluated_tick: int | None = None

        self._latest_metrics: dict[str, object] = {
            "alerts": [],
            "thresholds": self._threshold_snapshot(),
            "promotion": self._promotion_snapshot(),
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
        rivalry_events: Iterable[dict[str, object]] | None = None,
    ) -> None:
        """Track metrics and check alert thresholds.

        Delegates to 5 specialized analyzers and aggregates alerts:
        1. FairnessAnalyzer - queue conflict deltas
        2. RivalryTracker - high-intensity rivalry spikes
        3. StarvationDetector - sustained hunger incidents
        4. OptionThrashDetector - option switching rate
        5. RewardVarianceAnalyzer - reward distribution variance

        Also handles legacy alerts: embedding reuse, affordance failures,
        lateness spikes, employment queue overflow.

        Args:
            tick: Current simulation tick
            rewards: Per-agent rewards
            terminated: Per-agent termination flags
            queue_metrics: Queue conflict metrics (cumulative counters)
            embedding_metrics: Embedding reuse metrics
            job_snapshot: Employment snapshot for lateness
            events: Affordance events (for failure counting)
            employment_metrics: Employment exit queue metrics
            hunger_levels: Per-agent hunger levels (0.0 = starving)
            option_switch_counts: Per-agent option switch counts
            rivalry_events: Rivalry event list with intensity
        """
        previous_queue_metrics = self.last_queue_metrics or {}
        self.last_queue_metrics = queue_metrics
        self.last_embedding_metrics = embedding_metrics
        alerts: list[str] = []

        # Delegate to FairnessAnalyzer
        fairness_metrics = self._fairness.analyze(
            tick=tick, queue_metrics=queue_metrics
        )
        fairness_alert = self._fairness.check_alert()
        if fairness_alert:
            alerts.append(fairness_alert)
        fairness_delta = fairness_metrics.get("queue_deltas", {})

        # Delegate to RivalryTracker
        rivalry_metrics = self._rivalry.analyze(
            tick=tick, rivalry_events=rivalry_events
        )
        rivalry_alert = self._rivalry.check_alert()
        if rivalry_alert:
            alerts.append(rivalry_alert)
        rivalry_events_list = rivalry_metrics.get("rivalry_events", [])

        # Delegate to StarvationDetector
        starvation_metrics = self._starvation.analyze(
            tick=tick, hunger_levels=hunger_levels, terminated=terminated
        )
        starvation_alert = self._starvation.check_alert()
        if starvation_alert:
            alerts.append(starvation_alert)
        starvation_incidents = starvation_metrics.get("starvation_incidents", 0)

        # Delegate to OptionThrashDetector
        option_metrics = self._option_thrash.analyze(
            tick=tick, option_switch_counts=option_switch_counts
        )
        option_alert = self._option_thrash.check_alert()
        if option_alert:
            alerts.append(option_alert)
        option_rate = option_metrics.get("option_thrash_mean")
        option_samples = option_metrics.get("option_samples", 0)

        # Delegate to RewardVarianceAnalyzer
        reward_metrics = self._reward_variance.analyze(tick=tick, rewards=rewards)
        reward_alert = self._reward_variance.check_alert()
        if reward_alert:
            alerts.append(reward_alert)
        reward_variance = reward_metrics.get("reward_variance")
        reward_mean = reward_metrics.get("reward_mean")
        reward_samples = reward_metrics.get("reward_samples", 0)

        # Legacy alert: embedding reuse warning
        if embedding_metrics and embedding_metrics.get("reuse_warning"):
            alerts.append("embedding_reuse_warning")

        # Legacy alert: affordance failures
        fail_count = 0
        if events is not None:
            fail_count = sum(1 for e in events if e.get("event") == "affordance_fail")
        if self.fail_threshold >= 0 and fail_count > self.fail_threshold:
            alerts.append("affordance_failures_exceeded")

        # Legacy alert: lateness spike
        if job_snapshot is not None and self.lateness_threshold >= 0:
            lateness_total = 0
            for agent_info in job_snapshot.values():
                if self._employment_enabled:
                    late_value = agent_info.get("late_ticks_today", 0)
                else:
                    late_value = agent_info.get("lateness_counter", 0)
                lateness_total += coerce_int(late_value)
            if lateness_total > self.lateness_threshold:
                alerts.append("lateness_spike")

        # Legacy alert: employment exit queue
        if employment_metrics is not None:
            pending = coerce_int(employment_metrics.get("pending_count"))
            limit = coerce_int(employment_metrics.get("queue_limit"))
            if limit and pending > limit:
                alerts.append("employment_exit_queue_overflow")
            elif pending and not alerts:
                alerts.append("employment_exit_backlog")

        # Update promotion window
        self._update_promotion_window(tick, alerts)

        # Store aggregated results
        self.latest_alerts = alerts
        self.latest_alert = alerts[0] if alerts else None

        self._latest_metrics = {
            "starvation_incidents": starvation_incidents,
            "starvation_window_ticks": self.config.stability.starvation.window_ticks,
            "option_switch_rate": option_rate,
            "option_samples": option_samples,
            "reward_variance": reward_variance,
            "reward_mean": reward_mean,
            "reward_samples": reward_samples,
            "queue_totals": dict(queue_metrics or {}),
            "queue_deltas": fairness_delta,
            "rivalry_events": rivalry_events_list,
            "alerts": list(alerts),
            "thresholds": self._threshold_snapshot(),
            "promotion": self._promotion_snapshot(),
        }

    def latest_metrics(self) -> dict[str, object]:
        """Return copy of latest metrics dict."""
        return dict(self._latest_metrics)

    def export_state(self) -> dict[str, object]:
        """Export coordinator and analyzer state for snapshots."""
        return {
            "starvation": self._starvation.export_state(),
            "reward_variance": self._reward_variance.export_state(),
            "option_thrash": self._option_thrash.export_state(),
            "fairness": self._fairness.export_state(),
            "rivalry": self._rivalry.export_state(),
            "latest_metrics": dict(self._latest_metrics),
            "promotion": {
                "window_start": self._promotion_window_start,
                "window_failed": self._promotion_window_failed,
                "pass_streak": self._promotion_pass_streak,
                "candidate_ready": self._promotion_candidate_ready,
                "last_result": self._promotion_last_result,
                "last_evaluated_tick": self._promotion_last_evaluated_tick,
            },
        }

    def import_state(self, payload: Mapping[str, object]) -> None:
        """Import coordinator and analyzer state from snapshots."""
        # Import analyzer states
        starvation_state = payload.get("starvation")
        if isinstance(starvation_state, dict):
            self._starvation.import_state(starvation_state)

        reward_state = payload.get("reward_variance")
        if isinstance(reward_state, dict):
            self._reward_variance.import_state(reward_state)

        option_state = payload.get("option_thrash")
        if isinstance(option_state, dict):
            self._option_thrash.import_state(option_state)

        fairness_state = payload.get("fairness")
        if isinstance(fairness_state, dict):
            self._fairness.import_state(fairness_state)

        rivalry_state = payload.get("rivalry")
        if isinstance(rivalry_state, dict):
            self._rivalry.import_state(rivalry_state)

        # Import promotion state
        promotion = payload.get("promotion", {})
        if isinstance(promotion, dict):
            self._promotion_window_start = coerce_int(
                promotion.get("window_start"), default=0
            )
            self._promotion_window_failed = bool(promotion.get("window_failed", False))
            self._promotion_pass_streak = coerce_int(
                promotion.get("pass_streak"), default=0
            )
            self._promotion_candidate_ready = bool(
                promotion.get("candidate_ready", False)
            )
            last_result = promotion.get("last_result")
            self._promotion_last_result = (
                str(last_result) if last_result is not None else None
            )
            last_tick = promotion.get("last_evaluated_tick")
            self._promotion_last_evaluated_tick = (
                coerce_int(last_tick) if last_tick is not None else None
            )
        else:
            self._promotion_window_start = 0
            self._promotion_window_failed = False
            self._promotion_pass_streak = 0
            self._promotion_candidate_ready = False
            self._promotion_last_result = None
            self._promotion_last_evaluated_tick = None

        # Import latest metrics
        metrics = payload.get("latest_metrics", {})
        self._latest_metrics = dict(metrics) if isinstance(metrics, dict) else {}
        if "thresholds" not in self._latest_metrics:
            self._latest_metrics["thresholds"] = self._threshold_snapshot()
        self._latest_metrics["promotion"] = self._promotion_snapshot()
        alerts_obj = self._latest_metrics.get("alerts", [])
        self.latest_alerts = (
            list(alerts_obj) if isinstance(alerts_obj, Iterable) else []
        )
        self.latest_alert = self.latest_alerts[0] if self.latest_alerts else None

    def reset_state(self) -> None:
        """Reset all analyzer and coordinator state."""
        self._starvation.reset()
        self._reward_variance.reset()
        self._option_thrash.reset()
        self._fairness.reset()
        self._rivalry.reset()

        self._promotion_window_start = 0
        self._promotion_window_failed = False
        self._promotion_pass_streak = 0
        self._promotion_candidate_ready = False
        self._promotion_last_result = None
        self._promotion_last_evaluated_tick = None

        self._latest_metrics = {
            "alerts": [],
            "thresholds": self._threshold_snapshot(),
            "promotion": self._promotion_snapshot(),
        }
        self.latest_alert = None
        self.latest_alerts = []

    def _promotion_snapshot(self) -> dict[str, object]:
        """Return promotion window state snapshot."""
        window_end = self._promotion_window_start + self._promotion_window_ticks
        return {
            "window_start": self._promotion_window_start,
            "window_end": window_end,
            "window_ticks": self._promotion_window_ticks,
            "pass_streak": self._promotion_pass_streak,
            "required_passes": self._promotion_cfg.required_passes,
            "candidate_ready": self._promotion_candidate_ready,
            "last_result": self._promotion_last_result,
            "last_evaluated_tick": self._promotion_last_evaluated_tick,
        }

    def _threshold_snapshot(self) -> dict[str, object]:
        """Return threshold configuration snapshot."""
        return {
            "affordance_fail_threshold": self.fail_threshold,
            "lateness_threshold": self.lateness_threshold,
            "starvation": self.config.stability.starvation.model_dump(),
            "reward_variance": self.config.stability.reward_variance.model_dump(),
            "option_thrash": self.config.stability.option_thrash.model_dump(),
        }

    def _finalise_promotion_window(self, window_end: int) -> None:
        """Finalize completed promotion window and advance to next."""
        passed = not self._promotion_window_failed
        if passed:
            self._promotion_pass_streak += 1
            self._promotion_last_result = "pass"
        else:
            self._promotion_pass_streak = 0
            self._promotion_last_result = "fail"
        self._promotion_candidate_ready = (
            self._promotion_pass_streak >= self._promotion_cfg.required_passes
        )
        self._promotion_last_evaluated_tick = max(window_end - 1, 0)
        self._promotion_window_start = window_end
        self._promotion_window_failed = False

    def _update_promotion_window(self, tick: int, alerts: Iterable[str]) -> None:
        """Update promotion window state based on current tick and alerts."""
        window_end = self._promotion_window_start + self._promotion_window_ticks
        while tick >= window_end:
            self._finalise_promotion_window(window_end)
            window_end = self._promotion_window_start + self._promotion_window_ticks
        disallowed = [a for a in alerts if a not in self._promotion_allowed_alerts]
        if disallowed:
            self._promotion_window_failed = True
