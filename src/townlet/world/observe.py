"""Observation helpers (skeleton)."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Mapping

from .state import WorldState


def build_observations(state: WorldState, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]:
    """Return per-agent observations (placeholder implementation)."""

    raise NotImplementedError("build_observations pending WP2 implementation")


__all__ = ["build_observations"]
