"""Console validation scaffolding."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Mapping, Protocol

if TYPE_CHECKING:
    from townlet.config import SimulationConfig
    from townlet.policy.runner import PolicyRuntime
    from townlet.scheduler.perturbations import PerturbationScheduler
    from townlet.telemetry.publisher import TelemetryPublisher
    from townlet.world.grid import WorldState
    from townlet.lifecycle.manager import LifecycleManager

from townlet.snapshots import SnapshotManager
from townlet.stability.promotion import PromotionManager

SUPPORTED_SCHEMA_PREFIX = "0.9"
SUPPORTED_SCHEMA_LABEL = f"{SUPPORTED_SCHEMA_PREFIX}.x"


@dataclass
class ConsoleCommand:
    """Represents a parsed console command ready for execution."""

    name: str
    args: tuple[object, ...]
    kwargs: dict[str, object]


class ConsoleHandler(Protocol):
    def __call__(self, command: ConsoleCommand) -> object: ...


class ConsoleRouter:
    """Routes validated commands to subsystem handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, ConsoleHandler] = {}

    def register(self, name: str, handler: ConsoleHandler) -> None:
        self._handlers[name] = handler

    def dispatch(self, command: ConsoleCommand) -> object:
        handler = self._handlers.get(command.name)
        if handler is None:
            raise KeyError(f"Unknown console command: {command.name}")
        return handler(command)


class EventStream:
    """Simple subscriber that records the latest simulation events."""

    def __init__(self) -> None:
        self._latest: list[dict[str, object]] = []

    def connect(self, publisher: TelemetryPublisher) -> None:
        publisher.register_event_subscriber(self._record)

    def _record(self, events: list[dict[str, object]]) -> None:
        self._latest = events

    def latest(self) -> list[dict[str, object]]:
        return list(self._latest)


class TelemetryBridge:
    """Provides access to the latest telemetry snapshots for console consumers."""

    def __init__(self, publisher: TelemetryPublisher) -> None:
        self._publisher = publisher

    def snapshot(self) -> dict[str, dict[str, object]]:
        version, warning = _schema_metadata(self._publisher)
        return {
            "schema_version": version,
            "schema_warning": warning,
            "jobs": self._publisher.latest_job_snapshot(),
            "economy": self._publisher.latest_economy_snapshot(),
            "employment": self._publisher.latest_employment_metrics(),
            "conflict": self._publisher.latest_conflict_snapshot(),
            "relationships": self._publisher.latest_relationship_metrics() or {},
            "relationship_snapshot": self._publisher.latest_relationship_snapshot(),
            "relationship_updates": self._publisher.latest_relationship_updates(),
            "events": list(self._publisher.latest_events()),
            "narrations": self._publisher.latest_narrations(),
            "narration_state": self._publisher.latest_narration_state(),
            "anneal_status": self._publisher.latest_anneal_status(),
            "policy_snapshot": self._publisher.latest_policy_snapshot(),
            "policy_identity": self._publisher.latest_policy_identity() or {},
            "snapshot_migrations": self._publisher.latest_snapshot_migrations(),
            "affordance_manifest": self._publisher.latest_affordance_manifest(),
            "reward_breakdown": self._publisher.latest_reward_breakdown(),
            "stability": {
                "alerts": self._publisher.latest_stability_alerts(),
                "metrics": self._publisher.latest_stability_metrics(),
                "promotion_state": getattr(
                    self._publisher, "latest_promotion_state", lambda: None
                )(),
            },
            "perturbations": self._publisher.latest_perturbations(),
            "transport": self._publisher.latest_transport_status(),
            "console_results": self._publisher.latest_console_results(),
            "possessed_agents": self._publisher.latest_possessed_agents(),
            "precondition_failures": self._publisher.latest_precondition_failures(),
        }


def create_console_router(
    publisher: TelemetryPublisher,
    world: WorldState | None = None,
    scheduler: PerturbationScheduler | None = None,
    promotion: PromotionManager | None = None,
    *,
    policy: PolicyRuntime | None = None,
    mode: str = "viewer",
    config: SimulationConfig | None = None,
    lifecycle: "LifecycleManager" | None = None,
) -> ConsoleRouter:
    router = ConsoleRouter()
    if config is not None:
        config.register_snapshot_migrations()
    bridge = TelemetryBridge(publisher)

    def _forbidden(_: ConsoleCommand) -> object:
        return {
            "error": "forbidden",
            "message": "command requires admin mode",
        }

    def _attach_metadata(result: dict[str, object], command: ConsoleCommand) -> dict[str, object]:
        cmd_id = command.kwargs.get("cmd_id")
        if cmd_id is not None:
            result["cmd_id"] = cmd_id
        issuer = command.kwargs.get("issuer")
        if issuer is not None:
            result["issuer"] = issuer
        return result

    def _refresh_promotion_metrics() -> None:
        if promotion is None:
            return
        metrics = publisher.latest_stability_metrics()
        base = dict(metrics) if isinstance(metrics, dict) else {}
        base["promotion_state"] = promotion.snapshot()
        publisher.record_stability_metrics(base)

    def _apply_release_metadata(metadata: object) -> None:
        if policy is None and config is None:
            return
        metadata_dict: dict[str, object] = {}
        if isinstance(metadata, dict):
            metadata_dict = metadata
        policy_hash_value = metadata_dict.get("policy_hash")
        active_hash: str | None = None
        anneal_ratio: float | None = None
        if policy is not None:
            if policy_hash_value is not None:
                policy.set_policy_hash(str(policy_hash_value))
            else:
                policy.set_policy_hash(None)
            active_hash = policy.active_policy_hash()
            try:
                anneal_ratio = policy.current_anneal_ratio()
            except Exception:  # pragma: no cover - defensive
                anneal_ratio = None
        elif policy_hash_value is not None:
            active_hash = str(policy_hash_value)
        if config is not None:
            identity = config.build_snapshot_identity(
                policy_hash=active_hash,
                runtime_observation_variant=config.observation_variant,
                runtime_anneal_ratio=anneal_ratio,
            )
            publisher.update_policy_identity(identity)

    def _parse_snapshot_path(
        command: ConsoleCommand, usage: str
    ) -> tuple[Path | None, dict[str, object] | None]:
        path_arg = command.kwargs.get("path")
        if path_arg is None and command.args:
            path_arg = command.args[0]
        if path_arg is None:
            return None, {"error": "usage", "message": usage}
        try:
            path = Path(str(path_arg)).expanduser()
            path = path.resolve()
        except Exception as exc:  # pragma: no cover - defensive
            return None, {
                "error": "invalid_path",
                "message": str(exc),
            }
        if not path.exists():
            return None, {"error": "not_found", "path": str(path)}
        if path.is_dir():
            return None, {
                "error": "invalid_path",
                "message": "snapshot path must reference a file",
            }
        return path, None

    def _require_config() -> tuple[SimulationConfig | None, dict[str, object] | None]:
        if config is None:
            return None, {
                "error": "unsupported",
                "message": "snapshot command requires simulation config",
            }
        return config, None

    def telemetry_handler(command: ConsoleCommand) -> object:
        return bridge.snapshot()

    def employment_status_handler(command: ConsoleCommand) -> object:
        version, warning = _schema_metadata(publisher)
        metrics = publisher.latest_employment_metrics()
        return {
            "schema_version": version,
            "schema_warning": warning,
            "metrics": metrics,
            "pending_agents": metrics.get("pending", []),
        }

    def employment_exit_handler(command: ConsoleCommand) -> object:
        if world is None:
            raise RuntimeError("employment_exit requires world access")
        if not command.args:
            return {
                "error": "usage",
                "message": "employment_exit <approve|defer|review> [agent_id]",
            }
        action = str(command.args[0])
        if action == "review":
            return world.employment_queue_snapshot()
        if len(command.args) < 2:
            return {"error": "missing_agent_id"}
        agent_id = str(command.args[1])
        if action == "approve":
            success = world.employment_request_manual_exit(agent_id, tick=world.tick)
            return {"approved": success, "agent_id": agent_id}
        if action == "defer":
            success = world.employment_defer_exit(agent_id)
            return {"deferred": success, "agent_id": agent_id}
        return {"error": "unknown_action", "action": action}

    def possess_handler(command: ConsoleCommand) -> object:
        if policy is None:
            return {"error": "unsupported"}
        payload = command.kwargs.get("payload")
        agent_id: str | None = None
        action = command.kwargs.get("action") if isinstance(command.kwargs.get("action"), str) else None
        if isinstance(payload, Mapping):
            candidate = payload.get("agent_id")
            if isinstance(candidate, str):
                agent_id = candidate
            if isinstance(payload.get("action"), str):
                action = payload["action"]
        if agent_id is None and command.args:
            first = command.args[0]
            if isinstance(first, str):
                agent_id = first
        if agent_id is None or not agent_id:
            return {
                "error": "usage",
                "message": "possess requires agent_id",
            }
        if world is not None and agent_id not in world.agents:
            return {"error": "not_found", "agent_id": agent_id}
        verb = str(action or "acquire").lower()
        if verb not in {"acquire", "release"}:
            return {
                "error": "invalid_args",
                "message": "action must be 'acquire' or 'release'",
            }
        if verb == "acquire":
            if not policy.acquire_possession(agent_id):
                return {
                    "error": "conflict",
                    "message": "agent already possessed",
                    "agent_id": agent_id,
                }
            possessed = True
        else:
            if not policy.release_possession(agent_id):
                return {
                    "error": "invalid_args",
                    "message": "agent not currently possessed",
                    "agent_id": agent_id,
                }
            possessed = False
        return {
            "agent_id": agent_id,
            "possessed": possessed,
            "possessed_agents": policy.possessed_agents(),
        }

    def kill_handler(command: ConsoleCommand) -> object:
        if world is None:
            return {"error": "unsupported"}
        payload = command.kwargs.get("payload")
        agent_id: str | None = None
        reason: str | None = None
        if isinstance(payload, Mapping):
            candidate = payload.get("agent_id")
            if isinstance(candidate, str):
                agent_id = candidate
            if isinstance(payload.get("reason"), str):
                reason = payload["reason"]
        if agent_id is None and command.args:
            first = command.args[0]
            if isinstance(first, str):
                agent_id = first
        if agent_id is None or not agent_id:
            return {
                "error": "usage",
                "message": "kill requires agent_id",
            }
        if not world.kill_agent(agent_id, reason=reason):
            return {"error": "not_found", "agent_id": agent_id}
        return {
            "agent_id": agent_id,
            "killed": True,
            "reason": reason,
        }

    def toggle_mortality_handler(command: ConsoleCommand) -> object:
        if lifecycle is None:
            return {"error": "unsupported"}
        payload = command.kwargs.get("payload")
        value = command.kwargs.get("enabled") if isinstance(command.kwargs.get("enabled"), bool) else None
        if isinstance(payload, Mapping) and "enabled" in payload:
            candidate = payload.get("enabled")
            if isinstance(candidate, bool):
                value = candidate
        if value is None:
            return {
                "error": "usage",
                "message": "toggle_mortality requires enabled bool",
            }
        lifecycle.set_mortality_enabled(bool(value))
        return {"enabled": lifecycle.mortality_enabled}

    def set_exit_cap_handler(command: ConsoleCommand) -> object:
        if world is None:
            return {"error": "unsupported"}
        payload = command.kwargs.get("payload")
        cap_value = command.kwargs.get("daily_exit_cap") if isinstance(command.kwargs.get("daily_exit_cap"), int) else None
        if isinstance(payload, Mapping) and "daily_exit_cap" in payload:
            candidate = payload.get("daily_exit_cap")
            if isinstance(candidate, int):
                cap_value = candidate
        if cap_value is None:
            return {
                "error": "usage",
                "message": "set_exit_cap requires daily_exit_cap integer",
            }
        if cap_value < 0:
            return {
                "error": "invalid_args",
                "message": "daily_exit_cap must be >= 0",
            }
        world.config.employment.daily_exit_cap = cap_value
        metrics = world.employment_queue_snapshot()
        return {
            "daily_exit_cap": cap_value,
            "metrics": metrics,
        }

    def conflict_status_handler(command: ConsoleCommand) -> object:
        version, warning = _schema_metadata(publisher)
        try:
            history_limit = int(command.kwargs.get("history", 10))
        except (TypeError, ValueError):
            history_limit = 10
        try:
            rivalry_limit = int(command.kwargs.get("rivalries", 10))
        except (TypeError, ValueError):
            rivalry_limit = 10
        queue_history = publisher.latest_queue_history()
        if history_limit > 0:
            queue_history = queue_history[-history_limit:]
        rivalry_events = publisher.latest_rivalry_events()
        if rivalry_limit > 0:
            rivalry_events = rivalry_events[-rivalry_limit:]
        return {
            "schema_version": version,
            "schema_warning": warning,
            "queue_metrics": publisher.latest_queue_metrics() or {},
            "conflict": publisher.latest_conflict_snapshot(),
            "history": queue_history,
            "rivalry_events": rivalry_events,
            "stability_alerts": publisher.latest_stability_alerts(),
            "stability_metrics": publisher.latest_stability_metrics(),
        }

    def queue_inspect_handler(command: ConsoleCommand) -> object:
        if world is None:
            return {"error": "unsupported"}
        if not command.args:
            return {
                "error": "usage",
                "message": "queue_inspect <object_id>",
            }
        object_id = str(command.args[0])
        state = world.queue_manager.export_state()
        queues = state.get("queues", {})
        entries = [
            {
                "agent_id": str(entry.get("agent_id", "")),
                "joined_tick": int(entry.get("joined_tick", 0)),
            }
            for entry in queues.get(object_id, [])
        ]
        cooldowns = []
        for item in state.get("cooldowns", []):
            if str(item.get("object_id")) != object_id:
                continue
            expiry = int(item.get("expiry", 0))
            cooldowns.append(
                {
                    "agent_id": str(item.get("agent_id", "")),
                    "expiry_tick": expiry,
                    "ticks_remaining": max(0, expiry - world.tick),
                }
            )
        stall_counts = state.get("stall_counts", {})
        return {
            "object_id": object_id,
            "tick": world.tick,
            "active": world.queue_manager.active_agent(object_id),
            "queue": entries,
            "cooldowns": cooldowns,
            "stall_count": int(stall_counts.get(object_id, 0)),
            "metrics": publisher.latest_queue_metrics() or {},
        }

    def rivalry_dump_handler(command: ConsoleCommand) -> object:
        if world is None:
            return {"error": "unsupported"}
        snapshot_getter = getattr(world, "rivalry_snapshot", None)
        if not callable(snapshot_getter):
            return {"error": "unsupported"}
        ledger = snapshot_getter() or {}
        try:
            limit = int(command.kwargs.get("limit", 5))
        except (TypeError, ValueError):
            limit = 5
        if command.args:
            agent_id = str(command.args[0])
            rivals = ledger.get(agent_id, {}) or {}
            sorted_rivals = sorted(
                ((other, float(value)) for other, value in rivals.items()),
                key=lambda item: item[1],
                reverse=True,
            )
            if limit > 0:
                sorted_rivals = sorted_rivals[:limit]
            return {
                "agent_id": agent_id,
                "rivals": [
                    {"agent_id": other, "intensity": intensity}
                    for other, intensity in sorted_rivals
                ],
            }
        edges: list[tuple[str, str, float]] = []
        for owner, rivals in ledger.items():
            for other, value in (rivals or {}).items():
                if owner >= other:
                    continue
                edges.append((owner, other, float(value)))
        edges.sort(key=lambda item: item[2], reverse=True)
        if limit > 0:
            edges = edges[:limit]
        return {
            "pairs": [
                {"agent_a": a, "agent_b": b, "intensity": intensity}
                for a, b, intensity in edges
            ],
            "agent_count": len(ledger),
        }

    def promotion_status_handler(command: ConsoleCommand) -> object:
        if promotion is None:
            return _attach_metadata({"error": "unsupported"}, command)
        result = {"promotion": promotion.snapshot()}
        return _attach_metadata(result, command)

    def promote_policy_handler(command: ConsoleCommand) -> object:
        if promotion is None:
            return _attach_metadata({"error": "unsupported"}, command)
        if not promotion.candidate_ready:
            return _attach_metadata(
                {"error": "promotion_not_ready", "promotion": promotion.snapshot()},
                command,
            )
        checkpoint_arg = command.kwargs.get("checkpoint")
        if checkpoint_arg is None and command.args:
            checkpoint_arg = command.args[0]
        if checkpoint_arg is None:
            return _attach_metadata(
                {
                    "error": "usage",
                    "message": "promote_policy <checkpoint> [--policy-hash HASH]",
                },
                command,
            )
        try:
            checkpoint_path = Path(str(checkpoint_arg)).expanduser().resolve()
        except Exception as exc:  # pragma: no cover - defensive
            return _attach_metadata({"error": "invalid_path", "message": str(exc)}, command)
        metadata: dict[str, object] = {"checkpoint": str(checkpoint_path)}
        policy_hash = command.kwargs.get("policy_hash")
        if policy_hash is not None:
            metadata["policy_hash"] = str(policy_hash)
        promotion.set_candidate_metadata(metadata)
        promotion.mark_promoted(tick=getattr(world, "tick", 0), metadata=metadata)
        snapshot = promotion.snapshot()
        _refresh_promotion_metrics()
        _apply_release_metadata(snapshot.get("current_release"))
        return _attach_metadata({"promoted": True, "promotion": snapshot}, command)

    def rollback_policy_handler(command: ConsoleCommand) -> object:
        if promotion is None:
            return _attach_metadata({"error": "unsupported"}, command)
        metadata: dict[str, object] = {}
        checkpoint_arg = command.kwargs.get("checkpoint")
        if checkpoint_arg is not None:
            try:
                checkpoint_path = Path(str(checkpoint_arg)).expanduser().resolve()
                metadata["checkpoint"] = str(checkpoint_path)
            except Exception as exc:  # pragma: no cover - defensive
                return _attach_metadata({"error": "invalid_path", "message": str(exc)}, command)
        reason = command.kwargs.get("reason")
        if reason is not None:
            metadata["reason"] = str(reason)
        promotion.register_rollback(tick=getattr(world, "tick", 0), metadata=metadata)
        promotion.set_candidate_metadata(None)
        snapshot = promotion.snapshot()
        _refresh_promotion_metrics()
        _apply_release_metadata(snapshot.get("current_release"))
        return _attach_metadata({"rolled_back": True, "promotion": snapshot}, command)

    def arrange_meet_handler(command: ConsoleCommand) -> object:
        if scheduler is None or world is None:
            return {"error": "unsupported"}
        payload = command.kwargs.get("payload")
        if payload is None and command.args:
            payload = command.args[0]
        if not isinstance(payload, Mapping):
            return {"error": "invalid_args", "message": "payload must be a mapping"}
        spec = payload.get("spec")
        if not isinstance(spec, str) or not spec:
            return {"error": "invalid_args", "message": "spec is required"}
        agents = payload.get("agents")
        if not isinstance(agents, list) or not agents:
            return {"error": "invalid_args", "message": "agents list required"}
        agent_ids = [str(agent) for agent in agents]
        missing = [agent for agent in agent_ids if agent not in world.agents]
        if missing:
            return {
                "error": "not_found",
                "message": "agents missing",
                "agents": missing,
            }
        starts_in = int(payload.get("starts_in", 0) or 0)
        duration = payload.get("duration")
        duration_int = int(duration) if duration is not None else None
        overrides = dict(payload.get("payload", {})) if isinstance(payload.get("payload"), Mapping) else None
        try:
            event = scheduler.schedule_manual(
                world,
                spec_name=spec,
                current_tick=world.tick,
                starts_in=starts_in,
                duration=duration_int,
                targets=agent_ids,
                payload_overrides=overrides,
            )
        except KeyError:
            return {"error": "unknown_spec", "spec": spec}
        except ValueError as exc:
            return {"error": "invalid_args", "message": str(exc)}
        return {
            "event_id": event.event_id,
            "spec": spec,
            "starts_at": event.started_at,
            "ends_at": event.ends_at,
            "targets": agent_ids,
        }

    def perturbation_queue_handler(command: ConsoleCommand) -> object:
        if scheduler is None:
            return {"error": "unsupported"}
        return scheduler.latest_state()

    def perturbation_trigger_handler(command: ConsoleCommand) -> object:
        if scheduler is None or world is None:
            return {"error": "unsupported"}
        if not command.args:
            return {
                "error": "usage",
                "message": (
                    "perturbation_trigger <spec> [--starts_in ticks] [--duration ticks] "
                    "[--targets a,b] [--magnitude value] [--location place]"
                ),
            }
        spec_name = str(command.args[0])
        starts_in = int(command.kwargs.get("starts_in", 0))
        duration_arg = command.kwargs.get("duration")
        duration = int(duration_arg) if duration_arg is not None else None
        targets_arg = command.kwargs.get("targets")
        targets = None
        if isinstance(targets_arg, str):
            targets = [item.strip() for item in targets_arg.split(",") if item.strip()]
        elif isinstance(targets_arg, (list, tuple)):
            targets = [str(item) for item in targets_arg]
        payload: dict[str, object] = {}
        if "magnitude" in command.kwargs:
            try:
                payload["magnitude"] = float(command.kwargs["magnitude"])
            except (TypeError, ValueError):
                return {"error": "invalid_args", "message": "magnitude must be numeric"}
        if "location" in command.kwargs:
            payload["location"] = str(command.kwargs["location"])
        try:
            event = scheduler.schedule_manual(
                world,
                spec_name=spec_name,
                current_tick=world.tick,
                starts_in=starts_in,
                duration=duration,
                targets=targets,
                payload_overrides=payload or None,
            )
        except KeyError:
            return {"error": "unknown_spec", "spec": spec_name}
        except ValueError as exc:
            return {"error": "invalid_args", "message": str(exc)}
        return {"enqueued": True, "event": scheduler.serialize_event(event)}

    def perturbation_cancel_handler(command: ConsoleCommand) -> object:
        if scheduler is None or world is None:
            return {"error": "unsupported"}
        if not command.args:
            return {
                "error": "usage",
                "message": "perturbation_cancel <event_id>",
            }
        event_id = str(command.args[0])
        cancelled = scheduler.cancel_event(world, event_id)
        return {"cancelled": cancelled, "event_id": event_id}

    def snapshot_inspect_handler(command: ConsoleCommand) -> object:
        path, error = _parse_snapshot_path(command, "snapshot_inspect <path>")
        if error:
            return error
        try:
            document = json.loads(path.read_text())
        except Exception as exc:
            return {"error": "read_failed", "message": str(exc), "path": str(path)}
        state_payload = document.get("state")
        if not isinstance(state_payload, dict):
            state_payload = {}
        return {
            "path": str(path),
            "schema_version": document.get("schema_version"),
            "config_id": state_payload.get("config_id"),
            "tick": state_payload.get("tick"),
            "identity": state_payload.get("identity", {}),
            "migrations": state_payload.get("migrations", {}),
        }

    def snapshot_validate_handler(command: ConsoleCommand) -> object:
        path, error = _parse_snapshot_path(
            command, "snapshot_validate <path> [--strict]"
        )
        if error:
            return error
        cfg, cfg_error = _require_config()
        if cfg_error:
            return cfg_error
        manager = SnapshotManager(path.parent)
        strict = bool(command.kwargs.get("strict", False))
        allow_migration = (not strict) and cfg.snapshot.migrations.auto_apply
        try:
            state = manager.load(
                path,
                cfg,
                allow_migration=allow_migration,
                allow_downgrade=cfg.snapshot.guardrails.allow_downgrade,
                require_exact_config=cfg.snapshot.guardrails.require_exact_config,
            )
        except ValueError as exc:
            return {"valid": False, "error": str(exc), "path": str(path)}
        return {
            "valid": True,
            "config_id": state.config_id,
            "tick": state.tick,
            "migrations_applied": list(state.migrations.get("applied", [])),
        }

    def snapshot_migrate_handler(command: ConsoleCommand) -> object:
        path, error = _parse_snapshot_path(
            command, "snapshot_migrate <path> [--output dir]"
        )
        if error:
            return error
        cfg, cfg_error = _require_config()
        if cfg_error:
            return cfg_error
        manager = SnapshotManager(path.parent)
        try:
            state = manager.load(
                path,
                cfg,
                allow_migration=True,
                allow_downgrade=cfg.snapshot.guardrails.allow_downgrade,
                require_exact_config=cfg.snapshot.guardrails.require_exact_config,
            )
        except ValueError as exc:
            return {
                "error": "migration_failed",
                "message": str(exc),
                "path": str(path),
            }
        applied = list(state.migrations.get("applied", []))
        publisher.record_snapshot_migrations(applied)
        output_arg = command.kwargs.get("output")
        saved_path: Path | None = None
        if output_arg is not None:
            output_dir = Path(str(output_arg)).expanduser()
            if output_dir.suffix:
                return {
                    "error": "invalid_args",
                    "message": "output must be a directory path",
                }
            output_dir.mkdir(parents=True, exist_ok=True)
            out_manager = SnapshotManager(output_dir)
            saved_path = out_manager.save(state)
        result = {
            "migrated": True,
            "config_id": state.config_id,
            "tick": state.tick,
            "migrations_applied": applied,
        }
        if saved_path is not None:
            result["output_path"] = str(saved_path)
        return result

    router.register("conflict_status", conflict_status_handler)
    router.register("queue_inspect", queue_inspect_handler)
    router.register("rivalry_dump", rivalry_dump_handler)
    router.register("telemetry_snapshot", telemetry_handler)
    router.register("employment_status", employment_status_handler)
    router.register("employment_exit", employment_exit_handler)
    router.register("promotion_status", promotion_status_handler)
    router.register("arrange_meet", arrange_meet_handler)
    router.register("perturbation_queue", perturbation_queue_handler)
    router.register("snapshot_inspect", snapshot_inspect_handler)
    router.register("snapshot_validate", snapshot_validate_handler)
    if mode == "admin":
        router.register("possess", possess_handler)
        router.register("kill", kill_handler)
        router.register("toggle_mortality", toggle_mortality_handler)
        router.register("set_exit_cap", set_exit_cap_handler)
        router.register("perturbation_trigger", perturbation_trigger_handler)
        router.register("perturbation_cancel", perturbation_cancel_handler)
        router.register("snapshot_migrate", snapshot_migrate_handler)
        router.register("promote_policy", promote_policy_handler)
        router.register("rollback_policy", rollback_policy_handler)
    else:
        router.register("possess", _forbidden)
        router.register("kill", _forbidden)
        router.register("toggle_mortality", _forbidden)
        router.register("set_exit_cap", _forbidden)
        router.register("perturbation_trigger", _forbidden)
        router.register("perturbation_cancel", _forbidden)
        router.register("snapshot_migrate", _forbidden)
        router.register("promote_policy", _forbidden)
        router.register("rollback_policy", _forbidden)
    return router


def _schema_metadata(publisher: TelemetryPublisher) -> tuple[str, str | None]:
    version = publisher.schema()
    warning = None
    if not version.startswith(SUPPORTED_SCHEMA_PREFIX):
        warning = (
            "Console supports telemetry schema "
            f"{SUPPORTED_SCHEMA_PREFIX}.x; shard reported {version}. Upgrade required."
        )
    return version, warning
