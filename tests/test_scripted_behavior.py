from pathlib import Path

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world.grid import AgentSnapshot


def test_scripted_behavior_consumes_meals() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    world = loop.world
    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.2, "hygiene": 0.5, "energy": 0.5},
        wallet=2.0,
    )
    world._assign_jobs_to_agents()  # type: ignore[attr-defined]

    initial_wallet = world.agents["alice"].wallet
    for _ in range(20):
        loop.step()

    assert world.agents["alice"].wallet < initial_wallet
    assert world.agents["alice"].inventory.get("meals_consumed", 0) > 0
