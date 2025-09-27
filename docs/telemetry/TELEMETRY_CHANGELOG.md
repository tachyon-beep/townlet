# Telemetry Schema Change Log

| Version | Date | Summary | Consumer Actions |
| --- | --- | --- | --- |
| 0.8.1 | 2025-10-04 | Transport abstraction with buffered delivery, per-snapshot transport status, and observer telemetry smoke suite. | Update configs to set `telemetry.transport`, run admin smoke command (`pytest ...telemetry_transport.py`). |
| 0.7.0 | 2025-09-30 | Added narration throttle payloads (`narrations`, `narration_state`) and queue-conflict narration entries guarded by config. | Update consumers to read optional narration payloads and persist narration state in snapshots. |
| 0.6.0 | 2025-09-30 | Observer telemetry publishes relationship snapshots + per-tick updates; console schema bumped to 0.6.x and dashboard renders delta table. | Update UI clients to schema prefix 0.6, consume `relationship_snapshot`/`relationship_updates`, refresh dashboards and docs. |
| 0.5.0 | 2025-09-28 | Expanded PPO telemetry (`telemetry_version` 1.1) with cycle/data-mode, epoch duration, entropy/grad maxima, reward↔adv correlation, rollout ticks, and streaming offsets; tooling emits summaries/watch alerts. | Move consumers to v1.1 schema; update validators/watchers; regenerate dashboards using new fields. |
| 0.4.0 | 2025-09-26 | Introduced PPO training NDJSON telemetry (`telemetry_version` 1) with epoch-level KL divergence and conflict aggregates. | Update training log consumers to read `telemetry_version`, handle `kl_divergence`, and preserve baseline/conflict fields. |
| 0.3.0 | 2025-09-26 | Added `conflict` payload with queue fairness counters and rivalry snapshot; schema default bumped. | Update clients to use `conflict.queues` and `conflict.rivalry`; ensure schema prefix `0.3.x`. |
| 0.2.0 | 2025-09-25 | Added employment metrics to snapshots (shift state, attendance ratio, pending exits); console snapshot includes `schema_version`. | Update clients to respect `schema_version`, render employment KPIs, and validate payloads (use `scripts/telemetry_check.py`). |
| 0.2.0 UI | 2025-09-25 | Observer dashboard (`scripts/observer_ui.py`) and telemetry client library published. | Consume via `townlet_ui.telemetry.TelemetryClient`; ensure schema prefix `0.2.x`. |

Compatibility Matrix:

| Client Component | Supported Schema | Notes |
| --- | --- | --- |
| Console CLI (planned Typer) | ≥0.2.0 | Warns on newer schemas; blocks on unsupported major versions. |
| Observer UI dashboard | ≥0.3.0 | Displays employment widgets, conflict panel, ASCII map; warns on newer schemas. |
| Smoke Harness (`run_employment_smoke.py`) | ≥0.2.0 | Emits metrics payload compatible with `scripts/telemetry_check.py`. |
| Telemetry Validator (`scripts/telemetry_check.py`) | ≥0.3.0 | Validates employment and conflict payloads; extend with future schema entries. |
| PPO Telemetry Validator (`scripts/validate_ppo_telemetry.py`) | telemetry_version == 1 | Checks NDJSON schema, baseline drift, and conflict aggregates. |
| PPO Telemetry Watch (`scripts/telemetry_watch.py`) | telemetry_version == 1 | Tails NDJSON logs and alerts on KL/loss/gradient thresholds. |
| Training harness replay | ≥0.3.0 | `scripts/run_training.py --replay-manifest` verifies conflict batches before PPO integration. |
| Replay tooling | ≥0.3.0 | `scripts/run_replay.py` validates observation conflict features and telemetry samples. |

> Update this log whenever schema_version increments. Keep sample payloads (`docs/samples/telemetry_snapshot_*.json`) aligned with the latest schema.
