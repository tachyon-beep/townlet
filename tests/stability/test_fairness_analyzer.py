"""Unit tests for FairnessAnalyzer.

DESIGN#3.1: Analyzer Extraction (WP5 Phase 3.1)
"""

from __future__ import annotations

from townlet.stability.analyzers.fairness import FairnessAnalyzer


def test_fairness_analyzer_no_conflicts() -> None:
    """Analyzer should return zero deltas with no conflicts."""
    analyzer = FairnessAnalyzer(alert_limit=5)

    metrics = analyzer.analyze(tick=1, queue_metrics={"ghost_step_events": 0, "rotation_events": 0})
    alert = analyzer.check_alert()

    assert metrics["queue_deltas"]["ghost_step_events"] == 0
    assert metrics["queue_deltas"]["rotation_events"] == 0
    assert alert is None, "No conflicts should not trigger alert"


def test_fairness_analyzer_below_threshold() -> None:
    """Analyzer should not alert if delta below threshold."""
    analyzer = FairnessAnalyzer(alert_limit=5)

    # Tick 1: baseline
    analyzer.analyze(tick=1, queue_metrics={"ghost_step_events": 0})

    # Tick 2: small increase (below threshold)
    metrics = analyzer.analyze(tick=2, queue_metrics={"ghost_step_events": 3})
    alert = analyzer.check_alert()

    assert metrics["queue_deltas"]["ghost_step_events"] == 3
    assert alert is None, "Delta below threshold should not alert"


def test_fairness_analyzer_ghost_step_threshold() -> None:
    """Analyzer should alert when ghost_step events >= threshold."""
    analyzer = FairnessAnalyzer(alert_limit=5)

    # Tick 1: baseline
    analyzer.analyze(tick=1, queue_metrics={"ghost_step_events": 2})

    # Tick 2: spike (delta = 7)
    metrics = analyzer.analyze(tick=2, queue_metrics={"ghost_step_events": 9})
    alert = analyzer.check_alert()

    assert metrics["queue_deltas"]["ghost_step_events"] == 7
    assert alert == "queue_fairness_pressure", "Ghost step spike should trigger alert"


def test_fairness_analyzer_rotation_threshold() -> None:
    """Analyzer should alert when rotation events >= threshold."""
    analyzer = FairnessAnalyzer(alert_limit=5)

    # Tick 1: baseline
    analyzer.analyze(tick=1, queue_metrics={"rotation_events": 0})

    # Tick 2: spike (delta = 6)
    metrics = analyzer.analyze(tick=2, queue_metrics={"rotation_events": 6})
    alert = analyzer.check_alert()

    assert metrics["queue_deltas"]["rotation_events"] == 6
    assert alert == "queue_fairness_pressure", "Rotation spike should trigger alert"


def test_fairness_analyzer_reset() -> None:
    """Reset should clear all state."""
    analyzer = FairnessAnalyzer(alert_limit=5)

    # Build up state
    analyzer.analyze(tick=1, queue_metrics={"ghost_step_events": 10})
    analyzer.check_alert()

    # Reset
    analyzer.reset()

    # Should behave as if no previous state
    metrics = analyzer.analyze(tick=1, queue_metrics={"ghost_step_events": 3})
    alert = analyzer.check_alert()

    assert metrics["queue_deltas"]["ghost_step_events"] == 3, "After reset, delta should be from zero baseline"
    assert alert is None


def test_fairness_analyzer_export_import_state() -> None:
    """State export/import should preserve analyzer state."""
    analyzer1 = FairnessAnalyzer(alert_limit=5)

    # Build up state
    analyzer1.analyze(tick=1, queue_metrics={"ghost_step_events": 5, "rotation_events": 2})

    # Export state
    state = analyzer1.export_state()

    # Create new analyzer and import state
    analyzer2 = FairnessAnalyzer(alert_limit=5)
    analyzer2.import_state(state)

    # Should continue from same state
    metrics = analyzer2.analyze(tick=2, queue_metrics={"ghost_step_events": 12, "rotation_events": 3})

    assert metrics["queue_deltas"]["ghost_step_events"] == 7, "Delta should be based on imported state"
    assert metrics["queue_deltas"]["rotation_events"] == 1
