# Telemetry Command Quick Reference

## Validation & Drift
- `python scripts/validate_ppo_telemetry.py <log> --relative` — enforce schema and report drift (supports telemetry_version 1.1).
- `python scripts/telemetry_summary.py <log> [--baseline docs/samples/ppo_conflict_telemetry.jsonl] --format markdown` — generate run summaries for ops reports. Summaries list social interaction fields (`shared_meal_events`, `late_help_events`, `shift_takeover_events`, `chat_success_events`, `chat_failure_events`, `chat_quality_mean`) **and** hygiene/rest counters (`utility_outage_events`, `shower_complete_events`, `sleep_complete_events`) so you can spot outages or stalled loops at a glance.

## Live Monitoring
- `python scripts/telemetry_watch.py <log> --follow --kl-threshold 0.2 --loss-threshold 1.0 --grad-threshold 5.0 --entropy-threshold -0.2 --reward-corr-threshold -0.5 --queue-events-min 25 --queue-intensity-min 45 --shared-meal-min 1 --late-help-min 0 --shift-takeover-max 2 --chat-quality-min 0.5 --utility-outage-max 0 --shower-complete-min 1 --sleep-complete-min 1` — tail logs and emit alerts (append `--json` for machine-readable output). Tune the new hygiene/rest thresholds per scenario (e.g., allow a non-zero outage count when intentionally toggling utilities).

## Sample Paths
- Canonical log: `docs/samples/ppo_conflict_telemetry.jsonl`
- CI harness outputs: `tmp/ci_capture/ppo_log.jsonl` (generated during pipeline runs)

- Baselines: `docs/ops/queue_conflict_baselines.md`
