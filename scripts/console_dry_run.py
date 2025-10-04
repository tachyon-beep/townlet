"""Employment console dry-run harness."""
from __future__ import annotations

from pathlib import Path
import tempfile

from townlet.config import (
    ConsoleAuthConfig,
    ConsoleAuthTokenConfig,
    load_config,
)
from townlet.console.handlers import ConsoleCommand, create_console_router
from townlet.core.sim_loop import SimulationLoop
from townlet.snapshots import SnapshotManager
from townlet.snapshots.state import snapshot_from_world
from townlet.world.grid import AgentSnapshot


def main() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config.employment.enforce_job_loop = True
    config = config.model_copy(
        update={
            "console_auth": ConsoleAuthConfig(
                enabled=True,
                require_auth_for_viewer=False,
                tokens=[
                    ConsoleAuthTokenConfig(token="viewer-token", role="viewer"),
                    ConsoleAuthTokenConfig(token="admin-token", role="admin"),
                ],
            )
        }
    )
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
    world.employment.assign_jobs_to_agents(world)
    router = create_console_router(
        loop.telemetry,
        world,
        promotion=loop.promotion,
        policy=loop.policy,
        lifecycle=loop.lifecycle,
        config=config,
    )

    # Advance the sim to populate telemetry snapshots.
    for _ in range(20):
        loop.step()

    print("=== telemetry_snapshot ===")
    print(router.dispatch(ConsoleCommand(name="telemetry_snapshot", args=(), kwargs={})))

    print("=== affordance_status ===")
    print(router.dispatch(ConsoleCommand(name="affordance_status", args=(), kwargs={})))

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
            policy=restored.policy,
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

    world.employment.enqueue_exit(world, "agent_0", world.tick)

    print("=== employment_exit review (after enqueue) ===")
    print(router.dispatch(ConsoleCommand(name="employment_exit", args=("review",), kwargs={})))

    print("=== employment_exit approve ===")
    print(router.dispatch(ConsoleCommand(name="employment_exit", args=("approve", "agent_0"), kwargs={})))
    loop.lifecycle.evaluate(world, loop.tick)

    print("=== employment_exit defer ===")
    print(router.dispatch(ConsoleCommand(name="employment_exit", args=("defer", "agent_0"), kwargs={})))

    print("=== employment_status ===")
    print(router.dispatch(ConsoleCommand(name="employment_status", args=(), kwargs={})))

    print("=== latest console_results ===")
    print(loop.telemetry.latest_console_results())

    audit_path = Path("logs/console/commands.jsonl")
    if audit_path.exists():
        print("=== console audit tail ===")
        print(audit_path.read_text().splitlines()[-1])
    else:
        print("(console audit log not found; create logs/console directory)")

    print("=== force_chat agent_0->agent_1 ===")
    loop.telemetry.queue_console_command(
        {
            "name": "force_chat",
            "mode": "admin",
            "cmd_id": "chat-demo",
            "auth": {"token": "admin-token"},
            "kwargs": {
                "payload": {
                    "speaker": "agent_0",
                    "listener": "agent_1",
                    "quality": 0.75,
                }
            },
        }
    )
    loop.step()
    print(loop.telemetry.latest_console_results()[-1])


if __name__ == "__main__":
    main()
