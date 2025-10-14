"""Rivalry tracker - detects high-intensity rivalry spikes.

Monitors rivalry events and triggers alerts when high-intensity
events exceed the threshold.

DESIGN#3.1: Analyzer Extraction (WP5 Phase 3.1)
Extracted from: monitor.py lines 172-184
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from townlet.utils.coerce import coerce_float


class RivalryTracker:
    """Analyzes rivalry events and detects spikes.

    Monitors rivalry events from queue conflicts and triggers an alert
    when high-intensity events exceed the threshold.

    Alert triggered: "rivalry_spike"
    Threshold: 5 high-intensity rivalry events per tick

    State:
        - last_rivalry_events: Last tick's rivalry events (for metrics)

    Example:
        ```python
        tracker = RivalryTracker(alert_limit=5, intensity_threshold=0.8)

        # Low intensity events - no alert
        metrics = tracker.analyze(
            tick=1,
            rivalry_events=[
                {"intensity": 0.5, "agent_a": "alice", "agent_b": "bob"}
            ]
        )
        alert = tracker.check_alert()  # None

        # High intensity spike - alert
        metrics = tracker.analyze(
            tick=2,
            rivalry_events=[
                {"intensity": 1.0, "agent_a": "alice", "agent_b": "bob"},
                {"intensity": 0.9, "agent_a": "alice", "agent_b": "carol"},
                # ... 4 more high-intensity events
            ]
        )
        alert = tracker.check_alert()  # "rivalry_spike"
        ```
    """

    def __init__(self, *, alert_limit: int = 5, intensity_threshold: float = 0.8) -> None:
        """Initialize rivalry tracker.

        Args:
            alert_limit: Number of high-intensity events to trigger alert
            intensity_threshold: Minimum intensity to count as "high-intensity"
        """
        self._alert_limit = alert_limit
        self._intensity_threshold = intensity_threshold
        self._last_rivalry_events: list[dict[str, Any]] = []
        self._last_high_intensity_count = 0

    def analyze(
        self,
        *,
        tick: int,
        rivalry_events: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Compute rivalry metrics.

        Args:
            tick: Current simulation tick (unused, for protocol compatibility)
            rivalry_events: List of rivalry event dicts
            **kwargs: Ignored (for protocol compatibility)

        Returns:
            Dict with "rivalry_events" key containing processed events
        """
        # Convert and filter rivalry events
        rivalry_events_list = [
            {str(key): value for key, value in event.items()}
            for event in (rivalry_events or [])
            if isinstance(event, Mapping)
        ]

        # Count high-intensity events
        high_intensity = [
            event
            for event in rivalry_events_list
            if coerce_float(event.get("intensity"), default=0.0)
            >= self._intensity_threshold
        ]

        self._last_rivalry_events = rivalry_events_list
        self._last_high_intensity_count = len(high_intensity)

        return {"rivalry_events": rivalry_events_list}

    def check_alert(self) -> str | None:
        """Check if rivalry spike threshold exceeded.

        Returns:
            "rivalry_spike" if high-intensity events >= alert_limit
            None otherwise
        """
        if self._last_high_intensity_count >= self._alert_limit:
            return "rivalry_spike"
        return None

    def reset(self) -> None:
        """Reset tracker state for new simulation."""
        self._last_rivalry_events = []
        self._last_high_intensity_count = 0

    def export_state(self) -> dict[str, Any]:
        """Export state for snapshotting.

        Returns:
            Dict with last_rivalry_events and last_high_intensity_count
        """
        return {
            "last_rivalry_events": list(self._last_rivalry_events),
            "last_high_intensity_count": self._last_high_intensity_count,
        }

    def import_state(self, state: dict[str, Any]) -> None:
        """Import state from snapshot.

        Args:
            state: State dict from export_state()
        """
        last_events = state.get("last_rivalry_events")
        if isinstance(last_events, list):
            self._last_rivalry_events = list(last_events)
        else:
            self._last_rivalry_events = []

        last_count = state.get("last_high_intensity_count")
        if isinstance(last_count, int):
            self._last_high_intensity_count = last_count
        else:
            self._last_high_intensity_count = 0
