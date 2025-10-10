---
title: DTO Migration Notes
status: draft
updated: 2025-10-10
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

## Pending Work

- Migrate ML adapters back ends (PolicyRuntime + PPO trainer) to consume DTO
  batches exclusively and record parity outputs.
- Complete Stage 6 documentation (ADR-001 refresh, migration guidance, release notes)
  and retire remaining world adapter shims once DTO-only parity is proven.
- Document notebooks/CLI updates once DTO-only path is live and share DTO sample payloads
  with downstream teams.
