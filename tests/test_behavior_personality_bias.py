from __future__ import annotations

import json
from pathlib import Path
from statistics import mean

import pytest

from townlet.agents.models import Personality, PersonalityProfiles
from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.demo.runner import seed_demo_state
from townlet.policy.behavior import ScriptedBehavior
from townlet.world.grid import AgentSnapshot, WorldState


def _make_agent(
    agent_id: str,
    *,
    profile: str,
    position: tuple[int, int] = (0, 0),
    needs: dict[str, float] | None = None,
    personality_override: Personality | None = None,
) -> AgentSnapshot:
    profile_obj = PersonalityProfiles.get(profile)
    personality = personality_override or profile_obj.personality
    default_needs = {"hunger": 0.8, "hygiene": 0.8, "energy": 0.8}
    payload_needs = dict(default_needs)
    if needs:
        payload_needs.update(needs)
    snapshot = AgentSnapshot(
        agent_id=agent_id,
        position=position,
        needs=payload_needs,
        wallet=5.0,
        personality=personality,
        personality_profile=profile,
    )
    if personality_override is not None:
        snapshot.personality = personality_override
    return snapshot


def _run_demo_metrics(*, enable_flag: bool, ticks: int) -> dict[str, object]:
    config_path = Path("configs/scenarios/demo_story_arc.yaml")
    cfg = load_config(config_path)
    cfg.features.behavior.personality_profiles = enable_flag
    cfg.features.behavior.reward_multipliers = enable_flag
    telemetry_cfg = cfg.telemetry.model_copy(
        update={
            "transport": cfg.telemetry.transport.model_copy(
                update={"type": "file", "file_path": Path("/dev/null")}
            )
        }
    )
    cfg = cfg.model_copy(update={"telemetry": telemetry_cfg})
    loop = SimulationLoop(cfg)
    seed_demo_state(loop.world, telemetry=loop.telemetry, narration_level="summary")
    artifacts = loop.run_for_ticks(ticks, collect=True)
    rewards = [
        value
        for tick in artifacts
        for value in (tick.rewards.values() if isinstance(tick.rewards, dict) else [])
    ]
    needs = {need: [] for need in ("hunger", "hygiene", "energy")}
    for snapshot in loop.world.agents.values():
        for need in needs:
            needs[need].append(snapshot.needs.get(need, 0.0))
    needs_mean = {need: mean(values) if values else 0.0 for need, values in needs.items()}
    reward_mean = sum(rewards) / len(rewards) if rewards else 0.0
    return {
        "config": str(config_path),
        "ticks": loop.tick,
        "agents": sorted(loop.world.agents.keys()),
        "needs_mean": needs_mean,
        "reward_mean_per_tick": reward_mean,
    }


def test_chat_bias_respects_feature_flag() -> None:
    base_config = load_config(Path("configs/examples/poc_hybrid.yaml"))

    disabled_cfg = base_config.model_copy(deep=True)
    disabled_cfg.features.behavior.personality_profiles = False
    disabled_cfg.features.behavior.reward_multipliers = False
    disabled_world = WorldState.from_config(disabled_cfg)
    behavior_disabled = ScriptedBehavior(disabled_cfg)

    enabled_cfg = base_config.model_copy(deep=True)
    enabled_cfg.features.behavior.personality_profiles = True
    enabled_cfg.features.behavior.reward_multipliers = True
    enabled_world = WorldState.from_config(enabled_cfg)
    behavior_enabled = ScriptedBehavior(enabled_cfg)

    # Agent extroversion slightly below the default threshold (0.2).
    extroverted = Personality(extroversion=0.16, forgiveness=0.0, ambition=0.0)
    for world in (disabled_world, enabled_world):
        world.agents.clear()
        world.agents["listener"] = _make_agent("listener", profile="balanced", position=(0, 0))
        world.agents["talker"] = _make_agent(
            "talker",
            profile="socialite",
            position=(0, 0),
            personality_override=extroverted,
        )

    disabled_intent = behavior_disabled.decide(disabled_world, "talker")
    enabled_intent = behavior_enabled.decide(enabled_world, "talker")

    assert disabled_intent.kind == "wait"
    assert enabled_intent.kind == "chat"
    assert enabled_intent.target_agent == "listener"


def test_conflict_tolerance_relaxes_queue_guard() -> None:
    base_config = load_config(Path("configs/examples/poc_hybrid.yaml"))

    disabled_cfg = base_config.model_copy(deep=True)
    disabled_cfg.features.behavior.personality_profiles = False
    disabled_cfg.features.behavior.reward_multipliers = False
    disabled_world = WorldState.from_config(disabled_cfg)
    behavior_disabled = ScriptedBehavior(disabled_cfg)

    enabled_cfg = base_config.model_copy(deep=True)
    enabled_cfg.features.behavior.personality_profiles = True
    enabled_cfg.features.behavior.reward_multipliers = True
    enabled_world = WorldState.from_config(enabled_cfg)
    behavior_enabled = ScriptedBehavior(enabled_cfg)

    def setup(world: WorldState) -> None:
        world.agents.clear()
        world.register_object(object_id="fridge_1", object_type="fridge", position=(0, 0))
        world.agents["rival"] = _make_agent("rival", profile="balanced", position=(0, 0))
        world.agents["stoic"] = _make_agent("stoic", profile="stoic", position=(0, 0))
        ledger = world._get_rivalry_ledger("stoic")  
        for _ in range(6):
            ledger.apply_conflict("rival")
        world.queue_manager.request_access("fridge_1", "rival", tick=0)

    setup(disabled_world)
    setup(enabled_world)

    assert behavior_disabled._rivals_in_queue(disabled_world, "stoic", "fridge_1") is True
    assert behavior_enabled._rivals_in_queue(enabled_world, "stoic", "fridge_1") is False


def test_need_threshold_respects_multipliers() -> None:
    base_config = load_config(Path("configs/examples/poc_hybrid.yaml"))

    def build_world(*, enable: bool) -> tuple[WorldState, ScriptedBehavior]:
        cfg = base_config.model_copy(deep=True)
        cfg.features.behavior.personality_profiles = enable
        cfg.features.behavior.reward_multipliers = enable
        world = WorldState.from_config(cfg)
        behavior = ScriptedBehavior(cfg)
        world.register_object(object_id="bed_1", object_type="bed", position=(0, 0))
        world.agents.clear()
        world.agents["industrious"] = _make_agent(
            "industrious",
            profile="industrious",
            position=(0, 0),
            needs={"energy": 0.37, "hunger": 0.8, "hygiene": 0.8},
        )
        return world, behavior

    world_disabled, behavior_disabled = build_world(enable=False)
    world_enabled, behavior_enabled = build_world(enable=True)

    intent_disabled = behavior_disabled.decide(world_disabled, "industrious")
    intent_enabled = behavior_enabled.decide(world_enabled, "industrious")

    assert intent_disabled.kind == "request"
    assert intent_disabled.object_id == "bed_1"
    assert intent_enabled.kind != "request"
def test_personality_metrics_align_with_baseline_when_disabled() -> None:
    baseline_path = Path("tests/data/baselines/demo_story_arc_personality_baseline.json")
    expected = json.loads(baseline_path.read_text(encoding="utf-8"))
    metrics = _run_demo_metrics(enable_flag=False, ticks=int(expected["ticks"]))

    assert metrics["agents"] == expected["agents"]
    for need, value in expected["needs_mean"].items():
        assert metrics["needs_mean"][need] == pytest.approx(value, rel=1e-3, abs=1e-3)
    assert metrics["reward_mean_per_tick"] == pytest.approx(
        expected["reward_mean_per_tick"], rel=1e-3, abs=1e-3
    )


def test_personality_metrics_with_bias_match_fixture() -> None:
    baseline_path = Path("tests/data/baselines/demo_story_arc_personality_feature_on.json")
    expected = json.loads(baseline_path.read_text(encoding="utf-8"))
    metrics = _run_demo_metrics(enable_flag=True, ticks=int(expected["ticks"]))

    assert metrics["agents"] == expected["agents"]
    for need, value in expected["needs_mean"].items():
        assert metrics["needs_mean"][need] == pytest.approx(value, rel=1e-3, abs=1e-3)
    assert metrics["reward_mean_per_tick"] == pytest.approx(
        expected["reward_mean_per_tick"], rel=1e-3, abs=1e-3
    )
