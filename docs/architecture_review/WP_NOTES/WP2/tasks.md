# WP2 Working Tasks

## 1. Analysis & Discovery
- [ ] Catalogue responsibilities in `src/townlet/world/grid.py` and related modules (actions, console, telemetry, RNG, persistence).
- [ ] Identify external call sites (simulation loop, telemetry, observation builder) that depend on world internals.
- [ ] Map existing observation pipeline (`townlet/observations/builder.py`) to future `observe.py` responsibilities.
- [ ] Document current console/telemetry hooks inside world runtime to plan extraction.

## 2. Architecture Alignment
- [ ] Review ADR-002 and external guidance to confirm module boundaries/event schema.
- [ ] Decide interim strategy for observations (dict payloads vs DTOs) to avoid blocking on WP3.
- [ ] Determine how `WorldRuntime` protocol methods will be implemented in the new `WorldContext` while keeping simulation loop functional.

## 3. Planning & Resourcing
- [ ] Produce implementation plan (see `implementation_plan.md`).
- [ ] List required fixtures/tests (unit modules, integration, golden snapshots).
- [ ] Identify migration steps for factories/loop to adopt `WorldContext`.

## 4. Execution Tracking (fill once coding begins)
- [ ] Skeleton package creation.
- [ ] State/agents extraction.
- [ ] Action pipeline.
- [ ] Systems/events integration.
- [ ] RNG determinism.
- [ ] Legacy cleanup + factory updates.
- [ ] Tests & docs.

Update this file as tasks progress.
