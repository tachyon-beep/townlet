from __future__ import annotations

from pathlib import Path

import numpy as np

from townlet.config.loader import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.core import policy_registry, telemetry_registry
from townlet.factories.registry import register as factory_register
from townlet.policy.fallback import StubPolicyBackend
from townlet.telemetry.fallback import StubTelemetrySink


def _register_stub_ports() -> None:
    policy_registry().register("dto_stub", lambda **kwargs: StubPolicyBackend(**kwargs))
    telemetry_registry().register("dto_stub", lambda **kwargs: StubTelemetrySink(**kwargs))
    factory_register("policy", "dto_stub")(
        lambda **kwargs: StubPolicyBackend(**kwargs)
    )
    factory_register("telemetry", "dto_stub")(
        lambda **kwargs: StubTelemetrySink(**kwargs)
    )


def test_simulation_loop_dto_parity_across_ticks(tmp_path) -> None:
    _register_stub_ports()
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(
        config,
        policy_provider="dto_stub",
        telemetry_provider="dto_stub",
    )
    steps = 3
    world_snapshots: list[dict[str, object]] = []
    dto_snapshots: list[dict[str, object]] = []
    dto_actions: list[dict[str, object]] = []
    legacy_actions: list[dict[str, object]] = []

    for _ in range(steps):
        artifacts = loop.step()
        world_snapshot = {
            "tick": loop.tick,
            "observations": artifacts.observations,
            "rewards": dict(artifacts.rewards),
        }
        world_snapshots.append(world_snapshot)
        dto_snapshots.append(
            {
                "tick": loop.tick,
                "envelope": loop._policy_observation_envelope,  # type: ignore[attr-defined]
            }
        )
        dto_actions.append(artifacts.observations)
        legacy_actions.append(loop.runtime._pending_actions.copy())  # type: ignore[attr-defined]

    for world_payload, dto_payload in zip(world_snapshots, dto_snapshots):
        envelope = dto_payload["envelope"]
        assert envelope is not None
        dto_agents = {agent.agent_id: agent for agent in envelope.agents}
        for agent_id, obs in world_payload["observations"].items():
            assert agent_id in dto_agents
            dto_entry = dto_agents[agent_id]
            if dto_entry.features is not None:
                np.testing.assert_allclose(
                    obs["features"],
                    dto_entry.features,
                    rtol=1e-6,
                    atol=1e-6,
                )
            if dto_entry.map is not None and "map" in obs:
                np.testing.assert_allclose(
                    obs["map"],
                    dto_entry.map,
                    rtol=1e-6,
                    atol=1e-6,
                )
        global_rewards = {
            agent_id: components.get("total", 0.0)
            for agent_id, components in envelope.global_context.rewards.items()
        }
        for agent_id, reward in world_payload["rewards"].items():
            assert np.isclose(global_rewards.get(agent_id, 0.0), reward)
    for legacy, dto in zip(legacy_actions, dto_actions):
        assert set(legacy.keys()) == set(dto.keys())
        for agent_id in legacy:
            assert legacy[agent_id] == dto[agent_id]

    loop.close()
