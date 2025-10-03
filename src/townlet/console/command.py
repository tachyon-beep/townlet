"""Console command envelope and result helpers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

_VALID_MODES = {"viewer", "admin"}


class ConsoleCommandError(RuntimeError):
    """Raised by handlers when a command should return an error response."""

    def __init__(self, code: str, message: str, *, details: Mapping[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = dict(details) if details is not None else None


@dataclass(frozen=True)
class ConsoleCommandEnvelope:
    """Normalised representation of an incoming console command payload."""

    name: str
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)
    cmd_id: str | None = None
    issuer: str | None = None
    mode: str = "viewer"
    timestamp_ms: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    raw: Mapping[str, Any] | None = None

    @classmethod
    def from_payload(cls, payload: object) -> "ConsoleCommandEnvelope":
        """Parse a payload emitted by the console transport."""

        if hasattr(payload, "__dict__") and not isinstance(payload, Mapping):
            mapping: Mapping[str, Any] = {
                "name": getattr(payload, "name", None),
                "args": getattr(payload, "args", ()),
                "kwargs": getattr(payload, "kwargs", {}),
                "cmd_id": getattr(payload, "cmd_id", None),
                "issuer": getattr(payload, "issuer", None),
                "mode": getattr(payload, "mode", "viewer"),
                "timestamp": getattr(payload, "timestamp", None),
                "metadata": getattr(payload, "metadata", {}),
            }
        elif isinstance(payload, Mapping):
            mapping = payload
        else:
            raise ConsoleCommandError("usage", "console command payload must be a mapping")

        name = mapping.get("name") or mapping.get("cmd")
        if not isinstance(name, str) or not name:
            raise ConsoleCommandError("usage", "console command missing 'name'")

        raw_args = mapping.get("args", [])
        if raw_args is None:
            args: list[Any] = []
        elif isinstance(raw_args, (list, tuple)):
            args = list(raw_args)
        else:
            raise ConsoleCommandError("usage", "console command 'args' must be a list")

        raw_kwargs = mapping.get("kwargs", {})
        if raw_kwargs is None:
            kwargs: dict[str, Any] = {}
        elif isinstance(raw_kwargs, Mapping):
            kwargs = {str(key): value for key, value in raw_kwargs.items()}
        else:
            raise ConsoleCommandError("usage", "console command 'kwargs' must be a mapping")

        cmd_id = mapping.get("cmd_id")
        if cmd_id is not None and not isinstance(cmd_id, str):
            raise ConsoleCommandError("usage", "console command 'cmd_id' must be a string")

        issuer = mapping.get("issuer")
        if issuer is not None and not isinstance(issuer, str):
            raise ConsoleCommandError("usage", "console command 'issuer' must be a string")

        mode_value = mapping.get("mode", "viewer")
        if not isinstance(mode_value, str):
            mode = "viewer"
        else:
            lowered = mode_value.lower()
            mode = lowered if lowered in _VALID_MODES else "viewer"

        timestamp_raw = mapping.get("timestamp_ms")
        if timestamp_raw is None:
            timestamp_raw = mapping.get("timestamp")
        if timestamp_raw is not None and not isinstance(timestamp_raw, int):
            raise ConsoleCommandError("usage", "console command timestamp must be integer milliseconds")

        meta = mapping.get("metadata", {})
        if meta is None:
            metadata: dict[str, Any] = {}
        elif isinstance(meta, Mapping):
            metadata = {str(key): value for key, value in meta.items()}
        else:
            raise ConsoleCommandError("usage", "console command metadata must be a mapping")

        return cls(
            name=name,
            args=args,
            kwargs=kwargs,
            cmd_id=cmd_id,
            issuer=issuer,
            mode=mode,
            timestamp_ms=timestamp_raw,
            metadata=metadata,
            raw=mapping,
        )


@dataclass
class ConsoleCommandResult:
    """Standard response emitted after processing a console command."""

    name: str
    status: str
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
    cmd_id: str | None = None
    issuer: str | None = None
    tick: int | None = None
    latency_ms: int | None = None

    @classmethod
    def ok(
        cls,
        envelope: ConsoleCommandEnvelope,
        payload: Mapping[str, Any] | None = None,
        *,
        tick: int | None = None,
        latency_ms: int | None = None,
    ) -> "ConsoleCommandResult":
        result_payload = dict(payload) if payload is not None else {}
        return cls(
            name=envelope.name,
            status="ok",
            result=result_payload,
            cmd_id=envelope.cmd_id,
            issuer=envelope.issuer,
            tick=tick,
            latency_ms=latency_ms,
        )

    @classmethod
    def from_error(
        cls,
        envelope: ConsoleCommandEnvelope,
        code: str,
        message: str,
        *,
        details: Mapping[str, Any] | None = None,
        tick: int | None = None,
        latency_ms: int | None = None,
    ) -> "ConsoleCommandResult":
        error_payload = {"code": code, "message": message}
        if details is not None:
            error_payload["details"] = dict(details)
        return cls(
            name=envelope.name,
            status="error",
            error=error_payload,
            cmd_id=envelope.cmd_id,
            issuer=envelope.issuer,
            tick=tick,
            latency_ms=latency_ms,
        )

    def clone(self) -> "ConsoleCommandResult":
        return ConsoleCommandResult(
            name=self.name,
            status=self.status,
            result=None if self.result is None else dict(self.result),
            error=None if self.error is None else dict(self.error),
            cmd_id=self.cmd_id,
            issuer=self.issuer,
            tick=self.tick,
            latency_ms=self.latency_ms,
        )

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "status": self.status,
            "cmd_id": self.cmd_id,
            "issuer": self.issuer,
            "tick": self.tick,
            "latency_ms": self.latency_ms,
        }
        if self.result is not None:
            payload["result"] = dict(self.result)
        if self.error is not None:
            payload["error"] = dict(self.error)
        return payload


ConsoleHandler = Callable[[ConsoleCommandEnvelope], ConsoleCommandResult]
