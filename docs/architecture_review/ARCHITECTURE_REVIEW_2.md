# Townlet — Master Architectural Report

*(Consolidated from four prior reviews)*

**Document intent.** This master report merges and reconciles the four architectural analyses you provided, normalising overlapping findings and highlighting any discrepancies. Where the sources disagree (e.g., file sizes), I note ranges and assumptions, and tag key claims with **Words of Estimative Probability (WEP)** such as *Almost certain*, *Likely*, etc.

---

## 0) TL;DR – Where we actually are (and what to do next)

* **State:** A well‑intended, provider‑driven simulation loop sits atop **several god‑objects** (notably *WorldState/Grid*, *TelemetryPublisher*, *ObservationBuilder*, *StabilityMonitor*) and **loosely typed dict‑heavy contracts**. Quality gates are currently red. **Grade: C / C+ (borderline).** *(Likely)*
* **Top risks:**

  1. **Unsafe serialisation via `pickle.loads`** for RNG/snapshots → potential RCE if payloads are untrusted. *(Almost certain)*
  2. **Monoliths** with E/F complexity impede change; defects are hard to localise. *(Almost certain)*
  3. **Type hygiene** (mypy hundreds of errors) + **optional deps in tests** break CI and mask regressions. *(Almost certain)*
* **Immediate actions (this week):**

  * Replace/guard `pickle` RNG serialisation; add integrity checks. *(Almost certain)*
  * Gate Torch‑dependent tests with `pytest.importorskip("torch")`; exercise stub providers. *(Almost certain)*
  * Patch/ignore known dependency CVEs or pin within tooling venv; remove `assert` for control flow. *(Likely)*
* **One‑month arc:** Introduce **DTOs** (typed payloads) for telemetry/observations; **split TelemetryPublisher** and **decompose policy trainer**; enforce **incremental CI gates** (mypy/ruff/bandit/pip‑audit). *(Likely)*
* **One‑quarter arc:** **Break WorldState** into bounded services; **pipeline‑ise ObservationBuilder**; pursue **mypy --strict** for refactored seams. *(Likely)*

---

## 1) Executive Summary

### Current architecture (short)

A **`SimulationLoop`** resolves world/policy/telemetry providers from registries each tick, orchestrating: console → world runtime → rewards → observations → telemetry → stability/promotion → snapshots. This preserves pluggability at the edges but **exposes dict‑shaped payloads internally**, leaking concrete world details into telemetry, policy, rewards and stability. *(Almost certain)*

### Strengths

* **Provider registries + protocols** enable optional deps (Torch/httpx) to degrade gracefully. *(Almost certain)*
* **World adapter / façade** concept exists; clean‑architecture intent is evident in docs and adapters. *(Likely)*
* **Snapshotting** spans world/RNG/telemetry, aiding recovery and reproducibility. *(Likely)*

### Weaknesses

* **God‑objects**: *TelemetryPublisher*, *World grid/state*, *ObservationBuilder*, *StabilityMonitor.track* host multiple concerns and heavy mutable state. *(Almost certain)*
* **Untyped boundaries**: pervasive `dict[str, object]`/`Iterable[Mapping[str, object]]` erode substitution safety and static assurance. *(Almost certain)*
* **Quality posture**: mypy errors (≈**482+**), ruff ≈**1.2–1.3k** issues, failing pytest if ML extras absent, bandit **medium** on `pickle.loads`. *(Almost certain)*

**Overall assessment:** **C (trending C+)** — sound skeleton with poor interior ergonomics and guardrails. *(Likely)*

---

## 2) Evidence & Metrics (reconciled)

| Area                 | Observation                                                                                                                                                                                                                                                                  | Confidence (WEP)                          |
| -------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------- |
| **Size/shape**       | ~**26,940 LOC / 22,023 SLOC / 16,932 LLOC**, **147** modules; comment density ~**2–3%**; avg cyclomatic **A (≈3.2)** with D/E/F hotspots.                                                                                                                                    | *Almost certain*                          |
| **Hot files (SLOC)** | `telemetry/publisher.py`: **~400–2,006** (range due to helpers / measurement scope); `world/grid.py`: **~1,353–1,647**; `observations/builder.py`: **~904**; `console/handlers.py`: **~1,163**; `policy/training_orchestrator.py`: **~861**; `snapshots/state.py`: **~557**. | *Likely* (counts vary by revision & tool) |
| **Type quality**     | `mypy` errors **≥482** across ~60–70 files; strict mode not passing for core packages.                                                                                                                                                                                       | *Almost certain*                          |
| **Lint**             | `ruff` ~**1,254** issues (import order, unused ignores, style).                                                                                                                                                                                                              | *Almost certain*                          |
| **Tests**            | Pytest discovers **~600** items; fails during collection if Torch missing; unknown marker warnings.                                                                                                                                                                          | *Almost certain*                          |
| **Security**         | **`pickle.loads`** on RNG/snapshots (RCE risk if untrusted); asserts used for logic; `random.Random` flagged (acceptable for simulation if documented).                                                                                                                      | *Almost certain*                          |
| **Perf hotspots**    | Observation encoding O(n·r²)‑ish patterns; world action handling deeply branched; telemetry backpressure partly opaque.                                                                                                                                                      | *Likely*                                  |

*Normalisation note:* differing SLOC figures stem from whether helper modules and generated code are counted, and from snapshots of the code at slightly different times. Treat upper bounds as the safer planning reference. *(Likely)*

---

## 3) Architectural Analysis

### 3.1 Patterns used (the good bits)

* **Provider/registry pattern** with **Protocol** interfaces for world/policy/telemetry; **stubs** for optional deps. *(Almost certain)*
* **Adapters** (world runtime adapter) provide read‑only views—consistent with Clean Architecture. *(Likely)*
* **Snapshot/migration** centralises persistence and state identity. *(Likely)*

### 3.2 Anti‑patterns (the pain points)

* **God‑objects**: TelemetryPublisher, WorldState/Grid, ObservationBuilder; **long methods** (e.g., `run_ppo`, `StabilityMonitor.track`). *(Almost certain)*
* **Dict‑shaped contracts** across boundaries → type unsafety and wide ripple on change. *(Almost certain)*
* **Concrete coupling**: SimulationLoop knows about transport workers, world internals, training flows. *(Likely)*
* **Error handling**: `try/except/pass` and `assert` used for control flow. *(Likely)*

### 3.3 Coupling & flow

Despite registry abstraction at construction time, **runtime coupling** remains tight through **shared mutable state** and **raw structure access** (e.g., telemetry peeking into world internals), which hampers replaceability and parallel development. *(Almost certain)*

---

## 4) Quality & Security Posture

* **Typing:** Introduce **narrow interfaces** + **DTOs**; aim for **package‑by‑package strictness** rather than big‑bang. *(Almost certain)*
* **Testing:** Reduce reliance on fully constructed `SimulationLoop` in unit tests; **prefer service seams**. *(Likely)*
* **Security:** Replace or gate `pickle`; log and **fail closed** on malformed snapshot inputs; mark non‑crypto RNG use in docs and code comments (`# nosec` with rationale). *(Almost certain)*
* **Tooling:** Turn red gates green via staged thresholds (see §7). *(Almost certain)*

---

## 5) Strategic Target Architecture (end‑state we’re steering toward)

**Layered modules with typed seams:**

```
[ Domain ]  -> pure models (WorldSnapshot, ObservationDTO, RewardBreakdown, TelemetryEvent)
     ↑
[ App Services ] -> WorldService, ObservationService, TelemetryService, PolicyService, RewardService
     ↑
[ Infrastructure ] -> Transports, Persistence, Torch-backed trainers, HTTP, Console, UI, etc.
```

* **Dependencies flow inwards**; **registries return services**, not concrete mega‑classes. *(Likely)*
* **All cross‑module payloads** are **DTOs**, not `dict[str, object]`. *(Almost certain)*
* **Adapters** expose **read‑only** views of world state to policy/telemetry/observations/stability. *(Likely)*

*Confidence:* *Likely*. This aligns with all four reports and provides the seams required for safe evolution.

---

## 6) Tactical Plan (what to change and how)

### 6.1 Security first (P0)

* **RNG & snapshot serialisation**

  * Replace `pickle.loads` with **versioned JSON** (or msgpack) schema: `{"ver":1,"algo":"mt19937","state":[int,...]}`; base64 if needed.
  * Validate length/types; **reject unknown versions**; document trust boundary.
  * Provide **one‑shot migrator** for legacy snapshots. *(Almost certain)*

### 6.2 Shrink the god‑objects (P0/P1)

* **TelemetryPublisher → 4 services**
  `TelemetryAggregator`, `TransformPipeline`, `TransportManager`, `ConsoleGateway`; tiny façade implements `TelemetrySinkProtocol`.
  Surface **backpressure metrics** (“queued”, “dropped”, “retries”). *(Likely)*

* **WorldState/Grid → bounded contexts**
  Extract `AffordanceService`, `EmploymentService`, `EconomyService`, `RelationshipService`, `QueueService`.
  *WorldState* becomes a container and state holder; *WorldRuntime* dispatches via **ActionHandler** registry. *(Likely)*

* **ObservationBuilder → feature pipelines**
  Separate **map**, **social**, **landmarks/caches**; compose per variant (compact/hybrid/full). *(Likely)*

* **StabilityMonitor.track → analyzers**
  `FairnessAnalyzer`, `StarvationAnalyzer`, `RivalryAnalyzer`, `RewardVarianceAnalyzer`, `OptionThrashAnalyzer`. *(Likely)*

### 6.3 Type safety & contracts (P1)

* Introduce **DTOs** for externalised payloads and phase out raw dicts. Example sketch (Pydantic v2):

```python
from pydantic import BaseModel
from typing import Literal, List, Dict

class TelemetryEvent(BaseModel):
    tick: int
    kind: Literal["kpi","narrative","agent_metric"]
    data: Dict[str, float]  # narrow per event kind in follow-up models

class ObservationDTO(BaseModel):
    agent_id: str
    map: List[int]        # or ND array wrapper
    social: Dict[str, float]
    variant: Literal["compact","hybrid","full"]
```

*(Likely)*

### 6.4 Policy & tests (P1)

* **PolicyTrainingOrchestrator → strategies** (`BCTrainer`, `PPOTrainer`, `AnnealManager`).
* In tests, **`pytest.importorskip("torch")`**; prefer provider stubs; remove direct `import torch` in helpers. *(Almost certain)*

### 6.5 Config slimming (P1/P2)

* Move domain defaults/validators **into domain models**; keep `SimulationConfig` as composer/orchestrator only. *(Likely)*

---

## 7) CI Gates & Ratcheting Plan (keep us honest)

| Gate                 |                                           Week 1 |                         Week 4 |                                          Quarter |
| -------------------- | -----------------------------------------------: | -----------------------------: | -----------------------------------------------: |
| **mypy**             | Pass in `townlet.core`, `world.runtime` (strict) |  + `telemetry`, `observations` | **Strict** on refactored pkgs; error budget ≤ 50 |
| **ruff**             |                  `--select I,F,E,W` with `--fix` |                    Add `UP, B` |           Full ruleset (excluding optional perf) |
| **pytest**           |     Green without Torch; Torch tests **skipped** |      Torch tests run in ML job |                Coverage ≥ 70% on refactored pkgs |
| **bandit/pip‑audit** |                          No **medium+** findings | No **low+** in refactored pkgs |                       Zero **medium+** repo‑wide |
| **import‑linter**    |                     Enforce `config -> !runtime` | Add package boundaries per ADR |                 Hard fail on boundary violations |

*(Likely)*

---

## 8) Phased Roadmap (one page)

### Phase 0 — **Immediate (This Week)**

* Replace RNG `pickle` serialisation; add schema + validation + migrator.
* Gate Torch tests; register pytest markers; fix CI to **green baseline**.
* Upgrade or isolate CVE‑flagged dependencies; remove `assert` for flow control.
  **Exit criteria:** CI green without ML; **zero medium** bandit; snapshot load rejects malformed input. *(Almost certain)*

### Phase 1 — **Short‑term (Next Month)**

* Introduce **DTOs** for telemetry/observations; update protocols and adapters.
* Split **TelemetryPublisher** into aggregator/transform/transport/console; expose backpressure metrics.
* Policy trainer → strategies; tests rely on stubs; coverage for strategy seams.
  **Exit criteria:** mypy strict passes for `core`, `telemetry`, `policy` strategies; ruff baseline clean in refactored pkgs. *(Likely)*

### Phase 2 — **Medium‑term (Next Quarter)**

* **WorldState decomposition** (start with `QueueService`, `EmploymentService`); `ActionHandler` registry.
* **Observation pipelines** (map/social/landmarks) and simple perf harness.
* **Stability analyzers** extracted; promotion logic consumes analyzer outputs.
  **Exit criteria:** mypy strict passes for refactored world/obs/stability; targeted perf tests stable or faster for baseline scenarios. *(Likely)*

### Phase 3 — **Long‑term (Next Year)**

* Clean Architecture enforced with **import‑linter** rules; plugin surface for transports/policies.
* Consider **async/streaming** telemetry & vectorised observation hot paths.
* ADRs + generated API docs; onboarding guide updated.
  **Exit criteria:** boundaries enforced in CI; docs live; performance headroom demonstrated at target population scale. *(Even chance)*

---

## 9) Workstreams, Effort & Dependencies

| Workstream                | Scope                                                  | Effort | Risk     | Dependencies        | Success metric                                                     |
| ------------------------- | ------------------------------------------------------ | -----: | -------- | ------------------- | ------------------------------------------------------------------ |
| **Secure serialisation**  | RNG/snapshot schema + migrator + docs                  |      S | Low      | None                | No bandit medium; malformed inputs rejected                        |
| **Telemetry split**       | 4 components + metrics                                 |      L | Med‑High | DTOs exist          | mypy strict; backpressure metrics visible; fewer >200‑line methods |
| **World services**        | Queue/Employment/Economy/Relationships + ActionHandler |     XL | Med      | Tests & adapters    | Complexity drop; unit seams exist; loop unaware of internals       |
| **Observation pipelines** | Map/Social/Cache modules + DI                          |      L | Med      | DTOs, world adapter | Per‑agent CPU time flat or down; mypy strict                       |
| **Policy strategies**     | BC/PPO/Anneal separated; torch‑gated tests             |      M | Med      | None                | CI green both with/without ML; trainer methods <100 LOC            |
| **Stability analyzers**   | 5 analyzers + composer                                 |      M | Med      | DTOs, telemetry     | Each analyzer unit‑tested; E‑grade method retired                  |
| **Type & lint ratchet**   | Mypy/ruff on refactored pkgs                           |      M | Low      | All streams         | Error budgets met; no new dict‑shaped APIs                         |

*(Effort: S/M/L/XL ≈ days/1–2 weeks/2–3 weeks/4+ weeks for a small team.)* *(Likely)*

---

## 10) Traceability — Issues → Recommendations → Roadmap

| Issue (P0–P3)                      | Recommendation                                          | Phase   |
| ---------------------------------- | ------------------------------------------------------- | ------- |
| `pickle.loads` RCE risk (P0)       | Versioned JSON/msgpack schema, validation, migrator     | **0**   |
| Monolithic TelemetryPublisher (P1) | Split into Aggregator/Transform/Transport/Console; DTOs | **1**   |
| Dict‑typed contracts (P1)          | Introduce DTOs; mypy strict on seams                    | **1–2** |
| WorldState god‑object (P1)         | Bounded services + ActionHandler registry               | **2**   |
| Observation complexity (P2)        | Feature pipelines + caching                             | **2**   |
| Stability E‑grade (P1)             | Analyzer components + composer                          | **2**   |
| Torch coupling in tests (P0)       | `importorskip`, provider stubs, strategy split          | **0–1** |
| Config mega‑class (P2)             | Move validators/defaults into domain models             | **1–2** |

---

## 11) Example Interfaces (concrete enough to code against)

```python
from typing import Protocol, Iterable, Sequence
from pydantic import BaseModel

class RewardBreakdown(BaseModel):
    tick: int
    agent_id: str
    components: dict[str, float]
    total: float

class WorldSnapshot(BaseModel):
    tick: int
    agents: list[str]
    queues: dict[str, int]
    # …extend with strictly typed submodels over time…

class ObservationService(Protocol):
    def build(self, snapshot: WorldSnapshot, agents: Sequence[str]) -> list["ObservationDTO"]: ...

class TelemetrySink(Protocol):
    def publish(self, events: Iterable["TelemetryEvent"]) -> None: ...
```

These replace `Mapping[str, object]` at boundaries and let `mypy --strict` pull its weight. *(Likely)*

---

## 12) Documentation & Governance

* **ADRs to author:**

  1. *Safe serialisation for RNG/snapshots*;
  2. *Typed DTO boundary for cross‑module payloads*;
  3. *Telemetry pipeline decomposition*;
  4. *World bounded contexts & ActionHandler*;
  5. *Stability analyzer model*;
  6. *Import‑linter contracts*. *(Likely)*

* **Docs to update:** Architecture overview; developer guide (testing w/ and w/o ML); telemetry backpressure semantics; performance profiling harness usage. *(Likely)*

---

## 13) Known Discrepancies Across Source Reports (for the record)

* **TelemetryPublisher SLOC** varies widely (≈400 vs ≈1,000+ vs 2,006). This appears to be a **scope/tooling artefact** (helpers counted vs not; different commit snapshots). The qualitative conclusion (it’s a god‑object) **still stands**. *(Likely)*
* **World grid SLOC** reported as 1,353 and 1,647. Treat **~1.6k** as planning upper bound. *(Likely)*
* **Mypy errors**: “extensive” vs “482”. Plan to **ratchet from the measured baseline** in CI rather than chase a moving absolute. *(Almost certain)*

---

## 14) Glossary (short)

* **DTO:** Data Transfer Object—explicit, typed payload contract across module boundaries.
* **God‑object:** Class with many unrelated responsibilities and broad mutable state.
* **ActionHandler:** Strategy for a single world action kind (move/chat/request/etc.).
* **Backpressure:** When telemetry throughput exceeds transport capacity; queueing/dropping/retrying behaviour must be observable.

---

## 15) Confidence & Assumptions (WEP)

* **Accuracy of structural findings:** *Almost certain* — all four reports converge on the same pain points.
* **Specific metrics (SLOC counts, error tallies):** *Likely* — small disagreement exists between sources; ranges provided.
* **Feasibility of staged refactor without big‑bang rewrite:** *Likely* — registry/adapters provide enough seams to proceed incrementally.
* **Performance neutrality of refactors:** *Even chance* — decomposition may first add overhead before enabling optimisation; hence perf harness in Phase 2.

---

### Closing note

In short: the **shape** of the architecture is right; the **seams** are not. Put DTOs at the boundaries, slice up the god‑objects, secure serialisation, and ratchet the gates. Your SimulationLoop will finally be coordinating services rather than wrestling a hydra.
