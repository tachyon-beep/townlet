# DTO Observation Inventory (WP3 Step 1)

Date: 2025-10-09

This note captures the outputs of WP3 Step 1 — building a complete inventory of
current `WorldState` consumers, gathering representative observation payloads, and
highlighting the initial schema sketch + gaps prior to adapter work.

## 1. WorldState Consumers (Policy/Loop/Training)

The table below captures **explicit** `WorldState` attribute usage discovered via
source inspection. Where possible, file and line numbers reference the current
codebase (2025‑10‑09). This mapping will drive DTO converter work and parity
tests.

| Attribute | Callers / Locations |
|-----------|---------------------|
| `world.agents` | `policy/behavior.py:55,214,258,267,378`; `policy/runner.py:153`; `policy/scripted.py:35,65`; rollout seeding in `policy/scenario_utils.py:54-133`; loop orchestration in `core/sim_loop.py:379-395`; training capture in `policy/training_orchestrator.py:172-198`. |
| `world.queue_manager` | `policy/behavior.py:64,105,282,289`; observation building `observations/builder.py:331`; loop telemetry hooks `core/sim_loop.py:501,653`; console handlers `console/handlers.py:836-861`; adapter `world/core/runtime_adapter.py:95`. |
| `world.affordance_runtime` | `policy/behavior.py:64,105,175,248,282`; loop DTO prep `core/sim_loop.py:586`; snapshot utilities `snapshots/state.py:446`. |
| `world.tick` | `policy/behavior.py:125,186,341`; loop orchestration `core/sim_loop.py:536`; adapters `world/core/runtime_adapter.py:74`. |
| `world.objects` | `policy/behavior.py:158,198,229`; observation builder `core/sim_loop.py:420`; snapshot restore `snapshots/state.py:388`. |
| `world.rivalry_snapshot()` / events | `policy/behavior.py:277-337`; loop telemetry `core/sim_loop.py:612`; telemetry publisher relationship overlays `telemetry/publisher.py:1143`. |
| `world.relationships` / overlays | `policy/behavior.py:268`; telemetry publisher `telemetry/publisher.py:1102`. |
| `world.employment` | Loop stability + telemetry (`core/sim_loop.py:440,516,652`); exporter `telemetry/publisher.py:1169`. |
| `world.perturbations` | `core/sim_loop.py:457,665`; telemetry publisher `telemetry/publisher.py:1184`. |
| `world.promotion` | `core/sim_loop.py:470`; telemetry publisher `telemetry/publisher.py:1220`. |
| Misc. (`queue_console`, `request_ctx_reset`) | Loop legacy path `core/sim_loop.py:359`; policy controller bridging `policy/behavior_bridge.py:71-128`. |

Additional consumers (console dashboards, tests) are noted here to ensure DTOs
either retain derived data via events or expose replacement helpers as part of
cleanup tasks.

## 2. Representative Observation Sample

- Captured a one-tick snapshot from `configs/examples/poc_hybrid.yaml` after a
  single `SimulationLoop.step()`.
- Output stored at
  `docs/architecture_review/WP_NOTES/WP3/dto_sample_tick.json` and includes:
  observations batch (per-agent), reward breakdown, queue metrics,
  rivalry snapshot, and stability metrics.
- This payload serves as the baseline for DTO schema prototyping and parity
  comparisons.
- A trimmed DTO-oriented sample lives at
  `docs/architecture_review/WP_NOTES/WP3/dto_example_tick.json` (per-agent
  entries + global envelope only).

## 3. Base Types, Optionality & Validation

- **Per-agent DTO (proposal):**
  - `agent_id: str`
  - `position: [int, int] | null`
  - `needs: {"hunger": float, "hygiene": float, "energy": float}`
  - `employment: {job_id: str, lateness_counter: int, attendance_ratio: float, ...}` *(optional)*
  - `inventory: {wallet: float, queue_tokens: int, ...}` *(optional keys as enabled by config)*
  - `personality: {extroversion: float, agreeableness: float, ...}` *(present only if personalities enabled)*
  - `queue_state: {pending_action: str | null, reservation: str | null, rivalry_flags: {...}}`
  - `policy_metadata: {option_commit: bool, possessed: bool}` *(used by controller guardrails)*

- **Global envelope fields:**
  - `tick: int`
  - `queue_metrics: {cooldown_events: int, ...}`
  - `rivalry_events: [{agent_a: str, agent_b: str, intensity: float, reason: str, tick: int}]`
  - `stability_metrics`: float counters + alert list; `stability_inputs`: hunger/option switches/reward samples.
  - `rewards: {agent_id: {component: float}}`
  - `perturbations: {active: {...}, pending: [...], cooldowns: {...}}`
  - `promotion_state`: optional dict from `PromotionManager.snapshot()`
  - `policy_metadata`: provider hash, anneal ratio, possession state.
  - `rng_seed`: optional int (global seed for reproducibility).

- **Optionality rules:** omit keys when data is unavailable rather than sending
  empty objects. Downstream consumers must guard for absence.
- **Schema versioning:** include `dto_schema_version` (starting `0.1.0`) in the
  envelope. Any breaking change bumps the minor version and updates fixtures.
- **Validation:** introduce Pydantic (or equivalent) DTO models in the converter
  module. CI will load captured fixtures (`dto_example_tick.json`,
  `dto_sample_tick.json`) through the models to catch regressions (`tests/world/test_observation_dto_factory.py` exercises this path).

## 4. Initial Schema Sketch, Gaps & Source Mapping

- **Per-agent coverage** matches the proposal above; the global envelope will
  mirror telemetry-derived metrics while remaining policy-focused.
- **Gaps & proposed sources:**
  - *Relationship summaries*: combine `telemetry.publisher._latest_relationship_summary`
    with `WorldRuntimeAdapter.relationships_snapshot()` to deliver both summary
    and ledger views.
  - *RNG / anneal baselines*: expose `WorldState.rng_seed()` (available via
    WP2 Step 6) and `PolicyTrainingOrchestrator._anneal_context` for parity.
  - *Deterministic ordering*: use `sorted(world.agents.keys())` plus the shared
    action vocabulary from `BehaviorBridge` when encoding DTO tensors.
  - *Historical metrics*: align DTO exports with telemetry caches (queue
    history, promotion counters) so dashboards and training stay in sync.

## 5. Risk/Follow-up Notes

- Documented consumers will guide DTO converter implementation order:
  1. Scripted policy path (low risk, deterministic).
  2. Training/ML adapters (requires parity harness).
  3. Loop/console cleanup (removing `runtime.queue_console`).
- Before coding adapters, circulate schema draft + sample payload with policy &
  training stakeholders to confirm fields and highlight any downstream
  requirements (dashboards, analytics).
- Plan to extend parity harness to compare DTO vs legacy observations over a
  short simulation window (queue fairness, rivalry events, reward trajectories).
- DTO models now live in `src/townlet/world/dto/observation.py` (exported via `townlet.world.dto`); converters should target these Pydantic surfaces.
- `SimulationLoop` currently emits and caches the DTO envelope alongside `loop.tick` telemetry (`observations_dto`) while policy paths continue to consume the legacy `WorldState`; the parity harness (`tests/core/test_sim_loop_dto_parity.py`) verifies DTO tensor equality across ticks. Global context now includes queue rosters, running affordances, and relationship metrics.
