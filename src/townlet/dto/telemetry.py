"""Telemetry event DTOs."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TelemetryMetadata(BaseModel):
    """Metadata attached to telemetry events."""

    schema_version: str = "1.0"
    timestamp: float | None = None
    source: str = "townlet"


class TelemetryEventDTO(BaseModel):
    """Telemetry event with typed payload."""

    event_type: str  # e.g., "loop.tick", "stability.metrics", "policy.metadata"
    tick: int
    payload: dict[str, Any]
    metadata: TelemetryMetadata = Field(default_factory=TelemetryMetadata)


class ConsoleEventDTO(BaseModel):
    """Console command result event."""

    command: str
    agent_id: str | None = None
    success: bool
    result: dict[str, Any] = Field(default_factory=dict)
    tick: int
    error: str | None = None


__all__ = ["TelemetryEventDTO", "TelemetryMetadata", "ConsoleEventDTO"]
