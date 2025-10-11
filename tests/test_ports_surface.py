from __future__ import annotations

from townlet.factories import create_policy, create_telemetry, create_world
from townlet.testing import DummyPolicyBackend, DummyTelemetrySink, DummyWorldRuntime
from townlet.world.dto.observation import GlobalObservationDTO, ObservationEnvelope


def _build_envelope(tick: int = 1) -> ObservationEnvelope:
    return ObservationEnvelope(
        tick=tick,
        schema_version="0.dummy",
        agents=[],
        global_context=GlobalObservationDTO(),
        actions={},
        terminated={},
        termination_reasons={},
    )


def test_dummy_world_runtime_port_surface() -> None:
    runtime = create_world(provider="dummy", agents=("alice",))
    assert isinstance(runtime, DummyWorldRuntime)

    for method in ("reset", "tick", "agents", "observe", "apply_actions", "snapshot", "queue_console"):
        assert hasattr(runtime, method), f"WorldRuntime missing method {method}"

    unexpected = ("publish_tick", "record_console_results", "world_state")
    for attr in unexpected:
        assert not hasattr(runtime, attr), f"WorldRuntime exposes forbidden attribute {attr}"

    runtime.reset()
    result = runtime.tick(tick=1)
    assert isinstance(result.events, list)
    assert list(runtime.agents()) == ["alice"]
    observations = runtime.observe()
    assert "alice" in observations
    snapshot = runtime.snapshot()
    assert snapshot.config_id == runtime.config_id


def test_dummy_policy_backend_surface() -> None:
    backend = create_policy(provider="dummy")
    assert isinstance(backend, DummyPolicyBackend)

    for method in ("on_episode_start", "supports_observation_envelope", "decide", "on_episode_end"):
        assert hasattr(backend, method), f"PolicyBackend missing {method}"

    backend.on_episode_start(["alice"])
    assert backend.supports_observation_envelope() is True
    actions = backend.decide(tick=1, envelope=_build_envelope())
    assert isinstance(actions, dict)
    backend.on_episode_end()


def test_dummy_telemetry_sink_surface() -> None:
    telemetry = create_telemetry(provider="dummy")
    assert isinstance(telemetry, DummyTelemetrySink)

    telemetry.start()
    telemetry.emit_event("dummy.event", {"value": 1})
    telemetry.emit_metric("dummy.metric", 1.0, foo="bar")
    status = telemetry.transport_status()
    assert isinstance(status, dict)
    telemetry.stop()

    forbidden = ("publish_tick", "record_health_metrics", "record_loop_failure")
    for attr in forbidden:
        assert not hasattr(telemetry, attr), f"Telemetry sink exposes forbidden attribute {attr}"
