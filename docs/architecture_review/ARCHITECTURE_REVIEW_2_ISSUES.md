# Architecture Review 2 — Issues Tracker

This tracker enumerates codebase gaps called out in `ARCHITECTURE_REVIEW_2.md` and captures ownership plus next steps.

| ID | Issue | Location | Priority | Status | Next action |
| --- | --- | --- | --- | --- | --- |
| ISS-1 | RNG serialisation uses `pickle` without integrity checks | `src/townlet/utils/rng.py:13`, `src/townlet/utils/rng.py:19` | P0 | Open | Design and implement a JSON/msgpack schema with signature/HMAC validation; add backwards-compatible migrator and bandit test. |
| ISS-2 | TelemetryPublisher remains a god-object covering aggregation, transforms, transport, and console I/O | `src/townlet/telemetry/publisher.py:57` | P1 | Open | Draft decomposition plan into Aggregator/Transform/Transport/Console services, gated behind DTO introduction. |
| ISS-3 | PolicyTrainingOrchestrator bundles PPO/BC/anneal logic and direct loop orchestration | `src/townlet/policy/training_orchestrator.py:48` | P1 | Planned | Extract discrete trainer strategies (`BCTrainer`, `PPOTrainer`, `AnnealManager`) and wire via factory registry. |
| ISS-4 | Observations still emitted via dict-heavy `ObservationBuilder` without typed DTOs | `src/townlet/observations/builder.py:44` | P1 | Open | Introduce Pydantic DTO surfaces and convert builder to stage-based pipelines (map/social/landmarks). |
| ISS-5 | Control-flow `assert` statements remain in runtime code paths | `src/townlet/telemetry/transport.py:179`, `src/townlet/policy/training_orchestrator.py:827` | P1 | Open | Replace with explicit error handling; add lint rule to block control-flow asserts in production modules. |
| ISS-6 | Import boundary enforcement missing despite `import-linter` dependency | `pyproject.toml:25` | P2 | Not started | Add `importlinter` contract configuration and wire into CI. |
| ISS-7 | No automated security gate (bandit/pip-audit) to catch dependency CVEs | `pyproject.toml:25` | P0 | Not started | Add tooling stage to CI and triage current dependency advisories. |
| ISS-8 | DTO/typed payloads absent for telemetry event publishing | `src/townlet/telemetry/publisher.py:95` | P1 | Not started | Define telemetry event schemas and update transports/adapters to adopt them. |

Status codes: **Open** – no active work; **Planned** – effort scheduled for upcoming branch; **In progress** – changes under development; **Blocked** – awaiting external dependency. Priority bands follow the review: **P0** immediate, **P1** within next month, **P2** within quarter.
