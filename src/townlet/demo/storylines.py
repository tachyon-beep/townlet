"""Reusable demo storyline builders."""
from __future__ import annotations

import os
from collections.abc import Iterable
from typing import Callable, Dict, List

from .timeline import DemoTimeline, ScheduledCommand

StorylineBuilder = Callable[[], Iterable[ScheduledCommand]]


def _legacy_default() -> List[ScheduledCommand]:
    """Maintain historical default demo timeline for backward compatibility."""

    return [
        ScheduledCommand(
            tick=5,
            name="spawn_agent",
            kind="action",
            kwargs={"agent_id": "guest_1", "position": (2, 1), "wallet": 8.0},
        ),
        ScheduledCommand(
            tick=10,
            name="force_chat",
            kind="action",
            kwargs={"speaker": "guest_1", "listener": "demo_1", "quality": 0.95},
        ),
        ScheduledCommand(
            tick=20,
            name="perturbation_trigger",
            args=("price_spike",),
            kwargs={"magnitude": 1.4, "starts_in": 0},
        ),
    ]


def _demo_story_arc() -> List[ScheduledCommand]:
    """Narrative beats for the Milestone 1 demo story arc."""

    return [
        ScheduledCommand(
            tick=8,
            name="force_chat",
            kind="action",
            kwargs={"speaker": "avery", "listener": "kai", "quality": 0.9},
        ),
        ScheduledCommand(
            tick=18,
            name="set_need",
            kind="action",
            kwargs={"agent_id": "avery", "need": "energy", "value": 0.68},
        ),
        ScheduledCommand(
            tick=40,
            name="spawn_agent",
            kind="action",
            kwargs={
                "agent_id": "blair",
                "position": (13, 10),
                "wallet": 2.5,
                "needs": {"hunger": 0.55, "hygiene": 0.5, "energy": 0.48},
            },
        ),
        ScheduledCommand(
            tick=46,
            name="force_chat",
            kind="action",
            kwargs={"speaker": "blair", "listener": "avery", "quality": 0.6},
        ),
        ScheduledCommand(
            tick=60,
            name="perturbation_trigger",
            args=("price_spike",),
            kwargs={"magnitude": 1.55, "duration": 35, "targets": ["cafe"]},
        ),
        ScheduledCommand(
            tick=72,
            name="set_need",
            kind="action",
            kwargs={"agent_id": "blair", "need": "energy", "value": 0.35},
        ),
        ScheduledCommand(
            tick=88,
            name="force_chat",
            kind="action",
            kwargs={"speaker": "kai", "listener": "blair", "quality": 0.82},
        ),
        ScheduledCommand(
            tick=110,
            name="perturbation_trigger",
            args=("arrange_meet",),
            kwargs={"targets": ["avery", "blair"], "location": "cafe", "duration": 20},
        ),
        ScheduledCommand(
            tick=126,
            name="force_chat",
            kind="action",
            kwargs={"speaker": "avery", "listener": "blair", "quality": 0.93},
        ),
    ]


_STORYLINES: Dict[str, StorylineBuilder] = {
    "legacy": _legacy_default,
    "demo_story_arc": _demo_story_arc,
}


def available_storylines() -> tuple[str, ...]:
    """Return the registered storyline identifiers."""

    return tuple(sorted(_STORYLINES.keys()))


def resolve_storyline(storyline_id: str | None) -> StorylineBuilder:
    """Map a storyline identifier to its builder function."""

    if storyline_id is None:
        return _STORYLINES[default_storyline_id()]
    key = storyline_id if storyline_id in _STORYLINES else storyline_id.lower()
    if key not in _STORYLINES:
        raise KeyError(storyline_id)
    return _STORYLINES[key]


def build_storyline(storyline_id: str | None = None) -> DemoTimeline:
    """Construct a demo timeline for the requested storyline identifier."""

    builder = resolve_storyline(storyline_id)
    commands = list(builder())
    return DemoTimeline(commands)


def default_storyline_id() -> str:
    """Compute the default storyline identifier."""

    return os.getenv("TOWNLET_DEMO_STORYLINE", "legacy")


def default_timeline() -> DemoTimeline:
    """Return the default timeline using the current storyline selection."""

    return build_storyline(None)

