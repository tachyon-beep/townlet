# WP2 Working Tasks

## 1. Analysis & Discovery
- [x] Catalogue responsibilities in `src/townlet/world/grid.py` and related modules (actions, console, telemetry, RNG, persistence).
- [x] Identify external call sites (simulation loop, telemetry, observation builder) that depend on world internals.
- [x] Map existing observation pipeline (`townlet/observations/builder.py`) to future `observe.py` responsibilities.
- [x] Document current console/telemetry hooks inside world runtime to plan extraction.

## 2. Architecture Alignment
- [x] Review ADR-002 and external guidance to confirm module boundaries/event schema.
- [x] Decide interim strategy for observations (dict payloads vs DTOs) to avoid blocking on WP3.
- [ ] Determine how `WorldRuntime` protocol methods will be implemented in the new `WorldContext` while keeping simulation loop functional.

## 3. Planning & Resourcing
- [x] Produce implementation plan (see `implementation_plan.md`).
- [x] List required fixtures/tests (unit modules, integration, golden snapshots).
- [ ] Identify migration steps for factories/loop to adopt `WorldContext`.

## 4. Execution Tracking (fill once coding begins)
- [x] Skeleton package creation.
- [x] State/agents extraction.
- [ ] Action pipeline.
- [ ] Systems/events integration.
- [ ] RNG determinism.
- [x] Extracted spatial index & observation helpers (Step 3).
- [x] Event dispatcher helpers implemented with unit coverage (Step 3).
- [x] World state container (RNG, ctx-reset, event buffer) with unit coverage.
- [ ] Legacy cleanup + factory updates.
- [ ] Tests & docs.

Update this file as tasks progress.
