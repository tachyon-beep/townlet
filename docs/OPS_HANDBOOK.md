# Townlet Operations Handbook (v0.1)

## Run Modes & Entry Points
- `python scripts/run_simulation.py --config <yaml>` — starts a headless shard; honour `config_id` and observation variant declared in the file. Attach `--tick-limit` during smoke checks to bound runtime.
- `python scripts/run_training.py --config <yaml>` — spins the PPO training harness; ensure release and shadow checkpoints write to distinct directories (`snapshots/rel`, `snapshots/shadow`).
- Console access: launch the Typer CLI in `scripts/` (placeholder) or connect via REST; default mode is `viewer`, escalate to `admin` only when lifecycle overrides are required. Attach a `cmd_id` to destructive commands so retries stay idempotent.

## Promotion Playbook
1. **Pre-flight**
   - Verify `config_id` parity between release and shadow configs; observation variant must match (`SimulationConfig.require_observation_variant`).
   - Run `pytest` + linting (`ruff check src tests`, `mypy src`) and scenario smoke test `python scripts/run_simulation.py --tick-limit 1000`.
   - Confirm stability monitor KPIs meet thresholds for two consecutive windows: lateness ≤ baseline×2, starvation == 0, option-switch rate ≤ 25%.
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
- **Queue Deadlock**: use console `debug queues` (TBD) to inspect reservations; confirm queue fairness cooldown is active; if not, toggle feature flag and log issue.
- **Telemetry Backpressure**: check publisher backlog; if exceeds threshold, enable aggregation mode and archive raw stream for analysis.

## Tooling & Logs
- Metrics dashboard (TBD) pulls from telemetry diff stream; ensure schema version matches `docs/ARCHITECTURE_INTERFACES.md`.
- Audit logs live in `logs/console/*.jsonl`; include `cmd_id`, issuer, result.
- Promotion history tracked in `ops/rollouts.md`; append entry per promotion or rollback.

## Checklist Before Demos
- Validate console commands `spawn`, `setneed`, `force_chat`, `arrange_meet` in a dry-run town.
- Confirm narration throttle and privacy mode toggles respond instantly.
- Review KPIs vs. charter targets (self-sufficiency ≥70%, tenure ≥3 days, relationship coverage ≥60%).
- Prepare fallback config with perturbations disabled in case of instability.
