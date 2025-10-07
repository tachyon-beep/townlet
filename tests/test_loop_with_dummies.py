from __future__ import annotations

from townlet.runtime.loop import SimulationLoop


def test_loop_runs_with_dummy_providers() -> None:
    loop = SimulationLoop(
        world_cfg={"provider": "dummy", "agent_count": 2},
        policy_cfg={"provider": "dummy", "action_name": "test"},
        telemetry_cfg={"provider": "dummy"},
    )
    loop.run(3, seed=123)
    snapshot = loop.world.snapshot()
    assert snapshot["tick"] == 3
