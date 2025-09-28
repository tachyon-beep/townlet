# Conflict & Rivalry Release Checklist

Use this checklist before enabling or rolling out the conflict/rivalry system in a new environment.

## Configuration Toggles
- [ ] Verify `features.stages.relationships` is set to `"B"` (or higher) in the target config. Hybrid observations require relationships enabled.
- [ ] Confirm `queue_fairness` block matches expected defaults (cooldown, ghost-step threshold). Document any overrides.
- [ ] Ensure `conflict.rivalry` thresholds (`increment_per_conflict`, `decay_per_tick`, `avoid_threshold`, `max_edges`) align with baseline values.
- [ ] If running scripted scenarios, ensure `scenario` entries reference the updated fixtures (queue_conflict, rivalry_decay) and objects exist in the affordance manifest.

## Smoke Scenarios
- [ ] Run queue conflict integration test: `pytest tests/test_conflict_scenarios.py::test_queue_conflict_scenario_produces_alerts`.
- [ ] Run rivalry decay scenario test: `pytest tests/test_conflict_scenarios.py::test_rivalry_decay_scenario_tracks_events`.
- [ ] Execute randomized queue regression: `pytest tests/test_conflict_scenarios.py::test_queue_manager_randomised_regression`.
- [ ] Optionally replay full scenario via baseline snippet (see `docs/ops/queue_conflict_baselines.md`) and capture telemetry snapshot.
- [ ] Verify new samples exist: `docs/samples/queue_conflict_snapshot.json`, `docs/samples/rivalry_decay_snapshot.json`.

## Telemetry & Console Verification
- [ ] Run `conflict_status --history 10 --rivalries 5` and ensure queue history + alerts populate.
- [ ] Run `queue_inspect <object_id>` for key interactive objects; confirm cooldowns and active slot are accurate.
- [ ] Run `rivalry_dump --limit 5` (and per-agent variants) to inspect top rivalry edges.
- [ ] Check observer dashboard conflict panel for ROTATION/QUEUE banners and rivalry event list.
- [ ] Capture `telemetry_snapshot` payload to archive `queue_history` and `rivalry_events` slices.

## Regression Suite
- [ ] Run unit tests covering rivalry/queue/stability: `pytest tests/test_rivalry_ledger.py tests/test_policy_rivalry_behavior.py tests/test_queue_manager.py tests/test_stability_monitor.py tests/test_conflict_telemetry.py`.
- [ ] Run telemetry client coverage: `pytest tests/test_telemetry_client.py`.

## Ops Documentation & Alerts
- [ ] Confirm `docs/ops/OPS_HANDBOOK.md` conflict runbook is current for the environment; link in release notes.
- [ ] Update `docs/ops/queue_conflict_baselines.md` with any environment-specific thresholds before release.
- [ ] Notify on-call/ops with summary (new alerts to monitor, snippets to reproduce issues).

## Rollback Plan
- [ ] Identify previous stable config version and associated scenario snapshots.
- [ ] Prepare to disable conflict by setting `queue_fairness.cooldown_ticks` high and `conflict.rivalry.increment_per_conflict` to 0.0 if emergency rollback needed.
- [ ] Ensure telemetry transport + console commands remain available for post-rollback verification.
- [ ] Document rollback triggers (e.g., sustained `queue_fairness_pressure` or `rivalry_spike` alerts exceeding baseline for >5 minutes).

## Sign-off
- [ ] Attach telemetry snapshot, console outputs, and pytest logs to release ticket.
- [ ] Gain approval from Systems/Gameplay owner and Ops lead.

## Behaviour Cloning & Anneal Promotion
- [ ] Verify BC manifest (`data/bc_datasets/manifests/...`) and checksums before release.
- [ ] Run `python scripts/run_training.py <config> --mode bc --bc-manifest <manifest>`; archive metrics output.
- [ ] Run `python scripts/run_training.py <config> --mode anneal --bc-manifest <manifest> --anneal-log-dir <dir> --anneal-exit-on-failure`.
- [ ] Review `anneal_results.json`; use `scripts/telemetry_summary.py --format markdown` for summary and `scripts/telemetry_watch.py --anneal-bc-min 0.9 --anneal-loss-max 0.1 --anneal-queue-min ...` for drift checks.
- [ ] Capture dashboard screenshot of anneal panel + attach watcher JSON to release ticket.
- [ ] If status != PASS, halt promotion, log remediation, and rerun with adjusted config.
