## Prompt: *Implement Work Package 3 — Typed DTO Boundary for Telemetry & Observations*

**Role:** You are an autonomous coding agent contributing to **Townlet**. Implement **WP3**: replace dict-shaped cross-module payloads with typed DTOs so the simulation loop, world package, policy adapters, and telemetry pipeline exchange structured models. This work builds on WP1 (ports/factories) and WP2 (modular world). Backwards compatibility is **not** required (pre-1.0).

> **Read first (in repo):**
>
> * `docs/architecture_review`
> * `docs/architecture_review/ADR/ADR-001 - Port and Factory Registry.md`
> * `docs/architecture_review/ADR/ADR-002 - World Modularisation.md`
> * `docs/architecture_review/ARCHITECTURE_REVIEW_2.md` (sections on DTOs & telemetry split)
> * Current observation builder (`src/townlet/observations/builder.py`), telemetry aggregator/publisher, and snapshot manager.

**High-level goal:** Introduce a **`townlet.dto`** module containing Pydantic models (or dataclass equivalents) for world snapshots, observation payloads, rewards, and telemetry events. Update the ports from WP1, the world façade from WP2, the telemetry sink, and the simulation loop so **only DTOs cross module boundaries**. Downstream adapters may still convert to dicts for legacy consumers, but all internal APIs become typed.

---

### Deliverables (Definition of Done)

1. **DTO Package (`townlet/dto/`)**

   * Create `townlet/dto/` with at minimum:

     ```
     townlet/dto/
       __init__.py
       world.py          # WorldSnapshot, AgentSummary, QueueSnapshot, etc.
       observations.py   # ObservationDTO, ObservationMetadata, ObservationBatch
       rewards.py        # RewardBreakdown, RewardComponent
       telemetry.py      # TelemetryEventDTO, TelemetryMetadataDTO, ConsoleEventDTO, etc.
     ```

   * Use **Pydantic v2 `BaseModel`** (preferred) with type hints from the architecture review (e.g., `Literal["compact","hybrid","full"]` for variants, `numpy.ndarray` support via `pydantic_numpy`). If Pydantic integration proves heavy, a `dataclasses.dataclass` + manual validation is acceptable; document choice in the ADR.
   * Ensure models support `.model_dump()` to provide legacy dictionaries for downstream transports.

2. **Port Contract Upgrade (WP1 alignment)**

   * Update `townlet/ports/world.py` so `WorldRuntime.snapshot()` returns `WorldSnapshot` (new DTO) and `observe()` returns `ObservationBatchDTO`, not raw mappings.
   * Update `townlet/ports/policy.py` method signatures to consume DTOs where appropriate (e.g., `decide(observations: ObservationBatch) -> ActionMapDTO` if defined, otherwise maintain mapping but document typed alias).
   * Update `townlet/ports/telemetry.py` so `TelemetrySink.emit_event/emit_metric` accept DTOs; add a `publish_events(events: Iterable[TelemetryEventDTO])` convenience as needed.
   * Regenerate WP1 dummy implementations (`townlet/testing/dummies.py`) to satisfy the refined interfaces via structural typing.

3. **World Façade Integration (depends on WP2)**

   * Modify `townlet/world/context.py` (from WP2) so:
     * `snapshot()` returns `WorldSnapshot` assembled from segregated modules.
     * `observe()` builds `ObservationBatchDTO` using helper functions in `townlet/dto/observations.py`.
   * Move any dict assembly logic from the façade into DTO constructors/helpers for clarity.

4. **Observation Pipeline Rewrite**

   * Refactor `src/townlet/observations/builder.py` to emit DTO instances:
     * Provide functions like `build_observation_dto(agent_id, features, map_tensor, metadata)` returning `ObservationDTO`.
     * Replace the existing `dict[str, dict[str, np.ndarray]]` return with `ObservationBatchDTO` (mapping agent → DTO).
   * Add validation to ensure metadata (landmarks, social context) uses typed sub-models instead of raw dicts.
   * Update any direct consumers (policy backends, tests) to work with the DTO API.

5. **Telemetry Pipeline DTO Adoption**

   * Update `townlet/telemetry/aggregation/collector.py` and `aggregation/aggregator.py` to produce `TelemetryEventDTO` instances.
   * Update transforms (`telemetry/transform/*.py`), transport (`telemetry/transport.py`), and publisher to accept DTOs and only call `.model_dump()` at the transport boundary.
   * Replace ad-hoc dict return values (e.g., `latest_queue_metrics`, `latest_reward_breakdown`) with typed DTOs accessible via the telemetry sink interface; convert to dict lazily for console/export code.
   * Ensure console history and manual narration use dedicated DTOs so `TelemetrySink` no longer exposes dict-shaped helpers.

6. **Simulation Loop & Snapshot Manager Updates**

   * Modify `src/townlet/core/sim_loop.py` (or successor) so internal orchestration uses DTOs end-to-end:
     * `ObservationBuilder.build_batch()` returns DTOs consumed by policy backends.
     * Rewards and telemetry payloads leverage typed models when interacting with factories/ports.
   * Update snapshot persistence (`src/townlet/snapshots/state.py`) to serialise/deserialise via DTOs where possible, falling back to dicts only when writing JSON.

7. **Compatibility Adapters**

   * Provide helper functions (e.g., `dto_to_legacy_observation(dto: ObservationDTO) -> dict[str, object]`) for modules not yet refactored. Keep adapters close to the consumer to avoid leak-back into the DTO core.
   * Deprecate or delete redundant schema-normalisation code once DTOs guarantee shape (e.g., simplify `normalize_snapshot_payload`).

8. **Tests**

   * Add unit tests for DTO validation (invalid payloads rejected, optional fields default). Target directories:
     * `tests/dto/test_world_snapshot.py`
     * `tests/dto/test_observations.py`
     * `tests/dto/test_telemetry.py`
   * Update existing observation and telemetry tests to assert DTO usage (e.g., `isinstance(observation, ObservationDTO)`).
   * Add integration smoke covering:
     * Simulation loop running 2 ticks with dummy providers, verifying telemetry events are DTO instances until the transport boundary.
     * Telemetry aggregator diffing logic producing `TelemetryEventDTO(kind="diff")`.
   * Ensure `mypy --strict townlet/dto` and `ruff check` pass; add targeted `pyproject.toml` overrides if needed.

9. **Docs & ADR**

   * Author `docs/architecture_review/ADR/ADR-003 - DTO Boundary.md` with:
     * Rationale for DTO introduction.
     * Table of new models, fields, and invariants.
     * Serialization strategy (`model_dump` at boundaries).
   * Update developer docs (e.g., `docs/architecture_review/ARCHITECTURE_REVIEW_2.md` summary table) and any quickstarts referencing observation or telemetry payloads.

10. **Sanity Checklist**

* Simulation loop, world façade, policy adapters, and telemetry sink exchange DTOs only.
* No module outside `townlet/dto` imports Pydantic directly except for DTO construction.
* Legacy dict helpers exist only at adapters/bridges explicitly marked for future removal.
* `pytest -q`, `ruff check src tests`, and `mypy src/townlet/dto.py src/townlet/telemetry src/townlet/observations` succeed.
* ADR-003 merged; WP1/WP2 docs updated to reference DTO expectations where needed.

---

### Method & Cut Plan (Do This In Order)

1. **Inventory Current Payload Shapes**
   * Trace observation dict structure (`ObservationBuilder.build_batch`) and telemetry snapshot payload (`StreamPayloadBuilder.build`) using fixtures to capture sample outputs.
   * Document fields + types to feed ADR-003 and DTO definitions.

2. **Create DTO Module & ADR Outline**
   * Draft ADR-003 with proposed DTO models.
   * Implement DTO classes with minimal helper methods (`from_legacy`, `to_legacy`).

3. **Upgrade Ports & Dummies**
   * Adjust WP1 ports + testing dummies to new DTO types.
   * Add compatibility shims (e.g., `support/legacy_observation.py`) for modules not migrated yet.

4. **Wire DTOs into World Façade (WP2 dependency)**
   * Update `WorldContext` to construct DTOs.
   * Ensure world submodules emit native Python structures convertible into DTO fields.

5. **Refactor Observation Builder**
   * Lift reusable metadata builders into `townlet/dto/observations.py`.
   * Ensure policy code still functions; update tests accordingly.

6. **Telemetry Pipeline Conversion**
   * Convert aggregator + transforms + publisher sequentially.
   * Update simulation loop interactions.
   * Ensure transports only see dicts when necessary (e.g., serialisation).

7. **Snapshot & Loop Integration**
   * Refactor snapshot manager to leverage DTO `.model_dump()` for persistence.
   * Update simulation loop to operate on DTOs and adjust reward engine/policy orchestrator as needed.

8. **Testing & Validation**
   * Run targeted unit tests, then full `pytest`.
   * Run `mypy --strict` on DTO package, fix issues.
   * Capture golden sample of telemetry event output for regression.

9. **Docs & Final Polish**
   * Finalise ADR-003, update WP docs to mention DTO requirement.
   * Add README snippet or dev guide entry explaining DTO usage for contributors.

---

**Proceed to implement Work Package 3 once WP1 & WP2 are merged.**
