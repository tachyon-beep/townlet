# Townlet — Conceptual Design v1.2 Addendum

## 1) Reward tuning and experimentation framework

Make reward weights first-class config with an experiment harness so we can iterate fast and avoid weird loops.

### Config

```yaml
rewards:
  needs_weights: { hunger: 1.0, hygiene: 0.6, energy: 0.8, money: 0.5 }
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

### Harness

* One agent micro-suite for A/B weights before multi-agent
* Grid search or PBT light on the reward keys above
* Automatic metric logging per run: time to self sufficiency, lateness rate, starvation incidents, work attendance, option thrash

Pseudocode sketch

```python
def run_experiment(cfg, seed):
    env = Townlet(cfg, seed)
    trainer = PPO(cfg.ppo)
    metrics = []
    for epoch in range(cfg.epochs):
        trainer.learn(n_steps=cfg.steps_per_epoch)
        m = eval_suite(trainer.policy, env, cfg.eval_episodes)
        metrics.append(m)
        if stability_guard.tripped(m): break
    return metrics
```

### Guardrails

* Hard floor overrides so agents ignore social biases when any need deficit exceeds 0.85
* Cap punctuality bonus to be less than the hunger pain accrued from skipping one meal

WEP: High that this avoids runaway behaviours, about 85 percent.

## 2) Engineered emergence so it never gets dull

DRL will optimise the fun out of things if we let it. Add a small event scheduler that throws spanners without changing rewards.

### Perturbation scheduler

* Low frequency randomised events with bounds so they are legible and fair

  * Price spikes once per day window
  * Blackout or water outage with short duration
  * Queue bottleneck by temporarily closing a shower or till
  * System arranged meet between rivals at the cafe

```yaml
perturbations:
  price_spike: { prob_per_day: 0.3, magnitude: [1.2, 1.8], duration_min: 60 }
  blackout:    { prob_per_day: 0.15, duration_min: [20, 60] }
  outage:      { prob_per_day: 0.10, duration_min: [20, 60] }
  arranged_meet: { prob_per_day: 0.25, target: "top_rivals", location: "cafe" }
```

These are event layer only. No fresh reward taps needed. Narration makes them visible.

WEP: High that this keeps stories bubbling, about 75 percent for watchability uplift.

## 3) Scripted to learned primitives handoff

We do not yank the rug. We clone the behaviour first, then fine tune.

### Handoff protocol

1. Phase A and B use scripted controllers under options
2. Record script trajectories for key options GetFed, GetClean, ShopGroceries, GoToWork
3. Train a primitive policy head with behaviour cloning on those trajectories until imitation loss crosses a target
4. Switch options to call the learned primitives with mixed control

   * Start with 80 percent scripted, 20 percent learned per primitive call
   * Anneal to 0 scripted over N epochs
5. Allow PPO to fine tune end to end after BC warm start

BC objective

```python
L_bc = CE(a_script, a_pred) + λ * MSE(v_script, v_pred)  # optional value distillation
```

Safety

* If performance drops more than 30 percent against baseline KPIs during anneal, freeze at current mix and retry later with more BC data

WEP: High that this keeps the meta policy stable during the switch, around 80 percent.

## 4) Observation compression options

We keep the rich egocentric map for the baseline, but provide smaller ablations so you can test speed vs competence.

### Variants

A. Full map 9 by 9 by C plus scalars and social snippet. Current default.

B. Hybrid compact

* Replace the full affordance channel with three directional fields to nearest relevant objects

  * Vector to nearest shower, fridge, till, home, work
  * 2D unit vector per target + distance scalar
* Keep occupancy and agent positions in a thinner map

C. Ultra-compact

* No map
* Distilled vectors only

  * Distances and bearing to targets
  * Boolean flags like rival\_in\_current\_queue
  * Top K social tuples
  * Pathfinding hint as 4 logits for NSEW from a shallow planner

Switchable in config

```yaml
observations:
  variant: "hybrid"   # full | hybrid | compact
  local_window: 9
  id_embed_dim: 8
```

Plan

* Start full for clarity
* If training throughput is poor, test hybrid
* Keep compact reserved for mobile or very large populations

WEP: Moderate that compact keeps competency without extra shaping, about 60 percent. Hybrid is safer, about 80 percent.

## 5) Curriculum and phases updated

* Insert M2.5 Basic Conflict intro as we already did
* Split Phase C as C1 chat reward only, C2 avoidance bonus, C3 relationship quality modifiers
* Add BC warm start step before unfreezing primitives

Revised slice

1. M2 job loop stable
2. M2.5 queue friction penalties only
3. M3 relationships in observations only
4. C1 chat reward
5. C2 avoidance reward
6. BC train primitives on recorded scripts
7. Anneal scripted to learned primitives
8. C3 small relationship quality modifiers
9. M4 perturbation scheduler on, narration and overlay

## 6) Stability monitor and rollback policy

We keep the simple rolling window test and add a few canaries.

Canaries

* Late arrivals rate spike above 2 times baseline
* Starvation incidents per agent per day exceeds threshold
* Option switch rate spikes more than 25 percent for two evaluation windows

Rollback

* Pin current release policy
* Continue training in shadow
* Promote only after two consecutive evaluation wins

## 7) Console safety checks

Add minimal validation to all admin commands so we cannot soft lock an agent or corrupt state. Examples we will enforce

* Possess only non sleeping agents
* No teleport into blocked tiles
* set\_rel only for valid ids and dim names trust, fam, riv
* force\_chat denies if target already in a blocking affordance

## 8) KPIs refined

Add Gemini’s useful ones on top of ours

* Self sufficiency percent with all needs above 0.3 for 24 hours
* Job tenure mean greater than 3 days
* Relationship formation percent above 60 with ties stronger than 0.3
* Conflict resolution under 20 percent repeating avoidance with the same pair
* Throughput target steps per second per env shard for each observation variant

## 9) Doc pointers for the next phase

When we turn this into requirements and a high level design, pull out these sections as explicit requirements

* Reward config keys and guardrails
* Perturbation scheduler spec and frequencies
* BC data recording and loss targets
* Observation variant interface and switch
* Stability gates and rollback rules
* Console validation rules and error texts

That gives us a clean testable spec and keeps the build honest.
