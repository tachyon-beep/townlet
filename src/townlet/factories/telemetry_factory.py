"""Factory helpers for telemetry sink providers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from townlet.factories.registry import ConfigurationError, _resolve
from townlet.ports.telemetry import TelemetrySink

_DEFAULT_PROVIDER = "stdout"


def create_telemetry(config: Mapping[str, Any] | None = None) -> TelemetrySink:
    """Return a :class:`TelemetrySink` constructed from ``config``."""

    cfg = dict(config or {})
    provider = str(cfg.pop("provider", _DEFAULT_PROVIDER)).strip().lower()
    try:
        factory = _resolve("telemetry", provider)
    except ConfigurationError as exc:  # pragma: no cover - defensive
        raise ConfigurationError(str(exc)) from exc
    instance = factory(**cfg)
    required = ("start", "stop", "emit_event", "emit_metric")
    missing = [name for name in required if not hasattr(instance, name)]
    if missing:
        raise ConfigurationError(
            f"Telemetry provider '{provider}' is invalid; missing methods: {sorted(missing)}."
        )
    return instance  # type: ignore[return-value]


from townlet.adapters import telemetry_stdout as _telemetry_stdout  # noqa: E402,F401
from townlet.testing import dummies as _telemetry_dummies  # noqa: E402,F401
