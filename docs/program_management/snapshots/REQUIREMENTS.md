# Townlet — Requirements v1.3

Source of truth: docs/program_management/snapshots/CONCEPTUAL_DESIGN.md (v1.3)
Config identity: `config_id` must be included in logs, snapshots, and release metadata.

## 1. Feature Flags

Provide a single `features` object in config with explicit stages and toggles:

```yaml
config_id: "v1.3.0"
features:
  stages:
    relationships: "B"        # OFF | A | B | C1 | C2 | C3
    social_rewards: "C2"      # OFF | C1 | C2 | C3
  systems:
    lifecycle: "on"           # on | off
    observations: "hybrid"    # full | hybrid | compact
  training:
    curiosity: "phase_A"      # phase_A | off
  console:
    mode: "viewer"            # viewer | admin
```

Observation variant must be baked into `config_id` and the policy hash; candidates that change variant require a variant A/B eval gate before promotion.

Migration: on `config_id` mismatch, reject snapshot load unless a migration step is declared and passes.

## 2. Time & Determinism

- Tick: 250 ms real-time; 1,000 ticks = 1 in‑sim day.
- Time dilation: {1×, 10×, 100×, pause}; hot-switchable.
- Determinism: three RNG streams — `world`, `events`, `policy`; captured in snapshots. Document reseed policy on spawn/exit.

## 3. Observation Contract

Common fields:

- Self scalars (~15): needs[hunger, hygiene, energy], wallet, time_sin, time_cos, has_job, lateness, last_action_id, last_action_success, last_action_duration.
- Social snippet: top-2 friends + top-2 rivals; each (id_embed_dim=8 + trust, fam, riv) → 11 floats; total 44.
- Personality: 3 floats.
- LSTM state is internal (not part of obs).

Variants:

- full: local egocentric map 9×9..12×12 with channels for occupancy, object types, affordance/path hints; + common fields.
- hybrid: thinner map + directional fields (unit vectors + distance) to shower, fridge, till, home, work; keep occupancy/agents.
- compact: no map; distilled vectors only; include 4‑logit NSEW path hint.

IDs & embeddings:

- Max agent IDs (e.g., 64). On respawn, assign new ID; do not return an embedding slot to service until its two-day cooldown (~2,000 ticks) has elapsed. Track `released_at_tick` so the allocator prefers fully cooled slots; if all slots remain in cooldown, reuse the oldest-expired slot and emit a warning. New embeddings initialise near mean/zero.

Spatial index:

- Maintain a uniform grid bucket (or quadtree) for neighbor lookups; O(1) expected for local queries; required for 50+ agents and hybrid/compact variants.

## 4. Action Space & Masking

- Primitives: Move(N/E/S/W), Interact, Wait, Talk, Buy, UseItem, Sleep, Equip.
- Options: GetFed, GetClean, GoToWork, ShopGroceries, Sleep, Socialise(target?).
- Masking: expose masks for impossible options and obviously invalid primitives (e.g., Talk without target, Interact when no queue slot, UseItem without item).
- Option commitment: enforce a commit window `K_ticks` (default 15) unless a hard need threshold is crossed.
- LSTM context: retain hidden state on option switches by default; reset only on hard context cuts (teleport, possess, death). Expose `ctx_reset_flag` in obs.

## 5. Queues, Reservations, Collisions

- Reservations: reserve target tile/object; auto-release on success/fail/timeout.
- Queue nodes: ordered queue tiles; agents select next free; stalled queues → timeout + path retry.
- Arrival conflict: tie-break by `patience` ± jitter; fallback to jitter when off.
- Queue fairness: cooldown for cutters/blockers at that facility (~60 ticks); tiny queue‑age priority to reduce starvation.
- Deadlock breaker: after N failed retries, permit one‑tick “ghost step” and log.

## 6. Rewards & Guardrails

Config keys and ranges (example defaults):

```yaml
rewards:
  needs_weights: { hunger: [0.5..2.0]=1.0, hygiene: [0.2..1.0]=0.6, energy: [0.4..1.5]=0.8 }
  punctuality_bonus: [0..0.1]=0.05
  wage_rate: [0..0.05]=0.01
  survival_tick: [0..0.01]=0.002
  faint_penalty: [-5..0]=-1.0
  eviction_penalty: [-5..0]=-2.0
  social:
    C1_chat_base: [0..0.05]=0.01
    C1_coeff_trust: [0..1]=0.3
    C1_coeff_fam: [0..1]=0.2
    C2_avoid_conflict: [0..0.02]=0.005
  clip_per_tick: [0.01..1.0]=0.2
  clip_per_episode: [1..200]=50
  no_positive_within_death_ticks: [0..200]=10
shaping:
  use_potential: true
curiosity:
  phase_A_weight: [0..0.1]=0.02
  decay_by_milestone: M2
```

Rules:

- Money is a resource only; not in homeostatic loss.
- Punctuality window: triangular weighting within ±30 sim minutes of shift start; ensure “one skipped meal pain” > max punctual bonus.
- Clip per‑tick absolute reward to `clip_per_tick` and per‑episode to `clip_per_episode`.
- For death/exit triggers, do not grant positive rewards within `no_positive_within_death_ticks` after trigger.
- Track running mean/std of per‑tick rewards (for logging/optional normalisation); allow value‑loss scaling when flipping C‑phases.
- Terminal penalty sanity: in eval, assert typical daily cumulative reward >> 10×|terminal_penalty| to ensure no EV‑positive reset strategies.

## 7. Economy Invariants

Reference basket: rent/day + 3 meals + hygiene consumables; baseline wage/day must cover basket with 10–20% slack. Validate on price/wage change.

Auto‑tuner (optional):

- PID‑style micro‑adjustments within bounds to wage_rate or staple prices when KPI drift persists across two windows; log adjustments; never during Phase A.

## 8. Lifecycle

- `training_mode`: off during Phase A/B; on for Phase C eval/live.
- Exits/day cap=2; cooldown=120 ticks.
- Collapse/eviction/unemployment/chronic thresholds per conceptual spec.
- City events suppress related exits during event + grace window (e.g., 60 ticks post-end).
- Replacement spawn: 5–20 ticks; starter kit; optional elitist warm start (jitter σ=0.01); never from failed agent.

Credit assignment & churn:

- Use per‑agent returns/advantages; reset advantage traces on per‑agent termination/spawn. No cross‑agent shaping. Optionally baseline returns by population running stats.

## 9. Scheduler (Perturbations)

- Bounded daily rates (per spec) with per‑agent cooldown buckets.
- Limit 2-event overlap probability <5%/day; otherwise auto-stagger with jitter.
- Suppress lifecycle exits for N ticks after city‑event end (grace window).

## 10. BC → Anneal

Dataset manifest must include stress scenarios: low money, outage mid‑affordance, price spike, queue contention, lateness.
Targets: record scripted action logits and value targets.
Gate: imitation accuracy ≥90% on held‑out scripted episodes; value MSE within tolerance before anneal.
Anneal: start 80/20 scripted/learned → 0 scripted; freeze if KPIs drop >30% vs baseline.

## 11. Stability & Promotion

- Windows: rolling 24h (1,000 ticks). Require two consecutive wins to promote.
- Gate formula: hold/pin on sharp regression; implement lateness/starvation/option‑thrash canaries.
- Release vs shadow: viewers use release; training happens on shadow replicas.
- Eval suite: fixed‑seed scenarios per milestone; variant A/B gate (do not promote variant changes without passing A/B eval).
- Golden rollouts replay: offline eval to catch catastrophic forgetting; alert on regression > threshold.

Policy/version compatibility:

- New spawns must use the current release policy (not shadow). If `features.observations` differs between release and shadow, defer variant change until promoted; do not mix.

## 12. Save/Load & Hot‑Reload

Snapshot must include: world state, RNG seeds (3 streams), policy hash, `config_id`, obs variant, anneal ratio.
Hot‑reload allowed: affordances YAML, perturbations; must pass dry‑run parse + checksum.
Restart required: reward weights, network architecture, embedding table size.

Backpressure & circuit breakers:

- Telemetry pub/sub must drop/aggregate diffs when backlog exceeds threshold; circuit breaker trips to preserve sim loop; emit warning.

Console idempotency:

- Accept optional `cmd_id`; deduplicate replays/retries server‑side.

## 13. Console & Auth

- Token-gated; “viewer” mode allowlist (no destructive ops). Log command, issuer, result.
- Standard error codes/strings (examples): `E_NOT_FOUND`, `E_ALREADY_POSSESSED`, `E_BLOCKED_TILE`, `E_BUSY_TARGET`, `E_INVALID_ARG`.

## 14. Telemetry & Observer API

- Pub/sub: initial full snapshot then diffs; include `tick`, `agents[..]`, `events[..]`, `economy`, `weather`, `utilities`.
- Telemetry schema: versioned; needs in [0,1]; money in “meals” units. Privacy mode hashes agent IDs.
- Provide JSON Schema/Proto definitions and a changelog for UI parity.
- Metrics to expose: embedding_collision_rate, slowest_tick_ms (rolling top‑N), queue_block_cooldowns, ghost_step_count, reward_clip_events, variant_id.

## 15. Performance Targets

- ≥4k env‑steps/sec on 8×8 agents, full obs, CPU‑only.
- PPO baseline GPU batch size ~64k steps/iter (tune later).

Acceleration plan:

- Hot paths (affordance apply, neighborhood queries, rewards) are candidates for Numba/Cython.
- Keep a thin FFI boundary for optional Rust/C++ pathfinding; guard behind feature flag.

## 16. Testing & Acceptance

Golden tests

- Affordance YAML invariants: schema, types, numeric ranges, precond/effect units.

Fuzz & failure injection

- 10k‑tick sim fuzzer; assert no deadlocks/NaNs/leaks; random teleports; blackout toggles mid‑affordance.
- Utility outage during shower must fail gracefully; no stuck reservations.
- Blackout + eviction grace suppresses exits.
- Mass arrival surge (3 in quick succession) → no deadlocks.

Economy & KPI gates

- Basket sanity: wages/day ≥ basket * (1.1..1.2) or fail.
- KPI unit tests: lateness spike triggers rollback; starvation=0 in M0; attendance ≥ target in M2.

Property‑based tests

- Economic invariants (prices, wages, basket) hold across randomized scenarios (units, ranges, bounds).

Obs variant A/B

- Same seed on full vs hybrid; attendance within ±10% of baseline; key KPIs within bands.

Chaos engineering

- Random agent removal; simulated telemetry backpressure; network partitions between modules. Sim should degrade gracefully; no deadlocks.

Promotion protocol

- Candidate passes eval suite twice (consecutive windows); variant changes must pass A/B gates; no canaries tripped.

## 17. MVP Cutlist (if needed)

- Drop either outage or blackout in M4; keep one.
- Only hybrid obs until perf demands otherwise.
- Skip age‑out and automatic arranged_meet; keep console control only.
