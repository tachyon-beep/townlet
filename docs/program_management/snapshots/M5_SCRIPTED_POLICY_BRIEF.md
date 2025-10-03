# M5 Scripted Policy Review Brief (2025-09-30)

## Objective
Prepare behaviour scripts for BC trajectory capture. This brief consolidates the scenarios and target behaviours to review with the RL lead before bulk captures.

## Target Scenarios & Behaviours
1. **queue_conflict_bc (Kitchen Shower Queue)**
   - Behaviour: deterministic queue etiquette (request -> wait -> exit), explicit conflict resolution branch.
   - Metrics: queue wait time distribution, conflict intensity coverage.
2. **employment_punctuality_bc**
   - Behaviour: commute routine with scripted lateness/recovery cases.
   - Metrics: on-time ratio >= 80%, lateness events for training negative examples.
3. **rivalry_decay_bc**
   - Behaviour: alternating cooperative vs antagonistic interactions to hit rivalry decay thresholds.
   - Metrics: rivalry max/decay curves covering [0.1, 0.7].
4. **meal_prep_social_bc**
   - Behaviour: shared meal routine + conversation triggers to capture positive social deltas.
   - Metrics: chat success rate, shared meal count, trust/familiarity deltas.

## Open Questions (to resolve with RL lead)
- Required action space coverage (do we need exploration noise?).
- Balance between expert vs stochastic trajectories.
- Dataset size per scenario (initial target 500 trajectories each?).
- Additional metadata tags needed for filtering (difficulty, outcome labels).

## Preparation Checklist
- [ ] Produce prototype scripts (sketch stub behaviour functions).
- [ ] Define success metrics per scenario (see metrics above).
- [ ] Align on dataset versioning (naming, checksums).
- [ ] Schedule walkthrough (tentatively 2025-10-01 midday).

## Notes
- Synthetic trajectory round-trip validated (`tests/test_bc_capture_prototype.py`).
- Capture CLI/API pending Phase 5.1 development.
