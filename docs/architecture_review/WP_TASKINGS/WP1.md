## Prompt: *Implement Work Package 1 — Core Interfaces & Factories (ADR‑aligned) for Townlet*

**Role:** You are an autonomous coding agent contributing to **Townlet**. Implement **WP1** per **ADR 0001: Ports and Factory Registry**. Your job: introduce minimal ports (`WorldRuntime`, `PolicyBackend`, `TelemetrySink`), add adapters for current implementations, wire **registry‑backed factories**, and refactor the composition root so the loop depends **only** on ports. Backwards compatibility is **not** required (pre‑1.0).

> **Read first (in repo):**
>
> * `docs/architecture_review`
> * `docs/adr/0001-ports-and-factory-registry.md` (or `0001-ports-and-factories.md`) — the ADR that defines the intended surface
> * The simulation entrypoint/loop
> * Current world/policy/telemetry code paths

**Non‑negotiable ADR constraints (bake these in):**

* **Minimal ports only.** No console buffering, HTTP/transport specifics, or training hooks on ports.
* **World owns the tick** → `world.tick()` takes no tick arg; loop can read tick via `world.snapshot()`.
* **Telemetry has lifecycle** (`start`, `stop`) and two generic calls: `emit_event`, `emit_metric`.
* **Policy is stateless from the loop’s perspective** apart from `on_episode_start`, `decide`, `on_episode_end`.

---

### Deliverables (Definition of Done)

1. **Ports (Protocols) — minimal and ADR‑compliant**

   * Create `townlet/ports/` with:

     * `world.py`:

       ```python
       from typing import Protocol, Iterable, Mapping, Any
       class WorldRuntime(Protocol):
           def reset(self, seed: int | None = None) -> None: ...
           def tick(self) -> None: ...
           def agents(self) -> Iterable[str]: ...
           def observe(self, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]: ...
           def apply_actions(self, actions: Mapping[str, Any]) -> None: ...
           def snapshot(self) -> Mapping[str, Any]: ...
       ```

     * `policy.py`:

       ```python
       from typing import Protocol, Mapping, Any, Iterable
       class PolicyBackend(Protocol):
           def on_episode_start(self, agent_ids: Iterable[str]) -> None: ...
           def decide(self, observations: Mapping[str, Any]) -> Mapping[str, Any]: ...
           def on_episode_end(self) -> None: ...
       ```

     * `telemetry.py`:

       ```python
       from typing import Protocol, Mapping, Any
       class TelemetrySink(Protocol):
           def start(self) -> None: ...
           def stop(self) -> None: ...
           def emit_event(self, name: str, payload: Mapping[str, Any] | None = None) -> None: ...
           def emit_metric(self, name: str, value: float, **tags: Any) -> None: ...
       ```

   * **Do not** add methods like `queue_console`, `drain_console_buffer`, `flush_transitions`, `active_policy_hash`, `publish_tick`, `record_loop_failure`, etc. If current code calls those, they move to adapters or internal helpers — not the ports.

2. **Adapters (anti‑corruption layer)**

   * Implement thin adapters that satisfy the ports by delegating to today’s concrete classes:

     * `townlet/adapters/world_default.py` → `DefaultWorldAdapter(WorldRuntime)`
     * `townlet/adapters/policy_scripted.py` → `ScriptedPolicyAdapter(PolicyBackend)`
     * `townlet/adapters/telemetry_stdout.py` → `StdoutTelemetryAdapter(TelemetrySink)`
   * Keep each adapter focused; translation of legacy shapes happens here.

3. **Registry‑backed Factories**

   * Add `townlet/factories/registry.py` with a simple `REGISTRY: dict[str, dict[str, Callable[..., object]]]` and:

     ```python
     def register(kind: str, key: str): ...
     class ConfigurationError(RuntimeError): ...
     ```

   * Add:

     * `townlet/factories/world_factory.py` → `create_world(cfg) -> WorldRuntime`
    * `townlet/factories/policy_factory.py` → `create_policy(cfg, world=None) -> PolicyBackend`
     * `townlet/factories/telemetry_factory.py` → `create_telemetry(cfg) -> TelemetrySink`
   * Register built‑ins:

     * World: `"default"`, `"dummy"`
     * Policy: `"scripted"` (default), `"dummy"`
     * Telemetry: `"stdout"` (default), `"stub"`, `"dummy"`
   * Unknown keys must raise `ConfigurationError(f"Unknown {kind} provider: {key}. Known: {sorted(REGISTRY[kind])}")`.

4. **Refactor the Composition Root**

   * Update the run/CLI entrypoint to:

     ```python
     world = create_world(cfg)
     policy = create_policy(cfg, world=world)
     telemetry = create_telemetry(cfg)
     telemetry.start()
     # Loop sketch:
     obs = world.observe()                        # agent_ids=None → all
     actions = policy.decide(obs)
     world.apply_actions(actions)
     world.tick()
     telemetry.emit_event("tick", world.snapshot())
     telemetry.stop()
     ```

   * The loop imports only `townlet.ports.*` and factory helpers. **No concrete imports**.

5. **Minimal Stubs (for tests & examples)**

   * `townlet/testing/dummies.py`:

     * `DummyWorld(WorldRuntime)`
     * `DummyPolicy(PolicyBackend)`
     * `DummyTelemetry(TelemetrySink)`
   * Register them with keys (`"dummy"`/`"stub"`), and allow selection via config for smoke tests.

6. **Tests**

   * `tests/test_ports_surface.py` — assert **forbidden symbols** are not present in port modules (simple string scan).
   * `tests/test_factories.py` — known keys resolve; unknown keys raise; returned objects behave as ports (duck‑typed).
   * `tests/test_loop_with_dummies.py` — 2–3 ticks using only dummies; no exceptions; deterministic `snapshot()["tick"]` increments.
   * `tests/test_loop_with_adapters_smoke.py` — 1–2 ticks with default adapters (mark `slow` if needed).

7. **Docs & Hygiene**

   * Ensure `docs/adr/0001-ports-and-factory-registry.md` matches these **minimal** method tables. If your ADR filename differs, update it in place rather than adding a new ADR.
   * Add concise docstrings to all public port and factory functions.
   * New/changed files pass `ruff` and `mypy` (project settings). Keep functions short and cohesive.

---

### Constraints & Non‑Goals

* No plugin entry points or optional‑deps machinery yet (that’s a later WP). Keep the registry simple.
* Do not mirror legacy god‑classes on ports; ports reflect only what the loop needs **today**.
* No console/HTTP/training detail leaks onto the ports.

---

### Method Discovery (do this before coding the ports)

1. Scan the loop for all calls into world, policy, telemetry; list the operations.
2. **Trim aggressively**: if the loop doesn’t absolutely need a method, it’s not on the port.
3. Where current code expects extra behaviours (console buffers, training artefacts), implement them **inside adapters** or helper modules, not on the ports.

---

### Example Registry Wiring

```python
# townlet/adapters/world_default.py
from townlet.factories.registry import register
from townlet.ports.world import WorldRuntime

@register("world", "default")
def build_world(cfg) -> WorldRuntime:
    # construct and return adapter that wraps the current world
    ...
```

(Mirror for `policy` and `telemetry`.)

---

### Sanity Checklist (acceptance gates)

* [ ] `townlet/ports/*` expose exactly the ADR‑specified methods; **no** console/training/transport methods.
* [ ] Composition root imports only ports and factories.
* [ ] At least one `"default"` adapter per domain is registered and used by default config.
* [ ] `pytest -q` passes the new tests; smoke tests green.
* [ ] `ruff`/`mypy` clean for new code; docstrings present.
* [ ] ADR updated to reflect the exact method tables implemented.

---

### Optional Quality Guard (tiny test snippet)

```python
# tests/test_ports_surface.py
import importlib, pathlib
FORBIDDEN = {"queue_console","drain_console_buffer","flush_transitions",
             "active_policy_hash","publish_tick","record_loop_failure","close"}

def test_ports_do_not_expose_forbidden_symbols():
    for mod in ("townlet.ports.world","townlet.ports.policy","townlet.ports.telemetry"):
        m = importlib.import_module(mod)
        text = pathlib.Path(m.__file__).read_text()
        assert all(s not in text for s in FORBIDDEN), f"{mod} leaks forbidden API"
```

---

**Proceed to implement Work Package 1 now, strictly following ADR 0001.**
