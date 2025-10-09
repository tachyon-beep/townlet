# WP3 Telemetry Event Schema

This document specifies the canonical event/metric payloads that the telemetry sink will accept. The schema covers the lifecycle, console, policy, and stability flows required to unblock WP1/WP2.

All event payloads are JSON-serialisable mappings. Timestamps are expressed as integers (simulation ticks) or ISO-8601 strings where appropriate. Optional fields are marked accordingly.

## 1. Loop Lifecycle Events

### 1.1 `loop.tick`
Emitted once per simulation tick after world advancement and reward computation.

```json
{
  "tick": 123,
  "runtime_variant": "facade",
  "world": {
    "snapshot_ref": "memory://world/123",          // reference or inline snapshot (implementation detail)
    "agents_active": 42,
    "objects_active": 128
  },
  "observations": {
    "agents": [...],                               // list/dict of observation DTOs (see §2)
    "terminated": { "alice": false, "bob": true }
  },
  "rewards": { "alice": 1.25, "bob": -0.5 },
  "reward_breakdown": { ... },                     // optional per-agent breakdown
  "stability_inputs": {
    "hunger_levels": { "alice": 0.3, "bob": 0.7 },
    "option_switch_counts": { "alice": 0, "bob": 2 },
    "reward_samples": { "alice": 12.0 }
  },
  "policy_snapshot": { ... },                      // latest policy metadata (per-agent)
  "policy_identity": {
    "hash": "abc123",
    "anneal_ratio": 0.4,
    "provider": "scripted"
  },
  "possessed_agents": ["spectator_1"],
  "events": [ { "type": "affordance.fail", ... } ],
  "perturbations": { ... },                        // normalised perturbation payload
  "social_events": [ ... ]                         // optional
}
```

### 1.2 `loop.health`
Emitted after each tick summarising health metrics and transport status.

```json
{
  "tick": 123,
  "status": "ok",
  "duration_ms": 7.5,
  "queue_metrics": {
    "cooldown_events": 1,
    "ghost_step_events": 0,
    "rotation_events": 0
  },
  "transport": {
    "provider": "stdout",
    "queue_length": 3,
    "dropped_messages": 0,
    "last_flush_duration_ms": 1.2,
    "worker_alive": true,
    "worker_restart_count": 0,
    "auth_enabled": false
  },
  "promotion": { ... },                            // promotion snapshot
  "stability": {
    "latest_metrics": { ... },
    "alerts": ["queue_fairness_pressure"]
  }
}
```

### 1.3 `loop.failure`
Emitted when a tick raises an unrecoverable error.

```json
{
  "tick": 124,
  "error": "SimulationLoopError: ...",
  "duration_ms": 5.1,
  "failure_count": 3,
  "snapshot_path": "s3://snapshots/failure_124",
  "transport": { ... }                             // same shape as loop.health.transport
}
```

## 2. Policy Events

- `policy.metadata`: emitted whenever policy hash/variant/anneal ratio changes.
- `policy.possession`: emitted when agent possession changes (e.g., spectator takes control).
- `policy.anneal.update`: anneal ratio adjustments (tick, ratio, source).

Observation DTOs referenced in `loop.tick` will be defined as:

```json
{
  "agent_id": "alice",
  "position": [1, 2],
  "needs": { "hunger": 0.2, "energy": 0.8 },
  "inventory": { "wages_earned": 10 },
  "job": {
    "id": "chef",
    "on_shift": true,
    "lateness_counter": 0,
    "late_ticks_today": 0,
    "attendance_ratio": 0.95
  },
  "relations": {
    "rivalry": { "bob": -0.3 }
  }
}
```

## 3. Console & Stability Events

- `console.result`: results emitted for each processed command.
- `stability.metrics`: optional aggregate metrics per tick (rolling windows).
- `rivalry.events`: batched rivalry updates (tick, agents, intensity, reason).

## 4. Metrics (`emit_metric`)

Metrics carry a numerical value and optional tags. Standard tags include `tick`, `provider`, `agent_id`. Core metrics:

| Metric Name               | Description                                 | Value Type | Tags                       |
|---------------------------|---------------------------------------------|------------|----------------------------|
| `loop.duration_ms`        | Wall-clock duration per tick                | float      | `tick`                     |
| `telemetry.queue.length`  | Transport backlog                           | float      | `provider`, `tick`         |
| `queue.cooldown_events`   | Delta cooldown events per tick              | float      | `tick`                     |
| `policy.anneal.ratio`     | Current anneal ratio                        | float      | `tick`, `provider`         |
| `stability.alert`         | Count of alerts emitted in the tick         | float      | `tick`, `alert_type`       |

## 5. Retention & History

- Queue history: maintain last 120 ticks for fairness, emitted via `loop.health`.
- Rivalry history: retain latest 120 events, surfaced in `loop.tick` (optional) and `rivalry.events`.
- Possessed agents: emit full list on change and include in `loop.tick`.

## 6. WP1/WP2 Integration Points

- WP1 Step 8 will update `SimulationLoop` to emit `loop.tick`, `loop.health`, `loop.failure` events instead of calling legacy writers.
- WP2 Step 7 will supply observation DTOs and rivalry metrics via the modular world context, feeding directly into the event payloads above.

Future updates to this schema should be versioned and documented here before implementation.

