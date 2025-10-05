from pathlib import Path
from types import MappingProxyType

import pytest

from townlet.config import SimulationConfig, load_config
from townlet.rewards.engine import RewardEngine
from townlet.world.grid import AgentSnapshot, WorldState


class StubSnapshot:
    def __init__(self, needs: dict[str, float], wallet: float) -> None:
        self.needs = dict(needs)
        self.wallet = wallet


class StubWorld:
    def __init__(
        self,
        config,
        snapshot: StubSnapshot,
        context: dict[str, float],
    ) -> None:
        self.config = config
        self.tick = 0
        snapshot.agent_id = "alice"
        snapshot.wages_paid = context.get("wages_paid", 0.0)
        snapshot.punctuality_bonus = context.get("punctuality_bonus", 0.0)
        self.agents = {"alice": snapshot}
        self._snapshots = {"alice": snapshot}
        self._context = context

    def agent_snapshots_view(self):
        return MappingProxyType(self._snapshots)

    def consume_chat_events(self):
        return []

    def agent_context(self, agent_id: str) -> dict[str, float]:
        return self._context

    def _employment_context_wages(self, agent_id: str) -> float:
        return float(self._context.get("wages_paid", 0.0))

    def _employment_context_punctuality(self, agent_id: str) -> float:
        return float(self._context.get("punctuality_bonus", 0.0))

    def relationship_tie(self, subject: str, target: str):
        return None

    def rivalry_top(self, agent_id: str, limit: int):
        return []


def _make_world(hunger: float = 0.5) -> WorldState:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": hunger, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    return world


def test_reward_negative_with_high_deficit() -> None:
    world = _make_world(hunger=0.1)
    rewards = RewardEngine(world.config).compute(world, terminated={})
    assert rewards["alice"] < 0.0


def test_reward_clipped_by_config() -> None:
    world = _make_world(hunger=0.0)
    engine = RewardEngine(world.config)
    rewards = engine.compute(world, terminated={})
    assert rewards["alice"] >= -world.config.rewards.clip.clip_per_tick


def test_survival_tick_positive_when_balanced() -> None:
    world = _make_world(hunger=0.8)
    engine = RewardEngine(world.config)
    rewards = engine.compute(world, terminated={})
    expected = world.config.rewards.survival_tick
    weights = world.config.rewards.needs_weights
    for need, value in world.agents["alice"].needs.items():
        weight = getattr(weights, need, 0.0)
        deficit = 1.0 - value
        expected -= weight * max(0.0, deficit) ** 2
    clip = world.config.rewards.clip.clip_per_tick
    expected = max(min(expected, clip), -clip)
    assert rewards["alice"] == pytest.approx(expected)


def test_chat_reward_applied_for_successful_conversation() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    for agent_id in ("alice", "bob"):
        world.agents[agent_id] = AgentSnapshot(
            agent_id=agent_id,
            position=(0, 0),
            needs={"hunger": 1.0, "hygiene": 1.0, "energy": 1.0},
            wallet=1.0,
        )
    world.tick = 100
    world.record_chat_success("alice", "bob", quality=1.0)

    engine = RewardEngine(world.config)
    terminated = dict.fromkeys(world.agents, False)
    rewards = engine.compute(world, terminated)

    base = world.config.rewards.survival_tick
    social_cfg = world.config.rewards.social
    expected_bonus = (
        social_cfg.C1_chat_base
        + social_cfg.C1_coeff_trust * 0.05
        + social_cfg.C1_coeff_fam * 0.10
    )
    assert rewards["alice"] == pytest.approx(base + expected_bonus, rel=1e-5)
    assert rewards["bob"] == pytest.approx(base + expected_bonus, rel=1e-5)


def test_chat_reward_skipped_when_needs_override_triggers() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.1, "hygiene": 1.0, "energy": 1.0},
        wallet=1.0,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(0, 0),
        needs={"hunger": 1.0, "hygiene": 1.0, "energy": 1.0},
        wallet=1.0,
    )
    world.tick = 5
    world.record_chat_success("alice", "bob", quality=1.0)

    engine = RewardEngine(world.config)
    terminated = dict.fromkeys(world.agents, False)
    rewards = engine.compute(world, terminated)

    assert rewards["bob"] > rewards["alice"]
    assert rewards["alice"] <= 0.0


def test_chat_events_ignored_when_social_stage_disabled() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    data = config.model_dump()
    data["features"]["stages"]["social_rewards"] = "OFF"
    config = SimulationConfig.model_validate(data)
    world = WorldState.from_config(config)
    for agent_id in ("alice", "bob"):
        world.agents[agent_id] = AgentSnapshot(
            agent_id=agent_id,
            position=(0, 0),
            needs={"hunger": 1.0, "hygiene": 1.0, "energy": 1.0},
            wallet=1.0,
        )
    world.record_chat_success("alice", "bob", quality=1.0)

    engine = RewardEngine(config)
    terminated = dict.fromkeys(world.agents, False)
    rewards = engine.compute(world, terminated)

    for agent_id in ("alice", "bob"):
        assert rewards[agent_id] == pytest.approx(config.rewards.survival_tick)
        breakdown = engine.latest_reward_breakdown()[agent_id]
        assert breakdown["social"] == pytest.approx(0.0)


def test_chat_reward_blocked_within_termination_window() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    for agent_id in ("alice", "bob"):
        world.agents[agent_id] = AgentSnapshot(
            agent_id=agent_id,
            position=(0, 0),
            needs={"hunger": 1.0, "hygiene": 1.0, "energy": 1.0},
            wallet=1.0,
        )
    engine = RewardEngine(world.config)

    world.tick = 50
    world.record_chat_success("alice", "bob", quality=1.0)
    rewards = engine.compute(world, {"alice": True, "bob": False})
    assert rewards["alice"] <= 0.0
    assert rewards["bob"] > 0.0

    world.tick = 55
    world.record_chat_success("alice", "bob", quality=1.0)
    rewards = engine.compute(world, {"alice": False, "bob": False})
    assert rewards["alice"] <= 0.0  # still within termination window

    world.tick = 70
    world.record_chat_success("alice", "bob", quality=1.0)
    rewards = engine.compute(world, {"alice": False, "bob": False})
    assert rewards["alice"] > 0.0


def test_chat_failure_penalty() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 1.0, "hygiene": 1.0, "energy": 1.0},
        wallet=1.0,
    )
    world.agents["bob"] = AgentSnapshot(
        agent_id="bob",
        position=(0, 1),
        needs={"hunger": 1.0, "hygiene": 1.0, "energy": 1.0},
        wallet=1.0,
    )
    world.record_chat_failure("alice", "bob")

    engine = RewardEngine(world.config)
    rewards = engine.compute(world, dict.fromkeys(world.agents, False))

    assert rewards["alice"] < world.config.rewards.survival_tick


def test_rivalry_avoidance_reward() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    data = config.model_dump()
    data["features"]["stages"]["social_rewards"] = "C2"
    config = SimulationConfig.model_validate(data)
    world = WorldState.from_config(config)
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 1.0, "hygiene": 1.0, "energy": 1.0},
        wallet=1.0,
    )
    world.record_relationship_guard_block(
        agent_id="alice",
        reason="queue_rival",
        object_id="stove_1",
    )

    engine = RewardEngine(config)
    rewards = engine.compute(world, dict.fromkeys(world.agents, False))

    assert rewards["alice"] > config.rewards.survival_tick


def test_episode_clip_enforced() -> None:
    world = _make_world(hunger=0.0)
    engine = RewardEngine(world.config)
    # Force large positive reward repeatedly to exceed clip_per_episode
    world.agents["alice"].needs["hunger"] = 1.0
    clip_episode = world.config.rewards.clip.clip_per_episode
    rewards = []
    for _ in range(10):
        rewards.append(engine.compute(world, terminated={})["alice"])
    assert sum(rewards) <= clip_episode
    # Reset episode totals on termination
    engine.compute(world, terminated={"alice": True})
    # After reset the agent should accrue rewards again (bounded by tick clip)
    next_reward = engine.compute(world, terminated={})["alice"]
    assert next_reward >= -world.config.rewards.clip.clip_per_tick


def test_wage_and_punctuality_bonus() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    context = {
        "needs": {"hunger": 1.0, "hygiene": 1.0, "energy": 1.0},
        "wallet": 0.0,
        "lateness_counter": 0,
        "on_shift": True,
        "attendance_ratio": 0.5,
        "wages_withheld": 0.0,
        "shift_state": "on_time",
        "last_action_id": "wait",
        "last_action_success": True,
        "last_action_duration": 1,
        "wages_paid": 0.1,
        "punctuality_bonus": 0.5,
    }
    snapshot = StubSnapshot(needs=context["needs"], wallet=context["wallet"])
    world = StubWorld(config, snapshot, context)

    engine = RewardEngine(config)
    reward = engine.compute(world, terminated={})["alice"]
    base = config.rewards.survival_tick  # needs all satisfied so only survival tick
    expected = (
        base
        + context["wages_paid"]
        + (config.rewards.punctuality_bonus * context["punctuality_bonus"])
    )
    assert reward == pytest.approx(expected)
    breakdown = engine.latest_reward_breakdown()["alice"]
    assert breakdown["wage"] == context["wages_paid"]
    assert breakdown["punctuality"] == pytest.approx(
        config.rewards.punctuality_bonus * context["punctuality_bonus"]
    )
    assert breakdown["total"] == pytest.approx(reward)


def test_terminal_penalty_applied_for_faint() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 1.0, "hygiene": 1.0, "energy": 1.0},
        wallet=0.0,
    )
    engine = RewardEngine(config)
    terminated = {"alice": True}
    reasons = {"alice": "faint"}
    reward = engine.compute(world, terminated, reasons)["alice"]
    raw_expected = config.rewards.survival_tick + config.rewards.faint_penalty
    clip = config.rewards.clip.clip_per_tick
    expected = max(min(raw_expected, clip), -clip)
    assert reward == pytest.approx(expected)
    breakdown = engine.latest_reward_breakdown()["alice"]
    assert breakdown["terminal_penalty"] == pytest.approx(config.rewards.faint_penalty)
    assert breakdown["clip_adjustment"] == pytest.approx(expected - raw_expected)



def test_terminal_penalty_applied_for_eviction() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 1.0, "hygiene": 1.0, "energy": 1.0},
        wallet=0.0,
    )
    engine = RewardEngine(config)
    terminated = {"alice": True}
    reasons = {"alice": "eviction"}
    reward = engine.compute(world, terminated, reasons)["alice"]
    raw_expected = config.rewards.survival_tick + config.rewards.eviction_penalty
    clip = config.rewards.clip.clip_per_tick
    expected = max(min(raw_expected, clip), -clip)
    assert reward == pytest.approx(expected)
    breakdown = engine.latest_reward_breakdown()["alice"]
    assert breakdown["terminal_penalty"] == pytest.approx(config.rewards.eviction_penalty)
    assert breakdown["clip_adjustment"] == pytest.approx(expected - raw_expected)


def test_positive_rewards_blocked_within_death_window() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    world = WorldState.from_config(config)
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 1.0, "hygiene": 1.0, "energy": 1.0},
        wallet=1.0,
    )
    engine = RewardEngine(config)
    baseline = engine.compute(world, {"alice": False})["alice"]
    assert baseline > 0

    window = int(config.rewards.clip.no_positive_within_death_ticks)
    engine.compute(world, {"alice": True})
    for offset in range(1, window):
        world.tick += 1
        reward = engine.compute(world, {"alice": False})["alice"]
        assert reward <= 0.0

    world.tick += window + 1
    reward = engine.compute(world, {"alice": False})["alice"]
    assert reward == pytest.approx(baseline)
