# Townlet — Conceptual Design v1.1 (with Deepseek refinements)

## 0. What changed (quick)

* **Obs size sanity-checked** (\~500–800 floats; plenty of headroom).
* **Relationship cap**: Top-K = **6** ties per agent (3 “friend”, 3 “rival”), sparse, decaying.
* **Curriculum tweak**: Insert **M2.5 Basic Conflict** (queue friction without memory). Split Phase C into **C1/C2/C3** for social rewards.
* **Safety**: Console command validation; narrative rate limiting; stability monitor + rollback gate.
* **KPIs**: Added self-sufficiency / tenure / relationship formation / conflict resolution metrics.

---

## 1. Vision (unchanged)

Always-on tiny town; DRL agents learn to live; you meddle live; watch emergent drama.

## 2. PoC Scope (unchanged core)

* **World**: 48×48 2D grid; homes, grocer, café, office, park, gym (shower).
* **Agents**: 6–10 citizens; shopkeepers initially scripted.
* **Needs**: hunger, hygiene, energy, money. (Social later in Phase C).
* **Learning**: PPO at option level; primitives scripted first; unfreeze later.
* **Run mode**: headless shards + lightweight viewer.

## 3. Core Principles (unchanged)

Simple affordances; hierarchical control; hot hooks; sparse social memory; phased rollout.

---

## 4. World Model (as before)

Tiles, objects, weather, utilities, simple economy. Affordances in hot-reload YAML.

---

## 5. Agent Model

### 5.1 Needs & State

As before (needs vector, inventory, job/shift, memory).

### 5.2 Personality (kept minimal)

* `extroversion` \[−1,1] → social pull and chat gains
* `forgiveness` \[−1,1] → scales down negative social deltas & rivalry decay
* `ambition` \[−1,1] → bumps rivalry from work conflicts; higher punctuality pressure
  (Reserve `frugal`, `patience` behind a flag if we need them.)

### 5.3 Relationships (multi-dim, sparse, capped)

**Store:** per agent, **Top-K=6** ties with decay toward 0; drop faint/old ties.

Dims per tie:

* `trust`   (help/lend/compliance)
* `familiarity` (chat ease, comfort)
* `rivalry` (queue conflict/avoidance)

**Update policy (event-driven, additive, clamped):**

| Event                | Δtrust |  Δfam | Δriv |
| -------------------- | :----: | :---: | :--: |
| shared\_meal         |  +.10  |  +.25 |   0  |
| queued\_politely     |  +.05  |  +.05 | −.05 |
| blocked\_shower      |    0   |  −.05 | +.15 |
| took\_my\_shift      |  −.10  |   0   | +.30 |
| helped\_when\_late   |  +.20  |  +.10 | −.10 |
| good\_chat(q∈\[0,1]) |  +.05q | +.10q |   0  |
| failed\_chat         |    0   |  −.05 | +.05 |

**Personality hooks:**
`forgiveness` scales negatives (down to \~50% at high end); `ambition` scales rivalry on work conflicts (+30% bias); `extroversion` adds +0.02 to familiarity on successful chats.

**Admission rule (cap-aware):**

```python
def update_relationship(self, other_id, d):
    if other_id in self.ties:
        apply_deltas(other_id, d)
    elif len(self.ties) < 6 or abs(d['trust']+d['fam']-d['riv']) > 0.2:
        add_relationship(other_id, d)  # evict weakest if full
```

---

## 6. Observation Space (sized & tidy)

* **Local map**: 9×9×C (occupancy, object types, affordances, path hint) ≈ 324–432 floats.
* **Self scalars**: \~15 (needs, wallet, time sin/cos, job flags, last action).
* **Personality**: 3 floats.
* **Social snippet**: top-2 friends + top-2 rivals → each (id-embed 8 + trust/fam/riv 3) = 11; total 44.
* **LSTM hidden**: handled internally by the net; not in obs tensor.

Target: **\~500–800 floats** per agent. Plenty of slack.

---

## 7. Action Space

**Primitives**: Move NSEW, Interact(object, affordance), Wait, Talk(target), Buy(item), UseItem, Sleep, Equip.
**Options**: GetFed, GetClean, GoToWork, ShopGroceries, Sleep, Socialise(target optional).
Meta-policy picks option; option calls short scripted controller initially.

**Social success gate (cheap):**

```python
p_success = 0.7
           * (1 + 0.3*clip(trust_ij, -1,1))
           * (1 + 0.2*clip(fam_ij, -1,1))
           * topic_pref_j
```

---

## 8. Rewards (event-based socials; no tick leaks)

* **Homeostasis**: `−Σ w_i * deficit_i²` per tick.
* **Shaping**: potential φ(s)=−Σ w\_i \* deficit\_i.
* **Work**: wages while working; punctuality bonus in window.
* **Survival**: small life tick; penalties for faint/evict.

**Phase C (split):**

* **C1**: reward only **successful conversation** completion: `+0.01 + 0.3*trust + 0.2*fam` (scaled small).
* **C2**: add **conflict avoidance** micro-bonus `+0.005`.
* **C3**: allow small **relationship-quality modifiers** on C1 reward.
  No global scaling of “social need” by affinity in PoC.

---

## 9. Policy Architecture & Training

* **Env**: PettingZoo ParallelEnv.
* **Algo**: PPO (CleanRL or RLlib).
* **Net**: tiny CNN(9×9)→64, MLP on scalars, concat → LSTM(128), heads: meta-option & value. Primitive head later.
* **Pop training**: 3–8 replicas, light PBT jitter, gated promotion.
* **Stability Monitor**: rollback guard on sharp regressions:

```python
if mean_last_50 < 0.7 * mean_prev_50: hold/pin current release
```

**Phases:**
A — needs/jobs only (personalities present; relationships off)
B — relationships **in obs only**, no social reward
C — C1→C2→C3 social rewards (tiny), entropy ↓ a touch, longer eval windows

---

## 10. Hooks, Console & Safety

Hooks unchanged plus `on_conflict`, `on_quit_job`.

**Console (validation examples):**

```python
def possess_agent(aid):
    if aid not in live: return "Error: not found"
    if aid in possessed: return "Error: already possessed"
    if agents[aid].state == "sleep": return "Error: sleeping"
    possessed.add(aid); return "OK"
```

Commands: spawn, teleport, price, blackout, rain, possess, setneed, **set\_rel a b trust|fam|riv v**, **force\_chat a b q=0.8**, arrange\_meet.

---

## 11. Events & Narrative (with throttle)

* **Dramatic hooks**: rage-quit job (cooldown), public argument (delay only), spiral day debuff until sleep.
* **Narration templates** (no model) with **rate limits** (global \~2/s; per-agent cooldown \~15s):

```python
if throttle.can_narrate("late_blocked", agent_id):
    emit("{A} is late and {B} is camping the shower. Rivalry {riv:.2f}.")
```

---

## 12. UI & Telemetry

Viewer: tiles, agent cards, **relationship overlay** (green/red edges, thickness=|strength|), narrative ticker.
Telemetry: attendance, starvation, shower cadence, option-switch rate, chat success vs trust, queue conflicts/day, lunch-pairing diversity.

**Quantitative KPIs (added):**

* **Self-sufficiency**: % agents with all needs > 0.3 for 24h.
* **Job stability**: mean tenure > 3 days.
* **Relationship formation**: ≥60% agents have at least one tie with |value|>0.3.
* **Conflict resolution**: <20% conflicts escalate to repeated avoidance.

---

## 13. Curriculum (refined)

1. **M0** Home sandbox; maintain needs.
2. **M1** Add shop; stipend; buy/cook.
3. **M2** Add job; remove stipend; punctuality.
4. **M2.5** **Basic Conflict Intro**: queue friction/penalties **without** relationships.
5. **M3** Relationships ON as **observations only**; option biases include social context.
6. **M3.5** Split Phase C:

   * **C1** chat reward only
   * **C2** add conflict-avoidance bonus
   * **C3** add relationship-quality modifiers
7. **M4** Weather/utilities, price shocks, narration + overlay.
8. **M5** Personality polish, admin social commands, evaluation gating.

---

## 14. Performance & Scale (unchanged)

Sparse ties (<1 KB/agent), event-driven updates + hourly decay, several k steps/s CPU-only typical; later mirror to 3D voxels with Python server as authority.

---

## 15. Success Criteria (recap)

* Needs & work routines within \~1–2 in-sim days of training.
* Rivalry-aware avoidance visible by M3.5.
* Short emergent stories within 30–60 min runtime.
* Console hooks feel immediate; no retrain required to see effects.
