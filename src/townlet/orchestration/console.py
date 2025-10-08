"""Console routing service mapping commands to world actions/results."""

from __future__ import annotations

from collections import deque
from typing import Any, Callable, Mapping

from townlet.ports.telemetry import TelemetrySink
from townlet.ports.world import WorldRuntime


ConsoleHandler = Callable[[str], Mapping[str, Any]]


class ConsoleRouter:
    """Queue-based console router emitting structured results via telemetry."""

    def __init__(self, world: WorldRuntime, telemetry: TelemetrySink) -> None:
        self._world = world
        self._telemetry = telemetry
        self._queue: deque[str] = deque()
        self._handlers: dict[str, ConsoleHandler] = {
            "snapshot": self._handle_snapshot,
            "help": self._handle_help,
        }

    def register(self, command: str, handler: ConsoleHandler) -> None:
        self._handlers[command.strip().lower()] = handler

    def enqueue(self, command: str) -> None:
        self._queue.append(command)

    def run_pending(self) -> None:
        while self._queue:
            raw = self._queue.popleft()
            result = self._dispatch(raw)
            self._telemetry.emit_event(
                "console.result",
                {
                    "command": raw,
                    "result": result,
                },
            )

    # ------------------------------------------------------------------
    # Default handlers
    # ------------------------------------------------------------------
    def _handle_snapshot(self, command: str) -> Mapping[str, Any]:
        _ = command
        return self._world.snapshot()

    def _handle_help(self, command: str) -> Mapping[str, Any]:  # pragma: no cover - deterministic
        _ = command
        return {
            "commands": sorted(self._handlers.keys()),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _dispatch(self, command: str) -> Mapping[str, Any]:
        name = command.strip().lower().split()[0] if command.strip() else ""
        handler = self._handlers.get(name)
        if handler is None:
            return {
                "ok": False,
                "error": f"unknown command '{name}'",
            }
        try:
            response = handler(command)
        except Exception as exc:  # pragma: no cover - defensive
            return {
                "ok": False,
                "error": str(exc),
            }
        return {"ok": True, **response}


__all__ = ["ConsoleRouter"]
