"""Unit tests for OptionThrashDetector.

DESIGN#3.1: Analyzer Extraction (WP5 Phase 3.1)
"""

from __future__ import annotations

from townlet.stability.analyzers.option_thrash import OptionThrashDetector


def test_option_thrash_no_samples() -> None:
    """Detector should handle no option samples."""
    detector = OptionThrashDetector(
        window_ticks=1000, max_thrash_rate=0.4, min_samples=20
    )

    metrics = detector.analyze(tick=1, option_switch_counts=None)
    alert = detector.check_alert()

    assert metrics["option_thrash_mean"] == 0.0
    assert metrics["option_samples"] == 0
    assert alert is None


def test_option_thrash_low_rate() -> None:
    """Detector should not alert for low switching rate."""
    detector = OptionThrashDetector(
        window_ticks=1000, max_thrash_rate=0.4, min_samples=20
    )

    # Add 30 samples with low switching (all 0)
    for tick in range(30):
        metrics = detector.analyze(
            tick=tick,
            option_switch_counts={
                "alice": 0,
                "bob": 0,
                "carol": 0,
            },
        )

    alert = detector.check_alert()

    assert metrics["option_samples"] == 90  # 30 ticks * 3 agents
    assert metrics["option_thrash_mean"] == 0.0  # No switching
    assert alert is None, "Low switching rate should not trigger alert"


def test_option_thrash_high_rate() -> None:
    """Detector should alert when switching rate exceeds threshold."""
    detector = OptionThrashDetector(
        window_ticks=1000, max_thrash_rate=0.4, min_samples=20
    )

    # Add 10 samples with high switching rate (1+ switches per agent per tick)
    for tick in range(10):
        metrics = detector.analyze(
            tick=tick,
            option_switch_counts={
                "alice": 2,
                "bob": 1,
                "carol": 2,
            },
        )

    alert = detector.check_alert()

    assert metrics["option_samples"] == 30  # 10 ticks * 3 agents
    assert metrics["option_thrash_mean"] > 0.4  # High switching rate (mean ~1.67)
    assert alert == "option_thrashing", "High switching rate should trigger alert"


def test_option_thrash_insufficient_samples() -> None:
    """Detector should not alert without sufficient samples."""
    detector = OptionThrashDetector(
        window_ticks=1000, max_thrash_rate=0.4, min_samples=20
    )

    # Add only 5 samples with high switching
    for tick in range(5):
        detector.analyze(
            tick=tick,
            option_switch_counts={"alice": 2, "bob": 2},
        )

    alert = detector.check_alert()

    # Even with high rate, should not alert due to insufficient samples
    assert alert is None, "Insufficient samples should not trigger alert"


def test_option_thrash_window_pruning() -> None:
    """Detector should prune old samples outside window."""
    detector = OptionThrashDetector(
        window_ticks=100, max_thrash_rate=0.4, min_samples=20
    )

    # Add 50 samples with high switching
    for tick in range(50):
        detector.analyze(
            tick=tick,
            option_switch_counts={"alice": 1, "bob": 1},
        )

    # Jump far ahead (outside window)
    metrics = detector.analyze(
        tick=200,
        option_switch_counts={"alice": 0, "bob": 0},
    )

    # Should only have the latest 2 samples (tick 200)
    assert metrics["option_samples"] == 2


def test_option_thrash_mixed_rates() -> None:
    """Detector should calculate mean across mixed switching rates."""
    detector = OptionThrashDetector(
        window_ticks=1000, max_thrash_rate=0.4, min_samples=20
    )

    # Add 10 samples with low switching
    for tick in range(10):
        detector.analyze(
            tick=tick,
            option_switch_counts={"alice": 0, "bob": 0},
        )

    # Add 10 samples with high switching
    for tick in range(10, 20):
        metrics = detector.analyze(
            tick=tick,
            option_switch_counts={"alice": 2, "bob": 2},
        )

    alert = detector.check_alert()

    # Mean should be ~1.0 ((0*20 + 2*20) / 40)
    assert 0.9 <= metrics["option_thrash_mean"] <= 1.1
    assert alert == "option_thrashing", "High mean should trigger alert"


def test_option_thrash_reset() -> None:
    """Reset should clear all state."""
    detector = OptionThrashDetector(
        window_ticks=1000, max_thrash_rate=0.4, min_samples=20
    )

    # Build up state
    for tick in range(30):
        detector.analyze(
            tick=tick,
            option_switch_counts={"alice": 2, "bob": 2},
        )
    assert detector.check_alert() == "option_thrashing"

    # Reset
    detector.reset()

    # Should behave as if no previous state
    metrics = detector.analyze(tick=1, option_switch_counts=None)
    alert = detector.check_alert()

    assert metrics["option_thrash_mean"] == 0.0
    assert metrics["option_samples"] == 0
    assert alert is None


def test_option_thrash_export_import_state() -> None:
    """State export/import should preserve detector state."""
    detector1 = OptionThrashDetector(
        window_ticks=1000, max_thrash_rate=0.4, min_samples=20
    )

    # Build up state
    for tick in range(10):
        detector1.analyze(
            tick=tick,
            option_switch_counts={"alice": 1, "bob": 0},
        )

    # Export state
    state = detector1.export_state()

    # Create new detector and import state
    detector2 = OptionThrashDetector(
        window_ticks=1000, max_thrash_rate=0.4, min_samples=20
    )
    detector2.import_state(state)

    # Should have same state
    assert len(detector2._option_samples) == 20  # 10 ticks * 2 agents
    assert detector2._last_mean == detector1._last_mean
    assert detector2._last_sample_count == detector1._last_sample_count
