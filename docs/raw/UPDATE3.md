# Lifecycle & Turnover (PoC spec)

## Goals

* In-character consequences for chronic failure (starvation, eviction, etc.).
* Continuous population size (e.g., hold at 8 agents).
* Minimal training instability: deaths act like tidy per-agent episode boundaries.
* Optional light “evolution” by seeding newcomers from successful policies.

---

## 1) IC death & exit conditions (any one can trigger)

Each is checked on a rolling window so it’s not one bad minute.

**Hard failures (instant):**

* **Collapse from hunger:** `hunger > 0.97` for `>= 30` consecutive ticks.
* **Exposure collapse (optional):** `warmth < 0.05` for `>= 30` ticks during cold weather with no shelter.

**Soft failures (cumulated):**

* **Eviction:** rent unpaid for `≥ 2` consecutive days → agent is evicted. If they fail to recover `money > rent*0.5` within the next day, they leave town.
* **Chronic unemployment:** wages earned `== 0` for `≥ 2` days while having a job available (not a systemic outage).
* **Chronic neglect:** any need `> 0.9` for `≥ 25%` of ticks over a 24-hour window.
* **Age-out (optional spice):** random lifespan 10–20 in-sim days to keep turnover even if all are competent (off by default for PoC).

**Guardrail:** if a city-wide event (blackout, water outage) is active, suppress exits caused by facilities for the duration + grace period.

**On death/exit:**

* Emit **narration** + small **global delay** (ambulance/transport).
* Apply a **terminal penalty** to that agent’s return (e.g., −1.0) so there’s never an incentive to “reset” by dying.
* Mark per-agent `terminated=True` in the env step (PettingZoo `terminations[agent_id]=True`), **others continue**.

---

## 2) Replacement (arrival)

When an agent exits, spawn a newcomer within 5–20 ticks so the town feels alive.

**Spawn details:**

* **Entry point:** roadside tile near “bus stop / car park”.
* **SFX:** short car arrival “vroom + door thunk” (client-side only).
* **Starter kit:** `money = rent*1.5`, `food_raw=1`, `clothes_clean=1`.
* **Job state:** 50% chance pre-assigned entry-level job for faster integration; else they must apply.
* **Personality:** sample new `extroversion/forgiveness/ambition` from a fixed prior (keep diversity).
* **Social memory:** empty (no inherited grudges).

**Policy initialisation (choose one):**

* **Simple (default):** same current release policy weights as others.
* **Elitist warm-start (flag):** copy from the **best-performing** policy replica (PBT-style) with tiny Gaussian jitter (σ=0.01) to encourage exploration. Never copy from a just-failed agent.

**Stability caps:**

* Max **2 exits** per in-sim day.
* Cooldown **120 ticks** between exits.

---

## 3) Fitness & culling transparency (IC + OOC)

Track an **Agent Fitness Index (AFI)** (rolling 24h):

```python
AFI =  wR * normalised_return
     + wN * (1 - mean_need_deficit)
     + wJ * attendance_rate
     - wV * violations (queue grief, fines)
```

Use AFI only for **analytics and optional elitist warm-starts**; **never** for direct rewards. Avoid perverse incentives.

**Narration cues:**

* “{A} couldn’t keep up with rent and left town.”
* “{A} collapsed from exhaustion. Paramedics took them away.”
* Arrival: “A car pulls up. {A} steps out, new to town.”

---

## 4) Training considerations (so this doesn’t wreck PPO)

* Treat each death as **per-agent episode end**; other agents keep rolling (multi-agent environments support per-agent terminations).
* **Don’t** weigh dead-agent transitions more highly; if anything, **down-weight** their last 100 ticks in the learner to reduce overfitting to doom spirals.
* Keep **terminal penalty small** (−1.0) vs. day-scale returns to avoid shock.
* **Cap daily exits** and enforce **cooldowns** to limit non-stationarity.
* If replacements use elitist warm-starts, **don’t** mutate the release policy; mutate only the spawn’s private copy (or the target replica in PBT, not the global release).

---

## 5) Hooks, console & config

**New hooks:**

* `on_agent_exit(agent_id, reason)`
* `on_agent_spawn(agent_id)`
* `on_agent_near_death(agent_id, need)`  (for tense narration)

**Console:**

```markdown
kill <name> reason=<text>          # IC removal for testing (logs reason)
toggle_mortality on|off
set_exit_cap <per_day>
set_spawn_delay <min> <max>
set_death_threshold <need> <value> <ticks>
```

**Config (yaml):**

```yaml
lifecycle:
  enabled: true
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

---

## 6) UI bits (cheap and cheerful)

* **Arrival vignette:** camera pans to roadside; “New arrival: {A}”.
* **Exit vignette:** ambulance or moving van icon; reason tooltip.
* **Cemetery / ledger (optional):** small panel listing the last 5 exits with reasons and lived days.

---

## 7) Edge-case rules (to avoid weird incentives)

* **No reward on death** (ever). Terminal penalty only.
* **Debt reset?** Keep money floors at `0` on spawn; **do not** carry over debts or rent arrears across identities.
* **Self-harm exploit:** since death is strictly penalised and exits capped, there’s no positive loop in dying to “reroll”.
* **City-wide disasters:** pausing exits avoids mass wipe-outs that would destabilise learning.

---

## 8) Test cards

* **Starvation path:** block shop access; expect collapse → exit → spawn in under 20 ticks; others unaffected.
* **Eviction path:** set price spike + wage cut; watch one eviction; ensure grace window works.
* **Exit-storm guard:** script three failures in quick succession; confirm cooldown enforces ≤2 exits/day.
* **Elitist spawn:** enable elitist seeding; verify new agent competence > baseline without policy drift.

---

**Confidence (WEP):**

* Training stability with per-agent terminations and capped exits: **High (\~85%)**.
* Watchability uplift from arrivals/departures & narration: **Moderately High (\~75%)**.
* No perverse incentives introduced (given terminal penalty and caps): **High (\~80%)**.

If you’re happy, I’ll slot this as Section 18 “Lifecycle & Turnover” in the conceptual doc and then include the YAML + hooks in the requirements draft.
