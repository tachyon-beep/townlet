from __future__ import annotations

from pathlib import Path

from townlet.config import load_config
from townlet.demo.storylines import available_storylines, build_storyline
from townlet.demo.timeline import load_timeline


def _normalise(value):
    if isinstance(value, list):
        return tuple(_normalise(entry) for entry in value)
    if isinstance(value, dict):
        return {key: _normalise(val) for key, val in value.items()}
    return value


def _snapshot(timeline) -> list[tuple[int, str, str, tuple, dict]]:
    return [
        (
            item.tick,
            item.name,
            item.kind,
            tuple(item.args),
            dict(_normalise(item.kwargs or {})),
        )
        for item in timeline.upcoming()
    ]


def test_demo_story_arc_builder_registers() -> None:
    assert "demo_story_arc" in available_storylines()


def test_demo_story_arc_builder_matches_expected_schedule() -> None:
    timeline = build_storyline("demo_story_arc")
    assert _snapshot(timeline) == [
        (8, "force_chat", "action", (), {"speaker": "avery", "listener": "kai", "quality": 0.9}),
        (18, "set_need", "action", (), {"agent_id": "avery", "need": "energy", "value": 0.68}),
        (
            40,
            "spawn_agent",
            "action",
            (),
            {
                "agent_id": "blair",
                "position": (13, 10),
                "wallet": 2.5,
                "needs": {"hunger": 0.55, "hygiene": 0.5, "energy": 0.48},
            },
        ),
        (46, "force_chat", "action", (), {"speaker": "blair", "listener": "avery", "quality": 0.6}),
        (
            60,
            "perturbation_trigger",
            "console",
            ("price_spike",),
            {"magnitude": 1.55, "duration": 35, "targets": ("cafe",)},
        ),
        (72, "set_need", "action", (), {"agent_id": "blair", "need": "energy", "value": 0.35}),
        (88, "force_chat", "action", (), {"speaker": "kai", "listener": "blair", "quality": 0.82}),
        (
            110,
            "perturbation_trigger",
            "console",
            ("arrange_meet",),
            {"targets": ("avery", "blair"), "location": "cafe", "duration": 20},
        ),
        (126, "force_chat", "action", (), {"speaker": "avery", "listener": "blair", "quality": 0.93}),
    ]


def test_demo_story_arc_timeline_files_match_builder(tmp_path: Path) -> None:
    builder_snapshot = _snapshot(build_storyline("demo_story_arc"))

    yaml_path = Path("configs/scenarios/timelines/demo_story_arc.yaml")
    yaml_timeline = load_timeline(yaml_path)
    assert _snapshot(yaml_timeline) == builder_snapshot

    json_path = Path("configs/scenarios/timelines/demo_story_arc.json")
    json_timeline = load_timeline(json_path)
    assert _snapshot(json_timeline) == builder_snapshot


def test_demo_story_arc_config_tick_budget() -> None:
    config = load_config(Path("configs/scenarios/demo_story_arc.yaml"))
    assert getattr(config, "seed", None) == 4242
    meta = getattr(config, "meta", {})
    assert meta.get("tick_budget") == 150
    scenario = getattr(config, "scenario", {})
    ticks = scenario.get("ticks") if isinstance(scenario, dict) else getattr(scenario, "ticks", None)
    assert ticks == 150
