# Architecture Review 2 — Prioritised Work Packages

Work packages are ordered by sequencing impact and readiness. Each item references the related issues in `ARCHITECTURE_REVIEW_2_ISSUES.md`.

| Rank | Work package | Scope | Depends on | Exit criteria |
| --- | --- | --- | --- | --- |
| 1 | Secure RNG serialisation | Replace `pickle`-based RNG snapshotting with signed JSON/msgpack schema, add migration tooling, bandit regression test. | None | `encode_rng_state`/`decode_rng_state` free of `pickle`; bandit reports zero medium findings; corrupted payloads rejected with clear error. |
| 2 | DTO boundary introduction | Define Pydantic DTOs for telemetry events and observation payloads; update adapters and tests. | WP#1 | Telemetry/observation APIs emit typed models; `mypy --strict` passes for DTO modules; backwards compatibility documented. |
| 3 | Telemetry pipeline split | Decompose `TelemetryPublisher` into Aggregator, Transform, Transport Coordinator, Console Bridge; surface backpressure metrics. | WP#2 | No component >200 LOC; metrics exposed via telemetry sink; existing tests updated and new unit tests for each component. |
| 4 | Policy trainer strategies | Split `PolicyTrainingOrchestrator` into strategy objects for PPO/BC/Anneal; enforce stub-friendly tests. | WP#2 | Strategy classes <200 LOC; Torch-dependent tests skip cleanly; rollout capture respects stub detection. |
| 5 | CI guardrails ratchet | Add ruff/mypy gating on touched packages, plus bandit and pip-audit stages with error budgets. | WP#1 | CI blocks on new lint/type errors; security scans run on every PR; documented in contributor guide. |
| 6 | World services extraction | Introduce Queue/Employment/Economy/Relationship services with ActionHandler registry, trimming `world/grid.py` | WP#2, WP#5 | Service seams documented; targeted unit tests; world grid complexity reduced; import-linter boundaries enforced. |
| 7 | Stability analyzer modularisation | Extract `StabilityMonitor` analyzers (Fairness, Starvation, Rivalry, Reward Variance, Option Thrash) | WP#2, WP#5 | Analyzer classes unit tested; monitor class slimmed; promotion logic consumes analyzer outputs. |
| 8 | Import boundary enforcement | Define import-linter contracts for core/telemetry/world/policy boundaries and wire into CI. | WP#5 | Contracts pass in CI; exception process documented; ADR published. |

Use this ranking when planning the upcoming refactor branch to ensure dependency-heavy restructuring (e.g., DTO adoption) lands before downstream decompositions.
