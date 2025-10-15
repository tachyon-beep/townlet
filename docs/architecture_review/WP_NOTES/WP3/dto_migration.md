---
title: DTO Migration Notes
status: draft
updated: 2025-10-11
---

# DTO Migration Notes

This living document tracks how downstream consumers should adopt the DTO-only
policy observation flow introduced in WP3.

## Scope

- Policy decision providers (scripted + ML backends)
- Telemetry transports and dashboards consuming policy metadata/anneal events
- Training harnesses, replay exporters, and CLI tooling (Townlet + notebooks)

## Status

- DTO schema v0.2.0 ships richer agent/global context (needs, wallet, job, queue,
  employment, anneal).
- Simulation loop emits DTO-driven `policy.metadata`, `policy.possession`,
  `policy.anneal.update` events; telemetry dispatcher caches the latest payloads.
- Telemetry guardrails added (`tests/core/test_no_legacy_observation_usage.py`,
  `tests/test_telemetry_surface_guard.py`) to prevent regressions and expose the new
  DTO caches (`latest_policy_metadata_snapshot`, `latest_observation_envelope`).
- ML smoke harness (`tests/policy/test_dto_ml_smoke.py`) validates random-weight
  parity between DTO and legacy feature tensors; exposed via `tox -e ml`.
- Lightweight training config (`configs/training/dto_smoke.yaml`) supports fast
  rollout/ML experiments.

### Parity Verification — 2025-10-11

- Commands:
  - `pytest tests/core/test_sim_loop_dto_parity.py -q`
  - `pytest tests/policy/test_dto_ml_smoke.py -q`
  - `pytest tests/world/test_world_context_parity.py -q`
- All suites passed, confirming:
  - DTO envelopes reproduce queue metrics, employment snapshots, reward totals,
    and economy/anneal context for the first three ticks of the baseline config.
  - Random-weight Torch logits match between DTO features and legacy builder
    tensors (feature_dim=81, map_shape=(4, 11, 11)).
  - WorldContext exports remain in parity with service snapshots for queues,
    relationships, and economy metrics.
- No schema drift detected; existing baselines in
  `docs/architecture_review/WP_NOTES/WP3/dto_parity/` remain valid.

## Pending Work

- Migrate ML adapters back ends (PolicyRuntime + PPO trainer) to consume DTO
  batches exclusively and record parity outputs.
- Complete Stage 6 documentation (ADR-001 refresh, migration guidance, release notes)
  and retire remaining world adapter shims once DTO-only parity is proven.
- Document notebooks/CLI updates once DTO-only path is live and share DTO sample payloads
  with downstream teams.
