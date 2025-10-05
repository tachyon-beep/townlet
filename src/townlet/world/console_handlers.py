"""Console command handlers for `WorldState`."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict
from typing import TYPE_CHECKING

from townlet.console.command import (
    ConsoleCommandEnvelope,
    ConsoleCommandError,
    ConsoleCommandResult,
)
from townlet.console.service import ConsoleService

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from .grid import WorldState


class WorldConsoleController:
    """Coordinates console command handlers bound to a world instance."""

    def __init__(self, world: WorldState) -> None:
        self._world = world

    # ------------------------------------------------------------------
    # Registration helpers
    # ------------------------------------------------------------------
    def register_handlers(self, console: ConsoleService) -> None:
        console.register_handler(
            "noop", self.noop, mode="viewer", require_cmd_id=False
        )
        console.register_handler(
            "employment_status",
            self.employment_status,
            mode="viewer",
            require_cmd_id=False,
        )
        console.register_handler(
            "affordance_status",
            self.affordance_status,
            mode="viewer",
            require_cmd_id=False,
        )
        console.register_handler(
            "employment_exit",
            self.employment_exit,
            mode="admin",
            require_cmd_id=True,
        )
        console.register_handler(
            "spawn",
            self.spawn_agent,
            mode="admin",
            require_cmd_id=True,
        )
        console.register_handler(
            "teleport",
            self.teleport_agent,
            mode="admin",
            require_cmd_id=True,
        )
        console.register_handler(
            "setneed",
            self.set_need,
            mode="admin",
            require_cmd_id=True,
        )
        console.register_handler(
            "price",
            self.set_price,
            mode="admin",
            require_cmd_id=True,
        )
        console.register_handler(
            "force_chat",
            self.force_chat,
            mode="admin",
            require_cmd_id=True,
        )
        console.register_handler(
            "set_rel",
            self.set_relationship,
            mode="admin",
            require_cmd_id=True,
        )

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------
    def noop(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        world = self._world
        return ConsoleCommandResult.ok(envelope, {}, tick=world.tick)

    def employment_status(
        self, envelope: ConsoleCommandEnvelope
    ) -> ConsoleCommandResult:
        world = self._world
        metrics = world.employment_queue_snapshot()
        payload = {
            "metrics": metrics,
            "pending_agents": list(metrics.get("pending", [])),
        }
        return ConsoleCommandResult.ok(envelope, payload, tick=world.tick)

    def affordance_status(
        self, envelope: ConsoleCommandEnvelope
    ) -> ConsoleCommandResult:
        world = self._world
        runtime = world.running_affordances_snapshot()
        payload = {
            "running": {object_id: asdict(state) for object_id, state in runtime.items()},
            "running_count": len(runtime),
            "active_reservations": world.active_reservations,
        }
        return ConsoleCommandResult.ok(envelope, payload, tick=world.tick)

    def employment_exit(
        self, envelope: ConsoleCommandEnvelope
    ) -> ConsoleCommandResult:
        world = self._world
        if not envelope.args:
            raise ConsoleCommandError(
                "usage", "employment_exit <review|approve|defer> [agent_id]"
            )
        action = str(envelope.args[0])
        if action == "review":
            return ConsoleCommandResult.ok(
                envelope, world.employment_queue_snapshot(), tick=world.tick
            )
        if len(envelope.args) < 2:
            raise ConsoleCommandError(
                "usage", "employment_exit <approve|defer> <agent_id>"
            )
        agent_id = str(envelope.args[1])
        if action == "approve":
            success = world.employment_request_manual_exit(agent_id, tick=world.tick)
            return ConsoleCommandResult.ok(
                envelope,
                {"approved": bool(success), "agent_id": agent_id},
                tick=world.tick,
            )
        if action == "defer":
            success = world.employment_defer_exit(agent_id)
            return ConsoleCommandResult.ok(
                envelope,
                {"deferred": bool(success), "agent_id": agent_id},
                tick=world.tick,
            )
        raise ConsoleCommandError(
            "usage", "Unknown employment_exit action", details={"action": action}
        )

    def spawn_agent(
        self, envelope: ConsoleCommandEnvelope
    ) -> ConsoleCommandResult:
        world = self._world
        payload = envelope.kwargs.get("payload")
        if payload is None:
            payload = dict(zip(["agent_id", "position"], envelope.args))
        if not isinstance(payload, Mapping):
            raise ConsoleCommandError("invalid_args", "spawn payload must be a mapping")
        agent_id = payload.get("agent_id")
        if not isinstance(agent_id, str) or not agent_id:
            raise ConsoleCommandError("invalid_args", "spawn requires agent_id")
        if agent_id in world.agents:
            raise ConsoleCommandError(
                "conflict", "agent already exists", details={"agent_id": agent_id}
            )
        position = payload.get("position")
        if not isinstance(position, (list, tuple)) or len(position) != 2:
            raise ConsoleCommandError("invalid_args", "position must be [x, y]")
        try:
            x, y = int(position[0]), int(position[1])
        except (TypeError, ValueError) as error:
            raise ConsoleCommandError(
                "invalid_args", "position must be integers"
            ) from error
        if not world._is_position_walkable((x, y)):
            raise ConsoleCommandError(
                "invalid_args",
                "position not walkable",
                details={"position": [x, y]},
            )
        home_payload = payload.get("home_position")
        if home_payload is None:
            home_tuple = (x, y)
        else:
            if not isinstance(home_payload, (list, tuple)) or len(home_payload) != 2:
                raise ConsoleCommandError(
                    "invalid_args", "home_position must be [x, y]"
                )
            try:
                hx, hy = int(home_payload[0]), int(home_payload[1])
            except (TypeError, ValueError) as error:
                raise ConsoleCommandError(
                    "invalid_args", "home_position must be integers"
                ) from error
            home_tuple = (hx, hy)
            if home_tuple != (x, y) and not world._is_position_walkable(home_tuple):
                raise ConsoleCommandError(
                    "invalid_args",
                    "home_position not walkable",
                    details={"home_position": [hx, hy]},
                )
        needs = payload.get("needs") or {}
        if not isinstance(needs, Mapping):
            raise ConsoleCommandError("invalid_args", "needs must be a mapping")
        hunger = float(needs.get("hunger", 0.5))
        hygiene = float(needs.get("hygiene", 0.5))
        energy = float(needs.get("energy", 0.5))
        wallet = float(payload.get("wallet", 0.0))
        profile_field = payload.get("personality_profile")
        profile_name, resolved_personality = world._choose_personality_profile(
            agent_id,
            profile_field if isinstance(profile_field, str) else None,
        )

        from townlet.world.grid import AgentSnapshot  # local import to avoid cycles

        snapshot = AgentSnapshot(
            agent_id=agent_id,
            position=(x, y),
            needs={"hunger": hunger, "hygiene": hygiene, "energy": energy},
            wallet=wallet,
            home_position=home_tuple,
            personality=resolved_personality,
            personality_profile=profile_name,
        )
        world.agents[agent_id] = snapshot
        world._spatial_index.insert_agent(agent_id, snapshot.position)
        job_override = payload.get("job_id")
        if isinstance(job_override, str):
            snapshot.job_id = job_override
        world._assign_job_if_missing(snapshot)
        world._sync_agent_spawn(snapshot)
        result_payload = {
            "agent_id": agent_id,
            "position": [x, y],
            "job_id": snapshot.job_id,
            "home_position": list(home_tuple),
            "personality_profile": profile_name,
        }
        return ConsoleCommandResult.ok(envelope, result_payload, tick=world.tick)

    def teleport_agent(
        self, envelope: ConsoleCommandEnvelope
    ) -> ConsoleCommandResult:
        world = self._world
        payload = envelope.kwargs.get("payload")
        if payload is None:
            payload = dict(zip(["agent_id", "position"], envelope.args))
        if not isinstance(payload, Mapping):
            raise ConsoleCommandError("invalid_args", "teleport payload must be a mapping")
        agent_id = payload.get("agent_id")
        if not isinstance(agent_id, str) or not agent_id:
            raise ConsoleCommandError("invalid_args", "teleport requires agent_id")
        snapshot = world.agents.get(agent_id)
        if snapshot is None:
            raise ConsoleCommandError(
                "not_found", "agent not found", details={"agent_id": agent_id}
            )
        position = payload.get("position")
        if not isinstance(position, (list, tuple)) or len(position) != 2:
            raise ConsoleCommandError("invalid_args", "position must be [x, y]")
        try:
            x, y = int(position[0]), int(position[1])
        except (TypeError, ValueError) as error:
            raise ConsoleCommandError(
                "invalid_args", "position must be integers"
            ) from error
        if not world._is_position_walkable((x, y)):
            raise ConsoleCommandError(
                "invalid_args",
                "position not walkable",
                details={"position": [x, y]},
            )
        world._release_queue_membership(snapshot.agent_id)
        world._spatial_index.move_agent(snapshot.agent_id, (x, y))
        snapshot.position = (x, y)
        world._sync_reservation_for_agent(snapshot.agent_id)
        world.request_ctx_reset(agent_id)
        return ConsoleCommandResult.ok(
            envelope, {"agent_id": agent_id, "position": [x, y]}, tick=world.tick
        )

    def set_need(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        world = self._world
        payload = envelope.kwargs.get("payload")
        if payload is None:
            payload = dict(zip(["agent_id", "needs"], envelope.args))
        if not isinstance(payload, Mapping):
            raise ConsoleCommandError("invalid_args", "setneed payload must be a mapping")
        agent_id = payload.get("agent_id")
        if not isinstance(agent_id, str) or not agent_id:
            raise ConsoleCommandError("invalid_args", "setneed requires agent_id")
        snapshot = world.agents.get(agent_id)
        if snapshot is None:
            raise ConsoleCommandError(
                "not_found", "agent not found", details={"agent_id": agent_id}
            )
        needs_payload = payload.get("needs")
        if not isinstance(needs_payload, Mapping):
            raise ConsoleCommandError(
                "invalid_args", "needs must be a mapping of need names to values"
            )
        updated: dict[str, float] = {}
        for key, value in needs_payload.items():
            if key not in snapshot.needs:
                raise ConsoleCommandError(
                    "invalid_args",
                    "unknown need",
                    details={"need": key},
                )
            try:
                float_value = float(value)
            except (TypeError, ValueError) as error:
                raise ConsoleCommandError(
                    "invalid_args", "need values must be numeric", details={"need": key}
                ) from error
            clamped = max(0.0, min(1.0, float_value))
            snapshot.needs[key] = clamped
            updated[key] = clamped
        return ConsoleCommandResult.ok(
            envelope,
            {"agent_id": agent_id, "needs": updated},
            tick=world.tick,
        )

    def set_price(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        world = self._world
        payload = envelope.kwargs.get("payload")
        if payload is None:
            payload = dict(zip(["key", "value"], envelope.args))
        if not isinstance(payload, Mapping):
            raise ConsoleCommandError("invalid_args", "price payload must be a mapping")
        key = payload.get("key")
        if not isinstance(key, str) or not key:
            raise ConsoleCommandError("invalid_args", "price requires key")
        if key not in world.config.economy:
            raise ConsoleCommandError(
                "not_found", "unknown economy key", details={"key": key}
            )
        value = payload.get("value")
        try:
            numeric_value = float(value)
        except (TypeError, ValueError) as error:
            raise ConsoleCommandError(
                "invalid_args", "value must be numeric", details={"key": key}
            ) from error
        world.config.economy[key] = numeric_value
        world._economy_baseline[key] = numeric_value
        if world._price_spike_events:
            world._recompute_price_spikes()
        if key in {
            "meal_cost",
            "cook_energy_cost",
            "cook_hygiene_cost",
            "ingredients_cost",
        }:
            world._update_basket_metrics()
        result_payload = {"key": key, "value": numeric_value}
        return ConsoleCommandResult.ok(envelope, result_payload, tick=world.tick)

    def force_chat(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        world = self._world
        payload = envelope.kwargs.get("payload")
        if payload is None:
            payload = dict(zip(["speaker", "listener", "quality"], envelope.args))
        if not isinstance(payload, Mapping):
            raise ConsoleCommandError(
                "invalid_args", "force_chat payload must be a mapping"
            )
        speaker = payload.get("speaker")
        listener = payload.get("listener")
        if not isinstance(speaker, str) or not isinstance(listener, str):
            raise ConsoleCommandError(
                "invalid_args", "force_chat requires speaker and listener"
            )
        if speaker == listener:
            raise ConsoleCommandError(
                "invalid_args", "speaker and listener must differ"
            )
        if speaker not in world.agents:
            raise ConsoleCommandError(
                "not_found", "speaker not found", details={"agent_id": speaker}
            )
        if listener not in world.agents:
            raise ConsoleCommandError(
                "not_found", "listener not found", details={"agent_id": listener}
            )
        quality = payload.get("quality", 1.0)
        try:
            quality_value = float(quality)
        except (TypeError, ValueError) as error:
            raise ConsoleCommandError(
                "invalid_args", "quality must be numeric", details={"quality": quality}
            ) from error
        clipped = max(0.0, min(1.0, quality_value))
        world.record_chat_success(speaker, listener, clipped)
        tie_forward = world.relationship_tie(speaker, listener)
        tie_reverse = world.relationship_tie(listener, speaker)
        result_payload = {
            "speaker": speaker,
            "listener": listener,
            "quality": clipped,
            "speaker_tie": tie_forward.as_dict() if tie_forward else {},
            "listener_tie": tie_reverse.as_dict() if tie_reverse else {},
        }
        return ConsoleCommandResult.ok(envelope, result_payload, tick=world.tick)

    def set_relationship(
        self, envelope: ConsoleCommandEnvelope
    ) -> ConsoleCommandResult:
        world = self._world
        payload = envelope.kwargs.get("payload")
        if payload is None:
            payload = dict(
                zip(
                    ["agent_a", "agent_b", "trust", "familiarity", "rivalry"],
                    envelope.args,
                )
            )
        if not isinstance(payload, Mapping):
            raise ConsoleCommandError(
                "invalid_args", "set_rel payload must be a mapping"
            )
        agent_a = payload.get("agent_a")
        agent_b = payload.get("agent_b")
        if not isinstance(agent_a, str) or not isinstance(agent_b, str):
            raise ConsoleCommandError(
                "invalid_args", "set_rel requires agent_a and agent_b"
            )
        if agent_a == agent_b:
            raise ConsoleCommandError(
                "invalid_args", "agent_a and agent_b must differ"
            )
        if agent_a not in world.agents:
            raise ConsoleCommandError(
                "not_found", "agent_a not found", details={"agent_id": agent_a}
            )
        if agent_b not in world.agents:
            raise ConsoleCommandError(
                "not_found", "agent_b not found", details={"agent_id": agent_b}
            )
        target_trust = payload.get("trust")
        target_fam = payload.get("familiarity")
        target_rivalry = payload.get("rivalry")
        if target_trust is None and target_fam is None and target_rivalry is None:
            raise ConsoleCommandError(
                "invalid_args",
                "set_rel requires at least one of trust/familiarity/rivalry",
            )
        forward = world._get_relationship_ledger(agent_a).tie_for(agent_b)
        current_forward = (
            forward.as_dict()
            if forward
            else {"trust": 0.0, "familiarity": 0.0, "rivalry": 0.0}
        )

        def _compute_delta(
            target: object, current: float, *, clamp_low: float, clamp_high: float
        ) -> float:
            if target is None:
                return 0.0
            try:
                coerced = float(target)
            except (TypeError, ValueError) as error:
                raise ConsoleCommandError(
                    "invalid_args", "relationship values must be numeric"
                ) from error
            coerced = max(clamp_low, min(clamp_high, coerced))
            return coerced - current

        delta_trust = _compute_delta(
            target_trust, current_forward["trust"], clamp_low=-1.0, clamp_high=1.0
        )
        delta_fam = _compute_delta(
            target_fam, current_forward["familiarity"], clamp_low=-1.0, clamp_high=1.0
        )
        delta_rivalry = _compute_delta(
            target_rivalry, current_forward["rivalry"], clamp_low=0.0, clamp_high=1.0
        )

        world.update_relationship(
            agent_a,
            agent_b,
            trust=delta_trust,
            familiarity=delta_fam,
            rivalry=delta_rivalry,
            event="console_override",
        )
        forward_tie = world.relationship_tie(agent_a, agent_b)
        reverse_tie = world.relationship_tie(agent_b, agent_a)
        result_payload = {
            "agent_a": agent_a,
            "agent_b": agent_b,
            "agent_a_tie": forward_tie.as_dict() if forward_tie else {},
            "agent_b_tie": reverse_tie.as_dict() if reverse_tie else {},
        }
        return ConsoleCommandResult.ok(envelope, result_payload, tick=world.tick)


def install_world_console_handlers(
    world: WorldState, console: ConsoleService
) -> WorldConsoleController:
    """Attach default console handlers for a world instance."""

    controller = WorldConsoleController(world)
    controller.register_handlers(console)
    return controller

