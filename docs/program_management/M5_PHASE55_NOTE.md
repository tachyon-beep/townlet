# Phase 5.5 Risk & Issue Log

## Close-Out Notes
- Promotion gates will be enforced via nightly scripted runs; dashboard panel is informational (watcher fails trigger HOLD/FAIL).
- Observer dashboard refresh remains manual; ops to capture screenshots post rehearsal (notification backlog logged for M6).
- BC manifests are pinned per promotion (`training.bc.manifest` and release checklist).

## Risks (Carry into Steering Review)
- **R1 (Low)**: Nightly anneal workflow may increase CI runtime; monitor first weekly run and adjust schedule if queue contention appears.
- **R2 (Medium)**: Ops adoption of new scripts may lag without training; mitigate via session and quick-reference guide.
- **R3 (Medium)**: Observer UI still CLI-based; stakeholder expectation of richer visuals before M6 could add scope.

## Actions
- A1: Present training plan and confirm scheduling with Ops/QA leads.
- A2: Prototype notification (Slack/email) once nightly workflow uploads artefacts.
- A3: Track UI usability feedback post-anneal panel rollout; feed into M6 backlog.

