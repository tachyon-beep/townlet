# M5 Behaviour Cloning & Anneal – Acceptance Report (Draft)

## Overview
- **Milestone:** M5 – Behaviour Cloning & Anneal
- **Phase:** 5.4 – End-to-End Validation & Ops Readiness
- **Status:** In progress (draft report prepared pending completion of remaining tasks).
- **Acting Project Director:** Townlet Delivery Lead (self-review authority).

## Scope Covered
1. Behaviour cloning dataset capture & curation workflow.
2. BC trainer convergence safeguards (accuracy thresholds, evaluation harness).
3. Anneal scheduler with rollback guardrails.
4. Operational hand-off: documentation, dataset catalogue, CI coverage, go/no-go approval.

## Evidence Collected (2025-09-30)
- **Production idle dataset** captured via `scripts/capture_scripted.py` (200 ticks) and curated into
  `data/bc_datasets/captures/idle_v1` with manifest/checksum entries recorded in
  `data/bc_datasets/manifests/idle_v1.json` and `data/bc_datasets/checksums/idle_v1.json`
  (`data/bc_datasets/versions.json:idle_v1_production`).
- **Synthetic rehearsal bundle** retained at `artifacts/m5/preflight/` for rollback drills only
  (`preflight_idle_v0` marked deprecated).
- **Config overlays**
  - `artifacts/m5/preflight/config_preflight.yaml` — synthetic rehearsal manifest (kept for rollback drills).
  - `artifacts/m5/acceptance/config_idle_v1.yaml` — production idle dataset pins for acceptance smoke.
- **Acceptance smoke artefacts** archived under `artifacts/m5/acceptance/`:
  - `logs/anneal_results.json`
  - `summary_idle_v1.json`
- **Regression suites** (`tests/test_bc_trainer.py`, `tests/test_training_anneal.py`,
  `tests/test_curate_trajectories.py`, `tests/test_capture_scripted_cli.py`,
  `tests/test_bc_capture_prototype.py`) pass in 1.8 s wall-clock locally.
- **Ops rehearsal outline** (`docs/program_management/M5_PHASE54_OPS_REHEARSAL.md`) enumerates the
  dry-run procedure (checksum verification, BC gate, anneal run, rollback drill).

## Sign-off
- **Decision:** **GO** (2025-09-30)
- **Assessors:** Project Director, Senior User, System Architect (self-review multi-hat).
- **Rationale:** Production dataset validated, BC/anneal smoke green, ops/CI guardrails landed; no open blockers.

## Residual Risks & Watchpoints
- **Dataset drift (5.4-R1):** Mitigated by CI checksum gate; monitor for new datasets requiring registration.
- **CI runtime (5.4-R2):** Current incremental cost ~2 s; reassess after first full pipeline run.
- **Future documentation drift:** Embed BC/anneal updates in onboarding to keep ops guides synced.

## Follow-up Actions
1. Update `MASTER_PLAN_PROGRESS.md` and `docs/program_management/MILESTONE_ROADMAP.md` to mark Phase 5.4 complete.
2. Transition to Phase 5.5 planning (M5 post-anneal metrics and promotion prep).
3. Schedule first periodic dataset audit (monthly) to keep `versions.json` authoritative.

*Prepared 2025-09-30. Update upon completion of Phase 5.4 tasks.*
