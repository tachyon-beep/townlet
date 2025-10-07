# Architecture Review 2 — Risk Register

| Risk ID | Description | Cause / Evidence | Probability | Impact | Mitigation / Owner | Status |
| --- | --- | --- | --- | --- | --- | --- |
| R-01 | Remote code execution via crafted RNG snapshot payloads | `pickle.loads` in `decode_rng_state` accepts untrusted data (`src/townlet/utils/rng.py:19`) | High | Critical | Deliver Secure RNG serialisation work package (WP#1); add bandit gate. Owner: Core Platform | Open |
| R-02 | Telemetry outages or console backlog due to single-process publisher | `TelemetryPublisher` handles aggregation + transport + console in one 1.2k LOC class (`src/townlet/telemetry/publisher.py:57`) | Medium | High | Execute Telemetry pipeline split (WP#3); add backpressure metrics. Owner: Runtime Observability | Open |
| R-03 | Training harness unusable without Torch leading to CI breaks | Policy orchestrator still requires Torch for key flows (`src/townlet/policy/training_orchestrator.py:48`) and optional tests import Torch directly (`tests/test_ppo_utils.py:9`) | Medium | High | Complete policy trainer strategies (WP#4); extend stub coverage; document Torch vs stub workflows. Owner: ML Runtime | Planned |
| R-04 | World refactor stalls due to lack of explicit service seams | `world/grid.py` encapsulates multiple domains (`src/townlet/world/grid.py:140`) making incremental changes risky | Medium | High | Prioritise DTO boundary work (WP#2) to enable world services extraction (WP#6); invest in focused regression tests. Owner: World Simulation | Open |
| R-05 | Regression risk from absence of typed payloads at module boundaries | Observations/telemetry still rely on `dict[str, object]` payloads (`src/townlet/observations/builder.py:44`, `src/townlet/telemetry/publisher.py:95`) | High | Medium | Land DTO boundary introduction (WP#2); enforce `mypy --strict` on DTO modules. Owner: Core Platform | Open |
| R-06 | CI remains red due to missing lint/type/security gates | `pyproject.toml` lists tools but CI does not enforce them; control-flow asserts remain (`src/townlet/telemetry/transport.py:179`) | Medium | High | Implement CI guardrail ratchet (WP#5) and remove control-flow asserts. Owner: Dev Experience | Not started |

Probability/Impact scale: Low / Medium / High. Update this register as mitigation actions land or new risks emerge during the refactor.
