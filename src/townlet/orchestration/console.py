"""Console routing service mapping commands to world actions/results."""

from __future__ import annotations

import logging
from collections import deque
from collections.abc import Callable, Iterable, Mapping
from typing import Any

from townlet.console.command import (
    ConsoleCommandEnvelope,
    ConsoleCommandError,
    ConsoleCommandResult,
)
from townlet.dto.telemetry import TelemetryEventDTO, TelemetryMetadata
from townlet.dto.world import SimulationSnapshot
from townlet.ports.telemetry import TelemetrySink
from townlet.ports.world import WorldRuntime
from townlet.snapshots.state import SnapshotState

ConsoleHandler = Callable[[ConsoleCommandEnvelope], Any]

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

    def run_pending(
        self,
        results: Iterable[ConsoleCommandResult] | None = None,
        *,
        tick: int | None = None,
    ) -> None:
        """Emit console results for commands processed this tick.

        The world runtime is responsible for executing commands and returning
        ``ConsoleCommandResult`` entries. The router pairs those results with
        the original envelopes (to preserve raw payload metadata) and forwards
        them to telemetry. If the runtime does not supply a result for an
        enqueued command, the router falls back to its local handler registry.
        """

        pending = list(self._queue)
        self._queue.clear()
        result_iter = iter(results or ())

        def _next_result() -> ConsoleCommandResult | None:
            try:
                return next(result_iter)
            except StopIteration:
                return None

        for envelope in pending:
            runtime_result = _next_result()
            if runtime_result is None:
                runtime_result = self._execute(envelope, tick=tick)
            else:
                runtime_result = runtime_result.clone()
                if runtime_result.tick is None and tick is not None:
                    runtime_result.tick = tick
                if (
                    runtime_result.status == "error"
                    and envelope is not None
                    and envelope.name.strip().lower() in self._handlers
                ):
                    error_payload = runtime_result.error or {}
                    if str(error_payload.get("code")) in {"unknown_command", "unsupported"}:
                        runtime_result = self._execute(envelope, tick=tick)
            self._emit_event(envelope, runtime_result)

        # Emit any additional runtime results that were produced without a
        # matching queued command (should be rare, but guard defensively).
        for orphan in result_iter:
            payload = orphan.clone()
            if payload.tick is None and tick is not None:
                payload.tick = tick
            self._emit_event(None, payload)

    # ------------------------------------------------------------------
    # Default handlers
    # ------------------------------------------------------------------
    def _handle_snapshot(self, command: ConsoleCommandEnvelope) -> Mapping[str, Any]:
        """Handle snapshot command by returning snapshot as dict."""
        _ = command
        snapshot = self._world.snapshot()
        return snapshot.model_dump()

    def _handle_help(self, command: ConsoleCommandEnvelope) -> Mapping[str, Any]:  # pragma: no cover - deterministic
        _ = command
        return {
            "commands": sorted(self._handlers.keys()),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _emit_event(
        self,
        envelope: ConsoleCommandEnvelope | None,
        result: ConsoleCommandResult,
    ) -> None:
        command_payload: Mapping[str, Any]
        if envelope is None:
            command_payload = {
                "name": result.name,
                "args": [],
                "kwargs": {},
                "cmd_id": result.cmd_id,
                "issuer": result.issuer,
                "mode": "viewer",
            }
        elif envelope.raw is not None:
            command_payload = envelope.raw
        else:
            command_payload = {
                "name": envelope.name,
                "args": list(envelope.args),
                "kwargs": dict(envelope.kwargs),
                "cmd_id": envelope.cmd_id,
                "issuer": envelope.issuer,
                "mode": envelope.mode,
            }
        event_payload = {
            "command": command_payload,
            "result": result.to_dict(),
        }
        event = TelemetryEventDTO(
            event_type="console.result",
            tick=result.tick or 0,
            payload=event_payload,
            metadata=TelemetryMetadata(),
        )
        self._telemetry.emit_event(event)

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
        # Convert snapshot DTOs to dict for console result serialization
        if isinstance(payload, SimulationSnapshot):
            payload = payload.model_dump()
        elif isinstance(payload, SnapshotState):
            payload = payload.as_dict()
        return ConsoleCommandResult.ok(envelope, payload, tick=tick)


__all__ = ["ConsoleRouter"]
