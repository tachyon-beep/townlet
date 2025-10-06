"""Relationship and rivalry management extracted from the world core."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Dict, Tuple

from townlet.agents.models import Personality
from townlet.agents.relationship_modifiers import (
    RelationshipDelta,
    RelationshipEvent,
    apply_personality_modifiers,
)
from townlet.config import SimulationConfig
from townlet.telemetry.relationship_metrics import RelationshipChurnAccumulator
from townlet.world.relationships import (
    RelationshipLedger,
    RelationshipParameters,
    RelationshipTie,
)
from townlet.world.rivalry import RivalryLedger, RivalryParameters


class RelationshipService:
    """Own relationship and rivalry ledgers for the world."""

    def __init__(
        self,
        config: SimulationConfig,
        *,
        tick_supplier: Callable[[], int],
        personality_resolver: Callable[[str], Personality],
        churn_window: int = 600,
    ) -> None:
        self._config = config
        self._tick_supplier = tick_supplier
        self._resolve_personality = personality_resolver
        self._relationship_ledgers: Dict[str, RelationshipLedger] = {}
        self._rivalry_ledgers: Dict[str, RivalryLedger] = {}
        self._relationship_churn = RelationshipChurnAccumulator(
            window_ticks=churn_window,
            max_samples=8,
        )
        self._pinned_ties: Dict[tuple[str, str], tuple[float, float, float, int]] = {}

    # ------------------------------------------------------------------
    # Core accessors
    # ------------------------------------------------------------------
    def relationship_tie(self, agent_id: str, other_id: str) -> RelationshipTie | None:
        ledger = self._relationship_ledgers.get(agent_id)
        if ledger is None:
            return None
        return ledger.tie_for(other_id)

    def relationships_snapshot(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        payload: Dict[str, Dict[str, Dict[str, float]]] = {}
        for agent_id, ledger in self._relationship_ledgers.items():
            data = ledger.snapshot()
            if data:
                payload[agent_id] = data
        return payload

    def rivalry_snapshot(self) -> Dict[str, Dict[str, float]]:
        payload: Dict[str, Dict[str, float]] = {}
        for agent_id, ledger in self._rivalry_ledgers.items():
            data = ledger.snapshot()
            if data:
                payload[agent_id] = data
        return payload

    def relationship_metrics_snapshot(self) -> dict[str, object]:
        return self._relationship_churn.latest_payload()

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------
    def update_relationship(
        self,
        agent_a: str,
        agent_b: str,
        *,
        trust: float = 0.0,
        familiarity: float = 0.0,
        rivalry: float = 0.0,
        event: RelationshipEvent = "generic",
    ) -> None:
        if agent_a == agent_b:
            return
        delta = RelationshipDelta(trust=trust, familiarity=familiarity, rivalry=rivalry)
        self._apply_relationship_delta(agent_a, agent_b, delta=delta, event=event)
        self._apply_relationship_delta(agent_b, agent_a, delta=delta, event=event)

    def set_relationship(
        self,
        agent_a: str,
        agent_b: str,
        *,
        trust: float,
        familiarity: float,
        rivalry: float,
    ) -> None:
        if agent_a == agent_b:
            return
        tick = self._tick_supplier()
        self._set_relationship_single(
            owner_id=agent_a,
            other_id=agent_b,
            trust=trust,
            familiarity=familiarity,
            rivalry=rivalry,
        )
        self._set_relationship_single(
            owner_id=agent_b,
            other_id=agent_a,
            trust=trust,
            familiarity=familiarity,
            rivalry=rivalry,
        )
        self._pinned_ties[(agent_a, agent_b)] = (trust, familiarity, rivalry, tick)
        self._pinned_ties[(agent_b, agent_a)] = (trust, familiarity, rivalry, tick)

    def apply_rivalry_conflict(
        self,
        agent_a: str,
        agent_b: str,
        *,
        intensity: float,
    ) -> None:
        if agent_a == agent_b:
            return
        ledger_a = self._get_rivalry_ledger(agent_a)
        ledger_b = self._get_rivalry_ledger(agent_b)
        ledger_a.apply_conflict(agent_b, intensity=intensity)
        ledger_b.apply_conflict(agent_a, intensity=intensity)
        self.update_relationship(
            agent_a,
            agent_b,
            rivalry=0.1 * intensity,
            event="conflict",
        )

    def rivalry_value(self, agent_id: str, other_id: str) -> float:
        ledger = self._rivalry_ledgers.get(agent_id)
        if ledger is None:
            return 0.0
        return ledger.score_for(other_id)

    def rivalry_should_avoid(self, agent_id: str, other_id: str) -> bool:
        ledger = self._rivalry_ledgers.get(agent_id)
        if ledger is None:
            return False
        return ledger.should_avoid(other_id)

    def rivalry_top(self, agent_id: str, limit: int) -> list[tuple[str, float]]:
        ledger = self._rivalry_ledgers.get(agent_id)
        if ledger is None:
            return []
        return ledger.top_rivals(limit)

    def get_relationship_ledger(self, agent_id: str) -> RelationshipLedger:
        return self._get_relationship_ledger(agent_id)

    def get_rivalry_ledger(self, agent_id: str) -> RivalryLedger:
        return self._get_rivalry_ledger(agent_id)

    def decay(self) -> None:
        if self._rivalry_ledgers:
            emptied: list[str] = []
            for agent_id, ledger in self._rivalry_ledgers.items():
                ledger.decay(ticks=1)
                if not ledger.snapshot():
                    emptied.append(agent_id)
            for agent_id in emptied:
                self._rivalry_ledgers.pop(agent_id, None)
        if self._relationship_ledgers:
            emptied = []
            current_tick = self._tick_supplier()
            for agent_id, ledger in self._relationship_ledgers.items():
                ledger.decay()
                self._restore_pinned_ties(
                    owner_id=agent_id,
                    ledger=ledger,
                    current_tick=current_tick,
                )
                if not ledger.snapshot():
                    emptied.append(agent_id)
            for agent_id in emptied:
                self._relationship_ledgers.pop(agent_id, None)
            # drop any pinned ties that are no longer relevant
            for key, (_, _, _, tick) in list(self._pinned_ties.items()):
                if tick < current_tick:
                    self._pinned_ties.pop(key, None)

    def remove_agent(self, agent_id: str) -> None:
        """Drop references to ``agent_id`` from relationship and rivalry ledgers."""

        self._relationship_ledgers.pop(agent_id, None)
        for ledger in self._relationship_ledgers.values():
            ledger.remove_tie(agent_id, reason="removed")
        self._rivalry_ledgers.pop(agent_id, None)
        for ledger in self._rivalry_ledgers.values():
            ledger.remove(agent_id, reason="removed")

    # ------------------------------------------------------------------
    # Snapshot import/export
    # ------------------------------------------------------------------
    def load_relationship_snapshot(
        self,
        snapshot: Mapping[str, Mapping[str, Mapping[str, float]]],
    ) -> None:
        self._relationship_ledgers.clear()
        for owner_id, edges in snapshot.items():
            ledger = RelationshipLedger(
                owner_id=owner_id,
                params=self._relationship_parameters(),
            )
            ledger.inject(dict(edges))
            ledger.set_eviction_hook(owner_id=owner_id, hook=self._record_relationship_eviction)
            self._relationship_ledgers[owner_id] = ledger

    def load_relationship_metrics(self, payload: Mapping[str, object] | None) -> None:
        if not payload:
            self._relationship_churn = RelationshipChurnAccumulator(
                window_ticks=self._relationship_churn.window_ticks,
                max_samples=8,
            )
            return
        self._relationship_churn.ingest_payload(dict(payload))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _relationship_parameters(self) -> RelationshipParameters:
        return RelationshipParameters(max_edges=self._config.conflict.rivalry.max_edges)

    def _rivalry_parameters(self) -> RivalryParameters:
        cfg = self._config.conflict.rivalry
        return RivalryParameters(
            increment_per_conflict=cfg.increment_per_conflict,
            decay_per_tick=cfg.decay_per_tick,
            min_value=cfg.min_value,
            max_value=cfg.max_value,
            avoid_threshold=cfg.avoid_threshold,
            eviction_threshold=cfg.eviction_threshold,
            max_edges=cfg.max_edges,
        )

    def _get_relationship_ledger(self, agent_id: str) -> RelationshipLedger:
        ledger = self._relationship_ledgers.get(agent_id)
        if ledger is None:
            ledger = RelationshipLedger(
                owner_id=agent_id,
                params=self._relationship_parameters(),
                eviction_hook=self._record_relationship_eviction,
            )
            self._relationship_ledgers[agent_id] = ledger
        else:
            ledger.set_eviction_hook(
                owner_id=agent_id,
                hook=self._record_relationship_eviction,
            )
        return ledger

    def _get_rivalry_ledger(self, agent_id: str) -> RivalryLedger:
        ledger = self._rivalry_ledgers.get(agent_id)
        if ledger is None:
            ledger = RivalryLedger(
                owner_id=agent_id,
                params=self._rivalry_parameters(),
                eviction_hook=self._record_relationship_eviction,
            )
            self._rivalry_ledgers[agent_id] = ledger
        else:
            ledger.eviction_hook = self._record_relationship_eviction
        return ledger

    def _apply_relationship_delta(
        self,
        owner_id: str,
        other_id: str,
        *,
        delta: RelationshipDelta,
        event: RelationshipEvent,
    ) -> None:
        ledger = self._get_relationship_ledger(owner_id)
        personality = self._resolve_personality(owner_id)
        adjusted = apply_personality_modifiers(
            delta=delta,
            personality=personality,
            event=event,
            enabled=bool(self._config.features.relationship_modifiers),
        )
        ledger.apply_delta(
            other_id,
            trust=adjusted.trust,
            familiarity=adjusted.familiarity,
            rivalry=adjusted.rivalry,
        )

    def _set_relationship_single(
        self,
        *,
        owner_id: str,
        other_id: str,
        trust: float,
        familiarity: float,
        rivalry: float,
        ledger: RelationshipLedger | None = None,
    ) -> None:
        if ledger is None:
            ledger = self._get_relationship_ledger(owner_id)
        current = ledger.tie_for(other_id)
        current_trust = current.trust if current else 0.0
        current_familiarity = current.familiarity if current else 0.0
        current_rivalry = current.rivalry if current else 0.0
        ledger.apply_delta(
            other_id,
            trust=trust - current_trust,
            familiarity=familiarity - current_familiarity,
            rivalry=rivalry - current_rivalry,
        )

    def _restore_pinned_ties(
        self,
        *,
        owner_id: str,
        ledger: RelationshipLedger,
        current_tick: int,
    ) -> None:
        for (candidate_owner, other_id), payload in list(self._pinned_ties.items()):
            if candidate_owner != owner_id:
                continue
            trust, familiarity, rivalry, tick = payload
            if tick != current_tick:
                continue
            self._set_relationship_single(
                owner_id=owner_id,
                other_id=other_id,
                trust=trust,
                familiarity=familiarity,
                rivalry=rivalry,
                ledger=ledger,
            )
            self._pinned_ties.pop((candidate_owner, other_id), None)

    def _record_relationship_eviction(self, owner_id: str, other_id: str, reason: str) -> None:
        self._relationship_churn.record_eviction(
            tick=self._tick_supplier(),
            owner_id=owner_id,
            evicted_id=other_id,
            reason=reason,
        )


__all__ = ["RelationshipService"]
