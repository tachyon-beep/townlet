from __future__ import annotations

from pathlib import Path

from townlet.config import load_config
from townlet.core.interfaces import TelemetrySinkProtocol
from townlet.core.sim_loop import SimulationLoop
from townlet.telemetry.publisher import TelemetryPublisher


def test_telemetry_protocol_excludes_legacy_writers() -> None:
    legacy_methods = {
        "publish_tick",
        "record_console_results",
        "record_health_metrics",
        "record_loop_failure",
    }

    protocol_attrs = {name for name in dir(TelemetrySinkProtocol)}
    publisher_attrs = {name for name in dir(TelemetryPublisher)}

    offending_protocol = legacy_methods & protocol_attrs
    offending_publisher = legacy_methods & publisher_attrs

    assert not offending_protocol, f"Legacy telemetry writers still exposed on protocol: {sorted(offending_protocol)}"
    assert not offending_publisher, f"Legacy telemetry writers reintroduced on publisher: {sorted(offending_publisher)}"


def test_simulation_loop_emits_events_via_dispatcher(tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    dispatcher = loop.telemetry.event_dispatcher

    try:
        loop.step()
        latest_tick = dispatcher.latest_tick
        assert latest_tick is not None, "loop.tick event was not captured by dispatcher"
        assert latest_tick.get("tick") == loop.tick

        latest_health = dispatcher.latest_health
        assert latest_health is not None, "loop.health event was not captured by dispatcher"
        assert latest_health.get("tick") == loop.tick

        latest_failure = dispatcher.latest_failure
        assert latest_failure is None, "Failure event should not be recorded during healthy tick"
    finally:
        loop.close()
