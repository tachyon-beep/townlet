"""Legacy observation helper module.

The functions here now proxy to ``townlet.world.observations`` submodules. They
will be removed once downstream consumers migrate to the new import paths.
"""

from __future__ import annotations

import warnings
from typing import Any

from townlet.world.observations.cache import build_local_cache as _build_local_cache
from townlet.world.observations.context import (
    agent_context as _agent_context,
    snapshot_precondition_context as _snapshot_precondition_context,
)
from townlet.world.observations.views import (
    find_nearest_object_of_type as _find_nearest_object_of_type,
    local_view as _local_view,
)


def _warn(target: str) -> None:
    warnings.warn(
        f"{target} is deprecated; import from townlet.world.observations.* instead",
        DeprecationWarning,
        stacklevel=2,
    )


def build_local_cache(*args: Any, **kwargs: Any):
    _warn("townlet.world.observation.build_local_cache")
    return _build_local_cache(*args, **kwargs)


def local_view(*args: Any, **kwargs: Any):
    _warn("townlet.world.observation.local_view")
    return _local_view(*args, **kwargs)


def agent_context(*args: Any, **kwargs: Any):
    _warn("townlet.world.observation.agent_context")
    return _agent_context(*args, **kwargs)


def find_nearest_object_of_type(*args: Any, **kwargs: Any):
    _warn("townlet.world.observation.find_nearest_object_of_type")
    return _find_nearest_object_of_type(*args, **kwargs)


def snapshot_precondition_context(*args: Any, **kwargs: Any):
    _warn("townlet.world.observation.snapshot_precondition_context")
    return _snapshot_precondition_context(*args, **kwargs)


__all__ = [
    "agent_context",
    "build_local_cache",
    "find_nearest_object_of_type",
    "local_view",
    "snapshot_precondition_context",
]
