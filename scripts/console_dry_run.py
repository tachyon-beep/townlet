"""Employment console dry-run harness."""
from __future__ import annotations

from pathlib import Path
import tempfile

from townlet.config import load_config
from townlet.console.handlers import ConsoleCommand, create_console_router
from townlet.core.sim_loop import SimulationLoop
from townlet.snapshots import SnapshotManager
from townlet.snapshots.state import snapshot_from_world
from townlet.world.grid import AgentSnapshot


def main() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.employment.enforce_job_loop = True
    loop = SimulationLoop(config)
    world = loop.world
    world.agents.clear()
    # Seed deterministic agents
    world.agents["agent_0"] = AgentSnapshot(
        agent_id="agent_0",
        position=(0, 0),
        needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
        wallet=1.0,
    )
    world.agents["agent_1"] = AgentSnapshot(
        agent_id="agent_1",
        position=(1, 0),
        needs={"hunger": 0.4, "hygiene": 0.4, "energy": 0.4},
        wallet=1.0,
    )
    world._assign_jobs_to_agents()  # type: ignore[attr-defined]
    router = create_console_router(loop.telemetry, world, promotion=loop.promotion, config=config)

    # Advance the sim to populate telemetry snapshots.
    for _ in range(20):
        loop.step()

    print("=== telemetry_snapshot ===")
    print(router.dispatch(ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={})))

    # Demonstrate snapshot save/load to mirror ops workflow.
    with tempfile.TemporaryDirectory() as tmpdir:
        snapshot_dir = Path(tmpdir) / "snapshots"
        snapshot_path = loop.save_snapshot(snapshot_dir)
        print(f"=== snapshot saved to {snapshot_path}")

        restored = SimulationLoop(config)
        restored.load_snapshot(snapshot_path)
        restored_router = create_console_router(
            restored.telemetry,
            restored.world,
            config=config,
        )

        print("=== restored telemetry_snapshot ===")
        print(
            restored_router.dispatch(
                ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={})
            )
        )
        print(
            "Snapshot equality:",
            snapshot_from_world(config, restored.world).as_dict()
            == snapshot_from_world(config, loop.world).as_dict(),
        )

    print("=== employment_exit review (before) ===")
    print(router.dispatch(ConsoleCommand(name="employment_exit", args=("review",), kwargs={})))

    world._employment_enqueue_exit("agent_0", world.tick)

    print("=== employment_exit review (after enqueue) ===")
    print(router.dispatch(ConsoleCommand(name="employment_exit", args=("review",), kwargs={})))

    print("=== employment_exit approve ===")
    print(router.dispatch(ConsoleCommand(name="employment_exit", args=("approve", "agent_0"), kwargs={})))
    loop.lifecycle.evaluate(world, loop.tick)

    print("=== employment_exit defer ===")
    print(router.dispatch(ConsoleCommand(name="employment_exit", args=("defer", "agent_0"), kwargs={})))

    print("=== employment_status ===")
    print(router.dispatch(ConsoleCommand(name="employment_status", args=(), kwargs={})))


if __name__ == "__main__":
    main()
