# Milestone M4 – Rollout & Monitoring Plan

## Merge Strategy
- Continue using short-lived feature branches targeting `main`; legacy runtime has been removed, so no additional feature flag required.
- For high-risk changes touching `townlet.world`, stage the merge in a `release/m4-rollout` branch to allow integration testing before promoting to `main`.
- Tag the first facade-only release as `v0.9.0-m4` (or next available tag) to give downstream consumers a checkpoint for rollback.

## Validation Gate
- Before merging into `main`, run:
  - `.venv/bin/python -m pytest` (full suite or targeted observation/employment/telemetry suites during iteration).
  - `.venv/bin/ruff check src/townlet/world src/townlet/observations`.
  - `.venv/bin/mypy src/townlet/world/observation.py src/townlet/observations` (ongoing debt noted below).
  - For TCP telemetry deployments, run a handshake smoke test with `configs/demo/poc_demo_tls.yaml` (or staging config) to confirm TLS negotiation and cert loading before promotion.
- Capture telemetry snapshots via `scripts/run_simulation.py configs/examples/poc_hybrid.yaml --ticks 500 --telemetry-path tmp/rollout/telemetry.jsonl` and compare the `runtime_variant`, queue metrics, and observation tensors against the Phase 3 baselines.

## Monitoring Hooks
- Tick-health logging already emits `runtime_variant`, queue depth, and telemetry drop counts (`SimulationLoop.step`). Ensure log aggregation dashboards track these fields with alerts on:
  - Non-`facade` `runtime_variant` values.
  - Telemetry drop counts exceeding historical thresholds.
  - Employment exit queue length spikes.
- Telemetry payloads include `runtime_variant`; confirm dashboards ingest the field and add a quick visualization to verify all environments report `facade`.
- Alert on `telemetry_tcp_plaintext_enabled` warnings in log aggregation; plaintext transport should only appear in localhost development environments.
- For UI smoke testing, run `scripts/observer_ui.py configs/examples/poc_hybrid.yaml --ticks 0 --refresh 1.0` in staging once per release candidate to ensure dashboards render with the facade.

## Stakeholder Sign-off
- UI Team: confirm observer dashboard renders without legacy flag guidance.
- Telemetry Team: verify ingestion pipeline handles the simplified `runtime_variant` values.
- Training/Automation: run scheduled jobs with the facade build and report back before tagging.

## Open Risk/Follow-up
- `mypy src/townlet/world` still reports legacy debt (ObservationBuilder etc.); track under Phase 2 debt burn-down.
- No runtime feature flag available post-cleanup; rollback requires reverting the facade commits (documented in this plan).

