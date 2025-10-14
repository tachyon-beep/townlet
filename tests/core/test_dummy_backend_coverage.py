"""Comprehensive tests for dummy implementations to ensure WP1 completion."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers.dummy_loop import build_dummy_loop
from townlet.config import SimulationConfig, load_config
from townlet.dto.observations import ObservationEnvelope
from townlet.dto.world import SimulationSnapshot


@pytest.fixture()
def simulation_config() -> SimulationConfig:
    return load_config(Path("configs/examples/poc_hybrid.yaml"))


def test_dummy_world_runtime_snapshot(simulation_config) -> None:
    """Test that dummy world runtime returns valid SimulationSnapshot DTO."""
    harness = build_dummy_loop(simulation_config, agent_ids=("alice", "bob"))
    runtime = harness.runtime

    snapshot = runtime.snapshot()

    assert isinstance(snapshot, SimulationSnapshot)
    assert snapshot.config_id == "dummy-config"
    assert snapshot.tick == 0


def test_dummy_policy_backend_interface(simulation_config) -> None:
    """Test that dummy policy backend satisfies PolicyBackend protocol."""
    harness = build_dummy_loop(simulation_config, agent_ids=("alice", "bob"))
    policy = harness.policy

    # Test episode lifecycle
    policy.on_episode_start(("alice", "bob"))
    policy.on_episode_end()

    # Test decision interface
    loop = harness.loop
    artifacts = loop.step()
    actions = policy.decide(harness.world, 1, envelope=artifacts.envelope)

    assert isinstance(actions, dict)
    assert "alice" in actions
    assert "bob" in actions


def test_dummy_loop_multi_tick_determinism(simulation_config) -> None:
    """Test that dummy loop produces deterministic tick sequence."""
    harness = build_dummy_loop(simulation_config, agent_ids=("alice",))
    loop = harness.loop

    ticks_data = []
    for _ in range(5):
        artifacts = loop.step()
        ticks_data.append({
            "tick": loop.tick,
            "envelope_tick": artifacts.envelope.tick,
            "agents_count": len(artifacts.envelope.agents),
        })

    assert len(ticks_data) == 5
    assert ticks_data[0]["tick"] == 1
    assert ticks_data[4]["tick"] == 5
    assert all(data["agents_count"] == 1 for data in ticks_data)


def test_dummy_telemetry_sink_captures_events(simulation_config) -> None:
    """Test that DummyTelemetrySink correctly captures telemetry events."""
    harness = build_dummy_loop(simulation_config, agent_ids=("alice",))
    telemetry_sink = harness.telemetry_sink

    # Run a few ticks
    for _ in range(3):
        harness.loop.step()

    # Verify events captured
    tick_events = [e for e in telemetry_sink.events if e[0] == "loop.tick"]
    health_events = [e for e in telemetry_sink.events if e[0] == "loop.health"]

    assert len(tick_events) >= 3, "Expected at least 3 loop.tick events"
    assert len(health_events) >= 3, "Expected at least 3 loop.health events"

    # Verify event payloads have expected structure
    for event_name, payload in telemetry_sink.events:
        assert isinstance(event_name, str)
        assert isinstance(payload, dict)
        if event_name == "loop.tick":
            assert "tick" in payload


def test_dummy_world_runtime_agents(simulation_config) -> None:
    """Test that dummy world runtime exposes agent IDs."""
    harness = build_dummy_loop(simulation_config, agent_ids=("alice", "bob", "charlie"))
    runtime = harness.runtime

    agents = list(runtime.agents())

    assert len(agents) == 3
    assert "alice" in agents
    assert "bob" in agents
    assert "charlie" in agents


def test_dummy_world_runtime_observe(simulation_config) -> None:
    """Test that dummy world runtime produces observations."""
    harness = build_dummy_loop(simulation_config, agent_ids=("alice",))
    runtime = harness.runtime

    obs = runtime.observe(agent_ids=["alice"])

    assert isinstance(obs, dict)
    assert "alice" in obs
    assert "tick" in obs["alice"]


def test_dummy_context_observation_envelope(simulation_config) -> None:
    """Test that dummy context produces valid ObservationEnvelope DTOs."""
    harness = build_dummy_loop(simulation_config, agent_ids=("alice", "bob"))
    loop = harness.loop

    artifacts = loop.step()

    assert isinstance(artifacts.envelope, ObservationEnvelope)
    assert len(artifacts.envelope.agents) == 2
    assert artifacts.envelope.tick == 1
    assert artifacts.envelope.global_context is not None


def test_dummy_reward_engine_returns_dtos(simulation_config) -> None:
    """Test that dummy reward engine returns RewardBreakdown DTOs."""
    from townlet.dto.rewards import RewardBreakdown

    harness = build_dummy_loop(simulation_config, agent_ids=("alice",))
    loop = harness.loop

    artifacts = loop.step()

    # Verify rewards are RewardBreakdown DTOs (via loop internals)
    reward_engine = loop.rewards
    terminated = {"alice": False}
    breakdowns = reward_engine.compute(harness.world, terminated, {})

    assert isinstance(breakdowns, dict)
    assert "alice" in breakdowns
    assert isinstance(breakdowns["alice"], RewardBreakdown)
    assert breakdowns["alice"].total == 0.0
    assert breakdowns["alice"].agent_id == "alice"


def test_dummy_loop_multiple_agents(simulation_config) -> None:
    """Test dummy loop handles multiple agents correctly."""
    agent_ids = ("alice", "bob", "charlie", "dave")
    harness = build_dummy_loop(simulation_config, agent_ids=agent_ids)
    loop = harness.loop

    artifacts = loop.step()

    assert len(artifacts.envelope.agents) == len(agent_ids)
    for agent_id in agent_ids:
        agent_obs = next((a for a in artifacts.envelope.agents if a.agent_id == agent_id), None)
        assert agent_obs is not None, f"Missing observation for {agent_id}"
        assert agent_obs.agent_id == agent_id
