"""Personality helpers shared across agent services."""

from __future__ import annotations

from typing import Tuple

from townlet.agents.models import Personality, personality_from_profile

DEFAULT_PROFILE_NAME = "balanced"


def default_personality() -> Personality:
    """Return a neutral personality profile when none is provided."""

    return personality_from_profile(DEFAULT_PROFILE_NAME)[1]


def resolve_personality_profile(name: str | None) -> Tuple[str, Personality]:
    """Resolve a profile name to canonical id + personality."""

    try:
        return personality_from_profile(name)
    except KeyError:
        # Fallback to balanced profile when the manifest does not recognise the
        # requested trait. This mirrors legacy world behaviour.
        from logging import getLogger

        logger = getLogger(__name__)
        logger.warning(
            "unknown_personality_profile name=%s fallback=%s",
            name,
            DEFAULT_PROFILE_NAME,
        )
        return personality_from_profile(DEFAULT_PROFILE_NAME)


def normalize_profile_name(name: str | None) -> str | None:
    """Normalise user supplied names for downstream lookup hooks."""

    if name is None:
        return None
    trimmed = str(name).strip()
    return trimmed.lower() if trimmed else None


__all__ = [
    "DEFAULT_PROFILE_NAME",
    "default_personality",
    "resolve_personality_profile",
    "normalize_profile_name",
]
