# Townlet Architecture & Interfaces Guide (v0.2)

## 1. Overview
Townlet is a headless simulation and training platform built around a deterministic tick loop, modular world representation, and PettingZoo-compatible reinforcement-learning harness. The architecture emphasises hot-reloadable configuration, strict guardrails for stability, and rich telemetry so human operators can nudge the town without retraining. This document expands the subsystem map, describes control flow, and enumerates integration contracts that must hold through milestones M0–M5.

### 1.1 High-Level Components
```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Console/API  │    │  Telemetry   │    │  Observer UI │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                  │                   │
       ▼                  ▼                   │
┌──────────────────────────────────────────────────────┐
│              Core Simulation Process                  │
│  ┌──────────────┐   ┌──────────────┐   ┌───────────┐ │
│  │ World Model  │   │ Queue/Life-  │   │ Reward &  │ │
│  │  + Config    │   │ cycle Mgmt   │   │ Stability │ │
│  └──────┬───────┘   └──────┬───────┘   └──────┬────┘ │
│         │                  │                   │    │
│  ┌──────▼───────┐  ┌───────▼───────┐   ┌───────▼────┐ │
│  │ Observation  │  │ Policy Runner │   │ Snapshots  │ │
│  │ Builder      │  │ (PettingZoo)  │   │ & Config   │ │
│  └──────────────┘  └───────────────┘   └────────────┘ │
└──────────────────────────────────────────────────────┘
```

### 1.2 Tick Timeline (Happy Path)
1. **Console Drain** — Apply queued commands (spawn, toggle flags) with validation.
2. **Scheduler Events** — Evaluate perturbation triggers, enforcing fairness buckets.
3. **Policy Step** — Build per-agent observations → PettingZoo policy call → action masks.
4. **Affordance Resolution** — Reservation manager arbitrates; hooks fire pre/after/fail.
5. **Needs & Lifecycle** — Update needs, compute rewards, detect exits, queue spawns.
6. **Telemetry** — Emit diff payload and KPIs; stability monitor ingests metrics.
7. **Persistence** — Snapshot if required; record config/variant hashes.

Each subsystem exposes hooks so new features (e.g., renderer, pathfinder) can slot in without breaking contracts.

## 2. Subsystem Deep Dives
### 2.1 Core Tick Orchestrator (`src/townlet/core/sim_loop.py`)
- owns deterministic tick ordering, 250 ms cadence, and RNG stream management (`world`, `events`, `policy`).
- interfaces:
  - `WorldState.apply_console(operations)`
  - `PerturbationScheduler.tick(world, tick)`
  - `PolicyRunner.step(world)` returning `(actions, action_masks)`
  - `LifecycleManager.evaluate(world, tick)`
  - `TelemetryPublisher.publish(diff)`
- guardrails: enforces observation variant gates (via `SimulationConfig.require_observation_variant`) and ensures `config_id` stamped on snapshots.

### 2.2 World Model & Affordances (`src/townlet/world/`, `configs/affordances/*.yaml`)
- responsibilities: grid topology, object definitions, economy state (prices, stock, wages), hot-reloadable affordance registry with schema validation.
- data structures:
  - `WorldState` — central mutable container referencing `SimulationConfig` + agent snapshots.
  - `InteractiveObject` instances capture object type and current occupancy; `AffordanceSpec` pairs with `RunningAffordance` to track execution progress.
- affordance specs load automatically from `config.affordances.affordances_file`, including `type: object` entries that pre-register interactive objects; the runtime still allows programmatic overrides via `register_object`/`register_affordance` for tests.
- extension hooks: add YAML schema + hook dispatch to bridge console/telemetry events (planned).
- need decay is applied post-affordance using `rewards.decay_rates`, keeping needs clamped to [0,1].
- economy fields (`economy.*`) fund affordance execution (e.g., `eat_meal` consumes wallet + fridge stock, `cook_meal` deducts ingredients) and provide default wage rates.
- job scheduler assigns agents to configured shifts (`jobs.*`), applies wage income, and emits `job_late` events on missed, location-based punctuality windows.
- rivalry ledger (`WorldState._rivalry_ledgers`) captures queue-driven tension; queue manager hooks call `_record_queue_conflict` during ghost steps/handovers, emitting `queue_conflict` events with intensity metadata for telemetry and behaviour avoidance heuristics.

### 2.3 Queue & Reservation Manager (`src/townlet/world/queue_manager.py`)
- responsibilities: per-object queue nodes, reservation timeouts, queue age priority, ghost-step deadlock breaker.
- config inputs: `config.queue_fairness` (cooldown ticks, ghost-step threshold, age priority weight).
- integration: invoked from world update prior to affordance resolution; surfaces cooldown and ghost-step counters for telemetry.

### 2.4 Lifecycle Manager (`src/townlet/lifecycle/manager.py`)
- monitors needs, wages, perturbation states to determine exits (`terminations[agent] = True`) and schedules replacements respecting cooldown + daily caps.
- config inputs: `features.systems.lifecycle`, reward guardrails (`no_positive_within_death_ticks`), `employment.*` (daily exit cap, queue limits, review window).
- employment loop: consumes per-agent absence counters, manages hybrid exit queue (per-agent threshold + daily cap) and manual approvals, raises telemetry events (`employment_exit_pending`, `employment_exit_processed`).
- hooks: emits `on_agent_exit`, `on_agent_spawn` for telemetry and narration.

### 2.5 Observation Builder (`src/townlet/observations/builder.py`)
- variant-aware encoding (full, hybrid, compact); attaches `ctx_reset_flag` when agent terminated.
- dependencies: world snapshots, embedding allocator; social graph wiring TBD.
- Hybrid variant now emits structured tensors:
  - map tensor (4×11×11) with channels for self, other agents, objects/reservations (placeholder zeros for now).
  - feature vector containing needs, wallet, lateness metrics, employment stats, shift-state one-hot, embedding slot normalised, context flags, rivalry magnitude/avoidance counters, and social placeholder.
- metadata includes channel names and feature index to aid downstream consumers; see `docs/design/OBSERVATION_TENSOR_SPEC.md`.
- open work: enrich object/reservation channels once world tracks coordinates; feed social snippet when relationship system arrives.

### 2.6 Embedding Allocator (`src/townlet/observations/embedding.py`)
- assigns stable embedding slots; enforces cooldown before reuse; logs forced reuse counts and warning flag when the reuse rate exceeds the configured threshold.
- config inputs: `config.embedding_allocator` (cooldown ticks, warning threshold, max slots).
- telemetry: exposes metrics consumed by the publisher (`forced_reuse_rate`, `reuse_warning`).

### 2.7 Policy Runner (`src/townlet/policy/runner.py`)
- wraps PettingZoo `ParallelEnv`, manages option commitment windows, scripted primitive controllers, action masking, and behaviour-clone anneal scheduler.
- outputs `actions` + metadata (masks, diagnostics) consumed by core loop.
- config inputs: `features.stages`, `features.training`, anneal ratios from config or runtime flags.
- Scripted controller plug-in (`BehaviorController`) currently returns idle intents; foundation laid for richer logic.

### 2.8 Reward Engine (`src/townlet/rewards/engine.py`)
- computes per-agent reward: survival tick, needs penalty, wage, punctuality, social taps; enforces per-tick & per-episode clip bounds, death-window suppression.
- dependencies: lifecycle signals (exits), employment context (wages paid/withheld, punctuality), chat events, rivalry data for social guardrails.
- outputs per-agent totals plus component breakdown (survival, needs penalty, social, wage, punctuality, clip adjustment); telemetry consumer records the breakdown for ops/console.

### 2.9 Stability Monitor (`src/townlet/stability/monitor.py`)
- aggregates lateness, starvation, option-switch rate, and reward variance over rolling windows to drive promotion and rollback decisions.
- integration: subscribes to telemetry stream and snapshot metadata. Guardrail status is exposed via `TelemetryPublisher.latest_stability_alerts()` / `TelemetryPublisher.latest_stability_metrics()` for console snapshots and dashboards.
- configuration: `stability.affordance_fail_threshold` caps per-tick affordance failures alongside embedding reuse warnings. Blocks `stability.starvation`, `stability.reward_variance`, and `stability.option_thrash` define window length, thresholds, and minimum sample counts for canaries.

- publishes initial snapshot + diffs (agents, events, economy, utilities, metrics) over WebSocket (planned) or file sink.
- enforces privacy mode (hashed IDs) and backpressure (aggregate diffs, drop events when overloaded).
- maintains semantic version string (`schema_version`, currently `0.3.0`) surfaced on every console/telemetry snapshot for consumer compatibility.
- captures queue manager, embedding allocator, and employment queue counters for ops dashboards.
- emits per-tick lifecycle events (`affordance_start`, `affordance_finish`, `affordance_fail`, `employment_exit_pending`, `employment_exit_processed`) sourced from the world.
- exposes per-agent job snapshots (job id, on-shift flag, shift state, attendance ratio, late ticks, wages withheld, wages earned, meals cooked/consumed, basket cost) plus global employment metrics (pending exits, exits today, queue limits) for planning.

### 2.10 PPO Telemetry NDJSON Contract (`TrainingHarness.run_ppo`)
- **Producer:** `TrainingHarness.run_ppo` writes newline-delimited JSON (NDJSON) to `log_path` / `--ppo-log`.
- **Schema version:** default `telemetry_version == 1.1`. Set `config.training.telemetry_version` (future flag) to `1.0` only when consumers cannot handle the new fields.
- **Epoch summary fields (v1.1):** `epoch`, `updates`, `transitions`, `steps`, `loss_policy`, `loss_value`, `loss_entropy`, `loss_total`, `clip_fraction`, `adv_mean`, `adv_std`, `grad_norm`, `kl_divergence`, optimiser learning rate `lr`, **plus**:
  - `epoch_duration_sec`: wall-clock seconds for the epoch.
  - `data_mode`: `"replay"`, `"rollout"`, or `"mixed"` (alternating cycles).
  - `cycle_id`: monotonically incrementing rollout/train cycle id.
  - `batch_entropy_mean` / `batch_entropy_std`: entropy stats across mini-batches.
  - `grad_norm_max` / `kl_divergence_max`: maxima observed across mini-batches.
  - `reward_advantage_corr`: Pearson correlation between rewards and advantages (0 if variance is zero).
  - `rollout_ticks`: tick budget feeding the dataset (0 for pure replay).
  - `log_stream_offset`: running counter for NDJSON streaming.
- **Baseline metrics:** when replay/rollout datasets provide aggregates, the log injects `baseline_sample_count`, `baseline_reward_mean`, `baseline_reward_sum`, `baseline_reward_sum_mean`, and optional `baseline_log_prob_mean`. Absence indicates no baseline comparison was available.
- **Conflict telemetry:** rivalry telemetry collapses into `conflict.rivalry_max_mean_avg`, `conflict.rivalry_max_max_avg`, `conflict.rivalry_avoid_count_mean_avg`, and `conflict.rivalry_avoid_count_max_avg`.
- **Rotation contract:** `max_log_entries` triggers roll-over into suffixed files (`.1`, `.2`, …). Tooling must glob by prefix to reconstruct sequences; `log_stream_offset` continues incrementing across rotations.
- **Compatibility notes:** v1.0 payloads exclude the v1.1 fields and must not include them partially. Validator (`scripts/validate_ppo_telemetry.py`) enforces version-specific requirements; sample logs live under `docs/samples/` and are refreshed with each schema change.

### 2.11 Console & Auth (`src/townlet/console/`)
- Typer CLI / REST service with viewer/admin modes, bearer tokens, and audit logging.
- commands: spawn, teleport, setneed, force_chat, arrange_meet, price adjustments, promotion/rollback (TBD), debug queues, `employment_status`, `employment_exit <review|approve|defer>`, and admin-only perturbation controls (`perturbation_queue`, `perturbation_trigger`, `perturbation_cancel`).
- idempotency: `cmd_id` required for destructive operations; logs `cmd_id`, issuer, result.
- event stream subscriber surfaces telemetry event batches for operator tooling.
- `telemetry_snapshot` command returns per-agent job/economy payloads and employment queue metrics for planning and basket checks.

### 2.12 Persistence & Config Service (`src/townlet/snapshots/`, `src/townlet/config/`)
- YAML configs validated via `SimulationConfig` (pydantic). New sections include `queue_fairness` and `embedding_allocator`.
- snapshot payloads store world state, RNG seeds, policy hash, `config_id`, observation variant, anneal ratio.
- migration: snapshot load rejects `config_id` mismatch unless migration defined.

### 2.13 Perturbation Scheduler (`src/townlet/scheduler/perturbations.py`)
- owns config-driven events (price spikes, outages, arranged meets) with per-spec
  windows, magnitudes, cooldowns, and fairness buckets.
- provides `schedule_manual` / `cancel_event` APIs for console-triggered actions;
  viewer mode receives a `forbidden` response, while admin mode records audit
  entries for each command.
- emits `perturbation_started`, `perturbation_cancelled`, and
  `perturbation_ended` telemetry events; `TelemetryPublisher` exposes the latest
  `perturbations` block (active, pending, cooldowns) for console snapshots and
  downstream dashboards.

## 3. End-to-End Sequences
### 3.1 Policy Step Sequence
1. World snapshot -> Observation builder encodes variant-specific tensors (reserving embedding slots).
2. Policy runner consumes observations, merges with action masks, invokes PPO policy.
3. Actions returned with `action_masks`; invalid selections suppressed.
4. Core loop passes actions to world state for affordance resolution.

### 3.2 Exit & Respawn
1. Lifecycle manager detects exit trigger (needs, eviction, unemployment, age-out) and sets `terminations[agent]` for PettingZoo.
2. Reward engine applies terminal penalty; no positive rewards within configured window after exit trigger.
3. Spawner schedules replacement after 5–20 ticks, sampling new personality and job, respecting exit cooldown (120 ticks) and per-day cap (2).
4. Embedding allocator releases old ID, records `released_at_tick`, and logs if reuse occurs before 2,000-tick cooldown.

### 3.3 Promotion & Rollback (Ops Flow)
1. Shadow policy hits KPI thresholds twice → stability monitor raises promotion candidate.
2. Ops issues `promote_policy <checkpoint>` via console (TBD) or manual config swap; release pointer updates.
3. Monitor telemetry for two windows; if canaries fire (lateness spike, starvation, option-switch spike), issue `rollback_policy --to <snapshot>`; otherwise log success.

### 3.4 Perturbation Event
1. Scheduler tick inspects config-defined event rates and fairness buckets.
2. If event fires (e.g., price_spike), world state updated; lifecycle temporarily suppress exits tied to the event.
3. Telemetry records event with metadata; stability monitor notes fairness metrics.

## 4. Configuration Influence Map
| Config Node | Affects | Notes |
| --- | --- | --- |
| `features.stages.relationships` | Observation builder, policy runner | Enables social tuple encoding; must sync with reward config.
| `features.systems.observations` | Observation builder, policy runner, promotion gates | Variant baked into `config_id`/policy hash.
| `queue_fairness.*` | Queue manager, telemetry, ops debug | Cooldown/ghost-step/priority weights; ensure metrics exposed.
| `conflict.rivalry.*` | Queue manager, WorldState, telemetry, behaviour | Tunes rivalry increment/decay, avoidance thresholds, and conflict event payloads; keep UI/tests aligned.
| `embedding_allocator.*` | Observation builder, telemetry | Cooldown ticks and warning threshold for reuse; log forced reuse.
| `rewards.decay_rates` | WorldState, RewardEngine | Drives per-need decay applied each tick.
| `rewards.clip.*` | Reward engine | Enforce guardrails for PPO stability.
| `curiosity.*` | Reward engine, policy runner | Phase A only unless toggled.
| `stability.affordance_fail_threshold` | Stability monitor | Controls alerts when affordance failures spike.
| `economy.*` | WorldState economy logic | Defines meal costs, cook costs, wage income defaults.
| `jobs.*` | Job scheduler | Shift windows, wage rates, lateness penalties.
| `stability.lateness_threshold` | Stability monitor | Alert threshold for lateness spikes.
| `behavior.*` | Behavior controller | Need thresholds and job arrival buffer guiding scripted policy.
| `employment.*` | Employment loop, lifecycle, console | Grace windows, absence slack, exit caps, queue limits, enable/disable flag.
| `perturbations/*.yaml` | Scheduler, lifecycle | Event probabilities, fairness buckets.

## 5. Extension Points & TBD Work
- **Queue Manager**: telemetry now emits `queue_conflict` events with rivalry intensity; next step is throttling heuristics and pathfinding-aware reservations.
- **Embedding Allocator**: integrate allocator metrics into release/shadow promotion gating and observer payloads.
- **Telemetry Transport**: formalise WebSocket schema; consider gRPC fallback.
- **FFI Pathfinding**: define stable C ABI if Rust/C++ microservice introduced; interface contract TBD.
- **Renderer Integration**: expose observer subscription to drive external renderer (pooled from telemetry diffs).

## 6. Testing Matrix
| Test Type | Coverage | Status |
| --- | --- | --- |
| Unit (`pytest`) | config loader (queue fairness, embedding allocator), reward clipping, console command validation | Partial (loader covered) |
| Integration | PettingZoo env step, lifecycle exit→spawn, telemetry diff formatting | TODO |
| Scenario | Queue contention, perturbation fairness, promotion/rollback dry run | TODO |
| Chaos | Telemetry backpressure, agent removal, utility outages | TODO |

## 7. Sequencing Checklist
1. Implement queue manager and embedding allocator to honour new config sections.
2. Flesh out observation tensors and integrate embedding allocator cooldown logging.
3. Wire promotion/rollback console commands and telemetry metrics.
4. Build integration test harness for policy step → reward → telemetry pipeline.
5. Stand up telemetry transport prototype (WebSocket) for demo readiness.

This guide will evolve alongside implementation milestones; keep cross-references (`docs/program_management/snapshots/CONCEPTUAL_DESIGN.md`, `docs/program_management/snapshots/REQUIREMENTS.md`, `docs/ops/OPS_HANDBOOK.md`) up to date when interfaces shift.
