"""Console command handling exports."""

from __future__ import annotations

from importlib import import_module
from typing import Any

__all__ = ["ConsoleCommand", "ConsoleRouter"]


def __getattr__(name: str) -> Any:
    if name in __all__:
        module = import_module("townlet.console.handlers")
        return getattr(module, name)
    raise AttributeError(name)
