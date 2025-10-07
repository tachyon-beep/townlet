"""Console-facing world utilities (placeholder package).

This module currently re-exports the legacy console bridge implementation.
Future phases of WP-C will migrate concrete implementations into this package.
"""

from __future__ import annotations

from .bridge import ConsoleBridge
from .handlers import WorldConsoleController, install_world_console_handlers

__all__ = ["ConsoleBridge", "WorldConsoleController", "install_world_console_handlers"]
