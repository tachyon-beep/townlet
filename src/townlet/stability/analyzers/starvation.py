"""Starvation detector - detects sustained hunger incidents.

Tracks per-agent hunger streaks and triggers alerts when incidents
exceed the threshold within a rolling window.

DESIGN#3.1: Analyzer Extraction (WP5 Phase 3.1)
Extracted from: monitor.py lines 155-164, 352-386
"""

from __future__ import annotations

from collections import deque
from typing import Any

from townlet.utils.coerce import coerce_float


class StarvationDetector:
    """Analyzes hunger levels and detects sustained starvation incidents.

    Monitors per-agent hunger levels and tracks sustained starvation streaks.
    Triggers an alert when the number of incidents exceeds the threshold
    within a rolling window.

    Alert triggered: "starvation_spike"
    Threshold: incidents > max_incidents with window tracking
    Window: Configurable (default 10000 ticks)

    State:
        - starvation_streaks: Per-agent sustained hunger streak counters
        - starvation_active: Set of agents currently in starvation
        - starvation_incidents: Rolling deque of (tick, agent_id) incidents

    Example:
        ```python
        detector = StarvationDetector(
            hunger_threshold=0.2,
            min_duration_ticks=100,
            window_ticks=10000,
            max_incidents=5
        )

        # Agent with high hunger - no incident yet (streak building)
        metrics = detector.analyze(
            tick=1,
            hunger_levels={"alice": 0.15},
            terminated={}
        )
        alert = detector.check_alert()  # None (streak < min_duration)

        # Sustained hunger - triggers incident
        for tick in range(2, 102):
            metrics = detector.analyze(
                tick=tick,
                hunger_levels={"alice": 0.15},
                terminated={}
            )
        alert = detector.check_alert()  # None (only 1 incident)

        # Multiple agents starving - alert
        for tick in range(102, 202):
            metrics = detector.analyze(
                tick=tick,
                hunger_levels={
                    "alice": 0.10,
                    "bob": 0.12,
                    "carol": 0.08,
                    "dave": 0.15,
                    "eve": 0.18,
                    "frank": 0.11,
                },
                terminated={}
            )
        alert = detector.check_alert()  # "starvation_spike" (6 incidents)
        ```
    """

    def __init__(
        self,
        *,
        hunger_threshold: float = 0.2,
        min_duration_ticks: int = 100,
        window_ticks: int = 10000,
        max_incidents: int = 5,
    ) -> None:
        """Initialize starvation detector.

        Args:
            hunger_threshold: Hunger level below which agent is starving
            min_duration_ticks: Minimum consecutive ticks to count as incident
            window_ticks: Size of rolling window for incidents
            max_incidents: Incident count threshold to trigger alert
        """
        self._hunger_threshold = hunger_threshold
        self._min_duration_ticks = min_duration_ticks
        self._window_ticks = window_ticks
        self._max_incidents = max_incidents
        self._starvation_streaks: dict[str, int] = {}
        self._starvation_active: set[str] = set()
        self._starvation_incidents: deque[tuple[int, str]] = deque()

    def analyze(
        self,
        *,
        tick: int,
        hunger_levels: dict[str, float] | None = None,
        terminated: dict[str, bool] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Compute starvation metrics.

        Args:
            tick: Current simulation tick
            hunger_levels: Per-agent hunger levels (0.0 = starving, 1.0 = full)
            terminated: Per-agent termination flags
            **kwargs: Ignored (for protocol compatibility)

        Returns:
            Dict with starvation_incidents count
        """
        # Prune old incidents outside window
        cutoff = tick - self._window_ticks
        while self._starvation_incidents and self._starvation_incidents[0][0] <= cutoff:
            self._starvation_incidents.popleft()

        if hunger_levels is None:
            return {"starvation_incidents": len(self._starvation_incidents)}

        # Track hunger streaks
        for agent_id, hunger in hunger_levels.items():
            hunger_value = coerce_float(hunger, default=1.0)
            if hunger_value <= self._hunger_threshold:
                # Increment streak
                streak = self._starvation_streaks.get(agent_id, 0) + 1
                self._starvation_streaks[agent_id] = streak

                # Record incident if streak threshold reached
                if (
                    streak >= self._min_duration_ticks
                    and agent_id not in self._starvation_active
                ):
                    self._starvation_incidents.append((tick, agent_id))
                    self._starvation_active.add(agent_id)
            else:
                # Reset streak when hunger is above threshold
                self._starvation_streaks.pop(agent_id, None)
                self._starvation_active.discard(agent_id)

        # Clear terminated agents
        if terminated:
            for agent_id, was_terminated in terminated.items():
                if bool(was_terminated):
                    self._starvation_streaks.pop(agent_id, None)
                    self._starvation_active.discard(agent_id)

        return {"starvation_incidents": len(self._starvation_incidents)}

    def check_alert(self) -> str | None:
        """Check if starvation incidents exceed threshold.

        Returns:
            "starvation_spike" if incidents > max_incidents
            None otherwise (or if max_incidents < 0, which disables alerts)
        """
        if (
            len(self._starvation_incidents) > self._max_incidents
            and self._max_incidents >= 0
        ):
            return "starvation_spike"
        return None

    def reset(self) -> None:
        """Reset detector state for new simulation."""
        self._starvation_streaks.clear()
        self._starvation_active.clear()
        self._starvation_incidents.clear()

    def export_state(self) -> dict[str, Any]:
        """Export state for snapshotting.

        Returns:
            Dict with starvation_streaks, starvation_active, starvation_incidents
        """
        return {
            "starvation_streaks": dict(self._starvation_streaks),
            "starvation_active": list(self._starvation_active),
            "starvation_incidents": list(self._starvation_incidents),
        }

    def import_state(self, state: dict[str, Any]) -> None:
        """Import state from snapshot.

        Args:
            state: State dict from export_state()
        """
        streaks = state.get("starvation_streaks")
        if isinstance(streaks, dict):
            self._starvation_streaks = {
                str(agent): int(count)
                for agent, count in streaks.items()
                if isinstance(count, int)
            }
        else:
            self._starvation_streaks = {}

        active = state.get("starvation_active")
        if isinstance(active, list):
            self._starvation_active = {str(agent) for agent in active}
        else:
            self._starvation_active = set()

        incidents = state.get("starvation_incidents")
        if isinstance(incidents, list):
            self._starvation_incidents = deque(
                (int(t), str(agent))
                for t, agent in incidents
                if isinstance(t, int) and isinstance(agent, str)
            )
        else:
            self._starvation_incidents = deque()
