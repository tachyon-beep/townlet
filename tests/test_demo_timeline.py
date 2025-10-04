from pathlib import Path

import pytest

from townlet.config import load_config
import json

from townlet.core.sim_loop import SimulationLoop
from townlet.demo.runner import DemoScheduler, default_timeline, seed_demo_state
from townlet.demo.timeline import load_timeline
from townlet.console.handlers import create_console_router
from townlet_ui.commands import ConsoleCommandExecutor


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



def test_default_timeline_deterministic() -> None:
    timeline = default_timeline()
    snapshot = [
        (item.tick, item.name, item.kind, tuple(item.args), dict(item.kwargs or {}))
        for item in timeline.upcoming()
    ]
    assert snapshot == [
        (5, "spawn_agent", "action", (), {"agent_id": "guest_1", "position": (2, 1), "wallet": 8.0}),
        (10, "force_chat", "action", (), {"speaker": "guest_1", "listener": "demo_1", "quality": 0.95}),
        (20, "perturbation_trigger", "console", ("price_spike",), {"magnitude": 1.4, "starts_in": 0}),
    ]


def test_seed_demo_state_emits_opening_narration() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    loop = SimulationLoop(config)

    seed_demo_state(loop.world, telemetry=loop.telemetry, narration_level="summary")

    narrations = loop.telemetry.latest_narrations()
    assert narrations, "Expected opening narration to be queued"
    entry = next((item for item in narrations if item.get("category") == "demo_story"), None)
    assert entry is not None
    assert entry.get("data", {}).get("stage") == "warmup"


def test_demo_story_arc_narrations_match_golden() -> None:
    config = load_config(Path("configs/scenarios/demo_story_arc.yaml"))
    loop = SimulationLoop(config)
    seed_demo_state(loop.world, telemetry=loop.telemetry, narration_level="summary")

    router = create_console_router(
        loop.telemetry,
        loop.world,
        loop.perturbations,
        promotion=loop.promotion,
        policy=loop.policy,
        config=loop.config,
        lifecycle=loop.lifecycle,
        mode="viewer",
    )
    executor = ConsoleCommandExecutor(router)
    try:
        timeline = load_timeline(Path("configs/scenarios/timelines/demo_story_arc.yaml"))
        scheduler = DemoScheduler(timeline=timeline)

        records: list[dict[str, object]] = []

        def collect() -> None:
            for entry in loop.telemetry.latest_narrations():
                record: dict[str, object] = {
                    "tick": int(loop.tick),
                    "category": entry.get("category"),
                    "message": entry.get("message"),
                    "priority": bool(entry.get("priority", False)),
                }
                data = entry.get("data")
                if isinstance(data, dict):
                    record["data"] = data
                records.append(record)

        collect()
        for _ in range(150):
            loop.step()
            collect()
            scheduler.on_tick(loop, executor, loop.tick)
    finally:
        executor.shutdown()

    fixture_path = Path("tests/data/demo_story_arc_narrations.json")
    golden = json.loads(fixture_path.read_text(encoding="utf-8"))
    assert records == golden
