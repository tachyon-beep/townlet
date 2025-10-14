"""Base protocol for stability analyzers.

Analyzers decompose the monolithic StabilityMonitor into focused,
testable components. Each analyzer computes specific metrics and
checks for alert conditions.

DESIGN#3.1: Analyzer Extraction (WP5 Phase 3.1)
"""

from __future__ import annotations

from typing import Any, Protocol


class StabilityAnalyzer(Protocol):
    """Protocol for stability metric analyzers.

    Each analyzer is responsible for:
    1. Computing specific stability metrics from world state
    2. Maintaining any required rolling window state
    3. Checking alert thresholds and returning alert names
    4. Supporting snapshot export/import for state persistence

    Analyzers follow a functional pattern:
    - analyze() takes inputs, returns metrics dict
    - check_alert() examines internal state, returns alert name or None
    - State mutations happen only in analyze()

    Example:
        ```python
        class FairnessAnalyzer:
            def analyze(self, *, tick: int, queue_metrics: dict, **kwargs) -> dict:
                delta = self._calculate_delta(queue_metrics)
                return {"queue_deltas": delta}

            def check_alert(self) -> str | None:
                if self._last_delta["ghost_step_events"] >= 5:
                    return "queue_fairness_pressure"
                return None
        ```
    """

    def analyze(
        self,
        *,
        tick: int,
        rewards: dict[str, float] | None = None,
        terminated: dict[str, bool] | None = None,
        queue_metrics: dict[str, int] | None = None,
        hunger_levels: dict[str, float] | None = None,
        option_switch_counts: dict[str, int] | None = None,
        rivalry_events: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Compute metrics from world state.

        Args:
            tick: Current simulation tick
            rewards: Per-agent rewards {agent_id: reward}
            terminated: Per-agent termination status {agent_id: bool}
            queue_metrics: Queue conflict metrics
            hunger_levels: Per-agent hunger levels {agent_id: hunger}
            option_switch_counts: Per-agent option switches {agent_id: count}
            rivalry_events: List of rivalry event dicts
            **kwargs: Additional inputs (ignored by analyzer)

        Returns:
            Dict of metric_name -> value pairs
            Keys should be stable and match baseline expectations
        """
        ...

    def check_alert(self) -> str | None:
        """Check if analyzer's alert condition is triggered.

        Returns:
            Alert name (str) if threshold exceeded, None otherwise

        Note:
            Should be called AFTER analyze() on same tick
            Uses internal state set by analyze()
        """
        ...

    def reset(self) -> None:
        """Reset analyzer state for new simulation.

        Clears all rolling windows, counters, and cached state.
        Called when simulation restarts or snapshot resets.
        """
        ...

    def export_state(self) -> dict[str, Any]:
        """Export analyzer state for snapshotting.

        Returns:
            Dict containing all state needed to restore analyzer

        Note:
            Must be JSON-serializable
            Should include all rolling windows, counters, etc.
        """
        ...

    def import_state(self, state: dict[str, Any]) -> None:
        """Import analyzer state from snapshot.

        Args:
            state: State dict from export_state()

        Note:
            Should handle missing keys gracefully (backward compatibility)
            Should validate state structure
        """
        ...


class NullAnalyzer:
    """Null object pattern analyzer (no-op).

    Useful for testing or disabling specific analyzers.
    """

    def analyze(
        self,
        *,
        tick: int,
        rewards: dict[str, float] | None = None,
        terminated: dict[str, bool] | None = None,
        queue_metrics: dict[str, int] | None = None,
        hunger_levels: dict[str, float] | None = None,
        option_switch_counts: dict[str, int] | None = None,
        rivalry_events: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Return empty metrics dict."""
        return {}

    def check_alert(self) -> None:
        """Never trigger alerts."""
        return None

    def reset(self) -> None:
        """No state to reset."""
        pass

    def export_state(self) -> dict[str, Any]:
        """Return empty state."""
        return {}

    def import_state(self, state: dict[str, Any]) -> None:
        """Ignore state (no state to import)."""
        pass
