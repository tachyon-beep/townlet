# Phase 5.5 Risk & Issue Log

## Open Questions
1. Should anneal promotion gates be enforced in real time (dashboard) or only via scripted audits?
2. What triggers observer UI to fetch updated telemetry when anneal rehearsals run headless (consider notifications or poll interval tuning)?
3. Do future BC datasets require version pinning per promotion (config override vs dynamic manifest)?

## Risks (Carry into Steering Review)
- **R1 (Low)**: Nightly anneal workflow may increase CI runtime; monitor first weekly run and adjust schedule if queue contention appears.
- **R2 (Medium)**: Ops adoption of new scripts may lag without training; mitigate via session and quick-reference guide.
- **R3 (Medium)**: Observer UI still CLI-based; stakeholder expectation of richer visuals before M6 could add scope.

## Actions
- A1: Present training plan and confirm scheduling with Ops/QA leads.
- A2: Prototype notification (Slack/email) once nightly workflow uploads artefacts.
- A3: Track UI usability feedback post-anneal panel rollout; feed into M6 backlog.

