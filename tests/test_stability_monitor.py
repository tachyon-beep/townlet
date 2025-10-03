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
    config.stability.promotion.window_ticks = 2
    config.stability.promotion.required_passes = 1
    return StabilityMonitor(config)


def _track_minimal(
    monitor: StabilityMonitor,
    *,
    tick: int,
    embedding_warning: bool = False,
    queue_alert: bool = False,
) -> None:
    queue_metrics = {"ghost_step_events": 6} if queue_alert else {}
    embedding_metrics = {"reuse_warning": 1} if embedding_warning else {}
    monitor.track(
        tick=tick,
        rewards={},
        terminated={"alice": False},
        queue_metrics=queue_metrics,
        embedding_metrics=embedding_metrics,
        job_snapshot={},
        events=[],
        employment_metrics={},
        hunger_levels={"alice": 0.5},
        option_switch_counts={"alice": 0},
    )


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
    metrics = monitor.latest_metrics()
    assert "thresholds" in metrics
    assert "promotion" in metrics


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
    metrics = monitor.latest_metrics()
    assert "thresholds" in metrics
    assert "promotion" in metrics


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
    assert "promotion" in restored_metrics


def test_queue_fairness_alerts_include_metrics() -> None:
    monitor = make_monitor()
    monitor.track(
        tick=0,
        rewards={},
        terminated={"alice": False},
        queue_metrics={"ghost_step_events": 6, "rotation_events": 6},
        embedding_metrics={},
        job_snapshot={},
        events=[],
        employment_metrics={},
        hunger_levels={"alice": 0.5},
        option_switch_counts={"alice": 0},
    )
    assert "queue_fairness_pressure" in monitor.latest_alerts
    metrics = monitor.latest_metrics()
    assert metrics["queue_totals"]["ghost_step_events"] == 6
    assert metrics["queue_deltas"]["rotation_events"] == 6
    assert "promotion" in metrics


def test_rivalry_spike_alert_triggers_on_intensity() -> None:
    monitor = make_monitor()
    events = [{"agent_a": "alice", "agent_b": "bob", "intensity": 0.7} for _ in range(6)]
    monitor.track(
        tick=0,
        rewards={},
        terminated={"alice": False},
        queue_metrics={},
        embedding_metrics={},
        job_snapshot={},
        events=[],
        employment_metrics={},
        hunger_levels={"alice": 0.5},
        option_switch_counts={"alice": 0},
        rivalry_events=events,
    )
    assert "rivalry_spike" in monitor.latest_alerts


def test_promotion_window_tracking() -> None:
    monitor = make_monitor()
    for tick in range(3):
        monitor.track(
            tick=tick,
            rewards={},
            terminated={"alice": False},
            hunger_levels={"alice": 0.5},
            option_switch_counts={"alice": 0},
            events=[],
        )
    promotion = monitor.latest_metrics()["promotion"]
    assert promotion["pass_streak"] == 1
    assert promotion["candidate_ready"] is True

    monitor.track(
        tick=3,
        rewards={},
        terminated={"alice": False},
        queue_metrics={"ghost_step_events": 10},
        embedding_metrics={},
        job_snapshot={},
        events=[],
        employment_metrics={},
        hunger_levels={"alice": 0.5},
        option_switch_counts={"alice": 0},
    )
    monitor.track(
        tick=4,
        rewards={},
        terminated={"alice": False},
        hunger_levels={"alice": 0.5},
        option_switch_counts={"alice": 0},
        events=[],
    )
    promotion = monitor.latest_metrics()["promotion"]
    assert promotion["pass_streak"] == 0
    assert promotion["candidate_ready"] is False
    assert promotion["last_result"] == "fail"


def test_promotion_window_respects_allowed_alerts() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.stability.promotion.window_ticks = 2
    config.stability.promotion.required_passes = 2
    config.stability.promotion.allowed_alerts = ("embedding_reuse_warning",)
    monitor = StabilityMonitor(config)

    _track_minimal(monitor, tick=0)
    _track_minimal(monitor, tick=1)
    _track_minimal(monitor, tick=2, embedding_warning=True)
    promotion = monitor.latest_metrics()["promotion"]
    assert promotion["pass_streak"] == 1
    assert promotion["candidate_ready"] is False

    _track_minimal(monitor, tick=3)
    _track_minimal(monitor, tick=4)
    promotion = monitor.latest_metrics()["promotion"]
    assert promotion["pass_streak"] == 2
    assert promotion["candidate_ready"] is True

    _track_minimal(monitor, tick=5, queue_alert=True)
    _track_minimal(monitor, tick=6)
    promotion = monitor.latest_metrics()["promotion"]
    assert promotion["pass_streak"] == 0
    assert promotion["candidate_ready"] is False
