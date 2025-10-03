# Telemetry Schema Change Log

| Version | Date | Summary | Consumer Actions |
| --- | --- | --- | --- |
| 0.9.8 | 2025-10-24 | Introduced diff-mode telemetry streaming with per-tick health metrics (`transport_status.worker_alive`, queue depth, dropped counters). Snapshot payloads now carry `payload_type`, and diffs include changed sections only. | Update clients to apply `payload_type` aware merges (consume `changes`/`removed` fields) and surface transport health in dashboards. |
| 0.9.7 | 2025-10-23 | Narrations now emit `relationship_friendship`, `relationship_rivalry`, and `relationship_social_alert` events (trust milestones, rivalry escalation, chat failures/avoidance). Console/UI clients can render social stories with limiter-safe payloads and operators can tune thresholds via `telemetry.relationship_narration.*`. | Update watchers/dashboards to subscribe to new narration categories; ensure schema validators accept expanded narration payloads and propagate any threshold overrides to ops tooling. |
| 0.9.6 | 2025-10-22 | Added `relationship_summary` (top friends/rivals, churn totals) and `social_events` (chat successes/failures, rivalry avoidance) to observer snapshots. Reward breakdown now splits social bonuses, penalties, and avoidance contributions. | Update dashboards/validators to handle new telemetry fields; trim social event history as needed and consume expanded reward breakdown keys. |
| 0.9.5 | 2025-10-15 | Telemetry snapshots expose affordance runtime payload (running set, reservations, per-tick event counts) and console includes the new `affordance_status` command. | Update consumers/validators to tolerate the optional `affordance_runtime` block; surface new command in ops tooling. |
| 0.9.4 | 2025-10-06 | PPO telemetry adds advantage health metrics (`adv_zero_std_batches`, `adv_min_std`, `clip_fraction_max`, `clip_triggered_minibatches`), emits option commitment state (`option_commit_remaining`, `option_commit_kind`, `option_commit_enforced`) in trajectory frames, surfaces promotion candidate metadata/history, and adds NaN guards in the training harness. | Update validators/watchers to expect new fields; investigate logs if harness raises the new NaN errors. |
| 0.9.3 | 2025-10-21 | Reward breakdown adds `terminal_penalty`; docs updated with LR2 reward model. | Update dashboards/watchers to tolerate the new breakdown key; refresh local schema fixtures. |
| 0.9.2 | 2025-10-19 | Added nightly reset event (`agent_nightly_reset`), home routing metadata in console spawn responses, and rivalry/queue fairness regression metrics. | Update event consumers/watchers to handle nightly reset payload (`home_position`, `moved` flags), `agent_respawn.original_agent_id`, and conflict snapshot rivalry history; console automation should persist new `home_position` field. |
| 0.9.1 | 2025-10-12 | PPO telemetry tooling records hygiene/rest metrics (`utility_outage_events`, `shower_complete_events`, `sleep_complete_events`) and exposes watcher thresholds. | Upgrade `telemetry_watch.py`/`telemetry_summary.py`; configure new flags for hygiene outages and completion rates. |
| 0.9.0 | 2025-10-12 | Conflict snapshot adds queue history, rivalry events, and stability alert payload; console gains conflict inspection commands. | Upgrade clients to schema prefix 0.9, parse `conflict.queue_history`, `conflict.rivalry_events`, and `stability` blocks; use new console commands for ops runbooks. |
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
| PPO Telemetry Watch (`scripts/telemetry_watch.py`) | telemetry_version == 1 | Tails NDJSON logs and alerts on KL/loss/gradient thresholds plus queue/social/hygiene counters. |
| Training harness replay | ≥0.3.0 | `scripts/run_training.py --replay-manifest` verifies conflict batches before PPO integration. |
| Replay tooling | ≥0.3.0 | `scripts/run_replay.py` validates observation conflict features and telemetry samples. |

> Update this log whenever schema_version increments. Keep sample payloads (`docs/samples/telemetry_snapshot_*.json`) aligned with the latest schema.
