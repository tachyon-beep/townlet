# M5 Behaviour Cloning Alignment Notes (2025-09-30)

## Peer Review (RL Lead)
- Reviewed BC model architecture reuse (ConflictAwarePolicyNetwork) and trainer flow.
- Agreed on accuracy target (≥90%) and evaluation harness (`BCTrainer.evaluate`).
- Noted next steps: capture real scripted policies for queue_conflict, punctuality, rivalry.

## Manifest Validation
- Dry-run capture + curation executed using idle policy:
  ```bash
  python scripts/capture_scripted.py configs/examples/poc_hybrid.yaml --scenario idle --ticks 5 --output tmp/m5_idle_capture
  python scripts/curate_trajectories.py tmp/m5_idle_capture --output tmp/m5_idle_manifest.json --min-timesteps 1
  ```
- Manifest inspected (ensured `tags`, `quality_metrics` fields present). No files committed; outputs in `tmp/`.

## Anneal Dry-Run (Ops Preview)
- Command executed:
  ```bash
  source .venv/bin/activate
  python - <<'PY'
  # (see tmp/m5_anneal_demo3 script in shell history)
  PY
  ```
- Results logged to `tmp/m5_anneal_demo3/logs/anneal_results.json` with BC accuracy 1.0 and PPO summary.
- Confirms `run_anneal` telemetry/logging works with synthetic data before real deployment.

