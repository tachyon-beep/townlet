# Reward Engine

The reward engine aggregates per-agent signals every tick. It applies guardrails for PPO
stability and ensures feature flags drive optional reward taps. This note documents the Phase C1
social reward hook added in Milestone M4 Phase 4.3 and the LR2 terminal penalty updates.

## Baseline Homeostasis
- Survival tick (`rewards.survival_tick`) seeds each agent’s reward before deductions.
- Need deficits subtract `weight * deficit^2` per need (`rewards.needs_weights`).
- Tick-level clip (`rewards.clip.clip_per_tick`) bounds the post-aggregation reward.

## Phase C1 Chat Reward
- Enabled when `features.stages.social_rewards ∈ {C1, C2, C3}`.
- Chat successes emit per-agent rewards based on the current relationship tie:
  - Formula: `chat_base + coeff_trust * trust + coeff_fam * familiarity`.
  - Quality scalars clamp to `[0, 1]` and scale the combined total.
  - Relationship data is sourced via `WorldState.relationship_tie` immediately after the chat event.
- Both speaker and listener qualify for the reward; failures never contribute.
- Need override guard: if any tracked need has a deficit > 0.85, the social bonus is skipped.

## Work & Attendance Taps
- Wage reward derives from the employment context: `RewardEngine` reads
  `world.agent_context(agent_id)["wages_paid"]` and subtracts any withheld
  wages so the reward ledger mirrors payroll telemetry. Tune via
  `rewards.wage_rate`.
- Punctuality reward scales the on-time ratio gathered by the employment
  manager. The tap uses `rewards.punctuality_bonus` as the multiplier and
  stays bounded in `[0, 1]` before scaling.
- Both taps flow through the same clipping guardrails as other reward
  components, so large wage adjustments must stay below
  `rewards.clip.clip_per_tick`.

## Terminal Penalties
- Lifecycle emits termination reasons; `RewardEngine.compute` now accepts
  an optional `reasons` mapping to distinguish faint vs. employment
  eviction.
- Faint: apply `rewards.faint_penalty` once and expose it in the breakdown
  under `terminal_penalty`.
- Eviction: apply `rewards.eviction_penalty` with the same breakdown entry
  so ops can reconcile console audits with telemetry.
- Subsequent guardrails (death-window suppression, tick/episode clipping)
  still apply, preserving the existing PPO stability guarantees.

## Termination Window Guardrail
- `rewards.clip.no_positive_within_death_ticks` blocks positive reward once an agent is terminated.
- The guard applies immediately and persists for the configured number of ticks.
- Rewards remain clipped, and negative totals still propagate (e.g., eviction penalties).

## Event Consumption Contract
- `WorldState.record_chat_success/record_chat_failure` queue chat events and update ledgers.
- `WorldState.consume_chat_events` exposes the staged events for one tick; telemetry still drains the
  underlying event log separately.
- RewardEngine consumes the staged events per tick to prevent double-crediting while preserving
  downstream telemetry.

## Validation
- `tests/test_reward_engine.py` now covers chat rewards, wage/punctuality taps, terminal penalties,
  and guardrail clipping.
- `tests/test_relationship_metrics.py::test_consume_chat_events_is_single_use` ensures the helper
  buffer is single-use and safe for reward integration.
- `tests/test_lifecycle_manager.py::test_termination_reasons_captured` verifies lifecycle emits the
  reasons that drive penalty selection.

## Operational Notes
- Update configs under `configs/examples/` or `configs/scenarios/` to toggle C1 rewards via
  `features.stages.social_rewards`.
- Training harness honours `training.social_reward_stage_override` plus
  `training.social_reward_schedule` (cycle-indexed) before each rollout/train cycle;
  use `scripts/manage_phase_c.py` to manage these values safely.
- When refreshing goldens, capture scenario runs that exercise chat interactions so PPO drift tests
  detect regression in social reward magnitudes.
