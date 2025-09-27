# Townlet Operations Handbook (v0.1)

## Run Modes & Entry Points
- `python scripts/run_simulation.py --config <yaml>` — starts a headless shard; honour `config_id` and observation variant declared in the file. Attach `--tick-limit` during smoke checks to bound runtime.
- `python scripts/run_training.py --config <yaml> [--mode replay|rollout|mixed]` — spins the PPO training harness; `mode` overrides `training.source` in YAML.
- Replay example: `--mode replay --train-ppo --capture-dir captures/<scenario>`.
- Rollout example: `--mode rollout --rollout-ticks 200 --rollout-auto-seed-agents --ppo-log logs/live.jsonl`.
- Mixed example: `--mode mixed --capture-dir captures/<scenario> --rollout-ticks 100 --ppo-log logs/mixed.jsonl`.
- Affordance manifest lint: `python scripts/validate_affordances.py --strict` — run after editing files under `configs/affordances/` to confirm schema, duplicate, and checksum compliance (CI runs the same check).
- Mixed-mode queue-conflict workflow:
  1. `python scripts/capture_rollout.py configs/scenarios/queue_conflict.yaml --output tmp/ops_run`
  2. `python scripts/run_training.py configs/scenarios/queue_conflict.yaml --mode mixed --replay-manifest tmp/ops_run/rollout_sample_manifest.json --rollout-ticks 40 --epochs 1 --ppo-log tmp/ops_run/ppo_mixed.jsonl`
  3. `head -n 1 docs/samples/ppo_conflict_telemetry.jsonl > tmp/ops_run/baseline.json`
  4. `python scripts/validate_ppo_telemetry.py tmp/ops_run/ppo_mixed.jsonl --baseline tmp/ops_run/baseline.json`
  5. `python scripts/telemetry_watch.py tmp/ops_run/ppo_mixed.jsonl --kl-threshold 0.5 --grad-threshold 5 --entropy-threshold -0.2 --reward-corr-threshold -0.5 --queue-events-min 30 --queue-intensity-min 45 --shared-meal-min 1 --late-help-min 0 --shift-takeover-max 2 --chat-quality-min 0.5 --json > tmp/ops_run/watch.jsonl`
  6. `python scripts/telemetry_summary.py tmp/ops_run/ppo_mixed.jsonl --format markdown > tmp/ops_run/summary.md`
  Attach `tmp/ops_run/{ppo_mixed.jsonl,watch.jsonl,summary.md}` to the ops log for audit.
- Behaviour cloning / anneal workflow:
  1. Validate dataset integrity: `python - <<'PY' ...` (see below) to recompute SHA-256 for
     `data/bc_datasets/checksums/idle_v1.json`. Abort if mismatches occur.
  2. Run BC gate: `python - <<'PY'` (load config `artifacts/m5/acceptance/config_idle_v1.yaml`, invoke
     `TrainingHarness.run_bc_training()`) and confirm accuracy ≥ threshold (`0.8` by default).
  3. Execute anneal smoke: `python - <<'PY'` running `TrainingHarness.run_anneal(..., log_dir=Path('artifacts/m5/acceptance/logs'))` to emit `anneal_results.json`.
  4. Archive artefacts under `artifacts/m5/acceptance/` (`config_idle_v1.yaml`, `logs/anneal_results.json`,
     `summary_idle_v1.json`). Attach to acceptance report.
  5. Rollback drill: increase `anneal_accuracy_threshold` to force failure; verify harness stops after BC
     stage with `"rolled_back": true`.
  6. Update `data/bc_datasets/versions.json` when publishing new datasets (increment id, capture
     manifest + checksum, mark superseded entries `deprecated`).
  7. Evaluate promotion gates using `docs/ops/ANNEAL_PROMOTION_GATES.md` (BC accuracy ≥0.90 rolling mean, queue/social metrics ±15 % bands, telemetry thresholds). Flag “hold” and initiate rollback if any gate is breached.
  8. Monthly: `python scripts/audit_bc_datasets.py --versions data/bc_datasets/versions.json --exit-on-failure`.
  9. Monthly: `python scripts/run_anneal_rehearsal.py --exit-on-failure` (captures updated summary under `artifacts/m5/acceptance/summary_<timestamp>.json`).
  10. Pre-release bundle: include dataset manifest/checksums + audit report, anneal rehearsal artefacts, telemetry summary markdown, and dashboard screenshots.
  11. If `run_anneal_rehearsal.py` returns `HOLD`, freeze promotion, capture watcher output (`telemetry_watch.py --anneal-bc-min 0.9`) and escalate for dataset refresh or drift investigation. `FAIL` indicates BC gate regression and requires rollback.
  Dataset checksum helper:
  ```bash
  python - <<'PY'
  import hashlib, json, pathlib
  checks = json.loads(pathlib.Path("data/bc_datasets/checksums/idle_v1.json").read_text())
  failures = []
  for name, info in checks.items():
      sample = pathlib.Path(info['sample'])
      meta = pathlib.Path(info['meta'])
      digest = hashlib.sha256(sample.read_bytes() + meta.read_bytes()).hexdigest()
      if digest != info['sha256']:
          failures.append(f"{name}: expected {info['sha256']} got {digest}")
  if failures:
      raise SystemExit("Checksum mismatch\n" + "\n".join(failures))
  PY
  ```
- Phase C social rewards:
  - Toggle global stage: `python scripts/manage_phase_c.py set-stage configs/examples/poc_hybrid.yaml --stage C1 --in-place`.
  - Stage schedule overrides live under `training.social_reward_schedule`; e.g. `python scripts/manage_phase_c.py schedule configs/examples/poc_hybrid.yaml --override OFF --schedule 0:OFF --schedule 1:C1 --in-place` ensures rollouts stay OFF on cycle 0 and enable C1 afterwards.
  - Use `--output` to dry-run changes (`--output -` prints to stdout) before committing; the helper preserves existing schedules unless `--clear` is supplied.
- Narration controls:
  - Tune throttles via `telemetry.narration` (global/category cooldowns, dedupe window, rolling window limit). Example: `global_cooldown_ticks=30`, `category_cooldown_ticks.queue_conflict=30` keeps conflict narrations to ~1 every 30 ticks per queue.
  - Recent narrations surface in the observer dashboard (look for the "Narrations" panel); priority items (ghost steps) show a red `!` marker.
  - Snapshot payloads now include `narrations` (latest entries) and `narration_state`; export/import these when copying snapshots between shards to preserve throttle continuity.
  - For long-form audits, redirect the state to JSON: `python scripts/telemetry_summary.py <log> --format json | jq '.narrations'`.
- Console access: launch the Typer CLI in `scripts/` (placeholder) or connect via REST; default mode is `viewer`, escalate to `admin` only when lifecycle overrides are required. Attach a `cmd_id` to destructive commands so retries stay idempotent.
- Telemetry snapshot command: `telemetry_snapshot` returns per-agent job status, economy stock, employment queue metrics, and a `schema_version` string (currently `0.2.0`) so tooling can validate compatibility.
- `snapshot_inspect <path>` — read snapshot metadata (schema version, tick, identity, migrations) without applying it.
- `snapshot_validate <path> [--strict]` — load snapshot against the active config; with `--strict` it refuses to auto-migrate and surfaces the mismatch.
- `snapshot_migrate <path> [--output <dir>]` *(admin only)* — apply registered migrations and optionally re-save the migrated snapshot to a directory.
  - `snapshot` config block now drives behaviour:
    - `snapshot.storage.root` defines the default save location; `SimulationLoop.save_snapshot()`
      uses this when no directory is supplied.
    - `snapshot.autosave.cadence_ticks` enables periodic saves (minimum 100 ticks) with retention
      capped by `snapshot.autosave.retain`.
    - `snapshot.identity.policy_hash|policy_artifact|observation_variant|anneal_ratio` override
      runtime values used in telemetry and saved payloads. Release snapshots must set
      `policy_hash` explicitly so promotion gates can verify integrity.
    - `snapshot.migrations.handlers` auto-registers migration callables (`module:function`) that
      chain legacy `config_id` values to the current build; `auto_apply` toggles whether they run
      automatically.
    - `snapshot.guardrails.require_exact_config` controls whether mismatched `config_id`s fail
      fast; set to `False` only for manual recovery flows. `snapshot.guardrails.allow_downgrade`
      must be `True` before loading snapshots produced by newer schema versions.
    - Quick reference YAML lives at `docs/samples/snapshot_config_example.yaml`.
  - Console usage examples:
    - `snapshot_validate snapshots/release/snapshot-900.json` → run migrations if the config
      allows auto-apply; append `--strict` to verify without mutating.
    - `snapshot_migrate snapshots/legacy/snapshot-800.json --output tmp/migrated` → admin-only
      command that applies the registry chain, records audit metadata, and writes the migrated
      artifact.
    - `snapshot_validate --strict ...` returning `auto-migration disabled` indicates config
      guardrails blocked the attempt; flip `snapshot.migrations.auto_apply` or run
      `snapshot_migrate` in admin mode.
- The console warns when connecting to shards reporting a newer schema (e.g., `0.3.x`); upgrade the client before issuing mutating commands.
- Employment commands:
  - `employment_status` — dumps employment KPIs (pending exits, exit cap usage, queue limit) and latest queue contents.
  - `employment_exit review` — view backlog; `employment_exit approve <agent_id>` requests immediate exit; `employment_exit defer <agent_id>` clears the queue entry.
- Validation: run `python scripts/telemetry_check.py <payload.json>` to confirm consumer compatibility; consult `docs/telemetry/TELEMETRY_CHANGELOG.md` for schema history.
- Change management: follow `docs/EMPLOYMENT_DOCS_TEST_CHECKLIST.md` when modifying employment logic; reviewers should require the checklist is satisfied before merge.
- Observer dashboard: `scripts/observer_ui.py` launches a Rich-based console view of employment KPIs; see `docs/guides/OBSERVER_UI_GUIDE.md`.

## Promotion Playbook
1. **Pre-flight**
   - Verify `config_id` parity between release and shadow configs; observation variant must match (`SimulationConfig.require_observation_variant`).
   - Run `pytest` + linting (`ruff check src tests`, `mypy src`) and scenario smoke test `python scripts/run_simulation.py --tick-limit 1000`.
   - Confirm stability monitor KPIs meet thresholds for two consecutive windows: lateness ≤ baseline×2, starvation == 0, option-switch rate ≤ 25%.
   - Inspect console `telemetry_snapshot` stability block.
     `stability.alerts` must be empty when promoting and entries in
     `stability.metrics.thresholds.*` must match the release config. Treat
     `starvation_spike`, `reward_variance_spike`, and `option_thrash_detected`
     as hard holds until mitigated (raise hunger availability, reset policy, or
     widen clipping as described below).
2. **Promotion**
   - Snapshot current release (`snapshots/release/<timestamp>.pkl`) and shadow candidate.
   - Flip release pointer to the candidate via console command `promote_policy <checkpoint>` (TBD implementation) or manual config swap.
   - Monitor telemetry UI; ensure canaries stay green for two windows; log promotion in `ops/rollouts.md`.
3. **Rollback**
   - On canary breach, issue `rollback_policy --to <snapshot>` (TBD) or restore previous checkpoint manually.
   - Re-enable shadow training; file incident note referencing telemetry graphs and logs.

## Incident Response
- **Crash / Hang**: capture latest snapshot, collect stderr/stdout, restart shard with same config; open issue tagged `ops/crash` with timeline.
- **Reward Explosion**: inspect `reward_clip_events`; if unbounded, pause training, raise guardrails by lowering `clip_per_tick` in config, and re-run smoke tests.
- **Stability Alerts**:
  - `starvation_spike`: verify hunger configs and recent perturbations; consider
    rolling back or increasing food availability.
  - `reward_variance_spike`: usually signals PPO drift—reset optimisers, revisit
    clipping, and compare against baselines.
  - `option_thrash_detected`: policies are flapping between options; clamp
    scheduler noise, review option weights, and pause promotion until resolved.
- **Queue Deadlock**: use console `debug queues` (TBD) to inspect reservations; confirm queue fairness cooldown is active; if not, toggle feature flag and log issue.
- **Telemetry Backpressure**: check publisher backlog; if exceeds threshold, enable aggregation mode and archive raw stream for analysis.
- **Employment Backlog**: monitor `employment_status`. If `pending_count` exceeds `queue_limit`, issue `employment_exit review`, approve or defer entries, and document decisions in ops log. Manual approvals emit `employment_exit_manual_request`; ensure lifecycle processes the exit next tick.
- **Perturbation Control**: admin mode only. Use `perturbation_queue` to inspect
  active/pending events, `perturbation_trigger` (admin) to enqueue specs (provide
  `--targets`, optional `--starts_in`, `--magnitude`, `--location`), and
  `perturbation_cancel <event_id>` to stop events. Each command is recorded in
  `logs/console/*.jsonl` and emits `perturbation_started`,
  `perturbation_cancelled`, and `perturbation_ended` telemetry entries for
  observability.

## Conflict & Rivalry Runbook
- **Telemetry surfaces**: Use the observer dashboard conflict panel (rotations, queue deltas, latest rivalry events) alongside `conflict_status`, `queue_inspect`, and `rivalry_dump`. Expect `queue_history` entries with `tick`, `delta`, and `totals` keys—record tail snapshots during incidents.
- **Baseline references**: `docs/ops/queue_conflict_baselines.md` lists expected ghost-step/rotation counts and intensity sums. Compare against new captures in `docs/samples/queue_conflict_snapshot.json` and `docs/samples/rivalry_decay_snapshot.json` when validating fixes.
- **Alert interpretation**:
  - `queue_fairness_pressure`: ghost-step or rotation deltas exceeded guardrail for the tick window—inspect cooldown configuration and queue occupancy.
  - `rivalry_spike`: rivalry events at or above `avoid_threshold` in quick succession—use `rivalry_dump` for top edges and consider manual decay/reset.
  - `option_thrash_detected`: policy switch counts spiking; coordinate with policy team before relaxing thresholds.
- **Intervention steps**:
  1. Reproduce the scenario with `python - <<'PY'` snippet in the baselines doc to gather a fresh telemetry snapshot.
  2. Inspect queue state with `queue_inspect <object_id>` (look for repeated stall counts and cooldown backlogs).
  3. Review rivalries via `rivalry_dump [agent_id] --limit 5`; if a single edge dominates, consider manual decay (`world.rivalry_ledgers[...] .decay(...)` via admin console) or widening `avoid_threshold` temporarily.
  4. Adjust fairness knobs (`queue_fairness.cooldown_ticks`, `ghost_step_after`) only after confirming baseline drift. Document changes in ops logs.
  5. For repeated spikes, freeze promotion, gather telemetry snapshots + console outputs, and escalate.
- **Rollback guidance**: capture `telemetry_snapshot`, `conflict_status`, and watcher JSON. If conflict pressure stays out-of-band, revert to last known good config seed or disable scripted queues, then rerun smoke scenarios.

## Queue-Conflict Troubleshooting
- **Purpose**: ensure live or mixed-mode PPO runs maintain the conflict pressure captured in baselines.
- **Baselines**: reference `docs/ops/queue_conflict_baselines.md` for expected event counts and intensity sums. Queue-conflict mixed runs should stay within ±15% of the recorded intensity unless intentionally experimenting.
- **Validation**: run `telemetry_watch.py` with `--json` to capture alerts; set `--queue-events-min`, `--queue-intensity-min`, and social thresholds using the scenario table in `docs/ops/queue_conflict_baselines.md` (e.g., `--late-help-min 1` for employment punctuality). Keep the JSONL artefact with the training log.
- **Summary review**: use `telemetry_summary.py --format markdown` to produce a one-page digest; file under `ops/rollouts/<date>-<scenario>.md`.
- **Drift response**: if event counts or intensity drop below thresholds, pause promotion, rerun capture to confirm reproducibility, and notify the training lead. Investigate agent availability (missing scenario agents are the usual culprit) and rerun with `--rollout-auto-seed-agents` only as a temporary workaround.
- **CI guardrail**: GitHub Actions uploads `tmp/ci_phase4/{ppo_mixed.jsonl,summary.md,watch.jsonl}` for each run; inspect these artefacts when investigating regressions.
- **Canonical captures**: reference `artifacts/phase4/` for the latest checked-in mixed-mode logs, watch outputs, and summaries per scenario.
- **Soak reference**: `artifacts/phase4/queue_conflict_soak/summary.md` provides the latest alternating
  replay↔rollout drift snapshot (12-cycle run); use it as a benchmark during incident reviews.

## Telemetry Transport & Observer Workflow

- Observer telemetry emits schema version `0.9.x`; console and dashboard clients warn on newer majors but expect the new conflict history fields. Run `telemetry_snapshot` after upgrades to confirm the reported schema matches `0.9.x`.
- `config.telemetry.transport` selects the stream destination. Supported types:
  - `stdout`: development/debug. Payloads print to the shard stdout (NDJSON).
  - `file`: append-only JSONL file (set `file_path`). Parents are created automatically.
  - `tcp`: send to `host:port` (set `endpoint`). The transport retries on failure and surfaces status in the console snapshot.
- Buffering defaults (`transport.buffer.*`) bound the in-memory backlog. If `max_buffer_bytes` is exceeded the oldest payloads drop; drops are reported via telemetry (`telemetry_snapshot.transport.dropped_messages`).
- The console telemetry snapshot now includes a `transport` block exposing `connected`, `dropped_messages`, `last_success_tick`, `last_failure_tick`, and `last_error`. Use `telemetry_snapshot` in admin mode to inspect health.
- Admin runbook for outages:
  1. Check console snapshot (`telemetry_snapshot`) for `transport.connected` and `last_error`.
  2. If disconnected, tail the shard logs for tracebacks; re-run with `transport.retry.max_attempts` >0 when using flaky TCP endpoints.
  3. For persistent failure, switch config to `stdout` or `file` and rerun smoke test below while root-causing the external service.
- Smoke command after transport changes: `pytest tests/test_telemetry_client.py tests/test_observer_ui_dashboard.py tests/test_telemetry_stream_smoke.py tests/test_telemetry_transport.py`.
- Sample payload located at `docs/samples/telemetry_stream_sample.jsonl` demonstrates schema headers and transport metadata.
- Console conflict tooling: `conflict_status [--history N --rivalries N]` surfaces queue deltas, rivalry events, and stability alerts; `queue_inspect <object_id>` dumps active/cooldown entries; `rivalry_dump [agent_id] [--limit N]` reports rivalry intensities for audit logs. Record these outputs during incident response.
- Observer dashboard conflict panel highlights rotation counts and maintains a rolling table of fairness deltas plus latest rivalry events; include screenshots when drafting incident timelines.

## Tooling & Logs
- Metrics dashboard (TBD) pulls from telemetry diff stream; ensure schema version matches `docs/program_management/snapshots/ARCHITECTURE_INTERFACES.md`.
- Audit logs live in `logs/console/*.jsonl`; include `cmd_id`, issuer, result.
- Promotion history tracked in `ops/rollouts.md`; append entry per promotion or rollback.
- PPO telemetry tooling:
  - `python scripts/validate_ppo_telemetry.py <log> --relative`
- `python scripts/telemetry_watch.py <log> --follow --kl-threshold 0.2 --grad-threshold 5.0 --entropy-threshold -0.2 --reward-corr-threshold -0.5 [--queue-events-min INT] [--queue-intensity-min FLOAT] [--shared-meal-min INT] [--late-help-min INT] [--shift-takeover-max INT] [--chat-quality-min FLOAT] [--json]`
- `python scripts/telemetry_summary.py <log> --format markdown`
- `python scripts/audit_bc_datasets.py --versions data/bc_datasets/versions.json`
- `python scripts/run_anneal_rehearsal.py --exit-on-failure`
- `python scripts/telemetry_summary.py artifacts/m5/acceptance/logs/anneal_results.json --format markdown > artifacts/m5/acceptance/summary_release.md`
- `python scripts/telemetry_watch.py artifacts/m5/acceptance/logs/anneal_results.json --anneal-bc-min 0.9`

## Checklist Before Demos
- Validate console commands `spawn`, `setneed`, `force_chat`, `arrange_meet` in a dry-run town.
- Validate employment console flow: queue an agent (`employment_exit review`), approve/defer, and confirm telemetry reflects the change.
- Confirm narration throttle and privacy mode toggles respond instantly.
- Review KPIs vs. charter targets (self-sufficiency ≥70%, tenure ≥3 days, relationship coverage ≥60%).
- Prepare fallback config with perturbations disabled in case of instability.
