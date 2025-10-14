# External Guidance — WP1 Console & Monitoring Design

Source: Architecture review feedback (2024-XX-XX) confirming approach for WP1 adapters and loop refactor.

## Summary
- Ports remain minimal; orchestration services handle console and health monitoring.
- Introduce a `ConsoleRouter` service that converts console commands into world actions/queries and emits results via telemetry events.
- Introduce a `HealthMonitor` (stability monitor) consuming world snapshots/events to compute metrics; metrics emitted via telemetry sink.
- World adapter owns `ObservationBuilder`; `WorldRuntime.observe()` stays the single entrypoint for observation payloads.
- World snapshots must include tick-scoped domain events under a stable key (e.g., `events`).
- Telemetry sink stays write-only; remove reliance on `telemetry.latest_*`.
- Tick pipeline sequence: console → observe → decide → apply actions → tick → snapshot → health monitor → telemetry events/metrics.
- Event schema recommendation: `{"type": "domain.namespace", "tick": int, "payload": {...}}`.
- Config guidance: world observation profile, monitor window, telemetry provider remain runtime options.
- Tests to add: console routing, health monitor metrics, observation profile selection, telemetry getter guard.
- Risks: avoid reintroducing telemetry getters; forbid world from handling console logic; guard observation shape churn with golden tests.
- Note: the “Fix Pack” diff that accompanied this guidance used placeholder imports/constructors and changed scripted behaviour; we are adopting the strategic direction while implementing code tailored to the actual Townlet runtime.

Full architect response (verbatim):

> Got it. You’ve landed exactly on the right fault lines to sort *before* writing adapters. Here’s a clean, ADR‑aligned design that answers those three questions and gives you a concrete Step‑2 plan the agent can implement without guessing.
>
> ---
>
> ## Core principles (unchanged from ADR 0001)
>
> * **Ports stay minimal.** World is the source of truth; Telemetry is a sink; Policy decides actions. No console/training/transport concerns in any port.
> * **Event‑first orchestration.** World produces domain events and state; orchestration‑level services (console, monitors) *consume* those and decide what to emit to telemetry. The loop never “pulls” from telemetry.
>
> ---
>
> ## Q1 — Console commands/results without leaking into ports
>
> **Decision:** Add a small **ConsoleRouter** service in the orchestration layer (not a port). It parses commands, invokes world operations using `WorldRuntime` methods, and emits results as events to `TelemetrySink`.
>
> * **Why:** Keeps CLI/UI concerns out of domain and out of telemetry’s API. Telemetry remains a dumb sink.
> * **Shape:** Commands are translated into *world actions* where possible (e.g., “spawn Agent42 at (x,y)” → `world.apply_actions`), or world queries (use `world.snapshot()`/`observe()`).
>
> **Sketch:**
>
> ```python
> # orchestration/console.py
> from collections import deque
> from typing import Mapping, Any
> from townlet.ports.world import WorldRuntime
> from townlet.ports.telemetry import TelemetrySink
>
> class ConsoleRouter:
>     def __init__(self, world: WorldRuntime, telemetry: TelemetrySink):
>         self._q: deque[str] = deque()
>         self._world = world
>         self._telemetry = telemetry
>
>     def enqueue(self, cmd: str) -> None:
>         self._q.append(cmd)
>
>     def run_pending(self) -> None:
>         while self._q:
>             cmd = self._q.popleft()
>             result: Mapping[str, Any] = self._execute(cmd)
>             self._telemetry.emit_event("console.result", {"cmd": cmd, "result": result})
>
>     def _execute(self, cmd: str) -> Mapping[str, Any]:
>         # parse → {op, args}
>         # map to world.apply_actions(...) or world.snapshot()/observe()
>         # return a structured result (never raw strings)
>         ...
> ```
>
> * **Where does input come from?** Your UI/CLI feeds `ConsoleRouter.enqueue(...)`.
> * **How do results get out?** Only via `telemetry.emit_event("console.result", ...)`.
>
> ---
>
> ## Q2 — Stability/promotions without `telemetry.latest_*`
>
> **Decision:** Introduce a **HealthMonitor** (or “StabilityMonitor”) service in orchestration. It *consumes* (a) the world’s **snapshot** and (b) the world’s **domain events** for the current tick, and it *produces* metrics/events that are then sent to Telemetry. No “pulling” from telemetry.
>
> * **Why:** A sink should never be your data source. The monitor is where rollups, moving windows, queue lengths, rivalry counters, etc., live.
>
> **World → events:** Keep ports minimal by returning events inside `world.snapshot()` under a stable key (e.g., `{"events": [...]}`). That’s legal per ADR because it doesn’t expand the API surface—`snapshot()` already returns a mapping.
>
> **Sketch:**
>
> ```python
> # orchestration/health.py
> from collections import deque
> from typing import Mapping, Iterable, Any
> from townlet.ports.telemetry import TelemetrySink
>
> class HealthMonitor:
>     def __init__(self, window: int = 100):
>         self._rivalry_events: deque[Mapping[str, Any]] = deque(maxlen=window)
>         self._queue_lengths: deque[int] = deque(maxlen=window)
>
>     def on_tick(self, snapshot: Mapping[str, Any], telemetry: TelemetrySink) -> None:
>         tick = snapshot.get("tick")
>         events: Iterable[Mapping[str, Any]] = snapshot.get("events", [])
>
>         # Update rolling state
>         for ev in events:
>             if ev.get("type") == "rivalry.started":
>                 self._rivalry_events.append(ev)
>         qlen = snapshot.get("metrics", {}).get("queue_length")  # or derive from state
>         if qlen is not None:
>             self._queue_lengths.append(qlen)
>
>         # Emit metrics: source-of-truth is snapshot+events, not telemetry
>         telemetry.emit_metric("queue.length.latest", self._queue_lengths[-1] if self._queue_lengths else 0, tick=tick)
>         telemetry.emit_metric("rivalry.started.rate", len(self._rivalry_events), tick=tick)
> ```
>
> * **If stability/promotions need metrics to affect gameplay:** they should **query world state** (via `snapshot()`/`observe()`), *not* telemetry.
>
> ---
>
> ## Q3 — Where does `ObservationBuilder` live?
>
> **Decision:** **Internal to the world implementation** (adapter/facade), not a public port. The port already exposes `observe(agent_ids=None)`. Your world adapter composes an `ObservationBuilder` behind the scenes.
>
> * **Why:** Observations are a *view of world state*. They evolve with world internals and shouldn’t leak a second abstraction into the loop.
> * **Configurability:** Allow a config value like `world.observation_profile: "default" | "minimal" | "ml_v1"` that the world factory uses to pick/compose the builder.
>
> **Sketch:**
>
> ```python
> # townlet/world/observe_builder.py  (world-internal)
> class ObservationBuilder:
>     def __init__(self, profile: str = "default"): ...
>     def build(self, state, agent_ids=None) -> dict[str, dict]:
>         ...
>
> # townlet/adapters/world_default.py
> class DefaultWorldAdapter(WorldRuntime):
>     def __init__(self, impl, obs_builder: ObservationBuilder):
>         self._impl = impl
>         self._obs = obs_builder
>
>     def observe(self, agent_ids=None):
>         state = self._impl.state()  # or however you expose it internally
>         return self._obs.build(state, agent_ids)
> ```
>
> ---
>
> ## Updated tick pipeline (loop + services)
>
> ```python
> # composition root
> world = create_world(cfg)
> policy = create_policy(cfg)
> telemetry = create_telemetry(cfg)
>
> console = ConsoleRouter(world, telemetry)
> health  = HealthMonitor(window=cfg.monitor.window)
>
> telemetry.start()
> world.reset(seed=cfg.seed)
>
> for _ in range(cfg.runtime.max_ticks):
>     # 0) handle any console inputs that arrived since last tick
>     console.run_pending()
>
>     # 1) decision
>     obs = world.observe()                         # agent_ids=None → all
>     actions = policy.decide(obs)
>
>     # 2) transition
>     world.apply_actions(actions)
>     world.tick()
>
>     # 3) inspect & publish
>     snap = world.snapshot()                       # includes {"tick": int, "events": [...]}
>     health.on_tick(snap, telemetry)               # emits metrics derived from events/state
>     telemetry.emit_event("tick", {"tick": snap["tick"]})
>
> telemetry.stop()
> ```
>
> ---
>
> ## Adapter responsibilities map (who owns what)
>
> | Concern                                        | Owner                                                 | Why                                         |
> | ---------------------------------------------- | ----------------------------------------------------- | ------------------------------------------- |
> | Command parsing, help text                     | `ConsoleRouter`                                       | UI concern; not domain.                     |
> | Executing admin ops (spawn, move, set attr)    | `ConsoleRouter` → `WorldRuntime`                      | Admin ops become world actions.             |
> | Console output                                 | `ConsoleRouter` → `emit_event("console.result", ...)` | Telemetry is sink, not source.              |
> | Queue metrics, rivalry counts, moving averages | `HealthMonitor`                                       | Aggregations derived from snapshots/events. |
> | Emitting metrics                               | `HealthMonitor` (→ `TelemetrySink.emit_metric`)       | Keep Telemetry dumb.                        |
> | Observations                                   | World adapter + internal `ObservationBuilder`         | Observations are a view on state.           |
> | Domain events                                  | Produced by world (in snapshot)                       | Source-of-truth lives with world.           |
>
> ---
>
> ## Work Package 2 — concrete task list (updated)
>
> **A. Scaffolding**
> 1. Create `orchestration/console.py` and `orchestration/health.py`.
> 2. Add simple, structured event schema conventions (see below).
>
> **B. World adapter**
> 3. Move/compose the existing `ObservationBuilder` into the world adapter; add `observation_profile` selection in the world factory.
> 4. Ensure `world.snapshot()` includes `{"tick": int, "events": list[dict]}`. (Events are drained per tick by convention.)
> 5. Keep *all* console hooks out of world; admin commands go via `ConsoleRouter` → `apply_actions`.
>
> **C. Telemetry adapter**
> 6. Keep the adapter a **sink** only: `start/stop/emit_event/emit_metric`. If it currently offered getters, delete or move to monitors.
>
> **D. Loop refactor**
> 7. Wire `ConsoleRouter` and `HealthMonitor` into the composition root like the pipeline above.
>
> **E. Tests**
> 8. `tests/test_console_router.py` — command routing to world + emits `console.result`.
> 9. `tests/test_health_monitor.py` — given snapshots/events, emits expected metrics.
> 10. `tests/test_world_observe_integration.py` — `observe()` reflects selected `observation_profile`.
> 11. `tests/test_loop_no_telemetry_pull.py` — prove there are no imports/calls of `telemetry.latest_*`.
>
> **F. Docs**
> 12. Add `docs/adr/0002-console-and-monitoring.md` with: data‑flow diagram, event schema, and the new tick pipeline.
>
> ---
>
> ## Event schema (keep it boring and regular)
>
> * Every event is a dict with:
>   `{"type": "<domain|console|system>.<name>", "tick": int, "ts": float, "payload": {...}}`
> * Examples:
>
>   * `{"type": "rivalry.started", "tick": 42, "payload": {"agent_a": "id1","agent_b":"id2"}}`
>   * `{"type": "console.result", "tick": 42, "payload": {"cmd": "spawn Bob", "result": {"ok": True}}}`
>
> This lets monitors pattern‑match without coupling.
>
> ---
>
> ## Config nudges
>
> ```yaml
> runtime:
>   seed: 123
>   max_ticks: 1000
>   observation_profile: default
>
> monitor:
>   window: 200
>
> telemetry:
>   provider: stdout
>   # optional: log_level, path, etc.
> ```
>
> * World factory reads `runtime.observation_profile` to pick the builder.
> * HealthMonitor reads `monitor.window`.
>
> ---
>
> ## Risks & mitigations
>
> * **Accidentally re‑introducing getters on telemetry.**
>   *Guard:* a test that greps the codebase for `latest_` usage on telemetry imports.
>
> * **Hidden console behaviours in world.**
>   *Guard:* forbid imports from `orchestration.console` under `townlet/world/*` in lint rules, and assert world emits no `console.*` events by itself.
>
> * **Observation shape churn.**
>   *Guard:* snapshot/observation golden tests; profile‑specific builders to compartmentalise change.
>
> ---
>
> ## What your agent should implement now (Step‑2 ready)
>
> 1. Add `ConsoleRouter` and `HealthMonitor` as above.
> 2. Update world adapter to own `ObservationBuilder` internally and to include `events` in `snapshot()`.
> 3. Remove any telemetry pulls; ensure monitors compute and emit metrics.
> 4. Wire the updated tick pipeline in the composition root.
> 5. Add the tests enumerated.
>
> ---
>
> **WEP (confidence):** High‑likely this design cleanly resolves your three blockers while staying faithful to ADR 0001; Moderate on exact event/metric names matching your existing audit (easy to rename in implementation).
