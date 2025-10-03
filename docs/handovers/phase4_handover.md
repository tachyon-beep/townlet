Phase 5 Handover Notes
=========================

Scope
-----
Configurable runtime: set config.affordances.runtime and reload via SimulationLoop/WorldState (files: src/townlet/config/loader.py, src/townlet/core/sim_loop.py, src/townlet/world/grid.py)\nDefault runtime instrumentation/options accessible for telemetry/tooling (src/townlet/world/affordances.py)\nScenario helpers log synthetic affordance stubs (src/townlet/policy/scenario_utils.py)\nRuntime inspector CLI scripts/inspect_affordances.py plus tests/runtime_stubs.py tests/test_affordance_runtime_config.py\nDocs updated: docs/design/AFFORDANCE_RUNTIME.md, docs/engineering/IMPLEMENTATION_NOTES.md, audit/WORK_PACKAGES.md\nTest matrix: tests/test_affordance_runtime_config.py, tests/test_affordance_manifest.py, tests/test_reward_engine.py, tests/test_rollout_capture.py, tests/test_training_replay.py\n

Verification
------------
- pytest tests/test_affordance_runtime_config.py
- pytest tests/test_affordance_manifest.py tests/test_reward_engine.py
- pytest tests/test_rollout_capture.py tests/test_training_replay.py

Follow-Up
---------
- Monitor runtime instrumentation uptake; revisit TODO-AFF-001 once schema updates scheduled.
- Future work: TLS transport (WP-102), console auth (WP-101) remain open.
