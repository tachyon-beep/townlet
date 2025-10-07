"""Factory helpers for policy backend providers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from townlet.factories.registry import ConfigurationError, _resolve
from townlet.ports.policy import PolicyBackend

_DEFAULT_PROVIDER = "scripted"


def create_policy(config: Mapping[str, Any] | None = None) -> PolicyBackend:
    """Return a :class:`PolicyBackend` constructed from ``config``."""

    cfg = dict(config or {})
    provider = str(cfg.pop("provider", _DEFAULT_PROVIDER)).strip().lower()
    try:
        factory = _resolve("policy", provider)
    except ConfigurationError as exc:  # pragma: no cover - defensive
        raise ConfigurationError(str(exc)) from exc
    instance = factory(**cfg)
    required = ("on_episode_start", "decide", "on_episode_end")
    missing = [name for name in required if not hasattr(instance, name)]
    if missing:
        raise ConfigurationError(
            f"Policy provider '{provider}' is invalid; missing methods: {sorted(missing)}."
        )
    return instance  # type: ignore[return-value]


from townlet.adapters import policy_scripted as _policy_scripted  # noqa: E402,F401
from townlet.testing import dummies as _policy_dummies  # noqa: E402,F401
