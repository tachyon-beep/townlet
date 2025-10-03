from pathlib import Path

import pytest

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop
from townlet.demo.runner import DemoScheduler, default_timeline, seed_demo_state
from townlet.demo.timeline import load_timeline


def test_load_timeline_from_yaml(tmp_path: Path) -> None:
    path = tmp_path / "timeline.yml"
    path.write_text(
        """
        timeline:
          - tick: 2
            command: social_events
            kwargs:
              limit: 5
          - tick: 4
            action: spawn_agent
            kwargs:
              agent_id: newcomer
        """,
        encoding="utf-8",
    )
    timeline = load_timeline(path)
    due = timeline.pop_due(2)
    assert len(due) == 1
    assert due[0].name == "social_events"
    assert due[0].kind == "console"
    future = timeline.pop_due(4)
    assert future[0].name == "spawn_agent"
    assert future[0].kind == "action"


class StubExecutor:
    def __init__(self) -> None:
        self.commands: list[dict[str, object]] = []

    def submit_payload(self, payload: dict[str, object], *, enqueue: bool = True) -> dict[str, object]:
        self.commands.append(payload)
        return payload

    def pending_count(self) -> int:
        return len(self.commands)


def test_demo_scheduler_actions_update_world(tmp_path: Path) -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)
    seed_demo_state(loop.world)
    timeline = default_timeline()
    scheduler = DemoScheduler(timeline=timeline)
    executor = StubExecutor()

    # simulate ticks
    for tick in range(1, 25):
        scheduler.on_tick(loop, executor, tick)

    # spawn action should have added guest_1
    assert "guest_1" in loop.world.agents
    # force_chat should have increased trust
    speaker = "guest_1"
    listener = "demo_1"
    ledger = loop.world._relationship_ledgers.get(speaker)
    assert ledger is not None
    tie = ledger.tie_for(listener)
    assert tie is not None and tie.trust > 0
    # console command should have been queued
    assert any(cmd["name"] == "perturbation_trigger" for cmd in executor.commands)
