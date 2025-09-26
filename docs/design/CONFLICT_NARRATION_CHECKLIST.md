# Conflict Narration Throttling & UX Sign-Off Checklist

## Throttling Strategy
- **Rate limiter**: Emit at most one `conflict_detected` narration per 30 simulation ticks (≈30 seconds) per queue. Additional events are buffered and summarised at the cooldown expiry.
- **Severity tiering**: Allow immediate narration bypass when a queue ghost-step fires or a rivalry score crosses the avoidance threshold; these are high-signal events.
- **Aggregation**: Merge repeated low-severity conflicts into a single summary message (e.g., "Cafe queue experienced 3 minor shuffles in the last 5 minutes").
- **Global cap**: Limit total conflict narrations to 10 per in-sim hour to avoid log spam during large regressions.
- **Instrumentation hooks**: Emit throttling counters to telemetry (`conflict.throttled_events`, `conflict.published_events`) so UI and stability monitors can verify behaviour.

## UX Review Checklist (Pre-Enablement)
1. **Scenario Coverage** — Run scripted scenarios for: single queue ghost-step, simultaneous queues, and rivalry escalation to ensure narration copy matches context.
2. **Copy Review** — Confirm message templates are concise, reference object names, and avoid jargon. Validate colour/badge choices in the dashboard remain legible in both light/dark terminals.
3. **Throttling Verification** — Capture telemetry snapshot showing throttled vs published counts and attach to review notes. Ensure counters reset predictably across tick windows.
4. **UI Demonstration** — Record a short dashboard capture (GIF/video) highlighting at least one conflict narration and the associated conflict panel metrics.
5. **Accessibility Pass** — Check narration text with screen-reader (Rich console export) and ensure badge colours meet contrast requirements.
6. **Sign-Off Log** — Document reviewer names, date, and decisions in `docs/engineering/IMPLEMENTATION_NOTES.md` under the Conflict Intro section, noting any follow-up tasks.

Use this checklist before flipping the conflict events feature flag to `on` in default configs.
