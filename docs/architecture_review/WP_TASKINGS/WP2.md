## Prompt: *Implement Work Package 2 — Modularise the World Subsystem (Townlet)*

**Role:** You are an autonomous coding agent contributing to the open‑source project **Townlet**. Your task is to implement **Work Package 2**: break up the monolithic *World* implementation into a cohesive, testable **world package** behind the `WorldRuntime` interface created in WP1. Backwards compatibility is **not** required (pre‑1.0).

> **Read first (in repo):**
>
> * `docs/architecture_review`
> * `docs/architecture_review/ADR/ADR-002 - World Modularisation.md`
> * The current world module(s), e.g. `world/grid.py` and anything it imports
> * The `townlet/ports/world.py` (or equivalent) from **WP1** defining `WorldRuntime`
> * The simulation loop/entrypoint that calls into the world

**High‑level goal:** Replace the single “god module” with a **package of small, cohesive modules** (domain‑driven) and expose a single façade (e.g. `WorldContext`) that **implements `WorldRuntime`**. The simulation loop must only touch the `WorldRuntime` interface, not internals.

---

### Deliverables (Definition of Done)

1. **New Package Layout**

   * Create `townlet/world/` with submodules. Treat this outline as a reference template: keep the façade, state, actions, observations, systems, events, and RNG slices; rename or omit supporting modules once you understand the real responsibilities.

     ```
     townlet/world/
       __init__.py
       context.py            # façade implementing WorldRuntime
       state.py              # world state store & lifecycle (reset/seed/snapshot)
       spatial.py            # grid/map, coordinates, neighbourhood queries
       agents.py             # agent registry, lifecycle (add/remove), attributes
       actions.py            # action schema, validation, application pipeline
       observe.py            # observations/views of the world for policies
       systems/
         __init__.py
         employment.py       # example “system” operating each tick
         relationships.py    # …
         economy.py          # …
       events.py             # domain events & hooks
       rng.py                # deterministic seeding & random helpers
       errors.py             # world-specific exceptions
     ```

   * Move **console/UI code** and any **telemetry outputs** out of world logic if currently embedded. World emits **domain events** only; orchestration or telemetry consumes them elsewhere.

2. **Façade (`WorldContext`) implementing `WorldRuntime`**

   * Implement `WorldContext` in `context.py`. It composes the submodules above and **only** exposes methods required by `WorldRuntime` (as defined in WP1), e.g.:

     * `reset(seed: int | None) -> None`
     * `tick() -> None`
     * `agents() -> Iterable[AgentId]`
     * `observe(agent_ids: Iterable[AgentId] | None) -> ObsMap`
     * `apply_actions(actions: ActionMap) -> None`
     * `snapshot() -> Mapping[str, Any]`
   * `WorldRuntime` is a `typing.Protocol`; inheritance is optional if `WorldContext` is structurally compatible.
   * Internals (systems, spatial grid, etc.) **must not** be imported by the simulation loop.

3. **Domain Separation**

   * Split responsibilities cleanly:

     * **`state.py`**: mutable state containers and lifecycle (`reset`, `load`, `snapshot`).
     * **`spatial.py`**: grid/coordinate maths, occupancy, pathing helpers.
     * **`agents.py`**: agent registry and metadata; zero knowledge of telemetry or policy.
     * **`actions.py`**: define action types, validation, and the apply pipeline (validate → resolve → mutate state → emit domain events).
     * **`observe.py`**: compute observations/views from state (no side effects).
     * **`systems/*`**: per‑tick domain systems (employment, relationships, etc.), each with a `step(state, context)` function. Systems can emit **domain events** via `events.py`.
     * **`events.py`**: event dataclasses and a minimal in‑process dispatcher (sync). WorldContext collects emitted events each tick for the orchestrator/telemetry.
     * **`rng.py`**: centralised RNG (e.g., `random.Random` or `numpy.random.Generator`) seeded in `reset` and passed where needed for determinism.
   * **No circular imports**: keep shared types in small leaf modules (e.g. `types.py` if necessary).

4. **Decouple from Non‑Domain Concerns**

   * Remove any direct imports of telemetry, CLI/console, HTTP, or ML/policy internals from world code.
   * World code must not log to external sinks directly; optional: use a lightweight logger for debug only.

5. **Adapter Integration**

   * If WP1 created an adapter for the old world class, replace it with `WorldContext` as the concrete implementation returned by `WorldFactory`.
   * Update the world factory registration, e.g.:

   ```python
   @register("world", "default")
   def build_default_world(cfg) -> WorldRuntime:
       return WorldContext.from_config(cfg)
   ```
   * Update existing configs, fixtures, and integration tests that referenced the legacy world module so they resolve the new factory + module paths.

6. **Tests**

   * **Unit tests** for each submodule:

     * `spatial`: neighbourhood queries, bounds, occupancy invariants.
     * `agents`: add/remove agents; uniqueness; retrieval.
     * `actions`: invalid actions rejected; valid actions mutate state correctly.
     * `observe`: observation shape/content stable for a known tiny world.
     * `systems`: each system’s `step` produces expected diffs/events.
     * `rng`: same seed ⇒ same tick sequence outcomes.
   * **Integration tests**:

     * A **golden 2–3 tick** run that asserts deterministic behaviour given a fixed seed (snapshot compare).
     * World emits expected **domain events**; events list is cleared between ticks.
   * Ensure existing **WP1 smoke test** (loop with dummies) still passes when using `WorldContext`.

7. **Docs**

   * Add or update `docs/architecture_review/ADR/ADR-002 - World Modularisation.md`:

     * ASCII module map diagram showing primary modules and relationships.
     * Tick pipeline: validate actions → systems step → state updates → events emitted → snapshot.
     * Event list (brief) and intended consumers.
     * Determinism & seeding policy.
   * Update any quickstart or developer docs showing the new world import path.

8. **Quality Gates**

   * New/changed files pass `ruff` and `mypy` for public surfaces.
   * Keep functions small and single‑purpose; docstrings on public classes/functions.
   * No import cycles; run a simple cycle detector if available (or enforce by structure).

---

### Method & Cut Plan (Do This In Order)

1. **Discover Current Responsibilities**

   * Grep/scan the old world module for responsibilities: spatial/grid maths, agent lifecycle, action handling, observation, per‑tick systems, console I/O, telemetry, seeding, persistence.
   * Write a short checklist mapping each responsibility → target module listed above.

2. **Introduce New Package Skeleton (no behaviour yet)**

   * Create files and public APIs with TODO bodies and type hints. Ensure imports compile.

3. **Move Pure Functions First**

   * Extract spatial helpers and observation builders (usually stateless) into `spatial.py` and `observe.py`.
   * Add tight unit tests for these now‑isolated bits.

4. **Carve Out State & Agents**

   * Build `state.py` (central store) and `agents.py`.
   * Replace global/module‑level state in the old code with `WorldState` owned by `WorldContext`.

5. **Action Pipeline**

   * Define action schemas (typed payloads), validators, and application hooks in `actions.py`.
   * Wire `WorldContext.apply_actions()` to call into this pipeline.

6. **Systems**

   * For each domain responsibility that mutates state each tick, create a `systems/<name>.py` with a `step(state, ctx)` function.
   * Compose an ordered list in `context.py` (e.g., `self._systems: list[Callable[[WorldState, WorldContext], None]]`).

7. **Events**

   * Introduce `Event` dataclasses in `events.py` and a tiny dispatcher. Systems/action pipeline push events; `WorldContext.tick()` returns/records them for the orchestrator.

8. **Determinism**

   * Implement `rng.py` and thread a single RNG through state changes that require randomness.
   * `reset(seed)` re‑creates RNG and re‑initialises state; assert reproducibility in tests.

9. **Delete/Migrate Old Code**

   * Gradually empty the old world module; leave a thin shim (optional) or remove it if unused.
   * Update imports, configs, and tests to point to the new `townlet/world` package and `WorldContext` factory registration.

10. **Polish & Document**

   * Tighten types, docstrings, ruff/mypy.
   * Ensure `docs/architecture_review/ADR/ADR-002 - World Modularisation.md` includes the ASCII module map diagram, pipeline narrative, and migration notes.

---

### Interface & Type Sketches (adjust to reality)

```python
# townlet/world/state.py
from dataclasses import dataclass, field
from typing import Any

@dataclass
class WorldState:
    tick: int = 0
    grid: "Grid" | None = None      # define in spatial.py
    agents: dict[str, "Agent"] = field(default_factory=dict)
    # add domain-specific state here
```

```python
# townlet/world/context.py
from typing import Iterable, Mapping, Any
from townlet.ports.world import WorldRuntime
from .state import WorldState
from . import actions, observe, events, systems, rng

class WorldContext:
    """Implements WorldRuntime via structural typing."""
    def __init__(self, state: WorldState) -> None:
        self.state = state
        self._rng = rng.make()
        self._systems = systems.default_pipeline()

    @classmethod
    def from_config(cls, cfg) -> "WorldContext":
        # build initial state from cfg
        return cls(WorldState())

    def reset(self, seed: int | None = None) -> None:
        self.state = WorldState()
        self._rng = rng.make(seed)

    def tick(self) -> None:
        for step in self._systems:
            step(self.state, self)  # may emit events
        self.state.tick += 1

    def agents(self) -> Iterable[str]:
        return self.state.agents.keys()

    def observe(self, agent_ids: Iterable[str] | None = None) -> Mapping[str, Any]:
        return observe.for_agents(self.state, agent_ids)

    def apply_actions(self, actions_map: Mapping[str, Any]) -> None:
        actions.apply(self.state, actions_map, rng=self._rng)

    def snapshot(self) -> Mapping[str, Any]:
        # compose a stable, serialisable view
        return {"tick": self.state.tick, "agents": len(self.state.agents)}
```

---

### Testing Strategy

* **Property/Determinism tests (optional but valuable):**

  * For a tiny world and fixed seed, running N ticks twice yields identical snapshots.
* **Action validity tests:**

  * Invalid action types/targets are rejected with clear exceptions; state unchanged.
* **Systems tests:**

  * Each system’s `step` creates expected state diffs and events (use small fixtures).
* **Integration (smoke):**

  * Construct `WorldContext` via factory, run 2–3 ticks with a scripted policy from WP1 dummies; assert no exceptions and event flow is sane.

---

### Constraints & Non‑Goals

* No telemetry, HTTP, or CLI code in `townlet/world/*`.
* Avoid introducing concurrency; keep the tick pipeline single‑threaded and deterministic.
* Do not expand the `WorldRuntime` interface unless absolutely necessary—prefer adapting internals to the existing port.

---

### Risks & Mitigations

* **Import cycles:** isolate shared types, and keep `context.py` as the only orchestrator that imports many submodules.
* **Hidden side effects in old code:** when moving functions, add tests that assert “no mutation” for helpers that should be pure.
* **Performance regressions:** keep hot loops in `spatial.py`; avoid per‑tick object churn; prefer preallocated structures where obvious.

---

### Git Hygiene

* Branch: `feature/wp2-world-modularisation`.
* Commit slices (suggested):

  1. package skeleton + types;
  2. move spatial/observe + tests;
  3. state/agents + tests;
  4. actions pipeline + tests;
  5. systems + events + tests;
  6. façade + factory wiring;
  7. remove old module + ADR.

---

### Sanity Checks Before You Finish

* Simulation loop depends **only** on `WorldRuntime`.
* `WorldContext` is the registered default world in the factory.
* No imports from telemetry/policy inside `townlet/world/*`.
* `pytest -q` passes; determinism tests pass with fixed seed.
* `ruff` and `mypy` clean for new/changed files.
* `docs/architecture_review/ADR/ADR-002 - World Modularisation.md` (with ASCII module map) matches the implemented package.

---

**Proceed to implement Work Package 2 now.**
