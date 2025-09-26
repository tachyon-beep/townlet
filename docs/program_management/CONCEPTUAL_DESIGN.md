# Townlet — Conceptual Design v1.3

## 0. What Changed (Quick)

- Obs size sanity-checked (~500–800 floats; ample headroom).
- Relationship cap: Top-K = 6 ties per agent (3 “friend”, 3 “rival”), sparse, decaying.
- Curriculum refined: Insert M2.5 Basic Conflict; split Phase C into C1/C2/C3; add BC warm-start + anneal for primitives.
- Rewards: first-class config, experiment harness, and guardrails.
- Emergence: perturbation scheduler (price spikes, outages, arranged meets) without reward taps.
- Safety: console validation, narration rate limiting, stability monitor with canaries + rollback policy.
- Observations: switchable variants (full | hybrid | compact) via config.
- KPIs: add throughput per observation variant alongside self-sufficiency, tenure, relationships, conflicts.
- Lifecycle & Turnover: per-agent terminations, capped exits/day + cooldown, newcomer spawn, AFI analytics, new hooks/console/config, arrival/exit vignettes.
- Ops & Eval hygiene: feature flags + hot‑reload safety + console auth + profiling; RL guardrails and sim polish (reward normalisation, action masking, queue fairness, deadlock breaker, economic sanity, optional spoilage); observability (policy inspector, event dedupe, audio toggle, telemetry schema + privacy).

---

## 1. Vision

An always-on, small town life-sim where 6 to 10 agents at PoC (scaling later) learn daily living via DRL. Viewers can meddle with a live console. The charm comes from simple needs, a clean affordance system, lightweight personalities, and a sparse relationship graph that produces drama without wrecking training.

## 2. Scope for the PoC

- **World**: 2D grid, 48×48. Homes, grocer, café, office, park, gym (shower).
- **Agents**: 6–10 citizens. Shopkeepers can be scripted early.
- **Needs**: hunger, hygiene, energy. Social added in Phase C.
- **Learning**: PPO at option level first. Primitives scripted initially; later unfreeze.
- **Run mode**: headless training shards continuously; viewer subscribes to state.

## 3. Core Principles

1. **Simple but legible**. Grid world with explicit affordances.
2. **Hierarchical control**. Options over primitives to dodge exploration traps.
3. **Hooks everywhere**. Hot events and YAML affordances for live tinkering.
4. **Sparse social memory**. Drama with a tiny memory footprint.
5. **Phased complexity**. Turn features on in stages to preserve stationarity.

## 4. World Model

- **Tiles**: floor, wall, door, road, counter, table, queue nodes.
- **Objects**: bed, fridge, stove, shower, wardrobe, till, desk, shelf.
- **Weather**: sunny or rainy or cold. Affects warmth, path cost, and some prices.
- **Utilities**: power and water booleans with random faults.
- **Economy**: items have prices and stock. Daily restock truck. Simple wages. Daily rent.
  - Units: define 1.0 money unit ≈ price of a basic meal; baseline wage rate targets ~0.01 per tick; perturbations (inflation) bounded via scheduler magnitudes.

**Affordances** are defined declaratively and hot-reload:

```yaml
- id: use_shower
  object_type: shower
  preconds: [ "occupied == false", "power_on == true" ]
  duration: 30
  effects: { hygiene: +0.45, energy: -0.03, money: -0.2 }
  hooks: { before: ["on_attempt_shower"], after: ["on_finish_shower"], fail: ["on_no_power"] }
```

### 4.1 Queues & Collisions

- Reservations: interacting agents reserve their target tile/object to prevent deadlocks; reservations auto-release on success/fail/timeout.
- Queue nodes: interactive objects expose an ordered list of queue tiles; agents join the next free node; stalled queues trigger a timeout + path retry.
- Arrival conflict: when two agents reach the same node on the same tick, tie‑break by `patience` ± small jitter; if `patience` is disabled, use uniform random with jitter.
- Queue fairness: apply a short cooldown to agents that cut in or block, and add a tiny queue‑age priority so the same agent cannot dominate a bottleneck.
- Deadlock breaker: after N failed retries, allow a one‑tick “ghost step” to clear collisions, then log the incident for diagnostics.

## 5. Agent Model

### 5.1 Needs and State

- Needs vector in [0, 1]: hunger, hygiene, energy. Money is not a need.
- Wallet (money) is a scalar resource; keep it out of the homeostatic loss. Work earns money; prices/rent create pressure to earn.
- Per‑tick natural decay rates are defined per need (config), in [need units]/tick.
- Inventory: raw food, meal, clean clothes.
  - Optional spoilage (flag): meals can go stale after X hours to prevent extreme hoarding.
- Job status: has_job, site, shift window.
- Memory: home location, known shops, last failures.

### 5.2 Personality (fixed at spawn, observed by policy)

- `extroversion` [−1, 1]: social pull and chat gains.
- `forgiveness` [−1, 1]: scales down negative social deltas; speeds rivalry decay.
- `ambition` [−1, 1]: increases rivalry from work conflicts; higher punctuality pressure.
- Reserve `frugal` and `patience` behind a feature flag if needed; if `patience` is enabled, it participates in queue tie‑breaks.

### 5.3 Relationships (sparse, multi-dimensional)

Per pair, capped store per agent with hourly decay; evict weakest when full.

- `trust` influences help, lending, and compliance.
- `familiarity` influences chat ease and comfort.
- `rivalry` influences queuing conflicts and avoidance.
- Event-driven updates with small deltas. Clamp to [−1, 1]. Drop faint ties.

Event table sketch:

| Event              | trust |  fam  |  riv |
| ------------------ | :---: | :---: | :--: |
| shared_meal       |  +.10 |  +.25 |   0  |
| queued_politely   |  +.05 |  +.05 | -.05 |
| blocked_shower    |   0   |  -.05 | +.15 |
| took_my_shift    |  -.10 |   0   | +.30 |
| helped_when_late |  +.20 |  +.10 | -.10 |
| good_chat(q)      | +.05q | +.10q |   0  |
| failed_chat       |   0   |  -.05 | +.05 |

Personality hooks: `forgiveness` scales negatives (down to ~50% at high end); `ambition` adds ~+30% rivalry on work-conflict events; `extroversion` adds +0.02 familiarity on successful chats.

Cap ties per agent at Top-K = 6 (e.g., 3 “friend”, 3 “rival”); decay toward 0 and evict weakest when full. Cap-aware admission rule:

```python
def update_relationship(self, other_id, d):
    if other_id in self.ties:
        apply_deltas(other_id, d)
    elif len(self.ties) < 6 or abs(d['trust']+d['fam']-d['riv']) > 0.2:
        add_relationship(other_id, d)  # evict weakest if full
```

## 6. Observations

Per agent, per tick. Target ~500–800 floats total.

- **Egocentric local map**: 9×9 to 12×12 tiles with channels for occupancy, object types, and simple path hints (≈324–432 floats typical).
- **Self scalars**: needs, wallet, time of day sin/cos, has_job, lateness flag (~15).
- **Last action**: id, success flag, duration.
- **Personality**: 3 floats.
- **Social snippet**: top-2 friends and top-2 rivals as (id-embed 8 + trust/fam/riv 3) per tie → ~44 total, plus local summaries (mean/max rivalry/trust nearby).
- LSTM hidden is internal to the network (not part of obs tensor).

Variants (config-switchable):

- **full**: baseline map + scalars + social snippet.
- **hybrid**: slimmer map; replace full affordance channel with directional fields to nearest targets (shower, fridge, till, home, work): 2D unit vector + distance scalar per target; keep occupancy/agent positions.
- **compact**: no map; distilled vectors only (distances, bearings, flags like `rival_in_current_queue`, top-K social tuples, and a 4-logit NSEW path hint from a shallow planner).

Config example:

```yaml
observations:
  variant: "hybrid"   # full | hybrid | compact
  local_window: 9
  id_embed_dim: 8
```

IDs & embeddings:

- Fix a max agent ID namespace (e.g., 64 IDs) and size embedding tables accordingly.
- On respawn, assign a new ID; avoid immediate reuse of the prior embedding slot for at least two in-sim days (~2,000 ticks). Track `released_at_tick` per slot and only return a slot to the free pool once its cooldown expires; if the pool is exhausted, recycle the oldest-expired slot and log the reuse.

## 7. Action Space

### 7.1 Primitives

Move (N E S W), Interact(object, affordance), Wait, Talk(target), Buy(item), UseItem, Sleep, Equip.

### 7.2 Options

GetFed, GetClean, GoToWork, ShopGroceries, Sleep, Socialise(target optional), DailyRoutine later.

Meta-policy chooses an option. Option may call a short scripted controller for primitives in the PoC. Later unfreeze primitives for end-to-end fine-tuning.

Social success gate:

```python
p_success = 0.7
           * (1 + 0.3*clip(trust_ij, -1,1))
           * (1 + 0.2*clip(fam_ij, -1,1))
           * topic_pref_j
```

### 7.3 Action Masking

- When an affordance/option is impossible, expose an action mask to the meta head and suppress invalid selections to avoid learning “try impossible, get penalty”.

## 8. Rewards

- **Homeostasis**: `−Σ w_i * deficit_i²` per tick.
- **Potential shaping**: φ(s) = `−Σ w_i * deficit_i` to preserve optimality.
- **Work**: wages while working; punctuality bonus within a small window.
- **Survival**: small life tick; penalties for faint/evict.
- Money: affects rewards via wages/costs and constraints (buying, rent) only — it is not part of the homeostatic loss.
- **Phase C social rewards (split)**:
  - **C1**: reward only successful conversation completion: `+0.01 + 0.3*trust + 0.2*fam` (small scale).
  - **C2**: add conflict-avoidance micro-bonus `+0.005`.
  - **C3**: allow small relationship-quality modifiers on C1 reward.
  - No global “social need” scaling by affinity in the PoC.

Lifecycle note:

- Apply a small terminal penalty on agent exit (see lifecycle config); never grant reward on death.

First-class reward config:

```yaml
rewards:
  needs_weights: { hunger: 1.0, hygiene: 0.6, energy: 0.8 }
  punctuality_bonus: 0.05         # per on-time work interval
  wage_rate: 0.01                  # per tick at work
  survival_tick: 0.002
  faint_penalty: -1.0
  eviction_penalty: -2.0
  social:
    C1_chat_base: 0.01
    C1_coeff_trust: 0.3
    C1_coeff_fam: 0.2
    C2_avoid_conflict: 0.005
shaping:
  use_potential: true
```

Guardrails:

- Hard floor overrides: ignore social biases when any need deficit > 0.85.
- Cap punctuality bonus to be less than the hunger pain from skipping one meal.
- No positive reward within N ticks around a death/exit trigger (both immediately before detection and after) to prevent last‑second reward exploits.
- Clip per‑tick absolute reward to ±r_max (config) to keep PPO stable.

Normalisation & scaling:

- Track running mean/std of per‑tick rewards for logging and optional normalisation.
- Optionally scale value loss when flipping C‑phases to avoid instability.

Exploration (early only):

- Add a small RND curiosity bonus in Phase A to reduce flailing; decay it to zero by M2; keep it off during social phases.

Experiment harness (sketch):

```python
def run_experiment(cfg, seed):
    env = Townlet(cfg, seed)
    trainer = PPO(cfg.ppo)
    metrics = []
    for epoch in range(cfg.epochs):
        trainer.learn(n_steps=cfg.steps_per_epoch)
        m = eval_suite(trainer.policy, env, cfg.eval_episodes)
        metrics.append(m)
        if stability_guard.tripped(m):
            break
    return metrics
```

Protocol:

- Use a one-agent micro-suite for A/B on weights before multi-agent.
- Light grid search or PBT on keys above; auto-log metrics: time to self-sufficiency, lateness rate, starvation incidents, attendance, option thrash.

## 9. Learning Architecture

- **Framework**: PettingZoo ParallelEnv. PPO via RLlib or CleanRL.
- **Network**: small CNN on local map to 64 features, MLP on scalars, then LSTM 128. Two heads: meta-option and value. Primitive head later.
- **Population training**: 3 to 8 replicas with a light PBT jitter. Promote checkpoints that hit KPIs.
- **Stability gate**: rollback guard on sharp regressions; gated promotion of candidates (metrics over rolling 24h windows = 1,000 ticks; require two consecutive windows to promote):

```python
if mean_last_50 < 0.7 * mean_prev_50:  # example threshold
    hold/pin current release
```

- **Phases**:

  - Phase A: needs and jobs; personalities present; relationships off.
  - Phase B: relationships in observations only; no social rewards.
  - Phase C: C1 → C2 → C3 social rewards; reduce entropy slightly; longer eval windows.

LSTM context handling:

- Retain LSTM hidden across option switches by default; reset only on hard context cuts (teleport, possess, death). Expose a `ctx_reset_flag` in observations.

Per-agent terminations:

- Treat agent death/exit as per-agent episode end (`terminations[agent_id]=True`); other agents continue.
- Optionally down-weight the last ~100 ticks of a failing agent to reduce overfitting to doom spirals.

Canaries & rollback:

- Lateness rate spikes above 2× baseline.
- Starvation incidents per agent per day exceed threshold.
- Option-switch rate spikes >25% for two evaluation windows.

Rollback by pinning current release; continue training in shadow; promote only after two consecutive evaluation wins.

Evaluation suite & promotion:

- Fixed‑seed scenarios per milestone (M0/M1/M2/…) run on each candidate; produce a scorecard (attendance, starvation=0, lateness, etc.).
- One “release policy” serves viewers; “shadow policies” train. Promotion requires passing the eval suite twice (two consecutive windows).

Catastrophic forgetting guard:

- Maintain a replay set of “golden” rollouts from prior releases; run periodic offline eval; alert on regression beyond threshold.

Scripted → learned primitives handoff:

1. Phase A/B use scripted controllers under options.
2. Record trajectories for key options (GetFed, GetClean, ShopGroceries, GoToWork).
3. Train primitive policy head with behaviour cloning until imitation loss crosses target.
4. Mixed control per primitive call (start 80% scripted / 20% learned; anneal to 0 scripted over N epochs).
5. PPO fine-tunes end-to-end after BC warm start.

BC objective (with value distillation by default):

```python
L_bc = CE(a_script, a_pred) + λ * MSE(v_script, v_pred)
```

Safety: if performance drops >30% against baseline KPIs during anneal, freeze at current mix and retry later with more BC data.

Success gate for BC → anneal:

- Imitation accuracy ≥ 90% on held‑out scripted episodes (actions); value targets within tolerance. Only then begin anneal.

## 10. Hooks, Console, and Admin

Global hooks receive `(tick, agent_id, event, context)` for:
`on_tick`, `on_spawn`, `on_need_threshold`, `on_affordance_before`, `on_affordance_after`, `on_affordance_fail`, `on_price_change`, `on_weather_change`, `on_power_cut`, `on_conflict`, `on_quit_job`, `on_agent_exit`, `on_agent_spawn`, `on_agent_near_death`.

Console commands:

```markdown
spawn <name> <x> <y>
teleport <name> <x> <y>
price <item> <value>
blackout on|off
rain start|stop
possess <name>
setneed <name> hunger 0.9
set_rel <a> <b> trust|fam|riv <value>
force_chat <a> <b> q=0.8
arrange_meet <a> <b> <place_id>
```

```python
def possess_agent(aid):
    if aid not in live: return "Error: not found"
    if aid in possessed: return "Error: already possessed"
    if agents[aid].state == "sleep": return "Error: sleeping"
    possessed.add(aid); return "OK"
```

Console commands validated; add safety guards for common errors.
Including:

- Possess only non-sleeping agents.
- No teleport into blocked tiles.
- `set_rel` only for valid ids and dim names `trust|fam|riv`.
- `force_chat` denies if target is in a blocking affordance.

Lifecycle console controls:

```markdown
kill <name> reason=<text>
toggle_mortality on|off
set_exit_cap <per_day>
set_spawn_delay <min> <max>
set_death_threshold <need> <value> <ticks>
```

## 11. Events and Narrative

- **Dramatic hooks** that cost time rather than changing reward structure.

  - Rage-quit job when stress exceeds a threshold. Cooldown before re-hire.
  - Public argument when high rivalry pair collide in a queue. Causes delay and narration.
  - Spiral day debuff after multiple failures. Clears after sleep.
- **Narration templates** for key states. Global and per agent throttling.

  - “Alice is late and Bob is blocking the shower. Rivalry 0.72.”
  - “First clash between Alice and Bob. They will remember this.”
  - “Carol and Dana bonded over lunch. Trust 0.41.”

```python
if throttle.can_narrate("late_blocked", agent_id):
    emit("{A} is late and {B} is camping the shower. Rivalry {riv:.2f}.")
```

Perturbation scheduler (event-layer only; no reward taps):

- Low-frequency, bounded events keep stories bubbling and legible:
  - Price spikes once per day window
  - Blackouts or water outages (short duration)
  - Queue bottlenecks by temporarily closing a shower or till
  - System-arranged meets between top rivals at the café

Config example:

```yaml
perturbations:
  price_spike: { prob_per_day: 0.3, magnitude: [1.2, 1.8], duration_min: 60 }
  blackout:    { prob_per_day: 0.15, duration_min: [20, 60] }
  outage:      { prob_per_day: 0.10, duration_min: [20, 60] }
  arranged_meet: { prob_per_day: 0.25, target: "top_rivals", location: "cafe" }
```

Scheduler fairness:

- Apply per‑agent cooldown buckets so perturbations do not repeatedly target the same agent.

## 12. UI and Telemetry

- **Viewer**: simple web client. Tiles and icons. Agent card shows needs, current option, top friends and rivals, and last event.
- **Relationship overlay**: toggle to draw green or red lines with thickness by magnitude.
- **Ticker**: narrative stream with click-to-focus.
- **Event dedupe**: a short window deduplicates repeating narratives (beyond throttle) to avoid spam when conditions persist.
- **Metrics**: attendance, starvation events, shower cadence, option switch rate, chat success vs trust, queue conflicts per day, diversity of lunch pairings.
- **Replays**: snapshot plus RNG seed for short deterministic replays.
- **Audio**: config toggle and volume for SFX (arrival car, etc.).
- **Policy inspector**: per‑agent card shows top‑3 option logits, value estimate, and key bias terms (e.g., `friend_near`, `rival_near`) for debugging.

KPIs:

- Self-sufficiency: % agents with all needs > 0.3 for 24h.
- Job stability: mean tenure > 3 days.
- Relationship formation: ≥60% agents have at least one tie with |value| > 0.3.
- Conflict resolution: <20% conflicts escalate to repeated avoidance.
- Throughput: steps/sec per env shard, tracked per observation variant (full | hybrid | compact).

Ethics & sandbox:

- Violence/harassment guardrails: ceiling at verbal arguments only; apply time penalties + narration; no physical harm.
- Streamer mode: optional redaction of agent names (display IDs only) for privacy.

Telemetry schema:

- Lock types/units (needs in [0,1]; money in “meals” units); version the schema and publish a JSON/Proto definition for UI parity.
- Privacy mode: hash/redact agent IDs in logs exported publicly.

Assets config:

- Name generator list and arrival SFX filenames are keys in config so packs can be swapped without code changes.
  - Also expose an audio volume and on/off toggle.

Observer API (pub/sub):

- Initial message is a full snapshot; subsequent messages are diffs.
- Schema sketch:

```json
{
  "tick": 12345,
  "agents": [
    {"id":"alice","pos":[10,14],"option":"GetFed","needs":{"hunger":0.35,"hygiene":0.8,"energy":0.6},
     "ties_top":[{"id":"bob","trust":0.1,"fam":0.3,"riv":0.2}]}
  ],
  "events":[{"t":12344,"type":"narration","msg":"Alice is late..."}],
  "economy":{"prices":{"meal":1.0},"stock":{"shop_1":{"meal":10}}},
  "weather":{"rain":false,"cold":false},
  "utilities":{"power":true,"water":true}
}
```

Snapshots & repro:

- Snapshot schema includes: world state, RNG seeds, policy hash, config version (`config_id`).
- Short replay slices: capture N ticks around a bug; deterministic by seed.
- Config versioning: include `config_id` in logs; refuse to load snapshots with mismatched config.

Seed discipline:

- Lock three RNG streams (world, events, policy) and capture them in snapshots.
- Document which streams are reseeded on spawn/exit to keep repro consistent.

Lifecycle UI:

- Arrival vignette: camera pans to roadside; “New arrival: {A}”.
- Exit vignette: ambulance or moving van icon; reason tooltip.
- Optional cemetery/ledger: last 5 exits with reasons and lived days.

Lifecycle metrics:

- Exits/day vs cap; exit cooldown adherence.
- Agent Fitness Index (AFI) per agent (analytics only).
  - Surface AFI on the agent inspector UI for transparency.

## 13. Curriculum

1. **M0** Home sandbox only. Maintain needs.
2. **M1** Add shop. Stipend. Buy and cook basics.
3. **M2** Add job. Remove stipend. Pay only at work. Add punctuality; loop stable.
4. **M2.5** Basic Conflict Intro — queue friction/penalties without relationships.
5. **M3** Relationships ON as observations only; option biases include social context.
Phase C & handoff (6–10):
6. **C1** Chat reward only (tiny).
7. **C2** Add conflict-avoidance bonus.
8. **BC** Train primitives via behaviour cloning on recorded scripts.
9. **Anneal** Scripted→learned primitives (start 80/20; anneal to 0 scripted).
10. **C3** Add small relationship-quality modifiers.
11. **M4** Perturbation scheduler ON; narration + relationship overlay.
12. **M5** Personality polish, admin social commands, evaluation gating.

Curriculum guard:

- City‑wide events (blackouts, outages, price spikes) are locked out during M0–M2 to stabilise early learning; they flip on at M4 per spec.
- Optional auto‑phase advancement: transition when KPI bands are held for two consecutive windows; manual override supported.

## 14. Risks and Mitigations

- **Training instability** when relationships turn on. Use phased enable and KPI-gated promotion of checkpoints.
- **Boring optimal loops**. Conflicting needs, price shocks, and tiny curiosity bonus early mitigate this.
- **Cliques that starve needs**. Safety guard ignores rivalry when a need exceeds a hard threshold.
- **Narration spam**. Rate limit and dedupe templates.

## 15. Performance and Scale Notes

- Sparse ties with Top-K = 6 per agent keep memory very low (<1 KB/agent for ties alone).
- Event-driven updates plus hourly decay pass are cheap.
- With 8 envs × 8 agents and no render, expect several thousand steps per second on CPU.
- Future scale to 3D voxels and 50+ agents by mirroring server state into a renderer and keeping Python sim authoritative.
- Observation variants enable throughput/competence trade-offs; track per-variant shard performance.
- Minimal perf targets: ≥4k env-steps/sec on 8×8 agents with full observations, CPU-only.
- PPO baseline: GPU batch size ~64k steps/iteration (tune later).

## 16. Minimal Data Sketches

### Agent

```json
{
  "id":"alice",
  "pos":[10,14],
  "needs":{"hunger":0.35,"hygiene":0.8,"energy":0.6},
  "wallet":25.0,
  "job":{"site":"office_1","shift":[540,1020],"late":false},
  "inventory":{"food_raw":1,"meal":0,"clothes_clean":1},
  "personality":{"extroversion":0.4,"forgiveness":0.2,"ambition":0.7},
  "social_top":[{"id":"bob","trust":0.1,"fam":0.3,"riv":0.2}],
  "option":"GetFed"
}
```

### Affordance runtime

```json
{"agent":"alice","object":"fridge_3","affordance":"eat_meal","duration":12,"delta":{"hunger":+0.4,"money":0}}
```

## 17. Success Criteria

- Agents maintain needs and attend work within 1 to 2 in-sim days of training.
- Visible avoidance of rivals in queues by M3.5.
- Emergent small stories appear within 30 to 60 minutes of live runtime.
- Console hooks feel responsive and do not require retraining to show effects.

## 18. Lifecycle & Turnover (PoC)

Goals

- In-character consequences for chronic failure (starvation, eviction, etc.).
- Continuous population size (e.g., hold at 8 agents).
- Minimal training instability: deaths act like tidy per-agent episode boundaries.
- Optional light “evolution” by seeding newcomers from successful policies.

1 IC death & exit conditions (any one can trigger)

- Checked on rolling windows to avoid single blips.

Hard failures (instant):

- Collapse from hunger: `hunger > 0.97` for `>= 30` consecutive ticks.
- Exposure collapse (optional): `warmth < 0.05` for `>= 30` ticks during cold weather with no shelter.

Soft failures (cumulated):

- Eviction: rent unpaid for ≥2 consecutive days → evicted. If recovery fails (`money > rent*0.5`) within the next day, agent leaves town.
- Chronic unemployment: wages earned == 0 for ≥2 days while jobs are available (exclude systemic outages).
- Chronic neglect: any need > 0.9 for ≥25% of ticks over a 24h window.
- Age-out (optional): random lifespan 10–20 in-sim days (off by default).

Guardrail: if a city-wide event (blackout, water outage) is active, suppress exits caused by facilities for the duration + grace period.

On death/exit:

- Emit narration + small global delay (ambulance/transport).
- Apply terminal penalty to that agent’s return (e.g., −1.0).
- No positive rewards are credited within N ticks after the death trigger to prevent last‑second reward exploits.
- Mark per-agent `terminated=True` (PettingZoo); others continue.

2 Replacement (arrival)

- Spawn newcomer within 5–20 ticks so the town stays lively.

Spawn details:

- Entry: roadside near bus stop/car park.
- SFX: car arrival “vroom + door thunk” (client-side).
- Starter kit: `money = rent*1.5`, `food_raw=1`, `clothes_clean=1`.
- Job: 50% chance pre-assigned entry job; else apply.
- Personality: sample `extroversion/forgiveness/ambition` from fixed prior.
- Spawn diversity: use a low‑discrepancy sequence (Sobol/Halton) to spread personalities across the space for small populations.
- Social memory: empty (no inherited grudges).

Policy init:

- Simple (default): use current release policy.
- Elitist warm-start (flag): copy best-performing replica (PBT-style) with jitter σ=0.01; never copy from a just-failed agent.

Stability caps:

- Max 2 exits per in-sim day; 120-tick cooldown between exits.

3 Fitness & culling transparency

Agent Fitness Index (AFI), rolling 24h, for analytics/elitist seeding only:

```python
AFI =  wR * normalised_return
     + wN * (1 - mean_need_deficit)
     + wJ * attendance_rate
     - wV * violations
```

Narration cues:

- “{A} couldn’t keep up with rent and left town.”
- “{A} collapsed from exhaustion. Paramedics took them away.”
- Arrival: “A car pulls up. {A} steps out, new to town.”

4 Training considerations

- Use per-agent terminations; keep terminal penalty small vs day-scale returns.
- Down-weight last ~100 ticks for failing agents to avoid doom-spiral overfit.
- Cap daily exits and enforce cooldowns to limit non-stationarity.
- For elitist warm-starts, never mutate the release policy; mutate only the spawn’s copy or the target replica (PBT), not the global release.

5 Hooks, console & config

New hooks:

- `on_agent_exit(agent_id, reason)`
- `on_agent_spawn(agent_id)`
- `on_agent_near_death(agent_id, need)`

Console (in addition to existing):

```markdown
kill <name> reason=<text>
toggle_mortality on|off
set_exit_cap <per_day>
set_spawn_delay <min> <max>
set_death_threshold <need> <value> <ticks>
```

Config (yaml):

```yaml
lifecycle:
  enabled: true
  training_mode: off   # off in Phase A/B training; on for Phase C eval/live
  max_exits_per_day: 2
  spawn_delay_ticks: [5, 20]
  terminal_penalty: -1.0
  collapse:
    hunger: { threshold: 0.97, ticks: 30 }
    warmth: { threshold: 0.05, ticks: 30, enabled: false }
  eviction:
    days_unpaid: 2
    recovery_days: 1
  unemployment_days: 2
  chronic_need:
    threshold: 0.9
    fraction_of_day: 0.25
  age_out:
    enabled: false
    min_days: 10
    max_days: 20
  stability:
    exit_cooldown_ticks: 120
    suppress_during_city_events: true
  spawn_policy: "release"   # release | elitist
  elitist_jitter: 0.01
```

6 UI bits

- Arrival vignette, exit vignette, optional cemetery/ledger (see UI & Telemetry).

7 Edge-case rules

- No reward on death; terminal penalty only.
- No debt carryover across identities; money floors at 0 on spawn.
- Exits capped and suppressed during city-wide disasters to avoid mass wipe-outs.

8 Test cards

- Starvation path: block shop access; expect collapse → exit → spawn in <20 ticks; others unaffected.
- Eviction path: price spike + wage cut; ensure eviction and grace window work.
- Exit-storm guard: script three failures quickly; confirm ≤2 exits/day via cooldown.
- Elitist spawn: enable elitist seeding; new agent competence > baseline; no policy drift.

Confidence (WEP)

- Training stability with per-agent terminations and capped exits: High (~85%).
- Watchability uplift from arrivals/departures & narration: Moderately High (~75%).
- No perverse incentives introduced (terminal penalty + caps): High (~80%).

===================

## 19. Time Model & Control

- Tick spec: 250 ms real‑time per tick; 1,000 ticks = 1 in‑sim day.
- Time dilation: {1×, 10×, 100×, pause}, hot‑switchable at runtime.
- Determinism toggle: `--deterministic` fixes RNG streams (env + policy) for reproducible slices and tests.
- UI displays current sim speed and tick → day mapping.

## 20. Testing & Validation

- Golden tests for affordances: YAML invariants (preconds/effects types, ranges).
- Sim fuzzer: random event injector for ≥10k ticks; assert no deadlocks, no NaNs, no stuck reservations.
- KPI unit tests: synthetic scenarios to hit thresholds (e.g., lateness KPI spikes → rollback triggers).
- Failure injection cards:
  - Utility outage during shower → affordance fails gracefully; no stuck "occupied".
  - Blackout + eviction grace → exits suppressed during event + grace.
  - Mass arrival surge (spawn 3 quickly) → queues adapt; no deadlocks.
- Economic sanity check: baseline wages/day must cover median basket + rent with ~10–20% slack; run when prices/wages change.
- Obs‑variant A/B: run the same seed on full vs hybrid obs; define acceptance ranges (e.g., attendance within 10% of baseline).
- Fuzz path: random teleport bursts and blackout toggles mid‑affordance; assert no NaNs, no stuck reservations, and no memory growth.

## 21. Systems & Ops Hygiene

- Feature flags & config versioning:
  - `features: { relationships: "B", social_rewards: "C2", lifecycle: "on" }` and a top‑level `config_id`.
  - Savegame/schema migration note: reject or auto‑migrate on mismatches.
- Hot‑reload safety:
  - Hot‑reload allowed: affordances, event/perturbation YAML; requires dry‑run parse + checksum before apply.
  - Restart required: reward weights, network arch; log and defer.
- Console auth:
  - Token‑gated console with an allowlist of commands in viewer mode; prevent bricking towns on streams.
- Profiling hooks:
  - Per‑tick timers for pathing, affordances, RL step, IO; emit periodic report of slowest N ticks.

## 22. Optional Flags (Low‑risk)

- Venue reputation (mini): per‑venue rep nudges hiring/discounts; local only; off by default.
- Chaos hour (debug): temporarily 3× event rates for 5 in‑sim minutes to stress‑test narration/hooks.
