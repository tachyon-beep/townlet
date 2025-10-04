"""Console service abstraction wrapping the bridge implementation."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from townlet.console.command import ConsoleCommandEnvelope, ConsoleCommandResult
from townlet.world.console_bridge import ConsoleBridge


class ConsoleService:
    """Façade providing a stable console API for world and telemetry layers."""

    def __init__(self, *, world: Any, history_limit: int, buffer_limit: int) -> None:
        self._bridge = ConsoleBridge(
            world=world,
            history_limit=history_limit,
            buffer_limit=buffer_limit,
        )

    # ------------------------------------------------------------------
    # Handler registration & lookup
    # ------------------------------------------------------------------
    def register_handler(
        self,
        name: str,
        handler: Callable[[ConsoleCommandEnvelope], ConsoleCommandResult],
        *,
        mode: str = "viewer",
        require_cmd_id: bool = False,
    ) -> None:
        self._bridge.register_handler(
            name,
            handler,
            mode=mode,
            require_cmd_id=require_cmd_id,
        )

    def handlers(self) -> Iterable[str]:
        return self._bridge.handlers().keys()

    # ------------------------------------------------------------------
    # Command execution / result management
    # ------------------------------------------------------------------
    def apply(self, operations: Iterable[Any]) -> None:
        self._bridge.apply(operations)

    def consume_results(self) -> list[ConsoleCommandResult]:
        return self._bridge.consume_results()

    def record_result(self, result: ConsoleCommandResult) -> None:
        self._bridge.record_result(result)

    def cached_result(self, cmd_id: str) -> ConsoleCommandResult | None:
        return self._bridge.cached_result(cmd_id)

    def clear(self) -> None:
        self._bridge.consume_results()

    @property
    def bridge(self) -> ConsoleBridge:
        """Expose the underlying bridge for legacy integrations/tests."""

        return self._bridge
