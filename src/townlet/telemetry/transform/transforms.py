"""Reusable telemetry transform implementations."""

from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing only
    from townlet.telemetry.interfaces import TelemetryEvent

__all__ = [
    "EnsureFieldsTransform",
    "RedactFieldsTransform",
    "SchemaValidationTransform",
]

logger = logging.getLogger(__name__)


class RedactFieldsTransform:
    """Remove sensitive fields from telemetry payloads."""

    def __init__(
        self,
        fields: Iterable[str],
        *,
        apply_to_kinds: Iterable[str] | None = None,
    ) -> None:
        self._fields = {str(field) for field in fields}
        self._kinds = {str(kind) for kind in apply_to_kinds} if apply_to_kinds is not None else None

    def process(self, event: TelemetryEvent) -> TelemetryEvent | None:
        if not self._fields:
            return event
        if self._kinds is not None and event.kind not in self._kinds:
            return event
        payload = dict(event.payload)
        removed = False
        for field in self._fields:
            if field in payload:
                payload.pop(field, None)
                removed = True
        if not removed:
            return event
        from townlet.telemetry.interfaces import TelemetryEvent

        return TelemetryEvent(
            tick=int(event.tick),
            kind=event.kind,
            payload=payload,
            metadata=dict(event.metadata),
        )

    def flush(self) -> Iterable[TelemetryEvent]:  # pragma: no cover - no buffering
        return ()


class EnsureFieldsTransform:
    """Drop telemetry events missing required payload fields."""

    def __init__(
        self,
        *,
        required_fields_by_kind: Mapping[str, Iterable[str]] | None = None,
        default_required_fields: Iterable[str] | None = None,
    ) -> None:
        self._required_by_kind = {
            str(kind): {str(field) for field in fields}
            for kind, fields in (required_fields_by_kind or {}).items()
        }
        if default_required_fields is None:
            default_required_fields = ("tick",)
        self._default_required = {str(field) for field in default_required_fields}

    def process(self, event: TelemetryEvent) -> TelemetryEvent | None:
        required = self._required_by_kind.get(event.kind, self._default_required)
        if not required:
            return event
        missing = [field for field in required if field not in event.payload]
        if missing:
            logger.warning(
                "telemetry_transform_missing_fields event_kind=%s missing=%s",
                event.kind,
                ",".join(missing),
            )
            return None
        return event

    def flush(self) -> Iterable[TelemetryEvent]:  # pragma: no cover - no buffering
        return ()


class SchemaValidationTransform:
    """Validate telemetry events against minimal JSON schema definitions."""

    def __init__(
        self,
        *,
        schema_by_kind: Mapping[str, CompiledSchema],
        mode: str = "drop",
    ) -> None:
        self._schemas = {str(kind): schema for kind, schema in schema_by_kind.items()}
        normalized_mode = mode.lower()
        if normalized_mode not in {"drop", "warn", "raise"}:
            raise ValueError("schema_validator mode must be one of 'drop', 'warn', 'raise'")
        self._mode = normalized_mode

    def process(self, event: TelemetryEvent) -> TelemetryEvent | None:
        schema = self._schemas.get(event.kind)
        if schema is None:
            return event
        errors = schema.validate(event.payload)
        if not errors:
            return event
        message = ", ".join(errors)
        if self._mode == "warn":
            logger.warning(
                "telemetry_schema_validation_warning event_kind=%s errors=%s",
                event.kind,
                message,
            )
            return event
        if self._mode == "raise":
            raise ValueError(f"Telemetry event kind '{event.kind}' failed schema validation: {message}")
        logger.warning(
            "telemetry_schema_validation_dropped event_kind=%s errors=%s",
            event.kind,
            message,
        )
        return None

    def flush(self) -> Iterable[TelemetryEvent]:  # pragma: no cover - no buffering
        return ()


class CompiledSchema:
    """Lightweight validator for a subset of JSON Schema features."""

    def __init__(self, *, required: set[str], properties: Mapping[str, Mapping[str, object]]) -> None:
        self._required = set(required)
        self._properties = {
            str(name): {
                key: value
                for key, value in spec.items()
                if key in {"type", "enum", "const"}
            }
            for name, spec in properties.items()
        }

    def validate(self, payload: Mapping[str, object]) -> list[str]:
        errors: list[str] = []
        for field in self._required:
            if field not in payload:
                errors.append(f"missing field '{field}'")
        for name, spec in self._properties.items():
            if name not in payload:
                continue
            value = payload[name]
            if "type" in spec and not self._check_type(value, spec["type"]):
                errors.append(f"field '{name}' expected type {spec['type']}")
            if "enum" in spec and value not in spec["enum"]:
                errors.append(f"field '{name}' not in enum {spec['enum']}")
            if "const" in spec and value != spec["const"]:
                errors.append(f"field '{name}' expected const {spec['const']}")
        return errors

    @staticmethod
    def _check_type(value: object, expected: object) -> bool:
        if isinstance(expected, list):
            return any(CompiledSchema._check_type(value, item) for item in expected)
        if expected == "string":
            return isinstance(value, str)
        if expected == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        if expected == "number":
            return isinstance(value, (int, float)) and not isinstance(value, bool)
        if expected == "object":
            return isinstance(value, Mapping)
        if expected == "boolean":
            return isinstance(value, bool)
        if expected == "array":
            return isinstance(value, (list, tuple))
        return True


def compile_json_schema(schema: Mapping[str, object]) -> CompiledSchema:
    """Compile a subset of JSON schema into a validator."""

    schema_type = schema.get("type")
    if schema_type not in ("object", None):
        raise ValueError("SchemaValidationTransform only supports object schemas")
    required = set(schema.get("required", []))
    properties = schema.get("properties", {})
    if not isinstance(properties, Mapping):
        raise TypeError("schema 'properties' must be a mapping")
    return CompiledSchema(required=required, properties=properties)
