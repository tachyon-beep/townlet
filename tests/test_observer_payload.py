from pathlib import Path

import pytest

from townlet.agents.models import PersonalityProfiles
from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.telemetry.publisher import TelemetryPublisher
from townlet.world.grid import AgentSnapshot


def make_loop() -> SimulationLoop:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    world = loop.world
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    world.assign_jobs_to_agents()  
    return loop


def test_observer_payload_contains_job_and_economy() -> None:
    loop = make_loop()
    publisher: TelemetryPublisher = loop.telemetry
    for _ in range(5):
        loop.step()

    job_snapshot = publisher.latest_job_snapshot()
    economy_snapshot = publisher.latest_economy_snapshot()
    assert "alice" in job_snapshot
    assert "wages_earned" in job_snapshot["alice"]["inventory"]
    assert economy_snapshot
    assert "settings" in economy_snapshot
    assert "utility_snapshot" in economy_snapshot


def test_planning_payload_consistency() -> None:
    loop = make_loop()
    publisher: TelemetryPublisher = loop.telemetry
    for _ in range(5):
        loop.step()
    job_snapshot = publisher.latest_job_snapshot()
    economy_snapshot = publisher.latest_economy_snapshot()

    for agent_info in job_snapshot.values():
        assert isinstance(agent_info.get("wallet"), float)
        assert isinstance(agent_info.get("lateness_counter"), int)
        inventory = agent_info.get("inventory", {})
        assert isinstance(inventory.get("wages_earned"), (float, int))

    utility_snapshot = economy_snapshot.get("utility_snapshot", {})
    for status in utility_snapshot.values():
        assert isinstance(status, bool)


def test_personality_snapshot_respects_flag() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.features.observations.personality_channels = False
    loop = SimulationLoop(config)
    world = loop.world
    world.agents.clear()
    world.agents["avery"] = AgentSnapshot(
        agent_id="avery",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.6, "energy": 0.7},
        wallet=3.0,
    )
    loop.step()
    publisher: TelemetryPublisher = loop.telemetry
    assert publisher.latest_personality_snapshot() == {}

    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.features.observations.personality_channels = True
    loop = SimulationLoop(config)
    world = loop.world
    world.agents.clear()
    world.agents["avery"] = AgentSnapshot(
        agent_id="avery",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.6, "energy": 0.7},
        wallet=3.0,
        personality_profile="socialite",
        personality=PersonalityProfiles.get("socialite").personality,
    )
    loop.step()
    publisher = loop.telemetry
    snapshot = publisher.latest_personality_snapshot()
    assert "avery" in snapshot
    entry = snapshot["avery"]
    assert entry["profile"] == "socialite"
    assert entry["traits"]["extroversion"] == pytest.approx(0.6)
    assert "multipliers" in entry


def test_export_state_includes_personalities_when_available() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.features.observations.personality_channels = True
    loop = SimulationLoop(config)
    world = loop.world
    world.agents.clear()
    world.agents["avery"] = AgentSnapshot(
        agent_id="avery",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.6, "energy": 0.7},
        wallet=3.0,
        personality_profile="socialite",
        personality=PersonalityProfiles.get("socialite").personality,
    )
    loop.step()
    state = loop.telemetry.export_state()
    personalities = state.get("personalities")
    assert personalities is not None
    assert "avery" in personalities
