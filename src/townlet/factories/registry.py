"""Simple registry used by runtime factories to resolve providers."""

from __future__ import annotations

from collections.abc import Callable

REGISTRY: dict[str, dict[str, Callable[..., object]]] = {
    "world": {},
    "policy": {},
    "telemetry": {},
}


class ConfigurationError(RuntimeError):
    """Raised when a factory cannot resolve the requested provider."""


def register(kind: str, key: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
    """Register ``key`` for ``kind`` and return the decorating factory."""

    normalised_kind = kind.strip().lower()
    if normalised_kind not in REGISTRY:
        raise KeyError(f"Unknown registry kind: {kind}")
    normalised_key = key.strip().lower()
    if not normalised_key:
        raise ValueError("Registry key must not be empty")

    def decorator(factory: Callable[..., object]) -> Callable[..., object]:
        REGISTRY[normalised_kind][normalised_key] = factory
        return factory

    return decorator


def known_providers(kind: str) -> list[str]:
    """Return the sorted list of registered providers for ``kind``."""

    return sorted(REGISTRY.get(kind, {}))


def _resolve(kind: str, provider: str) -> Callable[..., object]:
    try:
        return REGISTRY[kind][provider]
    except KeyError as exc:  # pragma: no cover - defensive branch
        raise ConfigurationError(
            f"Unknown {kind} provider: {provider}. Known: {known_providers(kind)}"
        ) from exc
