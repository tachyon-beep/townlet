# Townlet — Conceptual Design v1.3

## 1. Vision

An always-on, small town life-sim where 6 to 10 agents at PoC (scaling later) learn daily living via DRL. Viewers can meddle with a live console. The charm comes from simple needs, a clean affordance system, lightweight personalities, and a sparse relationship graph that produces drama without wrecking training.

## 2. Scope for the PoC

* **World**: 2D grid, 48 by 48. Homes, grocer, café, office, park, gym with shower.
* **Agents**: 6 to 10 citizens. Shopkeepers can be scripted early.
* **Needs**: hunger, hygiene, energy, money. Social optional but planned.
* **Learning**: PPO at option level first. Primitives scripted. Later unfreeze.
* **Always-on**: headless training shards run continuously. Viewer UI subscribes to state.

## 3. Core Principles

1. **Simple but legible**. Grid world with explicit affordances.
2. **Hierarchical control**. Options over primitives to dodge exploration traps.
3. **Hooks everywhere**. Hot events and YAML affordances for live tinkering.
4. **Sparse social memory**. Drama with a tiny memory footprint.
5. **Phased complexity**. Turn features on in stages to preserve stationarity.

## 4. World Model

* **Tiles**: floor, wall, door, road, counter, table, queue nodes.
* **Objects**: bed, fridge, stove, shower, wardrobe, till, desk, shelf.
* **Weather**: sunny or rainy or cold. Affects warmth, path cost, and some prices.
* **Utilities**: power and water booleans with random faults.
* **Economy**: items have prices and stock. Daily restock truck. Simple wages. Daily rent.

**Affordances** are defined declaratively and hot-reload:

```yaml
- id: use_shower
  object_type: shower
  preconds: [ "occupied == false", "power_on == true" ]
  duration: 30
  effects: { hygiene: +0.45, energy: -0.03, money: -0.2 }
  hooks: { before: ["on_attempt_shower"], after: ["on_finish_shower"], fail: ["on_no_power"] }
```

## 5. Agent Model

### 5.1 Needs and State

* Needs vector in \[0, 1]: hunger, hygiene, energy, money normalised. Optional social later.
* Inventory: raw food, meal, clean clothes.
* Job status: has\_job, site, shift window.
* Memory: home location, known shops, last failures.

### 5.2 Personality (fixed at spawn, observed by policy)

* `extroversion` in \[−1, 1] affects desire to socialise and gain from chats.
* `forgiveness` in \[−1, 1] scales down negative social deltas and speeds rivalry decay.
* `ambition` in \[−1, 1] increases rivalry for work conflicts and punctuality pressure.
* `frugal` and `patience` are available if needed but not required for the first cut.

### 5.3 Relationships (sparse, multi-dimensional)

Per pair, capped top-K store per agent with hourly decay.

* `trust` influences help, lending, and compliance.
* `familiarity` influences chat ease and comfort.
* `rivalry` influences queuing conflicts and avoidance.
* Event-driven updates with small deltas. Clamp to \[−1, 1]. Drop faint ties.

Event table sketch:

| Event              | trust |  fam  |  riv |
| ------------------ | :---: | :---: | :--: |
| shared\_meal       |  +.10 |  +.25 |   0  |
| queued\_politely   |  +.05 |  +.05 | -.05 |
| blocked\_shower    |   0   |  -.05 | +.15 |
| took\_my\_shift    |  -.10 |   0   | +.30 |
| helped\_when\_late |  +.20 |  +.10 | -.10 |
| good\_chat(q)      | +.05q | +.10q |   0  |
| failed\_chat       |   0   |  -.05 | +.05 |

Personality hooks: forgiveness reduces negatives, ambition increases rivalry from work conflicts, extroversion adds a tiny bonus to familiarity for successful chats.

## 6. Observations

Per agent, per tick. Target 2 to 4k floats total.

* **Egocentric local map**: 9 by 9 to 12 by 12 tiles with channels for occupancy, object types, and simple path hints.
* **Self scalars**: needs, wallet, time of day sin and cos, has\_job, lateness flag.
* **Last action**: id, success flag, duration.
* **Personality**: 3 floats.
* **Social snippet**: top-2 friends and top-2 rivals as small id embeddings plus their \[trust, fam, riv] vectors, plus local summaries such as mean trust near, mean rivalry near, max rivalry near.

## 7. Action Space

### 7.1 Primitives

Move (N E S W), Interact(object, affordance), Wait, Talk(target), Buy(item), UseItem, Sleep, Equip.

### 7.2 Options

GetFed, GetClean, GoToWork, ShopGroceries, Sleep, Socialise(target optional), DailyRoutine later.

Meta-policy chooses an option. Option may call a short scripted controller for primitives in the PoC. Later we unfreeze primitives for end to end fine-tuning.

## 8. Rewards

* **Homeostatic tick loss**: `r_needs = −Σ w_i * deficit_i^2`.
* **Potential shaping** with φ(s) = −Σ w\_i \* deficit\_i to preserve optimality.
* **Work**: wages during work interval. Punctuality bonus in a small time window.
* **Survival**: small per tick bonus for not fainting or eviction. Penalties for eviction or collapse.
* **Social taps** (small and event only in Phase C): successful chat gives `+0.01 * (0.5*trust + 0.5*fam)`. Avoided conflict `+0.005`. Repeated nuisance with same target `−0.01`.
* Do not globally scale social reward by affinity at first. Keep it stable.

## 9. Learning Architecture

* **Framework**: PettingZoo ParallelEnv. PPO via RLlib or CleanRL.
* **Network**: small CNN on local map to 64 features, MLP on scalars, then LSTM 128. Two heads: meta-option and value. Primitive head later.
* **Population training**: 3 to 8 replicas with a light PBT jitter. Promote checkpoints that hit KPIs.
* **Phases**:

  * Phase A: train needs and jobs. Personalities present. Relationships off.
  * Phase B: enable relationships as observations only. No social rewards.
  * Phase C: enable tiny social reward taps. Reduce entropy a touch and lengthen evaluation.

## 10. Hooks, Console, and Admin

Global hooks receive `(tick, agent_id, event, context)` for:
`on_tick`, `on_spawn`, `on_need_threshold`, `on_affordance_before`, `on_affordance_after`, `on_affordance_fail`, `on_price_change`, `on_weather_change`, `on_power_cut`, `on_conflict`, `on_quit_job`.

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

## 11. Events and Narrative

* **Dramatic hooks** that cost time rather than changing reward structure.

  * Rage-quit job when stress exceeds a threshold. Cooldown before re-hire.
  * Public argument when high rivalry pair collide in a queue. Causes delay and narration.
  * Spiral day debuff after multiple failures. Clears after sleep.
* **Narration templates** for key states. Global and per agent throttling.

  * “Alice is late and Bob is blocking the shower. Rivalry 0.72.”
  * “First clash between Alice and Bob. They will remember this.”
  * “Carol and Dana bonded over lunch. Trust 0.41.”

## 12. UI and Telemetry

* **Viewer**: simple web client. Tiles and icons. Agent card shows needs, current option, top friends and rivals, and last event.
* **Relationship overlay**: toggle to draw green or red lines with thickness by magnitude.
* **Ticker**: narrative stream with click-to-focus.
* **Metrics**: attendance, starvation events, shower cadence, option switch rate, chat success vs trust, queue conflicts per day, diversity of lunch pairings.
* **Replays**: snapshot plus RNG seed for short deterministic replays.

## 13. Curriculum

1. **M0** Home sandbox only. Learn to maintain needs.
2. **M1** Add shop. Stipend. Buy and cook basics.
3. **M2** Add job. Remove stipend. Pay only at work. Add punctuality.
4. **M3** Enable relationships as observations only. Option biases include social cues.
5. **M3.5** Tiny social reward taps. Reduce entropy slightly.
6. **M4** Weather and utilities. Price shocks. Narration and relationship overlay.
7. **M5** Social option refined. Personality tweaks. Admin social commands.

## 14. Risks and Mitigations

* **Training instability** when relationships turn on. Use phased enable and KPI-gated promotion of checkpoints.
* **Boring optimal loops**. Conflicting needs, price shocks, and tiny curiosity bonus early mitigate this.
* **Cliques that starve needs**. Safety guard ignores rivalry when a need exceeds a hard threshold.
* **Narration spam**. Rate limit and dedupe templates.

## 15. Performance and Scale Notes

* Sparse ties with cap 12 per agent keeps memory to a few KB per agent.
* Event-driven updates plus hourly decay pass are cheap.
* With 8 envs by 8 agents and no render, expect several thousand steps per second on CPU.
* Future scale to 3D voxels and 50+ agents by mirroring server state into a renderer and keeping Python sim authoritative.

## 16. Minimal Data Sketches

### Agent

```json
{
  "id":"alice",
  "pos":[10,14],
  "needs":{"hunger":0.35,"hygiene":0.8,"energy":0.6,"money":25.0},
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

* Agents maintain needs and attend work within 1 to 2 in-sim days of training.
* Visible avoidance of rivals in queues by M3.5.
* Emergent small stories appear within 30 to 60 minutes of live runtime.
* Console hooks feel responsive and do not require retraining to show effects.

===================
