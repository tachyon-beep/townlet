# Reward Engine

The reward engine aggregates per-agent signals every tick. It applies guardrails for PPO
stability and ensures feature flags drive optional reward taps. This note documents the Phase C1
social reward hook added in Milestone M4 Phase 4.3.

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
- `tests/test_reward_engine.py` covers: formula application, need overrides, and termination window
  suppression.
- `tests/test_relationship_metrics.py::test_consume_chat_events_is_single_use` ensures the helper
  buffer is single-use and safe for reward integration.

## Operational Notes
- Update configs under `configs/examples/` or `configs/scenarios/` to toggle C1 rewards via
  `features.stages.social_rewards`.
- Training harness honours `training.social_reward_stage_override` plus
  `training.social_reward_schedule` (cycle-indexed) before each rollout/train cycle;
  use `scripts/manage_phase_c.py` to manage these values safely.
- When refreshing goldens, capture scenario runs that exercise chat interactions so PPO drift tests
  detect regression in social reward magnitudes.
