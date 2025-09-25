# Telemetry Command Quick Reference

## Validation & Drift
- `python scripts/validate_ppo_telemetry.py <log> --relative` — enforce schema and report drift (supports telemetry_version 1.1).
- `python scripts/telemetry_summary.py <log> [--baseline docs/samples/ppo_conflict_telemetry.jsonl] --format markdown` — generate run summaries for ops reports.

## Live Monitoring
- `python scripts/telemetry_watch.py <log> --follow --kl-threshold 0.2 --loss-threshold 1.0 --grad-threshold 5.0 --entropy-threshold -0.2 --reward-corr-threshold -0.5 --queue-events-min 25 --queue-intensity-min 45` — tail logs and emit alerts (append `--json` for machine-readable output).

## Sample Paths
- Canonical log: `docs/samples/ppo_conflict_telemetry.jsonl`
- CI harness outputs: `tmp/ci_capture/ppo_log.jsonl` (generated during pipeline runs)

- Baselines: `docs/ops/queue_conflict_baselines.md`
