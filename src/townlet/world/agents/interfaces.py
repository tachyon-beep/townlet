"""Protocols describing agent-facing services.

These interfaces allow consumers (console handlers, telemetry, training) to
reason about the behaviours exposed by the decomposed world modules without
binding to concrete implementations. They will remain intentionally small so we
can iterate on the internals while keeping the external contract stable.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from typing import Protocol, runtime_checkable

from townlet.world.agents.snapshot import AgentSnapshot
from townlet.world.relationships import RelationshipLedger, RelationshipTie
from townlet.world.rivalry import RivalryLedger


@runtime_checkable
class AgentRegistryProtocol(Protocol):
    """Mutable mapping facade for agent snapshots."""

    def __getitem__(self, key: str) -> AgentSnapshot:
        ...

    def __setitem__(self, key: str, value: AgentSnapshot) -> None:
        ...

    def __delitem__(self, key: str) -> None:
        ...

    def __iter__(self) -> Iterable[str]:
        ...

    def __len__(self) -> int:
        ...

    def add(self, snapshot: AgentSnapshot) -> AgentSnapshot:
        ...

    def discard(self, agent_id: str) -> AgentSnapshot | None:
        ...

    def configure_callbacks(
        self,
        *,
        on_add: Callable[[AgentSnapshot], None] | None = None,
        on_remove: Callable[[AgentSnapshot], None] | None = None,
    ) -> None:
        ...

    def values_map(self) -> Mapping[str, AgentSnapshot]:
        ...


@runtime_checkable
class RelationshipServiceProtocol(Protocol):
    """Contract for relationship and rivalry bookkeeping."""

    def relationship_tie(self, agent_id: str, other_id: str) -> RelationshipTie | None:
        ...

    def relationships_snapshot(self) -> Mapping[str, Mapping[str, Mapping[str, float]]]:
        ...

    def rivalry_snapshot(self) -> Mapping[str, Mapping[str, float]]:
        ...

    def relationship_metrics_snapshot(self) -> Mapping[str, object]:
        ...

    def update_relationship(
        self,
        agent_a: str,
        agent_b: str,
        *,
        trust: float = 0.0,
        familiarity: float = 0.0,
        rivalry: float = 0.0,
        event: str = "generic",
    ) -> None:
        ...

    def set_relationship(
        self,
        agent_a: str,
        agent_b: str,
        *,
        trust: float,
        familiarity: float,
        rivalry: float,
    ) -> None:
        ...

    def apply_rivalry_conflict(
        self,
        agent_a: str,
        agent_b: str,
        *,
        intensity: float,
    ) -> None:
        ...

    def rivalry_value(self, agent_id: str, other_id: str) -> float:
        ...

    def rivalry_should_avoid(self, agent_id: str, other_id: str) -> bool:
        ...

    def rivalry_top(self, agent_id: str, limit: int) -> Iterable[tuple[str, float]]:
        ...

    def decay(self) -> None:
        ...

    def remove_agent(self, agent_id: str) -> None:
        ...

    def load_relationship_metrics(self, payload: Mapping[str, object] | None) -> None:
        ...

    def load_relationship_snapshot(
        self,
        snapshot: Mapping[str, Mapping[str, Mapping[str, float]]],
    ) -> None:
        ...

    def get_rivalry_ledger(self, agent_id: str) -> RivalryLedger:
        ...

    def get_relationship_ledger(self, agent_id: str) -> RelationshipLedger:
        ...


@runtime_checkable
class EmploymentServiceProtocol(Protocol):
    """Bridge around employment coordinator/runtime behaviour."""

    def request_manual_exit(self, agent_id: str, tick: int) -> bool:
        ...

    def defer_exit(self, agent_id: str) -> bool:
        ...

    def exits_today(self) -> int:
        ...

    def reset_exits_today(self) -> None:
        ...

    def increment_exits_today(self) -> None:
        ...

    def queue_snapshot(self) -> Mapping[str, object]:
        ...

    def apply_job_state(self) -> None:
        ...

    def assign_jobs_to_agents(self) -> None:
        ...

    def assign_job_if_missing(
        self,
        snapshot: AgentSnapshot,
        *,
        job_index: int | None = None,
    ) -> None:
        ...

    def import_state(self, payload: Mapping[str, object]) -> None:
        ...

    def pending_agents(self) -> Iterable[str]:
        ...


__all__ = [
    "AgentRegistryProtocol",
    "EmploymentServiceProtocol",
    "RelationshipServiceProtocol",
]
