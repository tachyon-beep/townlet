# Demo Story Arc Narrative Plan

**Objective:** showcase a three-beat narrative (arrival → disruption → recovery) that
highlights Townlet's employment, relationship, and perturbation telemetry during live
demos.

## Characters & Roles
- **Avery (demo_host):** resident anchor who introduces the town and keeps morale high.
- **Blair (newcomer):** arrives mid-demo, seeking work at the cafe; used to illustrate job
  onboarding and late-arrival handling.
- **Kai (shopkeeper):** existing agent whose stall experiences the perturbation and
  demonstrates recovery behaviour.
- **Spectator Hooks:** Narrations should call out Avery welcoming Blair, the supply shock,
  and the resolution when jobs stabilize.

## Beat Structure & Tick Budget
| Stage | Ticks | Description | Key Telemetry |
| --- | --- | --- | --- |
| Warm-up | 0–40 | Avery + Kai already working; queue stable, relationships warm. | Employment panel green, narrations celebrating friendships. |
| Disruption | 40–90 | Blair arrives; price spike perturbation triggers; queue stress builds. | Perturbation telemetry, narration for price spike + queue conflicts. |
| Recovery | 90–150 | Operators trigger relief command, relationships normalize, wages credited. | Narrations for recovery, employment KPIs cooling, wallet increases. |

> Keep total runtime ≤ 150 ticks to fit within conference demo slots. Tests will enforce
a max tick budget of 180 to ensure guard rails.

## Deterministic Seeds
| Component | Seed | Notes |
| --- | --- | --- |
| Scenario config (`demo_story_arc.yaml`) | 4242 | Drives SimulationConfig.seed for world RNG. |
| Perturbation trigger macro | 991 | Reserved for optional CLI plan files; timeline uses deterministic payloads. |
| Timeline builder | 73 | For future use if randomized offsets are introduced (currently static). |

Store these seeds in both the scenario config metadata and the timeline files to prevent
drift.

## KPI Targets
- **Employment:** highlight pending_count spikes during disruption and show wages emitted
  after recovery.
- **Relationships:** target at least one friendship narration and one rivalry warning.
- **Narrations:** ensure `relationship_friendship`, `conflict`, and
  `perturbation_price_spike` categories appear.

## Operator Checklist (Preview)
1. Launch demo via `python scripts/demo_run.py configs/scenarios/demo_story_arc.yaml --ticks 150`.
2. At tick ≈40 confirm Blair's arrival narration.
3. At tick ≈60 watch for price spike narration and queue stress.
4. Around tick 110 confirm the scripted `arrange_meet` console command fires to ease tension.
5. Verify final narration congratulates the town and wallets increase.

This document stays as the single source of truth; any adjustments to the arc must update
seeds, tick ranges, and KPI expectations here and in the forward work program.
