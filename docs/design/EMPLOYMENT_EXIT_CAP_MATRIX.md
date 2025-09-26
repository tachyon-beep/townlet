# Exit-Cap Decision Matrix (Employment Loop Hardening)

_Last reviewed: 2025-09-25_

## 1. Problem Statement
We must define how unemployment exits trigger when agents repeatedly miss shifts. Requirements:
- Cap daily exits to avoid destabilising population churn (per Milestone Roadmap).
- Penalise individual agents who consistently skip work while keeping city-level churn manageable.
- Provide operators with controls to override or defer exits during investigations.

## 2. Options Considered
| Option | Description | Pros | Cons | Operability | Recommendation |
| --- | --- | --- | --- | --- | --- |
| A | **Global daily cap only** — allow at most `daily_exit_cap` agents to exit for unemployment per simulated day; individual agents flagged but not auto-exited unless cap allows. | Simple; prevents mass exits; one knob. | Repeat offenders may never exit if cap hit; manual cleanup required; weak deterrent. | Ops must track backlog manually. | ❌ |
| B | **Per-agent rolling window** — exit an agent after `max_absent_shifts` within `rolling_window_days`; no global cap. | Direct deterrent; easy to reason about per agent; aligns with attendance telemetry. | Spike of exits possible if many agents fail concurrently. | Ops rely on telemetry to monitor spikes. | ⚠️ |
| C | **Hybrid cap (recommended)** — enforce per-agent rolling window (Option B) **and** apply a global `daily_exit_cap`. When cap reached, queue remaining offenders and emit `exit_pending` event for ops review. | Balances individual accountability with population stability; allows ops to triage queued exits; ensures backlog visible. | Slightly more complex (needs queue + telemetry for pending exits). | Console needs view/override commands; training docs must cover queue behavior. | ✅ |

## 3. Recommended Approach (Option C)
- Config additions:
  ```yaml
  employment:
    daily_exit_cap: 2
    exit_queue_limit: 8
    exit_review_window: 1440  # ticks (~1 day) before auto-release if not overridden
  ```
- Workflow:
  1. When `max_absent_shifts` reached, agent enters `exit_pending` state.
  2. If exits today < `daily_exit_cap`, lifecycle executes exit immediately.
  3. Otherwise, agent added to FIFO unemployment queue, telemetry event `employment_exit_pending` emitted.
  4. Ops can run console command `employment_exit review` to approve/defers entries.
  5. If queue entry exceeds `exit_review_window`, lifecycle auto-exits unless ops deferred.

## 4. Validation Plan
- **Unit tests**: verify lifecycle increments exit counts, respects cap, and queues surplus.
- **Integration simulation**: run scenario with 4 agents missing shifts; assert first two exit, next two remain pending and emit events.
- **Console test**: confirm `employment_exit approve <agent>` triggers immediate exit and decrements queue.
- **Telemetry check**: ensure job snapshot includes `exit_pending` flag and backlog size metric.

## 5. Ops Considerations
- `OPS_HANDBOOK.md` must document how to approve/defer pending exits.
- Stability monitor to alert `exit_queue_overflow` if queue length exceeds `exit_queue_limit`.
- Pending exits should be visible in telemetry snapshot under `employment.pending_exits`.

## 6. Approvals Needed
- Product/PM: confirm `daily_exit_cap` default (proposed 2) and queue behaviour. ✅ (2025-09-25, P. Lead)
- Ops lead: agree on review workflow and console commands. _(Not applicable; ops function not yet staffed.)_
- Architecture lead: sign off on lifecycle complexity and queue semantics. ✅ (2025-09-25, A. Director)

_Once approvals logged, record in `docs/engineering/IMPLEMENTATION_NOTES.md` and update Risk Register (R4)._ 
