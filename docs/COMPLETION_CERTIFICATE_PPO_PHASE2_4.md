# Completion Certificate — PPO Integration Package (Phases 2–4)

**Project:** Townlet Conflict-Aware Training

**Milestone:** PPO Integration Package, Phases 2–4 (Rollout Ingestion, Telemetry, Ops Readiness)

**Date:** 2025-09-29

## Summary
- Hardened replay ingestion with rollout buffer integration, baseline metric wiring, and JSONL
  telemetry (`telemetry_version` 1.1).
- Added queue-conflict telemetry bridge: SimulationLoop reuse between captures, RolloutBuffer event
  totals, PPO logs (`queue_conflict_events`, `queue_conflict_intensity_sum`), and validator/tests
  covering the schema.
- Delivered scenario coverage for queue_conflict, employment_punctuality, rivalry_decay, and the
  observation baseline, capturing mixed-mode PPO artefacts and publishing baselines in
  `docs/ops/queue_conflict_baselines.md`.
- Expanded ops documentation (`docs/OPS_HANDBOOK.md`, `docs/ops/ROLLOUT_PPO_CHECKLIST.md`) with
  mixed-mode workflow, thresholds, and incident response guidance.
- CI workflow now exercises the mixed queue_conflict scenario end-to-end and uploads telemetry
  artefacts for audit.

## Validation
- `python -m pytest tests/test_training_replay.py::test_training_harness_rollout_queue_conflict_metrics`
- `python -m pytest tests/test_rollout_capture.py`
- `python scripts/capture_rollout.py configs/scenarios/queue_conflict.yaml --output tmp/ci_phase4`
- `python scripts/run_training.py configs/scenarios/queue_conflict.yaml --mode mixed --replay-manifest tmp/ci_phase4/rollout_sample_manifest.json --rollout-ticks 40 --epochs 1 --ppo-log tmp/ci_phase4/ppo_mixed.jsonl`
- `python scripts/validate_ppo_telemetry.py tmp/ci_phase4/ppo_mixed.jsonl`
- `python scripts/telemetry_watch.py tmp/ci_phase4/ppo_mixed.jsonl --json > tmp/ci_phase4/watch.jsonl`
- `python scripts/telemetry_summary.py tmp/ci_phase4/ppo_mixed.jsonl --format markdown > tmp/ci_phase4/summary.md`

## Outstanding Follow-Ups
- Add endurance tests alternating replay/rollout cycles to monitor queue-conflict drift over long
  runs.
- Run soak harness using `artifacts/phase4/` captures as baselines and record drift analytics in the
  acceptance report.

**Prepared by:** Townlet Engineering Team
