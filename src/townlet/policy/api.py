"""Convenience accessors for policy backends."""

from __future__ import annotations

import logging
from typing import Any

from townlet.core.factory_registry import resolve_policy
from townlet.core.interfaces import PolicyBackendProtocol

DEFAULT_POLICY_PROVIDER = "scripted"

logger = logging.getLogger(__name__)


def resolve_policy_backend(
    provider: str | None = None,
    **kwargs: Any,
) -> PolicyBackendProtocol:
    """Return a policy backend instance resolved via the factory registry."""

    selected = provider or DEFAULT_POLICY_PROVIDER
    backend = resolve_policy(selected, **kwargs)
    capability = getattr(backend, "supports_observation_envelope", None)
    if capability is None or not callable(capability):
        raise TypeError(
            f"Policy backend '{selected}' does not expose supports_observation_envelope(); "
            "update the provider to the Stage 3 DTO contract."
        )
    if not bool(capability()):
        logger.warning(
            "policy_backend_dto_support_missing provider=%s message='Backend does not "
            "declare DTO observation support; expect failures once legacy payloads are removed.'",
            selected,
        )
    return backend


__all__ = ["DEFAULT_POLICY_PROVIDER", "resolve_policy_backend"]
