"""Console-facing world utilities (placeholder package).

This module currently re-exports the legacy console bridge implementation.
Future phases of WP-C will migrate concrete implementations into this package.
"""

from __future__ import annotations

from townlet.world.console_bridge import ConsoleBridge
from townlet.world.console_handlers import (
    WorldConsoleController,
    install_world_console_handlers,
)

__all__ = ["ConsoleBridge", "WorldConsoleController", "install_world_console_handlers"]
