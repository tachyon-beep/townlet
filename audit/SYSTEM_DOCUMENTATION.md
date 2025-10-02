# System Documentation

## 1. Architecture Overview

Townlet implements a modular simulation stack centred on the `SimulationLoop` orchestrator. Configuration, world state, policy control, scheduler, rewards, telemetry, and stability subsystems are all assembled at runtime from a single YAML configuration entry point.

```mermaid
graph TD
    A[configs/*.yml<br/>SimulationConfig] --> B[SimulationLoop]
    B --> C[WorldState & Grid]
    B --> D[LifecycleManager]
    B --> E[PerturbationScheduler]
    B --> F[ObservationBuilder]
    B --> G[PolicyRuntime]
    B --> H[RewardEngine]
    B --> I[TelemetryPublisher]
    B --> J[StabilityMonitor & PromotionManager]
    B --> K[SnapshotManager]
    G --> L[Behavior controllers<br/>Replay/BC/PPO]
    I --> M[TransportBuffer]
    M --> N[Stdout/File/TCP Transport]
    I --> O[Console Router]
    O --> P[Townlet UI (rich dashboard)]
    K --> Q[Snapshot files]
    G --> R[Training scripts (run_training.py)]
    I --> S[Telemetry scripts (telemetry_watch.py)]
```

* **Simulation loop:** `townlet.core.sim_loop.SimulationLoop` builds a `WorldState`, policy runner, scheduler, reward engine, telemetry publisher, promotion, and stability monitors using a `SimulationConfig` model.
* **World subsystem:** `townlet.world` manages agents (`AgentSnapshot`), affordances, queues, rivalry, and employment state. Hooks allow affordance-specific Python callbacks.
* **Policy subsystem:** `townlet.policy` wraps scripted behaviour, replay buffers, BC datasets, and optional PPO networks (via PyTorch) behind `PolicyRuntime`.
* **Scheduler & Lifecycle:** `PerturbationScheduler` injects configured events; `LifecycleManager` controls spawn/exit logic and employment queue actions.
* **Telemetry & UI:** `TelemetryPublisher` captures per-tick artefacts, feeds console commands, and exports snapshots. Transport adapters ship JSON payloads to stdout, files, or TCP sockets. `townlet_ui` renders telemetry and issues console commands.
* **Snapshots & migrations:** `townlet.snapshots` persists/restores world, telemetry, and RNG state with migration support. Promotion manager records stability metrics and promotion events.
* **Automation scripts:** `scripts/` provides CLI utilities for running simulations, training harnesses, replay capture, telemetry analysis, and validation flows.

## 2. Technology Stack

| Layer | Technology | Notes & Upgrade Considerations |
| --- | --- | --- |
| Language | Python ≥ 3.11 | Strict mypy configuration, Ruff formatting; ensure compat when upgrading to 3.12. |
| Core libs | `pydantic>=2.11`, `pyyaml>=6`, `numpy>=2.3`, `pettingzoo>=1.24`, `typer>=0.9`, `rich>=13.7` | Pinning is wide; consider locking upper bounds before production. |
| Optional | `torch` (for PPO), UI uses `rich` | Guarded import for Torch; ensure GPU builds documented. |
| Tooling | `pytest`, `mypy`, `ruff`, GitHub Actions (`ci.yml`, `anneal_rehearsal.yml`) | CI runs lint, type-check, and tests. |
| Storage | Local filesystem snapshots/logs; future `.duskmantle/*` directories hint at Neo4j/Qdrant but not yet wired. | Document integration plan before enabling services. |

## 3. Key Features & Capabilities

- **Agent simulation core:** Tick-based grid world with affordances, hookable world events, relationship tracking, employment loops, and nightly resets.
- **Policy orchestration:** Scripted controllers, replay datasets, behaviour cloning trainer, and PPO scaffolding (advantage computation, loss functions, annealing, policy promotion).
- **Configurable perturbations:** Weighted random or manual events (blackouts, outages, arranged meetings) with guardrails on concurrency, cool-downs, and targeting.
- **Telemetry surface:** High-volume JSON snapshots including KPIs, queue metrics, rivalry, narration, and promotion state; console bridge enables interactive management.
- **Snapshotting & migrations:** Full-state capture with RNG streams, relationship ledgers, and migration registry to ensure compatibility across releases.
- **Operational tooling:** Dozens of CLI scripts for rollout capture, annotation curation, telemetry summarisation, anneal rehearsals, soak tests, and reward analysis.
- **Rich observer UI:** Terminal dashboard that renders telemetry panels, queue health, conflict history, and narration timeline while issuing console commands.

## 4. Data Architecture

- **In-memory domain models:** Dataclasses (`AgentSnapshot`, `InteractiveObject`, `RunningAffordance`, `ScheduledPerturbation`, `Lifecycle` tickets) represent simulation entities. `WorldState` aggregates agent maps, affordance manifests, employment state, and event queues.
- **Configuration models:** Pydantic models in `townlet.config.loader` define validation rules for feature flags, rewards, perturbations, telemetry, stability guardrails, and snapshot settings. YAML documents resolve to these structured models.
- **Telemetry payloads:** Structured dictionaries capturing queue metrics, rivalry stats, policy state, KPIs, perturbations, console results, and transport health. `TelemetryPublisher.export_state` returns canonical payloads for persistence or UI consumption.
- **Snapshots:** `SnapshotState` serialises world/telemetry/promotion/lifecycle data to JSON line files. Migration registry upgrades payloads; RNG streams preserve deterministic replays.
- **Persistent artefacts:** Logs under `logs/`, snapshot archives under configurable roots, BC datasets under `data/bc_datasets/`, and analysis outputs under `artifacts/`.
- **External stores:** No direct Neo4j or Qdrant integration exists yet; `.duskmantle/neo4j` and `.duskmantle/qdrant` directories act as placeholders for future ingestion pipelines.

## 5. API & Interface Layer

- **CLI entry points:** Scripts use `argparse` to expose simulation (`run_simulation.py`), training (`run_training.py`), anneal rehearsals, telemetry watchers, replay capture, BC audits, and validation utilities. Inputs are YAML configs and optional flags; outputs are logs, JSON summaries, or console prints.
- **Console bridge:** `ConsoleRouter` registers commands for telemetry snapshots, employment management, perturbation control, policy promotion, snapshot operations, and admin actions (kill, possess). Commands return JSON-compatible dicts.
- **Observer UI:** `townlet_ui` consumes telemetry snapshots via `TelemetryClient`, renders Rich panels, and issues `ConsoleCommand` payloads through `ConsoleCommandExecutor`.
- **Policy interfaces:** `PolicyRuntime` exposes `decide`, `post_step`, `flush_transitions`, and `register_ctx_reset_callback` for simulation integration. PPO utilities provide advantage computation, clipping, and optimiser hooks for training scripts.
- **Telemetry transport:** Factory supports stdout, newline-delimited file append, or raw TCP sockets (no TLS/auth). Buffering ensures batch flush; overflow currently drops oldest payloads.
- **No public REST/gRPC APIs**: All interactions are local CLI or console sockets; future service surfaces would need explicit design.

## 6. Configuration & Deployment

- **Config sources:** YAML files in `configs/examples`, `configs/affordances`, `configs/perturbations`, `configs/scenarios`. `SimulationConfig` enforces schema, snapshot guardrails, anneal policy, and telemetry transport parameters.
- **Environment variables:** Minimal usage—module-level constants rely on config. Telemetry file transport resolves to `logs/` by default. Consider centralising env var support if deploying to cloud runtimes.
- **Deployment:** No Dockerfile or docker-compose provided. CI expects local Python environment. To containerise, define images bundling dependencies, config volumes, and persistent snapshot mounts.
- **Runtime assets:** Snapshots saved to configurable directories; console audit logs stored at `logs/console/commands.jsonl`. Ensure directories exist with appropriate permissions.
- **Startup sequence:**
  1. Load YAML config via `load_config`.
  2. `SimulationLoop` seeds RNG streams, constructs world/policy/telemetry/scheduler.
  3. Optional snapshot load via console.
  4. Run loop (`run()`/`step()`), producing telemetry and handling perturbations each tick.

## 7. Data Flow Scenarios

### 7.1 Simulation Tick Pipeline
1. `SimulationLoop.step()` increments tick, syncs world tick, and processes lifecycle respawns.
2. Pending console commands drain into the world; results feed back to telemetry.
3. `PerturbationScheduler.tick()` may activate events; `PolicyRuntime.decide()` selects agent actions (scripted + anneal blends).
4. World applies actions, resolves affordances, performs nightly resets, and updates agent episodes.
5. `LifecycleManager.evaluate()` detects terminations; `RewardEngine.compute()` calculates rewards and breakdowns.
6. Observation batches built via `ObservationBuilder`, passed to policy for transition flushing.
7. Telemetry publishes tick snapshot, updates KPIs, and records perturbation/promotion state.
8. `StabilityMonitor` ingests metrics; `PromotionManager` evaluates promotion gates.

### 7.2 Snapshot Save/Load
1. `SimulationLoop.save_snapshot()` collects world, lifecycle, telemetry, scheduler, stability, promotion, RNG streams, and identity into `SnapshotState`.
2. `SnapshotManager.save()` writes JSON line files under configured root with identity metadata.
3. Loading calls `SnapshotManager.load()` with guardrails; telemetry and world import state; RNG streams restored; stability/promotion optionally reset.
4. Policy registers active policy hash and anneal ratio to maintain alignment.

### 7.3 Policy Training Flow
1. Scripts (`run_training.py`, `promotion_evaluate.py`, etc.) load configs and instantiate `PolicyRuntime` with replay/batch datasets.
2. `RolloutBuffer` collects transitions; `compute_gae`, `policy_surrogate`, and `clipped_value_loss` compute PPO objectives.
3. BC datasets loaded via `load_bc_samples`; `BCTrainer` updates imitation models.
4. Training outputs telemetry (versioned by `PPO_TELEMETRY_VERSION`), metrics JSON, and promotion artefacts.

### 7.4 Telemetry & UI Loop
1. `TelemetryPublisher.publish_tick()` batches metrics, events, snapshots, and stability data.
2. `TransportBuffer` accumulates JSON lines; flush interval sends to configured transport (stdout/file/TCP).
3. `townlet_ui.TelemetryClient` polls transport stream (typically file/stdout tail) and renders dashboards.
4. UI commands send JSON envelopes to console router; world/components execute and return results for rendering.

*No persistent storage in Neo4j/Qdrant is yet implemented; instrumentation directories exist but integration code is absent.*

## 8. Dependencies & Integration Points

- **Internal packages:** `townlet` (simulation core), `townlet_ui` (observer console), `scripts` (ops tooling), `tests` (pytest suites).
- **External libraries:** NumPy, Pydantic, YAML, PettingZoo, Typer, Rich, optional PyTorch, `socket` for TCP telemetry.
- **Third-party services:** None at runtime; future plans may include Neo4j (relationship analytics) and Qdrant (vector search) referenced in docs but not in code.
- **Inter-module communication:** Pure function/method calls; no message queues. Telemetry uses in-process buffer plus file/TCP writer. Console commands operate as function calls invoked by UI executor.
- **File system integration:** Affordance manifests, snapshots, BC datasets, and telemetry logs rely on relative paths—ensure path whitelisting in production.

## 9. Development & Operations

- **Environment setup:**
  - `python -m venv .venv && source .venv/bin/activate`
  - `pip install -e .[dev]`
- **Local workflows:**
  - Run simulation: `python scripts/run_simulation.py --config configs/examples/poc_hybrid.yaml`
  - Launch training stub: `python scripts/run_training.py --config ...`
  - Observe telemetry: `python scripts/telemetry_watch.py --config ...`
- **Testing & validation:**
  - `pytest` (fast unit suites under `tests/`)
  - `pytest -m "not slow"` to skip soak scenarios
  - `ruff check src tests` & `mypy src`
- **Continuous Integration:** `.github/workflows/ci.yml` executes lint, type, unit test stages; `anneal_rehearsal.yml` covers anneal promotion checks.
- **Logging & Monitoring:** Rich logging is sparse; telemetry data doubles as monitoring. Console audit file logs commands for traceability. No external observability stack yet; consider hooking Telemetry TCP stream into log aggregation.
- **Deployment gaps:** No container definitions, service manifests, or secret management. Security hardening (auth, TLS, filesystem sandboxing) required before exposing console/telemetry over networks.

---
