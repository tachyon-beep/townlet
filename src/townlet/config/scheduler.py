"""Scheduler and perturbation configuration models."""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .core import FloatRange, IntRange


class PerturbationKind(str, Enum):
    """Supported perturbation event identifiers."""

    PRICE_SPIKE = "price_spike"
    BLACKOUT = "blackout"
    OUTAGE = "outage"
    ARRANGED_MEET = "arranged_meet"


class BasePerturbationEventConfig(BaseModel):
    kind: PerturbationKind
    probability_per_day: float = Field(0.0, ge=0.0, alias="prob_per_day")
    cooldown_ticks: int = Field(0, ge=0)
    duration: IntRange = Field(default_factory=lambda: IntRange(min=0, max=0))

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    @model_validator(mode="before")
    def _normalise_duration(cls, values: dict[str, object]) -> dict[str, object]:  # noqa: N805
        if isinstance(values, Mapping):
            if "duration" not in values and "duration_min" in values:
                copy = dict(values)
                copy["duration"] = copy.get("duration_min")
                return copy
        return values


class PriceSpikeEventConfig(BasePerturbationEventConfig):
    kind: Literal[PerturbationKind.PRICE_SPIKE] = PerturbationKind.PRICE_SPIKE
    magnitude: FloatRange = Field(default_factory=lambda: FloatRange(min=1.0, max=1.0))
    targets: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    def _normalise_magnitude(cls, values: dict[str, object]) -> dict[str, object]:  # noqa: N805
        if isinstance(values, Mapping):
            if "magnitude" not in values and "magnitude_range" in values:
                copy = dict(values)
                copy["magnitude"] = copy.get("magnitude_range")
                return copy
        return values


class BlackoutEventConfig(BasePerturbationEventConfig):
    kind: Literal[PerturbationKind.BLACKOUT] = PerturbationKind.BLACKOUT
    utility: Literal["power"] = "power"


class OutageEventConfig(BasePerturbationEventConfig):
    kind: Literal[PerturbationKind.OUTAGE] = PerturbationKind.OUTAGE
    utility: Literal["water"] = "water"


class ArrangedMeetEventConfig(BasePerturbationEventConfig):
    kind: Literal[PerturbationKind.ARRANGED_MEET] = PerturbationKind.ARRANGED_MEET
    target: str = Field(default="top_rivals")
    location: str = Field(default="cafe")
    max_participants: int = Field(2, ge=2)


PerturbationEventConfig = Annotated[
    PriceSpikeEventConfig | BlackoutEventConfig | OutageEventConfig | ArrangedMeetEventConfig,
    Field(discriminator="kind"),
]


class PerturbationSchedulerConfig(BaseModel):
    """Configure the perturbation scheduler and event catalogue."""

    max_concurrent_events: int = Field(1, ge=1)
    global_cooldown_ticks: int = Field(0, ge=0)
    per_agent_cooldown_ticks: int = Field(0, ge=0)
    grace_window_ticks: int = Field(60, ge=0)
    window_ticks: int = Field(1440, ge=1)
    max_events_per_window: int = Field(1, ge=0)
    events: dict[str, PerturbationEventConfig] = Field(default_factory=dict)

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @property
    def event_list(self) -> list[PerturbationEventConfig]:
        return list(self.events.values())


__all__ = [
    "ArrangedMeetEventConfig",
    "BasePerturbationEventConfig",
    "BlackoutEventConfig",
    "OutageEventConfig",
    "PerturbationEventConfig",
    "PerturbationKind",
    "PerturbationSchedulerConfig",
    "PriceSpikeEventConfig",
]
