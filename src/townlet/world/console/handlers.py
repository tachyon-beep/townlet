"""World console command handlers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict
from typing import TYPE_CHECKING

from townlet.console.command import (
    ConsoleCommandEnvelope,
    ConsoleCommandError,
    ConsoleCommandResult,
)

if TYPE_CHECKING:  # pragma: no cover
    from townlet.console.service import ConsoleService
    from townlet.world.grid import WorldState


class WorldConsoleController:
    def __init__(self, world: WorldState) -> None:
        self._world = world

    def register_handlers(self, console: ConsoleService) -> None:
        console.register_handler("noop", self.noop, mode="viewer")
        console.register_handler(
            "employment_status",
            self.employment_status,
            mode="viewer",
        )
        console.register_handler(
            "affordance_status",
            self.affordance_status,
            mode="viewer",
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

    def noop(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        world = self._world
        return ConsoleCommandResult.ok(envelope, {}, tick=world.tick)

    def employment_status(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        world = self._world
        metrics = world.employment_queue_snapshot()
        payload = {"metrics": metrics, "pending_agents": list(metrics.get("pending", []))}
        return ConsoleCommandResult.ok(envelope, payload, tick=world.tick)

    def affordance_status(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        world = self._world
        runtime = world.running_affordances_snapshot()
        payload = {
            "running": {object_id: asdict(state) for object_id, state in runtime.items()},
            "running_count": len(runtime),
            "active_reservations": world.active_reservations,
        }
        return ConsoleCommandResult.ok(envelope, payload, tick=world.tick)

    def employment_exit(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
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

    def spawn_agent(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
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
            if (
                home_tuple != (x, y)
                and not world.lifecycle_service.is_position_walkable(home_tuple)
            ):
                raise ConsoleCommandError(
                    "invalid_args",
                    "home_position not walkable",
                    details={"home_position": [hx, hy]},
                )
        needs_payload = payload.get("needs")
        needs = {
            "hunger": 0.5,
            "hygiene": 0.5,
            "energy": 0.5,
        }
        if isinstance(needs_payload, Mapping):
            for key, value in needs_payload.items():
                try:
                    needs[str(key)] = float(value)
                except (TypeError, ValueError) as err:
                    raise ConsoleCommandError(
                        "invalid_args",
                        "needs must be numeric",
                        details={"needs": needs_payload},
                    ) from err
        wallet = payload.get("wallet")
        try:
            wallet_value = float(wallet) if wallet is not None else None
        except (TypeError, ValueError) as error:
            raise ConsoleCommandError("invalid_args", "wallet must be numeric") from error
        try:
            snapshot = world.spawn_agent(
                agent_id=str(agent_id),
                position=(x, y),
                needs=needs,
                home_position=home_tuple,
                wallet=wallet_value,
                personality_profile=payload.get("profile")
                or payload.get("personality_profile"),
            )
        except ValueError as error:
            raise ConsoleCommandError(
                "invalid_args", str(error), details={"agent_id": agent_id, "position": [x, y]}
            ) from error
        return ConsoleCommandResult.ok(
            envelope,
            {
                "spawned": agent_id,
                "position": [x, y],
                "needs": dict(snapshot.needs),
                "wallet": snapshot.wallet,
            },
            tick=world.tick,
        )

    def teleport_agent(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        world = self._world
        payload = envelope.kwargs.get("payload")
        agent_id: str | None = None
        position: object | None = None
        if isinstance(payload, Mapping):
            agent_id = payload.get("agent_id")
            position = payload.get("position") or payload.get("destination")
        if not agent_id and envelope.args:
            agent_id = str(envelope.args[0])
            position = envelope.args[1:3]
        if not agent_id:
            raise ConsoleCommandError("usage", "teleport <agent_id> [x y]")
        agent_id = str(agent_id)
        if agent_id not in world.agents:
            raise ConsoleCommandError("not_found", "agent not found", details={"agent_id": agent_id})
        if not isinstance(position, (list, tuple)) or len(position) != 2:
            raise ConsoleCommandError("invalid_args", "teleport requires position [x, y]")
        try:
            x, y = int(position[0]), int(position[1])
        except (TypeError, ValueError) as error:
            raise ConsoleCommandError("invalid_args", "teleport requires integer x y") from error
        try:
            world.teleport_agent(agent_id, (x, y))
        except ValueError as error:
            raise ConsoleCommandError(
                "invalid_args",
                str(error),
                details={"agent_id": agent_id, "position": [x, y]},
            ) from error
        return ConsoleCommandResult.ok(
            envelope,
            {"agent_id": agent_id, "position": [x, y]},
            tick=world.tick,
        )

    def set_need(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        world = self._world
        payload = envelope.kwargs.get("payload")
        agent_id: str | None = None
        updates: Mapping[str, object] | None = None
        if isinstance(payload, Mapping):
            agent_id = payload.get("agent_id")
            if "needs" in payload:
                maybe_mapping = payload.get("needs")
                if isinstance(maybe_mapping, Mapping):
                    updates = maybe_mapping
            elif {"need", "value"} <= payload.keys():
                updates = {str(payload["need"]): payload["value"]}
        if not agent_id and envelope.args:
            agent_id = str(envelope.args[0])
            if len(envelope.args) >= 3:
                updates = {str(envelope.args[1]): envelope.args[2]}
        if not agent_id or not updates:
            raise ConsoleCommandError("usage", "setneed <agent_id> <need> <value>")
        agent_id = str(agent_id)
        snapshot = world.agents.get(agent_id)
        if snapshot is None:
            raise ConsoleCommandError("not_found", "agent not found", details={"agent_id": agent_id})
        applied: dict[str, float] = {}
        valid_needs = set(snapshot.needs.keys())
        for raw_key, raw_value in updates.items():
            key = str(raw_key)
            if key not in valid_needs:
                raise ConsoleCommandError(
                    "invalid_args",
                    "unknown need",
                    details={"need": key},
                )
            try:
                numeric = float(raw_value)
            except (TypeError, ValueError) as error:
                raise ConsoleCommandError(
                    "invalid_args",
                    "value must be numeric",
                    details={"need": key},
                ) from error
            clamped = max(0.0, min(1.0, numeric))
            snapshot.needs[key] = clamped
            applied[key] = clamped
        world.request_ctx_reset(agent_id)
        return ConsoleCommandResult.ok(
            envelope,
            {"agent_id": agent_id, "needs": applied},
            tick=world.tick,
        )

    def set_price(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        world = self._world
        payload = envelope.kwargs.get("payload")
        key: str | None = None
        value: object | None = None
        if isinstance(payload, Mapping):
            key = payload.get("key") or payload.get("item")
            value = payload.get("value")
        if key is None and envelope.args:
            key = str(envelope.args[0])
            if len(envelope.args) >= 2:
                value = envelope.args[1]
        if key is None or value is None:
            raise ConsoleCommandError("usage", "price <item> <value>")
        key = str(key)
        try:
            numeric = float(value)
        except (TypeError, ValueError) as error:
            raise ConsoleCommandError("invalid_args", "value must be numeric") from error
        try:
            updated = world.set_price_target(key, numeric)
        except KeyError as error:
            raise ConsoleCommandError(
                "not_found", "unknown price target", details={"item": key}
            ) from error
        return ConsoleCommandResult.ok(
            envelope,
            {"item": key, "value": updated},
            tick=world.tick,
        )

    def force_chat(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        world = self._world
        payload = envelope.kwargs.get("payload")
        speaker: str | None = None
        listener: str | None = None
        quality_obj: object | None = None
        if isinstance(payload, Mapping):
            speaker = payload.get("speaker")
            listener = payload.get("listener")
            quality_obj = payload.get("quality")
        if speaker is None and envelope.args:
            speaker = str(envelope.args[0])
            if len(envelope.args) >= 2:
                listener = str(envelope.args[1])
            if len(envelope.args) >= 3:
                quality_obj = envelope.args[2]
        if speaker is None or listener is None:
            raise ConsoleCommandError("usage", "force_chat <speaker> <listener>")
        speaker = str(speaker)
        listener = str(listener)
        if speaker == listener:
            raise ConsoleCommandError("invalid_args", "speaker and listener must differ")
        if speaker not in world.agents:
            raise ConsoleCommandError(
                "not_found", "speaker not found", details={"agent_id": speaker}
            )
        if listener not in world.agents:
            raise ConsoleCommandError(
                "not_found", "listener not found", details={"agent_id": listener}
            )
        if quality_obj is None:
            quality = 1.0
        else:
            try:
                quality = float(quality_obj)
            except (TypeError, ValueError) as error:
                raise ConsoleCommandError(
                    "invalid_args", "quality must be numeric"
                ) from error
        quality = max(0.0, min(1.0, quality))
        world.record_chat_success(speaker, listener, quality)
        tie_a = world.relationship_tie(speaker, listener)
        tie_b = world.relationship_tie(listener, speaker)
        return ConsoleCommandResult.ok(
            envelope,
            {
                "speaker": speaker,
                "listener": listener,
                "quality": quality,
                "speaker_tie": asdict(tie_a) if tie_a else None,
                "listener_tie": asdict(tie_b) if tie_b else None,
            },
            tick=world.tick,
        )

    def set_relationship(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult:
        world = self._world
        payload = envelope.kwargs.get("payload")
        agent_a: str | None = None
        agent_b: str | None = None
        trust_obj: object | None = None
        familiarity_obj: object | None = None
        rivalry_obj: object | None = None
        if isinstance(payload, Mapping):
            agent_a = payload.get("agent_a")
            agent_b = payload.get("agent_b")
            trust_obj = payload.get("trust")
            familiarity_obj = payload.get("familiarity")
            rivalry_obj = payload.get("rivalry")
        if agent_a is None and envelope.args:
            agent_a = str(envelope.args[0])
            if len(envelope.args) >= 2:
                agent_b = str(envelope.args[1])
            if len(envelope.args) >= 3:
                trust_obj = envelope.args[2]
        if agent_a is None or agent_b is None or trust_obj is None:
            raise ConsoleCommandError(
                "usage", "set_rel <agent_a> <agent_b> <trust> [familiarity] [rivalry]"
            )
        agent_a = str(agent_a)
        agent_b = str(agent_b)
        if agent_a not in world.agents or agent_b not in world.agents:
            missing = agent_a if agent_a not in world.agents else agent_b
            raise ConsoleCommandError(
                "not_found", "agent not found", details={"agent_id": missing}
            )
        try:
            trust = float(trust_obj)
        except (TypeError, ValueError) as error:
            raise ConsoleCommandError("invalid_args", "trust must be numeric") from error
        familiarity = 0.0
        rivalry = 0.0
        if familiarity_obj is not None:
            try:
                familiarity = float(familiarity_obj)
            except (TypeError, ValueError) as error:
                raise ConsoleCommandError("invalid_args", "familiarity must be numeric") from error
        if rivalry_obj is not None:
            try:
                rivalry = float(rivalry_obj)
            except (TypeError, ValueError) as error:
                raise ConsoleCommandError("invalid_args", "rivalry must be numeric") from error
        world.set_relationship(
            agent_a,
            agent_b,
            trust=trust,
            familiarity=familiarity,
            rivalry=rivalry,
        )
        tie_ab = world.relationship_tie(agent_a, agent_b)
        tie_ba = world.relationship_tie(agent_b, agent_a)
        return ConsoleCommandResult.ok(
            envelope,
            {
                "agent_a": agent_a,
                "agent_b": agent_b,
                "trust": trust,
                "familiarity": familiarity,
                "rivalry": rivalry,
                "agent_a_tie": asdict(tie_ab) if tie_ab else None,
                "agent_b_tie": asdict(tie_ba) if tie_ba else None,
            },
            tick=world.tick,
        )


def install_world_console_handlers(world: WorldState, console: ConsoleService) -> WorldConsoleController:
    controller = WorldConsoleController(world)
    controller.register_handlers(console)
    return controller
