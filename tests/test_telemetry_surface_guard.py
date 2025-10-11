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


def test_publisher_prefers_global_context(tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    publisher = TelemetryPublisher(config)
    publisher.config.personality_channels_enabled = lambda: False
    publisher.config.personality_profiles_enabled = lambda: False

    global_context = {
        "queue_metrics": {
            "cooldown_events": 2,
            "ghost_step_events": 1,
            "rotation_events": 0,
        },
        "relationship_snapshot": {
            "alice": {
                "bob": {"trust": 0.6, "familiarity": 0.4, "rivalry": 0.1},
            }
        },
        "relationship_metrics": {"total": 3},
        "job_snapshot": {
            "alice": {
                "job_id": "cook",
                "on_shift": True,
                "wallet": 12.0,
                "lateness_counter": 0,
                "wages_earned": 1.5,
                "meals_cooked": 2,
                "meals_consumed": 1,
                "basket_cost": 0.5,
                "shift_state": "active",
                "attendance_ratio": 0.9,
                "late_ticks_today": 0,
                "absent_shifts_7d": 0,
                "wages_withheld": 0.0,
                "exit_pending": False,
                "needs": {"energy": 0.8},
            }
        },
        "economy_snapshot": {
            "fridge_1": {
                "type": "fridge",
                "stock": {"meals": 3},
            }
        },
        "economy_settings": {"wage_income": 0.25},
        "price_spikes": {},
        "utilities": {"power": True, "water": False},
        "employment_snapshot": {"pending_count": 0, "review_window": 1440},
        "running_affordances": {
            "bed_1": {
                "agent_id": "alice",
                "affordance_id": "sleep",
                "tick_started": 1,
                "duration_remaining": 3,
                "elapsed_ticks": 5,
            }
        },
        "queues": {
            "active_reservations": {
                "alice": {"bed_1": {"tick": 1}},
            }
        },
        "queue_affinity_metrics": {"assign_calls": 1},
        "stability_metrics": {"queue_totals": {"cooldown_events": 2}},
        "promotion_state": {"state": "monitoring"},
        "anneal_context": {"anneal_ratio": None},
    }
    observations_dto = {
        "tick": 1,
        "dto_schema_version": "0.2.0",
        "agents": [],
        "global": {"queue_metrics": global_context["queue_metrics"]},
    }

    publisher._ingest_loop_tick(
        tick=1,
        world=None,
        rewards={},
        events=[],
        policy_snapshot={},
        policy_metadata={
            "identity": {"config_id": "test", "observation_variant": "dto"},
            "anneal_ratio": None,
            "option_switch_counts": {},
            "possessed_agents": [],
        },
        runtime_variant="dto",
        observations_dto=observations_dto,
        global_context=global_context,
    )

    assert publisher._global_context_warning_fields == set()
    assert publisher.latest_economy_snapshot() == {
        "fridge_1": {"type": "fridge", "stock": {"meals": 3}}
    }
    assert publisher.latest_job_snapshot()["alice"]["job_id"] == "cook"
    runtime_snapshot = publisher.latest_affordance_runtime()
    assert runtime_snapshot["running_count"] == 1
    assert runtime_snapshot["active_reservations"]["alice"]["bed_1"]["tick"] == 1
    assert publisher.latest_utilities()["water"] is False
