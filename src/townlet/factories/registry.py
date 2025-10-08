"""Simple registry-backed factory helpers."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

REGISTRY: dict[str, dict[str, Callable[..., object]]] = defaultdict(dict)


class ConfigurationError(RuntimeError):
    """Raised when configuration selects an unknown provider."""


def register(kind: str, key: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
    """Register a factory callable under ``kind``/``key``."""

    def decorator(factory: Callable[..., object]) -> Callable[..., object]:
        providers = REGISTRY.setdefault(kind, {})
        providers[key] = factory
        return factory

    return decorator


def resolve(kind: str, key: str) -> Callable[..., object]:
    """Return the factory callable for ``kind``/``key``."""

    providers = REGISTRY.get(kind, {})
    try:
        return providers[key]
    except KeyError as exc:  # pragma: no cover - defensive guard
        known = sorted(providers)
        raise ConfigurationError(
            f"Unknown {kind} provider: {key}. Known: {known}"
        ) from exc


__all__ = ["REGISTRY", "ConfigurationError", "register", "resolve"]
