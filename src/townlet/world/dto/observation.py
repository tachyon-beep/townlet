"""Schema definitions for policy observation payloads."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

DTO_SCHEMA_VERSION = "0.2.0"


class _FrozenModel(BaseModel):
    """Base model that rejects unknown fields and keeps data immutable."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class AgentObservationDTO(_FrozenModel):
    """Per-agent observation payload exposed to policy adapters."""

    agent_id: str
    map: Sequence[Sequence[Sequence[float]]] | None = None
    features: Sequence[float] | None = None
    metadata: Mapping[str, Any] = Field(default_factory=dict)
    rewards: Mapping[str, float] | None = None
    terminated: bool | None = None
    position: Sequence[float] | None = None
    needs: Mapping[str, float] | None = None
    wallet: float | None = None
    inventory: Mapping[str, Any] | None = None
    job: Mapping[str, Any] | None = None
    personality: Mapping[str, Any] | None = None
    queue_state: Mapping[str, Any] | None = None
    pending_intent: Mapping[str, Any] | None = None


class GlobalObservationDTO(_FrozenModel):
    """Global context bundled alongside per-agent observations."""

    queue_metrics: Mapping[str, int] = Field(default_factory=dict)
    rewards: Mapping[str, Mapping[str, float]] = Field(default_factory=dict)
    perturbations: Mapping[str, Any] = Field(default_factory=dict)
    policy_snapshot: Mapping[str, Any] = Field(default_factory=dict)
    rivalry_events: Sequence[Mapping[str, Any]] = Field(default_factory=list)
    stability_metrics: Mapping[str, Any] = Field(default_factory=dict)
    promotion_state: Mapping[str, Any] | None = None
    policy_metadata: Mapping[str, Any] = Field(default_factory=dict)
    rng_seed: int | None = None
    queues: Mapping[str, Any] = Field(default_factory=dict)
    running_affordances: Mapping[str, Any] = Field(default_factory=dict)
    relationship_snapshot: Mapping[str, Any] = Field(default_factory=dict)
    relationship_metrics: Mapping[str, Any] = Field(default_factory=dict)
    employment_snapshot: Mapping[str, Any] = Field(default_factory=dict)
    queue_affinity_metrics: Mapping[str, Any] = Field(default_factory=dict)
    economy_snapshot: Mapping[str, Any] = Field(default_factory=dict)
    anneal_context: Mapping[str, Any] = Field(default_factory=dict)


class ObservationEnvelope(_FrozenModel):
    """Top-level container delivered to policy runners and telemetry."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True, frozen=True)

    tick: int
    schema_version: str = Field(default=DTO_SCHEMA_VERSION, alias="dto_schema_version")
    agents: Sequence[AgentObservationDTO] = Field(default_factory=list)
    global_context: GlobalObservationDTO = Field(
        default_factory=GlobalObservationDTO, alias="global"
    )
    actions: Mapping[str, Any] = Field(default_factory=dict)
    terminated: Mapping[str, bool] = Field(default_factory=dict)
    termination_reasons: Mapping[str, str] = Field(default_factory=dict)
