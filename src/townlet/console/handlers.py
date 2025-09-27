"""Console validation scaffolding."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from townlet.config import SimulationConfig
    from townlet.scheduler.perturbations import PerturbationScheduler
    from townlet.telemetry.publisher import TelemetryPublisher
    from townlet.world.grid import WorldState

from townlet.snapshots import SnapshotManager

SUPPORTED_SCHEMA_PREFIX = "0.8"
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

    def connect(self, publisher: "TelemetryPublisher") -> None:
        publisher.register_event_subscriber(self._record)

    def _record(self, events: list[dict[str, object]]) -> None:
        self._latest = events

    def latest(self) -> list[dict[str, object]]:
        return list(self._latest)


class TelemetryBridge:
    """Provides access to the latest telemetry snapshots for console consumers."""

    def __init__(self, publisher: "TelemetryPublisher") -> None:
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
            "anneal_status": self._publisher.latest_anneal_status(),
            "policy_snapshot": self._publisher.latest_policy_snapshot(),
            "policy_identity": self._publisher.latest_policy_identity() or {},
            "snapshot_migrations": self._publisher.latest_snapshot_migrations(),
            "affordance_manifest": self._publisher.latest_affordance_manifest(),
            "reward_breakdown": self._publisher.latest_reward_breakdown(),
            "stability": {
                "alerts": self._publisher.latest_stability_alerts(),
                "metrics": self._publisher.latest_stability_metrics(),
            },
            "perturbations": self._publisher.latest_perturbations(),
        }


def create_console_router(
    publisher: "TelemetryPublisher",
    world: "WorldState" | None = None,
    scheduler: "PerturbationScheduler" | None = None,
    *,
    mode: str = "viewer",
    config: "SimulationConfig" | None = None,
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

    def _require_config() -> tuple["SimulationConfig" | None, dict[str, object] | None]:
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

    router.register("telemetry_snapshot", telemetry_handler)
    router.register("employment_status", employment_status_handler)
    router.register("employment_exit", employment_exit_handler)
    router.register("perturbation_queue", perturbation_queue_handler)
    router.register("snapshot_inspect", snapshot_inspect_handler)
    router.register("snapshot_validate", snapshot_validate_handler)
    if mode == "admin":
        router.register("perturbation_trigger", perturbation_trigger_handler)
        router.register("perturbation_cancel", perturbation_cancel_handler)
        router.register("snapshot_migrate", snapshot_migrate_handler)
    else:
        router.register("perturbation_trigger", _forbidden)
        router.register("perturbation_cancel", _forbidden)
        router.register("snapshot_migrate", _forbidden)
    return router


def _schema_metadata(publisher: "TelemetryPublisher") -> tuple[str, str | None]:
    version = publisher.schema()
    warning = None
    if not version.startswith(SUPPORTED_SCHEMA_PREFIX):
        warning = (
            "Console supports telemetry schema "
            f"{SUPPORTED_SCHEMA_PREFIX}.x; shard reported {version}. Upgrade required."
        )
    return version, warning
