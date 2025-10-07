# Architecture Review 2 — Gameplay Expansion Recommendations

This note captures concrete, code-grounded recommendations for evolving the simulation toward richer emergent behaviour. Each entry cites current seams and outlines actionable work.

## 1. Agent progression scaffolding

- **Extend `AgentSnapshot` with typed progression fields.** Add `skills: dict[str, float]` and `memories: dict[str, float]` to the dataclass (`src/townlet/world/agents/snapshot.py:18`). Use conservative defaults in `__post_init__` so legacy saves load cleanly and clamp values to `[0.0, 1.0]` similar to need normalisation.
- **Apply affordance effects to new channels.** Update `_apply_affordance_effects` so keys prefixed with `skill:` or `memory:` update the corresponding dicts (`src/townlet/world/grid.py:1380`). Persist recent skill deltas in the `_affordance_outcomes` log to support telemetry.
- **Surface progression in observations.** Gate new feature channels behind a config toggle (e.g., `features.stages.progression`). When enabled, append `skill:<name>` and `memory:<name>` features in `ObservationBuilder` (`src/townlet/observations/builder.py:44`) so policies can learn long-term arcs. Document sampling behaviour in a follow-up DTO once observation typing work lands.

## 2. Economy depth and resource categories

- **Promote resource tracking.** Expand `EconomyService.update_basket_metrics` to compute multiple baskets (e.g., `meal_cost`, `tech_cost`, `recreation_cost`) and store them in agent inventories for behavioural pivots (`src/townlet/world/economy/service.py:44`).
- **Tie perturbations to resources.** Introduce named resource pools like `electronics_stock` or `pool_chemicals` in the objects’ stock dict. Utility outages or price spikes should adjust these pools so new affordances can react (see Section 3).
- **Expose metrics for telemetry.** After DTO rollout, include resource snapshots in telemetry events so dashboards can visualise scarcity and cascading effects.

## 3. New affordance suites

- **Computer lab arc.**
  - Add `computer_lab_1` object and `use_computer` affordance to `configs/affordances/core.yaml:1`. Preconditions include `power_on == true` and optionally `seat_available`
  - Hook sequence (new entries in `townlet.world.hooks.default`): `_on_attempt_computer` checks power and charges an electricity fee (tie into `EconomyService`), `_on_finish_computer` increases `skills["programming"]`, boosts wallet via freelancing probability, and raises trust with co-working agents present. Use `world.update_relationship` similar to meal sharing (`src/townlet/world/hooks/default.py:149`).
- **Community pool arc.**
  - Add `pool_1` object and `swim_laps` affordance with hygiene drain, energy boost, and `memory:pool_session` increment.
  - Hooks should enforce `water_clean == true`; integrate with `EconomyService._set_utility_state` so prolonged outages close the pool. Successful sessions reduce rivalry between agents who share the pool tick and increase `skills["fitness"]`.
- **Shared projects.** Introduce cooperative affordances (e.g., `collaborate_project`) requiring multiple agents to start simultaneously. Use `QueueManager` reservations and `AffordanceRuntime.start` to ensure all participants meet preconditions; unlock unique rewards when all participants finish without abandoning.

## 4. Event-driven social dynamics

- **Scripted festivals/hackathons.** Use `PerturbationService.apply_arranged_meet` to move targeted cohorts to venues when an event starts (`src/townlet/world/perturbations/service.py:45`). During the event window, tweak economy multipliers (e.g., `EconomyService.apply_price_spike` for festival vendors) and boost `memories["festival"]`.
- **Relationship adjustments.** Extend `RelationshipService.update_relationship` to consider event-specific payloads—e.g., attending a festival together provides a larger familiarity delta while skipping causes mild rivalry gains.
- **Telemetry hooks.** Emit dedicated events (e.g., `festival_start`, `festival_attendance`) so console UI and analytics can react.

## 5. Tactical robustness improvements

- Replace control-flow `assert` in `TelemetryTransport.send` with explicit error handling so new networked affordances fail gracefully (`src/townlet/telemetry/transport.py:179`).
- Expand `_apply_affordance_effects` to log unknown effect keys with a structured warning, making it easier to diagnose mis-specified affordances while iterating on new content.
- Add sanity checks in hooks to avoid double-counting outcomes when cooperative affordances abort mid-way.

These changes dovetail with the DTO/telemetry refactor: typed payloads will make it easier to serialise skills, memories, and event metrics without hand-maintaining dict schemas. Prioritise progression scaffolding and affordance additions so the upcoming refactor branch has concrete gameplay wins to showcase alongside architectural cleanup.
