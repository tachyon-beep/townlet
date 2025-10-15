"""Agent-related dataclasses and helpers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import ClassVar


@dataclass
class Personality:
    extroversion: float
    forgiveness: float
    ambition: float


@dataclass(frozen=True)
class PersonalityProfile:
    """Bundle of trait multipliers applied when instantiating an agent."""

    name: str
    personality: Personality
    need_multipliers: Mapping[str, float] = field(default_factory=dict)
    reward_bias: Mapping[str, float] = field(default_factory=dict)
    behaviour_bias: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "need_multipliers", self._freeze(self.need_multipliers))
        object.__setattr__(self, "reward_bias", self._freeze(self.reward_bias))
        object.__setattr__(self, "behaviour_bias", self._freeze(self.behaviour_bias))

    @staticmethod
    def _freeze(payload: Mapping[str, float]) -> Mapping[str, float]:
        if isinstance(payload, MappingProxyType):
            return payload
        return MappingProxyType({key: float(value) for key, value in payload.items()})


def _profile(
    name: str,
    *,
    personality: Personality,
    need_multipliers: Mapping[str, float] | None = None,
    reward_bias: Mapping[str, float] | None = None,
    behaviour_bias: Mapping[str, float] | None = None,
) -> PersonalityProfile:
    return PersonalityProfile(
        name=name,
        personality=personality,
        need_multipliers=need_multipliers or {},
        reward_bias=reward_bias or {},
        behaviour_bias=behaviour_bias or {},
    )


class PersonalityProfiles:
    """Registry of built-in personality archetypes."""

    _profiles: ClassVar[dict[str, PersonalityProfile]] = {
        "balanced": _profile(
            "balanced",
            personality=Personality(extroversion=0.0, forgiveness=0.0, ambition=0.0),
        ),
        "socialite": _profile(
            "socialite",
            personality=Personality(extroversion=0.6, forgiveness=0.1, ambition=-0.1),
            need_multipliers={"hygiene": 1.1},
            reward_bias={"social": 1.2},
            behaviour_bias={"chat_preference": 1.3},
        ),
        "industrious": _profile(
            "industrious",
            personality=Personality(extroversion=-0.2, forgiveness=-0.1, ambition=0.5),
            need_multipliers={"energy": 0.9},
            reward_bias={"employment": 1.25},
            behaviour_bias={"work_affinity": 1.4},
        ),
        "stoic": _profile(
            "stoic",
            personality=Personality(extroversion=-0.3, forgiveness=0.5, ambition=-0.2),
            need_multipliers={"hunger": 0.95},
            reward_bias={"survival": 1.1},
            behaviour_bias={"conflict_tolerance": 0.6},
        ),
    }

    @classmethod
    def get(cls, name: str) -> PersonalityProfile:
        """Return the personality profile registered under ``name``."""

        key = name.lower()
        if key not in cls._profiles:
            raise KeyError(name)
        return cls._profiles[key]

    @classmethod
    def names(cls) -> tuple[str, ...]:
        """Return all profile names registered on this class."""

        return tuple(sorted(cls._profiles.keys()))

    @classmethod
    def resolve(cls, name: str | None) -> PersonalityProfile:
        """Resolve ``name`` to a profile, falling back to balanced."""

        if not name:
            return cls._profiles["balanced"]
        return cls.get(name)


def personality_from_profile(name: str | None) -> tuple[str, Personality]:
    """Resolve an optional profile name to `(profile_name, personality)`."""

    profile = PersonalityProfiles.resolve(name)
    return profile.name, profile.personality


@dataclass
class RelationshipEdge:
    """Directed relationship edge from one agent to another."""

    other_id: str
    trust: float
    familiarity: float
    rivalry: float


@dataclass
class AgentState:
    """Canonical agent state used across modules."""

    agent_id: str
    needs: dict[str, float]
    wallet: float
    personality: Personality
    relationships: list[RelationshipEdge] = field(default_factory=list)
