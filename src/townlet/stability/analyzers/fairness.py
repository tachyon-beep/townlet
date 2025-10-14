"""Fairness analyzer - detects queue conflict pressure.

Tracks delta changes in queue metrics (cooldown, ghost_step, rotation events)
and triggers alerts when thresholds are exceeded.

DESIGN#3.1: Analyzer Extraction (WP5 Phase 3.1)
Extracted from: monitor.py lines 111-126
"""

from __future__ import annotations

from typing import Any

from townlet.utils.coerce import coerce_int


class FairnessAnalyzer:
    """Analyzes queue fairness and detects conflict pressure.

    Monitors queue conflict metrics (ghost steps, rotations, cooldowns) and
    triggers an alert when delta events exceed the fairness threshold.

    Alert triggered: "queue_fairness_pressure"
    Threshold: 5 ghost_step_events OR 5 rotation_events per tick

    State:
        - last_queue_metrics: Previous tick's queue metrics for delta calculation

    Example:
        ```python
        analyzer = FairnessAnalyzer(alert_limit=5)

        # Tick 1
        metrics = analyzer.analyze(tick=1, queue_metrics={"ghost_step_events": 0})
        alert = analyzer.check_alert()  # None

        # Tick 2 (spike in conflicts)
        metrics = analyzer.analyze(tick=2, queue_metrics={"ghost_step_events": 7})
        alert = analyzer.check_alert()  # "queue_fairness_pressure"
        ```
    """

    def __init__(self, *, alert_limit: int = 5) -> None:
        """Initialize fairness analyzer.

        Args:
            alert_limit: Number of ghost_step or rotation events to trigger alert
        """
        self._alert_limit = alert_limit
        self._last_queue_metrics: dict[str, int] | None = None
        self._last_delta: dict[str, int] = {
            "cooldown_events": 0,
            "ghost_step_events": 0,
            "rotation_events": 0,
        }

    def analyze(
        self,
        *,
        tick: int,
        queue_metrics: dict[str, int] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Compute queue fairness delta metrics.

        Args:
            tick: Current simulation tick (unused, for protocol compatibility)
            queue_metrics: Current queue metrics dict
            **kwargs: Ignored (for protocol compatibility)

        Returns:
            Dict with "queue_deltas" key containing event deltas
        """
        previous_queue_metrics = self._last_queue_metrics or {}
        self._last_queue_metrics = queue_metrics

        # Calculate delta for each metric
        fairness_delta: dict[str, int] = {
            "cooldown_events": 0,
            "ghost_step_events": 0,
            "rotation_events": 0,
        }

        if queue_metrics:
            for key in fairness_delta:
                new_value = coerce_int(queue_metrics.get(key))
                old_value = coerce_int(previous_queue_metrics.get(key))
                fairness_delta[key] = max(0, new_value - old_value)

        self._last_delta = fairness_delta

        return {"queue_deltas": fairness_delta}

    def check_alert(self) -> str | None:
        """Check if fairness pressure threshold exceeded.

        Returns:
            "queue_fairness_pressure" if ghost_step or rotation >= alert_limit
            None otherwise
        """
        if (
            self._last_delta["ghost_step_events"] >= self._alert_limit
            or self._last_delta["rotation_events"] >= self._alert_limit
        ):
            return "queue_fairness_pressure"
        return None

    def reset(self) -> None:
        """Reset analyzer state for new simulation."""
        self._last_queue_metrics = None
        self._last_delta = {
            "cooldown_events": 0,
            "ghost_step_events": 0,
            "rotation_events": 0,
        }

    def export_state(self) -> dict[str, Any]:
        """Export state for snapshotting.

        Returns:
            Dict with last_queue_metrics and last_delta
        """
        return {
            "last_queue_metrics": dict(self._last_queue_metrics or {}),
            "last_delta": dict(self._last_delta),
        }

    def import_state(self, state: dict[str, Any]) -> None:
        """Import state from snapshot.

        Args:
            state: State dict from export_state()
        """
        last_queue = state.get("last_queue_metrics")
        if isinstance(last_queue, dict):
            self._last_queue_metrics = dict(last_queue)
        else:
            self._last_queue_metrics = None

        last_delta = state.get("last_delta")
        if isinstance(last_delta, dict):
            self._last_delta = {
                "cooldown_events": coerce_int(last_delta.get("cooldown_events")),
                "ghost_step_events": coerce_int(last_delta.get("ghost_step_events")),
                "rotation_events": coerce_int(last_delta.get("rotation_events")),
            }
        else:
            self._last_delta = {
                "cooldown_events": 0,
                "ghost_step_events": 0,
                "rotation_events": 0,
            }
