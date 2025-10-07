# Architecture Review 2 — Project Response Log

This memo tracks the actionable recommendations from `ARCHITECTURE_REVIEW_2.md` and records the Townlet team's current stance. Status values use:

- **Done** – implemented on main.
- **In progress** – work exists behind local branches or partial patches.
- **Planned** – acknowledged backlog item with near-term intent.
- **Not started** – no active effort.
- **Clarified** – recommendation satisfied by existing behaviour.

| Recommendation | Status | Project response |
| --- | --- | --- |
| Replace/guard RNG `pickle` serialisation | Not started | `decode_rng_state` still applies `pickle.loads` without validation (`src/townlet/utils/rng.py:19`). A backlog ticket will swap this for a JSON/msgpack schema with HMAC verification before the next release. |
| Gate Torch-dependent tests; exercise stub providers | Clarified | Torch-bound suites now skip cleanly when Torch is absent via `pytest.mark.skipif` predicates (`tests/test_ppo_utils.py:7`, `tests/test_policy_models.py:12`). Stub fallbacks are covered by `tests/test_fallbacks.py:28` after the recent regression fix, so we consider the recommendation satisfied without migrating to `pytest.importorskip`. |
| Patch CVE-flagged tooling deps; remove `assert` for flow control | Not started | Tooling audits are manual and there is no bandit/pip-audit integration or enforcement in CI (`pyproject.toml:34`). Control-flow `assert` statements remain in runtime code (e.g. `src/townlet/telemetry/transport.py:179`), so a remediation work package is required. |
| Introduce DTOs for telemetry/observations | Not started | Telemetry and observation plumbing continues to return nested dicts (`src/townlet/telemetry/publisher.py:58`, `src/townlet/observations/builder.py:46`). No Pydantic-backed boundary models exist yet. |
| Split `TelemetryPublisher` into aggregator/transform/transport/console seams | Not started | `TelemetryPublisher` remains a 1,200+ line god-object coordinating aggregation, buffering, console IO, and transport (`src/townlet/telemetry/publisher.py:20`). Decomposition is queued behind DTO work. |
| Decompose policy trainer into strategies; favour stubs in tests | In progress | `PolicyTrainingOrchestrator` is still monolithic (`src/townlet/policy/training_orchestrator.py:34`), but tests now guard stub usage (`tests/test_fallbacks.py:28`). Strategy extraction is planned for the upcoming refactor branch. |
| Enforce incremental CI gates (ruff/mypy/bandit/pip-audit) | Not started | Although `pyproject.toml` lists ruff/mypy configs, CI does not currently fail on lint/type debt and lacks bandit/pip-audit stages. We need to extend the workflow after the branch merge. |
| Break `WorldState` into bounded services w/ `ActionHandler` registry | Not started | `world/grid.py` still encapsulates employment, economy, rivalry, and queue orchestration (`src/townlet/world/grid.py:86`). Service seams have not been carved out. |
| Pipeline-ise `ObservationBuilder` (map/social/landmarks) | Not started | The builder continues to mix channel assembly, social snippets, and caching in a single class (`src/townlet/observations/builder.py:64`). No modular pipeline exists. |
| Extract analyzers from `StabilityMonitor.track` | Not started | `StabilityMonitor` contains multiple analysis branches (`src/townlet/stability/monitor.py:112`) and no dedicated analyzer classes. |
| Move domain defaults/validators out of config mega-class | Not started | `SimulationConfig` and related config models still own domain defaults and validation logic (`src/townlet/config/runtime.py:12`). Refactoring deferred. |
| Ratchet import boundaries with `import-linter` | Not started | `import-linter` is listed as an optional dev dependency but no contract configuration or CI step exists (`pyproject.toml:29`). |
| Author ADRs for serialisation, DTO boundaries, telemetry split, world services, stability analyzers, import rules | Not started | No new ADRs exist under `docs/architecture_review/` or `docs/engineering/` since the report; placeholder README files were added but not the requested decision records. |

## Next steps

1. File backlog tickets for the "Not started" items above, grouped by the phased roadmap (immediate, month, quarter).
2. Schedule a secure-serialisation spike before the next release cut and add a failing bandit test to avoid regressions.
3. Draft an ADR template so upcoming refactor work streams can land documentation alongside code.
