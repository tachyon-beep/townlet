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
- ML smoke harness (`tests/policy/test_dto_ml_smoke.py`) validates random-weight
  parity between DTO and legacy feature tensors; exposed via `tox -e ml`.
- Lightweight training config (`configs/training/dto_smoke.yaml`) supports fast
  rollout/ML experiments.

## Pending Work

- Migrate ML adapters back ends (PolicyRuntime + PPO trainer) to consume DTO
  batches exclusively.
- Replace legacy observation payloads in `SimulationLoop` artifacts/telemetry.
- Document notebooks/CLI updates once DTO-only path is live.
