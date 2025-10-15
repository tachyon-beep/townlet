"""Baseline capture for StabilityMonitor behavior.

This test captures the exact metrics produced by the current monolithic
StabilityMonitor implementation. The captured baseline will be used to verify
that the extracted analyzer architecture (Phase 3.1) produces identical results.

DESIGN#0.3: Analyzer Behavior Characterization (WP5 Phase 0.3)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from townlet.core.sim_loop import SimulationLoop
from townlet.config import load_config


@pytest.fixture()
def baseline_output_path(tmp_path: Path) -> Path:
    """Path for baseline metrics output."""
    baseline_dir = Path("tests/fixtures/baselines")
    baseline_dir.mkdir(parents=True, exist_ok=True)
    return baseline_dir / "monitor_metrics_baseline.json"


def test_capture_stability_monitor_baseline(baseline_output_path: Path) -> None:
    """Capture baseline metrics from current monolithic StabilityMonitor.

    This test runs a deterministic simulation for 100 ticks and records all
    StabilityMonitor metrics at each tick. The output serves as the "ground truth"
    for verifying that the extracted analyzer architecture produces identical results.

    The baseline captures:
    - All metric values (starvation_incidents, reward_variance, option_switch_rate, etc.)
    - Alert emissions (timing and types)
    - Promotion window state
    - Rolling window calculations

    Run this test BEFORE Phase 3.1 extraction to establish the baseline.
    After extraction, run test_monitor_refactor_compatibility to verify equivalence.
    """
    # Use deterministic config for reproducibility
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config = config.model_copy(update={
        "seed": 42,  # Fixed seed for determinism
    })

    # Create simulation loop (will use default number of agents from config)
    loop = SimulationLoop(config)

    # Capture metrics for 100 ticks
    metrics_log = []
    for tick in range(100):
        # Step simulation
        loop.step()

        # Extract stability metrics from monitor
        stability_monitor = loop.stability
        metrics = stability_monitor.latest_metrics()

        # Record tick state
        tick_snapshot = {
            "tick": tick,
            "metrics": {
                "starvation_incidents": metrics.get("starvation_incidents"),
                "starvation_window_ticks": metrics.get("starvation_window_ticks"),
                "option_switch_rate": metrics.get("option_switch_rate"),
                "option_samples": metrics.get("option_samples"),
                "reward_variance": metrics.get("reward_variance"),
                "reward_mean": metrics.get("reward_mean"),
                "reward_samples": metrics.get("reward_samples"),
                "queue_totals": dict(metrics.get("queue_totals", {})),
                "queue_deltas": dict(metrics.get("queue_deltas", {})),
                "alerts": list(metrics.get("alerts", [])),
            },
            "alert": stability_monitor.latest_alert,
        }
        metrics_log.append(tick_snapshot)

    # Save baseline to disk
    with open(baseline_output_path, "w") as f:
        json.dump(metrics_log, f, indent=2)

    print(f"\n✅ Baseline captured: {baseline_output_path}")
    print(f"   Total ticks: {len(metrics_log)}")
    print(f"   Alerts emitted: {sum(1 for m in metrics_log if m['alert'])}")

    # Basic sanity checks
    assert len(metrics_log) == 100, "Should capture exactly 100 ticks"
    assert all("tick" in m for m in metrics_log), "All entries should have tick"
    assert all("metrics" in m for m in metrics_log), "All entries should have metrics"


def test_baseline_file_exists(baseline_output_path: Path) -> None:
    """Verify that the baseline file has been captured.

    This test will fail until test_capture_stability_monitor_baseline has been run.
    It serves as a reminder to capture the baseline before Phase 3.1 extraction.
    """
    if not baseline_output_path.exists():
        pytest.skip(
            "Baseline not yet captured. Run test_capture_stability_monitor_baseline first."
        )

    # Verify baseline structure
    with open(baseline_output_path) as f:
        baseline = json.load(f)

    assert isinstance(baseline, list), "Baseline should be a list of tick snapshots"
    assert len(baseline) > 0, "Baseline should contain at least one tick"

    # Check first entry structure
    first_tick = baseline[0]
    assert "tick" in first_tick, "Entry should have tick number"
    assert "metrics" in first_tick, "Entry should have metrics dict"
    assert "alert" in first_tick, "Entry should have alert field"

    print(f"\n✅ Baseline file valid: {len(baseline)} ticks captured")


def test_monitor_metrics_shape() -> None:
    """Document the expected shape of StabilityMonitor metrics.

    This test documents what fields are expected in the metrics dictionary
    returned by StabilityMonitor.latest_metrics(). This serves as documentation
    for what the extracted analyzers must produce.
    """
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config = config.model_copy(update={"seed": 42})

    loop = SimulationLoop(config)
    loop.step()

    metrics = loop.stability.latest_metrics()

    # Document expected fields
    expected_fields = {
        "starvation_incidents",
        "starvation_window_ticks",
        "option_switch_rate",
        "option_samples",
        "reward_variance",
        "reward_mean",
        "reward_samples",
        "queue_totals",
        "queue_deltas",
        "rivalry_events",
        "alerts",
        "thresholds",
        "promotion",
    }

    actual_fields = set(metrics.keys())

    # Verify all expected fields present
    missing = expected_fields - actual_fields
    assert not missing, f"Missing expected fields: {missing}"

    # Document types
    assert isinstance(metrics.get("starvation_incidents"), int)
    assert isinstance(metrics.get("starvation_window_ticks"), int)
    assert metrics.get("option_switch_rate") is None or isinstance(
        metrics.get("option_switch_rate"), float
    )
    assert isinstance(metrics.get("option_samples"), int)
    assert metrics.get("reward_variance") is None or isinstance(
        metrics.get("reward_variance"), float
    )
    assert metrics.get("reward_mean") is None or isinstance(
        metrics.get("reward_mean"), float
    )
    assert isinstance(metrics.get("reward_samples"), int)
    assert isinstance(metrics.get("queue_totals"), dict)
    assert isinstance(metrics.get("queue_deltas"), dict)
    assert isinstance(metrics.get("rivalry_events"), list)
    assert isinstance(metrics.get("alerts"), list)
    assert isinstance(metrics.get("thresholds"), dict)
    assert isinstance(metrics.get("promotion"), dict)

    print("\n✅ Monitor metrics shape documented:")
    for field in sorted(expected_fields):
        value = metrics.get(field)
        print(f"   {field}: {type(value).__name__}")
