"""Convenience accessors for policy backends."""

from __future__ import annotations

from typing import Any

from townlet.core.factory_registry import resolve_policy
from townlet.core.interfaces import PolicyBackendProtocol

DEFAULT_POLICY_PROVIDER = "scripted"


def resolve_policy_backend(
    provider: str | None = None,
    **kwargs: Any,
) -> PolicyBackendProtocol:
    """Return a policy backend instance resolved via the factory registry."""

    selected = provider or DEFAULT_POLICY_PROVIDER
    return resolve_policy(selected, **kwargs)


__all__ = ["DEFAULT_POLICY_PROVIDER", "resolve_policy_backend"]
