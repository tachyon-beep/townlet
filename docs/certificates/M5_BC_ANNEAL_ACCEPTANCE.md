# M5 Behaviour Cloning & Anneal – Acceptance Report

## Overview
- **Milestone:** M5 – Behaviour Cloning & Anneal
- **Phase:** 5.5 – Promotion Governance & Close-out
- **Status:** Complete (2025-10-06)
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
  - `summary_idle_v1_rehearsal.json`
  - `logs/anneal_watcher_output.jsonl`
- **Release bundle** collected under `artifacts/m5/release_bundle/`:
  - `playbooks/` (`ANNEAL_PROMOTION_GATES.md`, `ANNEAL_TRAINING_PLAN.md`, `OPS_HANDBOOK.md`)
  - `outputs/` (anneal results, summaries, watcher capture)
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
1. Hand off release bundle to operations archive (ticket M5-OPS-ACQ-01).
2. Schedule first monthly dataset audit to monitor drift (owner: Ops).

*Prepared 2025-09-30, updated 2025-10-06 for milestone close-out.*
