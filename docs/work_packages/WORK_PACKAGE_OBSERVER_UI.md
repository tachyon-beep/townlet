## Risks
| ID | Risk | Mitigation | Decision Needed |
| --- | --- | --- | --- |
| UI-1 | CLI UI not adequate for demo audiences | Provide screen capture/gif; gather demo feedback; schedule follow-up web UI if required | Decide post-MVP usability review |
| UI-2 | Observation map rendering unclear without world geometry | Add legends/tooltips; plan upgrade once `WorldState` exposes object coordinates | Prioritise geometry work vs accept placeholder |
| UI-3 | Console command latency (approve/defer) blocks UI loop | Run console calls asynchronously; display status indicator | Choose threading vs async approach before implementing controls |
| UI-4 | Schema bump before UI ships | Schema guard warns; UI instructions advise upgrade; client stays aligned with changelog | Define support policy (e.g., UI supports latest released schema only) |
| UI-5 | UI dependencies inflate footprint | Use Rich/Textual only, optional extras behind flag | Confirm dependency policy with DevEx |

### Risk Reduction Activities
1. **Usability Dry Run** — capture dashboard output (gif/video), collect stakeholder feedback, and log sign-off.
2. **Performance Probe** — measure dashboard refresh overhead (target <50 ms per tick).
3. **Concurrency Spike** — prototype background console command handling (read-only now but future-proof).
4. **Schema Mock** — simulate schema `0.3.x` payload (already in tests) to verify warning path; document upgrade steps.

### 6. Optional Web Front-End (Stretch)
- Revisit after conflict intro milestone; reuse `townlet_ui.telemetry` client.
- Prototype FastAPI + minimal front-end if demo feedback demands richer visuals.
### Follow-Up Actions
1. Add map legend/highlights (colour cues for backlog, ASCII legend explaining characters).
2. Implement logging for console executor failures to aid ops debugging.
3. Cache or batch observation tensors in dashboard to avoid redundant builder calls.
4. Confirm demo sign-off post-usability review; escalate to web prototype only if required.

### UX Enhancements Backlog
| Task | Description | Risk Reduction | Notes |
| --- | --- | --- | --- |
| UX-1 | Status badge in Employment header (e.g., red "BACKLOG") when pending exits >0 | Feature flag via config or environment to disable; treat as pure view change | No schema change; ensure tests cover "no backlog" vs backlog |
| UX-2 | Sort agent table by shift state / attendance ratio with indicator | Provide fallback to original order if data missing; add test fixture | Sorting uses existing data fields; low risk |
| UX-3 | Display tick timestamp/refresh metadata in header | None (read-only info); log once per refresh | Reuses `loop.tick` and `time.time()`; no schema impact |
| UX-4 | Expand legend (map symbols, color cues) and highlight text | Pure presentation change | Already requested in feedback |
| UX-5 | Optional coordinate labels around ASCII map | Guard with config option; disable if geometry missing | Prepping for future geometry; doesn't alter tensor |

Risk reduction: implement each behind minimal toggles, add snapshot tests, update guide with new cues, and gather feedback after rollout.

