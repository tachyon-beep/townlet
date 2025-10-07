from __future__ import annotations

import json
from pathlib import Path

from townlet.config import load_config
from townlet.config.loader import TelemetryTransformEntry, TelemetryTransformsConfig
from townlet.telemetry.interfaces import TelemetryEvent
from townlet.telemetry.publisher import TelemetryPublisher
from townlet.telemetry.transform import (
    EnsureFieldsTransform,
    RedactFieldsTransform,
    SchemaValidationTransform,
    SnapshotEventNormalizer,
    TelemetryTransformPipeline,
    TransformPipelineConfig,
    compile_json_schema,
)


def _build_pipeline(*transforms) -> TelemetryTransformPipeline:
    config = TransformPipelineConfig(transforms=transforms)
    return config.build_pipeline()


def test_redact_fields_transform_removes_sensitive_keys() -> None:
    event = TelemetryEvent(
        tick=1,
        kind="snapshot",
        payload={
            "schema_version": "1.0",
            "tick": 1,
            "policy_identity": {"hash": "secret"},
        },
        metadata={},
    )
    pipeline = _build_pipeline(
        SnapshotEventNormalizer(),
        RedactFieldsTransform(fields=("policy_identity",), apply_to_kinds=("snapshot",)),
        EnsureFieldsTransform(required_fields_by_kind={"snapshot": {"schema_version", "tick"}}),
    )

    [processed] = pipeline.process([event])
    assert "policy_identity" not in processed.payload
    assert processed.payload["schema_version"] == "1.0"


def test_ensure_fields_transform_drops_events_missing_required_fields() -> None:
    event = TelemetryEvent(
        tick=2,
        kind="snapshot",
        payload={"tick": 2},
        metadata={},
    )
    pipeline = _build_pipeline(
        EnsureFieldsTransform(required_fields_by_kind={"snapshot": {"schema_version"}}),
    )

    processed = pipeline.process([event])
    assert processed == []


def test_ensure_fields_transform_defaults_to_tick_requirement() -> None:
    event = TelemetryEvent(
        tick=3,
        kind="health",
        payload={"tick": 3, "error": "boom"},
        metadata={},
    )
    pipeline = _build_pipeline(EnsureFieldsTransform())

    [processed] = pipeline.process([event])
    assert processed.payload["error"] == "boom"


def test_configurable_transforms_override_defaults() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config = config.model_copy(deep=True)
    config.telemetry.transforms = TelemetryTransformsConfig(
        pipeline=[
            TelemetryTransformEntry(id="snapshot_normalizer"),
            TelemetryTransformEntry(
                id="redact_fields",
                options={"fields": ["custom_secret"], "kinds": ["snapshot"]},
            ),
        ]
    )

    publisher = TelemetryPublisher(config)
    event = TelemetryEvent(
        tick=5,
        kind="snapshot",
        payload={"schema_version": "1.0", "tick": 5, "custom_secret": "hide"},
        metadata={},
    )

    [processed] = publisher._transform_pipeline.process([event])
    assert "custom_secret" not in processed.payload
    assert processed.payload["tick"] == 5


def test_empty_transform_pipeline_uses_defaults() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config = config.model_copy(deep=True)
    config.telemetry.transforms = TelemetryTransformsConfig(pipeline=[])

    publisher = TelemetryPublisher(config)
    event = TelemetryEvent(
        tick=6,
        kind="snapshot",
        payload={
            "schema_version": "1.0",
            "tick": 6,
            "policy_identity": {"hash": "sensitive"},
        },
        metadata={},
    )

    [processed] = publisher._transform_pipeline.process([event])
    assert "policy_identity" not in processed.payload


def test_default_pipeline_drops_invalid_schema() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config = config.model_copy(deep=True)
    config.telemetry.transforms = TelemetryTransformsConfig(pipeline=[])

    publisher = TelemetryPublisher(config)
    invalid_event = TelemetryEvent(
        tick=7,
        kind="snapshot",
        payload={"tick": 7},
        metadata={},
    )

    result = publisher._transform_pipeline.process([invalid_event])
    assert result == []


SCHEMA_DIR = Path("tests/data/telemetry_schema").resolve()


def _load_schema(name: str):
    return json.loads((SCHEMA_DIR / name).read_text())


def test_schema_validator_drops_invalid_event() -> None:
    schema = compile_json_schema(_load_schema("snapshot_minimal.schema.json"))
    transform = SchemaValidationTransform(schema_by_kind={"snapshot": schema}, mode="drop")

    invalid_event = TelemetryEvent(
        tick=10,
        kind="snapshot",
        payload={"tick": 10},
        metadata={},
    )

    assert transform.process(invalid_event) is None


def test_schema_validator_warn_mode(caplog) -> None:
    schema = compile_json_schema(_load_schema("snapshot_minimal.schema.json"))
    transform = SchemaValidationTransform(schema_by_kind={"snapshot": schema}, mode="warn")

    invalid_event = TelemetryEvent(
        tick=11,
        kind="snapshot",
        payload={"tick": 11},
        metadata={},
    )

    caplog.clear()
    with caplog.at_level("WARNING"):
        result = transform.process(invalid_event)
    assert result is invalid_event
    assert any("telemetry_schema_validation_warning" in record.message for record in caplog.records)


def test_schema_validator_raise_mode() -> None:
    schema = compile_json_schema(_load_schema("snapshot_minimal.schema.json"))
    transform = SchemaValidationTransform(schema_by_kind={"snapshot": schema}, mode="raise")

    invalid_event = TelemetryEvent(
        tick=12,
        kind="snapshot",
        payload={"tick": 12},
        metadata={},
    )

    try:
        transform.process(invalid_event)
    except ValueError as exc:
        assert "schema validation" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("schema validator did not raise")


def test_schema_validator_pipeline_via_config() -> None:
    config = load_config(Path("configs/examples/poc_hybrid.yaml"))
    config = config.model_copy(deep=True)
    config.telemetry.transforms = TelemetryTransformsConfig(
        pipeline=[
            TelemetryTransformEntry(
                id="schema_validator",
                options={
                    "schemas": {
                        "snapshot": str(SCHEMA_DIR / "snapshot_minimal.schema.json"),
                    },
                    "mode": "drop",
                },
            )
        ]
    )

    publisher = TelemetryPublisher(config)

    invalid_event = TelemetryEvent(
        tick=13,
        kind="snapshot",
        payload={"tick": 13},
        metadata={},
    )

    processed = publisher._transform_pipeline.process([invalid_event])
    assert processed == []


def test_default_snapshots_schema_compiles() -> None:
    schema = compile_json_schema(json.loads(Path("src/townlet/telemetry/schemas/snapshot.schema.json").read_text()))
    event = TelemetryEvent(
        tick=0,
        kind="snapshot",
        payload={
            "schema_version": "0.9.7",
            "tick": 0,
            "payload_type": "snapshot",
            "queue_metrics": {"cooldown_events": 0},
            "stability": {"metrics": {}, "alerts": []},
        },
        metadata={},
    )
    assert schema.validate(event.payload) == []
