from __future__ import annotations

import pytest

from townlet.runtime.loop import SimulationLoop


@pytest.mark.slow
def test_loop_runs_with_default_adapters() -> None:
    loop = SimulationLoop(
        world_cfg={"provider": "default", "agents": ("alice", "bob")},
        policy_cfg={"provider": "scripted"},
        telemetry_cfg={"provider": "stdout"},
    )
    loop.run(2, seed=42)
    snapshot = loop.world.snapshot()
    assert snapshot["tick"] == 2
    assert set(snapshot["agents"]) == {"alice", "bob"}
