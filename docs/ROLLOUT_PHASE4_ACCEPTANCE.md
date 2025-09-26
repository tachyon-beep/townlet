# Phase 4 Acceptance Report — Rollout & Telemetry Hardening

**Project:** Townlet Conflict-Aware Training

**Milestone:** PPO Integration — Phase 4 (Scenario Rollout Bridge & Ops Readiness)

**Date:** 2025-09-29

## Scope
Phase 4 finalises the rollout-to-PPO bridge introduced in Phases 2–3. We exercised the mixed-mode
training loop across the curated scenario catalog, recorded telemetry artefacts, and updated the ops
runbook with queue-conflict guardrails.

## Scenario Coverage Summary
| Scenario | Mode | Rollout Ticks | Queue Conflict Events | Intensity Sum | PPO Log | Watch Log | Summary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| queue_conflict | mixed (replay→rollout) | 40 | 32.0 | 52.75 | `artifacts/phase4/queue_conflict/ppo_mixed.jsonl` | `artifacts/phase4/queue_conflict/watch.jsonl` | `artifacts/phase4/queue_conflict/summary.md` |
| employment_punctuality | mixed (replay→rollout) | 60 | 39.0 | 58.50 | `artifacts/phase4/employment_punctuality/ppo_mixed.jsonl` | `artifacts/phase4/employment_punctuality/watch.jsonl` | `artifacts/phase4/employment_punctuality/summary.md` |
| rivalry_decay | mixed (replay→rollout) | 50 | 32.0 | 48.00 | `artifacts/phase4/rivalry_decay/ppo_mixed.jsonl` | `artifacts/phase4/rivalry_decay/watch.jsonl` | `artifacts/phase4/rivalry_decay/summary.md` |
| observation_baseline | rollout control | 30 | 0.0 | 0.00 | `artifacts/phase4/observation_baseline/ppo_rollout.jsonl` | _n/a_ | `artifacts/phase4/observation_baseline/summary.md` |

Baseline thresholds and interpretation guidance live in `docs/ops/queue_conflict_baselines.md`.

## Telemetry Validation
- Schema validation via `scripts/validate_ppo_telemetry.py` passes for every scenario log.
- `scripts/telemetry_watch.py` (JSON mode) captured replay and rollout epochs, confirming queue
  conflict totals meet the recorded baselines.
- `scripts/telemetry_summary.py --format markdown` produced the summaries above; these should be
  archived alongside the NDJSON logs for audit.

## CI Integration
- `.github/workflows/ci.yml` runs the mixed-mode queue_conflict scenario and now uploads
  `tmp/ci_phase4/{ppo_mixed.jsonl,watch.jsonl,summary.md}` as workflow artefacts. The watch command
  writes JSONL output so ops can diff runs without re-tailing.

## Documentation Updates
- `docs/OPS_HANDBOOK.md` now details the mixed-mode workflow, queue-conflict troubleshooting steps,
  and links to the new artefacts.
- `docs/WORK_PACKAGE_PPO_PHASES_2_4.md` reflects the completion of Phases 2 and 3 plus the Phase 4
  telemetry bridge plan.
- `artifacts/phase4/README.md` documents the curated capture set and repro commands for future
  refreshes.

## Soak Validation
- Ran 12 alternating replay ↔ rollout cycles via
  `scripts/run_mixed_soak.py configs/scenarios/queue_conflict.yaml --baseline-dir artifacts/phase4/queue_conflict --output-dir artifacts/phase4/queue_conflict_soak --cycles 12 --rollout-ticks 40`.
- Artefacts captured under `artifacts/phase4/queue_conflict_soak/` (`ppo_soak.jsonl`, `watch.jsonl`,
  `summary.md`). Watch thresholds matched the ops playbook (KL 0.5, grad 5, queue minima 28/45) with
  no alerts.
- Drift summary (`summary.md`) vs. the baseline rollout shows queue-conflict metrics unchanged
  (events/intensity delta = 0) and acceptable movement on loss/gradient statistics (≤+8.5% loss
  total, +0.67 grad_norm). Cycle IDs/log offsets progressed as expected across the soak.

## Acceptance Checklist
- [x] Mixed-mode PPO run succeeds for each scenario with queue-conflict telemetry recorded.
- [x] Watcher and summary artefacts exported and referenced in ops docs.
- [x] CI wiring validated manually; artefact upload enabled for automation.
- [x] Ops runbook updated with thresholds and response playbook.
- [x] Alternating replay/rollout soak captured with drift analysis recorded.

**Prepared by:** Townlet Engineering Team — PPO Integration Task Force
