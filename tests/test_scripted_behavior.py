from __future__ import annotations

from pathlib import Path

import numpy as np

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.policy.behavior import AgentIntent, BehaviorController
from townlet.world.grid import AgentSnapshot


def test_scripted_behavior_determinism() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    loop.world.register_object(object_id="stove_1", object_type="stove")
    loop.world.agents["alice"] = AgentSnapshot(
        "alice",
        (0, 0),
        {"hunger": 0.3, "hygiene": 0.4, "energy": 0.5},
        wallet=1.0,
    )

    # Override behaviour with deterministic stub
    class StubBehavior(BehaviorController):
        def __init__(self) -> None:
            super().__init__(config)
            self._schedule = [
                AgentIntent(
                    kind="request",
                    object_id="stove_1",
                    affordance_id="cook",
                    blocked=False,
                ),
                AgentIntent(
                    kind="start",
                    object_id="stove_1",
                    affordance_id="cook",
                    blocked=False,
                ),
                AgentIntent(
                    kind="wait", object_id=None, affordance_id=None, blocked=False
                ),
            ]
            self._index = 0

        def decide(self, world, agent_id):  # type: ignore[override]
            intent = self._schedule[self._index % len(self._schedule)]
            self._index += 1
            return intent

    loop.policy.behavior = StubBehavior()

    actions_first = []
    for _ in range(5):
        loop.step()
        frames = [
            frame
            for frame in loop.policy.collect_trajectory(clear=True)
            if frame["agent_id"] == "alice"
        ]
        actions_first.extend(frame.get("action") for frame in frames)

    loop = SimulationLoop(config)
    loop.world.register_object(object_id="stove_1", object_type="stove")
    loop.world.agents["alice"] = AgentSnapshot(
        "alice",
        (0, 0),
        {"hunger": 0.3, "hygiene": 0.4, "energy": 0.5},
        wallet=1.0,
    )

    loop.policy.behavior = StubBehavior()

    actions_second = []
    for _ in range(5):
        loop.step()
        frames = [
            frame
            for frame in loop.policy.collect_trajectory(clear=True)
            if frame["agent_id"] == "alice"
        ]
        actions_second.extend(frame.get("action") for frame in frames)

    assert actions_first == actions_second
