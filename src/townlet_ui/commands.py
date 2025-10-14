"""Helper utilities for dispatching console commands asynchronously."""

from __future__ import annotations

import logging
import queue
import threading
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from townlet.console.handlers import ConsoleCommand

logger = logging.getLogger(__name__)


class CommandQueueFullError(RuntimeError):
    """Raised when the executor queue exceeds the configured pending limit."""

    def __init__(self, pending: int, max_pending: int) -> None:  # pragma: no cover - trivial
        super().__init__(f"command queue saturated ({pending}/{max_pending})")
        self.pending = pending
        self.max_pending = max_pending


class ConsoleCommandExecutor:
    """Background dispatcher that forwards console commands via a router."""

    def __init__(
        self,
        router: Any,
        *,
        daemon: bool = True,
        max_pending: int | None = None,
        autostart: bool = True,
    ) -> None:
        if not hasattr(router, "dispatch"):
            raise TypeError("Router must expose a dispatch method")
        self._router = router
        queue_size = max_pending if max_pending and max_pending > 0 else 0
        self._queue: queue.Queue[ConsoleCommand | None] = queue.Queue(maxsize=queue_size)
        self._max_pending = max_pending if max_pending and max_pending > 0 else None
        self._daemon = daemon
        self._thread = threading.Thread(target=self._worker, daemon=daemon)
        self._thread_started = False
        self._autostart = autostart
        if autostart:
            self.start()

    def start(self) -> None:
        """Start the worker thread if it has not already begun."""

        if self._thread_started:
            return
        self._thread = threading.Thread(target=self._worker, daemon=self._daemon)
        self._thread.start()
        self._thread_started = True

    def pending_count(self) -> int:
        """Number of commands waiting in the executor queue."""

        return self._queue.qsize()

    def submit(self, command: ConsoleCommand) -> None:
        if not self._thread_started and self._autostart:
            self.start()
        try:
            self._queue.put_nowait(command)
        except queue.Full as exc:
            pending = self.pending_count()
            max_pending = self._max_pending or pending
            raise CommandQueueFullError(pending, max_pending) from exc

    def submit_payload(
        self, payload: Mapping[str, Any], *, enqueue: bool = True
    ) -> ConsoleCommand:
        """Validate and enqueue a structured palette payload.

        Returns the normalised `ConsoleCommand` for dry-run inspection by the
        caller so the UI can surface exactly what will be dispatched.
        """

        command = PaletteCommandRequest.from_payload(payload).to_console_command()
        if enqueue:
            self.submit(command)
        return command

    def shutdown(self, timeout: float | None = 1.0) -> None:
        if not self._thread_started:
            return
        try:
            self._queue.put_nowait(None)
        except queue.Full:  # pragma: no cover - defensive
            # If queue saturated, fall back to blocking insert to guarantee sentinel delivery.
            self._queue.put(None)
        self._thread.join(timeout=timeout)
        self._thread_started = False

    def _worker(self) -> None:
        while True:
            command = self._queue.get()
            if command is None:
                break
            try:
                self._router.dispatch(command)
            except Exception:  # pragma: no cover - log and continue
                logger.exception("Console command dispatch failed", exc_info=True)


@dataclass(frozen=True)
class PaletteCommandRequest:
    """Normalised representation of a palette command submission."""

    name: str
    args: tuple[Any, ...] = field(default_factory=tuple)
    kwargs: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> PaletteCommandRequest:
        """Validate an incoming payload from the palette overlay."""

        raw_name = payload.get("name")
        if not isinstance(raw_name, str) or not raw_name.strip():
            raise ValueError("palette payload requires non-empty 'name'")

        raw_args = payload.get("args", ())
        args: tuple[Any, ...]
        if raw_args is None:
            args = ()
        elif isinstance(raw_args, Sequence) and not isinstance(raw_args, (str, bytes, bytearray)):
            args = tuple(raw_args)
        else:
            raise ValueError("palette payload 'args' must be a sequence if provided")

        raw_kwargs = payload.get("kwargs", {})
        if raw_kwargs is None:
            kwargs = {}
        elif isinstance(raw_kwargs, Mapping):
            kwargs = dict(raw_kwargs)
        else:
            raise ValueError("palette payload 'kwargs' must be a mapping if provided")

        return cls(name=raw_name.strip(), args=args, kwargs=kwargs)

    def to_console_command(self) -> ConsoleCommand:
        """Convert into the ConsoleCommand used by the router."""

        return ConsoleCommand(name=self.name, args=self.args, kwargs=dict(self.kwargs))
