# Townlet Architecture: Remaining Work

- WP-A: Core Protocol Definitions (Completed)
    Objective: capture exhaustive method contracts, payload schemas, and lifecycle hooks for WorldRuntime, PolicyBackend, and TelemetrySink.
    Key Tasks: draft protocol stubs with typing.Protocol; document data contracts; align with current loop calls for compatibility; socialize for review.
    Exit Criteria: protocols published with docstrings/tests; simulation loop references only protocol types (docs/architecture_review/townlet-target-architecture.md:23; src/townlet/core/sim_loop.py:112).
- WP-B: Bootstrap Factory & Descriptor Registry (Completed)
    Objective: land configuration-driven factories that resolve concrete implementations while handling missing optional dependencies gracefully.
    Key Tasks: design descriptor schema anchored in config loader; implement resolution with plugin discovery and stub fallbacks; cover error/telemetry paths.
    Exit Criteria: smoke simulation uses factories; pytest passes without ML extras; configuration docs updated (docs/architecture_review/townlet-target-architecture.md:39).
- WP-C: World Subsystem Modularization
    Objective: decompose world/grid.py into cohesive packages (agents, relationships, console, observation builders).
    Key Tasks: introduce WorldContext façade; migrate clusters iteratively with targeted unit tests; harden interface boundaries.
    Exit Criteria: legacy file <500 LOC; new modules own discrete responsibilities; façade satisfies protocol contract (docs/architecture_review/townlet-target-architecture.md:33; src/townlet/world/grid.py).
    Notes: Nightly upkeep now flows through `townlet.world.agents.nightly_reset.NightlyResetService`, and `WorldContext.apply_nightly_reset()` exposes the façade for downstream callers. Employment helpers delegate via the expanded `townlet.world.agents.employment.EmploymentService`; regression tests cover the delegation paths (`tests/test_world_nightly_reset.py`, `tests/test_world_employment_delegation.py`).
- WP-D: Telemetry Pipeline Refactor
    Objective: split telemetry into aggregation, transform, and transport layers with clear lifecycle management.
    Key Tasks: extract worker management; define event schemas; implement stdout/file adapters plus hooks for future sinks; add shutdown/backpressure tests.
    Exit Criteria: telemetry exposed through TelemetrySink; background workers managed via context managers; integration tests green (docs/architecture_review/townlet-target-architecture.md:58).
- WP-E: Policy Backend Abstraction
    Objective: isolate scripted vs. ML backends and provide optional extras for heavy stacks.
    Key Tasks: move training utilities into backend-specific modules; wire configuration selection; add stubs/skips when extras missing.
    Exit Criteria: policy selection is config-driven; scripted backend is default; pytest collects without torch (docs/architecture_review/townlet-target-architecture.md:53).
- WP-F: Config Loader Decomposition & Documentation
    Objective: align schemas with subsystem packages and improve developer guidance.
    Key Tasks: split loader into domain modules; add Field descriptions and docstrings; generate reference docs; ensure factories consume descriptors cleanly.
    Exit Criteria: config package acyclic; documentation reflects new structure; docstring coverage for config exceeds threshold (docs/architecture_review/townlet-target-architecture.md:39).
- WP-G: Quality Gate Ratchet & Observability Enhancements
    Objective: lock in lint/type/doc baselines and expand telemetry targets.
    Key Tasks: integrate tool gates into CI with ratcheting thresholds; reduce suppressions; add Prometheus/WebSocket transports using new telemetry layer; update developer handbook.
    Exit Criteria: CI enforces agreed thresholds; at least one new telemetry adapter runs in smoke tests; handbook covers architecture usage (docs/architecture_review/townlet-target-architecture.md:80; docs/architecture_review/townlet-architectural-analysis.md:12).

=== Remaining Work & Migration Notes

• Work Package 2B: Downstream Consumer Plan

  1. Inventory & Classification
      - Review each concrete consumer we flagged earlier:
          - src/townlet/console/handlers.py, console/service.py
          - src/townlet/snapshots/state.py
          - src/townlet/demo/runner.py
          - src/townlet/policy/training_orchestrator.py and policy/__init__.py
          - src/townlet_ui/dashboard.py (or API back-end if relevant)
          - CLI scripts under scripts/ (console_dry_run.py, promotion_drill.py, capture_rollout.py, etc.).
      - Categorize them by behaviour: read-only (needs type hints) vs. mutating (need fallback detection).
  2. Shared Utilities
      - Introduce helper predicates (e.g. is_stub_policy, is_stub_telemetry) exposed via townlet.core so consumers can check for reduced capability without importing stub classes directly.
      - Optionally extend registry to expose metadata (provider name in the resolved object) via SimulationLoop to avoid repeated isinstance.
  3. Console & Snapshot Update
      - Adjust console handlers/service so they import protocols from townlet.core and gracefully handle stub telemetry (e.g., skip commands requiring remote transport, present user-facing warning). Update type hints referencing TelemetryPublisher to
        TelemetrySinkProtocol.
      - In snapshots/state.py, gate telemetry import/export when sink is stubbed; ensure console buffer handling still works.
  4. Training Orchestrator & Policy Exports
      - Update training orchestrator to type against PolicyBackendProtocol and detect stub backend, e.g., logging that advanced training features are disabled.
      - Modify policy/__init__.py exports (or add new utility functions) so downstream imports use protocols rather than the concrete PolicyRuntime, while still exposing a compatibility interface for legacy users.
  5. Scripts & Demo Runner
      - Migrate scripts to import from townlet.core and check for stub providers before enabling features (e.g., instrumentation that expects telemetry transport).
      - Provide consistent CLI messaging (e.g., “Telemetry stub active; stream disabled”).
  6. UI / Gateway Integration
      - Ensure the UI gateway or API layer uses the protocols and surfaces stub status (e.g., disable certain panels, show fallback banner). If full integration is heavy, at minimum document current limitations and add logging.
  7. Testing
      - Add targeted tests per category (console, training, scripts) to verify behaviour with both default and stub providers. For scripts, lightweight unit tests or CLI smoke tests that patch fallback flags.
  8. Documentation & Migration Notes
      - Update relevant docs (console guide, training notes, UI docs) describing how to interpret stub warnings and how to enable full capability (install [ml], [api]).
      - Capture a migration checklist in engineering notes for teams touching these surfaces.
  9. Optional Enhancements
      - Consider exposing provider names via loop.policy_provider / loop.telemetry_provider properties so external tools (UI) can react without relying on type inspection.
      - Evaluate CI coverage to ensure minimal environments exercise these paths.
  
• Secondary consumers that still touch the concrete runtime/policy/telemetry types (and should migrate to the new protocols once factories land):

- src/townlet/console/handlers.py – optional imports for PolicyRuntime/TelemetryPublisher and router construction rely on the concrete classes.
- src/townlet/snapshots/state.py – snapshot restore helpers type‑hint TelemetryPublisher directly.
- src/townlet/demo/runner.py – demo harness instantiates TelemetryPublisher and expects the concrete API.
- src/townlet/policy/training_orchestrator.py – training loop reaches into loop.policy for trajectory capture and metadata.
- src/townlet/policy/__init__.py – re-exports PolicyRuntime, so downstream callers still grab the class rather than a protocol.
- src/townlet_ui/dashboard.py – UI wiring expects loop.policy/loop.telemetry attributes to be the current concrete implementations.
- Scripts in scripts/ (console_dry_run.py, promotion_drill.py, capture_rollout.py, capture_scripted.py, inspect_affordances.py, run_simulation.py, etc.) – all pass concrete loop.policy/loop.telemetry instances around.
- Test suites such as tests/test_console_dispatcher.py, tests/test_console_commands.py, tests/test_console_promotion.py, tests/test_policy_anneal_blend.py, tests/test_observer_ui_dashboard.py, and other telemetry/policy tests that construct or assume the concrete
    classes (useful to flag for later, even if lower priority).

  These are the main spots we’ll want to touch after WP‑A when we start swapping consumers over to protocol imports and, eventually, factory-produced instances.
