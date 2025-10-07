# Telemetry Schema Validation Guide

Townlet validates telemetry payloads before they leave the simulation loop.
The default pipeline ships with a schema validator using the bundled snapshot
and diff schemas. This guide explains how to configure the validator, author
schemas, and debug failures.

## 1. Overview

The telemetry pipeline is split into aggregation → transform → transport. The
`schema_validator` transform inspects each `TelemetryEvent` and compares the
payload against a JSON Schema document. When validation fails you can choose to
Drop the event, emit a warning, or raise an error.

## 2. Enabling validation

The default pipeline loads the bundled snapshot and diff schemas and drops any
event that fails validation. To customise behaviour add a `schema_validator`
entry to
`telemetry.transforms.pipeline` in your YAML configuration:

```yaml
docs: configs/examples/poc_hybrid.yaml
...
telemetry:
  transforms:
    pipeline:
      - id: schema_validator
        mode: drop        # drop | warn | raise
        schemas:
          snapshot: configs/schemas/telemetry/snapshot.schema.json
          diff:      configs/schemas/telemetry/diff.schema.json
```

* `schemas` is a mapping from telemetry event kind to the schema document.
* `mode` controls behaviour when validation fails:
  * `drop` (default) removes the event and logs a warning.
  * `warn` logs and forwards the original event unchanged.
  * `raise` raises a `ValueError`, causing the simulation tick to fail.

Relative paths are resolved from the working directory running the simulation.
Store project-specific schemas alongside your config for consistency.

## 3. Authoring schemas

Townlet ships reference schemas in `src/townlet/telemetry/schemas/` that cover
the core snapshot and diff payloads. These documents use a subset of JSON
Schema (HTTP draft 2020-12) and are intended as starting points. When creating
new schemas:

1. Begin by copying the bundled schema and trimming it to the fields you care
   about. It’s better to validate critical structures than to attempt to pin
   every optional field.
2. Keep schemas permissive (`additionalProperties: true`) unless you want to be
   alerted when new fields appear. This helps the validator stay forward
   compatible.
3. Use integer/number constraints to catch obvious regressions (negative tick,
   missing counters, etc.).
4. Check schemas into version control and update consumers that rely on them
   (dashboards, downstream services).

## 4. Testing schemas locally

Use the `tests/telemetry/test_transform_pipeline.py` examples as a template.
You can instantiate the validator directly and feed it telemetry events:

```python
from townlet.telemetry.transform import compile_json_schema, SchemaValidationTransform
schema = compile_json_schema(json.loads(Path("my_schema.json").read_text()))
validator = SchemaValidationTransform(schema_by_kind={"snapshot": schema}, mode="raise")
validator.process(snapshot_event)
```

Add unit tests for every new schema to prevent regressions from landing.

## 5. Debugging validation failures

When the validator drops or warns about an event the log includes:

```
telemetry_schema_validation_dropped event_kind=snapshot errors=missing field 'schema_version', field 'tick' expected type integer
```

Enable debug logging if you need to inspect the full payload. Consider running
with `mode: warn` in non-production environments to surface schema drift without
breaking runs.

## 6. Rollout checklist

* Update the simulation config with the correct schema paths.
* Verify `pytest tests/telemetry/test_transform_pipeline.py` passes using your
  schemas.
* Coordinate with observability tooling so dashboards understand any new
  fields.
* Document schema changes in `docs/` (for example alongside the plan docs).

With schemas in place you can iterate on telemetry payloads confidently and
catch structural regressions before they hit downstream systems.
