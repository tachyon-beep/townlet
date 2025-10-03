# M4 Go / No-Go Prep (2025-09-30)

## Stakeholders
- Delivery lead
- RL/Training lead
- Ops/Telemetry lead
- DevEx/Observer UI representative

## Artefact Bundle
1. **Training Metrics**
   - `artifacts/phase4/queue_conflict_soak/ppo_soak.jsonl`
   - `artifacts/phase4/queue_conflict_soak/summary.md`
   - `tests/golden/ppo_social/baseline.json`
2. **Telemetry & Narration Evidence**
   - `tmp/phase4/...` soak watcher logs (queue conflict, employment punctuality, rivalry decay, kitchen breakfast, observation baseline)
   - `docs/telemetry/TELEMETRY_CHANGELOG.md` (schema 0.7.0 entry)
   - Observer dashboard screenshot/GIF (to capture narration panel once recorded)
3. **Ops Documentation**
   - `docs/ops/OPS_HANDBOOK.md` (narration controls, mixed-mode workflow)
   - `docs/ops/ROLLOUT_PPO_CHECKLIST.md`
4. **Test Evidence**
   - CI run showing new narration tests (link post-merge)
   - Local pytest logs: `tests/test_telemetry_narration.py`, `tests/test_observer_ui_dashboard.py`, `tests/test_telemetry_client.py`

## Agenda
1. Review milestone scope vs achievements (relationship systems, social observations, rewards, narration).
2. Walk through artefacts (training drift, telemetry/narration, ops docs).
3. Identify outstanding risks (CI runtime, stakeholder follow-ups, BC prep).
4. Record decision and next steps (M5 readiness tasks).

## Action Items Before Meeting
- Capture dashboard screenshot with active narration example.
- Trigger CI dry-run after narration tests merge to collect runtime metrics.
- Circulate artefact bundle to stakeholders 24h before review.
