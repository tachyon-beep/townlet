from pathlib import Path

from townlet.config import load_config
from townlet.policy.behavior import AgentIntent, BehaviorController
from townlet.policy.runner import PolicyRuntime
from townlet.world.grid import AgentSnapshot

from tests.helpers.modular_world import ModularTestWorld


def _make_world(option_commit_ticks: int | None = None) -> tuple[PolicyRuntime, ModularTestWorld]:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    if option_commit_ticks is not None:
        config.policy_runtime.option_commit_ticks = option_commit_ticks
    runtime = PolicyRuntime(config)
    world = ModularTestWorld.from_config(config)
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    return runtime, world


def test_relationship_guardrail_blocks_rival_chat() -> None:
    runtime, world = _make_world()
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(0, 0),
        needs={"hunger": 0.8, "hygiene": 0.8, "energy": 0.8},
        wallet=1.0,
    )
    world.register_rivalry_conflict("alice", "bob", intensity=5.0)

    class ChatBehaviour(BehaviorController):
        def decide(self, _world, _agent_id, *, dto_world=None):  # type: ignore[override]
            _ = dto_world
            return AgentIntent(kind="chat", target_agent="bob", quality=0.9)

    runtime.behavior = ChatBehaviour()
    envelope = world.context.observe()
    actions = runtime.decide(world, tick=0, envelope=envelope)
    assert actions["alice"]["kind"] == "wait"
    assert actions["alice"].get("blocked") is True


def test_anneal_ratio_uses_provider_when_enabled() -> None:
    runtime, world = _make_world()
    runtime.enable_anneal_blend(True)
    runtime.set_anneal_ratio(1.0)

    def provider(_world, agent_id, _scripted):
        assert agent_id == "alice"
        return AgentIntent(kind="move", position=(1, 1))

    runtime.set_policy_action_provider(provider)
    runtime.seed_anneal_rng(123)

    envelope = world.context.observe()
    actions = runtime.decide(world, tick=0, envelope=envelope)
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
        envelope = world.context.observe()
        actions = runtime.decide(world, tick=tick, envelope=envelope)
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
    envelope = world.context.observe()
    actions = runtime.decide(world, tick=0, envelope=envelope)
    assert actions["alice"]["kind"] == "wait"


def test_option_commit_blocks_switch_until_expiry() -> None:
    runtime, world = _make_world(option_commit_ticks=3)
    runtime.enable_anneal_blend(True)
    runtime.set_anneal_ratio(1.0)

    intents = [
        AgentIntent(kind="move", position=(1, 1)),
        AgentIntent(kind="request", object_id="obj_a"),
        AgentIntent(kind="wait"),
        AgentIntent(kind="request", object_id="obj_b"),
    ]
    call_index = {"value": 0}

    def provider(_world, _agent_id, _scripted):
        idx = min(call_index["value"], len(intents) - 1)
        call_index["value"] += 1
        return intents[idx]

    runtime.set_policy_action_provider(provider)

    def run_tick(tick: int) -> tuple[dict[str, object], dict[str, object]]:
        world.tick = tick
        envelope = world.context.observe()
        actions = runtime.decide(world, tick=tick, envelope=envelope)
        entry = dict(runtime.transitions.get("alice", {}))
        runtime.post_step({"alice": 0.0}, {"alice": False})
        return actions, entry

    actions, entry = run_tick(0)
    assert actions["alice"]["kind"] == "move"
    assert entry.get("option_commit_remaining") == 3
    assert entry.get("option_commit_enforced") is False
    assert runtime._option_commit_until.get("alice") == 3

    actions, entry = run_tick(1)
    assert actions["alice"]["kind"] == "move"
    assert entry.get("option_commit_remaining") == 2
    assert entry.get("option_commit_enforced") is True
    assert entry.get("option_commit_kind") == "move"

    actions, entry = run_tick(2)
    assert actions["alice"]["kind"] == "move"
    assert entry.get("option_commit_remaining") == 1
    assert entry.get("option_commit_enforced") is True

    actions, entry = run_tick(3)
    assert actions["alice"]["kind"] == "request"
    assert entry.get("option_commit_remaining") == 3
    assert entry.get("option_commit_enforced") is False
    assert entry.get("option_commit_kind") == "request"


def test_option_commit_clears_on_termination() -> None:
    runtime, world = _make_world(option_commit_ticks=4)
    runtime.enable_anneal_blend(True)
    runtime.set_anneal_ratio(1.0)

    runtime.set_policy_action_provider(
        lambda _world, _agent_id, _scripted: AgentIntent(kind="move", position=(2, 2))
    )
    world.tick = 0
    envelope = world.context.observe()
    runtime.decide(world, tick=0, envelope=envelope)
    runtime.post_step({"alice": 0.0}, {"alice": True})
    assert "alice" not in runtime._option_commit_until
    assert "alice" not in runtime._option_committed_intent


def test_option_commit_respects_disabled_setting() -> None:
    runtime, world = _make_world(option_commit_ticks=0)
    runtime.enable_anneal_blend(True)
    runtime.set_anneal_ratio(1.0)
    runtime.set_policy_action_provider(
        lambda _world, _agent_id, _scripted: AgentIntent(kind="move", position=(3, 3))
    )
    world.tick = 0
    envelope = world.context.observe()
    actions = runtime.decide(world, tick=0, envelope=envelope)
    assert actions["alice"]["kind"] == "move"
    entry = runtime.transitions.get("alice", {})
    assert "option_commit_remaining" not in entry
    assert "alice" not in runtime._option_commit_until
