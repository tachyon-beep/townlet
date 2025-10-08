"""Lightweight provider registry for port factories."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable, Dict


Factory = Callable[..., object]


class ConfigurationError(RuntimeError):
    """Raised when a requested provider is not registered."""


_REGISTRY: Dict[str, Dict[str, Factory]] = defaultdict(dict)


def register(kind: str, key: str) -> Callable[[Factory], Factory]:
    """Register a factory callable under ``kind``/``key``."""

    normalized_kind = kind.strip().lower()
    normalized_key = key.strip().lower()

    def decorator(factory: Factory) -> Factory:
        _REGISTRY[normalized_kind][normalized_key] = factory
        return factory

    return decorator


def resolve(kind: str, key: str, **kwargs: Any) -> object:
    normalized_kind = kind.strip().lower()
    normalized_key = key.strip().lower()
    providers = _REGISTRY.get(normalized_kind)
    if not providers or normalized_key not in providers:
        known = sorted(providers.keys()) if providers else []
        raise ConfigurationError(
            f"Unknown {kind} provider '{key}'. Known providers: {known}"
        )
    factory = providers[normalized_key]
    return factory(**kwargs)


def available(kind: str) -> list[str]:
    return sorted(_REGISTRY.get(kind.strip().lower(), {}).keys())


__all__ = [
    "ConfigurationError",
    "register",
    "resolve",
    "available",
]
