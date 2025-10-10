# WP3B – Modular Systems Reattachment

Purpose: Replace the temporary legacy bridges left in place after the DTO refactor with fully modular
system steps so the world can operate through `WorldContext` without calling back into legacy
helpers.

## Objectives

1. Deliver queue/affordance/employment system steps that replicate the behaviour currently covered
   by `WorldState.apply_actions` and `WorldState.resolve_affordances`.
2. Remove the transitional bridge inside `WorldContext.tick` while keeping scripted parity
   (`tests/test_behavior_personality_bias.py`) and DTO parity smokes green.
3. Provide focused regression tests to lock in system sequencing and ensure nightly decay, job
   updates, and economy metrics still advance.

## Work Breakdown

### A. System Inventory & Gap Analysis
- Catalogue the methods exercised by `WorldState.apply_actions`, `resolve_affordances`, and
  `_apply_need_decay` during the demo parity run (queue reservations, running affordances, need
  decay, job state, relationship decay, basket metrics).
- Identify which behaviours already exist in the placeholder system modules (`queues`, `affordances`,
  `employment`, `economy`) and note missing helpers.
- Risk reduction: capture a short parity trace (actions, queue states, needs) with the legacy bridge
  active for later comparison.

### B. Implement Queue/Affordance Steps
- Extend `townlet.world.systems.queues.step` to synchronise reservations, blocked attempts, and queue
  conflict tracking; ensure events match legacy outputs. *(Status: `on_tick` + reservation refresh
  in place; ghost-step conflicts now emit via the queue system. Remaining work: handover promotion
  + affinity logic still runs inside `resolve` and needs modular extraction.)*
- Replace the affordance step bridge by importing actions into the affordance runtime and calling
  `resolve`/`apply_need_decay` through the modular service rather than the legacy wrapper. *(Status:
  `process_actions` extracted and `advance_running_affordances` now drives completions via the
  runtime service; remaining work is to drop the final `resolve_affordances` wrapper once employment
  / economy steps land.)*
- Add unit tests mirroring legacy expectations (use lightweight stubs similar to existing system
  tests).

### C. Employment & Economy Integration
- Move nightly job state updates and economy basket metrics into dedicated system steps.
- Ensure perturbation hooks still fire in the correct order; adjust `default_systems()` sequencing if
  required.
- Guard with tests that run `WorldContext.tick` in isolation and inspect employment/economy state.

### D. Remove Transitional Bridge
- Delete the fallback call to `WorldState.apply_actions` in `WorldContext.tick` and revert the
  affordance system step to modular-only logic. *(Fallback removed; final step is to stop calling
  `state.resolve_affordances` once modular queues/affordances cover all hooks.)*
- Run behaviour parity smokes, DTO parity harness, and targeted world tests to confirm no regression.
- Document the change in WP3 notes; update tasks to reflect the bridge removal.

## Exit Criteria

- `WorldContext.tick` no longer calls legacy `WorldState.apply_actions`/`resolve_affordances`.
- Queue/affordance/employment system modules contain the required logic with unit coverage.
- Parity tests (`tests/test_behavior_personality_bias.py`, DTO harness, guardrail events) remain
  green.
- Docs/tasks reference the completed bridge removal and highlight any outstanding cleanups.
