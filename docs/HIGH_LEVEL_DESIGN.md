# Townlet — High-Level Design (v1.3)

This is a one-page architecture map aligned to docs/CONCEPTUAL_DESIGN.md and docs/REQUIREMENTS.md.

## Modules

- Core Sim Loop
  - Tick scheduler (250 ms/tick; time dilation); RNG streams (world/events/policy); profiling timers.
  - Sequence per tick: apply console ops → process scheduler events → agents act → affordances resolve → needs/decay → lifecycle checks → rewards/logs → observations → RL step → publish telemetry.

- World Model
  - Grid (48×48), tiles/objects, utilities/weather, economy (prices, stock, wages, rent).
  - Affordance registry (hot‑reloaded YAML) with preconds/effects/hooks.

- Queue & Reservation Manager
  - Tile/object reservations with timeouts; queue nodes per interactive object; arrival tie‑break; fairness cooldown; queue‑age priority; deadlock “ghost step”.
  - Spatial index (uniform grid/quadtree) for neighbor queries and queue placement; O(1) expected for local lookups.

- Perturbation Scheduler
  - Bounded random events; fairness buckets; overlap/stagger controls; city‑event exit suppression + grace window.

- Lifecycle Manager
  - Failure monitors (collapse, eviction, unemployment, chronic neglect, optional age‑out). Exit caps/cooldowns. Replacement spawns. Training_mode gate.

- Observation Builder
  - Variant‑specific encoders (full/hybrid/compact), self scalars/personality/social snippet; ID→embedding; masks; `ctx_reset_flag` for hard context cuts.
  - Variant baked into `config_id` and policy hash; variant changes require A/B gate before promotion.

- Policy Runner (RL)
  - PettingZoo ParallelEnv wrapper; action masking for invalid options/primitives; option commitment window; scripted controllers; BC head; anneal scheduler.
  - Per‑agent advantage resets on termination/spawn; retain LSTM hidden on option switches; reset on teleport/possess/death.

- Reward Engine
  - Homeostasis + shaping; work/punctuality (triangular window); survival; social Phase C taps; guardrails (clips, death/exit windows); curiosity schedule Phase A.
  - Running reward normalisation stats; optional value‑loss scaling when flipping C‑phases.

- Stability Monitor & Promotion
  - Rolling 24h windows; canaries; eval suite (fixed seeds per milestone); variant A/B; golden rollouts; release vs shadow policy management.
  - Policy/version compatibility: spawns always use current release; defer variant changes to promotions.

- Persistence & Config
  - Snapshot (world, RNGs×3, policy hash, config_id, obs variant, anneal ratio). Hot‑reload parser (affordances/events). Restart‑required list. Feature‑flag surface.
  - Backpressure/circuit breaker for telemetry; console idempotency tokens; audit log.

- Telemetry & UI Gateway
  - Pub/sub (initial snapshot then diffs): agents, events, economy, weather/utilities. KPI streams. Policy inspector payloads.
  - Debug tooling: social graph explorer, event timelines, queue visualiser, AFI scoreboard.

- Console & Auth
  - Token‑gated endpoints; viewer/admin modes; error codes; audit log.
  - Idempotency (`cmd_id`) for safe retries.

## Data Flows (Happy Path)

1. Input: console commands → validated → applied (or rejected with code).
2. Scheduler emits events; World updates utilities/weather/economy.
3. Agents select actions (RL meta‑policy → options → scripted/learned primitives; action mask enforced; commitment window checked).
4. Queue/Reservation Manager arbitrates access; Affordances execute (hooks fire pre/after/fail).
5. Lifecycle evaluates; per‑agent terminations flagged; replacements queued.
6. Reward Engine computes per‑tick rewards; clips/guardrails applied.
7. Observation Builder encodes variant tensors; `ctx_reset_flag` set when needed.
8. Policy Runner steps PPO; buffers tagged (exclude possessed/no‑grad if configured).
9. Telemetry publishes diffs; KPIs updated; Profiling logs slowest ticks.
10. Stability Monitor updates eval/promotion state; Release/Shadow policies reconciled.

## Deployment Topology

- One or more headless training shards (ParallelEnv) + Shadow policies.
- Release policy process serving Viewer/UI via pub/sub.
- Console/API service (auth) colocated with release.
- Optional Rust/C++ microservice for pathfinding behind FFI if hot paths demand.
  - Future 3D renderer: mirror authoritative Python sim state into a 3D client; renderer is replaceable without changing sim/observer interfaces.

## Key Interfaces

- PettingZoo ParallelEnv (env.step/env.observe) with per‑agent terminations.
- YAML loaders (affordances/events) with checksum and schema validation.
- Observer API (JSON) — initial snapshot + diffs; versioned schema.
- Config service exposing `config_id`, feature flags, and restart/hot‑reload envelopes.
  - Optional pathfinding FFI boundary (stable C ABI).

## Notes & Defaults

- Default obs variant: hybrid. Switch via `features.observations` + policy hash/version gate.
- Default lifecycle.training_mode: off in A/B, on in Phase C eval/live.
- Punctuality window: triangular ±30 sim minutes; clip rewards per tick/episode.
- Option commitment window: 15 ticks (configurable).
- Compact obs may be default for large‑scale training; hybrid for PoC; changes require A/B gate.
- Auto‑phase advancement (optional): progress when KPI bands are held for two windows; manual override always available.
