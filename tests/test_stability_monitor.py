from pathlib import Path

from townlet.config import load_config
from townlet.stability.monitor import StabilityMonitor


def make_monitor() -> StabilityMonitor:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.stability.starvation.min_duration_ticks = 2
    config.stability.option_thrash.min_samples = 2
    config.stability.option_thrash.max_switch_rate = 0.1
    config.stability.reward_variance.min_samples = 2
    config.stability.reward_variance.max_variance = 0.01
    return StabilityMonitor(config)


def test_starvation_spike_alert_triggers_after_streak() -> None:
    monitor = make_monitor()
    for tick in range(2):
        monitor.track(
            tick=tick,
            rewards={},
            terminated={"alice": False},
            hunger_levels={"alice": 0.01},
            option_switch_counts={"alice": 0},
            events=[],
        )
    assert "starvation_spike" in monitor.latest_alerts
    assert "thresholds" in monitor.latest_metrics()


def test_option_thrash_alert_averages_over_window() -> None:
    monitor = make_monitor()
    for tick in range(2):
        monitor.track(
            tick=tick,
            rewards={},
            terminated={"alice": False},
            hunger_levels={"alice": 0.5},
            option_switch_counts={"alice": 1},
            events=[],
        )
    assert "option_thrash_detected" in monitor.latest_alerts
    assert "thresholds" in monitor.latest_metrics()


def test_reward_variance_alert_exports_state() -> None:
    monitor = make_monitor()
    monitor.track(
        tick=0,
        rewards={"alice": 0.5, "bob": -0.5},
        terminated={"alice": False, "bob": False},
        hunger_levels={"alice": 0.5, "bob": 0.5},
        option_switch_counts={"alice": 0, "bob": 0},
        events=[],
    )
    monitor.track(
        tick=1,
        rewards={"alice": 0.5, "bob": -0.5},
        terminated={"alice": False, "bob": False},
        hunger_levels={"alice": 0.5, "bob": 0.5},
        option_switch_counts={"alice": 0, "bob": 0},
        events=[],
    )
    assert "reward_variance_spike" in monitor.latest_alerts

    exported = monitor.export_state()
    restored = make_monitor()
    restored.import_state(exported)
    assert restored.latest_alert == monitor.latest_alert
    restored_metrics = restored.latest_metrics()
    monitor_metrics = monitor.latest_metrics()
    assert restored_metrics["reward_variance"] == monitor_metrics["reward_variance"]
    assert "thresholds" in restored_metrics
