from pathlib import Path

from townlet.config import load_config
from townlet.policy.behavior import AgentIntent
from townlet.policy.runner import PolicyRuntime
from townlet.world.grid import AgentSnapshot, WorldState


def _make_world() -> tuple[PolicyRuntime, WorldState]:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    runtime = PolicyRuntime(config)
    world = WorldState.from_config(config)
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    return runtime, world


def test_anneal_ratio_uses_provider_when_enabled() -> None:
    runtime, world = _make_world()
    runtime.enable_anneal_blend(True)
    runtime.set_anneal_ratio(1.0)

    def provider(_world, agent_id, _scripted):
        assert agent_id == "alice"
        return AgentIntent(kind="move", position=(1, 1))

    runtime.set_policy_action_provider(provider)
    runtime.seed_anneal_rng(123)

    actions = runtime.decide(world, tick=0)
    assert actions["alice"]["kind"] == "move"
    assert actions["alice"].get("position") == (1, 1)


def test_anneal_ratio_mix_respects_probability() -> None:
    runtime, world = _make_world()
    runtime.enable_anneal_blend(True)
    runtime.set_anneal_ratio(0.5)

    def provider(_world, _agent_id, _scripted):
        return AgentIntent(kind="move", position=(2, 2), blocked=False)

    runtime.set_policy_action_provider(provider)
    runtime.seed_anneal_rng(42)

    move_count = 0
    wait_count = 0
    for tick in range(20):
        actions = runtime.decide(world, tick=tick)
        if actions["alice"]["kind"] == "move":
            move_count += 1
        else:
            wait_count += 1
    assert move_count > 0
    assert wait_count > 0


def test_blend_disabled_returns_scripted() -> None:
    runtime, world = _make_world()

    def provider(_world, _agent_id, _scripted):
        return AgentIntent(kind="move", position=(5, 5))

    runtime.set_policy_action_provider(provider)
    runtime.set_anneal_ratio(1.0)
    runtime.enable_anneal_blend(False)
    actions = runtime.decide(world, tick=0)
    assert actions["alice"]["kind"] == "wait"
