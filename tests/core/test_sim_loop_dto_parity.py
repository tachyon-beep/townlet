from __future__ import annotations

from dataclasses import asdict, is_dataclass
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


def _to_builtin(value):
    if value is None:
        return None
    if isinstance(value, (int, float, str, bool)):
        return value
    if is_dataclass(value):
        return _to_builtin(asdict(value))
    if isinstance(value, dict):
        return {str(k): _to_builtin(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_builtin(v) for v in value]
    return value


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
    queue_metrics_history: list[dict[str, int]] = []
    job_snapshot_history: list[dict[str, dict[str, object]]] = []
    employment_queue_history: list[dict[str, object]] = []
    stability_history: list[dict[str, object]] = []
    queue_affinity_history: list[dict[str, int]] = []
    economy_history: list[dict[str, object]] = []
    anneal_history: list[dict[str, object]] = []
    agent_state_history: list[dict[str, dict[str, object]]] = []

    for _ in range(steps):
        artifacts = loop.step()
        job_snapshot = loop._collect_job_snapshot(loop.world_adapter)
        employment_metrics = loop._collect_employment_metrics()
        world_snapshot = {
            "tick": loop.tick,
            "observations": artifacts.observations,
            "rewards": dict(artifacts.rewards),
            "queue_metrics": loop._collect_queue_metrics(),
            "employment_snapshot": job_snapshot,
            "stability_metrics": loop.stability.latest_metrics(),
        }
        world_snapshots.append(world_snapshot)

        queue_metrics_history.append(world_snapshot["queue_metrics"])
        job_snapshot_history.append(job_snapshot)
        employment_queue_history.append(employment_metrics)
        stability_history.append(world_snapshot["stability_metrics"])
        queue_affinity_history.append(loop._collect_queue_affinity_metrics())
        economy_history.append(loop._collect_economy_snapshot())
        anneal_history.append(loop.policy.anneal_context())

        dto_snapshots.append(
            {
                "tick": loop.tick,
                "envelope": loop._policy_observation_envelope,  # type: ignore[attr-defined]
            }
        )
        dto_actions.append(artifacts.observations)
        legacy_actions.append(loop.runtime._pending_actions.copy())  # type: ignore[attr-defined]
        state_snapshot: dict[str, dict[str, object]] = {}
        for agent_id, snapshot in loop.world.agents.items():
            inventory = snapshot.inventory or {}
            personality = snapshot.personality
            state_snapshot[agent_id] = {
                "needs": {str(k): float(v) for k, v in snapshot.needs.items()},
                "wallet": float(snapshot.wallet),
                "inventory": {str(k): _to_builtin(v) for k, v in inventory.items()},
                "personality": _to_builtin(personality),
            }
        agent_state_history.append(state_snapshot)

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
            if dto_entry.needs is not None:
                expected_needs = agent_state_history[dto_payload["tick"] - 1][agent_id]["needs"]
                for need, value in dto_entry.needs.items():
                    assert np.isclose(float(value), float(expected_needs.get(need, 0.0)))
            if dto_entry.wallet is not None:
                expected_wallet = agent_state_history[dto_payload["tick"] - 1][agent_id]["wallet"]
                assert np.isclose(dto_entry.wallet, expected_wallet)
            if dto_entry.job is not None:
                expected_job = job_snapshot_history[dto_payload["tick"] - 1].get(agent_id)
                if expected_job is not None:
                    assert dto_entry.job == expected_job
        global_rewards = {
            agent_id: components.get("total", 0.0)
            for agent_id, components in envelope.global_context.rewards.items()
        }
        for agent_id, reward in world_payload["rewards"].items():
            assert np.isclose(global_rewards.get(agent_id, 0.0), reward)

        dto_global = envelope.global_context
        assert dto_global.queue_metrics == world_payload["queue_metrics"]
        idx = dto_payload["tick"] - 1
        assert dto_global.employment_snapshot == employment_queue_history[idx]
        assert dto_global.queue_affinity_metrics == queue_affinity_history[idx]
        assert dto_global.economy_snapshot == economy_history[idx]
        assert dto_global.anneal_context == anneal_history[idx]

    for legacy, dto in zip(legacy_actions, dto_actions):
        assert set(legacy.keys()) == set(dto.keys())
        for agent_id in legacy:
            assert legacy[agent_id] == dto[agent_id]

    loop.close()
