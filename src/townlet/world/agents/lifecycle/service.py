"""Agent lifecycle orchestration extracted from the world grid module."""

from __future__ import annotations

from collections.abc import Callable, Mapping, MutableMapping
from dataclasses import dataclass
from typing import Any

from townlet.agents.models import Personality
from townlet.world.agents.employment import EmploymentService
from townlet.world.agents.registry import AgentRegistry
from townlet.world.agents.relationships_service import RelationshipService
from townlet.world.agents.snapshot import AgentSnapshot
from townlet.world.queue import QueueManager
from townlet.world.queue.conflict import QueueConflictTracker

if __name__ == "__main__":  # pragma: no cover - module coverage
    raise SystemExit("lifecycle service module is not meant to be executed directly")


@dataclass(slots=True)
class LifecycleService:
    """Coordinate agent spawn/despawn flows on behalf of the world façade."""

    agents: AgentRegistry
    objects: MutableMapping[str, Any]
    queue_manager: QueueManager
    spatial_index: Any
    employment_service: EmploymentService
    relationship_service: RelationshipService
    affordance_service: Any
    embedding_allocator: Any
    queue_conflicts: QueueConflictTracker
    recent_meal_participants: MutableMapping[str, dict[str, Any]]
    respawn_counters: MutableMapping[str, int]
    emit_event: Callable[[str, dict[str, object]], None]
    request_ctx_reset: Callable[[str], None]
    sync_reservation: Callable[[str], None]
    tick_supplier: Callable[[], int]
    update_basket_metrics: Callable[[], None]
    choose_personality_profile: Callable[[str, str | None], tuple[str, Personality]]
    objects_by_position: MutableMapping[tuple[int, int], list[str]]
    active_reservations: MutableMapping[str, str | None]

    def spawn_agent(
        self,
        agent_id: str,
        position: tuple[int, int],
        *,
        needs: Mapping[str, float] | None = None,
        home_position: tuple[int, int] | None = None,
        wallet: float | None = None,
        personality_profile: str | None = None,
    ) -> AgentSnapshot:
        if agent_id in self.agents:
            raise ValueError(f"agent '{agent_id}' already exists")

        dest = (int(position[0]), int(position[1]))
        if not self._is_position_walkable(dest):
            raise ValueError("spawn position not walkable")

        if home_position is None:
            home_coord = dest
        else:
            home_coord = (int(home_position[0]), int(home_position[1]))

        wallet_value = float(wallet) if wallet is not None else 0.0
        resolved_needs = dict(needs or {})
        profile_name = personality_profile or "balanced"  # Default to "balanced" (required by DTO validation)

        snapshot = AgentSnapshot(
            agent_id=agent_id,
            position=dest,
            needs=resolved_needs,
            wallet=wallet_value,
            home_position=home_coord,
            personality_profile=profile_name,
        )
        self.agents[agent_id] = snapshot
        self.spatial_index.insert_agent(agent_id, snapshot.position)
        self._assign_job_if_missing(snapshot)
        self._sync_agent_spawn(snapshot)
        self.update_basket_metrics()
        self.request_ctx_reset(agent_id)
        self.emit_event(
            "agent_spawned",
            {"agent_id": agent_id, "position": list(snapshot.position)},
        )
        return snapshot

    def teleport_agent(self, agent_id: str, position: tuple[int, int]) -> tuple[int, int]:
        snapshot = self.agents.get(agent_id)
        if snapshot is None:
            raise KeyError(agent_id)

        dest = (int(position[0]), int(position[1]))
        if dest in self.objects_by_position:
            raise ValueError("destination blocked by object")

        occupied = {
            other_id
            for other_id, other in self.agents.items()
            if other_id != agent_id and other.position == dest
        }
        if occupied:
            raise ValueError("destination occupied")

        snapshot.position = dest
        self.spatial_index.move_agent(agent_id, dest)
        self.sync_reservation_for_agent(agent_id)
        self.request_ctx_reset(agent_id)
        self.emit_event(
            "agent_teleported",
            {"agent_id": agent_id, "position": list(dest)},
        )
        return dest

    def remove_agent(self, agent_id: str, tick: int) -> dict[str, Any] | None:
        snapshot = self.agents.pop(agent_id, None)
        if snapshot is None:
            return None

        self.spatial_index.remove_agent(agent_id)
        self.queue_manager.remove_agent(agent_id, tick)
        self.affordance_service.remove_agent(agent_id)

        for object_id, occupant in list(self.active_reservations.items()):
            if occupant == agent_id:
                self.queue_manager.release(object_id, agent_id, tick, success=False)
                self.active_reservations.pop(object_id, None)
                obj = self.objects.get(object_id)
                if obj is not None:
                    obj.occupied_by = None
                    if getattr(obj, "position", None) is not None:
                        self.spatial_index.set_reservation(obj.position, False)
                self.sync_reservation(object_id)

        self.embedding_allocator.release(agent_id, tick)
        self.employment_service.remove_agent(agent_id)
        self.relationship_service.remove_agent(agent_id)

        for record in self.recent_meal_participants.values():
            participants = record.get("agents")
            if isinstance(participants, set):
                participants.discard(agent_id)

        self.queue_conflicts.remove_agent(agent_id)

        blueprint = {
            "agent_id": snapshot.agent_id,
            "origin_agent_id": snapshot.origin_agent_id or snapshot.agent_id,
            "personality": snapshot.personality,
            "personality_profile": snapshot.personality_profile,
            "job_id": snapshot.job_id,
            "position": snapshot.position,
            "home_position": snapshot.home_position,
        }
        self.emit_event(
            "agent_removed",
            {
                "agent_id": snapshot.agent_id,
                "tick": tick,
            },
        )
        return blueprint

    def kill_agent(self, agent_id: str, *, reason: str | None = None) -> bool:
        tick = self.tick_supplier()
        blueprint = self.remove_agent(agent_id, tick)
        if blueprint is None:
            return False
        self.emit_event(
            "agent_killed",
            {
                "agent_id": agent_id,
                "reason": reason,
                "tick": tick,
            },
        )
        return True

    def respawn_agent(self, blueprint: Mapping[str, Any]) -> None:
        agent_id = str(blueprint.get("agent_id", ""))
        if not agent_id or agent_id in self.agents:
            return

        origin_agent_id = str(
            blueprint.get("origin_agent_id") or blueprint.get("agent_id") or agent_id
        )

        position_tuple = self._resolve_position(blueprint.get("position"))
        home_tuple = self._resolve_optional_position(blueprint.get("home_position"))

        profile_field = blueprint.get("personality_profile")
        resolved_profile, resolved_personality = self.choose_personality_profile(
            agent_id,
            profile_field if isinstance(profile_field, str) else None,
        )
        personality_override = blueprint.get("personality")
        if isinstance(personality_override, Personality):
            resolved_personality = personality_override

        snapshot = AgentSnapshot(
            agent_id=agent_id,
            position=position_tuple,
            needs={"hunger": 0.5, "hygiene": 0.5, "energy": 0.5},
            wallet=0.0,
            home_position=home_tuple,
            origin_agent_id=origin_agent_id,
            personality=resolved_personality,
            personality_profile=resolved_profile,
        )
        job_id = blueprint.get("job_id")
        if isinstance(job_id, str):
            snapshot.job_id = job_id

        self.agents[agent_id] = snapshot
        self.spatial_index.insert_agent(agent_id, snapshot.position)
        self._assign_job_if_missing(snapshot)
        self._sync_agent_spawn(snapshot)
        self.emit_event(
            "agent_respawn",
            {
                "agent_id": agent_id,
                "original_agent_id": origin_agent_id,
                "tick": self.tick_supplier(),
            },
        )

    def generate_agent_id(self, base_id: str) -> str:
        base = base_id or "agent"
        counter = self.respawn_counters.get(base, 0)
        while True:
            counter += 1
            candidate = f"{base}#{counter}"
            if candidate not in self.agents:
                self.respawn_counters[base] = counter
                return candidate

    # ------------------------------------------------------------------
    # Helper utilities
    # ------------------------------------------------------------------

    def _assign_job_if_missing(self, snapshot: AgentSnapshot) -> None:
        job_index = max(0, len(self.agents) - 1)
        self.employment_service.assign_job_if_missing(
            snapshot,
            job_index=job_index,
        )

    def _sync_agent_spawn(self, snapshot: AgentSnapshot) -> None:
        if snapshot.home_position is None:
            snapshot.home_position = snapshot.position
        self.employment_service.reset_context(snapshot.agent_id)
        self.embedding_allocator.allocate(snapshot.agent_id, self.tick_supplier())

    def sync_reservation_for_agent(self, agent_id: str) -> None:
        for object_id, occupant in list(self.active_reservations.items()):
            if occupant == agent_id:
                self.sync_reservation(object_id)

    def assign_job_if_missing(self, snapshot: AgentSnapshot) -> None:
        self._assign_job_if_missing(snapshot)

    def sync_agent_spawn(self, snapshot: AgentSnapshot) -> None:
        self._sync_agent_spawn(snapshot)

    def _is_position_walkable(self, position: tuple[int, int]) -> bool:
        if any(agent.position == position for agent in self.agents.values()):
            return False
        if position in self.objects_by_position:
            return False
        return True

    def _resolve_position(self, payload: Any) -> tuple[int, int]:
        if (
            isinstance(payload, (list, tuple))
            and len(payload) == 2
            and all(isinstance(coord, (int, float)) for coord in payload)
        ):
            candidate = (int(payload[0]), int(payload[1]))
            return candidate if self._is_position_walkable(candidate) else (0, 0)
        return (0, 0)

    @staticmethod
    def _resolve_optional_position(payload: Any) -> tuple[int, int] | None:
        if (
            isinstance(payload, (list, tuple))
            and len(payload) == 2
            and all(isinstance(coord, (int, float)) for coord in payload)
        ):
            return (int(payload[0]), int(payload[1]))
        return None

    def is_position_walkable(self, position: tuple[int, int]) -> bool:
        return self._is_position_walkable(position)


__all__ = ["LifecycleService"]
