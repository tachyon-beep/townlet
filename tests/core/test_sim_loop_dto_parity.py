from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path

import numpy as np
import pytest

from townlet.config.loader import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.core import policy_registry, telemetry_registry
from townlet.factories.registry import register as factory_register
from townlet.policy.fallback import StubPolicyBackend
from townlet.telemetry.fallback import StubTelemetrySink
from townlet.adapters.policy_scripted import ScriptedPolicyAdapter
from townlet.world.core import WorldContext
from townlet.observations import ObservationBuilder


def _register_stub_ports() -> None:
    policy_registry().register("dto_stub", lambda **kwargs: StubPolicyBackend(**kwargs))
    telemetry_registry().register("dto_stub", lambda **kwargs: StubTelemetrySink(**kwargs))
    factory_register("policy", "dto_stub")(
        lambda **kwargs: ScriptedPolicyAdapter(kwargs["backend"])
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

    bootstrap = loop._build_bootstrap_policy_envelope()
    loop._set_policy_observation_envelope(bootstrap)

    loop.world.context.observation_service = ObservationBuilder(config=config)
    steps = 3
    envelopes: list[object] = []
    queue_metrics_history: list[dict[str, int]] = []
    job_snapshot_history: list[dict[str, dict[str, object]]] = []
    employment_queue_history: list[dict[str, object]] = []
    stability_history: list[dict[str, object]] = []
    queue_affinity_history: list[dict[str, int]] = []
    economy_history: list[dict[str, object]] = []
    anneal_history: list[dict[str, object]] = []
    agent_state_history: list[dict[str, dict[str, object]]] = []
    reward_history: list[dict[str, float]] = []

    for _ in range(steps):
        artifacts = loop.step()
        envelope = artifacts.envelope
        envelopes.append(envelope)
        reward_history.append(dict(artifacts.rewards))
        job_snapshot = loop._collect_job_snapshot(loop.world_adapter)
        employment_metrics = loop._collect_employment_metrics()
        queue_metrics_history.append(loop._collect_queue_metrics())
        job_snapshot_history.append(job_snapshot)
        employment_queue_history.append(employment_metrics)
        stability_history.append(loop.stability.latest_metrics())
        queue_affinity_history.append(loop._collect_queue_affinity_metrics())
        economy_history.append(loop._collect_economy_snapshot())
        anneal_history.append(loop.policy.anneal_context())
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

    for idx, envelope in enumerate(envelopes):
        assert envelope.tick == idx + 1
        dto_agents = {agent.agent_id: agent for agent in envelope.agents}
        state_snapshot = agent_state_history[idx]
        job_snapshot = job_snapshot_history[idx]
        for agent_id, dto_entry in dto_agents.items():
            if dto_entry.needs is not None:
                expected_needs = state_snapshot.get(agent_id, {}).get("needs", {})
                for need, value in dto_entry.needs.items():
                    assert np.isclose(float(value), float(expected_needs.get(need, 0.0)))
            if dto_entry.wallet is not None:
                expected_wallet = state_snapshot.get(agent_id, {}).get("wallet", 0.0)
                assert np.isclose(float(dto_entry.wallet), float(expected_wallet))
            if dto_entry.job is not None:
                expected_job = job_snapshot.get(agent_id)
                if expected_job is not None:
                    assert dto_entry.job == expected_job
        global_rewards = {
            agent_id: components.get("total", 0.0)
            for agent_id, components in envelope.global_context.rewards.items()
        }
        for agent_id, reward in reward_history[idx].items():
            assert np.isclose(global_rewards.get(agent_id, 0.0), reward)

        dto_global = envelope.global_context
        assert dto_global.queue_metrics == queue_metrics_history[idx]
        assert dto_global.employment_snapshot == employment_queue_history[idx]
        assert dto_global.queue_affinity_metrics == queue_affinity_history[idx]
        assert dto_global.economy_snapshot == economy_history[idx]
        assert dto_global.anneal_context == anneal_history[idx]

    loop.close()


def test_simulation_loop_prefers_context_observe(monkeypatch: pytest.MonkeyPatch) -> None:
    _register_stub_ports()
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(
        config,
        policy_provider="dto_stub",
        telemetry_provider="dto_stub",
    )

    loop._set_policy_observation_envelope(loop._build_bootstrap_policy_envelope())
    loop.world.context.observation_service = ObservationBuilder(config=config)

    call_count = {"value": 0}
    original_observe = WorldContext.observe

    def spy_observe(self: WorldContext, *args, **kwargs):
        call_count["value"] += 1
        return original_observe(self, *args, **kwargs)

    monkeypatch.setattr(WorldContext, "observe", spy_observe, raising=False)

    def fail_legacy_batch(*_args, **_kwargs):
        raise AssertionError("legacy observation builder should not run")

    monkeypatch.setattr(loop._observation_builder, "build_batch", fail_legacy_batch, raising=False)

    try:
        artifacts = loop.step()
    finally:
        loop.close()

    assert call_count["value"] > 0
    assert artifacts.envelope.tick == 1
