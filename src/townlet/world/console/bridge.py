"""Console command bridge for world runtime."""

from __future__ import annotations

import logging
from collections import OrderedDict, deque
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from townlet.console.command import (
    ConsoleCommandEnvelope,
    ConsoleCommandError,
    ConsoleCommandResult,
)

logger = logging.getLogger(__name__)


@dataclass
class ConsoleHandlerEntry:
    handler: Callable[[ConsoleCommandEnvelope], ConsoleCommandResult]
    mode: str
    require_cmd_id: bool


class ConsoleBridge:
    """Maintains console handlers and result history for a world instance."""

    def __init__(
        self,
        *,
        world: Any,
        history_limit: int,
        buffer_limit: int,
    ) -> None:
        self._world = world
        self._handlers: dict[str, ConsoleHandlerEntry] = {}
        self._cmd_history: OrderedDict[str, ConsoleCommandResult] = OrderedDict()
        self._result_buffer: deque[ConsoleCommandResult] = deque(maxlen=buffer_limit)
        self._history_limit = history_limit

    def register_handler(
        self,
        name: str,
        handler: Callable[[ConsoleCommandEnvelope], ConsoleCommandResult],
        *,
        mode: str = "viewer",
        require_cmd_id: bool = False,
    ) -> None:
        self._handlers[name] = ConsoleHandlerEntry(
            handler=handler,
            mode=mode,
            require_cmd_id=require_cmd_id,
        )

    def handlers(self) -> Mapping[str, ConsoleHandlerEntry]:
        return self._handlers

    def record_result(self, result: ConsoleCommandResult) -> None:
        if result.cmd_id:
            self._cmd_history[result.cmd_id] = result.clone()
            while len(self._cmd_history) > self._history_limit:
                self._cmd_history.popitem(last=False)
        self._result_buffer.append(result)

    def consume_results(self) -> list[ConsoleCommandResult]:
        results = list(self._result_buffer)
        self._result_buffer.clear()
        return results

    def cached_result(self, cmd_id: str) -> ConsoleCommandResult | None:
        cached = self._cmd_history.get(cmd_id)
        if cached is None:
            return None
        clone = cached.clone()
        clone.tick = self._world.tick
        return clone

    def apply(self, operations: Iterable[Any]) -> None:
        for operation in operations:
            try:
                envelope = ConsoleCommandEnvelope.from_payload(operation)
            except ConsoleCommandError as exc:
                fallback = ConsoleCommandEnvelope(
                    name=str(getattr(operation, "name", "unknown") or "unknown"),
                    args=[],
                    kwargs={},
                    cmd_id=getattr(operation, "cmd_id", None)
                    if isinstance(getattr(operation, "cmd_id", None), str)
                    else None,
                    issuer=None,
                )
                result = ConsoleCommandResult.from_error(
                    fallback,
                    exc.code,
                    exc.message,
                    details=exc.details or {},
                    tick=self._world.tick,
                )
                logger.warning("Rejected console command: %s", exc)
                self.record_result(result)
                continue
            except Exception:  # pragma: no cover - defensive guard
                logger.exception("Failed to normalise console command payload: %r", operation)
                continue

            entry = self._handlers.get(envelope.name)
            if entry is None:
                result = ConsoleCommandResult.from_error(
                    envelope,
                    "unsupported",
                    f"Unknown console command '{envelope.name}'",
                    tick=self._world.tick,
                )
                self.record_result(result)
                continue

            if entry.mode == "admin" and envelope.mode != "admin":
                result = ConsoleCommandResult.from_error(
                    envelope,
                    "forbidden",
                    "Command requires admin mode",
                    tick=self._world.tick,
                )
                self.record_result(result)
                continue

            if entry.require_cmd_id and not envelope.cmd_id:
                result = ConsoleCommandResult.from_error(
                    envelope,
                    "usage",
                    "Command requires cmd_id for idempotency",
                    tick=self._world.tick,
                )
                self.record_result(result)
                continue

            if envelope.cmd_id:
                cached = self.cached_result(envelope.cmd_id)
                if cached is not None:
                    self.record_result(cached)
                    continue

            try:
                result = entry.handler(envelope)
            except ConsoleCommandError as exc:
                result = ConsoleCommandResult.from_error(
                    envelope,
                    exc.code,
                    exc.message,
                    details=exc.details or {},
                    tick=self._world.tick,
                )
            except Exception as exc:  # pragma: no cover - defensive
                logger.exception("Console command '%s' failed", envelope.name)
                result = ConsoleCommandResult.from_error(
                    envelope,
                    "internal",
                    "Internal error while executing command",
                    details={"exception": str(exc)},
                    tick=self._world.tick,
                )

            if result.tick is None:
                result.tick = self._world.tick
            self.record_result(result)
