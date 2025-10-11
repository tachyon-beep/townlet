"""Factory registry resolving runtime implementations from provider names."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, TypeVar

from townlet.core.interfaces import PolicyBackendProtocol, TelemetrySinkProtocol
from townlet.ports.world import WorldRuntime

ProviderFactory = Callable[..., object]
T_concrete = TypeVar("T_concrete", bound=object)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class FactoryRegistry:
    """Registers provider names for a specific domain."""

    domain: str
    _providers: dict[str, ProviderFactory] = field(default_factory=dict)

    def register(self, name: str, factory: ProviderFactory) -> None:
        key = name.strip().lower()
        if not key:
            raise ValueError("Provider name must not be empty")
        self._providers[key] = factory

    def has(self, name: str) -> bool:
        return name.strip().lower() in self._providers

    def resolve(self, name: str, **kwargs: Any) -> object:
        key = name.strip().lower()
        try:
            factory = self._providers[key]
        except KeyError as exc:  # pragma: no cover - defensive
            raise KeyError(f"Unknown {self.domain} provider '{name}'") from exc
        return factory(**kwargs)


_world_registry = FactoryRegistry("world")
_policy_registry = FactoryRegistry("policy")
_telemetry_registry = FactoryRegistry("telemetry")


def world_registry() -> FactoryRegistry:
    return _world_registry


def policy_registry() -> FactoryRegistry:
    return _policy_registry


def telemetry_registry() -> FactoryRegistry:
    return _telemetry_registry


def _ensure_protocol(instance: object, protocol: type[T_concrete], name: str) -> T_concrete:
    if not isinstance(instance, protocol):  # pragma: no cover - defensive
        raise TypeError(f"Provider '{name}' did not return an instance of {protocol.__name__}; got {type(instance).__name__}")
    return instance


def resolve_world(name: str, **kwargs: Any) -> WorldRuntime:
    instance = _world_registry.resolve(name, **kwargs)
    return _ensure_protocol(instance, WorldRuntime, name)


def resolve_policy(name: str, **kwargs: Any) -> PolicyBackendProtocol:
    instance = _policy_registry.resolve(name, **kwargs)
    return _ensure_protocol(instance, PolicyBackendProtocol, name)


def resolve_telemetry(name: str, **kwargs: Any) -> TelemetrySinkProtocol:
    instance = _telemetry_registry.resolve(name, **kwargs)
    return _ensure_protocol(instance, TelemetrySinkProtocol, name)


# Register built-in providers
from townlet.policy.fallback import StubPolicyBackend  # noqa: E402  pylint: disable=wrong-import-position
from townlet.policy.models import torch_available  # noqa: E402  pylint: disable=wrong-import-position
from townlet.policy.runner import PolicyRuntime  # noqa: E402  pylint: disable=wrong-import-position
from townlet.telemetry.fallback import StubTelemetrySink  # noqa: E402  pylint: disable=wrong-import-position
from townlet.telemetry.publisher import TelemetryPublisher  # noqa: E402  pylint: disable=wrong-import-position
from townlet.world.runtime import WorldRuntime  # noqa: E402  pylint: disable=wrong-import-position

_world_registry.register("default", lambda **kwargs: WorldRuntime(**kwargs))
_world_registry.register("facade", lambda **kwargs: WorldRuntime(**kwargs))
_policy_registry.register("scripted", lambda **kwargs: PolicyRuntime(**kwargs))
_policy_registry.register("default", lambda **kwargs: PolicyRuntime(**kwargs))
_policy_registry.register("stub", lambda **kwargs: StubPolicyBackend(**kwargs))
_policy_registry.register("pytorch", lambda **kwargs: _resolve_pytorch_policy(**kwargs))
_telemetry_registry.register("stdout", lambda **kwargs: TelemetryPublisher(**kwargs))
_telemetry_registry.register("default", lambda **kwargs: TelemetryPublisher(**kwargs))
_telemetry_registry.register("stub", lambda **kwargs: StubTelemetrySink(**kwargs))
_telemetry_registry.register("http", lambda **kwargs: _resolve_http_telemetry(**kwargs))


def _resolve_pytorch_policy(**kwargs: Any) -> PolicyBackendProtocol:
    if not torch_available():
        logger.warning("policy_provider_fallback provider=pytorch message='PyTorch not installed; using stub backend.'")
        return StubPolicyBackend(**kwargs)
    return PolicyRuntime(**kwargs)


def _resolve_http_telemetry(**kwargs: Any) -> TelemetrySinkProtocol:
    if not _httpx_available():
        logger.warning("telemetry_provider_fallback provider=http message='httpx not installed; using stub telemetry.'")
        return StubTelemetrySink(**kwargs)
    return TelemetryPublisher(**kwargs)


def _httpx_available() -> bool:
    try:
        import httpx  # noqa: F401
    except ModuleNotFoundError:
        return False
    return True
