"""Telemetry configuration models.

Holds narration thresholds, transport settings, buffer/retry policy, transform
pipeline descriptors, worker coordination, and the top-level TelemetryConfig.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

# Local literals to keep this module self-contained
TelemetryTransportType = Literal["stdout", "file", "tcp", "websocket"]
TelemetryBackpressureStrategy = Literal["drop_oldest", "block", "fan_out"]


class NarrationThrottleConfig(BaseModel):
    """Rate limiting knobs for narration output."""

    global_cooldown_ticks: int = Field(30, ge=0, le=10_000)
    category_cooldown_ticks: dict[str, int] = Field(default_factory=dict)
    dedupe_window_ticks: int = Field(20, ge=0, le=10_000)
    global_window_ticks: int = Field(600, ge=1, le=10_000)
    global_window_limit: int = Field(10, ge=1, le=1_000)
    priority_categories: list[str] = Field(default_factory=list)

    def get_category_cooldown(self, category: str) -> int:
        return int(self.category_cooldown_ticks.get(category, self.global_cooldown_ticks))


class PersonalityNarrationConfig(BaseModel):
    """Narration toggles tied to personality events."""

    enabled: bool = True
    chat_extroversion_threshold: float = Field(0.5, ge=-1.0, le=1.0)
    chat_priority_threshold: float = Field(0.75, ge=-1.0, le=1.0)
    chat_quality_threshold: float = Field(0.3, ge=0.0, le=1.0)
    conflict_tolerance_threshold: float = Field(0.95, ge=0.0, le=5.0)


class RelationshipNarrationConfig(BaseModel):
    """Narration thresholds for relationship events."""

    friendship_trust_threshold: float = Field(0.6, ge=-1.0, le=1.0)
    friendship_delta_threshold: float = Field(0.25, ge=0.0, le=2.0)
    friendship_priority_threshold: float = Field(0.85, ge=-1.0, le=1.0)
    rivalry_avoid_threshold: float = Field(0.7, ge=0.0, le=1.0)
    rivalry_escalation_threshold: float = Field(0.9, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def _validate_thresholds(self) -> RelationshipNarrationConfig:
        if self.friendship_priority_threshold < self.friendship_trust_threshold:
            raise ValueError(
                "telemetry.relationship_narration.friendship_priority_threshold must be >= friendship_trust_threshold"
            )
        if self.rivalry_escalation_threshold < self.rivalry_avoid_threshold:
            raise ValueError(
                "telemetry.relationship_narration.rivalry_escalation_threshold must be >= rivalry_avoid_threshold"
            )
        return self


class TelemetryRetryPolicy(BaseModel):
    """Retry/backoff policy applied to telemetry transports."""

    max_attempts: int = Field(default=3, ge=0, le=10)
    backoff_seconds: float = Field(default=0.5, ge=0.0, le=30.0)


class TelemetryBufferConfig(BaseModel):
    """Buffering thresholds controlling flush cadence."""

    max_batch_size: int = Field(default=32, ge=1, le=500)
    max_buffer_bytes: int = Field(default=256_000, ge=1_024, le=16_777_216)
    flush_interval_ticks: int = Field(default=1, ge=1, le=10_000)


class TelemetryTransportConfig(BaseModel):
    """Transport-specific telemetry configuration."""

    type: TelemetryTransportType = "stdout"
    endpoint: str | None = None
    file_path: Path | None = None
    connect_timeout_seconds: float = Field(default=5.0, ge=0.0, le=60.0)
    send_timeout_seconds: float = Field(default=1.0, ge=0.0, le=60.0)
    enable_tls: bool = True
    verify_hostname: bool = True
    ca_file: Path | None = None
    cert_file: Path | None = None
    key_file: Path | None = None
    allow_plaintext: bool = False
    dev_allow_plaintext: bool = False
    websocket_url: str | None = None
    retry: TelemetryRetryPolicy = TelemetryRetryPolicy()
    buffer: TelemetryBufferConfig = TelemetryBufferConfig()
    worker_poll_seconds: float = Field(default=0.5, ge=0.01, le=10.0)

    @model_validator(mode="after")
    def _validate_transport(self) -> TelemetryTransportConfig:
        transport_type = self.type
        fields_set: set[str] = set(getattr(self, "model_fields_set", set()))

        if transport_type == "stdout":
            if "enable_tls" in fields_set and self.enable_tls:
                raise ValueError("telemetry.transport.enable_tls is only supported for tcp transport")
            if any(value is not None for value in (self.ca_file, self.cert_file, self.key_file)):
                raise ValueError("telemetry.transport TLS options are only supported for tcp transport")
            if self.allow_plaintext:
                raise ValueError("telemetry.transport.allow_plaintext is only supported for tcp transport")
            if self.dev_allow_plaintext:
                raise ValueError("telemetry.transport.dev_allow_plaintext is only supported for tcp transport")
            if self.endpoint:
                raise ValueError("telemetry.transport.endpoint is not supported for stdout transport")
            if self.file_path is not None:
                raise ValueError("telemetry.transport.file_path must be omitted for stdout transport")
            self.enable_tls = False
            self.allow_plaintext = False
            self.dev_allow_plaintext = False
            return self

        if transport_type == "file":
            if "enable_tls" in fields_set and self.enable_tls:
                raise ValueError("telemetry.transport.enable_tls is only supported for tcp transport")
            if any(value is not None for value in (self.ca_file, self.cert_file, self.key_file)):
                raise ValueError("telemetry.transport TLS options are only supported for tcp transport")
            if self.allow_plaintext:
                raise ValueError("telemetry.transport.allow_plaintext is only supported for tcp transport")
            if self.dev_allow_plaintext:
                raise ValueError("telemetry.transport.dev_allow_plaintext is only supported for tcp transport")
            if self.file_path is None:
                raise ValueError("telemetry.transport.file_path is required when type is 'file'")
            if str(self.file_path).strip() == "":
                raise ValueError("telemetry.transport.file_path must not be blank")
            self.enable_tls = False
            self.allow_plaintext = False
            self.dev_allow_plaintext = False
            return self

        if transport_type == "tcp":
            endpoint = (self.endpoint or "").strip()
            if not endpoint:
                raise ValueError("telemetry.transport.endpoint is required when type is 'tcp'")
            self.endpoint = endpoint
            if self.file_path is not None:
                raise ValueError("telemetry.transport.file_path must be omitted for tcp transport")
            if "enable_tls" not in fields_set:
                self.enable_tls = not self.allow_plaintext

            if self.enable_tls:
                if self.allow_plaintext or self.dev_allow_plaintext:
                    self.allow_plaintext = False
                    self.dev_allow_plaintext = False
                if self.key_file and not self.cert_file:
                    raise ValueError("telemetry.transport.cert_file must be provided when key_file is set")
                if self.cert_file and not self.key_file:
                    raise ValueError("telemetry.transport.key_file must be provided when cert_file is set")
                if self.cert_file is not None and str(self.cert_file).strip() == "":
                    raise ValueError("telemetry.transport.cert_file must not be blank")
                if self.key_file is not None and str(self.key_file).strip() == "":
                    raise ValueError("telemetry.transport.key_file must not be blank")
                if self.ca_file is not None and str(self.ca_file).strip() == "":
                    raise ValueError("telemetry.transport.ca_file must not be blank")
                return self

            if not self.allow_plaintext:
                raise ValueError("telemetry.transport.tcp requires enable_tls=true or allow_plaintext=true")
            if not self.dev_allow_plaintext:
                raise ValueError("telemetry.transport.allow_plaintext requires dev_allow_plaintext=true for tcp transport")
            host, *_ = endpoint.split(":", 1)
            host = host.strip()
            if host not in {"localhost", "127.0.0.1", "::1"}:
                raise ValueError("telemetry.transport.allow_plaintext is only permitted for localhost endpoints")
            if ("enable_tls" in fields_set and self.enable_tls) and self.allow_plaintext:
                raise ValueError("telemetry.transport cannot enable TLS and allow_plaintext simultaneously")
            self.enable_tls = False
            return self

        if transport_type == "websocket":
            if self.endpoint is not None:
                raise ValueError("telemetry.transport.endpoint must be omitted for websocket transport")
            if self.file_path is not None:
                raise ValueError("telemetry.transport.file_path must be omitted for websocket transport")
            if any(value is not None for value in (self.ca_file, self.cert_file, self.key_file)):
                raise ValueError("telemetry.transport websocket does not support TLS certificate options")
            if self.allow_plaintext or self.dev_allow_plaintext:
                raise ValueError("telemetry.transport websocket does not use allow_plaintext flags")
            url = (self.websocket_url or "").strip()
            if not url:
                raise ValueError("telemetry.transport.websocket_url is required when type is 'websocket'")
            self.websocket_url = url
            self.enable_tls = False
            self.allow_plaintext = False
            self.dev_allow_plaintext = False
            return self

        raise ValueError(f"Unsupported telemetry transport type: {transport_type}")


class TelemetryWorkerConfig(BaseModel):
    """Worker coordination and backpressure strategy settings."""

    backpressure: TelemetryBackpressureStrategy = "drop_oldest"
    block_timeout_seconds: float = Field(default=0.5, ge=0.05, le=5.0)
    restart_limit: int = Field(default=3, ge=1, le=10)

    model_config = ConfigDict(extra="forbid")


SUPPORTED_TELEMETRY_TRANSFORMS = {
    "snapshot_normalizer",
    "redact_fields",
    "ensure_fields",
    "schema_validator",
}


class TelemetryTransformEntry(BaseModel):
    """Describes a single transform within the telemetry pipeline."""

    id: str
    options: dict[str, object] = Field(default_factory=dict)

    model_config = ConfigDict(extra="forbid")

    @model_validator(mode="before")
    @classmethod
    def _coerce_transform_entry(cls, value: object) -> object:
        if isinstance(value, str):
            return {"id": value}
        if isinstance(value, Mapping):
            data = dict(value)
            data.setdefault("id", data.get("name"))
            if "options" not in data:
                options = {key: data.pop(key) for key in list(data.keys()) if key not in {"id", "options"}}
                data["options"] = options
            elif not isinstance(data["options"], Mapping):
                raise TypeError("telemetry.transforms.pipeline.options must be a mapping")
            return data
        return value

    @model_validator(mode="after")
    def _validate_transform(self) -> TelemetryTransformEntry:
        transform_id = str(self.id).strip().lower()
        if not transform_id:
            raise ValueError("telemetry.transforms entries must define a non-empty id")
        if transform_id not in SUPPORTED_TELEMETRY_TRANSFORMS:
            supported = ", ".join(sorted(SUPPORTED_TELEMETRY_TRANSFORMS))
            raise ValueError(f"Unsupported telemetry transform id '{self.id}'. Supported transforms: {supported}")
        self.id = transform_id
        if not isinstance(self.options, dict):
            raise TypeError("telemetry.transforms options must be a mapping")
        return self


class TelemetryTransformsConfig(BaseModel):
    """Configuration block describing telemetry transform pipeline."""

    pipeline: list[TelemetryTransformEntry] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class TelemetryConfig(BaseModel):
    """Top-level telemetry configuration surfaces."""

    narration: NarrationThrottleConfig = NarrationThrottleConfig()
    transport: TelemetryTransportConfig = TelemetryTransportConfig()
    relationship_narration: RelationshipNarrationConfig = RelationshipNarrationConfig()
    personality_narration: PersonalityNarrationConfig = PersonalityNarrationConfig()
    diff_enabled: bool = True
    transforms: TelemetryTransformsConfig = TelemetryTransformsConfig()
    worker: TelemetryWorkerConfig = TelemetryWorkerConfig()


__all__ = [
    "NarrationThrottleConfig",
    "PersonalityNarrationConfig",
    "RelationshipNarrationConfig",
    "TelemetryBackpressureStrategy",
    "TelemetryBufferConfig",
    "TelemetryConfig",
    "TelemetryRetryPolicy",
    "TelemetryTransformEntry",
    "TelemetryTransformsConfig",
    "TelemetryTransportConfig",
    "TelemetryTransportType",
    "TelemetryWorkerConfig",
]

