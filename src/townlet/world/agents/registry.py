"""Mutable mapping wrapper for agent snapshots with bookkeeping metadata."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, MutableMapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from .snapshot import AgentSnapshot

AgentCallback = Callable[[AgentSnapshot], None]


@dataclass(slots=True)
class AgentRecord:
    """Tracks snapshot metadata for auditing and integration hooks."""

    agent_id: str
    snapshot: AgentSnapshot
    created_tick: int = 0
    updated_tick: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def touch(
        self,
        *,
        tick: int | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        if tick is not None:
            self.updated_tick = tick
        if metadata:
            self.metadata.update(metadata)


class AgentRegistry(MutableMapping[str, AgentSnapshot]):
    """Provide a central access point for agent snapshots with lifecycle hooks."""

    def __init__(
        self,
        initial: Iterable[tuple[str, AgentSnapshot]] | Iterable[AgentSnapshot] | None = None,
        *,
        on_add: AgentCallback | None = None,
        on_remove: AgentCallback | None = None,
    ) -> None:
        self._snapshots: dict[str, AgentSnapshot] = {}
        self._records: dict[str, AgentRecord] = {}
        self._on_add = on_add
        self._on_remove = on_remove
        if initial is not None:
            for item in initial:
                snapshot = self._coerce_snapshot(item)
                self.add(snapshot)

    # ------------------------------------------------------------------
    # MutableMapping interface
    # ------------------------------------------------------------------
    def __getitem__(self, key: str) -> AgentSnapshot:
        return self._snapshots[key]

    def __setitem__(self, key: str, value: AgentSnapshot) -> None:
        if value.agent_id != key:
            value.agent_id = key
        self._store_snapshot(value)

    def __delitem__(self, key: str) -> None:
        self._remove_snapshot(key, emit_callback=True)

    def __iter__(self) -> Iterator[str]:
        return iter(self._snapshots)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._snapshots)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------
    def add(
        self,
        snapshot: AgentSnapshot,
        *,
        tick: int | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> AgentSnapshot:
        """Insert or replace ``snapshot`` and return the stored instance."""

        record = self._store_snapshot(snapshot, tick=tick, metadata=metadata)
        if tick is not None and record.created_tick == 0:
            record.created_tick = tick
        return snapshot

    def discard(self, agent_id: str) -> AgentSnapshot | None:
        """Remove an agent if present and return the snapshot."""

        if agent_id not in self._snapshots:
            return None
        snapshot = self._snapshots[agent_id]
        self._remove_snapshot(agent_id, emit_callback=True)
        return snapshot

    def configure_callbacks(
        self,
        *,
        on_add: AgentCallback | None = None,
        on_remove: AgentCallback | None = None,
    ) -> None:
        """Update lifecycle callbacks used during mutation."""

        if on_add is not None:
            self._on_add = on_add
        if on_remove is not None:
            self._on_remove = on_remove

    def values_map(self) -> dict[str, AgentSnapshot]:
        """Return a shallow copy of the snapshot mapping."""

        return dict(self._snapshots)

    def snapshots_view(self) -> Mapping[str, AgentSnapshot]:
        """Return a read-only view of the snapshot mapping."""

        return MappingProxyType(self._snapshots)

    def records_map(self) -> Mapping[str, AgentRecord]:
        """Expose bookkeeping records for diagnostics/tests."""

        return MappingProxyType(self._records)

    def record(self, agent_id: str) -> AgentRecord | None:
        """Return the record for ``agent_id`` if it exists."""

        return self._records.get(agent_id)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _store_snapshot(
        self,
        snapshot: AgentSnapshot,
        *,
        tick: int | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> AgentRecord:
        agent_id = snapshot.agent_id
        record = self._records.get(agent_id)
        if record is None:
            record = AgentRecord(
                agent_id=agent_id,
                snapshot=snapshot,
                created_tick=tick or 0,
                updated_tick=tick or 0,
            )
            if metadata:
                record.metadata.update(metadata)
            self._records[agent_id] = record
        else:
            record.snapshot = snapshot
            record.touch(tick=tick, metadata=metadata)
        self._snapshots[agent_id] = snapshot
        if self._on_add is not None:
            self._on_add(snapshot)
        return record

    def _remove_snapshot(self, agent_id: str, *, emit_callback: bool) -> None:
        record = self._records.pop(agent_id, None)
        snapshot = self._snapshots.pop(agent_id, None)
        if record is None or snapshot is None:
            return
        if emit_callback and self._on_remove is not None:
            self._on_remove(snapshot)

    @staticmethod
    def _coerce_snapshot(
        item: AgentSnapshot | tuple[str, AgentSnapshot],
    ) -> AgentSnapshot:
        if isinstance(item, AgentSnapshot):
            return item
        if isinstance(item, tuple) and len(item) == 2:
            agent_id, snapshot = item
            if not isinstance(snapshot, AgentSnapshot):
                raise TypeError(
                    "initial iterable must contain AgentSnapshot instances; "
                    f"received {type(snapshot)!r}"
                )
            if snapshot.agent_id != agent_id:
                snapshot.agent_id = agent_id
            return snapshot
        raise TypeError(
            "initial must be an iterable of AgentSnapshot or (agent_id, snapshot) tuples"
        )


__all__ = ["AgentCallback", "AgentRecord", "AgentRegistry", "AgentSnapshot"]
