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


def test_loop_tick_payload_is_dto_only(tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)

    try:
        loop.step()
        dispatcher = loop.telemetry.event_dispatcher
        latest_tick = dispatcher.latest_tick
        assert latest_tick is not None, "loop.tick event was not captured"

        legacy_keys = {"observations", "latest_rewards", "latest_reward_breakdown"}
        offending = legacy_keys.intersection(latest_tick.keys())
        assert not offending, f"Legacy observation keys leaked into loop.tick payload: {sorted(offending)}"

        assert "observations_dto" in latest_tick, "DTO envelope missing from loop.tick payload"
        assert "policy_metadata" in latest_tick, "Policy metadata missing from loop.tick payload"
        global_context = latest_tick.get("global_context")
        assert isinstance(global_context, dict), "Global context missing from loop.tick payload"
        assert "queue_metrics" in global_context, "Queue metrics missing from global context"
        dto_envelope = latest_tick["observations_dto"]
        assert isinstance(dto_envelope, dict), "DTO envelope should be a dictionary"
        assert dto_envelope.get("tick") == loop.tick

        publisher = loop.telemetry
        metadata_snapshot = publisher.latest_policy_metadata_snapshot()
        assert metadata_snapshot is not None, "Telemetry publisher did not cache policy metadata snapshot"
        identity_snapshot = metadata_snapshot.get("identity")
        assert isinstance(identity_snapshot, dict), "Policy identity payload missing from metadata snapshot"
        assert "observation_variant" in identity_snapshot

        envelope_snapshot = publisher.latest_observation_envelope()
        assert envelope_snapshot is not None, "Telemetry publisher did not cache the DTO observation envelope"
        assert envelope_snapshot.get("tick") == loop.tick
        assert envelope_snapshot == dto_envelope
    finally:
        loop.close()
