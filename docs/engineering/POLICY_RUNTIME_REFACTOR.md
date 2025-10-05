# Policy Runtime Refactor Summary

## Current Topology

- ``townlet.policy.behavior_bridge.BehaviorBridge`` encapsulates behavior selection, option commits, and anneal blending.
- ``townlet.policy.trajectory_service.TrajectoryService`` manages per-agent transition buffers, trajectory accumulation, and reward rollups.
- ``townlet.policy.training_orchestrator.PolicyTrainingOrchestrator`` owns PPO/BC/anneal loops, promotion manager integration, and logging.
- ``townlet.policy.runner.PolicyRuntime`` coordinates behavior bridge, trajectory service, and export-facing APIs for the simulation loop.

## Usage Guidelines

- Simulation loop callers should depend on ``PolicyRuntime`` only; internal services remain implementation details.
- Training and CLI flows should instantiate ``PolicyTrainingOrchestrator``; ``TrainingHarness`` is a compatibility alias and will be removed in a future release.
- Monitoring code (tests, debugging scripts) should consume ``policy.transistions`` / ``policy.trajectory`` properties rather than private attributes.

## Outstanding Work (Milestone M3 Phase 4)

- Document public methods with docstrings and ensure ``PolicyRuntime`` exposes only supported accessors.
- Audit downstream code for legacy imports (``TrainingHarness``) and migrate to ``PolicyTrainingOrchestrator`` or ``policy.runner`` as appropriate.
- Expand targeted tests to cover orchestrator functions (BC, PPO, anneal) via unit-level mocks and CLI smoke tests.
- Update ``docs/engineering/WORLDSTATE_REFACTOR.md`` with final module layout and migration notes for external integrators.
