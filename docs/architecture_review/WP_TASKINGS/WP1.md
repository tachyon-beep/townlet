## Prompt: *Implement Work Package 1 — Core Interfaces & Factories for Townlet*

**Role:** You are an autonomous coding agent contributing to the open‑source project **Townlet**. Your task is to implement **Work Package 1**: introduce clean interface boundaries and factories for the World, Policy, and Telemetry subsystems, then refactor the simulation entrypoint to depend on these interfaces (not concrete implementations). Backwards compatibility is **not** required (pre‑1.0).

> **Important context to read first (in repo):**
>
> * `docs/architecture_review` (the audit explaining current problems and desired direction)
> * The simulation entrypoint/loop and the current “world”, “policy”, and “telemetry” code paths
>
> **Goal:** decouple the simulation loop from concrete classes using well‑defined interfaces + factories, add minimal adapters to wrap existing implementations, and provide stub/dummy backends for tests.

---

### Deliverables (Definition of Done)

1. **Interfaces (Ports)**

   * Introduce three interfaces (prefer `typing.Protocol`, fall back to `abc.ABC` if needed):

     * `WorldRuntime` — read/advance world state + apply actions.
     * `PolicyBackend` — decide actions for agents (can be scripted/ML later).
     * `TelemetrySink` — consume events/metrics, with optional lifecycle (start/stop).
   * Place these in a dedicated package, e.g. `townlet/ports/` (`__init__.py`, `world.py`, `policy.py`, `telemetry.py`), or `townlet/core/ports/` if that fits better.
   * Keep interfaces **minimal** and **inferred from actual call‑sites** (see “Method discovery” below).

2. **Adapters (Anti‑corruption Layer)**

   * Implement thin adapters that wrap **current** concrete implementations to satisfy the new interfaces:

     * `WorldRuntime` ← wraps current world engine (e.g., `Grid`/`World/...`).
     * `PolicyBackend` ← wraps current policy runner.
     * `TelemetrySink` ← wraps current telemetry/publisher.
   * Put adapters under `townlet/adapters/…` with small, cohesive modules.

3. **Factories / Registry**

   * Provide factories that return interface implementations from config:

     * `townlet/factories/world_factory.py` → `create_world(config) -> WorldRuntime`
     * `townlet/factories/policy_factory.py` → `create_policy(config) -> PolicyBackend`
     * `townlet/factories/telemetry_factory.py` → `create_telemetry(config) -> TelemetrySink`
   * Use a **string→callable registry** pattern (e.g., `REGISTRY["world"]["default"] = WorldAdapter`).
   * If a requested key is unknown, raise a clear `ConfigurationError`.
   * Do **not** introduce plugin entry points yet (save that for later work packages).

4. **Refactor Simulation Composition Root**

   * Identify the composition root (where the sim is wired up). Refactor it to:

     * Load config.
     * Instantiate `world = create_world(cfg)`, `policy = create_policy(cfg)`, `telemetry = create_telemetry(cfg)`.
     * Pass only **interfaces** to the simulation loop.
   * The simulation loop must import only `ports.*` interfaces, **not** concrete classes.

5. **Minimal Stubs for Tests**

   * Add simple `DummyWorld`, `DummyPolicy`, `DummyTelemetry` that implement the interfaces with trivial behaviour; place under `tests/util/` or `townlet/testing/`.
   * Verify factories can return these via config (e.g. `"world": "dummy"`).

6. **Tests**

   * Unit tests asserting:

     * Interfaces are respected by adapters (duck typing / `isinstance` via `Protocol` not required).
     * Factories produce the correct type for known keys; unknown keys raise.
     * Simulation loop can run 2–3 ticks using **only dummy** implementations.
   * A smoke test using the **real adapters** (world/policy/telemetry) for 1–2 ticks, guarded with `pytest.mark.slow` if needed.

7. **Docs & Dev Ergonomics**

   * Update `docs/architecture_review` or add `docs/adr/0001-ports-and-factories.md` summarising:

     * The three interfaces (with method tables).
     * Registry keys exposed by each factory.
     * Example config snippets to select implementations.
   * Inline docstrings on all interfaces + factories (concise but descriptive).
   * Ensure `ruff`/`mypy` pass for the new/changed files.

---

### Constraints & Non‑Goals

* No need to preserve older import paths or runtime flags.
* Do **not** introduce heavy plugin systems or optional dependency handling yet (that’s later). Just keep the factory/registry ready for that evolution.
* Keep interfaces small; **do not** mirror the current large classes. Interfaces must reflect what the sim actually needs.

---

### Method Discovery (crucial)

Before writing interfaces, **discover the minimal required methods** by scanning the simulation loop and call sites:

1. **Find usage** of world/policy/telemetry from the loop. Make a list of required operations, e.g.:

   * World: `reset(seed?)`, `tick()`, `apply_actions(actions)`, `observe(agent_ids|scope)`, `snapshot()`, `agents()`…
   * Policy: `decide(observation|world_view) -> actions`, optional `on_episode_start/end`, optional `train_step(...)`.
   * Telemetry: `emit_event(name, payload)`, `emit_metric(name, value, tags)`, optional `start()`, `stop()`.
2. **Trim aggressively**: if the loop doesn’t need it, don’t put it on the interface.
3. **Name for intent**: prefer domain verbs (`decide`, `snapshot`) over transport‑specific terms.

---

### Suggested Interface Sketch (adjust to findings)

```python
# townlet/ports/world.py
from typing import Protocol, Iterable, Mapping, Any

class WorldRuntime(Protocol):
    def reset(self, seed: int | None = None) -> None: ...
    def tick(self) -> None: ...
    def agents(self) -> Iterable[str]: ...
    def observe(self, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]: ...
    def apply_actions(self, actions: Mapping[str, Any]) -> None: ...
    def snapshot(self) -> Mapping[str, Any]: ...
```

```python
# townlet/ports/policy.py
from typing import Protocol, Mapping, Any, Iterable

class PolicyBackend(Protocol):
    def decide(self, observations: Mapping[str, Any]) -> Mapping[str, Any]: ...
    def on_episode_start(self, agent_ids: Iterable[str]) -> None: ...
    def on_episode_end(self) -> None: ...
```

```python
# townlet/ports/telemetry.py
from typing import Protocol, Any, Mapping

class TelemetrySink(Protocol):
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def emit_event(self, name: str, payload: Mapping[str, Any] | None = None) -> None: ...
    def emit_metric(self, name: str, value: float, **tags: Any) -> None: ...
```

> **Note:** These are **templates**. Replace with the **minimum** that the sim truly needs after your codebase scan.

---

### Factory/Registry Pattern (example)

```python
# townlet/factories/registry.py
from collections.abc import Callable

REGISTRY: dict[str, dict[str, Callable[..., object]]] = {
    "world": {},
    "policy": {},
    "telemetry": {},
}

def register(kind: str, key: str):
    def inner(fn: Callable[..., object]):
        REGISTRY.setdefault(kind, {})[key] = fn
        return fn
    return inner

class ConfigurationError(RuntimeError): ...
```

```python
# townlet/factories/world_factory.py
from .registry import REGISTRY, ConfigurationError
from townlet.ports.world import WorldRuntime

def create_world(cfg) -> WorldRuntime:
    key = (cfg.world.kind if hasattr(cfg, "world") else "default")
    try:
        ctor = REGISTRY["world"][key]
    except KeyError as exc:
        raise ConfigurationError(f"Unknown world kind: {key}") from exc
    return ctor(cfg)
```

* Mirror for `policy_factory.py` and `telemetry_factory.py`.
* In each adapter module, add decorators like:

  ```python
  @register("world", "default")
  def build_default_world(cfg) -> WorldRuntime: ...
  ```

---

### Refactor the Composition Root

* Locate the run entrypoint (CLI or `main()`).
* Replace direct imports/instantiation of concrete classes with:

  ```python
  world = create_world(cfg)
  policy = create_policy(cfg)
  telemetry = create_telemetry(cfg)
  ```

* Ensure the loop only references `WorldRuntime`, `PolicyBackend`, `TelemetrySink`.

---

### Testing Plan

* **tests/test_ports_minimum.py** — ensure dummy implementations satisfy Protocol expectations (via behaviour, not `isinstance`).
* **tests/test_factories.py** — known keys produce objects implementing the right Protocol; unknown key raises `ConfigurationError`.
* **tests/test_sim_smoke.py** — run a few ticks with dummies through the real loop.
* **tests/test_sim_adapters_smoke.py** — guarded smoke test that wires real adapters for 1–2 ticks (mark as slow if needed).

---

### Coding Standards

* Python ≥ 3.11.
* Type‑annotate public surfaces; run `mypy` in strict (or project default).
* `ruff` clean for new files; keep functions short; one responsibility per module.
* Docstrings on all interfaces + factories (Google or NumPy style, be consistent with repo).

---

### Git Hygiene

* Branch: `feature/wp1-ports-and-factories`.
* Squash into a logical series:

  1. add ports; 2) add registry+factories; 3) add adapters; 4) refactor composition root; 5) tests+docs.
* PR title: **WP1: Ports & Factories (World/Policy/Telemetry) + Composition Root Refactor**
* PR description: rationale (decoupling), interface tables, config sample, test summary.

---

### Sanity Checks Before You Finish

* Simulation loop imports **only** from `townlet.ports.*` and factory modules, never concrete classes.
* At least one real adapter per port is registered as `"default"`.
* `pytest -q` runs the new tests; smoke tests pass locally.
* `ruff`/`mypy` clean for new/changed code.
* Docs updated with the new architecture touchpoints.

---

### If You Encounter Unknowns

* Prefer inferring from usage. If two call sites want conflicting signatures, adapt the adapter layer; keep the **port** clean and minimal.
* If an interface method is only for telemetry or only for training, don’t leak it into unrelated ports.
* Avoid import cycles by keeping ports independent of concrete implementations and factories.

---

**Proceed to implement Work Package 1 now.**
