from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, List

import json

import yaml


@dataclass(frozen=True)
class ScheduledCommand:
    """Represents an item scheduled for a specific simulation tick."""

    tick: int
    name: str
    kind: str = "console"
    args: tuple[Any, ...] = ()
    kwargs: dict[str, Any] | None = None

    def payload(self) -> dict[str, Any]:
        if self.kind != "console":
            raise ValueError("Only console commands expose payloads")
        return {
            "name": self.name,
            "args": list(self.args),
            "kwargs": dict(self.kwargs or {}),
        }


class DemoTimeline:
    """Ordered queue of scheduled console commands for demos."""

    def __init__(self, commands: Iterable[ScheduledCommand]) -> None:
        self._commands: List[ScheduledCommand] = sorted(commands, key=lambda item: item.tick)
        self._index = 0

    def __bool__(self) -> bool:  # pragma: no cover - convenience
        return self.remaining > 0

    @property
    def remaining(self) -> int:
        return len(self._commands) - self._index

    def pop_due(self, current_tick: int) -> list[ScheduledCommand]:
        due: list[ScheduledCommand] = []
        while self._index < len(self._commands) and self._commands[self._index].tick <= current_tick:
            due.append(self._commands[self._index])
            self._index += 1
        return due

    def upcoming(self) -> Iterator[ScheduledCommand]:
        yield from self._commands[self._index :]

    def next_tick(self) -> int | None:
        if self._index < len(self._commands):
            return self._commands[self._index].tick
        return None


def load_timeline(path: Path) -> DemoTimeline:
    """Load a demo timeline from YAML or JSON configuration."""

    if not path.exists():
        raise FileNotFoundError(path)
    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        return DemoTimeline([])
    if path.suffix.lower() == ".json":
        payload = json.loads(raw)
    else:
        payload = yaml.safe_load(raw)
    if payload is None:
        return DemoTimeline([])
    if isinstance(payload, dict) and "timeline" in payload:
        entries = payload.get("timeline")
    else:
        entries = payload
    if not isinstance(entries, list):
        raise ValueError("Timeline payload must be a list")
    commands: list[ScheduledCommand] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Timeline entries must be mappings")
        tick = entry.get("tick")
        name = entry.get("command") or entry.get("name") or entry.get("action")
        if not isinstance(tick, int) or tick < 0:
            raise ValueError(f"Invalid tick value: {tick}")
        if not isinstance(name, str) or not name:
            raise ValueError("Timeline entry missing command/action name")
        kind = entry.get("kind") or ("action" if "action" in entry else "console")
        if kind not in {"console", "action", "narration"}:
            raise ValueError(f"Unsupported timeline kind: {kind}")
        raw_args = entry.get("args", ())
        if isinstance(raw_args, (list, tuple)):
            args = tuple(raw_args)
        elif raw_args in (None, {}):
            args = ()
        else:
            raise ValueError(f"Invalid args for entry {name!r}")
        raw_kwargs = entry.get("kwargs", {})
        if raw_kwargs is None:
            kwargs = {}
        elif isinstance(raw_kwargs, dict):
            kwargs = dict(raw_kwargs)
        else:
            raise ValueError(f"Invalid kwargs for entry {name!r}")
        commands.append(
            ScheduledCommand(
                tick=tick,
                name=name,
                kind=kind,
                args=args,
                kwargs=kwargs,
            )
        )
    return DemoTimeline(commands)
