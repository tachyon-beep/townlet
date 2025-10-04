# Townlet Scenario Catalog Baseline

This directory provides narrative and QA scenarios consumed by the demo runner.
The current canonical rehearsal baseline is recorded below to prevent drift when
new demo scripts are introduced.

| Scenario | Config Path | Seed | Notes |
| --- | --- | --- | --- |
| Baseline loop | `configs/examples/poc_hybrid.yaml` | CLI default (config does not specify) | Run with default demo timeline via `scripts/demo_run.py --ticks 60 --no-palette` |
| Demo story arc | `configs/scenarios/demo_story_arc.yaml` | 4242 | Pair with `timelines/demo_story_arc.yaml`; highlights arrival → disruption → recovery narrative |

## Telemetry Snapshot

The latest baseline rehearsal (2025-10-04) stored the first 50 events from
`logs/demo_stream.jsonl` under `artifacts/demo_baseline/demo_stream_head.jsonl`.
Refresh this snapshot whenever demo seeds/configs change so downstream QA has a
stable reference payload.

## Timeline Assets

Timeline files must be plain lists of tick-scheduled entries. Scenario configs
such as `queue_conflict.yaml` are *not* valid timelines. Use `src/townlet/demo/timeline.py`
to validate new assets before committing.

- `timelines/demo_story_arc.yaml` – primary operator asset; includes pacing comments and metadata.
- `timelines/demo_story_arc.json` – JSON mirror for tooling and smoke tests.
