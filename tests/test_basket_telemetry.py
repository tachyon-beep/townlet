from pathlib import Path

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.world.grid import AgentSnapshot


def test_basket_cost_in_telemetry_snapshot() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    world = loop.world
    publisher = loop.telemetry

    world.agents["alice"] = AgentSnapshot(
        agent_id="alice",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    world._assign_jobs_to_agents()  # type: ignore[attr-defined]

    for _ in range(5):
        loop.step()

    snapshot = publisher.latest_job_snapshot()
    assert (
        snapshot["alice"]["basket_cost"]
        == config.economy["meal_cost"]
        + config.economy["cook_energy_cost"]
        + config.economy["cook_hygiene_cost"]
        + config.economy["ingredients_cost"]
    )
