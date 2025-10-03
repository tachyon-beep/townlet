# System Documentation

## 1. Architecture Overview

Townlet is organised around a tick-based orchestrator that wires together configuration, world simulation, policy control, telemetry, and stability services. All runtime components are built from a single `SimulationConfig` loaded from YAML.

```mermaid
graph TD
    Config[SimulationConfig<br>configs/*.yml] --> Loop[SimulationLoop]
    Loop --> World[WorldState
(world/grid.py)]
    Loop --> Lifecycle[LifecycleManager
(lifecycle/manager.py)]
    Loop --> Scheduler[PerturbationScheduler
(scheduler/perturbations.py)]
    Loop --> Observations[ObservationBuilder
(observations/builder.py)]
    Loop --> Policy[PolicyRuntime
(policy/runner.py)]
    Loop --> Rewards[RewardEngine
(rewards/engine.py)]
    Loop --> Telemetry[TelemetryPublisher
(telemetry/publisher.py)]
    Loop --> Stability[StabilityMonitor + PromotionManager]
    Telemetry --> Transport[TransportBuffer + TransportClient]
    Telemetry --> ConsoleRouter[Console Router
(console/handlers.py)]
    Transport --> Outputs[Stdout/File/TCP streams]
    ConsoleRouter --> UI[townlet_ui dashboard]
    World --> Snapshots[SnapshotManager]
    Snapshots --> Storage[Snapshot files]
    Policy --> Training[scripts/run_training.py]
```

* **Core loop** (`src/townlet/core/sim_loop.py`): builds RNG streams, world state, perturbation scheduler, observation builders, policies, rewards, telemetry, and stability/promotion managers, then advances ticks.
* **World subsystem** (`src/townlet/world`): `WorldState` manages agents, affordances, queues, rivalry, employment flows, and console hookups. Queue and relationship ledgers live in sibling modules.
* **Policy subsystem** (`src/townlet/policy`): wraps scripted agents, replay datasets, behaviour cloning trainer, and PPO scaffolding behind `PolicyRuntime`.
* **Telemetry & console** (`src/townlet/telemetry`, `src/townlet/console`): collect per-tick metrics, publish JSON payloads via transports, and expose console handlers for admin actions.
* **Snapshots & recovery** (`src/townlet/snapshots`): serialise world, telemetry, RNG state, and promotion metadata; support migrations between config versions.
* **UI & tooling** (`src/townlet_ui`, `scripts/`): observer dashboard consumes telemetry snapshots; CLI utilities orchestrate simulations, training, replay capture, telemetry summarisation, and dataset audits.
* **Process model**: single Python process hosting the simulation loop, console router, and telemetry flush worker threads; no container or service decomposition defined yet.

## 2. Technology Stack

| Layer | Technology & Version | Notes |
| --- | --- | --- |
| Language | Python 3.11 (strict mypy config) | Ensure compatibility before upgrading to 3.12+. |
| Core libraries | `pydantic>=2.11`, `numpy>=2.3`, `pettingzoo>=1.24`, `pyyaml>=6.0`, `rich>=13.7`, `typer>=0.9` | PettingZoo integration currently stubbed in policy layer. |
| Optional | `torch` (PPO models), `pytest`, `ruff`, `mypy` | Torch import guarded; PPO unusable without GPU/CPU wheel present. |
| Tooling | GitHub Actions, CLI scripts, Rich TUI | No Docker/Kubernetes assets supplied. |
| Storage | Local filesystem snapshots/logs, BC datasets under `data/` | `.duskmantle/*` directories reserved for future Neo4j/Qdrant integration but unused. |

Upgrade considerations: pin upper bounds once features stabilise; evaluate moving to `pydantic` profiles for runtime validation cost; adopt dependency lock files for reproducible builds.

## 3. Key Features & Capabilities

- **Tick-driven world simulation** with employment loops, affordance queues, rivalry tracking, nightly resets, and configurable perturbations.
- **Policy orchestration** supporting scripted controllers, behaviour cloning replay, annealed policy blending, and placeholder PPO networks.
- **Rich telemetry surface** capturing queue metrics, rivalry events, stability KPIs, promotion state, anneal progress, and policy metadata.
- **Snapshot lifecycle** with identity enforcement, RNG stream persistence, and migration hooks to keep saves forward-compatible.
- **Operational scripts** for simulation runs, long-form soak tests, dataset audits, telemetry summarisation, and promotion rehearsals.
- **Observer dashboard (`townlet_ui`)** that renders telemetry panels, KPIs, promotion history, and issues console commands in real time.

## 4. Data Architecture

- **Configuration layer**: YAML files validated by `SimulationConfig` and nested Pydantic models (`src/townlet/config/loader.py`). Feature flags, rewards, telemetry transport, stability guardrails, and snapshot rules are centrally defined.
- **In-memory domain models**: dataclasses such as `AgentSnapshot`, `InteractiveObject`, `RunningAffordance`, `RelationshipLedger`, and `QueueManager` manage mutable simulation entities. `WorldState` aggregates them per tick.
- **Telemetry payloads**: dictionaries emitted on each tick contain metrics, event histories, console results, and health stats. `TelemetryPublisher.export_state()` produces canonical snapshots for storage/UI.
- **Persistence**: `SnapshotState` serialises world/telemetry/promotion/lifecycle data to disk; RNG streams stored as encoded tuples; promotion history written to `logs/promotion_history.jsonl`.
- **Datasets**: Behaviour cloning datasets live under `data/bc_datasets`; catalogue metadata checked by `scripts/audit_bc_datasets.py`.

## 5. API & Interface Layer

- **Console API** (`src/townlet/console/handlers.py`): command router registers telemetry/status handlers for all users and privileged actions (possess, kill, promote, snapshot migrate) when operating in `admin` mode. Commands return JSON-compatible dictionaries consumed by UI tests.
- **Telemetry transport** (`src/townlet/telemetry/transport.py`): stdout, file append, or raw TCP clients implement a `send`/`close` protocol. The TCP client lacks TLS or authentication today.
- **Observer UI** (`src/townlet_ui`): `TelemetryClient` parses telemetry snapshots, `ConsoleCommandExecutor` wraps router dispatch, and `dashboard.py` renders Rich tables/cards.
- **CLI entry points** (`scripts/`): `run_simulation.py`, `run_training.py`, `capture_rollout.py`, `run_anneal_rehearsal.py`, etc. expose operations via argparse. Inputs are YAML configs or metrics files; outputs are logs, JSON summaries, or zipped artefacts.
- **Policy API** (`policy/runner.py`): provides `decide`, `post_step`, `flush_transitions`, `register_ctx_reset_callback`, and anneal toggles. Scripted controllers and replay buffers plug into this interface.

## 6. Configuration & Deployment

- **Environment management**: repository expects a local venv (`python -m venv .venv`) and editable install (`pip install -e .[dev]`). No Dockerfile or compose manifest is supplied.
- **Runtime configuration**: `SimulationConfig` resolves snapshot roots, transport buffers, promotion thresholds, and perturbation rules. Console handlers fetch allow-listed snapshot roots via `config.snapshot_allowed_roots()`.
- **Environment variables**: minimal usage; telemetry file transport path defaults to `logs/telemetry.jsonl`; promotion history path hard-coded (`logs/promotion_history.jsonl`).
- **Deployment gap**: absence of containerization, orchestration manifests, or secrets management makes cloud deployment non-trivial. Introduce images and IaC before production exposure.

## 7. Data Flow Highlights

### Simulation Tick
1. `SimulationLoop.step()` (src/townlet/core/sim_loop.py:167) advances the global tick, processes console commands, ticks perturbations, retrieves policy actions, applies world affordances, and evaluates lifecycle termination.
2. Rewards are computed (`RewardEngine.compute`), observations built (`ObservationBuilder.build_batch`), and policy transitions flushed.
3. Telemetry payload assembled with rewards, events, stability inputs, and perturbation state before publishing.

### Telemetry Pipeline
1. `TelemetryPublisher.publish_tick()` (telemetry/publisher.py:612) updates metrics and serialises a payload.
2. `_enqueue_stream_payload()` encodes JSON and queues it in `TransportBuffer`; if buffer overflows, oldest payloads are dropped with warnings.
3. Background `_flush_loop()` drains the buffer, using `_send_with_retry()` to deliver via configured transport (stdout/file/TCP). Transport health metrics updated per flush.

### Snapshot Save/Load
1. `SimulationLoop.save_snapshot()` (core/sim_loop.py:88) collects world, telemetry, perturbations, stability, and RNG state into `SnapshotState`.
2. `SnapshotManager.save()` writes JSONL under snapshot root; `PromotionManager` history appended separately.
3. `SimulationLoop.load_snapshot()` (core/sim_loop.py:106) restores state, resets policy/scheduler, and reapplies RNG streams via `decode_rng_state`.

### Training Rollout Capture
1. `scripts/run_training.py` builds config, instantiates `PolicyRuntime`, and executes training loops using the same observation builder and reward engine.
2. Replay buffers (`policy/replay_buffer.py`) persist trajectories; `scripts/capture_rollout.py` collects rollouts for offline analysis.

## 8. Dependencies & Integration

- **Internal coupling**: `WorldState` depends on queue manager, relationship/rivalry ledgers, telemetry metrics, and affordance manifests. `SimulationLoop` depends on nearly every subsystem; stability and promotion managers rely on telemetry for metrics.
- **External services**: No live integration yet, but `.duskmantle/neo4j` and `.duskmantle/qdrant` directories indicate planned graph/vector stores. Current code assumes filesystem-only persistence.
- **Python packages**: PettingZoo env placeholders, PyTorch (optional) for PPO, Rich/typer for CLI/UI. Behaviour cloning tools expect NumPy-compatible datasets.

## 9. Development & Operations

- **Local setup**: create venv, install editable package with `pip install -e .[dev]`, then run `ruff check src tests`, `mypy src`, and `pytest`.
- **Testing**: Suites cover config loading, queue fairness, rivalry events, telemetry streams, promotion CLI, and snapshot migrations. Long-running simulations should be marked with `@pytest.mark.slow`.
- **Operations**: No monitoring stack provided. Telemetry transport exposes dropped-message counters via `TelemetryPublisher.latest_transport_status()`. Promotion lifecycle writes history to disk but lacks alerting or dashboards.
- **Release process**: Promotion manager tracks candidate state, but automation for policy promotion/release is incomplete. Behaviour cloning/training scripts require manual orchestration.
