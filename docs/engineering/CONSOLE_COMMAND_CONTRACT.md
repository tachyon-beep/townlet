# Console Command Contract — v2025-10-07

This note captures the authoritative schema for console commands, response payloads,
and the current vs. planned command catalog. It consolidates the architecture snapshot
(`docs/program_management/snapshots/ARCHITECTURE_INTERFACES.md`) with the live handler
surface in `src/townlet/console/handlers.py` so future implementation work can align with
ops expectations.

## 1. Command Envelope

Commands enter the simulation by being queued on `TelemetryPublisher.queue_console_command`
and drained each tick via `WorldState.apply_console`. Every enqueued entry MUST conform
to the following envelope (all fields snake_case, JSON serialisable):

| Field | Type | Notes |
| --- | --- | --- |
| `name` | `str` | Registered command identifier (see catalog). Case-sensitive. |
| `args` | `list` | Positional arguments; default `[]`. Values must already be parsed to native types. |
| `kwargs` | `dict` | Keyword arguments; default `{}`. Keys must be strings. |
| `cmd_id` | `str` | Optional idempotency token. Required for destructive/admin ops; router must reject duplicates. |
| `issuer` | `str` | Optional actor identifier (user/service). Propagated to audit log and response metadata. |
| `mode` | `"viewer"` \| `"admin"` | Authorisation tier. Defaults to `"viewer"`; admin commands MUST validate this. |
| `auth` | `dict` | Optional `{"token": str}` payload. Required when `console_auth.enabled` is true. Tokens are stripped server-side after verification. |
| `timestamp` | `int` | Optional Unix epoch (ms). Used only for audit trail; server clock is authoritative. |
| `metadata` | `dict` | Optional opaque client metadata (e.g., UI correlation ids). Stored with audit record only. |

Versioning: the envelope itself is implicitly v1.0. Future additions must be optional
and backward-compatible; breaking changes require bumping the queue/topic name.

## 2. Response Envelope

Command handlers return structured responses that the console transport will forward
back to clients and append to the audit journal.

```json
{
  "cmd_id": "7b8e...",
  "name": "spawn",
  "status": "ok",
  "result": {...},
  "issuer": "ops@example.com",
  "tick": 1234,
  "latency_ms": 12
}
```

| Field | Type | Notes |
| --- | --- | --- |
| `cmd_id` | `str | null` | Mirrors request id; null when omitted. |
| `name` | `str` | Echo of the command name. |
| `status` | `"ok"` \| `"error"` | Success indicator. |
| `result` | `dict` | Command-specific payload for success. Required when `status == "ok"`. |
| `error` | `dict` | Present when `status == "error"`; see below. |
| `issuer` | `str | null` | Echo of request issuer. |
| `tick` | `int` | Simulation tick at execution time. |
| `latency_ms` | `int` | Optional runtime measurement from queue to completion. |

Error payload schema:

```json
{
  "code": "invalid_args",
  "message": "teleport requires a target position",
  "details": {"missing": ["x", "y"]}
}
```

Valid error codes (extend as needed):

- `usage` — command invoked without required args/kwargs.
- `invalid_args` — arguments parsed but rejected (bad types, out-of-bounds).
- `not_found` — referenced agent/object missing.
- `forbidden` — issuer lacks permission (mode mismatch).
- `unsupported` — command not available in this shard/build.
- `conflict` — state conflict (e.g., duplicate spawn id, reservation clash).
- `internal` — unexpected exception; `details` should include truncated traceback.

Audit log entries mirror the response envelope with additional transport metadata
(client IP, auth context, etc.).

### 2.1 Telemetry Alignment

`TelemetryPublisher.export_state()` exposes `console_results` and historical records using the
same schema above. Any refactor must keep these payloads stable so dashboards and CLI tools
(`scripts/observer_ui.py`, `townlet_ui.dashboard`) continue to parse responses without changes.

## 3. Command Catalog

### 3.1 Implemented Handlers (as of `src/townlet/console/handlers.py`)

| Command | Mode | Args / Kwargs | Result Summary | Notes |
| --- | --- | --- | --- | --- |
| `telemetry_snapshot` | viewer | – | Latest telemetry blocks (jobs, economy, conflict, etc.). | Wraps `TelemetryBridge.snapshot()`.
| `employment_status` | viewer | – | Employment queue metrics + schema version. | Depends on employment telemetry being populated.
| `relationship_summary` | viewer | – | Per-agent top friends/rivals plus churn aggregates. | Read-only; safe for dashboards even when relationships disabled (returns empty sets).
| `social_events` | viewer | Optional `limit` kwarg (`int ≥ 0`). | Recent chat / rivalry-avoidance events (newest first). | Defaults to full bounded history (60 events).
| `relationship_detail` | admin | `agent_id` positional or kwarg. | Detailed ties, delta overlay, and update history for an agent. | Admin-only; exposes ledger edges and should be guarded in shared shards.
| `employment_exit` | admin | `("review")` or `("approve", agent_id)`, `("defer", agent_id)` | Queue state / boolean flags. | Calls `WorldState.employment_queue_snapshot` and approval helpers.
| `conflict_status` | viewer | Optional `history`, `rivalries`. | Conflict snapshot, queue history, rivalry events. | Useful for dashboards.
| `queue_inspect` | viewer | `object_id` | Queue entries, cooldowns, stall counts. | Requires queue manager export state.
| `rivalry_dump` | viewer | Optional `agent_id`, `limit`. | Rival edges or per-agent list. | Falls back to rivalry snapshot.
| `promotion_status` | viewer | – | Current promotion snapshot. | No-op when promotion manager absent.
| `promote_policy` | admin | `checkpoint`, optional `policy_hash`. | `{promoted: true, promotion: ...}` | Validates candidate readiness.
| `rollback_policy` | admin | Optional `checkpoint`, `reason`. | `{rolled_back: true, promotion: ...}` | Resets candidate metadata.
| `policy_swap` | admin | `checkpoint`, optional `policy_hash`. | `{swapped: true, release: ...}` | Verifies checkpoint exists, records manual swap event.
| `perturbation_queue` | viewer | – | Latest scheduler state. | Requires scheduler wired in router.
| `perturbation_trigger` | admin | `spec`, kwargs (`starts_in`, `duration`, `targets`, `magnitude`, `location`). | `{enqueued: true, event: ...}` | Rejects unknown specs/invalid args.
| `perturbation_cancel` | admin | `event_id` | `{cancelled: bool}` | No-op when scheduler absent.
| `snapshot_inspect` | viewer | `path` | Snapshot metadata (config, tick, migrations). | Performs filesystem I/O; mode viewer but may require path ACL.
| `snapshot_validate` | admin? | `path`, optional `strict`. | `{valid: bool, migrations_applied: [...]}` | Requires `SimulationConfig` to be injected.
| `snapshot_migrate` | admin | `path`, optional `output`. | `{migrated: true, ...}` | Admin-only; writes migrated snapshot.
| `spawn` | admin | `docs/program_management/snapshots/ARCHITECTURE_INTERFACES.md:127` | Payload `{"agent_id": str, "position": [x, y], "home_position"?, "job_id"?, "needs"?, "wallet"?}`. Creates agent, assigns job, initialises employment context, and returns snapshot summary (including `home_position`). |
| `teleport` | admin | same | Payload `{"agent_id": str, "position": [x, y]}`. Moves agent to walkable tile, updates reservations/queues, returns new position. |
| `setneed` | admin | `docs/ops/OPS_HANDBOOK.md:204` | Payload `{"agent_id": str, "needs": {...}}`. Clamps needs to [0,1], updates snapshot, returns new values. |
| `price` | admin | conceptual design | Payload `{"key": str, "value": float}` (existing `config.economy` key). Updates economy entry, recomputes basket cost, returns new value. |
| `force_chat` | admin | `docs/program_management/snapshots/CONCEPTUAL_DESIGN.md:321` | Payload `{"speaker": str, "listener": str, "quality"?: float}`. Forces chat success, updates relationship ties, returns trust/familiarity/rivalry. |
| `set_rel` | admin | `docs/program_management/snapshots/CONCEPTUAL_DESIGN.md:324` | Payload `{"agent_a": str, "agent_b": str, "trust"?, "familiarity"?, "rivalry"?}`. Sets relationship values (clamped), returns both ties. |
| `arrange_meet` | admin | `docs/program_management/snapshots/CONCEPTUAL_DESIGN.md:328` | Payload `{"spec": str, "agents": [..], "starts_in"?, "duration"?, "payload"?}`. Delegates to perturbation scheduler and returns scheduled event metadata. |
| `possess` | admin | `docs/program_management/snapshots/CONCEPTUAL_DESIGN.md:324` | Payload `{"agent_id": str, "action"?: "acquire"|"release"}`. Toggles possession state and pauses scripted behaviour. |
| `kill` | admin | conceptual design | Payload `{"agent_id": str, "reason"?: str}`. Queues immediate lifecycle exit and emits audit entry. |
| `toggle_mortality` | admin | conceptual design | Payload `{"enabled": bool}`. Enables or disables mortality guardrails. |
| `set_exit_cap` | admin | conceptual design | Payload `{"daily_exit_cap": int}`. Updates `employment.daily_exit_cap` and refreshes employment metrics. |
| `set_spawn_delay` | admin | conceptual design | Payload `{"delay": int}` or positional integer. Updates `lifecycle.respawn_delay_ticks`. |

### 3.2 Planned / Not Yet Implemented Commands

Derived from design docs and ops handbook; these are currently missing in the handler:

| Command | Intended Mode | Reference | Brief |
| --- | --- | --- | --- |
| `set_death_threshold` | admin | conceptual design | Parameterise need thresholds/ticks for lifecycle exits. |
| `set_employment_param` | admin | conceptual design | Tune other employment settings (grace_ticks, penalties) via console. |

These backlog commands require implementation in `WorldState.apply_console` plus
authz, validation, and telemetry/audit coverage before they can be exposed.

## 4. Outstanding Work

Console results are now captured each tick and exposed via both telemetry
(`telemetry_snapshot.console_results`) and the audit log at
`logs/console/commands.jsonl`, providing operators immediate confirmation of
command outcomes.

1. **Backlog Commands** — Implement the planned operations to close the gap with ops
   runbooks (spawn, teleport, setneed, force_chat, arrange_meet, lifecycle toggles).
2. **Admin Safety Rails** — Evaluate rate limits and multi-factor flows on top of
   the token-based authentication introduced in WP-101, especially for destructive
   commands.
3. **CLI/Transport Updates** — Update `scripts/console_*` clients to emit the
   full envelope (including `cmd_id`, `mode`) and surface `console_results` to
   operators alongside audit tail helpers.
4. **Documentation Sync** — Expand `docs/guides/CONSOLE_DRY_RUN.md` and ops playbooks
   with examples demonstrating the new result telemetry and audit log.

Maintaining this document whenever handlers change ensures the console transport,
CLI, and simulation stay in lockstep and prevents regressions during future
automation work.
