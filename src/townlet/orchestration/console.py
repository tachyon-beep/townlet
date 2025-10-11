"""Console routing service mapping commands to world actions/results."""

from __future__ import annotations

import logging
from collections import deque
from typing import Any, Callable, Mapping

from townlet.console.command import (
    ConsoleCommandEnvelope,
    ConsoleCommandError,
    ConsoleCommandResult,
)
from townlet.ports.telemetry import TelemetrySink
from townlet.ports.world import WorldRuntime

ConsoleHandler = Callable[[ConsoleCommandEnvelope], Mapping[str, Any]]

logger = logging.getLogger(__name__)


class ConsoleRouter:
    """Queue-based console router emitting structured results via telemetry."""

    def __init__(self, world: WorldRuntime, telemetry: TelemetrySink) -> None:
        self._world = world
        self._telemetry = telemetry
        self._queue: deque[ConsoleCommandEnvelope] = deque()
        self._handlers: dict[str, ConsoleHandler] = {
            "snapshot": self._handle_snapshot,
            "help": self._handle_help,
        }

    def register(self, command: str, handler: ConsoleHandler) -> None:
        self._handlers[command.strip().lower()] = handler

    def enqueue(self, command: object) -> None:
        envelope = self._coerce_envelope(command)
        self._queue.append(envelope)
        try:
            self._world.queue_console([envelope])
        except Exception:  # pragma: no cover - defensive
            logger.exception("Failed to queue console command on world runtime")

    def run_pending(self, *, tick: int | None = None) -> None:
        while self._queue:
            envelope = self._queue.popleft()
            result = self._execute(envelope, tick=tick)
            event_payload = {
                "command": envelope.raw
                if envelope.raw is not None
                else {
                    "name": envelope.name,
                    "args": list(envelope.args),
                    "kwargs": dict(envelope.kwargs),
                    "cmd_id": envelope.cmd_id,
                    "issuer": envelope.issuer,
                    "mode": envelope.mode,
                },
                "result": result.to_dict(),
            }
            self._telemetry.emit_event("console.result", event_payload)

    # ------------------------------------------------------------------
    # Default handlers
    # ------------------------------------------------------------------
    def _handle_snapshot(self, command: ConsoleCommandEnvelope) -> Mapping[str, Any]:
        _ = command
        return self._world.snapshot()

    def _handle_help(self, command: ConsoleCommandEnvelope) -> Mapping[str, Any]:  # pragma: no cover - deterministic
        _ = command
        return {
            "commands": sorted(self._handlers.keys()),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _coerce_envelope(self, payload: object) -> ConsoleCommandEnvelope:
        if isinstance(payload, ConsoleCommandEnvelope):
            return payload
        if isinstance(payload, str):
            command = payload.strip()
            if not command:
                raise ValueError("console command must not be empty")
            return ConsoleCommandEnvelope(name=command)
        try:
            return ConsoleCommandEnvelope.from_payload(payload)
        except ConsoleCommandError as exc:  # pragma: no cover - defensive
            raise ValueError(f"Invalid console command payload: {exc}") from exc

    def _execute(self, envelope: ConsoleCommandEnvelope, *, tick: int | None) -> ConsoleCommandResult:
        handler = self._handlers.get(envelope.name.strip().lower())
        if handler is None:
            return ConsoleCommandResult.from_error(
                envelope,
                code="unknown_command",
                message=f"unknown command '{envelope.name}'",
                tick=tick,
            )
        try:
            payload = handler(envelope)
        except Exception as exc:  # pragma: no cover - defensive
            return ConsoleCommandResult.from_error(
                envelope,
                code="handler_error",
                message=str(exc),
                tick=tick,
            )
        return ConsoleCommandResult.ok(envelope, payload, tick=tick)


__all__ = ["ConsoleRouter"]
