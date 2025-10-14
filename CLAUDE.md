# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Pre-Release Software Policy

**CRITICAL**: This is pre-release software under active development. **NO BACKWARDS COMPATIBILITY CODE IS TOLERATED.**

- This project is in pre-1.0 development phase; breaking changes are expected and acceptable
- When fixing bugs or making improvements, **NEVER** add backwards compatibility code
- **ALWAYS** fix forward: update data formats, regenerate baselines, migrate schemas
- If a data format changes (snapshots, configs, DTOs), regenerate the test fixtures — do not support legacy formats
- Breaking changes are acceptable; maintaining legacy code paths is not
- Clean, forward-only code is required; compatibility shims are explicitly forbidden

**Examples of what NOT to do:**
- Adding pickle fallback when migrating to JSON format
- Supporting both old and new field names in DTOs
- Maintaining deprecated code paths "for compatibility"

**Examples of correct approach:**
- Migrate data format, regenerate all test baselines
- Update all code to use new API, remove old API entirely
- Change schema, update all instances, regenerate fixtures

## Quick Reference

### Development Commands

**Install and setup:**
```bash
pip install -e .[dev]          # Core development dependencies
pip install -e .[ml]           # Add PyTorch for ML features
pip install -e .[api]          # Add httpx for API integration tests
```

**Testing:**
```bash
pytest                         # Run all tests with coverage
pytest tests/test_telemetry_client.py tests/test_observer_ui_dashboard.py \
       tests/test_telemetry_stream_smoke.py tests/test_telemetry_transport.py  # Telemetry tests
pytest tests/test_utils_rng.py tests/test_snapshot_manager.py \
       tests/test_snapshot_migrations.py tests/test_sim_loop_snapshot.py       # Snapshot/RNG tests
pytest path/to/test_file.py    # Run a single test file
pytest path/to/test_file.py::test_function_name  # Run a single test
```

**Code quality:**
```bash
ruff check src tests           # Lint
mypy src                       # Type check
lint-imports                   # Import boundary enforcement (5 contracts)
scripts/check_docstrings.py src/townlet --min-module 95 --min-callable 40  # Docstring coverage
```

**Simulation:**
```bash
python scripts/run_simulation.py configs/examples/poc_hybrid.yaml --ticks 100
python scripts/run_simulation.py CONFIG_PATH --ticks N --stream-telemetry  # Stream to stdout
python scripts/run_simulation.py CONFIG_PATH --ticks N --telemetry-path FILE  # Write to file
```

**Configuration:**
```bash
python scripts/gen_config_reference.py --out docs/guides/CONFIG_REFERENCE.md  # Regenerate config docs
```

## Architecture Overview

Townlet is a reinforcement-learning life simulation with 6–10 agents in a 48×48 grid world. Agents learn to satisfy needs (hunger, hygiene, energy), hold jobs, and navigate social relationships using hierarchical RL (PPO at the option level, with scripted/learned primitives).

### Core Architecture Pattern

The simulation follows a **ports-and-adapters pattern** with three main runtime boundaries:

1. **World Port** (`src/townlet/ports/world.py`, `WorldRuntime`) — Advances the world state each tick
2. **Policy Port** (`src/townlet/ports/policy.py`, `PolicyBackend`) — Makes decisions for agents
3. **Telemetry Port** (`src/townlet/ports/telemetry.py`, `TelemetrySink`) — Emits events and metrics

These are wired together by `SimulationLoop` (`src/townlet/core/sim_loop.py`), which orchestrates the tick sequence and delegates to factories (`src/townlet/factories/`) that resolve provider names (e.g., `"scripted"`, `"pytorch"`, `"stdout"`) into concrete implementations.

### Architectural Refactoring (Complete ✅)

The codebase has completed a major architectural improvement initiative documented in `docs/architecture_review/`. The completed work packages (WP1-4) introduced:

- **WP1 (Complete)**: Minimal port protocols, registry-backed factories, and adapter pattern to decouple the simulation loop from concrete implementations (see ADR-001)
- **WP2 (Complete)**: Modular world package with separated concerns (state, actions, observations, systems) behind the `WorldRuntime` façade and `WorldContext` aggregator (see ADR-002)
- **WP3 (Complete)**: DTO-based boundaries using Pydantic v2 models; observations, snapshots, policy, rewards, and telemetry DTOs complete (see ADR-003)
- **WP4 (Complete)**: Strategy-based training architecture with modular BC/PPO/Anneal strategies and comprehensive policy DTOs (see ADR-004)
- **WP4.1 (Complete)**: Reward DTO integration and WP1/WP2 documentation reconciliation with comprehensive architecture diagrams

**Overall Progress**: 100% complete ✅ (All work packages delivered: WP1, WP2, WP3, WP3.2, WP4, WP4.1)

**Key architectural documents:**
- `docs/architecture_review/ARCHITECTURE_REVIEW_2.md` — Master architectural report with refactoring roadmap
- `docs/architecture_review/ADR/ADR-001 - Port and Factory Registry.md` — Port contract definitions
- `docs/architecture_review/ADR/ADR-002 - World Modularisation.md` — World package structure
- `docs/architecture_review/ADR/ADR-003 - DTO Boundary.md` — DTO consolidation strategy and patterns
- `docs/architecture_review/ADR/ADR-004 - Policy Training Strategies.md` — Training strategy architecture
- `docs/architecture_review/WP_TASKINGS/` — Work package specifications and compliance assessment

### Simulation Tick Sequence

Each tick follows this order (see `SimulationLoop.step()` in `src/townlet/core/sim_loop.py:607`):

1. **Console operations** — Apply buffered commands from telemetry
2. **Lifecycle spawns** — Process respawns if population is below target
3. **Perturbations** — Scheduler emits bounded random events (price spikes, outages, arranged meets)
4. **Policy decisions** — Agents select actions via `PolicyController.decide()` or `PolicyRuntime.decide()`
5. **World tick** — `WorldRuntime.tick()` applies actions, resolves affordances, evaluates needs/decay
6. **Lifecycle evaluation** — Check termination conditions (collapse, eviction, unemployment)
7. **Rewards** — `RewardEngine.compute()` calculates per-agent rewards (homeostasis + shaping + social)
8. **Observations** — `ObservationService.observe()` encodes variant-specific tensors (full/hybrid/compact)
9. **Policy step** — `PolicyController.post_step()` buffers transitions for PPO
10. **Telemetry** — Emit `loop.tick`, `stability.metrics`, `loop.health` events
11. **Nightly reset** — If `tick % ticks_per_day == 0`, apply daily economy/utility updates

### Key Subsystems

**World Model** (`src/townlet/world/`)
- `runtime.py:WorldRuntime` — Façade implementing port protocol, delegates to WorldContext
- `core/context.py:WorldContext` — Internal aggregator coordinating 13 services
- `grid.py:WorldState` — 48×48 tile grid, agents, needs, inventory, economy
- `affordances/` — Declarative YAML-based action system (hot-reloadable)
- `systems/` — Domain systems (employment, economy, affordances, queues, relationships, perturbations)

**Observations** (`src/townlet/observations/`, `src/townlet/world/observations/`)
- Three variants (switchable via `features.observations`): `full`, `hybrid`, `compact`
- `full` — Local map (9×9) + scalars + social snippet (~500–800 floats)
- `hybrid` — Slimmer map with directional fields to key targets
- `compact` — No map; distilled vectors only (distances, bearings, flags)
- Variant is baked into `config_id` and policy hash; changes require A/B gate before promotion

**Policy** (`src/townlet/policy/`)
- `runner.py:PolicyRuntime` — Main backend implementing `PolicyBackendProtocol`
- Hierarchical: meta-policy chooses options, options call scripted/learned primitives
- Action masking enforces validity; option commitment window prevents thrashing
- BC warm-start + anneal scheduler for scripted→learned primitive handoff

**Rewards** (`src/townlet/rewards/`)
- `engine.py:RewardEngine` — Homeostasis + potential shaping + work/punctuality + social (Phase C)
- Guardrails: hard floor overrides when needs > 0.85; clip per-tick rewards to ±r_max
- Running normalization stats tracked for logging

**Lifecycle** (`src/townlet/lifecycle/`)
- `manager.py:LifecycleManager` — Monitors failure conditions (collapse, eviction, chronic neglect)
- Exit caps (max 2/day) + cooldown (120 ticks) to limit non-stationarity
- Replacement spawns maintain population; optional elitist warm-start from PBT replicas

**Perturbations** (`src/townlet/scheduler/`)
- `perturbations.py:PerturbationScheduler` — Bounded random events with fairness buckets
- Types: price spikes, blackouts, water outages, arranged meets (top rivals at café)
- Suppresses exits during city-wide events + grace window

**Snapshots** (`src/townlet/snapshots/`)
- `manager.py:SnapshotManager` — Save/load world + RNG streams + policy hash + config_id
- Auto-migration support (`config.snapshot.migrations.auto_apply`)
- Captures three RNG streams: `world`, `events`, `policy`
- **DTO-based architecture**: Uses `SimulationSnapshot` DTO (Pydantic v2) with 11 nested subsystem DTOs
- **Dict-based migrations**: Migrations operate on dicts, then final dict is validated into DTO
- See `docs/architecture_review/ADR/ADR-003 - DTO Boundary.md` for DTO consolidation patterns

**Telemetry** (`src/townlet/telemetry/`)
- `publisher.py:TelemetryPublisher` — Pub/sub with buffering + backpressure
- Transports: `stdout` (dev), `file` (JSONL), `tcp` (observer UI)
- Schema versioned; all payloads carry `schema_version` header

**Stability & Promotion** (`src/townlet/stability/`)
- `monitor.py:StabilityMonitor` — Rolling 24h windows; canaries detect regressions
- `promotion.py:PromotionManager` — A/B gates for observation variants and policy changes
- Promotion requires two consecutive evaluation windows passing thresholds

### Configuration System

All behavior is driven by `SimulationConfig` (`src/townlet/config/`):
- **config_id** — Hash of config + policy + obs variant; enforced in snapshots
- **features** — Phase gates (`relationships`, `social_rewards`, `lifecycle`)
- **runtime** — Provider overrides for world/policy/telemetry
- Hot-reload allowed: affordances, perturbations; restart required: reward weights, network arch

When modifying config models, regenerate docs:
```bash
python scripts/gen_config_reference.py --out docs/guides/CONFIG_REFERENCE.md
```

### RNG Discipline

Three independent RNG streams are seeded from `config_id`:
- `_rng_world` — World state updates (decay, economy)
- `_rng_events` — Perturbation scheduler
- `_rng_policy` — Policy decisions

All three are captured in snapshots for deterministic replay. Seed derivation is in `SimulationLoop._derive_seed()` (line 1541).

### Testing Patterns

- **Unit tests** — Config validation, reward calculations, lifecycle gates
- **Integration tests** — Full sim loop with stub policy/telemetry
- **Golden tests** — YAML schema invariants, telemetry payload shapes
- **Snapshot regression** — RNG determinism, migration compatibility
- Test fixtures live in `tests/fixtures/`

## Design Documentation

Critical design files (read when making architectural changes):
- `docs/program_management/snapshots/CONCEPTUAL_DESIGN.md` — Vision, principles, data models
- `docs/program_management/snapshots/HIGH_LEVEL_DESIGN.md` — Module architecture, data flows
- `docs/program_management/snapshots/REQUIREMENTS.md` — Functional requirements, KPIs
- `docs/guides/DOCSTRING_GUIDE.md` — Docstring style and tone

## Coding Standards

- **Python 3.11+** with strict type annotations
- Use `from __future__ import annotations` in new modules
- Pass explicit handles (RNG, config slices) rather than globals
- Feature flags (`features.*`) guard work-in-progress; no ad-hoc conditionals
- Modules should be small and cohesive; cross-module interactions via dataclasses/protocols
- Tag design references in comments: `# DESIGN#4.1` links to spec section

## Import Boundary Enforcement

The codebase enforces architectural boundaries using `import-linter` with 5 contracts:

**Enforced Boundaries**:
1. **DTO Independence** — DTOs must not import concrete implementations
2. **Layered Architecture** — Enforces domain → core → ports → dto hierarchy
3. **World/Policy Separation** — Prevents bidirectional coupling
4. **Policy/Telemetry Separation** — Prevents direct coupling (indirect paths allowed)
5. **Config DTO-Only** — Config only imports DTOs and minimal snapshots

**How to Work with Boundaries**:
- Run `lint-imports` before committing to check for violations
- CI blocks PRs with new import violations
- All exceptions are documented in `.importlinter` with architectural rationale
- See `docs/architecture_review/IMPORT_EXCEPTIONS.md` for exception registry
- Reference ADR-001 (Ports & Adapters), ADR-002 (World Modularization), ADR-003 (DTO Boundaries)

**Adding New Exceptions**:
If you need to add a legitimate architectural dependency that violates a contract:
1. Identify which contract is violated and why the import is necessary
2. Determine the architectural pattern (factory, composition, orchestration, etc.)
3. Add the exception to `.importlinter` under the appropriate contract's `ignore_imports`
4. Add a comment explaining the rationale with ADR reference
5. Update `docs/architecture_review/IMPORT_EXCEPTIONS.md` with full documentation

**Common Exception Patterns**:
- **Factory Pattern**: Factories must import what they instantiate (allowed)
- **Orchestration**: SimulationLoop owns domain objects for coordination (allowed)
- **Composition**: Parent objects own child components (allowed)
- **Cross-Cutting**: Snapshots serialize all subsystems (allowed)
- **Same Layer**: Domain modules can import each other (policy → world allowed)
- **Indirect Paths**: policy → core → telemetry is acceptable (not direct coupling)

## Common Patterns

**Adding a new provider:**
1. Implement the protocol (`PolicyBackend`, `TelemetrySink`, or extend `WorldRuntime`)
2. Register with `@register("category", "provider_name")` in the appropriate factory
3. Update runtime config schema if new options are needed

**Snapshot compatibility:**
- Snapshots carry `config_id`, `policy_hash`, `obs_variant`, `rng_streams`
- On load, `SnapshotManager` checks compatibility and applies migrations if enabled
- Add migrations in `src/townlet/snapshots/migrations.py`

**Working with DTOs (Pydantic v2):**
- The codebase uses Pydantic v2 DTOs for typed boundaries (observations, snapshots, policy results)
- Top-level DTO package: `townlet/dto/` (`observations.py`, `policy.py`, `world.py`)
- **Serialization**: Use `.model_dump()` (NOT `.dict()` from Pydantic v1)
- **Deserialization**: Use `.model_validate()` (NOT `.parse_obj()` from Pydantic v1)
- **Attribute access**: DTOs use attribute access, **never** dictionary access
  ```python
  # ✅ CORRECT
  applied = snapshot.migrations.applied
  state = snapshot.promotion.state

  # ❌ WRONG
  applied = snapshot.migrations.get("applied", [])  # AttributeError!
  state = snapshot["promotion"]["state"]            # TypeError!
  ```
- **Nested DTOs**: Complex DTOs (e.g., `SimulationSnapshot`) use nested composition for modular validation
- **Migration integration**: Migrations operate on dicts, then final dict is validated into DTO
- See ADR-003 for complete DTO consolidation patterns

**Adding a config field:**
- Update the Pydantic model in `src/townlet/config/`
- Regenerate `docs/guides/CONFIG_REFERENCE.md`
- Check if the change affects `config_id` (if so, existing snapshots become incompatible)

**Observation variant changes:**
- New variants require A/B gating in `features.observations`
- Variant affects policy hash and must be included in `config_id`
- Test both full and slim variants to ensure parity

**Telemetry events:**
- Emit via `self.telemetry.emit_event(name, payload)` or `self._telemetry_port.emit_event(name, payload)`
- Standard events: `loop.tick`, `loop.health`, `loop.failure`, `policy.metadata`, `policy.possession`, `policy.anneal.update`, `stability.metrics`
- All events carry tick number and are buffered/batched before transport

## Common Pitfalls

- **Never mutate the release policy in-place** — Elitist spawn copies a replica, not the global release
- **Reset LSTM state on hard context cuts** — Teleport, possess, death all require `ctx_reset_flag=True`
- **No positive rewards near death** — Guardrail suppresses rewards within N ticks of termination
- **Observation variant must be in policy hash** — Otherwise promotion breaks determinism
- **Affordance hooks must be idempotent** — They may retry on failure or rollback
- **Console commands need validation** — Use `ConsoleCommandEnvelope.from_payload()` and handle `ConsoleCommandError`
- **DTOs are not dictionaries** — Use attribute access (`dto.field`) not dict access (`dto["field"]` or `dto.get()`). Pydantic models will raise `AttributeError` or `TypeError` on dict-style access

## Debugging

**Snapshot on failure:**
```yaml
snapshot:
  capture_on_failure: true
```
Saves world state to `snapshots/failures/tick_NNNNNNNNNN_TIMESTAMP/`

**Deterministic replay:**
```bash
python scripts/run_simulation.py CONFIG --deterministic --ticks N
```
Fixes all RNG streams for reproducibility.

**Health telemetry:**
- Every tick emits `loop.health` with `duration_ms`, `queue_length`, `dropped_messages`, `perturbations_pending`, `employment_exit_queue`
- On failure, emits `loop.failure` with `error`, `snapshot_path`, `traceback`

**Profiling:**
```bash
python scripts/benchmark_tick.py CONFIG  # Measure tick throughput
python scripts/profile_observation_tensor.py CONFIG  # Profile observation encoding
```

## Notes

- The codebase uses `# TODO(@townlet)` markers for implementation TODOs; search these when looking for unfinished work
- Module responsibilities are documented in each `__init__.py` or module docstring
- Perturbation scheduler is phase-gated; locked out during M0–M2, enabled at M4
- SonarQube metrics are configured in `.github/workflows/sonarcloud.yml` and `sonar-project.properties`
