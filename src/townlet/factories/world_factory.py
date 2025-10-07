"""Factory helpers for world runtime providers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from townlet.factories.registry import ConfigurationError, _resolve
from townlet.ports.world import WorldRuntime

_DEFAULT_PROVIDER = "default"


def create_world(config: Mapping[str, Any] | None = None) -> WorldRuntime:
    """Return a :class:`WorldRuntime` constructed from ``config``."""

    cfg = dict(config or {})
    provider = str(cfg.pop("provider", _DEFAULT_PROVIDER)).strip().lower()
    try:
        factory = _resolve("world", provider)
    except ConfigurationError as exc:  # pragma: no cover - defensive
        raise ConfigurationError(str(exc)) from exc
    instance = factory(**cfg)
    required = ("reset", "tick", "agents", "observe", "apply_actions", "snapshot")
    missing = [name for name in required if not hasattr(instance, name)]
    if missing:
        raise ConfigurationError(
            f"World provider '{provider}' is invalid; missing methods: {sorted(missing)}."
        )
    return instance  # type: ignore[return-value]


# Ensure built-in providers are registered on import.
from townlet.adapters import world_default as _world_default  # noqa: E402,F401
from townlet.testing import dummies as _world_dummies  # noqa: E402,F401
