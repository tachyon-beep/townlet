"""Helper utilities for dispatching console commands asynchronously."""

from __future__ import annotations

import logging
import queue
import threading
from typing import Any

from townlet.console.handlers import ConsoleCommand

logger = logging.getLogger(__name__)


class ConsoleCommandExecutor:
    """Background dispatcher that forwards console commands via a router."""

    def __init__(self, router: Any, *, daemon: bool = True) -> None:
        if not hasattr(router, "dispatch"):
            raise TypeError("Router must expose a dispatch method")
        self._router = router
        self._queue: queue.Queue[ConsoleCommand | None] = queue.Queue()
        self._thread = threading.Thread(target=self._worker, daemon=daemon)
        self._thread.start()

    def submit(self, command: ConsoleCommand) -> None:
        self._queue.put(command)

    def shutdown(self, timeout: float | None = 1.0) -> None:
        self._queue.put(None)
        self._thread.join(timeout=timeout)

    def _worker(self) -> None:
        while True:
            command = self._queue.get()
            if command is None:
                break
            try:
                self._router.dispatch(command)
            except Exception:  # pragma: no cover - log and continue
                logger.exception("Console command dispatch failed", exc_info=True)
