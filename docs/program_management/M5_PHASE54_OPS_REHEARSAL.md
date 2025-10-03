# M5 Phase 5.4 Ops Rehearsal Outline

This outline scopes the dry-run that must occur before Phase 5.4 acceptance. It now defaults to the
production idle dataset (`data/bc_datasets/captures/idle_v1`). Keep the earlier synthetic bundle
(`artifacts/m5/preflight/`) available for rollback drills or CI sandboxing.

## Preconditions
- Validation environment activated (`source .venv/bin/activate`).
- Production manifest: `data/bc_datasets/manifests/idle_v1.json` (accepted entries = 2).
- Checksum sheet: `data/bc_datasets/checksums/idle_v1.json`.
- Training config overlay derived from `configs/examples/poc_hybrid.yaml` pointing to the production
  manifest (create copy under `artifacts/m5/acceptance/config_idle_v1.yaml`).
- Optional: synthetic rehearsal bundle under `artifacts/m5/preflight/` if you need to simulate
  rollback failure paths quickly.

## Rehearsal Flow
1. **Dataset integrity check**
   - Run `python - <<'PY' ...` to recompute sha256 for accepted samples.
   - Compare against `data/bc_datasets/checksums/idle_v1.json`; abort if any mismatch.
2. **BC trainer verification**
   - `python - <<'PY'` snippet calling `TrainingHarness(config).run_bc_training()` with the pinned
     manifest; confirm `accuracy >= 0.8` (threshold matches overlay).
3. **Anneal smoke**
   - Invoke `python scripts/run_training.py artifacts/m5/acceptance/config_idle_v1.yaml --mode mixed --epochs 1`
     with `--ppo-log artifacts/m5/acceptance/ppo_idle_v1.jsonl`.
   - Inspect `artifacts/m5/acceptance/logs/anneal_results.json` for `{"mode": "bc", "passed": true}` and
     `{ "mode": "ppo", "loss_total": ... }` entries.
4. **Rollback drill**
   - Modify overlay threshold to `0.95` (forcing failure) and rerun anneal; verify harness exits
     after BC stage with `"rolled_back": true`.
5. **Ops artefact capture**
   - Copy manifest, checksum file, anneal logs, PPO log (if captured), and acceptance summary into
     `artifacts/m5/acceptance/` for inclusion in the acceptance report (baseline bundle: `config_idle_v1.yaml`, `logs/anneal_results.json`, `summary_idle_v1.json`).

## Runtime Benchmarks
- Local `pytest` (BC + anneal suites) runtime: ~1.8s wall-clock (see preflight notes). Use as
  baseline when wiring CI.

## Exit
- Update acceptance report with outcomes of the rehearsal (pass/fail, artefact paths).
- If any step fails, log the remedial action before proceeding to Phase 5.4 execution.
