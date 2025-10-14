"""Console-facing world utilities (placeholder package).

This package re-exports the event-driven console bridge until the dedicated
orchestration surface is finalised by WP1. No legacy queue shims remain.
"""

from __future__ import annotations

from .bridge import ConsoleBridge
from .handlers import WorldConsoleController, install_world_console_handlers

__all__ = ["ConsoleBridge", "WorldConsoleController", "install_world_console_handlers"]
