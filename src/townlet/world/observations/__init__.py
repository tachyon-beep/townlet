"""Observation helper shim package maintained during WP-C Phase 4.

Direct imports remain temporarily supported but emit ``DeprecationWarning`` so
consumers can migrate to the dedicated modules in ``townlet.world.observations``.
"""

from __future__ import annotations

import warnings
from typing import Any


def _warn(target: str) -> None:
    warnings.warn(
        f"{target} is deprecated; import from townlet.world.observations.cache/context/views instead",
        DeprecationWarning,
        stacklevel=2,
    )


def build_local_cache(*args: Any, **kwargs: Any):
    _warn("townlet.world.observations.build_local_cache")
    from .cache import build_local_cache as _impl

    return _impl(*args, **kwargs)


def local_view(*args: Any, **kwargs: Any):
    _warn("townlet.world.observations.local_view")
    from .views import local_view as _impl

    return _impl(*args, **kwargs)


def find_nearest_object_of_type(*args: Any, **kwargs: Any):
    _warn("townlet.world.observations.find_nearest_object_of_type")
    from .views import find_nearest_object_of_type as _impl

    return _impl(*args, **kwargs)


def agent_context(*args: Any, **kwargs: Any):
    _warn("townlet.world.observations.agent_context")
    from .context import agent_context as _impl

    return _impl(*args, **kwargs)


def snapshot_precondition_context(*args: Any, **kwargs: Any):
    _warn("townlet.world.observations.snapshot_precondition_context")
    from .context import snapshot_precondition_context as _impl

    return _impl(*args, **kwargs)


__all__ = [
    "agent_context",
    "build_local_cache",
    "find_nearest_object_of_type",
    "local_view",
    "snapshot_precondition_context",
]
