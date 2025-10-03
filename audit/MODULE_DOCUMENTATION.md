# Module Documentation

Generated automatically via static analysis of the repository. Each section summarises the structure and surface of an individual Python module.

## scripts/audit_bc_datasets.py

- **File path**: `scripts/audit_bc_datasets.py`
- **Purpose**: Audit behaviour cloning datasets for checksum and metadata freshness.
- **Dependencies**: stdlib [__future__, argparse, datetime, hashlib, json, pathlib, typing] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 161
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `load_versions(path: Path) -> Mapping[str, Mapping[str, object]]` — No docstring provided.
- `audit_dataset(name: str, payload: Mapping[str, object]) -> dict[str, object]` — No docstring provided.
- `audit_catalog(versions_path: Path) -> dict[str, object]` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- `DEFAULT_VERSIONS_PATH` = Path('data/bc_datasets/versions.json')
- `REQUIRED_VERSION_KEYS` = {'manifest', 'checksums', 'captures_dir'}

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/bc_metrics_summary.py

- **File path**: `scripts/bc_metrics_summary.py`
- **Purpose**: Summarise behaviour cloning evaluation metrics.
- **Dependencies**: stdlib [__future__, argparse, json, pathlib] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 52
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `load_metrics(path: Path) -> list[dict[str, float]]` — No docstring provided.
- `summarise(metrics: list[dict[str, float]]) -> dict[str, float]` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/benchmark_tick.py

- **File path**: `scripts/benchmark_tick.py`
- **Purpose**: Simple benchmark to estimate average tick duration.
- **Dependencies**: stdlib [__future__, argparse, pathlib, time] / third-party [None] / internal [townlet.config, townlet.core.sim_loop]
- **Related modules**: townlet.config, townlet.core.sim_loop
- **Lines of code**: 39
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `benchmark(config_path: Path, ticks: int, enforce: bool) -> float` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.core.sim_loop

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/capture_rollout.py

- **File path**: `scripts/capture_rollout.py`
- **Purpose**: CLI to capture Townlet rollout trajectories into replay samples.
- **Dependencies**: stdlib [__future__, argparse, datetime, json, pathlib, typing] / third-party [numpy] / internal [townlet.config.loader, townlet.core.sim_loop, townlet.policy.metrics, townlet.policy.replay, townlet.policy.scenario_utils]
- **Related modules**: townlet.config.loader, townlet.core.sim_loop, townlet.policy.metrics, townlet.policy.replay, townlet.policy.scenario_utils
- **Lines of code**: 140
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy
- Internal: townlet.config.loader, townlet.core.sim_loop, townlet.policy.metrics, townlet.policy.replay, townlet.policy.scenario_utils

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/capture_rollout_suite.py

- **File path**: `scripts/capture_rollout_suite.py`
- **Purpose**: Run rollout capture across a suite of configs.
- **Dependencies**: stdlib [__future__, argparse, pathlib, subprocess, sys, typing] / third-party [None] / internal [townlet.config.loader]
- **Related modules**: townlet.config.loader
- **Lines of code**: 112
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `run_capture(config: Path, ticks: int, output: Path, auto_seed: bool, agent_filter: str | None, compress: bool, retries: int) -> None` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config.loader

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/capture_scripted.py

- **File path**: `scripts/capture_scripted.py`
- **Purpose**: Capture scripted trajectories for behaviour cloning datasets.
- **Dependencies**: stdlib [__future__, argparse, collections, json, pathlib, typing] / third-party [numpy] / internal [townlet.config, townlet.core.sim_loop, townlet.policy.replay, townlet.policy.scenario_utils, townlet.policy.scripted]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.policy.replay, townlet.policy.scenario_utils, townlet.policy.scripted
- **Lines of code**: 135
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args(argv: List[str] | None = None) -> argparse.Namespace` — No docstring provided.
- `_build_frame(adapter: ScriptedPolicyAdapter, agent_id: str, observation: Dict[str, np.ndarray], reward: float, terminated: bool, trajectory_id: str) -> Dict[str, object]` — No docstring provided.
- `main(argv: List[str] | None = None) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy
- Internal: townlet.config, townlet.core.sim_loop, townlet.policy.replay, townlet.policy.scenario_utils, townlet.policy.scripted

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/console_dry_run.py

- **File path**: `scripts/console_dry_run.py`
- **Purpose**: Employment console dry-run harness.
- **Dependencies**: stdlib [__future__, pathlib, tempfile] / third-party [None] / internal [townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.snapshots, townlet.snapshots.state, townlet.world.grid]
- **Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.snapshots, townlet.snapshots.state, townlet.world.grid
- **Lines of code**: 129
- **Environment variables**: None detected

### Classes
- None

### Functions
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.snapshots, townlet.snapshots.state, townlet.world.grid

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/curate_trajectories.py

- **File path**: `scripts/curate_trajectories.py`
- **Purpose**: Filter and summarise behaviour-cloning trajectories.
- **Dependencies**: stdlib [__future__, argparse, dataclasses, json, pathlib, typing] / third-party [numpy] / internal [townlet.policy.replay]
- **Related modules**: townlet.policy.replay
- **Lines of code**: 104
- **Environment variables**: None detected

### Classes
- **EvaluationResult(object)** — No docstring provided.
  - Attributes:
    - `sample_path` (type=Path)
    - `meta_path` (type=Path)
    - `metrics` (type=Mapping[str, float])
    - `accepted` (type=bool)
  - Methods: None

### Functions
- `parse_args(argv: List[str] | None = None) -> argparse.Namespace` — No docstring provided.
- `_pair_files(directory: Path) -> Iterable[tuple[Path, Path]]` — No docstring provided.
- `evaluate_sample(npz_path: Path, json_path: Path) -> EvaluationResult` — No docstring provided.
- `curate(result: EvaluationResult, *, min_timesteps: int, min_reward: float | None) -> EvaluationResult` — No docstring provided.
- `write_manifest(results: Iterable[EvaluationResult], output: Path) -> None` — No docstring provided.
- `summarise(results: Iterable[EvaluationResult]) -> Mapping[str, float]` — No docstring provided.
- `main(argv: List[str] | None = None) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy
- Internal: townlet.policy.replay

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/demo_run.py

- **File path**: `scripts/demo_run.py`
- **Purpose**: Run a scripted Townlet demo with dashboard timeline orchestration.
- **Dependencies**: stdlib [__future__, argparse, pathlib, typing] / third-party [None] / internal [townlet.config, townlet.core.sim_loop, townlet.demo.runner, townlet.demo.timeline, townlet_ui.dashboard]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.demo.runner, townlet.demo.timeline, townlet_ui.dashboard
- **Lines of code**: 99
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `load_demo_timeline(path: Optional[Path]) -> DemoTimeline` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.core.sim_loop, townlet.demo.runner, townlet.demo.timeline, townlet_ui.dashboard

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/inspect_affordances.py

- **File path**: `scripts/inspect_affordances.py`
- **Purpose**: Inspect affordance runtime state from configs or snapshots.
- **Dependencies**: stdlib [__future__, argparse, contextlib, dataclasses, io, json, pathlib, typing] / third-party [None] / internal [townlet.config, townlet.core.sim_loop]
- **Related modules**: townlet.config, townlet.core.sim_loop
- **Lines of code**: 145
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `_normalise_running_payload(running: dict[str, Any]) -> dict[str, Any]` — No docstring provided.
- `inspect_snapshot(path: Path) -> dict[str, Any]` — No docstring provided.
- `inspect_config(path: Path, ticks: int) -> dict[str, Any]` — No docstring provided.
- `render_text(report: dict[str, Any]) -> str` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.core.sim_loop

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/manage_phase_c.py

- **File path**: `scripts/manage_phase_c.py`
- **Purpose**: Helper script to toggle Phase C social reward stages in configs.
- **Dependencies**: stdlib [__future__, argparse, pathlib, typing] / third-party [yaml] / internal [None]
- **Related modules**: None
- **Lines of code**: 164
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `load_config(path: Path) -> Dict[str, Any]` — No docstring provided.
- `ensure_nested(mapping: Dict[str, Any], keys: List[str]) -> Dict[str, Any]` — No docstring provided.
- `write_config(data: Dict[str, Any], *, output: Path | None, in_place: bool, source: Path) -> None` — No docstring provided.
- `handle_set_stage(args: argparse.Namespace) -> None` — No docstring provided.
- `parse_schedule_entries(entries: List[str]) -> List[Dict[str, Any]]` — No docstring provided.
- `handle_schedule(args: argparse.Namespace) -> None` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- `VALID_STAGES` = {'OFF', 'C1', 'C2', 'C3'}

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: yaml
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/merge_rollout_metrics.py

- **File path**: `scripts/merge_rollout_metrics.py`
- **Purpose**: Merge captured rollout metrics into the golden stats JSON.
- **Dependencies**: stdlib [__future__, argparse, json, pathlib] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 132
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `_load_metrics_from_dir(scenario_dir: Path) -> dict[str, dict[str, float]] | None` — No docstring provided.
- `_collect_input_metrics(root: Path, allow_template: bool) -> dict[str, dict[str, dict[str, float]]]` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- `DEFAULT_GOLDEN_PATH` = Path('docs/samples/rollout_scenario_stats.json')
- `METRICS_FILENAME` = 'rollout_sample_metrics.json'

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/observer_ui.py

- **File path**: `scripts/observer_ui.py`
- **Purpose**: Launch the Townlet observer dashboard against a local simulation.
- **Dependencies**: stdlib [__future__, argparse, pathlib] / third-party [None] / internal [townlet.config, townlet.core.sim_loop, townlet_ui.dashboard]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet_ui.dashboard
- **Lines of code**: 62
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.core.sim_loop, townlet_ui.dashboard

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/ppo_telemetry_plot.py

- **File path**: `scripts/ppo_telemetry_plot.py`
- **Purpose**: Quick-look plotting utility for PPO telemetry JSONL logs.
- **Dependencies**: stdlib [__future__, argparse, json, pathlib, typing] / third-party [matplotlib.pyplot] / internal [None]
- **Related modules**: None
- **Lines of code**: 101
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `load_entries(log_path: Path) -> list[dict[str, Any]]` — No docstring provided.
- `summarise(entries: list[dict[str, Any]]) -> None` — No docstring provided.
- `plot(entries: list[dict[str, Any]], show: bool, output: Path | None) -> None` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: matplotlib.pyplot
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/profile_observation_tensor.py

- **File path**: `scripts/profile_observation_tensor.py`
- **Purpose**: Profile observation tensor dimensions for a given config.
- **Dependencies**: stdlib [__future__, argparse, json, pathlib, statistics] / third-party [numpy] / internal [townlet.config, townlet.observations.builder, townlet.world]
- **Related modules**: townlet.config, townlet.observations.builder, townlet.world
- **Lines of code**: 112
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `bootstrap_world(config_path: Path, agent_count: int) -> tuple[WorldState, ObservationBuilder]` — No docstring provided.
- `profile(world: WorldState, builder: ObservationBuilder, ticks: int) -> dict[str, object]` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy
- Internal: townlet.config, townlet.observations.builder, townlet.world

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/promotion_drill.py

- **File path**: `scripts/promotion_drill.py`
- **Purpose**: Run a scripted promotion/rollback drill and capture artefacts.
- **Dependencies**: stdlib [__future__, argparse, json, pathlib, typing] / third-party [None] / internal [townlet.config, townlet.console.handlers, townlet.core.sim_loop]
- **Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop
- **Lines of code**: 107
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_ensure_candidate_ready(loop: SimulationLoop) -> None` — No docstring provided.
- `run_drill(config_path: Path, output_dir: Path, checkpoint: Path) -> dict[str, Any]` — No docstring provided.
- `main(argv: list[str] | None = None) -> int` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/promotion_evaluate.py

- **File path**: `scripts/promotion_evaluate.py`
- **Purpose**: Evaluate promotion readiness from anneal results payloads.
- **Dependencies**: stdlib [__future__, argparse, json, pathlib, sys, typing] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 190
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args(argv: list[str] | None = None) -> argparse.Namespace` — No docstring provided.
- `_load_payload(path: Path | None) -> Dict[str, Any]` — No docstring provided.
- `_derive_status(results: List[Dict[str, Any]]) -> str` — No docstring provided.
- `_collect_reasons(results: List[Dict[str, Any]]) -> List[str]` — No docstring provided.
- `evaluate(payload: Dict[str, Any]) -> Dict[str, Any]` — No docstring provided.
- `_print_human(summary: Dict[str, Any]) -> None` — No docstring provided.
- `main(argv: list[str] | None = None) -> int` — No docstring provided.

### Constants and Configuration
- `DEFAULT_INPUT_PATH` = Path('artifacts/m7/anneal_results.json')

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/reward_summary.py

- **File path**: `scripts/reward_summary.py`
- **Purpose**: Summarise reward breakdown telemetry for operations teams.
- **Dependencies**: stdlib [__future__, argparse, collections, dataclasses, json, pathlib, sys, typing] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 323
- **Environment variables**: None detected

### Classes
- **ComponentStats(object)** — No docstring provided.
  - Attributes:
    - `count` (type=int, default=0)
    - `total` (type=float, default=0.0)
    - `minimum` (type=float, default=float('inf'))
    - `maximum` (type=float, default=float('-inf'))
  - Methods:
    - `update(self, value: float) -> None` — No docstring provided.
    - `mean(self) -> float` — No docstring provided.
    - `as_dict(self) -> dict[str, float | int]` — No docstring provided.
- **RewardAggregator(object)** — Aggregate reward breakdowns from telemetry payloads.
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `add_payload(self, payload: Mapping[str, object], source: str) -> None` — No docstring provided.
    - `summary(self) -> dict[str, object]` — No docstring provided.

### Functions
- `_is_number(value: object) -> bool` — No docstring provided.
- `iter_payloads(path: Path) -> Iterator[tuple[Mapping[str, object], str]]` — No docstring provided.
- `collect_statistics(paths: Sequence[Path]) -> RewardAggregator` — No docstring provided.
- `render_text(summary: Mapping[str, object], *, top: int, agent_filters: set[str] | None) -> str` — No docstring provided.
- `render_markdown(summary: Mapping[str, object], *, top: int, agent_filters: set[str] | None) -> str` — No docstring provided.
- `render_json(summary: Mapping[str, object]) -> str` — No docstring provided.
- `parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace` — No docstring provided.
- `main(argv: Sequence[str] | None = None) -> int` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/run_anneal_rehearsal.py

- **File path**: `scripts/run_anneal_rehearsal.py`
- **Purpose**: Run BC + anneal rehearsal using production manifests and capture artefacts.
- **Dependencies**: stdlib [., __future__, argparse, importlib.util, json, pathlib, sys, typing] / third-party [None] / internal [townlet.config, townlet.policy.replay, townlet.policy.runner]
- **Related modules**: townlet.config, townlet.policy.replay, townlet.policy.runner
- **Lines of code**: 111
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `run_rehearsal(config_path: Path, manifest_path: Path, log_dir: Path) -> Dict[str, object]` — No docstring provided.
- `evaluate_summary(summary: Dict[str, object]) -> Dict[str, object]` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- `DEFAULT_CONFIG` = Path('artifacts/m5/acceptance/config_idle_v1.yaml')
- `DEFAULT_MANIFEST` = Path('data/bc_datasets/manifests/idle_v1.json')
- `DEFAULT_LOG_DIR` = Path('artifacts/m5/acceptance/logs')

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.policy.replay, townlet.policy.runner

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/run_employment_smoke.py

- **File path**: `scripts/run_employment_smoke.py`
- **Purpose**: Employment loop smoke test runner for R2 mitigation.
- **Dependencies**: stdlib [__future__, argparse, json, pathlib, typing] / third-party [None] / internal [townlet.config, townlet.core.sim_loop]
- **Related modules**: townlet.config, townlet.core.sim_loop
- **Lines of code**: 81
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `run_smoke(config_path: Path, ticks: int, enforce: bool) -> Dict[str, Any]` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.core.sim_loop

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/run_mixed_soak.py

- **File path**: `scripts/run_mixed_soak.py`
- **Purpose**: Run alternating replay/rollout PPO cycles for soak testing.
- **Dependencies**: stdlib [__future__, argparse, pathlib, sys] / third-party [None] / internal [townlet.config.loader, townlet.policy.replay, townlet.policy.runner]
- **Related modules**: townlet.config.loader, townlet.policy.replay, townlet.policy.runner
- **Lines of code**: 110
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- `ROOT` = Path(__file__).resolve().parents[1]
- `SRC` = ROOT / 'src'

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config.loader, townlet.policy.replay, townlet.policy.runner

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/run_replay.py

- **File path**: `scripts/run_replay.py`
- **Purpose**: Utility to replay observation/telemetry samples for analysis or tutorials.
- **Dependencies**: stdlib [__future__, argparse, json, pathlib, typing] / third-party [numpy] / internal [townlet.policy.replay]
- **Related modules**: townlet.policy.replay
- **Lines of code**: 118
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `render_observation(sample: Dict[str, Any]) -> None` — No docstring provided.
- `inspect_telemetry(path: Path) -> None` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy
- Internal: townlet.policy.replay

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/run_simulation.py

- **File path**: `scripts/run_simulation.py`
- **Purpose**: Run a headless Townlet simulation loop for debugging.
- **Dependencies**: stdlib [__future__, argparse, pathlib] / third-party [None] / internal [townlet.config.loader, townlet.core.sim_loop]
- **Related modules**: townlet.config.loader, townlet.core.sim_loop
- **Lines of code**: 31
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config.loader, townlet.core.sim_loop

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/run_training.py

- **File path**: `scripts/run_training.py`
- **Purpose**: CLI entry point for training Townlet policies.
- **Dependencies**: stdlib [__future__, argparse, json, pathlib] / third-party [None] / internal [townlet.config, townlet.config.loader, townlet.policy.replay, townlet.policy.runner]
- **Related modules**: townlet.config, townlet.config.loader, townlet.policy.replay, townlet.policy.runner
- **Lines of code**: 466
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `_collect_ppo_overrides(args: argparse.Namespace) -> dict[str, object]` — No docstring provided.
- `_apply_ppo_overrides(config, overrides: dict[str, object]) -> None` — No docstring provided.
- `_build_dataset_config_from_args(args: argparse.Namespace, default_manifest: Path | None) -> ReplayDatasetConfig | None` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.config.loader, townlet.policy.replay, townlet.policy.runner

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/telemetry_check.py

- **File path**: `scripts/telemetry_check.py`
- **Purpose**: Validate Townlet telemetry payloads against known schema versions.
- **Dependencies**: stdlib [__future__, argparse, json, pathlib, typing] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 84
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `load_payload(path: Path) -> Dict[str, Any]` — No docstring provided.
- `validate(payload: Dict[str, Any], schema_version: str) -> None` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- `SUPPORTED_SCHEMAS` = {'0.2.0': {'employment_keys': {'pending', 'pending_count', 'exits_today', 'daily_exit_cap', 'queue_limit', 'review_window'}, 'job_required_keys': {'job_id', 'on_shift', 'wallet', 'shift_state', 'attendance_ratio', 'late_ticks_today', 'wages_withheld'}}}

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/telemetry_summary.py

- **File path**: `scripts/telemetry_summary.py`
- **Purpose**: Produce summaries for PPO telemetry logs.
- **Dependencies**: stdlib [__future__, argparse, json, pathlib, typing] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 338
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `load_records(path: Path) -> list[dict[str, object]]` — No docstring provided.
- `load_baseline(path: Path | None) -> dict[str, float] | None` — No docstring provided.
- `summarise(records: Sequence[dict[str, object]], baseline: dict[str, float] | None) -> dict[str, object]` — No docstring provided.
- `_format_optional_float(value: object, precision: int = 3) -> str` — No docstring provided.
- `render_text(summary: dict[str, object]) -> str` — No docstring provided.
- `render_markdown(summary: dict[str, object]) -> str` — No docstring provided.
- `render(summary: dict[str, object], fmt: str) -> str` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/telemetry_watch.py

- **File path**: `scripts/telemetry_watch.py`
- **Purpose**: Tail PPO telemetry logs and alert on metric thresholds.
- **Dependencies**: stdlib [__future__, argparse, json, pathlib, sys, time, typing] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 525
- **Environment variables**: None detected

### Classes
- None

### Functions
- `build_parser() -> argparse.ArgumentParser` — No docstring provided.
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `parse_args_from_list(argv: list[str]) -> argparse.Namespace` — No docstring provided.
- `stream_records(path: Path, follow: bool, interval: float) -> Iterator[dict[str, float]]` — No docstring provided.
- `_parse_health_line(line: str) -> dict[str, float]` — No docstring provided.
- `stream_health_records(path: Path, follow: bool, interval: float) -> Iterator[dict[str, float]]` — No docstring provided.
- `check_thresholds(record: dict[str, object], args: argparse.Namespace) -> None` — No docstring provided.
- `check_health_thresholds(record: dict[str, float], args: argparse.Namespace) -> None` — No docstring provided.
- `main(args: list[str] | None = None) -> None` — No docstring provided.

### Constants and Configuration
- `MODES` = {'ppo', 'health'}
- `REQUIRED_KEYS` = {'epoch', 'loss_total', 'kl_divergence', 'grad_norm', 'batch_entropy_mean', 'reward_advantage_corr', 'log_stream_offset', 'data_mode', 'queue_conflict_events', 'queue_conflict_intensity_sum', 'shared_meal_events', 'late_help_events', 'shift_takeover_events', 'chat_success_events', 'chat_failure_events', 'chat_quality_mean'}
- `OPTIONAL_NUMERIC_KEYS` = {'anneal_cycle', 'anneal_bc_accuracy', 'anneal_bc_threshold', 'anneal_loss_baseline', 'anneal_queue_baseline', 'anneal_intensity_baseline'}
- `OPTIONAL_BOOL_KEYS` = {'anneal_bc_passed', 'anneal_loss_flag', 'anneal_queue_flag', 'anneal_intensity_flag'}
- `OPTIONAL_TEXT_KEYS` = {'anneal_stage', 'anneal_dataset'}
- `OPTIONAL_EVENT_KEYS` = {'utility_outage_events', 'shower_complete_events', 'sleep_complete_events'}

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/validate_affordances.py

- **File path**: `scripts/validate_affordances.py`
- **Purpose**: Validate affordance manifest files for schema compliance.
- **Dependencies**: stdlib [__future__, argparse, pathlib, sys, typing] / third-party [None] / internal [townlet.config.affordance_manifest, townlet.world.preconditions]
- **Related modules**: townlet.config.affordance_manifest, townlet.world.preconditions
- **Lines of code**: 126
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `discover_manifests(inputs: Iterable[str]) -> List[Path]` — No docstring provided.
- `validate_manifest(path: Path) -> AffordanceManifest` — No docstring provided.
- `main() -> int` — No docstring provided.

### Constants and Configuration
- `DEFAULT_SEARCH_ROOT` = Path('configs/affordances')

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config.affordance_manifest, townlet.world.preconditions

### Code Quality Notes
- No obvious static issues detected by automated scan.


## scripts/validate_ppo_telemetry.py

- **File path**: `scripts/validate_ppo_telemetry.py`
- **Purpose**: Validate PPO telemetry NDJSON logs and report baseline drift.
- **Dependencies**: stdlib [__future__, argparse, json, math, pathlib, typing] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 248
- **Environment variables**: None detected

### Classes
- None

### Functions
- `parse_args() -> argparse.Namespace` — No docstring provided.
- `_ensure_numeric(key: str, value: object) -> None` — No docstring provided.
- `_load_records(path: Path) -> List[dict[str, object]]` — No docstring provided.
- `_validate_record(record: dict[str, object], source: Path) -> None` — No docstring provided.
- `_load_baseline(path: Path | None) -> dict[str, float] | None` — No docstring provided.
- `_relative_delta(delta: float, base_value: float) -> float | None` — No docstring provided.
- `_report_drift(records: list[dict[str, object]], baseline: dict[str, float], threshold: float | None, include_relative: bool) -> None` — No docstring provided.
- `validate_logs(paths: Iterable[Path], baseline_path: Path | None, drift_threshold: float | None, include_relative: bool) -> None` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- `BASE_REQUIRED_KEYS` = {'epoch', 'updates', 'transitions', 'loss_policy', 'loss_value', 'loss_entropy', 'loss_total', 'clip_fraction', 'clip_fraction_max', 'clip_triggered_minibatches', 'adv_mean', 'adv_std', 'adv_zero_std_batches', 'adv_min_std', 'grad_norm', 'kl_divergence', 'telemetry_version', 'lr', 'steps'}
- `CONFLICT_KEYS` = {'conflict.rivalry_max_mean_avg', 'conflict.rivalry_max_max_avg', 'conflict.rivalry_avoid_count_mean_avg', 'conflict.rivalry_avoid_count_max_avg'}
- `BASELINE_KEYS` = {'baseline_sample_count', 'baseline_reward_mean', 'baseline_reward_sum', 'baseline_reward_sum_mean'}
- `REQUIRED_V1_1_NUMERIC_KEYS` = {'epoch_duration_sec', 'cycle_id', 'batch_entropy_mean', 'batch_entropy_std', 'grad_norm_max', 'kl_divergence_max', 'reward_advantage_corr', 'rollout_ticks', 'log_stream_offset', 'queue_conflict_events', 'queue_conflict_intensity_sum'}
- `REQUIRED_V1_1_STRING_KEYS` = {'data_mode'}

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/__init__.py

- **File path**: `src/townlet/__init__.py`
- **Purpose**: Townlet simulation package.
- **Dependencies**: stdlib [__future__] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 9
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/agents/__init__.py

- **File path**: `src/townlet/agents/__init__.py`
- **Purpose**: Agent state models.
- **Dependencies**: stdlib [__future__] / third-party [models, relationship_modifiers] / internal [None]
- **Related modules**: None
- **Lines of code**: 19
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: models, relationship_modifiers
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/agents/models.py

- **File path**: `src/townlet/agents/models.py`
- **Purpose**: Agent-related dataclasses and helpers.
- **Dependencies**: stdlib [__future__, dataclasses] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 31
- **Environment variables**: None detected

### Classes
- **Personality(object)** — No docstring provided.
  - Attributes:
    - `extroversion` (type=float)
    - `forgiveness` (type=float)
    - `ambition` (type=float)
  - Methods: None
- **RelationshipEdge(object)** — No docstring provided.
  - Attributes:
    - `other_id` (type=str)
    - `trust` (type=float)
    - `familiarity` (type=float)
    - `rivalry` (type=float)
  - Methods: None
- **AgentState(object)** — Canonical agent state used across modules.
  - Attributes:
    - `agent_id` (type=str)
    - `needs` (type=dict[str, float])
    - `wallet` (type=float)
    - `personality` (type=Personality)
    - `relationships` (type=list[RelationshipEdge], default=field(default_factory=list))
  - Methods: None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/agents/relationship_modifiers.py

- **File path**: `src/townlet/agents/relationship_modifiers.py`
- **Purpose**: Relationship delta adjustment helpers respecting personality flags.
- **Dependencies**: stdlib [__future__, dataclasses, typing] / third-party [None] / internal [townlet.agents.models]
- **Related modules**: townlet.agents.models
- **Lines of code**: 102
- **Environment variables**: None detected

### Classes
- **RelationshipDelta(object)** — Represents trust/familiarity/rivalry deltas for a single event.
  - Attributes:
    - `trust` (type=float, default=0.0)
    - `familiarity` (type=float, default=0.0)
    - `rivalry` (type=float, default=0.0)
  - Methods: None

### Functions
- `apply_personality_modifiers(*, delta: RelationshipDelta, personality: Personality, event: RelationshipEvent, enabled: bool) -> RelationshipDelta` — Adjust ``delta`` based on personality traits when enabled.
- `_apply_forgiveness(value: float, forgiveness: float) -> float` — No docstring provided.
- `_apply_extroversion(value: float, extroversion: float) -> float` — No docstring provided.
- `_apply_ambition(value: float, ambition: float) -> float` — No docstring provided.
- `_clamp(value: float, low: float, high: float) -> float` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.agents.models

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/config/__init__.py

- **File path**: `src/townlet/config/__init__.py`
- **Purpose**: Config utilities for Townlet.
- **Dependencies**: stdlib [__future__] / third-party [loader] / internal [None]
- **Related modules**: None
- **Lines of code**: 105
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: loader
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/config/affordance_manifest.py

- **File path**: `src/townlet/config/affordance_manifest.py`
- **Purpose**: Utilities for validating affordance manifest files.
- **Dependencies**: stdlib [__future__, collections.abc, dataclasses, hashlib, logging, pathlib] / third-party [yaml] / internal [None]
- **Related modules**: None
- **Lines of code**: 316
- **Environment variables**: None detected

### Classes
- **ManifestObject(object)** — Represents an interactive object entry from the manifest.
  - Attributes:
    - `object_id` (type=str)
    - `object_type` (type=str)
    - `stock` (type=dict[str, int])
    - `position` (type=tuple[int, int] | None, default=None)
  - Methods: None
- **ManifestAffordance(object)** — Represents an affordance definition with preconditions and hooks.
  - Attributes:
    - `affordance_id` (type=str)
    - `object_type` (type=str)
    - `duration` (type=int)
    - `effects` (type=dict[str, float])
    - `preconditions` (type=list[str])
    - `hooks` (type=dict[str, list[str]])
  - Methods: None
- **AffordanceManifest(object)** — Normalised manifest contents and checksum metadata.
  - Attributes:
    - `path` (type=Path)
    - `checksum` (type=str)
    - `objects` (type=list[ManifestObject])
    - `affordances` (type=list[ManifestAffordance])
  - Methods:
    - `object_count(self) -> int` — No docstring provided.
    - `affordance_count(self) -> int` — No docstring provided.
- **AffordanceManifestError(ValueError)** — Raised when an affordance manifest fails validation.
  - Methods: None

### Functions
- `load_affordance_manifest(path: Path) -> AffordanceManifest` — Load and validate an affordance manifest, returning structured entries.
- `_parse_object_entry(entry: Mapping[str, object], path: Path, index: int) -> ManifestObject` — No docstring provided.
- `_parse_affordance_entry(entry: Mapping[str, object], path: Path, index: int) -> ManifestAffordance` — No docstring provided.
- `_parse_position(value: object, *, path: Path, index: int, entry_id: str) -> tuple[int, int] | None` — No docstring provided.
- `_parse_string_list(value: object, *, field: str, path: Path, index: int, entry_id: str) -> list[str]` — No docstring provided.
- `_require_string(entry: Mapping[str, object], field: str, path: Path, index: int) -> str` — No docstring provided.
- `_ensure_unique(entry_id: str, seen: set[str], path: Path, index: int) -> None` — No docstring provided.

### Constants and Configuration
- `_ALLOWED_HOOK_KEYS` = {'before', 'after', 'fail'}

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: yaml
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/config/loader.py

- **File path**: `src/townlet/config/loader.py`
- **Purpose**: Configuration loader and validation layer.
- **Dependencies**: stdlib [__future__, collections.abc, enum, importlib, pathlib, re, typing] / third-party [pydantic, yaml] / internal [townlet.snapshots]
- **Related modules**: townlet.snapshots
- **Lines of code**: 927
- **Environment variables**: None detected

### Classes
- **StageFlags(BaseModel)** — No docstring provided.
  - Attributes:
    - `relationships` (type=RelationshipStage, default='OFF')
    - `social_rewards` (type=SocialRewardStage, default='OFF')
  - Methods: None
- **SystemFlags(BaseModel)** — No docstring provided.
  - Attributes:
    - `lifecycle` (type=LifecycleToggle, default='on')
    - `observations` (type=ObservationVariant, default='hybrid')
  - Methods: None
- **TrainingFlags(BaseModel)** — No docstring provided.
  - Attributes:
    - `curiosity` (type=CuriosityToggle, default='phase_A')
  - Methods: None
- **PolicyRuntimeConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `option_commit_ticks` (type=int, default=Field(15, ge=0, le=100000))
  - Methods: None
- **ConsoleFlags(BaseModel)** — No docstring provided.
  - Attributes:
    - `mode` (type=ConsoleMode, default='viewer')
  - Methods: None
- **FeatureFlags(BaseModel)** — No docstring provided.
  - Attributes:
    - `stages` (type=StageFlags)
    - `systems` (type=SystemFlags)
    - `training` (type=TrainingFlags)
    - `console` (type=ConsoleFlags)
    - `relationship_modifiers` (type=bool, default=False)
  - Methods: None
- **NeedsWeights(BaseModel)** — No docstring provided.
  - Attributes:
    - `hunger` (type=float, default=Field(1.0, ge=0.5, le=2.0))
    - `hygiene` (type=float, default=Field(0.6, ge=0.2, le=1.0))
    - `energy` (type=float, default=Field(0.8, ge=0.4, le=1.5))
  - Methods: None
- **SocialRewardWeights(BaseModel)** — No docstring provided.
  - Attributes:
    - `C1_chat_base` (type=float, default=Field(0.01, ge=0.0, le=0.05))
    - `C1_coeff_trust` (type=float, default=Field(0.3, ge=0.0, le=1.0))
    - `C1_coeff_fam` (type=float, default=Field(0.2, ge=0.0, le=1.0))
    - `C2_avoid_conflict` (type=float, default=Field(0.005, ge=0.0, le=0.02))
  - Methods: None
- **RewardClips(BaseModel)** — No docstring provided.
  - Attributes:
    - `clip_per_tick` (type=float, default=Field(0.2, ge=0.01, le=1.0))
    - `clip_per_episode` (type=float, default=Field(50, ge=1, le=200))
    - `no_positive_within_death_ticks` (type=int, default=Field(10, ge=0, le=200))
  - Methods: None
- **RewardsConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `needs_weights` (type=NeedsWeights)
    - `decay_rates` (type=dict[str, float], default=Field(default_factory=lambda: {'hunger': 0.01, 'hygiene': 0.005, 'energy': 0.008}))
    - `punctuality_bonus` (type=float, default=Field(0.05, ge=0.0, le=0.1))
    - `wage_rate` (type=float, default=Field(0.01, ge=0.0, le=0.05))
    - `survival_tick` (type=float, default=Field(0.002, ge=0.0, le=0.01))
    - `faint_penalty` (type=float, default=Field(-1.0, ge=-5.0, le=0.0))
    - `eviction_penalty` (type=float, default=Field(-2.0, ge=-5.0, le=0.0))
    - `social` (type=SocialRewardWeights, default=SocialRewardWeights())
    - `clip` (type=RewardClips, default=RewardClips())
  - Methods:
    - `_sanity_check_punctuality(self) -> 'RewardsConfig'` — No docstring provided.
- **ShapingConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `use_potential` (type=bool, default=True)
  - Methods: None
- **CuriosityConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `phase_A_weight` (type=float, default=Field(0.02, ge=0.0, le=0.1))
    - `decay_by_milestone` (type=Literal['M2', 'never'], default='M2')
  - Methods: None
- **QueueFairnessConfig(BaseModel)** — Queue fairness tuning parameters (see REQUIREMENTS#5).
  - Attributes:
    - `cooldown_ticks` (type=int, default=Field(60, ge=0, le=600))
    - `ghost_step_after` (type=int, default=Field(3, ge=0, le=100))
    - `age_priority_weight` (type=float, default=Field(0.1, ge=0.0, le=1.0))
  - Methods: None
- **RivalryConfig(BaseModel)** — Conflict/rivalry tuning knobs (see REQUIREMENTS#5).
  - Attributes:
    - `increment_per_conflict` (type=float, default=Field(0.15, ge=0.0, le=1.0))
    - `decay_per_tick` (type=float, default=Field(0.005, ge=0.0, le=1.0))
    - `min_value` (type=float, default=Field(0.0, ge=0.0, le=1.0))
    - `max_value` (type=float, default=Field(1.0, ge=0.0, le=1.0))
    - `avoid_threshold` (type=float, default=Field(0.7, ge=0.0, le=1.0))
    - `eviction_threshold` (type=float, default=Field(0.05, ge=0.0, le=1.0))
    - `max_edges` (type=int, default=Field(6, ge=1, le=32))
    - `ghost_step_boost` (type=float, default=Field(1.5, ge=0.0, le=5.0))
    - `handover_boost` (type=float, default=Field(0.4, ge=0.0, le=5.0))
    - `queue_length_boost` (type=float, default=Field(0.25, ge=0.0, le=2.0))
  - Methods:
    - `_validate_ranges(self) -> 'RivalryConfig'` — No docstring provided.
- **ConflictConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `rivalry` (type=RivalryConfig, default=RivalryConfig())
  - Methods: None
- **PPOConfig(BaseModel)** — Config for PPO training hyperparameters.
  - Attributes:
    - `learning_rate` (type=float, default=Field(0.0003, gt=0.0))
    - `clip_param` (type=float, default=Field(0.2, ge=0.0, le=1.0))
    - `value_loss_coef` (type=float, default=Field(0.5, ge=0.0))
    - `entropy_coef` (type=float, default=Field(0.01, ge=0.0))
    - `num_epochs` (type=int, default=Field(4, ge=1, le=64))
    - `mini_batch_size` (type=int, default=Field(32, ge=1))
    - `gae_lambda` (type=float, default=Field(0.95, ge=0.0, le=1.0))
    - `gamma` (type=float, default=Field(0.99, ge=0.0, le=1.0))
    - `max_grad_norm` (type=float, default=Field(0.5, ge=0.0))
    - `value_clip` (type=float, default=Field(0.2, ge=0.0, le=1.0))
    - `advantage_normalization` (type=bool, default=True)
    - `num_mini_batches` (type=int, default=Field(4, ge=1, le=1024))
  - Methods: None
- **EmbeddingAllocatorConfig(BaseModel)** — Embedding slot reuse guardrails (see REQUIREMENTS#3).
  - Attributes:
    - `cooldown_ticks` (type=int, default=Field(2000, ge=0, le=10000))
    - `reuse_warning_threshold` (type=float, default=Field(0.05, ge=0.0, le=0.5))
    - `log_forced_reuse` (type=bool, default=True)
    - `max_slots` (type=int, default=Field(64, ge=1, le=256))
  - Methods: None
- **HybridObservationConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `local_window` (type=int, default=Field(11, ge=3))
    - `include_targets` (type=bool, default=False)
    - `time_ticks_per_day` (type=int, default=Field(1440, ge=1))
  - Methods:
    - `_validate_window(self) -> 'HybridObservationConfig'` — No docstring provided.
- **SocialSnippetConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `top_friends` (type=int, default=Field(2, ge=0, le=8))
    - `top_rivals` (type=int, default=Field(2, ge=0, le=8))
    - `embed_dim` (type=int, default=Field(8, ge=1, le=32))
    - `include_aggregates` (type=bool, default=True)
  - Methods:
    - `_validate_totals(self) -> 'SocialSnippetConfig'` — No docstring provided.
- **ObservationsConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `hybrid` (type=HybridObservationConfig, default=HybridObservationConfig())
    - `social_snippet` (type=SocialSnippetConfig, default=SocialSnippetConfig())
  - Methods: None
- **StarvationCanaryConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `window_ticks` (type=int, default=Field(1000, ge=1, le=100000))
    - `max_incidents` (type=int, default=Field(0, ge=0, le=10000))
    - `hunger_threshold` (type=float, default=Field(0.05, ge=0.0, le=1.0))
    - `min_duration_ticks` (type=int, default=Field(30, ge=1, le=10000))
  - Methods: None
- **RewardVarianceCanaryConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `window_ticks` (type=int, default=Field(1000, ge=1, le=100000))
    - `max_variance` (type=float, default=Field(0.25, ge=0.0))
    - `min_samples` (type=int, default=Field(20, ge=1, le=100000))
  - Methods: None
- **OptionThrashCanaryConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `window_ticks` (type=int, default=Field(600, ge=1, le=100000))
    - `max_switch_rate` (type=float, default=Field(0.25, ge=0.0, le=10.0))
    - `min_samples` (type=int, default=Field(10, ge=1, le=100000))
  - Methods: None
- **PromotionGateConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `required_passes` (type=int, default=Field(2, ge=1, le=10))
    - `window_ticks` (type=int, default=Field(1000, ge=1, le=100000))
    - `allowed_alerts` (type=tuple[str, ...], default=())
    - `model_config` (default=ConfigDict(extra='forbid'))
  - Methods:
    - `_coerce_allowed(cls, value: object) -> object` — No docstring provided.
    - `_normalise(self) -> 'PromotionGateConfig'` — No docstring provided.
- **LifecycleConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `respawn_delay_ticks` (type=int, default=Field(0, ge=0, le=100000))
  - Methods: None
- **StabilityConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `affordance_fail_threshold` (type=int, default=Field(5, ge=0, le=100))
    - `lateness_threshold` (type=int, default=Field(3, ge=0, le=100))
    - `starvation` (type=StarvationCanaryConfig, default=StarvationCanaryConfig())
    - `reward_variance` (type=RewardVarianceCanaryConfig, default=RewardVarianceCanaryConfig())
    - `option_thrash` (type=OptionThrashCanaryConfig, default=OptionThrashCanaryConfig())
    - `promotion` (type=PromotionGateConfig, default=PromotionGateConfig())
  - Methods:
    - `as_dict(self) -> dict[str, object]` — No docstring provided.
- **IntRange(BaseModel)** — No docstring provided.
  - Attributes:
    - `min` (type=int, default=Field(ge=0))
    - `max` (type=int, default=Field(ge=0))
    - `model_config` (default=ConfigDict(extra='forbid'))
  - Methods:
    - `_coerce(cls, value: object) -> dict[str, int]` — No docstring provided.
    - `_validate_bounds(self) -> 'IntRange'` — No docstring provided.
- **FloatRange(BaseModel)** — No docstring provided.
  - Attributes:
    - `min` (type=float)
    - `max` (type=float)
    - `model_config` (default=ConfigDict(extra='forbid'))
  - Methods:
    - `_coerce(cls, value: object) -> dict[str, float]` — No docstring provided.
    - `_validate_bounds(self) -> 'FloatRange'` — No docstring provided.
- **PerturbationKind(str, Enum)** — No docstring provided.
  - Attributes:
    - `PRICE_SPIKE` (default='price_spike')
    - `BLACKOUT` (default='blackout')
    - `OUTAGE` (default='outage')
    - `ARRANGED_MEET` (default='arranged_meet')
  - Methods: None
- **BasePerturbationEventConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `kind` (type=PerturbationKind)
    - `probability_per_day` (type=float, default=Field(0.0, ge=0.0, alias='prob_per_day'))
    - `cooldown_ticks` (type=int, default=Field(0, ge=0))
    - `duration` (type=IntRange, default=Field(default_factory=lambda: IntRange(min=0, max=0)))
    - `model_config` (default=ConfigDict(extra='forbid', populate_by_name=True))
  - Methods:
    - `_normalise_duration(cls, values: dict[str, object]) -> dict[str, object]` — No docstring provided.
- **PriceSpikeEventConfig(BasePerturbationEventConfig)** — No docstring provided.
  - Attributes:
    - `kind` (type=Literal[PerturbationKind.PRICE_SPIKE], default=PerturbationKind.PRICE_SPIKE)
    - `magnitude` (type=FloatRange, default=Field(default_factory=lambda: FloatRange(min=1.0, max=1.0)))
    - `targets` (type=list[str], default=Field(default_factory=list))
  - Methods:
    - `_normalise_magnitude(cls, values: dict[str, object]) -> dict[str, object]` — No docstring provided.
- **BlackoutEventConfig(BasePerturbationEventConfig)** — No docstring provided.
  - Attributes:
    - `kind` (type=Literal[PerturbationKind.BLACKOUT], default=PerturbationKind.BLACKOUT)
    - `utility` (type=Literal['power'], default='power')
  - Methods: None
- **OutageEventConfig(BasePerturbationEventConfig)** — No docstring provided.
  - Attributes:
    - `kind` (type=Literal[PerturbationKind.OUTAGE], default=PerturbationKind.OUTAGE)
    - `utility` (type=Literal['water'], default='water')
  - Methods: None
- **ArrangedMeetEventConfig(BasePerturbationEventConfig)** — No docstring provided.
  - Attributes:
    - `kind` (type=Literal[PerturbationKind.ARRANGED_MEET], default=PerturbationKind.ARRANGED_MEET)
    - `target` (type=str, default=Field(default='top_rivals'))
    - `location` (type=str, default=Field(default='cafe'))
    - `max_participants` (type=int, default=Field(2, ge=2))
  - Methods: None
- **PerturbationSchedulerConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `max_concurrent_events` (type=int, default=Field(1, ge=1))
    - `global_cooldown_ticks` (type=int, default=Field(0, ge=0))
    - `per_agent_cooldown_ticks` (type=int, default=Field(0, ge=0))
    - `grace_window_ticks` (type=int, default=Field(60, ge=0))
    - `window_ticks` (type=int, default=Field(1440, ge=1))
    - `max_events_per_window` (type=int, default=Field(1, ge=0))
    - `events` (type=dict[str, PerturbationEventConfig], default=Field(default_factory=dict))
    - `model_config` (default=ConfigDict(extra='allow', populate_by_name=True))
  - Methods:
    - `event_list(self) -> list[PerturbationEventConfig]` — No docstring provided.
- **AffordanceRuntimeConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `factory` (type=str | None, default=None)
    - `instrumentation` (type=Literal['off', 'timings'], default='off')
    - `options` (type=dict[str, object], default=Field(default_factory=dict))
    - `hook_allowlist` (type=tuple[str, ...], default=Field(default_factory=tuple))
    - `allow_env_hooks` (type=bool, default=True)
    - `model_config` (default=ConfigDict(extra='allow'))
  - Methods: None
- **AffordanceConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `affordances_file` (type=str, default=Field('configs/affordances/core.yaml'))
    - `runtime` (type=AffordanceRuntimeConfig, default=AffordanceRuntimeConfig())
  - Methods: None
- **EmploymentConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `grace_ticks` (type=int, default=Field(5, ge=0, le=120))
    - `absent_cutoff` (type=int, default=Field(30, ge=0, le=600))
    - `absence_slack` (type=int, default=Field(20, ge=0, le=600))
    - `late_tick_penalty` (type=float, default=Field(0.005, ge=0.0, le=1.0))
    - `absence_penalty` (type=float, default=Field(0.2, ge=0.0, le=5.0))
    - `max_absent_shifts` (type=int, default=Field(3, ge=0, le=20))
    - `attendance_window` (type=int, default=Field(3, ge=1, le=14))
    - `daily_exit_cap` (type=int, default=Field(2, ge=0, le=50))
    - `exit_queue_limit` (type=int, default=Field(8, ge=0, le=100))
    - `exit_review_window` (type=int, default=Field(1440, ge=1, le=100000))
    - `enforce_job_loop` (type=bool, default=False)
  - Methods: None
- **BehaviorConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `hunger_threshold` (type=float, default=Field(0.4, ge=0.0, le=1.0))
    - `hygiene_threshold` (type=float, default=Field(0.4, ge=0.0, le=1.0))
    - `energy_threshold` (type=float, default=Field(0.4, ge=0.0, le=1.0))
    - `job_arrival_buffer` (type=int, default=Field(20, ge=0))
  - Methods: None
- **SocialRewardScheduleEntry(BaseModel)** — No docstring provided.
  - Attributes:
    - `cycle` (type=int, default=Field(0, ge=0))
    - `stage` (type=SocialRewardStage)
  - Methods: None
- **BCTrainingSettings(BaseModel)** — No docstring provided.
  - Attributes:
    - `manifest` (type=Path | None, default=None)
    - `learning_rate` (type=float, default=Field(0.001, gt=0.0))
    - `batch_size` (type=int, default=Field(64, ge=1))
    - `epochs` (type=int, default=Field(10, ge=1))
    - `weight_decay` (type=float, default=Field(0.0, ge=0.0))
    - `device` (type=str, default='cpu')
  - Methods: None
- **AnnealStage(BaseModel)** — No docstring provided.
  - Attributes:
    - `cycle` (type=int, default=Field(0, ge=0))
    - `mode` (type=Literal['bc', 'ppo'], default='ppo')
    - `epochs` (type=int, default=Field(1, ge=1))
    - `bc_weight` (type=float, default=Field(1.0, ge=0.0, le=1.0))
  - Methods: None
- **NarrationThrottleConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `global_cooldown_ticks` (type=int, default=Field(30, ge=0, le=10000))
    - `category_cooldown_ticks` (type=dict[str, int], default=Field(default_factory=dict))
    - `dedupe_window_ticks` (type=int, default=Field(20, ge=0, le=10000))
    - `global_window_ticks` (type=int, default=Field(600, ge=1, le=10000))
    - `global_window_limit` (type=int, default=Field(10, ge=1, le=1000))
    - `priority_categories` (type=list[str], default=Field(default_factory=list))
  - Methods:
    - `get_category_cooldown(self, category: str) -> int` — No docstring provided.
- **RelationshipNarrationConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `friendship_trust_threshold` (type=float, default=Field(0.6, ge=-1.0, le=1.0))
    - `friendship_delta_threshold` (type=float, default=Field(0.25, ge=0.0, le=2.0))
    - `friendship_priority_threshold` (type=float, default=Field(0.85, ge=-1.0, le=1.0))
    - `rivalry_avoid_threshold` (type=float, default=Field(0.7, ge=0.0, le=1.0))
    - `rivalry_escalation_threshold` (type=float, default=Field(0.9, ge=0.0, le=1.0))
  - Methods:
    - `_validate_thresholds(self) -> 'RelationshipNarrationConfig'` — No docstring provided.
- **TelemetryRetryPolicy(BaseModel)** — No docstring provided.
  - Attributes:
    - `max_attempts` (type=int, default=Field(default=3, ge=0, le=10))
    - `backoff_seconds` (type=float, default=Field(default=0.5, ge=0.0, le=30.0))
  - Methods: None
- **TelemetryBufferConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `max_batch_size` (type=int, default=Field(default=32, ge=1, le=500))
    - `max_buffer_bytes` (type=int, default=Field(default=256000, ge=1024, le=16777216))
    - `flush_interval_ticks` (type=int, default=Field(default=1, ge=1, le=10000))
  - Methods: None
- **TelemetryTransportConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `type` (type=TelemetryTransportType, default='stdout')
    - `endpoint` (type=str | None, default=None)
    - `file_path` (type=Path | None, default=None)
    - `connect_timeout_seconds` (type=float, default=Field(default=5.0, ge=0.0, le=60.0))
    - `send_timeout_seconds` (type=float, default=Field(default=1.0, ge=0.0, le=60.0))
    - `enable_tls` (type=bool, default=False)
    - `verify_hostname` (type=bool, default=True)
    - `ca_file` (type=Path | None, default=None)
    - `cert_file` (type=Path | None, default=None)
    - `key_file` (type=Path | None, default=None)
    - `allow_plaintext` (type=bool, default=False)
    - `retry` (type=TelemetryRetryPolicy, default=TelemetryRetryPolicy())
    - `buffer` (type=TelemetryBufferConfig, default=TelemetryBufferConfig())
    - `worker_poll_seconds` (type=float, default=Field(default=0.5, ge=0.01, le=10.0))
  - Methods:
    - `_validate_transport(self) -> 'TelemetryTransportConfig'` — No docstring provided.
- **TelemetryConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `narration` (type=NarrationThrottleConfig, default=NarrationThrottleConfig())
    - `transport` (type=TelemetryTransportConfig, default=TelemetryTransportConfig())
    - `relationship_narration` (type=RelationshipNarrationConfig, default=RelationshipNarrationConfig())
  - Methods: None
- **ConsoleAuthTokenConfig(BaseModel)** — Configuration entry for a single console authentication token.
  - Attributes:
    - `label` (type=str | None, default=None)
    - `role` (type=ConsoleMode, default='viewer')
    - `token` (type=str | None, default=None)
    - `token_env` (type=str | None, default=None)
  - Methods:
    - `_validate_token_source(self) -> 'ConsoleAuthTokenConfig'` — No docstring provided.
- **ConsoleAuthConfig(BaseModel)** — Authentication settings for console and telemetry command ingress.
  - Attributes:
    - `enabled` (type=bool, default=False)
    - `require_auth_for_viewer` (type=bool, default=True)
    - `tokens` (type=list[ConsoleAuthTokenConfig], default=Field(default_factory=list))
  - Methods:
    - `_validate_tokens(self) -> 'ConsoleAuthConfig'` — No docstring provided.
- **SnapshotStorageConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `root` (type=Path, default=Field(default=Path('snapshots')))
  - Methods:
    - `_validate_root(self) -> 'SnapshotStorageConfig'` — No docstring provided.
- **SnapshotAutosaveConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `cadence_ticks` (type=int | None, default=Field(default=None, ge=1))
    - `retain` (type=int, default=Field(default=3, ge=1, le=1000))
  - Methods:
    - `_validate_cadence(self) -> 'SnapshotAutosaveConfig'` — No docstring provided.
- **SnapshotIdentityConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `policy_hash` (type=str | None, default=None)
    - `policy_artifact` (type=Path | None, default=None)
    - `observation_variant` (type=ObservationVariant | Literal['infer'], default='infer')
    - `anneal_ratio` (type=float | None, default=Field(default=None, ge=0.0, le=1.0))
    - `_HEX40` (default=re.compile('^[0-9a-fA-F]{40}$'))
    - `_HEX64` (default=re.compile('^[0-9a-fA-F]{64}$'))
    - `_BASE64` (default=re.compile('^[A-Za-z0-9+/=]{32,88}$'))
  - Methods:
    - `_validate_policy_hash(self) -> 'SnapshotIdentityConfig'` — No docstring provided.
    - `_validate_variant(self) -> 'SnapshotIdentityConfig'` — No docstring provided.
- **SnapshotMigrationsConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `handlers` (type=dict[str, str], default=Field(default_factory=dict))
    - `auto_apply` (type=bool, default=False)
    - `allow_minor` (type=bool, default=False)
  - Methods:
    - `_validate_handlers(self) -> 'SnapshotMigrationsConfig'` — No docstring provided.
- **SnapshotGuardrailsConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `require_exact_config` (type=bool, default=True)
    - `allow_downgrade` (type=bool, default=False)
    - `allowed_paths` (type=list[Path], default=Field(default_factory=list))
  - Methods: None
- **SnapshotConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `storage` (type=SnapshotStorageConfig, default=SnapshotStorageConfig())
    - `autosave` (type=SnapshotAutosaveConfig, default=SnapshotAutosaveConfig())
    - `identity` (type=SnapshotIdentityConfig, default=SnapshotIdentityConfig())
    - `migrations` (type=SnapshotMigrationsConfig, default=SnapshotMigrationsConfig())
    - `guardrails` (type=SnapshotGuardrailsConfig, default=SnapshotGuardrailsConfig())
  - Methods:
    - `_validate_observation_override(self) -> 'SnapshotConfig'` — No docstring provided.
- **TrainingConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `source` (type=TrainingSource, default='replay')
    - `rollout_ticks` (type=int, default=Field(100, ge=0))
    - `rollout_auto_seed_agents` (type=bool, default=False)
    - `replay_manifest` (type=Path | None, default=None)
    - `social_reward_stage_override` (type=SocialRewardStage | None, default=None)
    - `social_reward_schedule` (type=list['SocialRewardScheduleEntry'], default=Field(default_factory=list))
    - `bc` (type=BCTrainingSettings, default=BCTrainingSettings())
    - `anneal_schedule` (type=list[AnnealStage], default=Field(default_factory=list))
    - `anneal_accuracy_threshold` (type=float, default=Field(0.9, ge=0.0, le=1.0))
    - `anneal_enable_policy_blend` (type=bool, default=False)
  - Methods: None
- **JobSpec(BaseModel)** — No docstring provided.
  - Attributes:
    - `start_tick` (type=int, default=0)
    - `end_tick` (type=int, default=0)
    - `wage_rate` (type=float, default=0.0)
    - `lateness_penalty` (type=float, default=0.0)
    - `location` (type=tuple[int, int] | None, default=None)
  - Methods: None
- **SimulationConfig(BaseModel)** — No docstring provided.
  - Attributes:
    - `config_id` (type=str)
    - `features` (type=FeatureFlags)
    - `rewards` (type=RewardsConfig)
    - `economy` (type=dict[str, float], default=Field(default_factory=lambda: {'meal_cost': 0.4, 'cook_energy_cost': 0.05, 'cook_hygiene_cost': 0.02, 'wage_income': 0.02, 'ingredients_cost': 0.15, 'stove_stock_replenish': 2}))
    - `jobs` (type=dict[str, JobSpec], default=Field(default_factory=lambda: {'grocer': JobSpec(start_tick=180, end_tick=360, wage_rate=0.02, lateness_penalty=0.1, location=(0, 0)), 'barista': JobSpec(start_tick=400, end_tick=560, wage_rate=0.025, lateness_penalty=0.12, location=(1, 0))}))
    - `shaping` (type=ShapingConfig | None, default=None)
    - `curiosity` (type=CuriosityConfig | None, default=None)
    - `queue_fairness` (type=QueueFairnessConfig, default=QueueFairnessConfig())
    - `conflict` (type=ConflictConfig, default=ConflictConfig())
    - `ppo` (type=PPOConfig | None, default=None)
    - `training` (type=TrainingConfig, default=TrainingConfig())
    - `embedding_allocator` (type=EmbeddingAllocatorConfig, default=EmbeddingAllocatorConfig())
    - `observations_config` (type=ObservationsConfig, default=ObservationsConfig())
    - `affordances` (type=AffordanceConfig, default=AffordanceConfig())
    - `stability` (type=StabilityConfig, default=StabilityConfig())
    - `behavior` (type=BehaviorConfig, default=BehaviorConfig())
    - `policy_runtime` (type=PolicyRuntimeConfig, default=PolicyRuntimeConfig())
    - `employment` (type=EmploymentConfig, default=EmploymentConfig())
    - `telemetry` (type=TelemetryConfig, default=TelemetryConfig())
    - `console_auth` (type=ConsoleAuthConfig, default=ConsoleAuthConfig())
    - `snapshot` (type=SnapshotConfig, default=SnapshotConfig())
    - `perturbations` (type=PerturbationSchedulerConfig, default=PerturbationSchedulerConfig())
    - `lifecycle` (type=LifecycleConfig, default=LifecycleConfig())
    - `model_config` (default=ConfigDict(extra='allow'))
  - Methods:
    - `_validate_observation_variant(self) -> 'SimulationConfig'` — No docstring provided.
    - `observation_variant(self) -> ObservationVariant` — No docstring provided.
    - `require_observation_variant(self, expected: ObservationVariant) -> None` — No docstring provided.
    - `snapshot_root(self) -> Path` — No docstring provided.
    - `snapshot_allowed_roots(self) -> tuple[Path, ...]` — No docstring provided.
    - `build_snapshot_identity(self, *, policy_hash: str | None, runtime_observation_variant: ObservationVariant | None, runtime_anneal_ratio: float | None) -> dict[str, object]` — No docstring provided.
    - `register_snapshot_migrations(self) -> None` — No docstring provided.

### Functions
- `load_config(path: Path) -> SimulationConfig` — Load and validate a Townlet YAML configuration file.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pydantic, yaml
- Internal: townlet.snapshots

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/console/__init__.py

- **File path**: `src/townlet/console/__init__.py`
- **Purpose**: Console command handling exports.
- **Dependencies**: stdlib [__future__, importlib, typing] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 15
- **Environment variables**: None detected

### Classes
- None

### Functions
- `__getattr__(name: str) -> Any` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/console/auth.py

- **File path**: `src/townlet/console/auth.py`
- **Purpose**: Authentication helpers for console and telemetry command ingress.
- **Dependencies**: stdlib [__future__, dataclasses, os, secrets, typing] / third-party [None] / internal [townlet.config]
- **Related modules**: townlet.config
- **Lines of code**: 141
- **Environment variables**: getenv

### Classes
- **AuthPrincipal(object)** — Represents an authenticated caller.
  - Attributes:
    - `role` (type=ConsoleMode)
    - `label` (type=str | None, default=None)
  - Methods: None
- **ConsoleAuthenticationError(Exception)** — Raised when authentication of a console command fails.
  - Methods:
    - `__init__(self, message: str, identity: dict[str, str | None]) -> None` — No docstring provided.
- **ConsoleAuthenticator(object)** — Authenticates console command payloads using configured tokens.
  - Methods:
    - `__init__(self, config: ConsoleAuthConfig) -> None` — No docstring provided.
    - `_load_tokens(self, entries: list[ConsoleAuthTokenConfig]) -> None` — No docstring provided.
    - `_to_mapping(command: object) -> dict[str, Any]` — No docstring provided.
    - `_identity(payload: Mapping[str, Any]) -> dict[str, str | None]` — No docstring provided.
    - `_normalise_role(value: object, *, default: ConsoleMode = 'viewer') -> ConsoleMode` — No docstring provided.
    - `authorise(self, command: object) -> tuple[dict[str, Any], AuthPrincipal | None]` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/console/command.py

- **File path**: `src/townlet/console/command.py`
- **Purpose**: Console command envelope and result helpers.
- **Dependencies**: stdlib [__future__, dataclasses, typing] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 201
- **Environment variables**: None detected

### Classes
- **ConsoleCommandError(RuntimeError)** — Raised by handlers when a command should return an error response.
  - Methods:
    - `__init__(self, code: str, message: str, *, details: Mapping[str, Any] | None = None) -> None` — No docstring provided.
- **ConsoleCommandEnvelope(object)** — Normalised representation of an incoming console command payload.
  - Attributes:
    - `name` (type=str)
    - `args` (type=list[Any], default=field(default_factory=list))
    - `kwargs` (type=dict[str, Any], default=field(default_factory=dict))
    - `cmd_id` (type=str | None, default=None)
    - `issuer` (type=str | None, default=None)
    - `mode` (type=str, default='viewer')
    - `timestamp_ms` (type=int | None, default=None)
    - `metadata` (type=dict[str, Any], default=field(default_factory=dict))
    - `raw` (type=Mapping[str, Any] | None, default=None)
  - Methods:
    - `from_payload(cls, payload: object) -> 'ConsoleCommandEnvelope'` — Parse a payload emitted by the console transport.
- **ConsoleCommandResult(object)** — Standard response emitted after processing a console command.
  - Attributes:
    - `name` (type=str)
    - `status` (type=str)
    - `result` (type=dict[str, Any] | None, default=None)
    - `error` (type=dict[str, Any] | None, default=None)
    - `cmd_id` (type=str | None, default=None)
    - `issuer` (type=str | None, default=None)
    - `tick` (type=int | None, default=None)
    - `latency_ms` (type=int | None, default=None)
  - Methods:
    - `ok(cls, envelope: ConsoleCommandEnvelope, payload: Mapping[str, Any] | None = None, *, tick: int | None = None, latency_ms: int | None = None) -> 'ConsoleCommandResult'` — No docstring provided.
    - `from_error(cls, envelope: ConsoleCommandEnvelope, code: str, message: str, *, details: Mapping[str, Any] | None = None, tick: int | None = None, latency_ms: int | None = None) -> 'ConsoleCommandResult'` — No docstring provided.
    - `clone(self) -> 'ConsoleCommandResult'` — No docstring provided.
    - `to_dict(self) -> dict[str, Any]` — No docstring provided.

### Functions
- None

### Constants and Configuration
- `_VALID_MODES` = {'viewer', 'admin'}

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/console/handlers.py

- **File path**: `src/townlet/console/handlers.py`
- **Purpose**: Console validation scaffolding.
- **Dependencies**: stdlib [__future__, collections.abc, dataclasses, json, pathlib, typing] / third-party [None] / internal [townlet.config, townlet.lifecycle.manager, townlet.policy.runner, townlet.scheduler.perturbations, townlet.snapshots, townlet.stability.promotion, townlet.telemetry.publisher, townlet.world.grid]
- **Related modules**: townlet.config, townlet.lifecycle.manager, townlet.policy.runner, townlet.scheduler.perturbations, townlet.snapshots, townlet.stability.promotion, townlet.telemetry.publisher, townlet.world.grid
- **Lines of code**: 1146
- **Environment variables**: None detected

### Classes
- **ConsoleCommand(object)** — Represents a parsed console command ready for execution.
  - Attributes:
    - `name` (type=str)
    - `args` (type=tuple[object, ...])
    - `kwargs` (type=dict[str, object])
  - Methods: None
- **ConsoleHandler(Protocol)** — No docstring provided.
  - Methods:
    - `__call__(self, command: ConsoleCommand) -> object` — No docstring provided.
- **ConsoleRouter(object)** — Routes validated commands to subsystem handlers.
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `register(self, name: str, handler: ConsoleHandler) -> None` — No docstring provided.
    - `dispatch(self, command: ConsoleCommand) -> object` — No docstring provided.
- **EventStream(object)** — Simple subscriber that records the latest simulation events.
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `connect(self, publisher: TelemetryPublisher) -> None` — No docstring provided.
    - `_record(self, events: list[dict[str, object]]) -> None` — No docstring provided.
    - `latest(self) -> list[dict[str, object]]` — No docstring provided.
- **TelemetryBridge(object)** — Provides access to the latest telemetry snapshots for console consumers.
  - Methods:
    - `__init__(self, publisher: TelemetryPublisher) -> None` — No docstring provided.
    - `snapshot(self) -> dict[str, dict[str, object]]` — No docstring provided.
    - `relationship_summary_payload(self) -> dict[str, object]` — Return normalised relationship summary data for console consumers.
    - `relationship_detail_payload(self, agent_id: str) -> dict[str, object]` — Expose ledger metrics and recent updates for the requested agent.
    - `social_events_payload(self, limit: int | None = None) -> list[dict[str, object]]` — Return a bounded list of the most recent social events.

### Functions
- `create_console_router(publisher: TelemetryPublisher, world: WorldState | None = None, scheduler: PerturbationScheduler | None = None, promotion: PromotionManager | None = None, *, policy: PolicyRuntime | None = None, mode: str = 'viewer', config: SimulationConfig | None = None, lifecycle: LifecycleManager | None = None) -> ConsoleRouter` — No docstring provided.
- `_schema_metadata(publisher: TelemetryPublisher) -> tuple[str, str | None]` — No docstring provided.

### Constants and Configuration
- `SUPPORTED_SCHEMA_PREFIX` = '0.9'
- `SUPPORTED_SCHEMA_LABEL` = f'{SUPPORTED_SCHEMA_PREFIX}.x'

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.lifecycle.manager, townlet.policy.runner, townlet.scheduler.perturbations, townlet.snapshots, townlet.stability.promotion, townlet.telemetry.publisher, townlet.world.grid

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/core/__init__.py

- **File path**: `src/townlet/core/__init__.py`
- **Purpose**: Core orchestration utilities.
- **Dependencies**: stdlib [__future__] / third-party [sim_loop] / internal [None]
- **Related modules**: None
- **Lines of code**: 7
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: sim_loop
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/core/sim_loop.py

- **File path**: `src/townlet/core/sim_loop.py`
- **Purpose**: Top-level simulation loop wiring.
- **Dependencies**: stdlib [__future__, collections.abc, dataclasses, hashlib, importlib, logging, pathlib, random, time, typing] / third-party [None] / internal [townlet.config, townlet.lifecycle.manager, townlet.observations.builder, townlet.policy.runner, townlet.rewards.engine, townlet.scheduler.perturbations, townlet.snapshots, townlet.stability.monitor, townlet.stability.promotion, townlet.telemetry.publisher, townlet.utils, townlet.world.affordances, townlet.world.grid]
- **Related modules**: townlet.config, townlet.lifecycle.manager, townlet.observations.builder, townlet.policy.runner, townlet.rewards.engine, townlet.scheduler.perturbations, townlet.snapshots, townlet.stability.monitor, townlet.stability.promotion, townlet.telemetry.publisher, townlet.utils, townlet.world.affordances, townlet.world.grid
- **Lines of code**: 325
- **Environment variables**: None detected

### Classes
- **TickArtifacts(object)** — Collects per-tick data for logging and testing.
  - Attributes:
    - `observations` (type=dict[str, object])
    - `rewards` (type=dict[str, float])
  - Methods: None
- **SimulationLoop(object)** — Orchestrates the Townlet simulation tick-by-tick.
  - Methods:
    - `__init__(self, config: SimulationConfig, *, affordance_runtime_factory: Callable[[WorldState, AffordanceRuntimeContext], DefaultAffordanceRuntime] | None = None) -> None` — No docstring provided.
    - `_build_components(self) -> None` — No docstring provided.
    - `reset(self) -> None` — Reset the simulation loop to its initial state.
    - `set_anneal_ratio(self, ratio: float | None) -> None` — No docstring provided.
    - `save_snapshot(self, root: Path | None = None) -> Path` — Persist the current world relationships and tick to ``root``.
    - `load_snapshot(self, path: Path) -> None` — Restore world relationships and tick from the snapshot at ``path``.
    - `run(self, max_ticks: int | None = None) -> Iterable[TickArtifacts]` — Run the loop until `max_ticks` or indefinitely.
    - `run_for(self, max_ticks: int) -> None` — Execute exactly ``max_ticks`` iterations of the simulation loop.
    - `step(self) -> TickArtifacts` — No docstring provided.
    - `_load_affordance_runtime_factory(self, runtime_config: AffordanceRuntimeConfig) -> Callable[[WorldState, AffordanceRuntimeContext], DefaultAffordanceRuntime] | None` — No docstring provided.
    - `_import_symbol(path: str)` — No docstring provided.
    - `_derive_seed(self, stream: str) -> int` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.lifecycle.manager, townlet.observations.builder, townlet.policy.runner, townlet.rewards.engine, townlet.scheduler.perturbations, townlet.snapshots, townlet.stability.monitor, townlet.stability.promotion, townlet.telemetry.publisher, townlet.utils, townlet.world.affordances, townlet.world.grid

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/demo/__init__.py

- **File path**: `src/townlet/demo/__init__.py`
- **Purpose**: Utilities for packaging scripted demo runs.
- **Dependencies**: stdlib [None] / third-party [timeline] / internal [None]
- **Related modules**: None
- **Lines of code**: 9
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: timeline
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/demo/runner.py

- **File path**: `src/townlet/demo/runner.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, dataclasses, logging, typing] / third-party [None] / internal [townlet.core.sim_loop, townlet.demo.timeline, townlet.world.grid, townlet_ui.commands, townlet_ui.dashboard]
- **Related modules**: townlet.core.sim_loop, townlet.demo.timeline, townlet.world.grid, townlet_ui.commands, townlet_ui.dashboard
- **Lines of code**: 205
- **Environment variables**: None detected

### Classes
- **DemoScheduler(object)** — Executes scheduled commands or scripted actions during the demo.
  - Attributes:
    - `timeline` (type=DemoTimeline)
    - `palette_state` (type=PaletteState | None, default=None)
  - Methods:
    - `on_tick(self, loop: SimulationLoop, executor: ConsoleCommandExecutor, tick: int) -> None` — No docstring provided.
    - `_execute_action(self, world: WorldState, command: ScheduledCommand) -> str` — No docstring provided.

### Functions
- `seed_demo_state(world: WorldState, *, agents_required: int = 3, history_window: int | None = 30) -> None` — Populate world with starter agents, relationships, and history for demos.
- `default_timeline() -> DemoTimeline` — No docstring provided.
- `run_demo_dashboard(loop: SimulationLoop, *, refresh_interval: float, max_ticks: int, timeline: DemoTimeline, palette_state: PaletteState | None) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.core.sim_loop, townlet.demo.timeline, townlet.world.grid, townlet_ui.commands, townlet_ui.dashboard

### Code Quality Notes
- Missing module docstring.


## src/townlet/demo/timeline.py

- **File path**: `src/townlet/demo/timeline.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, dataclasses, json, pathlib, typing] / third-party [yaml] / internal [None]
- **Related modules**: None
- **Lines of code**: 118
- **Environment variables**: None detected

### Classes
- **ScheduledCommand(object)** — Represents an item scheduled for a specific simulation tick.
  - Attributes:
    - `tick` (type=int)
    - `name` (type=str)
    - `kind` (type=str, default='console')
    - `args` (type=tuple[Any, ...], default=())
    - `kwargs` (type=dict[str, Any] | None, default=None)
  - Methods:
    - `payload(self) -> dict[str, Any]` — No docstring provided.
- **DemoTimeline(object)** — Ordered queue of scheduled console commands for demos.
  - Methods:
    - `__init__(self, commands: Iterable[ScheduledCommand]) -> None` — No docstring provided.
    - `__bool__(self) -> bool` — No docstring provided.
    - `remaining(self) -> int` — No docstring provided.
    - `pop_due(self, current_tick: int) -> list[ScheduledCommand]` — No docstring provided.
    - `upcoming(self) -> Iterator[ScheduledCommand]` — No docstring provided.
    - `next_tick(self) -> int | None` — No docstring provided.

### Functions
- `load_timeline(path: Path) -> DemoTimeline` — Load a demo timeline from YAML or JSON configuration.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: yaml
- Internal: None

### Code Quality Notes
- Missing module docstring.


## src/townlet/lifecycle/__init__.py

- **File path**: `src/townlet/lifecycle/__init__.py`
- **Purpose**: Lifecycle management utilities.
- **Dependencies**: stdlib [__future__] / third-party [manager] / internal [None]
- **Related modules**: None
- **Lines of code**: 7
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: manager
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/lifecycle/manager.py

- **File path**: `src/townlet/lifecycle/manager.py`
- **Purpose**: Agent lifecycle enforcement (exits, spawns, cooldowns).
- **Dependencies**: stdlib [__future__, dataclasses, typing] / third-party [None] / internal [townlet.config, townlet.world.grid]
- **Related modules**: townlet.config, townlet.world.grid
- **Lines of code**: 168
- **Environment variables**: None detected

### Classes
- **_RespawnTicket(object)** — No docstring provided.
  - Attributes:
    - `agent_id` (type=str)
    - `scheduled_tick` (type=int)
    - `blueprint` (type=dict[str, Any])
  - Methods: None
- **LifecycleManager(object)** — Centralises lifecycle checks as outlined in the conceptual design snapshot.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `evaluate(self, world: WorldState, tick: int) -> dict[str, bool]` — Return a map of agent_id -> terminated flag.
    - `finalize(self, world: WorldState, tick: int, terminated: dict[str, bool]) -> None` — No docstring provided.
    - `process_respawns(self, world: WorldState, tick: int) -> None` — No docstring provided.
    - `set_respawn_delay(self, ticks: int) -> None` — No docstring provided.
    - `set_mortality_enabled(self, enabled: bool) -> None` — No docstring provided.
    - `export_state(self) -> dict[str, int]` — No docstring provided.
    - `import_state(self, payload: dict[str, object]) -> None` — No docstring provided.
    - `reset_state(self) -> None` — No docstring provided.
    - `termination_reasons(self) -> dict[str, str]` — Return termination reasons captured during the last evaluation.
    - `_evaluate_employment(self, world: WorldState, tick: int) -> dict[str, bool]` — No docstring provided.
    - `_employment_execute_exit(self, world: WorldState, agent_id: str, tick: int, *, reason: str) -> bool` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.world.grid

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/observations/__init__.py

- **File path**: `src/townlet/observations/__init__.py`
- **Purpose**: Observation builders and utilities.
- **Dependencies**: stdlib [__future__] / third-party [builder] / internal [None]
- **Related modules**: None
- **Lines of code**: 7
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: builder
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/observations/builder.py

- **File path**: `src/townlet/observations/builder.py`
- **Purpose**: Observation encoding across variants.
- **Dependencies**: stdlib [__future__, collections.abc, hashlib, math, typing] / third-party [numpy] / internal [townlet.config, townlet.world.grid]
- **Related modules**: townlet.config, townlet.world.grid
- **Lines of code**: 673
- **Environment variables**: None detected

### Classes
- **ObservationBuilder(object)** — Constructs per-agent observation payloads.
  - Attributes:
    - `MAP_CHANNELS` (default=('self', 'agents', 'objects', 'reservations'))
    - `SHIFT_STATES` (default=('pre_shift', 'on_time', 'late', 'absent', 'post_shift'))
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `build_batch(self, world: 'WorldState', terminated: dict[str, bool]) -> dict[str, dict[str, np.ndarray]]` — Return a mapping from agent_id to observation payloads.
    - `_encode_common_features(self, features: np.ndarray, *, context: dict[str, object], slot: int, snapshot: 'AgentSnapshot', world_tick: int) -> None` — No docstring provided.
    - `_encode_rivalry(self, features: np.ndarray, world: 'WorldState', snapshot: 'AgentSnapshot') -> None` — No docstring provided.
    - `_encode_environmental_flags(self, features: np.ndarray, world: 'WorldState', snapshot: 'AgentSnapshot') -> None` — No docstring provided.
    - `_encode_path_hint(self, features: np.ndarray, world: 'WorldState', snapshot: 'AgentSnapshot') -> None` — No docstring provided.
    - `_initialise_feature_vector(self, world: 'WorldState', snapshot: 'AgentSnapshot', slot: int) -> tuple[np.ndarray, dict[str, object]]` — No docstring provided.
    - `_build_metadata(self, *, slot: int, map_shape: tuple[int, int, int], map_channels: tuple[str, ...] | list[str], social_context: dict[str, object] | None = None) -> dict[str, object]` — No docstring provided.
    - `_build_single(self, world: 'WorldState', snapshot: 'AgentSnapshot', slot: int) -> dict[str, np.ndarray | dict[str, object]]` — No docstring provided.
    - `_map_from_view(self, channels: tuple[str, ...], local_view: dict[str, object], window: int, center: int, snapshot: 'AgentSnapshot') -> np.ndarray` — No docstring provided.
    - `_build_hybrid(self, world: 'WorldState', snapshot: 'AgentSnapshot', slot: int) -> dict[str, np.ndarray | dict[str, object]]` — No docstring provided.
    - `_build_full(self, world: 'WorldState', snapshot: 'AgentSnapshot', slot: int) -> dict[str, np.ndarray | dict[str, object]]` — No docstring provided.
    - `_build_compact(self, world: 'WorldState', snapshot: 'AgentSnapshot', slot: int) -> dict[str, np.ndarray | dict[str, object]]` — No docstring provided.
    - `_build_social_vector(self, world: 'WorldState', snapshot: 'AgentSnapshot') -> tuple[np.ndarray, dict[str, object]]` — No docstring provided.
    - `_collect_social_slots(self, world: 'WorldState', snapshot: 'AgentSnapshot') -> tuple[list[dict[str, float]], dict[str, object]]` — No docstring provided.
    - `_resolve_relationships(self, world: 'WorldState', agent_id: str) -> tuple[list[dict[str, float]], str]` — No docstring provided.
    - `_encode_landmarks(self, features: np.ndarray, world: 'WorldState', snapshot: 'AgentSnapshot') -> None` — No docstring provided.
    - `_encode_relationship(self, entry: dict[str, float]) -> dict[str, float]` — No docstring provided.
    - `_empty_relationship_entry(self) -> dict[str, float]` — No docstring provided.
    - `_embed_agent_id(self, other_id: str) -> np.ndarray` — No docstring provided.
    - `_compute_aggregates(self, trust_values: Iterable[float], rivalry_values: Iterable[float]) -> tuple[float, float, float, float]` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy
- Internal: townlet.config, townlet.world.grid

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/observations/embedding.py

- **File path**: `src/townlet/observations/embedding.py`
- **Purpose**: Embedding slot allocation with cooldown logging.
- **Dependencies**: stdlib [__future__, dataclasses] / third-party [None] / internal [townlet.config]
- **Related modules**: townlet.config
- **Lines of code**: 160
- **Environment variables**: None detected

### Classes
- **_SlotState(object)** — Tracks release metadata for a slot.
  - Attributes:
    - `released_at_tick` (type=int | None, default=None)
  - Methods: None
- **EmbeddingAllocator(object)** — Assigns stable embedding slots to agents with a reuse cooldown.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `allocate(self, agent_id: str, tick: int) -> int` — Return the embedding slot for the agent, allocating if necessary.
    - `release(self, agent_id: str, tick: int) -> None` — Release the slot held by the agent.
    - `has_assignment(self, agent_id: str) -> bool` — Return whether the allocator still tracks the agent.
    - `metrics(self) -> dict[str, float]` — Expose allocation metrics for telemetry.
    - `export_state(self) -> dict[str, object]` — Serialise allocator bookkeeping for snapshot persistence.
    - `import_state(self, payload: dict[str, object]) -> None` — Restore allocator bookkeeping from snapshot data.
    - `_select_slot(self, tick: int) -> tuple[int, bool]` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/policy/__init__.py

- **File path**: `src/townlet/policy/__init__.py`
- **Purpose**: Policy integration layer.
- **Dependencies**: stdlib [__future__] / third-party [bc, runner] / internal [None]
- **Related modules**: None
- **Lines of code**: 22
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: bc, runner
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/policy/bc.py

- **File path**: `src/townlet/policy/bc.py`
- **Purpose**: Behaviour cloning utilities.
- **Dependencies**: stdlib [__future__, collections.abc, dataclasses, json, pathlib] / third-party [numpy, torch, torch.utils.data] / internal [townlet.policy.models, townlet.policy.replay]
- **Related modules**: townlet.policy.models, townlet.policy.replay
- **Lines of code**: 201
- **Environment variables**: None detected

### Classes
- **BCTrainingConfig(object)** — No docstring provided.
  - Attributes:
    - `learning_rate` (type=float, default=0.001)
    - `batch_size` (type=int, default=64)
    - `epochs` (type=int, default=5)
    - `weight_decay` (type=float, default=0.0)
    - `device` (type=str, default='cpu')
  - Methods: None
- **BCDatasetConfig(object)** — No docstring provided.
  - Attributes:
    - `manifest` (type=Path)
  - Methods: None
- **BCTrajectoryDataset(Dataset)** — Torch dataset flattening replay samples for behaviour cloning.
  - Methods:
    - `__init__(self, samples: Sequence[ReplaySample]) -> None` — No docstring provided.
    - `__len__(self) -> int` — No docstring provided.
    - `__getitem__(self, index: int)` — No docstring provided.
- **BCTrainer(object)** — Lightweight supervised trainer for behaviour cloning.
  - Methods:
    - `__init__(self, config: BCTrainingConfig, policy_config: ConflictAwarePolicyConfig) -> None` — No docstring provided.
    - `fit(self, dataset: BCTrajectoryDataset) -> Mapping[str, float]` — No docstring provided.
    - `evaluate(self, dataset: BCTrajectoryDataset) -> Mapping[str, float]` — No docstring provided.

### Functions
- `load_bc_samples(manifest_path: Path) -> list[ReplaySample]` — No docstring provided.
- `evaluate_bc_policy(model: ConflictAwarePolicyNetwork, dataset: BCTrajectoryDataset, device: str = 'cpu') -> Mapping[str, float]` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy, torch, torch.utils.data
- Internal: townlet.policy.models, townlet.policy.replay

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/policy/behavior.py

- **File path**: `src/townlet/policy/behavior.py`
- **Purpose**: Behavior controller interfaces for scripted decision logic.
- **Dependencies**: stdlib [__future__, dataclasses, typing] / third-party [None] / internal [townlet.config, townlet.world.grid]
- **Related modules**: townlet.config, townlet.world.grid
- **Lines of code**: 301
- **Environment variables**: None detected

### Classes
- **AgentIntent(object)** — Represents the next action an agent wishes to perform.
  - Attributes:
    - `kind` (type=str)
    - `object_id` (type=Optional[str], default=None)
    - `affordance_id` (type=Optional[str], default=None)
    - `blocked` (type=bool, default=False)
    - `position` (type=Optional[tuple[int, int]], default=None)
    - `target_agent` (type=Optional[str], default=None)
    - `quality` (type=Optional[float], default=None)
  - Methods: None
- **BehaviorController(Protocol)** — Defines the interface for agent decision logic.
  - Methods:
    - `decide(self, world: WorldState, agent_id: str) -> AgentIntent` — No docstring provided.
- **IdleBehavior(BehaviorController)** — Default no-op behavior that keeps agents idle.
  - Methods:
    - `decide(self, world: WorldState, agent_id: str) -> AgentIntent` — No docstring provided.
- **ScriptedBehavior(BehaviorController)** — Simple rule-based controller used before RL policies are available.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `decide(self, world: WorldState, agent_id: str) -> AgentIntent` — No docstring provided.
    - `cancel_pending(self, agent_id: str) -> None` — No docstring provided.
    - `_cleanup_pending(self, world: WorldState, agent_id: str) -> None` — No docstring provided.
    - `_maybe_move_to_job(self, world: WorldState, agent_id: str, snapshot: object) -> Optional[AgentIntent]` — No docstring provided.
    - `_satisfy_needs(self, world: WorldState, agent_id: str, snapshot: object) -> Optional[AgentIntent]` — No docstring provided.
    - `_maybe_chat(self, world: WorldState, agent_id: str, snapshot: object) -> Optional[AgentIntent]` — No docstring provided.
    - `_avoid_rivals(self, world: WorldState, agent_id: str, snapshot: object) -> Optional[AgentIntent]` — No docstring provided.
    - `_rivals_in_queue(self, world: WorldState, agent_id: str, object_id: str) -> bool` — No docstring provided.
    - `_plan_meal(self, world: WorldState, agent_id: str) -> Optional[AgentIntent]` — No docstring provided.
    - `_find_object_of_type(self, world: WorldState, object_type: str) -> Optional[str]` — No docstring provided.

### Functions
- `build_behavior(config: SimulationConfig) -> BehaviorController` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.world.grid

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/policy/metrics.py

- **File path**: `src/townlet/policy/metrics.py`
- **Purpose**: Utility helpers for replay and rollout metrics.
- **Dependencies**: stdlib [__future__, json, typing] / third-party [numpy, replay] / internal [None]
- **Related modules**: None
- **Lines of code**: 108
- **Environment variables**: None detected

### Classes
- None

### Functions
- `compute_sample_metrics(sample: ReplaySample) -> dict[str, float]` — Compute summary metrics for a replay sample.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy, replay
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/policy/models.py

- **File path**: `src/townlet/policy/models.py`
- **Purpose**: Torch-based policy/value networks for Townlet PPO.
- **Dependencies**: stdlib [__future__, dataclasses] / third-party [torch, torch.nn] / internal [None]
- **Related modules**: None
- **Lines of code**: 83
- **Environment variables**: None detected

### Classes
- **TorchNotAvailableError(RuntimeError)** — Raised when a Torch-dependent component is used without PyTorch.
  - Methods: None
- **ConflictAwarePolicyConfig(object)** — No docstring provided.
  - Attributes:
    - `feature_dim` (type=int)
    - `map_shape` (type=tuple[int, int, int])
    - `action_dim` (type=int)
    - `hidden_dim` (type=int, default=256)
  - Methods: None

### Functions
- `torch_available() -> bool` — Return True if PyTorch is available in the runtime.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: torch, torch.nn
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/policy/ppo/__init__.py

- **File path**: `src/townlet/policy/ppo/__init__.py`
- **Purpose**: PPO utilities package.
- **Dependencies**: stdlib [None] / third-party [utils] / internal [None]
- **Related modules**: None
- **Lines of code**: 19
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: utils
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/policy/ppo/utils.py

- **File path**: `src/townlet/policy/ppo/utils.py`
- **Purpose**: Utility functions for PPO advantage and loss computation.
- **Dependencies**: stdlib [__future__, dataclasses] / third-party [torch] / internal [None]
- **Related modules**: None
- **Lines of code**: 140
- **Environment variables**: None detected

### Classes
- **AdvantageReturns(object)** — Container for PPO advantage and return tensors.
  - Attributes:
    - `advantages` (type=torch.Tensor)
    - `returns` (type=torch.Tensor)
  - Methods: None

### Functions
- `compute_gae(rewards: torch.Tensor, value_preds: torch.Tensor, dones: torch.Tensor, gamma: float, gae_lambda: float) -> AdvantageReturns` — Compute Generalized Advantage Estimation (GAE).
- `normalize_advantages(advantages: torch.Tensor, eps: float = 1e-08) -> torch.Tensor` — Normalize advantage estimates to zero mean/unit variance.
- `value_baseline_from_old_preds(value_preds: torch.Tensor, timesteps: int) -> torch.Tensor` — Extract baseline values aligned with each timestep from stored predictions.
- `clipped_value_loss(new_values: torch.Tensor, returns: torch.Tensor, old_values: torch.Tensor, value_clip: float) -> torch.Tensor` — Compute the clipped value loss term.
- `policy_surrogate(new_log_probs: torch.Tensor, old_log_probs: torch.Tensor, advantages: torch.Tensor, clip_param: float) -> tuple[torch.Tensor, torch.Tensor]` — Compute PPO clipped policy loss and clip fraction.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: torch
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/policy/replay.py

- **File path**: `src/townlet/policy/replay.py`
- **Purpose**: Utilities for replaying observation/telemetry samples.
- **Dependencies**: stdlib [__future__, collections.abc, dataclasses, json, pathlib, typing] / third-party [numpy, yaml] / internal [None]
- **Related modules**: None
- **Lines of code**: 641
- **Environment variables**: None detected

### Classes
- **ReplaySample(object)** — Container for observation samples used in training replays.
  - Attributes:
    - `map` (type=np.ndarray)
    - `features` (type=np.ndarray)
    - `actions` (type=np.ndarray)
    - `old_log_probs` (type=np.ndarray)
    - `value_preds` (type=np.ndarray)
    - `rewards` (type=np.ndarray)
    - `dones` (type=np.ndarray)
    - `metadata` (type=dict[str, Any])
  - Methods:
    - `__post_init__(self) -> None` — No docstring provided.
    - `feature_names(self) -> Optional[list[str]]` — No docstring provided.
    - `conflict_stats(self) -> dict[str, float]` — No docstring provided.
- **ReplayBatch(object)** — Mini-batch representation composed from replay samples.
  - Attributes:
    - `maps` (type=np.ndarray)
    - `features` (type=np.ndarray)
    - `actions` (type=np.ndarray)
    - `old_log_probs` (type=np.ndarray)
    - `value_preds` (type=np.ndarray)
    - `rewards` (type=np.ndarray)
    - `dones` (type=np.ndarray)
    - `metadata` (type=dict[str, Any])
  - Methods:
    - `__post_init__(self) -> None` — No docstring provided.
    - `conflict_stats(self) -> dict[str, float]` — No docstring provided.
- **ReplayDatasetConfig(object)** — Configuration for building replay datasets.
  - Attributes:
    - `entries` (type=list[tuple[Path, Optional[Path]]])
    - `batch_size` (type=int, default=1)
    - `shuffle` (type=bool, default=False)
    - `seed` (type=Optional[int], default=None)
    - `drop_last` (type=bool, default=False)
    - `streaming` (type=bool, default=False)
    - `metrics_map` (type=Optional[dict[str, dict[str, float]]], default=None)
    - `label` (type=Optional[str], default=None)
  - Methods:
    - `from_manifest(cls, manifest_path: Path, batch_size: int = 1, shuffle: bool = False, seed: Optional[int] = None, drop_last: bool = False, streaming: bool = False) -> 'ReplayDatasetConfig'` — No docstring provided.
    - `from_capture_dir(cls, capture_dir: Path, batch_size: int = 1, shuffle: bool = False, seed: Optional[int] = None, drop_last: bool = False, streaming: bool = False) -> 'ReplayDatasetConfig'` — No docstring provided.
- **ReplayDataset(object)** — Iterable dataset producing conflict-aware replay batches.
  - Methods:
    - `__init__(self, config: ReplayDatasetConfig) -> None` — No docstring provided.
    - `_ensure_homogeneous(self, samples: Sequence[ReplaySample]) -> None` — No docstring provided.
    - `__len__(self) -> int` — No docstring provided.
    - `__iter__(self) -> Iterator[ReplayBatch]` — No docstring provided.
    - `_fetch_sample(self, index: int) -> ReplaySample` — No docstring provided.
    - `_ensure_sample_metrics(self, sample: ReplaySample, entry: tuple[Path, Optional[Path]]) -> None` — No docstring provided.
    - `_aggregate_metrics(self) -> dict[str, float]` — No docstring provided.

### Functions
- `_ensure_conflict_features(metadata: dict[str, Any]) -> None` — No docstring provided.
- `load_replay_sample(sample_path: Path, meta_path: Optional[Path] = None) -> ReplaySample` — Load observation tensors and metadata for replay-driven training scaffolds.
- `build_batch(samples: Sequence[ReplaySample]) -> ReplayBatch` — Stack multiple replay samples into a batch for training consumers.
- `_resolve_manifest_path(path_spec: Path, base: Path) -> Path` — Resolve manifest path specs that may be absolute or repo-relative.
- `_load_manifest(manifest_path: Path) -> list[tuple[Path, Optional[Path]]]` — No docstring provided.
- `frames_to_replay_sample(frames: Sequence[dict[str, Any]]) -> ReplaySample` — Convert collected trajectory frames into a replay sample.

### Constants and Configuration
- `REQUIRED_CONFLICT_FEATURES` = ('rivalry_max', 'rivalry_avoid_count')
- `STEP_ARRAY_FIELDS` = ('actions', 'old_log_probs', 'rewards', 'dones')
- `TRAINING_ARRAY_FIELDS` = STEP_ARRAY_FIELDS + ('value_preds',)

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy, yaml
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/policy/replay_buffer.py

- **File path**: `src/townlet/policy/replay_buffer.py`
- **Purpose**: In-memory replay dataset used for rollout captures.
- **Dependencies**: stdlib [__future__, collections.abc, dataclasses] / third-party [None] / internal [townlet.policy.replay]
- **Related modules**: townlet.policy.replay
- **Lines of code**: 62
- **Environment variables**: None detected

### Classes
- **InMemoryReplayDatasetConfig(object)** — No docstring provided.
  - Attributes:
    - `entries` (type=Sequence[ReplaySample])
    - `batch_size` (type=int, default=1)
    - `drop_last` (type=bool, default=False)
    - `rollout_ticks` (type=int, default=0)
    - `label` (type=str | None, default=None)
  - Methods: None
- **InMemoryReplayDataset(object)** — No docstring provided.
  - Methods:
    - `__init__(self, config: InMemoryReplayDatasetConfig) -> None` — No docstring provided.
    - `_validate_shapes(self) -> None` — No docstring provided.
    - `__iter__(self) -> Iterator[ReplayBatch]` — No docstring provided.
    - `__len__(self) -> int` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.policy.replay

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/policy/rollout.py

- **File path**: `src/townlet/policy/rollout.py`
- **Purpose**: Rollout buffer scaffolding for future live PPO integration.
- **Dependencies**: stdlib [__future__, collections.abc, dataclasses, json, pathlib] / third-party [numpy] / internal [townlet.policy.metrics, townlet.policy.replay, townlet.policy.replay_buffer]
- **Related modules**: townlet.policy.metrics, townlet.policy.replay, townlet.policy.replay_buffer
- **Lines of code**: 206
- **Environment variables**: None detected

### Classes
- **AgentRollout(object)** — No docstring provided.
  - Attributes:
    - `agent_id` (type=str)
    - `frames` (type=list[dict[str, object]], default=field(default_factory=list))
  - Methods:
    - `append(self, frame: dict[str, object]) -> None` — No docstring provided.
    - `to_replay_sample(self) -> ReplaySample` — No docstring provided.
- **RolloutBuffer(object)** — Collects trajectory frames and exposes helpers to save or replay them.
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `record_events(self, events: Iterable[dict[str, object]]) -> None` — No docstring provided.
    - `extend(self, frames: Iterable[dict[str, object]]) -> None` — No docstring provided.
    - `__len__(self) -> int` — No docstring provided.
    - `by_agent(self) -> dict[str, AgentRollout]` — No docstring provided.
    - `to_samples(self) -> dict[str, ReplaySample]` — No docstring provided.
    - `save(self, output_dir: Path, prefix: str = 'rollout_sample', compress: bool = True) -> None` — No docstring provided.
    - `build_dataset(self, batch_size: int = 1, drop_last: bool = False) -> InMemoryReplayDataset` — No docstring provided.
    - `is_empty(self) -> bool` — No docstring provided.
    - `set_tick_count(self, ticks: int) -> None` — No docstring provided.
    - `_aggregate_metrics(self, samples: list[ReplaySample]) -> dict[str, float]` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy
- Internal: townlet.policy.metrics, townlet.policy.replay, townlet.policy.replay_buffer

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/policy/runner.py

- **File path**: `src/townlet/policy/runner.py`
- **Purpose**: Policy orchestration scaffolding.
- **Dependencies**: stdlib [__future__, collections.abc, json, math, pathlib, random, statistics, time, typing] / third-party [numpy, torch, torch.distributions, torch.nn.utils] / internal [townlet.config, townlet.core.sim_loop, townlet.policy.bc, townlet.policy.behavior, townlet.policy.models, townlet.policy.ppo.utils, townlet.policy.replay, townlet.policy.replay_buffer, townlet.policy.rollout, townlet.policy.scenario_utils, townlet.stability.promotion, townlet.world.grid]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.policy.bc, townlet.policy.behavior, townlet.policy.models, townlet.policy.ppo.utils, townlet.policy.replay, townlet.policy.replay_buffer, townlet.policy.rollout, townlet.policy.scenario_utils, townlet.stability.promotion, townlet.world.grid
- **Lines of code**: 1481
- **Environment variables**: None detected

### Classes
- **PolicyRuntime(object)** — Bridges the simulation with PPO/backends via PettingZoo.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `seed_anneal_rng(self, seed: int) -> None` — No docstring provided.
    - `set_anneal_ratio(self, ratio: float | None) -> None` — No docstring provided.
    - `enable_anneal_blend(self, enabled: bool) -> None` — No docstring provided.
    - `register_ctx_reset_callback(self, callback: Callable[[str], None] | None) -> None` — No docstring provided.
    - `set_policy_action_provider(self, provider: Callable[[WorldState, str, AgentIntent], AgentIntent | None]) -> None` — No docstring provided.
    - `decide(self, world: WorldState, tick: int) -> dict[str, object]` — Return a primitive action per agent.
    - `post_step(self, rewards: dict[str, float], terminated: dict[str, bool]) -> None` — Record rewards and termination signals into buffers.
    - `flush_transitions(self, observations: dict[str, dict[str, object]]) -> list[dict[str, object]]` — Combine stored transition data with observations and return trajectory frames.
    - `collect_trajectory(self, clear: bool = True) -> list[dict[str, object]]` — Return accumulated trajectory frames and reset internal buffer.
    - `consume_option_switch_counts(self) -> dict[str, int]` — Return per-agent option switch counts accumulated since last call.
    - `acquire_possession(self, agent_id: str) -> bool` — No docstring provided.
    - `release_possession(self, agent_id: str) -> bool` — No docstring provided.
    - `is_possessed(self, agent_id: str) -> bool` — No docstring provided.
    - `possessed_agents(self) -> list[str]` — No docstring provided.
    - `reset_state(self) -> None` — Reset transient buffers so snapshot loads don’t duplicate data.
    - `_select_intent_with_blend(self, world: WorldState, agent_id: str, scripted: AgentIntent) -> AgentIntent` — No docstring provided.
    - `_apply_relationship_guardrails(self, world: WorldState, agent_id: str, intent: AgentIntent) -> AgentIntent` — No docstring provided.
    - `_clone_intent(intent: AgentIntent) -> AgentIntent` — No docstring provided.
    - `_intents_match(lhs: AgentIntent, rhs: AgentIntent) -> bool` — No docstring provided.
    - `_enforce_option_commit(self, agent_id: str, tick: int, intent: AgentIntent) -> tuple[AgentIntent, bool]` — No docstring provided.
    - `_annotate_with_policy_outputs(self, frame: dict[str, object]) -> None` — No docstring provided.
    - `_update_policy_snapshot(self, frames: list[dict[str, object]]) -> None` — No docstring provided.
    - `latest_policy_snapshot(self) -> dict[str, dict[str, object]]` — No docstring provided.
    - `active_policy_hash(self) -> str | None` — Return the configured policy hash, if any.
    - `set_policy_hash(self, value: str | None) -> None` — Set the policy hash after loading a checkpoint.
    - `current_anneal_ratio(self) -> float | None` — Return the latest anneal ratio (0..1) if tracking available.
    - `set_anneal_ratio(self, ratio: float | None) -> None` — No docstring provided.
    - `_ensure_policy_network(self, map_shape: tuple[int, int, int], feature_dim: int, action_dim: int) -> bool` — No docstring provided.
    - `_build_policy_network(self, feature_dim: int, map_shape: tuple[int, int, int], action_dim: int) -> ConflictAwarePolicyNetwork` — No docstring provided.
- **TrainingHarness(object)** — Coordinates RL training sessions.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `run(self) -> None` — Entry point for CLI training runs based on config.training.source.
    - `current_anneal_ratio(self) -> float | None` — No docstring provided.
    - `set_anneal_ratio(self, ratio: float | None) -> None` — No docstring provided.
    - `run_replay(self, sample_path: Path, meta_path: Path | None = None) -> dict[str, float]` — Load a replay observation sample and surface conflict-aware stats.
    - `run_replay_batch(self, pairs: Iterable[tuple[Path, Path | None]]) -> dict[str, float]` — No docstring provided.
    - `run_replay_dataset(self, dataset_config: ReplayDatasetConfig) -> dict[str, float]` — No docstring provided.
    - `capture_rollout(self, ticks: int, auto_seed_agents: bool = False, output_dir: Path | None = None, prefix: str = 'rollout_sample', compress: bool = True) -> RolloutBuffer` — Run the simulation loop for a fixed number of ticks and collect frames.
    - `run_rollout_ppo(self, ticks: int, batch_size: int = 1, auto_seed_agents: bool = False, output_dir: Path | None = None, prefix: str = 'rollout_sample', compress: bool = True, epochs: int = 1, log_path: Path | None = None, log_frequency: int = 1, max_log_entries: int | None = None) -> dict[str, float]` — No docstring provided.
    - `_load_bc_dataset(self, manifest: Path) -> BCTrajectoryDataset` — No docstring provided.
    - `run_bc_training(self, *, manifest: Path | None = None, config: BCTrainingParams | None = None) -> dict[str, float]` — No docstring provided.
    - `run_anneal(self, *, dataset_config: ReplayDatasetConfig | None = None, in_memory_dataset: InMemoryReplayDataset | None = None, log_dir: Path | None = None, bc_manifest: Path | None = None) -> list[dict[str, object]]` — No docstring provided.
    - `run_ppo(self, dataset_config: ReplayDatasetConfig | None = None, epochs: int = 1, log_path: Path | None = None, log_frequency: int = 1, max_log_entries: int | None = None, in_memory_dataset: InMemoryReplayDataset | None = None) -> dict[str, float]` — No docstring provided.
    - `evaluate_anneal_results(self, results: list[dict[str, object]]) -> str` — No docstring provided.
    - `last_anneal_status(self) -> str | None` — No docstring provided.
    - `_record_promotion_evaluation(self, *, status: str, results: list[dict[str, object]]) -> None` — No docstring provided.
    - `_select_social_reward_stage(self, cycle_id: int) -> str | None` — No docstring provided.
    - `_apply_social_reward_stage(self, cycle_id: int) -> None` — No docstring provided.
    - `_summarise_batch(self, batch: ReplayBatch, batch_index: int) -> dict[str, float]` — No docstring provided.
    - `build_replay_dataset(self, config: ReplayDatasetConfig) -> ReplayDataset` — No docstring provided.
    - `build_policy_network(self, feature_dim: int, map_shape: tuple[int, int, int], action_dim: int, hidden_dim: int | None = None) -> ConflictAwarePolicyNetwork` — No docstring provided.

### Functions
- `_softmax(logits: np.ndarray) -> np.ndarray` — No docstring provided.
- `_pretty_action(action_repr: str) -> str` — No docstring provided.

### Constants and Configuration
- `PPO_TELEMETRY_VERSION` = 1.2
- `ANNEAL_BC_MIN_DEFAULT` = 0.9
- `ANNEAL_LOSS_TOLERANCE_DEFAULT` = 0.1
- `ANNEAL_QUEUE_TOLERANCE_DEFAULT` = 0.15

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy, torch, torch.distributions, torch.nn.utils
- Internal: townlet.config, townlet.core.sim_loop, townlet.policy.bc, townlet.policy.behavior, townlet.policy.models, townlet.policy.ppo.utils, townlet.policy.replay, townlet.policy.replay_buffer, townlet.policy.rollout, townlet.policy.scenario_utils, townlet.stability.promotion, townlet.world.grid

### Code Quality Notes
- Raises `NotImplementedError`, indicating missing behaviour.


## src/townlet/policy/scenario_utils.py

- **File path**: `src/townlet/policy/scenario_utils.py`
- **Purpose**: Helpers for applying scenario initialisation to simulation loops.
- **Dependencies**: stdlib [__future__, logging, typing] / third-party [None] / internal [townlet.core.sim_loop, townlet.policy.behavior, townlet.world.grid]
- **Related modules**: townlet.core.sim_loop, townlet.policy.behavior, townlet.world.grid
- **Lines of code**: 144
- **Environment variables**: None detected

### Classes
- **ScenarioBehavior(object)** — Wraps an existing behavior controller with scripted schedules.
  - Methods:
    - `__init__(self, base_behavior, schedules: dict[str, list[AgentIntent]]) -> None` — No docstring provided.
    - `decide(self, world, agent_id)` — No docstring provided.

### Functions
- `apply_scenario(loop: SimulationLoop, scenario: dict[str, Any]) -> None` — No docstring provided.
- `seed_default_agents(loop: SimulationLoop) -> None` — No docstring provided.
- `has_agents(loop: SimulationLoop) -> bool` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.core.sim_loop, townlet.policy.behavior, townlet.world.grid

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/policy/scripted.py

- **File path**: `src/townlet/policy/scripted.py`
- **Purpose**: Simple scripted policy helpers for trajectory capture.
- **Dependencies**: stdlib [__future__, dataclasses] / third-party [None] / internal [townlet.world.grid]
- **Related modules**: townlet.world.grid
- **Lines of code**: 126
- **Environment variables**: None detected

### Classes
- **ScriptedPolicy(object)** — Base class for scripted policies used during BC trajectory capture.
  - Attributes:
    - `name` (type=str, default='scripted')
  - Methods:
    - `decide(self, world: WorldState, tick: int) -> dict[str, dict]` — No docstring provided.
    - `describe(self) -> str` — No docstring provided.
    - `trajectory_prefix(self) -> str` — No docstring provided.
- **IdlePolicy(ScriptedPolicy)** — Default scripted policy: all agents wait every tick.
  - Attributes:
    - `name` (type=str, default='idle')
  - Methods:
    - `decide(self, world: WorldState, tick: int) -> dict[str, dict]` — No docstring provided.
- **ScriptedPolicyAdapter(object)** — Adapter so SimulationLoop can call scripted policies.
  - Methods:
    - `__init__(self, scripted_policy: ScriptedPolicy) -> None` — No docstring provided.
    - `decide(self, world: WorldState, tick: int) -> dict[str, dict]` — No docstring provided.
    - `post_step(self, rewards: dict[str, float], terminated: dict[str, bool]) -> None` — No docstring provided.
    - `flush_transitions(self, observations) -> None` — No docstring provided.
    - `collect_trajectory(self, *, clear: bool = False)` — No docstring provided.
    - `latest_policy_snapshot(self) -> dict[str, dict[str, object]]` — No docstring provided.
    - `possessed_agents(self) -> list[str]` — No docstring provided.
    - `consume_option_switch_counts(self) -> dict[str, int]` — No docstring provided.
    - `active_policy_hash(self) -> str | None` — No docstring provided.
    - `set_policy_hash(self, value: str | None) -> None` — No docstring provided.
    - `current_anneal_ratio(self) -> float | None` — No docstring provided.
    - `set_anneal_ratio(self, ratio: float | None) -> None` — No docstring provided.
    - `enable_anneal_blend(self, _: bool) -> None` — No docstring provided.

### Functions
- `get_scripted_policy(name: str) -> ScriptedPolicy` — Factory for scripted policies; extend with richer behaviours as needed.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.world.grid

### Code Quality Notes
- Raises `NotImplementedError`, indicating missing behaviour.


## src/townlet/rewards/__init__.py

- **File path**: `src/townlet/rewards/__init__.py`
- **Purpose**: Reward computation utilities.
- **Dependencies**: stdlib [__future__] / third-party [engine] / internal [None]
- **Related modules**: None
- **Lines of code**: 7
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: engine
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/rewards/engine.py

- **File path**: `src/townlet/rewards/engine.py`
- **Purpose**: Reward calculation guardrails and aggregation.
- **Dependencies**: stdlib [__future__, collections.abc] / third-party [None] / internal [townlet.config, townlet.world.grid]
- **Related modules**: townlet.config, townlet.world.grid
- **Lines of code**: 340
- **Environment variables**: None detected

### Classes
- **RewardEngine(object)** — Compute per-agent rewards with clipping and guardrails.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `compute(self, world: WorldState, terminated: dict[str, bool], reasons: Mapping[str, str] | None = None) -> dict[str, float]` — No docstring provided.
    - `_consume_chat_events(self, world: WorldState) -> Iterable[dict[str, object]]` — No docstring provided.
    - `_consume_avoidance_events(self, world: WorldState) -> Iterable[dict[str, object]]` — No docstring provided.
    - `_social_stage_value(self) -> int` — No docstring provided.
    - `_compute_chat_rewards(self, world: WorldState, events: Iterable[dict[str, object]]) -> tuple[dict[str, float], dict[str, float]]` — No docstring provided.
    - `_compute_avoidance_rewards(self, world: WorldState, events: Iterable[dict[str, object]]) -> dict[str, float]` — No docstring provided.
    - `_prepare_social_event_log(self, chat_events: Iterable[dict[str, object]], avoidance_events: Iterable[dict[str, object]]) -> list[dict[str, object]]` — No docstring provided.
    - `_needs_override(self, snapshot) -> bool` — No docstring provided.
    - `_is_blocked(self, agent_id: str, tick: int, window: int) -> bool` — No docstring provided.
    - `_prune_termination_blocks(self, tick: int, window: int) -> None` — No docstring provided.
    - `_compute_wage_bonus(self, agent_id: str, world: WorldState, wage_rate: float) -> float` — No docstring provided.
    - `_compute_punctuality_bonus(self, agent_id: str, world: WorldState, bonus_rate: float) -> float` — No docstring provided.
    - `_compute_terminal_penalty(self, agent_id: str, terminated: Mapping[str, bool], reasons: Mapping[str, str]) -> float` — No docstring provided.
    - `_reset_episode_totals(self, terminated: dict[str, bool], world: WorldState) -> None` — No docstring provided.
    - `latest_reward_breakdown(self) -> dict[str, dict[str, float]]` — No docstring provided.
    - `latest_social_events(self) -> list[dict[str, object]]` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.world.grid

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/scheduler/__init__.py

- **File path**: `src/townlet/scheduler/__init__.py`
- **Purpose**: Schedulers for perturbations and timers.
- **Dependencies**: stdlib [__future__] / third-party [perturbations] / internal [None]
- **Related modules**: None
- **Lines of code**: 7
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: perturbations
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/scheduler/perturbations.py

- **File path**: `src/townlet/scheduler/perturbations.py`
- **Purpose**: Perturbation scheduler scaffolding.
- **Dependencies**: stdlib [__future__, collections.abc, dataclasses, random, typing] / third-party [None] / internal [townlet.config, townlet.utils, townlet.world.grid]
- **Related modules**: townlet.config, townlet.utils, townlet.world.grid
- **Lines of code**: 582
- **Environment variables**: None detected

### Classes
- **ScheduledPerturbation(object)** — Represents a perturbation that is pending or active in the world.
  - Attributes:
    - `event_id` (type=str)
    - `spec_name` (type=str)
    - `kind` (type=PerturbationKind)
    - `started_at` (type=int)
    - `ends_at` (type=int)
    - `payload` (type=dict[str, object], default=field(default_factory=dict))
    - `targets` (type=list[str], default=field(default_factory=list))
  - Methods: None
- **PerturbationScheduler(object)** — Injects bounded random events into the world.
  - Methods:
    - `__init__(self, config: SimulationConfig, *, rng: Optional[random.Random] = None) -> None` — No docstring provided.
    - `pending_count(self) -> int` — No docstring provided.
    - `active_count(self) -> int` — No docstring provided.
    - `tick(self, world: WorldState, current_tick: int) -> None` — No docstring provided.
    - `_expire_active(self, current_tick: int, world: WorldState) -> None` — No docstring provided.
    - `_expire_cooldowns(self, current_tick: int) -> None` — No docstring provided.
    - `_expire_window_events(self, current_tick: int) -> None` — No docstring provided.
    - `_drain_pending(self, world: WorldState, current_tick: int) -> None` — No docstring provided.
    - `_maybe_schedule(self, world: WorldState, current_tick: int) -> None` — No docstring provided.
    - `schedule_manual(self, world: WorldState, spec_name: str, current_tick: int, *, starts_in: int = 0, duration: int | None = None, targets: Optional[list[str]] = None, payload_overrides: Optional[dict[str, object]] = None) -> ScheduledPerturbation` — No docstring provided.
    - `cancel_event(self, world: WorldState, event_id: str) -> bool` — No docstring provided.
    - `_activate(self, world: WorldState, event: ScheduledPerturbation) -> None` — No docstring provided.
    - `_apply_event(self, world: WorldState, event: ScheduledPerturbation) -> None` — No docstring provided.
    - `_on_event_concluded(self, world: WorldState, event: ScheduledPerturbation) -> None` — No docstring provided.
    - `seed(self, value: int) -> None` — No docstring provided.
    - `_can_fire_spec(self, name: str, spec: PerturbationEventConfig, current_tick: int) -> bool` — No docstring provided.
    - `_per_tick_probability(self, spec: PerturbationEventConfig) -> float` — No docstring provided.
    - `_generate_event(self, name: str, spec: PerturbationEventConfig, current_tick: int, world: WorldState, *, duration_override: int | None = None, targets_override: Optional[list[str]] = None, payload_override: Optional[dict[str, object]] = None) -> Optional[ScheduledPerturbation]` — No docstring provided.
    - `_eligible_agents(self, world: WorldState, current_tick: int) -> list[str]` — No docstring provided.
    - `enqueue(self, events: Iterable[ScheduledPerturbation | Mapping[str, object]]) -> None` — No docstring provided.
    - `pending(self) -> list[ScheduledPerturbation]` — No docstring provided.
    - `active(self) -> dict[str, ScheduledPerturbation]` — No docstring provided.
    - `export_state(self) -> dict[str, object]` — No docstring provided.
    - `import_state(self, payload: dict[str, object]) -> None` — No docstring provided.
    - `reset_state(self) -> None` — No docstring provided.
    - `allocate_event_id(self) -> str` — No docstring provided.
    - `spec_for(self, name: str) -> Optional[PerturbationEventConfig]` — No docstring provided.
    - `rng_state(self) -> tuple` — No docstring provided.
    - `set_rng_state(self, state: tuple) -> None` — No docstring provided.
    - `rng(self) -> random.Random` — No docstring provided.
    - `_coerce_event(self, data: Mapping[str, object]) -> ScheduledPerturbation` — No docstring provided.
    - `_serialize_event(event: ScheduledPerturbation) -> dict[str, object]` — No docstring provided.
    - `serialize_event(self, event: ScheduledPerturbation) -> dict[str, object]` — No docstring provided.
    - `latest_state(self) -> dict[str, object]` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.utils, townlet.world.grid

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/snapshots/__init__.py

- **File path**: `src/townlet/snapshots/__init__.py`
- **Purpose**: Snapshot and restore helpers.
- **Dependencies**: stdlib [__future__] / third-party [migrations, state] / internal [None]
- **Related modules**: None
- **Lines of code**: 25
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: migrations, state
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/snapshots/migrations.py

- **File path**: `src/townlet/snapshots/migrations.py`
- **Purpose**: Snapshot migration registry and helpers.
- **Dependencies**: stdlib [__future__, collections, collections.abc, dataclasses, typing] / third-party [None] / internal [townlet.config, townlet.snapshots.state]
- **Related modules**: townlet.config, townlet.snapshots.state
- **Lines of code**: 121
- **Environment variables**: None detected

### Classes
- **MigrationNotFoundError(Exception)** — Raised when no migration path exists between config identifiers.
  - Methods: None
- **MigrationExecutionError(Exception)** — Raised when a migration handler fails or leaves the snapshot unchanged.
  - Methods: None
- **MigrationEdge(object)** — No docstring provided.
  - Attributes:
    - `source` (type=str)
    - `target` (type=str)
    - `handler` (type=MigrationHandler)
  - Methods:
    - `identifier(self) -> str` — No docstring provided.
- **SnapshotMigrationRegistry(object)** — Maintains registered snapshot migrations keyed by config identifiers.
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `register(self, from_config: str, to_config: str, handler: MigrationHandler) -> None` — No docstring provided.
    - `clear(self) -> None` — No docstring provided.
    - `_neighbours(self, node: str) -> Iterable[MigrationEdge]` — No docstring provided.
    - `find_path(self, start: str, goal: str) -> list[MigrationEdge]` — No docstring provided.
    - `apply_path(self, path: list[MigrationEdge], state: 'SnapshotState', config: 'SimulationConfig') -> tuple['SnapshotState', list[str]]` — No docstring provided.

### Functions
- `register_migration(from_config: str, to_config: str, handler: MigrationHandler) -> None` — Register a snapshot migration handler.
- `clear_registry() -> None` — Reset registry (intended for test teardown).

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.snapshots.state

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/snapshots/state.py

- **File path**: `src/townlet/snapshots/state.py`
- **Purpose**: Snapshot persistence scaffolding.
- **Dependencies**: stdlib [__future__, collections.abc, dataclasses, json, logging, pathlib, random, typing] / third-party [None] / internal [townlet.agents.models, townlet.config, townlet.lifecycle.manager, townlet.scheduler.perturbations, townlet.snapshots.migrations, townlet.stability.monitor, townlet.stability.promotion, townlet.telemetry.publisher, townlet.utils, townlet.world.grid]
- **Related modules**: townlet.agents.models, townlet.config, townlet.lifecycle.manager, townlet.scheduler.perturbations, townlet.snapshots.migrations, townlet.stability.monitor, townlet.stability.promotion, townlet.telemetry.publisher, townlet.utils, townlet.world.grid
- **Lines of code**: 649
- **Environment variables**: None detected

### Classes
- **SnapshotState(object)** — No docstring provided.
  - Attributes:
    - `config_id` (type=str)
    - `tick` (type=int)
    - `agents` (type=dict[str, dict[str, object]], default=field(default_factory=dict))
    - `objects` (type=dict[str, dict[str, object]], default=field(default_factory=dict))
    - `queues` (type=dict[str, object], default=field(default_factory=dict))
    - `embeddings` (type=dict[str, object], default=field(default_factory=dict))
    - `employment` (type=dict[str, object], default=field(default_factory=dict))
    - `lifecycle` (type=dict[str, object], default=field(default_factory=dict))
    - `rng_state` (type=Optional[str], default=None)
    - `rng_streams` (type=dict[str, str], default=field(default_factory=dict))
    - `telemetry` (type=dict[str, object], default=field(default_factory=dict))
    - `console_buffer` (type=list[object], default=field(default_factory=list))
    - `perturbations` (type=dict[str, object], default=field(default_factory=dict))
    - `affordances` (type=dict[str, object], default=field(default_factory=dict))
    - `relationships` (type=dict[str, dict[str, dict[str, float]]], default=field(default_factory=dict))
    - `relationship_metrics` (type=dict[str, object], default=field(default_factory=dict))
    - `stability` (type=dict[str, object], default=field(default_factory=dict))
    - `promotion` (type=dict[str, object], default=field(default_factory=dict))
    - `identity` (type=dict[str, object], default=field(default_factory=dict))
    - `migrations` (type=dict[str, object], default=field(default_factory=lambda: {'applied': [], 'required': []}))
  - Methods:
    - `as_dict(self) -> dict[str, object]` — No docstring provided.
    - `from_dict(cls, payload: Mapping[str, object]) -> 'SnapshotState'` — No docstring provided.
- **SnapshotManager(object)** — Handles save/load of simulation state and RNG streams.
  - Methods:
    - `__init__(self, root: Path) -> None` — No docstring provided.
    - `save(self, state: SnapshotState) -> Path` — No docstring provided.
    - `load(self, path: Path, config: SimulationConfig, *, allow_migration: bool | None = None, allow_downgrade: bool | None = None, require_exact_config: bool | None = None) -> SnapshotState` — No docstring provided.

### Functions
- `_parse_version(value: str) -> tuple[int, ...]` — No docstring provided.
- `snapshot_from_world(config: SimulationConfig, world: WorldState, *, lifecycle: Optional[LifecycleManager] = None, telemetry: Optional['TelemetryPublisher'] = None, perturbations: Optional[PerturbationScheduler] = None, stability: Optional['StabilityMonitor'] = None, promotion: Optional['PromotionManager'] = None, rng_streams: Optional[Mapping[str, random.Random]] = None, identity: Optional[Mapping[str, object]] = None) -> SnapshotState` — Capture the current world state into a snapshot payload.
- `apply_snapshot_to_world(world: WorldState, snapshot: SnapshotState, *, lifecycle: Optional[LifecycleManager] = None) -> None` — Restore world, queue, embeddings, and lifecycle state from snapshot.
- `apply_snapshot_to_telemetry(telemetry: 'TelemetryPublisher', snapshot: SnapshotState) -> None` — No docstring provided.

### Constants and Configuration
- `SNAPSHOT_SCHEMA_VERSION` = '1.6'

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.agents.models, townlet.config, townlet.lifecycle.manager, townlet.scheduler.perturbations, townlet.snapshots.migrations, townlet.stability.monitor, townlet.stability.promotion, townlet.telemetry.publisher, townlet.utils, townlet.world.grid

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/stability/__init__.py

- **File path**: `src/townlet/stability/__init__.py`
- **Purpose**: Stability guardrails.
- **Dependencies**: stdlib [__future__] / third-party [monitor, promotion] / internal [None]
- **Related modules**: None
- **Lines of code**: 8
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: monitor, promotion
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/stability/monitor.py

- **File path**: `src/townlet/stability/monitor.py`
- **Purpose**: Monitors KPIs and promotion guardrails.
- **Dependencies**: stdlib [__future__, collections, collections.abc] / third-party [None] / internal [townlet.config]
- **Related modules**: townlet.config
- **Lines of code**: 420
- **Environment variables**: None detected

### Classes
- **StabilityMonitor(object)** — Tracks rolling metrics and canaries.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `_promotion_snapshot(self) -> dict[str, object]` — No docstring provided.
    - `_finalise_promotion_window(self, window_end: int) -> None` — No docstring provided.
    - `_update_promotion_window(self, tick: int, alerts: Iterable[str]) -> None` — No docstring provided.
    - `track(self, *, tick: int, rewards: dict[str, float], terminated: dict[str, bool], queue_metrics: dict[str, int] | None = None, embedding_metrics: dict[str, float] | None = None, job_snapshot: dict[str, dict[str, object]] | None = None, events: Iterable[dict[str, object]] | None = None, employment_metrics: dict[str, object] | None = None, hunger_levels: dict[str, float] | None = None, option_switch_counts: dict[str, int] | None = None, rivalry_events: Iterable[dict[str, object]] | None = None) -> None` — No docstring provided.
    - `latest_metrics(self) -> dict[str, object]` — No docstring provided.
    - `export_state(self) -> dict[str, object]` — No docstring provided.
    - `import_state(self, payload: dict[str, object]) -> None` — No docstring provided.
    - `reset_state(self) -> None` — No docstring provided.
    - `_update_starvation_state(self, *, tick: int, hunger_levels: dict[str, float] | None, terminated: dict[str, bool]) -> int` — No docstring provided.
    - `_update_reward_samples(self, *, tick: int, rewards: dict[str, float]) -> tuple[float | None, float | None, int]` — No docstring provided.
    - `_threshold_snapshot(self) -> dict[str, object]` — No docstring provided.
    - `_update_option_samples(self, *, tick: int, option_switch_counts: dict[str, int] | None, active_agent_count: int) -> float | None` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/stability/promotion.py

- **File path**: `src/townlet/stability/promotion.py`
- **Purpose**: Promotion gate state tracking.
- **Dependencies**: stdlib [__future__, collections, collections.abc, json, pathlib] / third-party [None] / internal [townlet.config]
- **Related modules**: townlet.config
- **Lines of code**: 263
- **Environment variables**: None detected

### Classes
- **PromotionManager(object)** — Tracks promotion readiness and release/shadow state.
  - Methods:
    - `__init__(self, config: SimulationConfig, log_path: Path | None = None) -> None` — No docstring provided.
    - `update_from_metrics(self, metrics: Mapping[str, object], *, tick: int) -> None` — Update state based on the latest stability metrics.
    - `mark_promoted(self, *, tick: int, metadata: Mapping[str, object] | None = None) -> None` — Record a promotion event and update release metadata.
    - `register_rollback(self, *, tick: int, metadata: Mapping[str, object] | None = None) -> None` — Record a rollback event and return to monitoring state.
    - `record_manual_swap(self, *, tick: int, metadata: Mapping[str, object]) -> dict[str, object]` — Record a manual policy swap without altering candidate readiness.
    - `set_candidate_metadata(self, metadata: Mapping[str, object] | None) -> None` — No docstring provided.
    - `snapshot(self) -> dict[str, object]` — No docstring provided.
    - `export_state(self) -> dict[str, object]` — No docstring provided.
    - `import_state(self, payload: Mapping[str, object]) -> None` — No docstring provided.
    - `reset(self) -> None` — No docstring provided.
    - `_log_event(self, record: Mapping[str, object]) -> None` — No docstring provided.
    - `_normalise_release(self, metadata: Mapping[str, object] | None) -> dict[str, object]` — No docstring provided.
    - `_resolve_rollback_target(self, metadata: Mapping[str, object] | None) -> dict[str, object]` — No docstring provided.
    - `_latest_promoted_release(self) -> dict[str, object] | None` — No docstring provided.
    - `state(self) -> str` — No docstring provided.
    - `candidate_ready(self) -> bool` — No docstring provided.
    - `pass_streak(self) -> int` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/telemetry/__init__.py

- **File path**: `src/townlet/telemetry/__init__.py`
- **Purpose**: Telemetry publication surfaces.
- **Dependencies**: stdlib [__future__] / third-party [publisher] / internal [None]
- **Related modules**: None
- **Lines of code**: 7
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: publisher
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/telemetry/events.py

- **File path**: `src/townlet/telemetry/events.py`
- **Purpose**: Telemetry narration event constants for downstream consumers.
- **Dependencies**: stdlib [None] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 11
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- `RELATIONSHIP_FRIENDSHIP_EVENT` = 'relationship_friendship'
- `RELATIONSHIP_RIVALRY_EVENT` = 'relationship_rivalry'
- `RELATIONSHIP_SOCIAL_ALERT_EVENT` = 'relationship_social_alert'

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/telemetry/narration.py

- **File path**: `src/townlet/telemetry/narration.py`
- **Purpose**: Narration throttling utilities.
- **Dependencies**: stdlib [__future__, collections] / third-party [None] / internal [townlet.config]
- **Related modules**: townlet.config
- **Lines of code**: 133
- **Environment variables**: None detected

### Classes
- **NarrationRateLimiter(object)** — Apply global and per-category narration cooldowns with dedupe.
  - Methods:
    - `__init__(self, config: NarrationThrottleConfig) -> None` — No docstring provided.
    - `begin_tick(self, tick: int) -> None` — No docstring provided.
    - `allow(self, category: str, *, message: str, priority: bool = False, dedupe_key: str | None = None) -> bool` — Return True if a narration may be emitted for the given category.
    - `export_state(self) -> dict[str, object]` — No docstring provided.
    - `import_state(self, payload: dict[str, object]) -> None` — No docstring provided.
    - `_expire_recent_entries(self) -> None` — No docstring provided.
    - `_expire_window(self) -> None` — No docstring provided.
    - `_check_global_cooldown(self) -> bool` — No docstring provided.
    - `_check_category_cooldown(self, category: str) -> bool` — No docstring provided.
    - `_check_window_limit(self) -> bool` — No docstring provided.
    - `_record_emission(self, category: str, dedupe_key: str) -> None` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/telemetry/publisher.py

- **File path**: `src/townlet/telemetry/publisher.py`
- **Purpose**: Telemetry pipelines and console bridge.
- **Dependencies**: stdlib [__future__, collections, collections.abc, dataclasses, json, logging, pathlib, threading, time, typing] / third-party [None] / internal [townlet.config, townlet.console.auth, townlet.console.command, townlet.telemetry.events, townlet.telemetry.narration, townlet.telemetry.transport, townlet.world.grid]
- **Related modules**: townlet.config, townlet.console.auth, townlet.console.command, townlet.telemetry.events, townlet.telemetry.narration, townlet.telemetry.transport, townlet.world.grid
- **Lines of code**: 1869
- **Environment variables**: None detected

### Classes
- **TelemetryPublisher(object)** — Publishes observer snapshots and consumes console commands.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `queue_console_command(self, command: object) -> None` — No docstring provided.
    - `drain_console_buffer(self) -> Iterable[object]` — No docstring provided.
    - `export_state(self) -> dict[str, object]` — No docstring provided.
    - `import_state(self, payload: dict[str, object]) -> None` — No docstring provided.
    - `export_console_buffer(self) -> list[object]` — No docstring provided.
    - `import_console_buffer(self, buffer: Iterable[object]) -> None` — No docstring provided.
    - `record_console_results(self, results: Iterable[ConsoleCommandResult]) -> None` — No docstring provided.
    - `latest_console_results(self) -> list[dict[str, Any]]` — No docstring provided.
    - `console_history(self) -> list[dict[str, Any]]` — No docstring provided.
    - `record_possessed_agents(self, agents: Iterable[str]) -> None` — No docstring provided.
    - `latest_possessed_agents(self) -> list[str]` — No docstring provided.
    - `latest_precondition_failures(self) -> list[dict[str, object]]` — No docstring provided.
    - `latest_transport_status(self) -> dict[str, object]` — Return transport health and backlog counters for observability.
    - `record_health_metrics(self, metrics: Mapping[str, object]) -> None` — No docstring provided.
    - `latest_health_status(self) -> dict[str, object]` — No docstring provided.
    - `_build_transport_client(self)` — No docstring provided.
    - `_reset_transport_client(self) -> None` — No docstring provided.
    - `_send_with_retry(self, payload: bytes, tick: int) -> bool` — No docstring provided.
    - `_flush_transport_buffer(self, tick: int) -> None` — No docstring provided.
    - `_flush_loop(self) -> None` — No docstring provided.
    - `_enqueue_stream_payload(self, payload: Mapping[str, Any], *, tick: int) -> None` — No docstring provided.
    - `_build_stream_payload(self, tick: int) -> dict[str, Any]` — No docstring provided.
    - `close(self) -> None` — No docstring provided.
    - `stop_worker(self, *, wait: bool = True, timeout: float = 2.0) -> None` — Stop the background flush worker without closing transports.
    - `_capture_affordance_runtime(self, *, world: WorldState, events: Iterable[Mapping[str, object]] | None, tick: int) -> None` — No docstring provided.
    - `publish_tick(self, *, tick: int, world: WorldState, observations: dict[str, object], rewards: dict[str, float], events: Iterable[dict[str, object]] | None = None, policy_snapshot: Mapping[str, Mapping[str, object]] | None = None, kpi_history: bool = False, reward_breakdown: Mapping[str, Mapping[str, float]] | None = None, stability_inputs: Mapping[str, object] | None = None, perturbations: Mapping[str, object] | None = None, policy_identity: Mapping[str, object] | None = None, possessed_agents: Iterable[str] | None = None, social_events: Iterable[dict[str, object]] | None = None) -> None` — No docstring provided.
    - `latest_queue_metrics(self) -> dict[str, int] | None` — Expose the most recent queue-related telemetry counters.
    - `latest_queue_history(self) -> list[dict[str, object]]` — No docstring provided.
    - `latest_rivalry_events(self) -> list[dict[str, object]]` — No docstring provided.
    - `latest_affordance_runtime(self) -> dict[str, object]` — No docstring provided.
    - `update_anneal_status(self, status: Mapping[str, object] | None) -> None` — Record the latest anneal status payload for observer dashboards.
    - `kpi_history(self) -> dict[str, list[float]]` — No docstring provided.
    - `latest_conflict_snapshot(self) -> dict[str, object]` — Return the conflict-focused telemetry payload (queues + rivalry).
    - `latest_affordance_manifest(self) -> dict[str, object]` — Expose the most recent affordance manifest metadata.
    - `latest_reward_breakdown(self) -> dict[str, dict[str, float]]` — No docstring provided.
    - `latest_social_events(self) -> list[dict[str, object]]` — No docstring provided.
    - `latest_relationship_summary(self) -> dict[str, object]` — No docstring provided.
    - `latest_stability_inputs(self) -> dict[str, object]` — No docstring provided.
    - `record_stability_metrics(self, metrics: Mapping[str, object]) -> None` — No docstring provided.
    - `latest_stability_metrics(self) -> dict[str, object]` — No docstring provided.
    - `latest_promotion_state(self) -> dict[str, object] | None` — No docstring provided.
    - `_append_console_audit(self, payload: Mapping[str, Any]) -> None` — No docstring provided.
    - `latest_stability_alerts(self) -> list[str]` — No docstring provided.
    - `latest_perturbations(self) -> dict[str, object]` — No docstring provided.
    - `update_policy_identity(self, identity: Mapping[str, object] | None) -> None` — No docstring provided.
    - `latest_policy_identity(self) -> dict[str, object] | None` — No docstring provided.
    - `record_snapshot_migrations(self, applied: Iterable[str]) -> None` — No docstring provided.
    - `latest_snapshot_migrations(self) -> list[str]` — No docstring provided.
    - `_normalize_perturbations_payload(self, payload: Mapping[str, object]) -> dict[str, object]` — No docstring provided.
    - `latest_policy_snapshot(self) -> dict[str, dict[str, object]]` — No docstring provided.
    - `latest_anneal_status(self) -> dict[str, object] | None` — No docstring provided.
    - `latest_relationship_metrics(self) -> dict[str, object] | None` — Expose relationship churn payload captured during publish.
    - `latest_relationship_snapshot(self) -> dict[str, dict[str, dict[str, float]]]` — No docstring provided.
    - `latest_relationship_updates(self) -> list[dict[str, object]]` — No docstring provided.
    - `update_relationship_metrics(self, payload: dict[str, object]) -> None` — Allow external callers to seed the latest relationship metrics.
    - `latest_relationship_overlay(self) -> dict[str, list[dict[str, object]]]` — No docstring provided.
    - `latest_narrations(self) -> list[dict[str, object]]` — Expose narration entries emitted during the latest publish call.
    - `latest_embedding_metrics(self) -> dict[str, float] | None` — Expose embedding allocator counters.
    - `latest_events(self) -> Iterable[dict[str, object]]` — Return the most recent event batch.
    - `latest_narration_state(self) -> dict[str, object]` — Return the narration limiter state for snapshot export.
    - `register_event_subscriber(self, subscriber: Callable[[list[dict[str, object]]], None]) -> None` — Register a callback to receive each tick's event batch.
    - `latest_job_snapshot(self) -> dict[str, dict[str, object]]` — No docstring provided.
    - `latest_economy_snapshot(self) -> dict[str, dict[str, object]]` — No docstring provided.
    - `latest_economy_settings(self) -> dict[str, float]` — No docstring provided.
    - `latest_price_spikes(self) -> dict[str, dict[str, object]]` — No docstring provided.
    - `latest_utilities(self) -> dict[str, bool]` — No docstring provided.
    - `latest_employment_metrics(self) -> dict[str, object]` — No docstring provided.
    - `schema(self) -> str` — No docstring provided.
    - `_capture_relationship_snapshot(self, world: WorldState) -> dict[str, dict[str, dict[str, float]]]` — No docstring provided.
    - `_compute_relationship_updates(self, previous: dict[str, dict[str, dict[str, float]]], current: dict[str, dict[str, dict[str, float]]]) -> list[dict[str, object]]` — No docstring provided.
    - `_build_relationship_overlay(self) -> dict[str, list[dict[str, object]]]` — No docstring provided.
    - `_build_relationship_summary(self, snapshot: Mapping[str, Mapping[str, Mapping[str, float]]], world: WorldState) -> dict[str, object]` — No docstring provided.
    - `_process_narrations(self, events: Iterable[dict[str, object]], social_events: Iterable[Mapping[str, object]] | None, relationship_updates: Iterable[Mapping[str, object]], tick: int) -> None` — No docstring provided.
    - `_emit_relationship_friendship_narrations(self, updates: Iterable[Mapping[str, object]], tick: int) -> None` — No docstring provided.
    - `_emit_relationship_rivalry_narrations(self, tick: int) -> None` — No docstring provided.
    - `_emit_social_alert_narrations(self, events: Iterable[Mapping[str, object]], tick: int) -> None` — No docstring provided.
    - `_handle_queue_conflict_narration(self, event: dict[str, object], tick: int) -> None` — No docstring provided.
    - `_handle_shower_power_outage_narration(self, event: dict[str, object], tick: int) -> None` — No docstring provided.
    - `_handle_shower_complete_narration(self, event: dict[str, object], tick: int) -> None` — No docstring provided.
    - `_handle_sleep_complete_narration(self, event: dict[str, object], tick: int) -> None` — No docstring provided.
    - `_copy_relationship_snapshot(snapshot: dict[str, dict[str, dict[str, float]]]) -> dict[str, dict[str, dict[str, float]]]` — No docstring provided.
    - `_update_kpi_history(self, world: WorldState) -> None` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.console.auth, townlet.console.command, townlet.telemetry.events, townlet.telemetry.narration, townlet.telemetry.transport, townlet.world.grid

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/telemetry/relationship_metrics.py

- **File path**: `src/townlet/telemetry/relationship_metrics.py`
- **Purpose**: Helpers for tracking relationship churn and eviction telemetry.
- **Dependencies**: stdlib [__future__, collections, collections.abc, dataclasses] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 182
- **Environment variables**: None detected

### Classes
- **RelationshipEvictionSample(object)** — Aggregated eviction counts captured for a completed window.
  - Attributes:
    - `window_start` (type=int)
    - `window_end` (type=int)
    - `total_evictions` (type=int)
    - `per_owner` (type=dict[str, int])
    - `per_reason` (type=dict[str, int])
  - Methods:
    - `to_payload(self) -> dict[str, object]` — Serialise the sample into a telemetry-friendly payload.
- **RelationshipChurnAccumulator(object)** — Tracks relationship eviction activity over fixed tick windows.
  - Methods:
    - `__init__(self, *, window_ticks: int, max_samples: int = 8) -> None` — No docstring provided.
    - `record_eviction(self, *, tick: int, owner_id: str, evicted_id: str, reason: str | None = None) -> None` — Record an eviction event for churn tracking.
    - `_roll_window(self, tick: int) -> None` — No docstring provided.
    - `snapshot(self) -> dict[str, object]` — Return aggregates for the active window.
    - `history(self) -> Iterable[RelationshipEvictionSample]` — Return a snapshot of the recorded history.
    - `history_payload(self) -> list[dict[str, object]]` — Convert history samples into telemetry payloads.
    - `latest_payload(self) -> dict[str, object]` — Return the live window payload for telemetry publishing.
    - `ingest_payload(self, payload: dict[str, object]) -> None` — Restore the accumulator from an external payload.

### Functions
- `_advance_window(*, current_tick: int, window_ticks: int, window_start: int) -> int` — Move the window start forward until it covers ``current_tick``.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/telemetry/transport.py

- **File path**: `src/townlet/telemetry/transport.py`
- **Purpose**: Transport primitives for telemetry publishing.
- **Dependencies**: stdlib [__future__, collections, logging, pathlib, socket, ssl, sys, typing] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 247
- **Environment variables**: None detected

### Classes
- **TelemetryTransportError(RuntimeError)** — Raised when telemetry messages cannot be delivered.
  - Methods: None
- **TransportClient(Protocol)** — Common interface for transport implementations.
  - Methods:
    - `send(self, payload: bytes) -> None` — No docstring provided.
    - `close(self) -> None` — No docstring provided.
- **StdoutTransport(object)** — Writes telemetry payloads to stdout (for development/debug).
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `send(self, payload: bytes) -> None` — No docstring provided.
    - `close(self) -> None` — No docstring provided.
- **FileTransport(object)** — Appends newline-delimited payloads to a local file.
  - Methods:
    - `__init__(self, path: Path) -> None` — No docstring provided.
    - `send(self, payload: bytes) -> None` — No docstring provided.
    - `close(self) -> None` — No docstring provided.
- **TcpTransport(object)** — Sends telemetry payloads to a TCP endpoint.
  - Methods:
    - `__init__(self, endpoint: str, *, connect_timeout: float, send_timeout: float, enable_tls: bool, verify_hostname: bool, ca_file: Path | None, cert_file: Path | None, key_file: Path | None, allow_plaintext: bool) -> None` — No docstring provided.
    - `_connect(self) -> None` — No docstring provided.
    - `_build_ssl_context(self) -> ssl.SSLContext` — No docstring provided.
    - `send(self, payload: bytes) -> None` — No docstring provided.
    - `close(self) -> None` — No docstring provided.
- **TransportBuffer(object)** — Accumulates payloads prior to flushing to the transport.
  - Methods:
    - `__init__(self, *, max_batch_size: int, max_buffer_bytes: int) -> None` — No docstring provided.
    - `append(self, payload: bytes) -> None` — No docstring provided.
    - `popleft(self) -> bytes` — No docstring provided.
    - `clear(self) -> None` — No docstring provided.
    - `__len__(self) -> int` — No docstring provided.
    - `total_bytes(self) -> int` — No docstring provided.
    - `is_over_capacity(self) -> bool` — No docstring provided.
    - `drop_until_within_capacity(self) -> int` — Drop oldest payloads until buffer fits limits; returns drop count.

### Functions
- `create_transport(*, transport_type: str, file_path: Path | None, endpoint: str | None, connect_timeout: float, send_timeout: float, enable_tls: bool, verify_hostname: bool, ca_file: Path | None, cert_file: Path | None, key_file: Path | None, allow_plaintext: bool) -> TransportClient` — Factory helper for `TelemetryPublisher`.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Raises `NotImplementedError`, indicating missing behaviour.


## src/townlet/utils/__init__.py

- **File path**: `src/townlet/utils/__init__.py`
- **Purpose**: Utility helpers for Townlet.
- **Dependencies**: stdlib [None] / third-party [rng] / internal [None]
- **Related modules**: None
- **Lines of code**: 9
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: rng
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/utils/rng.py

- **File path**: `src/townlet/utils/rng.py`
- **Purpose**: Utility helpers for serialising deterministic RNG state.
- **Dependencies**: stdlib [__future__, base64, pickle, random] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 25
- **Environment variables**: None detected

### Classes
- None

### Functions
- `encode_rng_state(state: tuple[object, ...]) -> str` — Encode a Python ``random`` state tuple into a base64 string.
- `decode_rng_state(payload: str) -> tuple[object, ...]` — Decode a base64-encoded RNG state back into a Python tuple.
- `encode_rng(rng: random.Random) -> str` — Capture the current state of ``rng`` as a serialisable string.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/world/__init__.py

- **File path**: `src/townlet/world/__init__.py`
- **Purpose**: World modelling primitives.
- **Dependencies**: stdlib [__future__] / third-party [employment, grid, queue_manager, relationships] / internal [None]
- **Related modules**: None
- **Lines of code**: 18
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: employment, grid, queue_manager, relationships
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/world/affordances.py

- **File path**: `src/townlet/world/affordances.py`
- **Purpose**: Affordance runtime scaffolding pending extraction from `world.grid`.
- **Dependencies**: stdlib [__future__, dataclasses, logging, time, typing] / third-party [None] / internal [townlet.world.grid, townlet.world.preconditions, townlet.world.queue_manager]
- **Related modules**: townlet.world.grid, townlet.world.preconditions, townlet.world.queue_manager
- **Lines of code**: 646
- **Environment variables**: None detected

### Classes
- **AffordanceRuntimeContext(object)** — Dependencies supplied to the affordance runtime.
  - Attributes:
    - `world` (type='WorldState')
    - `queue_manager` (type=QueueManager)
    - `objects` (type=MutableMapping[str, Any])
    - `affordances` (type=MutableMapping[str, Any])
    - `running_affordances` (type=MutableMapping[str, Any])
    - `active_reservations` (type=MutableMapping[str, str])
    - `emit_event` (type=Callable[[str, dict[str, object]], None])
    - `sync_reservation` (type=Callable[[str], None])
    - `apply_affordance_effects` (type=Callable[[str, dict[str, float]], None])
    - `dispatch_hooks` (type=Callable[[str, Iterable[str]], bool])
    - `record_queue_conflict` (type=Callable[..., None])
    - `apply_need_decay` (type=Callable[[], None])
    - `build_precondition_context` (type=Callable[..., dict[str, Any]])
    - `snapshot_precondition_context` (type=Callable[[Mapping[str, Any]], dict[str, Any]])
  - Methods: None
- **RunningAffordanceState(object)** — Serialized view of a running affordance for telemetry/tests.
  - Attributes:
    - `agent_id` (type=str)
    - `object_id` (type=str)
    - `affordance_id` (type=str)
    - `duration_remaining` (type=int)
    - `effects` (type=dict[str, float], default=field(default_factory=dict))
  - Methods: None
- **HookPayload(TypedDict)** — Structured affordance hook payload shared across stages.
  - Attributes:
    - `stage` (type=Literal['before', 'after', 'fail'])
    - `hook` (type=str)
    - `tick` (type=int)
    - `agent_id` (type=str)
    - `object_id` (type=str)
    - `affordance_id` (type=str)
    - `world` (type='WorldState')
    - `spec` (type=Any)
    - `effects` (type=dict[str, float])
    - `reason` (type=str)
    - `condition` (type=str)
    - `context` (type=dict[str, object])
  - Methods: None
- **AffordanceOutcome(object)** — Represents the result of an affordance-related agent action.
  - Attributes:
    - `agent_id` (type=str)
    - `kind` (type=str)
    - `success` (type=bool)
    - `duration` (type=int)
    - `object_id` (type=str | None, default=None)
    - `affordance_id` (type=str | None, default=None)
    - `tick` (type=int | None, default=None)
    - `metadata` (type=dict[str, object], default=field(default_factory=dict))
  - Methods: None
- **AffordanceRuntime(Protocol)** — Protocol describing the affordance runtime contract.
  - Methods:
    - `bind(self, *, context: AffordanceRuntimeContext) -> None` — Attach the runtime to the provided world context.
    - `apply_actions(self, actions: Mapping[str, dict[str, object]], *, tick: int) -> None` — Process agent actions that may start or queue affordances.
    - `resolve(self, *, tick: int) -> None` — Advance running affordances and emit telemetry/hook events.
    - `running_snapshot(self) -> dict[str, RunningAffordanceState]` — Return the serialisable state of all running affordances.
    - `clear(self) -> None` — Reset runtime state (used on snapshot restore or world reset).
- **DefaultAffordanceRuntime(object)** — Default affordance runtime bound to an injected context.
  - Methods:
    - `__init__(self, context: AffordanceRuntimeContext, *, running_cls: type, instrumentation: str = 'off', options: Mapping[str, object] | None = None) -> None` — No docstring provided.
    - `context(self) -> AffordanceRuntimeContext` — No docstring provided.
    - `world(self) -> 'WorldState'` — No docstring provided.
    - `running_affordances(self) -> MutableMapping[str, Any]` — No docstring provided.
    - `instrumentation_level(self) -> str` — No docstring provided.
    - `options(self) -> dict[str, object]` — No docstring provided.
    - `remove_agent(self, agent_id: str) -> None` — Drop any running affordances owned by `agent_id`.
    - `start(self, agent_id: str, object_id: str, affordance_id: str, *, tick: int) -> tuple[bool, dict[str, object]]` — No docstring provided.
    - `release(self, agent_id: str, object_id: str, *, success: bool, reason: str | None, requested_affordance_id: str | None, tick: int) -> tuple[str | None, dict[str, object]]` — No docstring provided.
    - `handle_blocked(self, object_id: str, tick: int) -> None` — No docstring provided.
    - `_select_handover_candidate(self, world: 'WorldState', source_agent: str, waiting: list[str]) -> str | None` — No docstring provided.
    - `resolve(self, *, tick: int) -> None` — No docstring provided.
    - `_instrumentation_enabled(self) -> bool` — No docstring provided.
    - `running_snapshot(self) -> dict[str, RunningAffordanceState]` — No docstring provided.
    - `clear(self) -> None` — No docstring provided.
    - `export_state(self) -> dict[str, object]` — No docstring provided.
    - `import_state(self, payload: Mapping[str, Mapping[str, object]]) -> None` — No docstring provided.

### Functions
- `snapshot_running_affordance(*, object_id: str, agent_id: str, affordance_id: str, duration_remaining: int, effects: Mapping[str, float] | None = None) -> RunningAffordanceState` — Create a serializable snapshot for a running affordance entry.
- `build_hook_payload(*, stage: Literal['before', 'after', 'fail'], hook: str, tick: int, agent_id: str, object_id: str, affordance_id: str, world: 'WorldState', spec: Any, extra: Mapping[str, object] | None = None) -> HookPayload` — Compose the base payload forwarded to affordance hook handlers.
- `apply_affordance_outcome(snapshot: 'AgentSnapshot', outcome: AffordanceOutcome) -> None` — Update agent snapshot bookkeeping based on the supplied outcome.

### Constants and Configuration
- None detected

  TODO markers:
  - # TODO(@townlet-backlog): Persist richer outcome metadata (affordance/object ids)

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.world.grid, townlet.world.preconditions, townlet.world.queue_manager

### Code Quality Notes
- TODO markers present; implementation incomplete.


## src/townlet/world/console_bridge.py

- **File path**: `src/townlet/world/console_bridge.py`
- **Purpose**: Console command management for WorldState.
- **Dependencies**: stdlib [__future__, collections, dataclasses, logging, typing] / third-party [None] / internal [townlet.console.command]
- **Related modules**: townlet.console.command
- **Lines of code**: 166
- **Environment variables**: None detected

### Classes
- **ConsoleHandlerEntry(object)** — No docstring provided.
  - Attributes:
    - `handler` (type=Callable[[ConsoleCommandEnvelope], ConsoleCommandResult])
    - `mode` (type=str)
    - `require_cmd_id` (type=bool)
  - Methods: None
- **ConsoleBridge(object)** — Maintains console handlers and result history for a world instance.
  - Methods:
    - `__init__(self, *, world: Any, history_limit: int, buffer_limit: int) -> None` — No docstring provided.
    - `register_handler(self, name: str, handler: Callable[[ConsoleCommandEnvelope], ConsoleCommandResult], *, mode: str = 'viewer', require_cmd_id: bool = False) -> None` — No docstring provided.
    - `handlers(self) -> Mapping[str, ConsoleHandlerEntry]` — No docstring provided.
    - `record_result(self, result: ConsoleCommandResult) -> None` — No docstring provided.
    - `consume_results(self) -> list[ConsoleCommandResult]` — No docstring provided.
    - `cached_result(self, cmd_id: str) -> ConsoleCommandResult | None` — No docstring provided.
    - `apply(self, operations: Iterable[Any]) -> None` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.console.command

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/world/employment.py

- **File path**: `src/townlet/world/employment.py`
- **Purpose**: Employment domain logic extracted from WorldState.
- **Dependencies**: stdlib [__future__, collections, logging, typing] / third-party [grid] / internal [townlet.config]
- **Related modules**: townlet.config
- **Lines of code**: 611
- **Environment variables**: None detected

### Classes
- **EmploymentEngine(object)** — Manages employment state, queues, and shift bookkeeping.
  - Methods:
    - `__init__(self, config: SimulationConfig, emit_event: Callable[[str, dict[str, object]], None]) -> None` — No docstring provided.
    - `exits_today(self) -> int` — No docstring provided.
    - `assign_jobs_to_agents(self, world: WorldState) -> None` — No docstring provided.
    - `apply_job_state(self, world: WorldState) -> None` — No docstring provided.
    - `_apply_job_state_legacy(self, world: WorldState) -> None` — No docstring provided.
    - `_apply_job_state_enforced(self, world: WorldState) -> None` — No docstring provided.
    - `context_defaults(self) -> dict[str, Any]` — No docstring provided.
    - `get_employment_context(self, world: WorldState, agent_id: str) -> dict[str, Any]` — No docstring provided.
    - `employment_context_wages(self, agent_id: str) -> float` — No docstring provided.
    - `employment_context_punctuality(self, agent_id: str) -> float` — No docstring provided.
    - `_employment_idle_state(self, world: WorldState, snapshot: AgentSnapshot, ctx: dict[str, Any]) -> None` — No docstring provided.
    - `_employment_prepare_state(self, snapshot: AgentSnapshot, ctx: dict[str, Any]) -> None` — No docstring provided.
    - `_employment_begin_shift(self, ctx: dict[str, Any], start: int, end: int) -> None` — No docstring provided.
    - `_employment_determine_state(self, *, ctx: dict[str, Any], tick: int, start: int, at_required_location: bool, employment_cfg: EmploymentConfig) -> str` — No docstring provided.
    - `_employment_apply_state_effects(self, *, world: WorldState, snapshot: AgentSnapshot, ctx: dict[str, Any], state: str, at_required_location: bool, wage_rate: float, lateness_penalty: float, employment_cfg: EmploymentConfig) -> None` — No docstring provided.
    - `_employment_finalize_shift(self, world: WorldState, snapshot: AgentSnapshot, ctx: dict[str, Any], employment_cfg: EmploymentConfig, job_id: str | None) -> None` — No docstring provided.
    - `_employment_coworkers_on_shift(self, world: WorldState, snapshot: AgentSnapshot) -> list[str]` — No docstring provided.
    - `enqueue_exit(self, world: WorldState, agent_id: str, tick: int) -> None` — No docstring provided.
    - `remove_from_queue(self, world: WorldState, agent_id: str) -> None` — No docstring provided.
    - `queue_snapshot(self) -> dict[str, Any]` — No docstring provided.
    - `request_manual_exit(self, world: WorldState, agent_id: str, tick: int) -> bool` — No docstring provided.
    - `defer_exit(self, world: WorldState, agent_id: str) -> bool` — No docstring provided.
    - `export_state(self) -> dict[str, object]` — Return a serialisable snapshot of the employment domain state.
    - `import_state(self, payload: Mapping[str, object]) -> None` — Restore employment state from a snapshot payload.
    - `reset_exits_today(self) -> None` — No docstring provided.
    - `set_exits_today(self, value: int) -> None` — No docstring provided.
    - `increment_exits_today(self) -> None` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: grid
- Internal: townlet.config

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/world/grid.py

- **File path**: `src/townlet/world/grid.py`
- **Purpose**: Grid world representation and affordance integration.
- **Dependencies**: stdlib [__future__, collections, collections.abc, copy, dataclasses, logging, os, pathlib, random, time, typing] / third-party [None] / internal [townlet.agents.models, townlet.agents.relationship_modifiers, townlet.config, townlet.config.affordance_manifest, townlet.console.command, townlet.observations.embedding, townlet.telemetry.relationship_metrics, townlet.world.affordances, townlet.world.console_bridge, townlet.world.employment, townlet.world.hooks, townlet.world.preconditions, townlet.world.queue_conflict, townlet.world.queue_manager, townlet.world.relationships, townlet.world.rivalry]
- **Related modules**: townlet.agents.models, townlet.agents.relationship_modifiers, townlet.config, townlet.config.affordance_manifest, townlet.console.command, townlet.observations.embedding, townlet.telemetry.relationship_metrics, townlet.world.affordances, townlet.world.console_bridge, townlet.world.employment, townlet.world.hooks, townlet.world.preconditions, townlet.world.queue_conflict, townlet.world.queue_manager, townlet.world.relationships, townlet.world.rivalry
- **Lines of code**: 2583
- **Environment variables**: environ, get

### Classes
- **HookRegistry(object)** — Registers named affordance hooks and returns handlers on demand.
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `register(self, name: str, handler: Callable[[dict[str, Any]], None]) -> None` — No docstring provided.
    - `handlers_for(self, name: str) -> tuple[Callable[[dict[str, Any]], None], ...]` — No docstring provided.
    - `clear(self, name: str | None = None) -> None` — No docstring provided.
- **AgentSnapshot(object)** — Minimal agent view used for scaffolding.
  - Attributes:
    - `agent_id` (type=str)
    - `position` (type=tuple[int, int])
    - `needs` (type=dict[str, float])
    - `wallet` (type=float, default=0.0)
    - `home_position` (type=tuple[int, int] | None, default=None)
    - `origin_agent_id` (type=str | None, default=None)
    - `personality` (type=Personality, default=field(default_factory=_default_personality))
    - `inventory` (type=dict[str, int], default=field(default_factory=dict))
    - `job_id` (type=str | None, default=None)
    - `on_shift` (type=bool, default=False)
    - `lateness_counter` (type=int, default=0)
    - `last_late_tick` (type=int, default=-1)
    - `shift_state` (type=str, default='pre_shift')
    - `late_ticks_today` (type=int, default=0)
    - `attendance_ratio` (type=float, default=0.0)
    - `absent_shifts_7d` (type=int, default=0)
    - `wages_withheld` (type=float, default=0.0)
    - `exit_pending` (type=bool, default=False)
    - `last_action_id` (type=str, default='')
    - `last_action_success` (type=bool, default=False)
    - `last_action_duration` (type=int, default=0)
    - `episode_tick` (type=int, default=0)
  - Methods:
    - `__post_init__(self) -> None` — No docstring provided.
- **InteractiveObject(object)** — Represents an interactive world object with optional occupancy.
  - Attributes:
    - `object_id` (type=str)
    - `object_type` (type=str)
    - `occupied_by` (type=str | None, default=None)
    - `stock` (type=dict[str, int], default=field(default_factory=dict))
    - `position` (type=tuple[int, int] | None, default=None)
  - Methods: None
- **RunningAffordance(object)** — Tracks an affordance currently executing on an object.
  - Attributes:
    - `agent_id` (type=str)
    - `affordance_id` (type=str)
    - `duration_remaining` (type=int)
    - `effects` (type=dict[str, float])
  - Methods: None
- **AffordanceSpec(object)** — Static affordance definition loaded from configuration.
  - Attributes:
    - `affordance_id` (type=str)
    - `object_type` (type=str)
    - `duration` (type=int)
    - `effects` (type=dict[str, float])
    - `preconditions` (type=list[str], default=field(default_factory=list))
    - `hooks` (type=dict[str, list[str]], default=field(default_factory=dict))
    - `compiled_preconditions` (type=tuple[CompiledPrecondition, ...], default=field(default_factory=tuple, repr=False))
  - Methods: None
- **WorldState(object)** — Holds mutable world state for the simulation tick.
  - Attributes:
    - `config` (type=SimulationConfig)
    - `agents` (type=dict[str, AgentSnapshot], default=field(default_factory=dict))
    - `tick` (type=int, default=0)
    - `queue_manager` (type=QueueManager, default=field(init=False))
    - `embedding_allocator` (type=EmbeddingAllocator, default=field(init=False))
    - `_active_reservations` (type=dict[str, str], default=field(init=False, default_factory=dict))
    - `objects` (type=dict[str, InteractiveObject], default=field(init=False, default_factory=dict))
    - `affordances` (type=dict[str, AffordanceSpec], default=field(init=False, default_factory=dict))
    - `_running_affordances` (type=dict[str, RunningAffordance], default=field(init=False, default_factory=dict))
    - `_pending_events` (type=dict[int, list[dict[str, Any]]], default=field(init=False, default_factory=dict))
    - `store_stock` (type=dict[str, dict[str, int]], default=field(init=False, default_factory=dict))
    - `_job_keys` (type=list[str], default=field(init=False, default_factory=list))
    - `employment` (type=EmploymentEngine, default=field(init=False, repr=False))
    - `_rivalry_ledgers` (type=dict[str, RivalryLedger], default=field(init=False, default_factory=dict))
    - `_relationship_ledgers` (type=dict[str, RelationshipLedger], default=field(init=False, default_factory=dict))
    - `_relationship_churn` (type=RelationshipChurnAccumulator, default=field(init=False))
    - `_relationship_window_ticks` (type=int, default=600)
    - `_recent_meal_participants` (type=dict[str, dict[str, Any]], default=field(init=False, default_factory=dict))
    - `_rng_seed` (type=Optional[int], default=field(init=False, default=None))
    - `_rng_state` (type=Optional[tuple[Any, ...]], default=field(init=False, default=None))
    - `_rng` (type=Optional[random.Random], default=field(init=False, default=None, repr=False))
    - `affordance_runtime_factory` (type=Callable[['WorldState', AffordanceRuntimeContext], 'DefaultAffordanceRuntime'] | None, default=None)
    - `affordance_runtime_config` (type=AffordanceRuntimeConfig | None, default=None)
    - `_affordance_manifest_info` (type=dict[str, object], default=field(init=False, default_factory=dict))
    - `_objects_by_position` (type=dict[tuple[int, int], list[str]], default=field(init=False, default_factory=dict))
    - `_console` (type=ConsoleBridge, default=field(init=False))
    - `_queue_conflicts` (type=QueueConflictTracker, default=field(init=False))
    - `_hook_registry` (type=HookRegistry, default=field(init=False, repr=False))
    - `_ctx_reset_requests` (type=set[str], default=field(init=False, default_factory=set))
    - `_respawn_counters` (type=dict[str, int], default=field(init=False, default_factory=dict))
  - Methods:
    - `from_config(cls, config: SimulationConfig, *, rng: Optional[random.Random] = None, affordance_runtime_factory: Callable[['WorldState', AffordanceRuntimeContext], 'DefaultAffordanceRuntime'] | None = None, affordance_runtime_config: AffordanceRuntimeConfig | None = None) -> 'WorldState'` — Bootstrap the initial world from config.
    - `__post_init__(self) -> None` — No docstring provided.
    - `affordance_runtime(self) -> DefaultAffordanceRuntime` — No docstring provided.
    - `runtime_instrumentation_level(self) -> str` — No docstring provided.
    - `generate_agent_id(self, base_id: str) -> str` — No docstring provided.
    - `apply_console(self, operations: Iterable[Any]) -> None` — Apply console operations before the tick sequence runs.
    - `attach_rng(self, rng: random.Random) -> None` — Attach a deterministic RNG used for world-level randomness.
    - `rng(self) -> random.Random` — No docstring provided.
    - `get_rng_state(self) -> tuple[Any, ...]` — No docstring provided.
    - `set_rng_state(self, state: tuple[Any, ...]) -> None` — No docstring provided.
    - `register_console_handler(self, name: str, handler: Callable[[ConsoleCommandEnvelope], ConsoleCommandResult], *, mode: str = 'viewer', require_cmd_id: bool = False) -> None` — Register a console handler for queued commands.
    - `register_affordance_hook(self, name: str, handler: Callable[[dict[str, Any]], None]) -> None` — Register a callable invoked when a manifest hook fires.
    - `clear_affordance_hooks(self, name: str | None = None) -> None` — Clear registered affordance hooks (used primarily for tests).
    - `consume_console_results(self) -> list[ConsoleCommandResult]` — Return and clear buffered console results.
    - `_record_console_result(self, result: ConsoleCommandResult) -> None` — No docstring provided.
    - `_dispatch_affordance_hooks(self, stage: str, hook_names: Iterable[str], *, agent_id: str, object_id: str, spec: AffordanceSpec | None, extra: Mapping[str, Any] | None = None) -> bool` — No docstring provided.
    - `_build_precondition_context(self, *, agent_id: str, object_id: str, spec: AffordanceSpec) -> dict[str, Any]` — No docstring provided.
    - `_snapshot_precondition_context(self, context: Mapping[str, Any]) -> dict[str, Any]` — No docstring provided.
    - `_register_default_console_handlers(self) -> None` — No docstring provided.
    - `_console_noop_handler(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `_console_employment_status(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `_console_affordance_status(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `_console_employment_exit(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `_assign_job_if_missing(self, snapshot: AgentSnapshot) -> None` — No docstring provided.
    - `remove_agent(self, agent_id: str, tick: int) -> dict[str, Any] | None` — No docstring provided.
    - `respawn_agent(self, blueprint: Mapping[str, Any]) -> None` — No docstring provided.
    - `_sync_agent_spawn(self, snapshot: AgentSnapshot) -> None` — No docstring provided.
    - `_console_spawn_agent(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `_console_teleport_agent(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `_release_queue_membership(self, agent_id: str) -> None` — No docstring provided.
    - `_sync_reservation_for_agent(self, agent_id: str) -> None` — No docstring provided.
    - `_is_position_walkable(self, position: tuple[int, int]) -> bool` — No docstring provided.
    - `kill_agent(self, agent_id: str, *, reason: str | None = None) -> bool` — No docstring provided.
    - `_console_set_need(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `_console_set_price(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `_console_force_chat(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `_console_set_relationship(self, envelope: ConsoleCommandEnvelope) -> ConsoleCommandResult` — No docstring provided.
    - `register_object(self, *, object_id: str, object_type: str, position: tuple[int, int] | None = None) -> None` — Register or update an interactive object in the world.
    - `_index_object_position(self, object_id: str, position: tuple[int, int]) -> None` — No docstring provided.
    - `_unindex_object_position(self, object_id: str, position: tuple[int, int]) -> None` — No docstring provided.
    - `register_affordance(self, *, affordance_id: str, object_type: str, duration: int, effects: dict[str, float], preconditions: Iterable[str] | None = None, hooks: Mapping[str, Iterable[str]] | None = None) -> None` — Register an affordance available in the world.
    - `apply_actions(self, actions: dict[str, Any]) -> None` — Apply agent actions for the current tick.
    - `resolve_affordances(self, current_tick: int) -> None` — Resolve queued affordances and hooks.
    - `running_affordances_snapshot(self) -> dict[str, RunningAffordanceState]` — Return a serializable view of running affordances (for tests/telemetry).
    - `request_ctx_reset(self, agent_id: str) -> None` — Mark an agent so the next observation toggles ctx_reset_flag.
    - `consume_ctx_reset_requests(self) -> set[str]` — Return and clear pending ctx-reset requests.
    - `snapshot(self) -> dict[str, AgentSnapshot]` — Return a shallow copy of the agent dictionary for observers.
    - `local_view(self, agent_id: str, radius: int, *, include_agents: bool = True, include_objects: bool = True) -> dict[str, Any]` — Return local neighborhood information for observation builders.
    - `agent_context(self, agent_id: str) -> dict[str, object]` — Return scalar context fields for the requested agent.
    - `active_reservations(self) -> dict[str, str]` — Expose a copy of active reservations for diagnostics/tests.
    - `drain_events(self) -> list[dict[str, Any]]` — Return all pending events accumulated up to the current tick.
    - `_record_queue_conflict(self, *, object_id: str, actor: str, rival: str, reason: str, queue_length: int, intensity: float | None = None) -> None` — No docstring provided.
    - `register_rivalry_conflict(self, agent_a: str, agent_b: str, *, intensity: float = 1.0, reason: str = 'conflict') -> None` — No docstring provided.
    - `_apply_rivalry_conflict(self, agent_a: str, agent_b: str, *, intensity: float = 1.0, reason: str = 'conflict') -> None` — No docstring provided.
    - `rivalry_snapshot(self) -> dict[str, dict[str, float]]` — Expose rivalry ledgers for telemetry/diagnostics.
    - `relationships_snapshot(self) -> dict[str, dict[str, dict[str, float]]]` — No docstring provided.
    - `relationship_tie(self, agent_id: str, other_id: str) -> RelationshipTie | None` — Return the current relationship tie between two agents, if any.
    - `consume_chat_events(self) -> list[dict[str, Any]]` — Return chat events staged for reward calculations and clear the buffer.
    - `consume_relationship_avoidance_events(self) -> list[dict[str, Any]]` — Return relationship avoidance events recorded since the last call.
    - `rivalry_value(self, agent_id: str, other_id: str) -> float` — Return the rivalry score between two agents, if present.
    - `rivalry_should_avoid(self, agent_id: str, other_id: str) -> bool` — No docstring provided.
    - `rivalry_top(self, agent_id: str, limit: int) -> list[tuple[str, float]]` — No docstring provided.
    - `consume_rivalry_events(self) -> list[dict[str, Any]]` — Return rivalry events recorded since the last call.
    - `_get_rivalry_ledger(self, agent_id: str) -> RivalryLedger` — No docstring provided.
    - `_get_relationship_ledger(self, agent_id: str) -> RelationshipLedger` — No docstring provided.
    - `_relationship_parameters(self) -> RelationshipParameters` — No docstring provided.
    - `_personality_for(self, agent_id: str) -> Personality` — No docstring provided.
    - `_apply_relationship_delta(self, owner_id: str, other_id: str, *, delta: RelationshipDelta, event: RelationshipEvent) -> None` — No docstring provided.
    - `_rivalry_parameters(self) -> RivalryParameters` — No docstring provided.
    - `_decay_rivalry_ledgers(self) -> None` — No docstring provided.
    - `_decay_relationship_ledgers(self) -> None` — No docstring provided.
    - `_record_relationship_eviction(self, owner_id: str, other_id: str, reason: str) -> None` — No docstring provided.
    - `relationship_metrics_snapshot(self) -> dict[str, object]` — No docstring provided.
    - `load_relationship_metrics(self, payload: Mapping[str, object] | None) -> None` — No docstring provided.
    - `load_relationship_snapshot(self, snapshot: dict[str, dict[str, dict[str, float]]]) -> None` — Restore relationship ledgers from persisted snapshot data.
    - `update_relationship(self, agent_a: str, agent_b: str, *, trust: float = 0.0, familiarity: float = 0.0, rivalry: float = 0.0, event: RelationshipEvent = 'generic') -> None` — No docstring provided.
    - `record_chat_success(self, speaker: str, listener: str, quality: float) -> None` — No docstring provided.
    - `record_chat_failure(self, speaker: str, listener: str) -> None` — No docstring provided.
    - `record_relationship_guard_block(self, *, agent_id: str, reason: str, target_agent: str | None = None, object_id: str | None = None) -> None` — No docstring provided.
    - `_sync_reservation(self, object_id: str) -> None` — No docstring provided.
    - `_handle_blocked(self, object_id: str, tick: int) -> None` — No docstring provided.
    - `_start_affordance(self, agent_id: str, object_id: str, affordance_id: str) -> bool` — No docstring provided.
    - `_apply_affordance_effects(self, agent_id: str, effects: dict[str, float]) -> None` — No docstring provided.
    - `_emit_event(self, event: str, payload: dict[str, Any]) -> None` — No docstring provided.
    - `_load_affordance_definitions(self) -> None` — No docstring provided.
    - `affordance_manifest_metadata(self) -> dict[str, object]` — Expose manifest metadata (path, checksum, counts) for telemetry.
    - `find_nearest_object_of_type(self, object_type: str, origin: tuple[int, int]) -> tuple[int, int] | None` — No docstring provided.
    - `_apply_need_decay(self) -> None` — No docstring provided.
    - `apply_nightly_reset(self) -> list[str]` — Return agents home, refresh needs, and reset employment flags.
    - `_assign_jobs_to_agents(self) -> None` — No docstring provided.
    - `_apply_job_state(self) -> None` — No docstring provided.
    - `_apply_job_state_legacy(self) -> None` — No docstring provided.
    - `_apply_job_state_enforced(self) -> None` — No docstring provided.
    - `_employment_context_defaults(self) -> dict[str, Any]` — No docstring provided.
    - `_get_employment_context(self, agent_id: str) -> dict[str, Any]` — No docstring provided.
    - `_employment_context_wages(self, agent_id: str) -> float` — No docstring provided.
    - `_employment_context_punctuality(self, agent_id: str) -> float` — No docstring provided.
    - `_employment_idle_state(self, snapshot: AgentSnapshot, ctx: dict[str, Any]) -> None` — No docstring provided.
    - `_employment_prepare_state(self, snapshot: AgentSnapshot, ctx: dict[str, Any]) -> None` — No docstring provided.
    - `_employment_begin_shift(self, ctx: dict[str, Any], start: int, end: int) -> None` — No docstring provided.
    - `_employment_determine_state(self, *, ctx: dict[str, Any], tick: int, start: int, at_required_location: bool, employment_cfg: EmploymentConfig) -> str` — No docstring provided.
    - `_employment_apply_state_effects(self, *, snapshot: AgentSnapshot, ctx: dict[str, Any], state: str, at_required_location: bool, wage_rate: float, lateness_penalty: float, employment_cfg: EmploymentConfig) -> None` — No docstring provided.
    - `_employment_finalize_shift(self, *, snapshot: AgentSnapshot, ctx: dict[str, Any], employment_cfg: EmploymentConfig, job_id: str | None) -> None` — No docstring provided.
    - `_employment_coworkers_on_shift(self, snapshot: AgentSnapshot) -> list[str]` — No docstring provided.
    - `_employment_enqueue_exit(self, agent_id: str, tick: int) -> None` — No docstring provided.
    - `_employment_remove_from_queue(self, agent_id: str) -> None` — No docstring provided.
    - `employment_queue_snapshot(self) -> dict[str, Any]` — No docstring provided.
    - `employment_request_manual_exit(self, agent_id: str, tick: int) -> bool` — No docstring provided.
    - `employment_defer_exit(self, agent_id: str) -> bool` — No docstring provided.
    - `employment_exits_today(self) -> int` — No docstring provided.
    - `set_employment_exits_today(self, value: int) -> None` — No docstring provided.
    - `reset_employment_exits_today(self) -> None` — No docstring provided.
    - `increment_employment_exits_today(self) -> None` — No docstring provided.
    - `_update_basket_metrics(self) -> None` — No docstring provided.
    - `_restock_economy(self) -> None` — No docstring provided.
    - `apply_price_spike(self, event_id: str, *, magnitude: float, targets: Iterable[str] | None = None) -> None` — No docstring provided.
    - `clear_price_spike(self, event_id: str) -> None` — No docstring provided.
    - `apply_utility_outage(self, event_id: str, utility: str) -> None` — No docstring provided.
    - `clear_utility_outage(self, event_id: str, utility: str) -> None` — No docstring provided.
    - `apply_arranged_meet(self, *, location: str | None, targets: Iterable[str] | None = None) -> None` — No docstring provided.
    - `utility_online(self, utility: str) -> bool` — No docstring provided.
    - `_resolve_price_targets(self, targets: Iterable[str] | None) -> list[str]` — No docstring provided.
    - `_recompute_price_spikes(self) -> None` — No docstring provided.
    - `_set_utility_state(self, utility: str, *, online: bool) -> None` — No docstring provided.
    - `economy_settings(self) -> dict[str, float]` — Return the current economy configuration values.
    - `active_price_spikes(self) -> dict[str, dict[str, object]]` — Return a summary of currently active price spike events.
    - `utility_snapshot(self) -> dict[str, bool]` — Return on/off status for tracked utilities.

### Functions
- `_default_personality() -> Personality` — Provide a neutral personality for agents lacking explicit traits.

### Constants and Configuration
- `_CONSOLE_HISTORY_LIMIT` = 512
- `_CONSOLE_RESULT_BUFFER_LIMIT` = 256
- `_BASE_NEEDS` = ('hunger', 'hygiene', 'energy')

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.agents.models, townlet.agents.relationship_modifiers, townlet.config, townlet.config.affordance_manifest, townlet.console.command, townlet.observations.embedding, townlet.telemetry.relationship_metrics, townlet.world.affordances, townlet.world.console_bridge, townlet.world.employment, townlet.world.hooks, townlet.world.preconditions, townlet.world.queue_conflict, townlet.world.queue_manager, townlet.world.relationships, townlet.world.rivalry

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/world/hooks/__init__.py

- **File path**: `src/townlet/world/hooks/__init__.py`
- **Purpose**: Affordance hook plug-in namespace.
- **Dependencies**: stdlib [__future__, importlib, logging, typing] / third-party [None] / internal [townlet.world.grid]
- **Related modules**: townlet.world.grid
- **Lines of code**: 61
- **Environment variables**: None detected

### Classes
- None

### Functions
- `load_modules(world: 'WorldState', module_paths: Iterable[str]) -> tuple[list[str], list[tuple[str, str]]]` — Import hook modules and let them register against the given world.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.world.grid

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/world/hooks/default.py

- **File path**: `src/townlet/world/hooks/default.py`
- **Purpose**: Built-in affordance hook handlers.
- **Dependencies**: stdlib [__future__, typing] / third-party [None] / internal [townlet.world.grid]
- **Related modules**: townlet.world.grid
- **Lines of code**: 313
- **Environment variables**: None detected

### Classes
- None

### Functions
- `register_hooks(world: 'WorldState') -> None` — Register built-in affordance hooks with the provided world.
- `_on_attempt_shower(context: dict[str, Any]) -> None` — No docstring provided.
- `_on_finish_shower(context: dict[str, Any]) -> None` — No docstring provided.
- `_on_no_power(context: dict[str, Any]) -> None` — No docstring provided.
- `_on_attempt_eat(context: dict[str, Any]) -> None` — No docstring provided.
- `_on_finish_eat(context: dict[str, Any]) -> None` — No docstring provided.
- `_on_attempt_cook(context: dict[str, Any]) -> None` — No docstring provided.
- `_on_finish_cook(context: dict[str, Any]) -> None` — No docstring provided.
- `_on_cook_fail(context: dict[str, Any]) -> None` — No docstring provided.
- `_on_attempt_sleep(context: dict[str, Any]) -> None` — No docstring provided.
- `_on_finish_sleep(context: dict[str, Any]) -> None` — No docstring provided.
- `_abort_affordance(world: 'WorldState', spec: Any, agent_id: str, object_id: str, reason: str) -> None` — No docstring provided.

### Constants and Configuration
- `_AFFORDANCE_FAIL_EVENT` = 'affordance_fail'
- `_SHOWER_COMPLETE_EVENT` = 'shower_complete'
- `_SHOWER_POWER_EVENT` = 'shower_power_outage'
- `_SLEEP_COMPLETE_EVENT` = 'sleep_complete'

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.world.grid

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/world/preconditions.py

- **File path**: `src/townlet/world/preconditions.py`
- **Purpose**: Affordance precondition compilation and evaluation helpers.
- **Dependencies**: stdlib [__future__, ast, dataclasses, re, typing] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 289
- **Environment variables**: None detected

### Classes
- **PreconditionSyntaxError(ValueError)** — Raised when a manifest precondition has invalid syntax.
  - Methods: None
- **PreconditionEvaluationError(RuntimeError)** — Raised when evaluation fails due to missing context or type errors.
  - Methods: None
- **CompiledPrecondition(object)** — Stores the parsed AST and metadata for a precondition.
  - Attributes:
    - `source` (type=str)
    - `tree` (type=ast.AST)
    - `identifiers` (type=tuple[str, ...])
  - Methods: None
- **_IdentifierCollector(ast.NodeVisitor)** — No docstring provided.
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `visit_Name(self, node: ast.Name) -> None` — Collect bare identifiers used in the expression.

### Functions
- `_normalize_expression(expression: str) -> str` — No docstring provided.
- `_validate_tree(tree: ast.AST, source: str) -> tuple[str, ...]` — No docstring provided.
- `compile_preconditions(expressions: Iterable[str]) -> tuple[CompiledPrecondition, ...]` — Compile manifest preconditions, raising on syntax errors.
- `compile_precondition(expression: str) -> CompiledPrecondition` — Compile a single precondition expression.
- `_resolve_name(name: str, context: Mapping[str, Any]) -> Any` — No docstring provided.
- `_resolve_attr(value: Any, attr: str) -> Any` — No docstring provided.
- `_resolve_subscript(value: Any, key: Any) -> Any` — No docstring provided.
- `_evaluate(node: ast.AST, context: Mapping[str, Any]) -> Any` — No docstring provided.
- `_apply_compare(operator: ast.cmpop, left: Any, right: Any) -> bool` — No docstring provided.
- `evaluate_preconditions(preconditions: Sequence[CompiledPrecondition], context: Mapping[str, Any]) -> tuple[bool, CompiledPrecondition | None]` — Evaluate compiled preconditions against the provided context.

### Constants and Configuration
- `_ALLOWED_COMPARE_OPS` = (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn)
- `_ALLOWED_BOOL_OPS` = (ast.And, ast.Or)
- `_ALLOWED_UNARY_OPS` = (ast.Not, ast.USub, ast.UAdd)
- `_ALLOWED_NODE_TYPES` = (ast.Expression, ast.BoolOp, ast.Compare, ast.Name, ast.Attribute, ast.Subscript, ast.Constant, ast.UnaryOp, ast.Tuple, ast.List, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn, ast.And, ast.Or, ast.Load, ast.USub, ast.UAdd, ast.Not)

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/world/queue_conflict.py

- **File path**: `src/townlet/world/queue_conflict.py`
- **Purpose**: Queue conflict and rivalry event tracking.
- **Dependencies**: stdlib [__future__, collections, typing] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 152
- **Environment variables**: None detected

### Classes
- **QueueConflictTracker(object)** — Tracks queue conflict outcomes and rivalry/chat events.
  - Methods:
    - `__init__(self, *, world: Any, record_rivalry_conflict: Callable[..., None]) -> None` — No docstring provided.
    - `record_queue_conflict(self, *, object_id: str, actor: str, rival: str, reason: str, queue_length: int, intensity: float | None = None) -> None` — No docstring provided.
    - `record_chat_event(self, payload: dict[str, object]) -> None` — No docstring provided.
    - `consume_chat_events(self) -> list[dict[str, object]]` — No docstring provided.
    - `record_avoidance_event(self, payload: dict[str, object]) -> None` — No docstring provided.
    - `consume_avoidance_events(self) -> list[dict[str, object]]` — No docstring provided.
    - `record_rivalry_event(self, *, tick: int, agent_a: str, agent_b: str, intensity: float, reason: str) -> None` — No docstring provided.
    - `consume_rivalry_events(self) -> list[dict[str, object]]` — No docstring provided.
    - `reset(self) -> None` — No docstring provided.
    - `remove_agent(self, agent_id: str) -> None` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/world/queue_manager.py

- **File path**: `src/townlet/world/queue_manager.py`
- **Purpose**: Queue management with fairness guardrails.
- **Dependencies**: stdlib [__future__, dataclasses, time] / third-party [None] / internal [townlet.config]
- **Related modules**: townlet.config
- **Lines of code**: 287
- **Environment variables**: None detected

### Classes
- **QueueEntry(object)** — Represents an agent waiting to access an interactive object.
  - Attributes:
    - `agent_id` (type=str)
    - `joined_tick` (type=int)
  - Methods: None
- **QueueManager(object)** — Coordinates reservations and fairness across interactive queues.
  - Methods:
    - `__init__(self, config: SimulationConfig) -> None` — No docstring provided.
    - `on_tick(self, tick: int) -> None` — Expire cooldown entries whose window has elapsed.
    - `request_access(self, object_id: str, agent_id: str, tick: int) -> bool` — Attempt to reserve the object for the agent.
    - `release(self, object_id: str, agent_id: str, tick: int, *, success: bool = True) -> None` — Release the reservation and optionally apply cooldown.
    - `record_blocked_attempt(self, object_id: str) -> bool` — Register that the current head was blocked.
    - `active_agent(self, object_id: str) -> str | None` — Return the agent currently holding the reservation, if any.
    - `queue_snapshot(self, object_id: str) -> list[str]` — Return the queue as an ordered list of agent IDs for debugging.
    - `metrics(self) -> dict[str, int]` — Expose counters useful for telemetry.
    - `performance_metrics(self) -> dict[str, int]` — Expose aggregated nanosecond timings and call counts.
    - `reset_performance_metrics(self) -> None` — No docstring provided.
    - `requeue_to_tail(self, object_id: str, agent_id: str, tick: int) -> None` — Append `agent_id` to the end of the queue if not already present.
    - `promote_agent(self, object_id: str, agent_id: str) -> None` — Move `agent_id` to the front of the queue if present.
    - `remove_agent(self, agent_id: str, tick: int) -> None` — Remove `agent_id` from all queues and active reservations.
    - `export_state(self) -> dict[str, object]` — Serialise queue activity for snapshot persistence.
    - `import_state(self, payload: dict[str, object]) -> None` — Restore queue activity from persisted snapshot data.
    - `_assign_next(self, object_id: str, tick: int) -> str | None` — No docstring provided.

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/world/relationships.py

- **File path**: `src/townlet/world/relationships.py`
- **Purpose**: Relationship ledger for Phase 4 social systems.
- **Dependencies**: stdlib [__future__, collections.abc, dataclasses] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 169
- **Environment variables**: None detected

### Classes
- **RelationshipParameters(object)** — Tuning knobs for relationship tie evolution.
  - Attributes:
    - `max_edges` (type=int, default=6)
    - `trust_decay` (type=float, default=0.0)
    - `familiarity_decay` (type=float, default=0.0)
    - `rivalry_decay` (type=float, default=0.01)
  - Methods: None
- **RelationshipTie(object)** — No docstring provided.
  - Attributes:
    - `trust` (type=float, default=0.0)
    - `familiarity` (type=float, default=0.0)
    - `rivalry` (type=float, default=0.0)
  - Methods:
    - `as_dict(self) -> dict[str, float]` — No docstring provided.
- **RelationshipLedger(object)** — Maintains multi-dimensional ties for a single agent.
  - Methods:
    - `__init__(self, *, owner_id: str, params: RelationshipParameters | None = None, eviction_hook: EvictionHook | None = None) -> None` — No docstring provided.
    - `apply_delta(self, other_id: str, *, trust: float = 0.0, familiarity: float = 0.0, rivalry: float = 0.0) -> RelationshipTie` — No docstring provided.
    - `tie_for(self, other_id: str) -> RelationshipTie | None` — Return the tie for ``other_id`` if it exists.
    - `decay(self) -> None` — No docstring provided.
    - `snapshot(self) -> dict[str, dict[str, float]]` — No docstring provided.
    - `inject(self, payload: dict[str, dict[str, float]]) -> None` — No docstring provided.
    - `set_eviction_hook(self, *, owner_id: str, hook: EvictionHook | None) -> None` — No docstring provided.
    - `top_friends(self, limit: int) -> list[tuple[str, RelationshipTie]]` — No docstring provided.
    - `top_rivals(self, limit: int) -> list[tuple[str, RelationshipTie]]` — No docstring provided.
    - `remove_tie(self, other_id: str, *, reason: str = 'removed') -> None` — No docstring provided.
    - `_prune_if_needed(self, *, reason: str) -> None` — No docstring provided.
    - `_emit_eviction(self, other_id: str, *, reason: str) -> None` — No docstring provided.

### Functions
- `_clamp(value: float, *, low: float, high: float) -> float` — No docstring provided.
- `_decay_value(value: float, decay: float, *, minimum: float = -1.0) -> float` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet/world/rivalry.py

- **File path**: `src/townlet/world/rivalry.py`
- **Purpose**: Rivalry state helpers used by conflict intro scaffolding.
- **Dependencies**: stdlib [__future__, collections.abc, dataclasses, typing] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 135
- **Environment variables**: None detected

### Classes
- **RivalryParameters(object)** — Tuning knobs for rivalry evolution.
  - Attributes:
    - `increment_per_conflict` (type=float, default=0.15)
    - `decay_per_tick` (type=float, default=0.01)
    - `min_value` (type=float, default=0.0)
    - `max_value` (type=float, default=1.0)
    - `avoid_threshold` (type=float, default=0.7)
    - `eviction_threshold` (type=float, default=0.05)
    - `max_edges` (type=int, default=6)
  - Methods: None
- **RivalryLedger(object)** — Maintains rivalry scores against other agents for a single actor.
  - Attributes:
    - `owner_id` (type=str)
    - `params` (type=RivalryParameters, default=field(default_factory=RivalryParameters))
    - `eviction_hook` (type=Optional[Callable[[str, str, str], None]], default=None)
    - `_scores` (type=dict[str, float], default=field(default_factory=dict))
  - Methods:
    - `apply_conflict(self, other_id: str, *, intensity: float = 1.0) -> float` — Increase rivalry against `other_id` based on the conflict intensity.
    - `decay(self, ticks: int = 1) -> None` — Apply passive decay across all rivalry edges.
    - `inject(self, pairs: Iterable[tuple[str, float]]) -> None` — Seed rivalry scores from persisted state for round-tripping tests.
    - `score_for(self, other_id: str) -> float` — No docstring provided.
    - `should_avoid(self, other_id: str) -> bool` — Return True when rivalry exceeds the avoidance threshold.
    - `top_rivals(self, limit: int) -> list[tuple[str, float]]` — Return the strongest rivalry edges sorted descending.
    - `remove(self, other_id: str, *, reason: str = 'removed') -> None` — No docstring provided.
    - `encode_features(self, limit: int) -> list[float]` — Encode rivalry magnitudes into a fixed-width list for observations.
    - `snapshot(self) -> dict[str, float]` — Return a copy of rivalry scores for telemetry serialization.
    - `_emit_eviction(self, other_id: str, *, reason: str) -> None` — No docstring provided.

### Functions
- `_clamp(value: float, *, low: float, high: float) -> float` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet_ui/__init__.py

- **File path**: `src/townlet_ui/__init__.py`
- **Purpose**: Observer UI toolkit exports.
- **Dependencies**: stdlib [None] / third-party [commands, telemetry] / internal [None]
- **Related modules**: None
- **Lines of code**: 19
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: commands, telemetry
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet_ui/commands.py

- **File path**: `src/townlet_ui/commands.py`
- **Purpose**: Helper utilities for dispatching console commands asynchronously.
- **Dependencies**: stdlib [__future__, dataclasses, logging, queue, threading, typing] / third-party [None] / internal [townlet.console.handlers]
- **Related modules**: townlet.console.handlers
- **Lines of code**: 147
- **Environment variables**: None detected

### Classes
- **CommandQueueFull(RuntimeError)** — Raised when the executor queue exceeds the configured pending limit.
  - Methods:
    - `__init__(self, pending: int, max_pending: int) -> None` — No docstring provided.
- **ConsoleCommandExecutor(object)** — Background dispatcher that forwards console commands via a router.
  - Methods:
    - `__init__(self, router: Any, *, daemon: bool = True, max_pending: int | None = None, autostart: bool = True) -> None` — No docstring provided.
    - `start(self) -> None` — Start the worker thread if it has not already begun.
    - `pending_count(self) -> int` — Number of commands waiting in the executor queue.
    - `submit(self, command: ConsoleCommand) -> None` — No docstring provided.
    - `submit_payload(self, payload: Mapping[str, Any], *, enqueue: bool = True) -> ConsoleCommand` — Validate and enqueue a structured palette payload.
    - `shutdown(self, timeout: float | None = 1.0) -> None` — No docstring provided.
    - `_worker(self) -> None` — No docstring provided.
- **PaletteCommandRequest(object)** — Normalised representation of a palette command submission.
  - Attributes:
    - `name` (type=str)
    - `args` (type=tuple[Any, ...], default=field(default_factory=tuple))
    - `kwargs` (type=Mapping[str, Any], default=field(default_factory=dict))
  - Methods:
    - `from_payload(cls, payload: Mapping[str, Any]) -> PaletteCommandRequest` — Validate an incoming payload from the palette overlay.
    - `to_console_command(self) -> ConsoleCommand` — Convert into the ConsoleCommand used by the router.

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.console.handlers

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet_ui/dashboard.py

- **File path**: `src/townlet_ui/dashboard.py`
- **Purpose**: Rich-based console dashboard for Townlet observer UI.
- **Dependencies**: stdlib [__future__, collections.abc, dataclasses, difflib, itertools, math, time, typing] / third-party [numpy, rich.columns, rich.console, rich.panel, rich.table, rich.text] / internal [townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet_ui.commands, townlet_ui.telemetry]
- **Related modules**: townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet_ui.commands, townlet_ui.telemetry
- **Lines of code**: 1629
- **Environment variables**: None detected

### Classes
- **PaletteCommandMeta(object)** — Metadata describing a console command for palette display.
  - Attributes:
    - `name` (type=str)
    - `mode` (type=str)
    - `usage` (type=str)
    - `description` (type=str)
  - Methods: None
- **PaletteState(object)** — Represents the rendered state of the palette overlay.
  - Attributes:
    - `visible` (type=bool, default=False)
    - `query` (type=str, default='')
    - `mode_filter` (type=str, default='all')
    - `max_results` (type=int, default=7)
    - `highlight_index` (type=int, default=0)
    - `history_limit` (type=int, default=5)
    - `pending` (type=int, default=0)
    - `status_message` (type=str | None, default=None)
    - `status_style` (type=str, default='dim')
  - Methods:
    - `clamp_history(self, window: int | None) -> None` — No docstring provided.

### Functions
- `_extract_palette_commands(snapshot: TelemetrySnapshot) -> list[PaletteCommandMeta]` — No docstring provided.
- `_score_palette_match(command: PaletteCommandMeta, query: str) -> float` — No docstring provided.
- `_search_palette_commands(commands: list[PaletteCommandMeta], palette: PaletteState) -> list[PaletteCommandMeta]` — No docstring provided.
- `_format_palette_filter_label(mode_filter: str) -> str` — No docstring provided.
- `_build_palette_overlay(snapshot: TelemetrySnapshot, palette: PaletteState) -> Panel | None` — No docstring provided.
- `dispatch_palette_selection(snapshot: TelemetrySnapshot, palette: PaletteState, executor: ConsoleCommandExecutor, *, payload_override: Mapping[str, Any] | None = None, enqueue: bool = True) -> ConsoleCommand` — Dispatch the highlighted palette command via the executor.
- `render_snapshot(snapshot: TelemetrySnapshot, tick: int, refreshed: str, *, palette: PaletteState | None = None) -> Iterable[Panel]` — Yield rich Panels representing the current telemetry snapshot.
- `_build_social_panel(summary: RelationshipSummarySnapshot | None, relationships: RelationshipChurn | None, events: tuple[SocialEventEntry, ...]) -> Panel | None` — No docstring provided.
- `_build_agent_cards_panel(snapshot: TelemetrySnapshot) -> Panel | None` — No docstring provided.
- `_format_need_bar(name: str, value: float) -> Text` — No docstring provided.
- `_sparkline_text(series: Sequence[float] | tuple[float, ...], *, style: str = 'cyan', width: int = 12) -> Text` — No docstring provided.
- `_row_with_sparkline(text: Text, sparkline: Text) -> Table` — No docstring provided.
- `_build_perturbation_panel(snapshot: TelemetrySnapshot) -> Panel | None` — No docstring provided.
- `_build_social_status_panel(summary: RelationshipSummarySnapshot | None) -> Panel | None` — No docstring provided.
- `_build_social_cards_panel(summary: RelationshipSummarySnapshot | None) -> Panel | None` — No docstring provided.
- `_build_social_churn_panel(summary: RelationshipSummarySnapshot | None, relationships: RelationshipChurn | None) -> Panel | None` — No docstring provided.
- `_build_social_events_panel(events: tuple[SocialEventEntry, ...]) -> Panel | None` — No docstring provided.
- `_format_friends(friends: tuple[FriendSummary, ...]) -> str` — No docstring provided.
- `_format_rivals(rivals: tuple[RivalSummary, ...]) -> str` — No docstring provided.
- `_format_event_type(event_type: str) -> str` — No docstring provided.
- `_summarise_social_event(entry: SocialEventEntry) -> str` — No docstring provided.
- `_extract_churn_total(summary: RelationshipSummarySnapshot | None, relationships: RelationshipChurn | None) -> int` — No docstring provided.
- `_format_top_entries(entries: Mapping[str, int]) -> str` — No docstring provided.
- `_build_narration_panel(snapshot: TelemetrySnapshot) -> Panel` — No docstring provided.
- `_build_anneal_panel(snapshot: TelemetrySnapshot) -> Panel` — No docstring provided.
- `_promotion_border_style(promotion: PromotionSnapshot | None) -> str` — No docstring provided.
- `_derive_promotion_reason(promotion: PromotionSnapshot, status: AnnealStatus | None) -> str` — No docstring provided.
- `_format_metadata_summary(metadata: Mapping[str, Any]) -> str` — No docstring provided.
- `_build_promotion_history_panel(history: Iterable[Mapping[str, Any]], border_style: str) -> Panel` — No docstring provided.
- `_format_history_metadata(entry: Mapping[str, Any]) -> str` — No docstring provided.
- `_safe_format(value: float | None) -> str` — No docstring provided.
- `_format_optional_float(value: float | None) -> str` — No docstring provided.
- `_build_policy_inspector_panel(snapshot: TelemetrySnapshot) -> Panel` — No docstring provided.
- `_build_relationship_overlay_panel(snapshot: TelemetrySnapshot) -> Panel` — No docstring provided.
- `_format_delta(value: float, inverse: bool = False) -> str` — No docstring provided.
- `_build_kpi_panel(snapshot: TelemetrySnapshot) -> Panel` — No docstring provided.
- `_trend_from_series(series: list[float]) -> tuple[str, str]` — No docstring provided.
- `_humanize_kpi(key: str) -> str` — No docstring provided.
- `run_dashboard(loop: SimulationLoop, *, refresh_interval: float = 1.0, max_ticks: int = 0, approve: str | None = None, defer: str | None = None, focus_agent: str | None = None, show_coords: bool = False, palette_state: PaletteState | None = None, on_tick: Callable[[SimulationLoop, ConsoleCommandExecutor, int], None] | None = None) -> None` — Continuously render dashboard against a SimulationLoop instance.
- `_build_map_panel(snapshot: TelemetrySnapshot, obs_batch: Mapping[str, dict[str, np.ndarray]], focus_agent: str | None, show_coords: bool = False) -> Panel | None` — No docstring provided.

### Constants and Configuration
- `MAP_AGENT_CHAR` = 'A'
- `MAP_CENTER_CHAR` = 'S'
- `NARRATION_CATEGORY_STYLES` = {'utility_outage': ('Utility Outage', 'bold red'), 'shower_complete': ('Shower Complete', 'cyan'), 'sleep_complete': ('Sleep Complete', 'green'), 'queue_conflict': ('Queue Conflict', 'magenta')}
- `NEED_SPARK_STYLES` = {'hunger': 'magenta', 'hygiene': 'cyan', 'energy': 'yellow'}
- `_SPARKLINE_CHARS` = ' .:-=+*#%@'

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy, rich.columns, rich.console, rich.panel, rich.table, rich.text
- Internal: townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet_ui.commands, townlet_ui.telemetry

### Code Quality Notes
- No obvious static issues detected by automated scan.


## src/townlet_ui/telemetry.py

- **File path**: `src/townlet_ui/telemetry.py`
- **Purpose**: Schema-aware telemetry client utilities for observer UI components.
- **Dependencies**: stdlib [__future__, collections.abc, dataclasses, typing] / third-party [None] / internal [townlet.console.handlers]
- **Related modules**: townlet.console.handlers
- **Lines of code**: 1083
- **Environment variables**: None detected

### Classes
- **EmploymentMetrics(object)** — No docstring provided.
  - Attributes:
    - `pending` (type=list[str])
    - `pending_count` (type=int)
    - `exits_today` (type=int)
    - `daily_exit_cap` (type=int)
    - `queue_limit` (type=int)
    - `review_window` (type=int)
  - Methods: None
- **QueueHistoryEntry(object)** — No docstring provided.
  - Attributes:
    - `tick` (type=int)
    - `cooldown_delta` (type=int)
    - `ghost_step_delta` (type=int)
    - `rotation_delta` (type=int)
    - `totals` (type=Mapping[str, int])
  - Methods: None
- **RivalryEventEntry(object)** — No docstring provided.
  - Attributes:
    - `tick` (type=int)
    - `agent_a` (type=str)
    - `agent_b` (type=str)
    - `intensity` (type=float)
    - `reason` (type=str)
  - Methods: None
- **ConflictMetrics(object)** — No docstring provided.
  - Attributes:
    - `queue_cooldown_events` (type=int)
    - `queue_ghost_step_events` (type=int)
    - `queue_rotation_events` (type=int)
    - `queue_history` (type=tuple[QueueHistoryEntry, ...])
    - `rivalry_agents` (type=int)
    - `rivalry_events` (type=tuple[RivalryEventEntry, ...])
    - `raw` (type=Mapping[str, Any])
  - Methods: None
- **AffordanceRuntimeSnapshot(object)** — No docstring provided.
  - Attributes:
    - `running_count` (type=int)
    - `running` (type=Mapping[str, Mapping[str, Any]])
    - `active_reservations` (type=Mapping[str, str])
    - `event_counts` (type=Mapping[str, int])
  - Methods: None
- **NarrationEntry(object)** — No docstring provided.
  - Attributes:
    - `tick` (type=int)
    - `category` (type=str)
    - `message` (type=str)
    - `priority` (type=bool)
    - `data` (type=Mapping[str, Any])
  - Methods: None
- **RelationshipChurn(object)** — No docstring provided.
  - Attributes:
    - `window_start` (type=int)
    - `window_end` (type=int)
    - `total_evictions` (type=int)
    - `per_owner` (type=Mapping[str, int])
    - `per_reason` (type=Mapping[str, int])
  - Methods: None
- **RelationshipUpdate(object)** — No docstring provided.
  - Attributes:
    - `owner` (type=str)
    - `other` (type=str)
    - `status` (type=str)
    - `trust` (type=float)
    - `familiarity` (type=float)
    - `rivalry` (type=float)
    - `delta_trust` (type=float)
    - `delta_familiarity` (type=float)
    - `delta_rivalry` (type=float)
  - Methods: None
- **AgentSummary(object)** — No docstring provided.
  - Attributes:
    - `agent_id` (type=str)
    - `wallet` (type=float)
    - `shift_state` (type=str)
    - `attendance_ratio` (type=float)
    - `wages_withheld` (type=float)
    - `lateness_counter` (type=int)
    - `on_shift` (type=bool)
    - `job_id` (type=str | None)
    - `needs` (type=Mapping[str, float])
    - `exit_pending` (type=bool)
    - `late_ticks_today` (type=int)
    - `meals_cooked` (type=int)
    - `meals_consumed` (type=int)
    - `basket_cost` (type=float)
  - Methods: None
- **RelationshipOverlayEntry(object)** — No docstring provided.
  - Attributes:
    - `other` (type=str)
    - `trust` (type=float)
    - `familiarity` (type=float)
    - `rivalry` (type=float)
    - `delta_trust` (type=float)
    - `delta_familiarity` (type=float)
    - `delta_rivalry` (type=float)
  - Methods: None
- **FriendSummary(object)** — No docstring provided.
  - Attributes:
    - `agent` (type=str)
    - `trust` (type=float)
    - `familiarity` (type=float)
    - `rivalry` (type=float)
  - Methods: None
- **RivalSummary(object)** — No docstring provided.
  - Attributes:
    - `agent` (type=str)
    - `rivalry` (type=float)
  - Methods: None
- **RelationshipSummaryEntry(object)** — No docstring provided.
  - Attributes:
    - `top_friends` (type=tuple[FriendSummary, ...])
    - `top_rivals` (type=tuple[RivalSummary, ...])
  - Methods: None
- **RelationshipSummarySnapshot(object)** — No docstring provided.
  - Attributes:
    - `per_agent` (type=Mapping[str, RelationshipSummaryEntry])
    - `churn_metrics` (type=Mapping[str, Any])
  - Methods: None
- **SocialEventEntry(object)** — No docstring provided.
  - Attributes:
    - `type` (type=str)
    - `payload` (type=Mapping[str, Any])
  - Methods: None
- **PolicyInspectorAction(object)** — No docstring provided.
  - Attributes:
    - `action` (type=str)
    - `probability` (type=float)
  - Methods: None
- **PolicyInspectorEntry(object)** — No docstring provided.
  - Attributes:
    - `agent_id` (type=str)
    - `tick` (type=int)
    - `selected_action` (type=str)
    - `log_prob` (type=float)
    - `value_pred` (type=float)
    - `top_actions` (type=list[PolicyInspectorAction])
  - Methods: None
- **PriceSpikeEntry(object)** — No docstring provided.
  - Attributes:
    - `event_id` (type=str)
    - `magnitude` (type=float)
    - `targets` (type=tuple[str, ...])
  - Methods: None
- **AnnealStatus(object)** — No docstring provided.
  - Attributes:
    - `stage` (type=str)
    - `cycle` (type=float | None)
    - `dataset` (type=str)
    - `bc_accuracy` (type=float | None)
    - `bc_threshold` (type=float | None)
    - `bc_passed` (type=bool)
    - `loss_flag` (type=bool)
    - `queue_flag` (type=bool)
    - `intensity_flag` (type=bool)
    - `loss_baseline` (type=float | None)
    - `queue_baseline` (type=float | None)
    - `intensity_baseline` (type=float | None)
  - Methods: None
- **TransportStatus(object)** — No docstring provided.
  - Attributes:
    - `connected` (type=bool)
    - `dropped_messages` (type=int)
    - `last_error` (type=str | None)
    - `last_success_tick` (type=int | None)
    - `last_failure_tick` (type=int | None)
    - `queue_length` (type=int)
    - `last_flush_duration_ms` (type=float | None)
  - Methods: None
- **StabilitySnapshot(object)** — No docstring provided.
  - Attributes:
    - `alerts` (type=tuple[str, ...])
    - `metrics` (type=Mapping[str, Any])
  - Methods: None
- **HealthStatus(object)** — No docstring provided.
  - Attributes:
    - `tick` (type=int)
    - `tick_duration_ms` (type=float)
    - `telemetry_queue` (type=int)
    - `telemetry_dropped` (type=int)
    - `perturbations_pending` (type=int)
    - `perturbations_active` (type=int)
    - `employment_exit_queue` (type=int)
    - `raw` (type=Mapping[str, Any])
  - Methods: None
- **PromotionSnapshot(object)** — No docstring provided.
  - Attributes:
    - `state` (type=str | None)
    - `pass_streak` (type=int)
    - `required_passes` (type=int)
    - `candidate_ready` (type=bool)
    - `candidate_ready_tick` (type=int | None)
    - `last_result` (type=str | None)
    - `last_evaluated_tick` (type=int | None)
    - `candidate_metadata` (type=Mapping[str, Any] | None)
    - `current_release` (type=Mapping[str, Any] | None)
    - `history` (type=tuple[Mapping[str, Any], ...])
  - Methods: None
- **PerturbationSnapshot(object)** — No docstring provided.
  - Attributes:
    - `active` (type=Mapping[str, Mapping[str, Any]])
    - `pending` (type=tuple[Mapping[str, Any], ...])
    - `cooldowns_spec` (type=Mapping[str, int])
    - `cooldowns_agents` (type=Mapping[str, Mapping[str, int]])
  - Methods: None
- **TelemetryHistory(object)** — No docstring provided.
  - Attributes:
    - `needs` (type=Mapping[str, Mapping[str, tuple[float, ...]]])
    - `wallet` (type=Mapping[str, tuple[float, ...]])
    - `rivalry` (type=Mapping[str, Mapping[str, tuple[float, ...]]])
  - Methods: None
- **TelemetrySnapshot(object)** — No docstring provided.
  - Attributes:
    - `schema_version` (type=str)
    - `schema_warning` (type=str | None)
    - `employment` (type=EmploymentMetrics)
    - `affordance_runtime` (type=AffordanceRuntimeSnapshot)
    - `conflict` (type=ConflictMetrics)
    - `narrations` (type=list[NarrationEntry])
    - `narration_state` (type=Mapping[str, Any])
    - `relationships` (type=RelationshipChurn | None)
    - `relationship_snapshot` (type=Mapping[str, Mapping[str, Mapping[str, float]]])
    - `relationship_updates` (type=list[RelationshipUpdate])
    - `relationship_overlay` (type=Mapping[str, list[RelationshipOverlayEntry]])
    - `agents` (type=list[AgentSummary])
    - `anneal` (type=AnnealStatus | None)
    - `policy_inspector` (type=list[PolicyInspectorEntry])
    - `promotion` (type=PromotionSnapshot | None)
    - `stability` (type=StabilitySnapshot)
    - `kpis` (type=Mapping[str, list[float]])
    - `transport` (type=TransportStatus)
    - `health` (type=HealthStatus | None)
    - `economy_settings` (type=Mapping[str, float])
    - `price_spikes` (type=tuple[PriceSpikeEntry, ...])
    - `utilities` (type=Mapping[str, bool])
    - `relationship_summary` (type=RelationshipSummarySnapshot | None)
    - `social_events` (type=tuple[SocialEventEntry, ...])
    - `perturbations` (type=PerturbationSnapshot)
    - `console_commands` (type=Mapping[str, Mapping[str, Any]])
    - `console_results` (type=tuple[Mapping[str, Any], ...])
    - `history` (type=TelemetryHistory | None)
    - `raw` (type=Mapping[str, Any])
  - Methods: None
- **SchemaMismatchError(RuntimeError)** — Raised when telemetry schema is newer than the client supports.
  - Methods: None
- **TelemetryClient(object)** — Lightweight helper to parse telemetry payloads for the observer UI.
  - Methods:
    - `__init__(self, *, expected_schema_prefix: str = SUPPORTED_SCHEMA_PREFIX, history_window: int | None = 30) -> None` — No docstring provided.
    - `parse_snapshot(self, payload: Mapping[str, Any]) -> TelemetrySnapshot` — Validate and convert a telemetry payload into dataclasses.
    - `from_console(self, router: Any) -> TelemetrySnapshot` — Fetch snapshot via console router (expects telemetry_snapshot command).
    - `_check_schema(self, version: str) -> str | None` — No docstring provided.
    - `_parse_perturbations(self, payload: object) -> PerturbationSnapshot` — No docstring provided.
    - `_get_section(payload: Mapping[str, Any], key: str, expected: type) -> Mapping[str, Any]` — No docstring provided.

### Functions
- `_maybe_float(value: object) -> float | None` — No docstring provided.
- `_coerce_float(value: object, default: float = 0.0) -> float` — No docstring provided.
- `_coerce_mapping(value: object) -> Mapping[str, Any] | None` — No docstring provided.
- `_coerce_history_entries(value: object) -> tuple[Mapping[str, Any], ...]` — No docstring provided.
- `_coerce_series(value: object) -> tuple[float, ...]` — No docstring provided.
- `_console_command(name: str) -> Any` — Helper to build console command dataclass without importing CLI package.

### Constants and Configuration
- `SUPPORTED_SCHEMA_PREFIX` = '0.9'

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.console.handlers

### Code Quality Notes
- No obvious static issues detected by automated scan.


## tests/__init__.py

- **File path**: `tests/__init__.py`
- **Purpose**: Test package marker for Townlet.
- **Dependencies**: stdlib [None] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 1
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## tests/conftest.py

- **File path**: `tests/conftest.py`
- **Purpose**: Pytest configuration ensuring project imports resolve during tests.
- **Dependencies**: stdlib [__future__, pathlib, sys] / third-party [pytest] / internal [tests.runtime_stubs]
- **Related modules**: tests.runtime_stubs
- **Lines of code**: 25
- **Environment variables**: None detected

### Classes
- None

### Functions
- `stub_affordance_runtime_factory()` — No docstring provided.

### Constants and Configuration
- `ROOT` = Path(__file__).resolve().parents[1]
- `SRC` = ROOT / 'src'

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: tests.runtime_stubs

### Code Quality Notes
- No obvious static issues detected by automated scan.


## tests/helpers/social.py

- **File path**: `tests/helpers/social.py`
- **Purpose**: Test helpers for seeding social interaction data.
- **Dependencies**: stdlib [__future__] / third-party [None] / internal [townlet.world.grid]
- **Related modules**: townlet.world.grid
- **Lines of code**: 23
- **Environment variables**: None detected

### Classes
- None

### Functions
- `seed_relationship_activity(world: WorldState, *, agent_a: str, agent_b: str, rivalry_intensity: float = 1.0) -> None` — Populate trust/familiarity/rivalry metrics for tests expecting social signals.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.world.grid

### Code Quality Notes
- No obvious static issues detected by automated scan.


## tests/hooks/__init__.py

- **File path**: `tests/hooks/__init__.py`
- **Purpose**: Test hook modules for affordance security tests.
- **Dependencies**: stdlib [None] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 1
- **Environment variables**: None detected

### Classes
- None

### Functions
- None

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: Module provides constants or metadata only.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## tests/hooks/sample.py

- **File path**: `tests/hooks/sample.py`
- **Purpose**: Sample hook module for tests.
- **Dependencies**: stdlib [__future__] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 9
- **Environment variables**: None detected

### Classes
- None

### Functions
- `register_hooks(world)` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- No obvious static issues detected by automated scan.


## tests/runtime_stubs.py

- **File path**: `tests/runtime_stubs.py`
- **Purpose**: Stub affordance runtime implementations used by tests.
- **Dependencies**: stdlib [__future__, typing] / third-party [None] / internal [townlet.world.affordances]
- **Related modules**: townlet.world.affordances
- **Lines of code**: 75
- **Environment variables**: None detected

### Classes
- **StubAffordanceRuntime(object)** — Minimal affordance runtime used for testing configuration plumbing.
  - Methods:
    - `__init__(self, context: AffordanceRuntimeContext, *, instrumentation: str = 'off', options: Mapping[str, object] | None = None) -> None` — No docstring provided.
    - `start(self, agent_id: str, object_id: str, affordance_id: str, *, tick: int) -> tuple[bool, dict[str, object]]` — No docstring provided.
    - `release(self, agent_id: str, object_id: str, *, success: bool, reason: str | None, requested_affordance_id: str | None, tick: int) -> tuple[str | None, dict[str, object]]` — No docstring provided.
    - `resolve(self, *, tick: int) -> None` — No docstring provided.
    - `running_snapshot(self) -> dict[str, Any]` — No docstring provided.
    - `clear(self) -> None` — No docstring provided.
    - `remove_agent(self, agent_id: str) -> None` — No docstring provided.
    - `handle_blocked(self, object_id: str, tick: int) -> None` — No docstring provided.

### Functions
- `build_runtime(*, world: Any, context: AffordanceRuntimeContext, config: Any) -> StubAffordanceRuntime` — Factory used by runtime configuration tests.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.world.affordances

### Code Quality Notes
- No obvious static issues detected by automated scan.


## tests/test_affordance_hook_security.py

- **File path**: `tests/test_affordance_hook_security.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib, typing] / third-party [pytest] / internal [townlet.config, townlet.core.sim_loop]
- **Related modules**: townlet.config, townlet.core.sim_loop
- **Lines of code**: 80
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_load_config() -> SimulationLoop` — No docstring provided.
- `test_config_parses_hook_allowlist_defaults()` — No docstring provided.
- `test_hook_allowlist_allows_custom_module(monkeypatch: pytest.MonkeyPatch)` — No docstring provided.
- `test_env_module_not_in_allowlist_rejected(monkeypatch: pytest.MonkeyPatch)` — No docstring provided.
- `test_env_override_disabled_records_rejection(monkeypatch: pytest.MonkeyPatch)` — No docstring provided.
- `test_import_error_rejected(monkeypatch: pytest.MonkeyPatch)` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.core.sim_loop

### Code Quality Notes
- Missing module docstring.


## tests/test_affordance_hooks.py

- **File path**: `tests/test_affordance_hooks.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [None] / internal [townlet.config, townlet.core.sim_loop, townlet.world.grid]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid
- **Lines of code**: 260
- **Environment variables**: None detected

### Classes
- None

### Functions
- `make_world() -> tuple[SimulationLoop, WorldState]` — No docstring provided.
- `request_object(world, object_id: str, agent_id: str) -> None` — No docstring provided.
- `test_affordance_before_after_hooks_fire_once() -> None` — No docstring provided.
- `test_affordance_fail_hook_runs_once_per_failure() -> None` — No docstring provided.
- `test_shower_requires_power() -> None` — No docstring provided.
- `test_shower_completion_emits_event() -> None` — No docstring provided.
- `test_sleep_slots_cycle_and_completion_event() -> None` — No docstring provided.
- `test_sleep_attempt_fails_when_no_slots() -> None` — No docstring provided.
- `test_runtime_running_snapshot_and_remove_agent() -> None` — No docstring provided.
- `test_affordance_outcome_log_is_capped() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_affordance_manifest.py

- **File path**: `tests/test_affordance_manifest.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, hashlib, pathlib] / third-party [pytest] / internal [townlet.config, townlet.telemetry.publisher, townlet.world.grid]
- **Related modules**: townlet.config, townlet.telemetry.publisher, townlet.world.grid
- **Lines of code**: 114
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_configure_with_manifest(manifest_path: Path) -> SimulationConfig` — No docstring provided.
- `test_affordance_manifest_loads_and_exposes_metadata(tmp_path: Path) -> None` — No docstring provided.
- `test_affordance_manifest_duplicate_ids_fail(tmp_path: Path) -> None` — No docstring provided.
- `test_affordance_manifest_missing_duration_fails(tmp_path: Path) -> None` — No docstring provided.
- `test_affordance_manifest_checksum_exposed_in_telemetry(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.telemetry.publisher, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_affordance_preconditions.py

- **File path**: `tests/test_affordance_preconditions.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [pytest] / internal [townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet.world.preconditions]
- **Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet.world.preconditions
- **Lines of code**: 120
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_make_loop() -> tuple[SimulationLoop, object]` — No docstring provided.
- `_request_object(world, object_id: str, agent_id: str) -> None` — No docstring provided.
- `test_compile_preconditions_normalises_booleans() -> None` — No docstring provided.
- `test_compile_preconditions_rejects_function_calls() -> None` — No docstring provided.
- `test_evaluate_preconditions_supports_nested_attributes() -> None` — No docstring provided.
- `test_precondition_failure_blocks_affordance_and_emits_event() -> None` — No docstring provided.
- `test_precondition_success_allows_affordance_start() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet.world.preconditions

### Code Quality Notes
- Missing module docstring.


## tests/test_affordance_runtime_config.py

- **File path**: `tests/test_affordance_runtime_config.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, json, pathlib, subprocess, sys] / third-party [pytest] / internal [townlet.config, townlet.core.sim_loop, townlet.world.affordances]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.affordances
- **Lines of code**: 77
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_runtime_config_factory_and_instrumentation(instrumentation: str, tmp_path: Path) -> None` — No docstring provided.
- `test_runtime_factory_injection_via_fixture(stub_affordance_runtime_factory)` — No docstring provided.
- `test_inspect_affordances_cli_snapshot(tmp_path: Path) -> None` — No docstring provided.
- `test_inspect_affordances_cli_config(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.affordances

### Code Quality Notes
- Missing module docstring.


## tests/test_basket_telemetry.py

- **File path**: `tests/test_basket_telemetry.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [None] / internal [townlet.config, townlet.core.sim_loop, townlet.world.grid]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid
- **Lines of code**: 32
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_basket_cost_in_telemetry_snapshot() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_bc_capture_prototype.py

- **File path**: `tests/test_bc_capture_prototype.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, json, pathlib] / third-party [numpy] / internal [townlet.policy.replay]
- **Related modules**: townlet.policy.replay
- **Lines of code**: 64
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_synthetic_bc_capture_round_trip(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy
- Internal: townlet.policy.replay

### Code Quality Notes
- Missing module docstring.


## tests/test_bc_trainer.py

- **File path**: `tests/test_bc_trainer.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [numpy, pytest] / internal [townlet.policy, townlet.policy.models, townlet.policy.replay]
- **Related modules**: townlet.policy, townlet.policy.models, townlet.policy.replay
- **Lines of code**: 81
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_bc_trainer_overfits_toy_dataset(tmp_path: Path) -> None` — No docstring provided.
- `test_bc_evaluate_accuracy(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy, pytest
- Internal: townlet.policy, townlet.policy.models, townlet.policy.replay

### Code Quality Notes
- Missing module docstring.


## tests/test_behavior_rivalry.py

- **File path**: `tests/test_behavior_rivalry.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [None] / internal [townlet.config, townlet.policy.behavior, townlet.rewards.engine, townlet.world.grid]
- **Related modules**: townlet.config, townlet.policy.behavior, townlet.rewards.engine, townlet.world.grid
- **Lines of code**: 138
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_make_world() -> WorldState` — No docstring provided.
- `test_scripted_behavior_avoids_queue_with_rival() -> None` — No docstring provided.
- `test_scripted_behavior_requests_when_no_rival() -> None` — No docstring provided.
- `test_behavior_retries_after_rival_leaves() -> None` — No docstring provided.
- `test_scripted_behavior_initiates_chat_when_conditions_met() -> None` — No docstring provided.
- `test_scripted_behavior_avoids_chat_when_relationships_disabled() -> None` — No docstring provided.
- `test_scripted_behavior_moves_when_rival_on_same_tile() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.policy.behavior, townlet.rewards.engine, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_capture_scripted_cli.py

- **File path**: `tests/test_capture_scripted_cli.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [json, pathlib, runpy] / third-party [None] / internal [townlet.policy.replay]
- **Related modules**: townlet.policy.replay
- **Lines of code**: 39
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_capture_scripted_idle(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.policy.replay

### Code Quality Notes
- Missing module docstring.


## tests/test_cli_validate_affordances.py

- **File path**: `tests/test_cli_validate_affordances.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib, subprocess, sys] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 95
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_run(*args: str) -> subprocess.CompletedProcess[str]` — No docstring provided.
- `test_validate_affordances_cli_success(tmp_path: Path) -> None` — No docstring provided.
- `test_validate_affordances_cli_failure(tmp_path: Path) -> None` — No docstring provided.
- `test_validate_affordances_cli_bad_precondition(tmp_path: Path) -> None` — No docstring provided.
- `test_validate_affordances_cli_directory(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- `SCRIPT` = Path('scripts/validate_affordances.py').resolve()

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing module docstring.


## tests/test_config_loader.py

- **File path**: `tests/test_config_loader.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib, sys, types] / third-party [pytest, yaml] / internal [townlet.config, townlet.snapshots.migrations]
- **Related modules**: townlet.config, townlet.snapshots.migrations
- **Lines of code**: 319
- **Environment variables**: None detected

### Classes
- None

### Functions
- `poc_config(tmp_path: Path) -> Path` — No docstring provided.
- `test_demo_config_uses_file_transport() -> None` — No docstring provided.
- `test_load_config(poc_config: Path) -> None` — No docstring provided.
- `test_invalid_queue_cooldown_rejected(tmp_path: Path) -> None` — No docstring provided.
- `test_tcp_transport_requires_tls_or_explicit_plaintext(tmp_path: Path) -> None` — No docstring provided.
- `test_tcp_transport_tls_requires_cert_and_key_pair(tmp_path: Path) -> None` — No docstring provided.
- `test_tcp_transport_tls_loads_with_hostname_disabled(tmp_path: Path) -> None` — No docstring provided.
- `test_invalid_embedding_threshold_rejected(tmp_path: Path) -> None` — No docstring provided.
- `test_invalid_embedding_slot_count(tmp_path: Path) -> None` — No docstring provided.
- `test_invalid_affordance_file_absent(tmp_path: Path) -> None` — No docstring provided.
- `test_observation_variant_guard(tmp_path: Path) -> None` — No docstring provided.
- `test_ppo_config_defaults_roundtrip(tmp_path: Path) -> None` — No docstring provided.
- `test_observation_variant_full_supported(tmp_path: Path) -> None` — No docstring provided.
- `test_observation_variant_compact_supported(tmp_path: Path) -> None` — No docstring provided.
- `test_snapshot_autosave_cadence_validation(tmp_path: Path) -> None` — No docstring provided.
- `test_snapshot_identity_overrides_take_precedence(poc_config: Path) -> None` — No docstring provided.
- `test_register_snapshot_migrations_from_config(poc_config: Path) -> None` — No docstring provided.
- `test_telemetry_transport_defaults(poc_config: Path) -> None` — No docstring provided.
- `test_telemetry_file_transport_requires_path(tmp_path: Path) -> None` — No docstring provided.
- `test_telemetry_tcp_transport_requires_endpoint(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest, yaml
- Internal: townlet.config, townlet.snapshots.migrations

### Code Quality Notes
- Missing module docstring.


## tests/test_conflict_scenarios.py

- **File path**: `tests/test_conflict_scenarios.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib, random, types] / third-party [pytest] / internal [townlet.config.loader, townlet.core.sim_loop, townlet.policy.scenario_utils, townlet.world.queue_manager]
- **Related modules**: townlet.config.loader, townlet.core.sim_loop, townlet.policy.scenario_utils, townlet.world.queue_manager
- **Lines of code**: 89
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_run_scenario(config_path: str, ticks: int) -> SimulationLoop` — No docstring provided.
- `test_queue_conflict_scenario_produces_alerts() -> None` — No docstring provided.
- `test_rivalry_decay_scenario_tracks_events() -> None` — No docstring provided.
- `test_queue_manager_randomised_regression(seed: int) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config.loader, townlet.core.sim_loop, townlet.policy.scenario_utils, townlet.world.queue_manager

### Code Quality Notes
- Missing module docstring.


## tests/test_conflict_telemetry.py

- **File path**: `tests/test_conflict_telemetry.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [pytest] / internal [townlet.config, townlet.core.sim_loop, townlet.telemetry.publisher, townlet.world.grid]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.telemetry.publisher, townlet.world.grid
- **Lines of code**: 125
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_conflict_snapshot_reports_rivalry_counts() -> None` — No docstring provided.
- `test_replay_sample_matches_schema(tmp_path: Path) -> None` — No docstring provided.
- `test_conflict_export_import_preserves_history() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.core.sim_loop, townlet.telemetry.publisher, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_console_auth.py

- **File path**: `tests/test_console_auth.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [None] / internal [townlet.config, townlet.telemetry.publisher]
- **Related modules**: townlet.config, townlet.telemetry.publisher
- **Lines of code**: 83
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_config_with_auth() -> TelemetryPublisher` — No docstring provided.
- `test_console_command_requires_token_when_enabled() -> None` — No docstring provided.
- `test_console_command_accepts_valid_viewer_token() -> None` — No docstring provided.
- `test_console_command_assigns_admin_role() -> None` — No docstring provided.
- `test_console_command_rejects_invalid_token() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.telemetry.publisher

### Code Quality Notes
- Missing module docstring.


## tests/test_console_commands.py

- **File path**: `tests/test_console_commands.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [dataclasses, json, pathlib, threading] / third-party [pytest] / internal [townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.snapshots, townlet.snapshots.migrations, townlet.snapshots.state, townlet.world.grid, townlet_ui.commands]
- **Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.snapshots, townlet.snapshots.migrations, townlet.snapshots.state, townlet.world.grid, townlet_ui.commands
- **Lines of code**: 825
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_load_palette_fixture(name: str) -> dict[str, object]` — No docstring provided.
- `_load_palette_error_fixture(name: str) -> dict[str, object]` — No docstring provided.
- `test_palette_command_request_from_payload_normalises() -> None` — No docstring provided.
- `test_palette_command_request_from_payload_validation(payload: dict[str, object], message: str) -> None` — No docstring provided.
- `test_console_executor_submit_payload_enqueues_and_returns_command() -> None` — No docstring provided.
- `test_console_executor_submit_payload_dry_run_only() -> None` — No docstring provided.
- `test_console_executor_queue_limit_guard() -> None` — No docstring provided.
- `test_console_error_fixture_alignment(fixture_name: str) -> None` — No docstring provided.
- `_seed_relationship_state(loop: SimulationLoop) -> None` — No docstring provided.
- `test_console_telemetry_snapshot_returns_payload() -> None` — No docstring provided.
- `test_console_conflict_status_reports_history() -> None` — No docstring provided.
- `test_console_queue_inspect_returns_queue_details() -> None` — No docstring provided.
- `test_console_set_spawn_delay_updates_lifecycle() -> None` — No docstring provided.
- `test_console_rivalry_dump_reports_pairs() -> None` — No docstring provided.
- `test_console_relationship_summary_returns_payload() -> None` — No docstring provided.
- `test_console_relationship_detail_requires_admin_mode() -> None` — No docstring provided.
- `test_console_relationship_detail_returns_payload_for_admin() -> None` — No docstring provided.
- `test_console_relationship_detail_unknown_agent_returns_error() -> None` — No docstring provided.
- `test_console_social_events_limit_and_validation() -> None` — No docstring provided.
- `test_console_narrations_and_relationship_summary_snapshot() -> None` — No docstring provided.
- `test_console_affordance_status_reports_runtime() -> None` — No docstring provided.
- `test_employment_console_commands_manage_queue() -> None` — No docstring provided.
- `test_console_schema_warning_for_newer_version() -> None` — No docstring provided.
- `test_console_perturbation_requires_admin_mode() -> None` — No docstring provided.
- `test_console_perturbation_commands_schedule_and_cancel() -> None` — No docstring provided.
- `test_console_arrange_meet_schedules_event() -> None` — No docstring provided.
- `test_console_arrange_meet_unknown_spec_returns_error() -> None` — No docstring provided.
- `test_console_snapshot_commands(tmp_path: Path) -> None` — No docstring provided.
- `test_console_snapshot_rejects_outside_roots(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.snapshots, townlet.snapshots.migrations, townlet.snapshots.state, townlet.world.grid, townlet_ui.commands

### Code Quality Notes
- Missing module docstring.


## tests/test_console_dispatcher.py

- **File path**: `tests/test_console_dispatcher.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [pytest] / internal [townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid]
- **Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid
- **Lines of code**: 482
- **Environment variables**: None detected

### Classes
- None

### Functions
- `employment_loop() -> SimulationLoop` — No docstring provided.
- `_queue_command(loop: SimulationLoop, payload: dict[str, object]) -> None` — No docstring provided.
- `test_dispatcher_processes_employment_review(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_dispatcher_idempotency_reuses_history(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_dispatcher_requires_admin_mode(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_dispatcher_enforces_cmd_id_for_destructive_ops(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_spawn_command_creates_agent(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_spawn_rejects_duplicate_id(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_teleport_moves_agent(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_teleport_rejects_blocked_tile(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_setneed_updates_needs(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_setneed_rejects_unknown_need(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_price_updates_economy_and_basket(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_price_rejects_unknown_key(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_force_chat_updates_relationship(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_force_chat_requires_distinct_agents(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_set_rel_updates_ties(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_possess_acquire_and_release(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_possess_errors_on_duplicate_or_missing(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_kill_command_removes_agent(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_toggle_mortality_updates_flag(employment_loop: SimulationLoop) -> None` — No docstring provided.
- `test_set_exit_cap_updates_config(employment_loop: SimulationLoop) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_console_events.py

- **File path**: `tests/test_console_events.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [None] / internal [townlet.config, townlet.console.handlers, townlet.telemetry.publisher, townlet.world.grid]
- **Related modules**: townlet.config, townlet.console.handlers, townlet.telemetry.publisher, townlet.world.grid
- **Lines of code**: 40
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_event_stream_receives_published_events() -> None` — No docstring provided.
- `test_event_stream_handles_empty_batch() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.console.handlers, townlet.telemetry.publisher, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_console_promotion.py

- **File path**: `tests/test_console_promotion.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [pytest] / internal [townlet.config, townlet.console.handlers, townlet.core.sim_loop]
- **Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop
- **Lines of code**: 136
- **Environment variables**: None detected

### Classes
- None

### Functions
- `admin_router() -> tuple[SimulationLoop, object]` — No docstring provided.
- `make_ready(loop: SimulationLoop) -> None` — No docstring provided.
- `test_promotion_status_command(admin_router: tuple[SimulationLoop, object]) -> None` — No docstring provided.
- `test_promote_and_rollback_commands(admin_router: tuple[SimulationLoop, object]) -> None` — No docstring provided.
- `test_policy_swap_command(admin_router: tuple[SimulationLoop, object], tmp_path: Path) -> None` — No docstring provided.
- `test_policy_swap_missing_file(admin_router: tuple[SimulationLoop, object]) -> None` — No docstring provided.
- `viewer_router() -> object` — No docstring provided.
- `test_viewer_mode_forbidden(viewer_router: object) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop

### Code Quality Notes
- Missing module docstring.


## tests/test_curate_trajectories.py

- **File path**: `tests/test_curate_trajectories.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, json, pathlib, runpy] / third-party [numpy] / internal [townlet.policy.replay]
- **Related modules**: townlet.policy.replay
- **Lines of code**: 81
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_write_sample(output_dir: Path, stem: str, rewards: np.ndarray, timesteps: int) -> None` — No docstring provided.
- `test_curate_trajectories(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy
- Internal: townlet.policy.replay

### Code Quality Notes
- Missing module docstring.


## tests/test_dashboard_panels.py

- **File path**: `tests/test_dashboard_panels.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib, threading, types] / third-party [rich.console] / internal [townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet_ui.commands, townlet_ui.dashboard, townlet_ui.telemetry]
- **Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet_ui.commands, townlet_ui.dashboard, townlet_ui.telemetry
- **Lines of code**: 419
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_make_loop() -> SimulationLoop` — No docstring provided.
- `test_agent_cards_and_perturbation_banner_render() -> None` — No docstring provided.
- `test_agent_cards_panel_renders_social_context() -> None` — No docstring provided.
- `test_perturbation_panel_states() -> None` — No docstring provided.
- `test_agent_cards_panel_renders_sparklines_from_history() -> None` — No docstring provided.
- `test_palette_overlay_renders_history_and_search() -> None` — No docstring provided.
- `test_palette_overlay_respects_mode_filter() -> None` — No docstring provided.
- `test_dispatch_palette_selection_dispatches_and_updates_status() -> None` — No docstring provided.
- `test_dispatch_palette_selection_handles_queue_full() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: rich.console
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet_ui.commands, townlet_ui.dashboard, townlet_ui.telemetry

### Code Quality Notes
- Missing module docstring.


## tests/test_demo_run_cli.py

- **File path**: `tests/test_demo_run_cli.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, os, pathlib, subprocess, sys] / third-party [pytest] / internal [None]
- **Related modules**: None
- **Lines of code**: 46
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_demo_run_cli_smoke(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- `PYTHON` = Path(sys.executable)
- `SCRIPT` = Path('scripts/demo_run.py')

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: None

### Code Quality Notes
- Missing module docstring.


## tests/test_demo_run_script.py

- **File path**: `tests/test_demo_run_script.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib, subprocess] / third-party [pytest] / internal [None]
- **Related modules**: None
- **Lines of code**: 19
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_demo_run_help() -> None` — No docstring provided.
- `test_demo_run_missing_config(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- `SCRIPT` = Path('scripts/demo_run.py')

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: None

### Code Quality Notes
- Missing module docstring.


## tests/test_demo_timeline.py

- **File path**: `tests/test_demo_timeline.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [pytest] / internal [townlet.config, townlet.core.sim_loop, townlet.demo.runner, townlet.demo.timeline]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.demo.runner, townlet.demo.timeline
- **Lines of code**: 71
- **Environment variables**: None detected

### Classes
- **StubExecutor(object)** — No docstring provided.
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `submit_payload(self, payload: dict[str, object], *, enqueue: bool = True) -> dict[str, object]` — No docstring provided.
    - `pending_count(self) -> int` — No docstring provided.

### Functions
- `test_load_timeline_from_yaml(tmp_path: Path) -> None` — No docstring provided.
- `test_demo_scheduler_actions_update_world(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.core.sim_loop, townlet.demo.runner, townlet.demo.timeline

### Code Quality Notes
- Missing module docstring.


## tests/test_embedding_allocator.py

- **File path**: `tests/test_embedding_allocator.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [None] / internal [townlet.config, townlet.observations.builder, townlet.observations.embedding, townlet.stability.monitor, townlet.telemetry.publisher, townlet.world.grid]
- **Related modules**: townlet.config, townlet.observations.builder, townlet.observations.embedding, townlet.stability.monitor, townlet.telemetry.publisher, townlet.world.grid
- **Lines of code**: 142
- **Environment variables**: None detected

### Classes
- None

### Functions
- `make_allocator(*, cooldown: int = 5, max_slots: int = 2) -> EmbeddingAllocator` — No docstring provided.
- `test_allocate_reuses_slot_after_cooldown() -> None` — No docstring provided.
- `test_allocator_respects_multiple_slots() -> None` — No docstring provided.
- `test_observation_builder_releases_on_termination() -> None` — No docstring provided.
- `test_telemetry_exposes_allocator_metrics() -> None` — No docstring provided.
- `test_stability_monitor_sets_alert_on_warning() -> None` — No docstring provided.
- `test_telemetry_records_events() -> None` — No docstring provided.
- `test_stability_alerts_on_affordance_failures() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.observations.builder, townlet.observations.embedding, townlet.stability.monitor, townlet.telemetry.publisher, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_employment_loop.py

- **File path**: `tests/test_employment_loop.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [pytest] / internal [townlet.config, townlet.core.sim_loop, townlet.world.grid]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid
- **Lines of code**: 120
- **Environment variables**: None detected

### Classes
- None

### Functions
- `make_loop_with_employment() -> SimulationLoop` — No docstring provided.
- `advance_ticks(loop: SimulationLoop, ticks: int) -> None` — No docstring provided.
- `test_on_time_shift_records_attendance() -> None` — No docstring provided.
- `test_late_arrival_accumulates_wages_withheld() -> None` — No docstring provided.
- `test_employment_exit_queue_respects_cap_and_manual_override() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_lifecycle_manager.py

- **File path**: `tests/test_lifecycle_manager.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [None] / internal [townlet.config, townlet.lifecycle.manager, townlet.world.grid]
- **Related modules**: townlet.config, townlet.lifecycle.manager, townlet.world.grid
- **Lines of code**: 89
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_make_world(respawn_delay: int = 0) -> tuple[LifecycleManager, WorldState]` — No docstring provided.
- `_spawn_agent(world: WorldState, agent_id: str = 'alice') -> AgentSnapshot` — No docstring provided.
- `test_respawn_after_delay() -> None` — No docstring provided.
- `test_employment_exit_emits_event_and_resets_state() -> None` — No docstring provided.
- `test_employment_daily_reset() -> None` — No docstring provided.
- `test_termination_reasons_captured() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.lifecycle.manager, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_need_decay.py

- **File path**: `tests/test_need_decay.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [pytest] / internal [townlet.config, townlet.lifecycle.manager, townlet.world.grid]
- **Related modules**: townlet.config, townlet.lifecycle.manager, townlet.world.grid
- **Lines of code**: 89
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_make_world() -> tuple[LifecycleManager, WorldState]` — No docstring provided.
- `_spawn_agent(world: WorldState, *, hunger: float = 0.8, hygiene: float = 0.7, energy: float = 0.6) -> AgentSnapshot` — No docstring provided.
- `test_need_decay_matches_config() -> None` — No docstring provided.
- `test_need_decay_clamps_at_zero() -> None` — No docstring provided.
- `test_lifecycle_hunger_threshold_applies() -> None` — No docstring provided.
- `test_agent_snapshot_clamps_on_init() -> None` — No docstring provided.

### Constants and Configuration
- `CONFIG_PATH` = Path('configs/examples/poc_hybrid.yaml')

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.lifecycle.manager, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_observation_builder.py

- **File path**: `tests/test_observation_builder.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [numpy] / internal [townlet.config, townlet.console.command, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid]
- **Related modules**: townlet.config, townlet.console.command, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid
- **Lines of code**: 206
- **Environment variables**: None detected

### Classes
- None

### Functions
- `make_world(enforce_job_loop: bool = False) -> SimulationLoop` — No docstring provided.
- `test_observation_builder_hybrid_map_and_features() -> None` — No docstring provided.
- `test_observation_ctx_reset_releases_slot() -> None` — No docstring provided.
- `test_observation_rivalry_features_reflect_conflict() -> None` — No docstring provided.
- `test_observation_queue_and_reservation_flags() -> None` — No docstring provided.
- `test_observation_respawn_resets_features() -> None` — No docstring provided.
- `test_ctx_reset_flag_on_teleport_and_possession() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy
- Internal: townlet.config, townlet.console.command, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_observation_builder_compact.py

- **File path**: `tests/test_observation_builder_compact.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [numpy] / internal [townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid
- **Lines of code**: 72
- **Environment variables**: None detected

### Classes
- None

### Functions
- `make_compact_world() -> SimulationLoop` — No docstring provided.
- `test_compact_observation_features_only() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy
- Internal: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_observation_builder_full.py

- **File path**: `tests/test_observation_builder_full.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [numpy] / internal [townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid
- **Lines of code**: 89
- **Environment variables**: None detected

### Classes
- None

### Functions
- `make_full_world() -> SimulationLoop` — No docstring provided.
- `test_full_observation_map_and_features() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy
- Internal: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_observations_social_snippet.py

- **File path**: `tests/test_observations_social_snippet.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [numpy, pytest] / internal [tests.helpers.social, townlet.config, townlet.observations.builder, townlet.world.grid]
- **Related modules**: tests.helpers.social, townlet.config, townlet.observations.builder, townlet.world.grid
- **Lines of code**: 110
- **Environment variables**: None detected

### Classes
- None

### Functions
- `base_config() -> SimulationConfig` — No docstring provided.
- `_build_world(config: SimulationConfig, *, with_social: bool = True) -> WorldState` — No docstring provided.
- `test_social_snippet_vector_length(base_config: SimulationConfig) -> None` — No docstring provided.
- `test_relationship_stage_required(base_config: SimulationConfig) -> None` — No docstring provided.
- `test_disable_aggregates_via_config(base_config: SimulationConfig) -> None` — No docstring provided.
- `test_observation_matches_golden_fixture(base_config: SimulationConfig) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy, pytest
- Internal: tests.helpers.social, townlet.config, townlet.observations.builder, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_observer_payload.py

- **File path**: `tests/test_observer_payload.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [None] / internal [townlet.config, townlet.core.sim_loop, townlet.telemetry.publisher, townlet.world.grid]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.telemetry.publisher, townlet.world.grid
- **Lines of code**: 53
- **Environment variables**: None detected

### Classes
- None

### Functions
- `make_loop() -> SimulationLoop` — No docstring provided.
- `test_observer_payload_contains_job_and_economy() -> None` — No docstring provided.
- `test_planning_payload_consistency() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.core.sim_loop, townlet.telemetry.publisher, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_observer_ui_cli.py

- **File path**: `tests/test_observer_ui_cli.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib, subprocess, sys] / third-party [pytest] / internal [None]
- **Related modules**: None
- **Lines of code**: 45
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_observer_ui_cli_smoke(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- `PYTHON` = Path(sys.executable)
- `SCRIPT` = Path('scripts/observer_ui.py')

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: None

### Code Quality Notes
- Missing module docstring.


## tests/test_observer_ui_dashboard.py

- **File path**: `tests/test_observer_ui_dashboard.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [dataclasses, pathlib] / third-party [pytest, rich.console] / internal [townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.policy.models, townlet.world.grid, townlet_ui.dashboard, townlet_ui.telemetry]
- **Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.policy.models, townlet.world.grid, townlet_ui.dashboard, townlet_ui.telemetry
- **Lines of code**: 379
- **Environment variables**: None detected

### Classes
- None

### Functions
- `make_loop() -> SimulationLoop` — No docstring provided.
- `test_render_snapshot_produces_panels() -> None` — No docstring provided.
- `test_render_snapshot_includes_palette_overlay_when_visible() -> None` — No docstring provided.
- `test_run_dashboard_advances_loop(monkeypatch: pytest.MonkeyPatch) -> None` — No docstring provided.
- `test_build_map_panel_produces_table() -> None` — No docstring provided.
- `test_narration_panel_shows_styled_categories() -> None` — No docstring provided.
- `test_policy_inspector_snapshot_contains_entries() -> None` — No docstring provided.
- `test_social_panel_renders_with_summary_and_events() -> None` — No docstring provided.
- `test_social_panel_handles_missing_summary() -> None` — No docstring provided.
- `test_promotion_reason_logic() -> None` — No docstring provided.
- `test_promotion_border_styles() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest, rich.console
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.policy.models, townlet.world.grid, townlet_ui.dashboard, townlet_ui.telemetry

### Code Quality Notes
- Missing module docstring.


## tests/test_observer_ui_executor.py

- **File path**: `tests/test_observer_ui_executor.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [time] / third-party [None] / internal [townlet.console.handlers, townlet_ui.commands]
- **Related modules**: townlet.console.handlers, townlet_ui.commands
- **Lines of code**: 33
- **Environment variables**: None detected

### Classes
- **DummyRouter(object)** — No docstring provided.
  - Methods:
    - `__init__(self) -> None` — No docstring provided.
    - `dispatch(self, command: ConsoleCommand) -> None` — No docstring provided.

### Functions
- `test_console_command_executor_dispatches_async() -> None` — No docstring provided.
- `test_console_command_executor_swallow_errors() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.console.handlers, townlet_ui.commands

### Code Quality Notes
- Missing module docstring.


## tests/test_observer_ui_script.py

- **File path**: `tests/test_observer_ui_script.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib, subprocess, sys] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 22
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_observer_ui_script_runs_single_tick(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing module docstring.


## tests/test_perturbation_config.py

- **File path**: `tests/test_perturbation_config.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [None] / internal [townlet.config]
- **Related modules**: townlet.config
- **Lines of code**: 38
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_simulation_config_exposes_perturbations() -> None` — No docstring provided.
- `test_price_spike_event_config_parses_ranges() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config

### Code Quality Notes
- Missing module docstring.


## tests/test_perturbation_scheduler.py

- **File path**: `tests/test_perturbation_scheduler.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [pytest] / internal [townlet.config, townlet.scheduler.perturbations, townlet.world.grid]
- **Related modules**: townlet.config, townlet.scheduler.perturbations, townlet.world.grid
- **Lines of code**: 179
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_base_config() -> SimulationConfig` — No docstring provided.
- `test_manual_event_activation_and_expiry() -> None` — No docstring provided.
- `test_auto_scheduling_respects_cooldowns() -> None` — No docstring provided.
- `test_cancel_event_removes_from_active() -> None` — No docstring provided.
- `test_blackout_toggles_power_status() -> None` — No docstring provided.
- `test_arranged_meet_relocates_agents() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.scheduler.perturbations, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_policy_anneal_blend.py

- **File path**: `tests/test_policy_anneal_blend.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [None] / internal [townlet.config, townlet.policy.behavior, townlet.policy.runner, townlet.world.grid]
- **Related modules**: townlet.config, townlet.policy.behavior, townlet.policy.runner, townlet.world.grid
- **Lines of code**: 176
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_make_world(option_commit_ticks: int | None = None) -> tuple[PolicyRuntime, WorldState]` — No docstring provided.
- `test_relationship_guardrail_blocks_rival_chat() -> None` — No docstring provided.
- `test_anneal_ratio_uses_provider_when_enabled() -> None` — No docstring provided.
- `test_anneal_ratio_mix_respects_probability() -> None` — No docstring provided.
- `test_blend_disabled_returns_scripted() -> None` — No docstring provided.
- `test_option_commit_blocks_switch_until_expiry() -> None` — No docstring provided.
- `test_option_commit_clears_on_termination() -> None` — No docstring provided.
- `test_option_commit_respects_disabled_setting() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.policy.behavior, townlet.policy.runner, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_policy_models.py

- **File path**: `tests/test_policy_models.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [None] / third-party [pytest, torch] / internal [townlet.policy.models]
- **Related modules**: townlet.policy.models
- **Lines of code**: 32
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_conflict_policy_network_requires_torch_when_unavailable() -> None` — No docstring provided.
- `test_conflict_policy_network_forward() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest, torch
- Internal: townlet.policy.models

### Code Quality Notes
- Missing module docstring.


## tests/test_policy_rivalry_behavior.py

- **File path**: `tests/test_policy_rivalry_behavior.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [pytest] / internal [townlet.agents.models, townlet.config.loader, townlet.policy.behavior, townlet.world.grid]
- **Related modules**: townlet.agents.models, townlet.config.loader, townlet.policy.behavior, townlet.world.grid
- **Lines of code**: 94
- **Environment variables**: None detected

### Classes
- None

### Functions
- `base_config()` — No docstring provided.
- `_build_world(base_config)` — No docstring provided.
- `test_scripted_behavior_chat_intent(base_config)` — No docstring provided.
- `_occupy(world: WorldState, object_id: str, agent_id: str) -> None` — No docstring provided.
- `test_agents_avoid_rivals_when_rivalry_high(base_config)` — No docstring provided.
- `test_agents_request_again_after_rivalry_decay(base_config)` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.agents.models, townlet.config.loader, townlet.policy.behavior, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_ppo_utils.py

- **File path**: `tests/test_ppo_utils.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__] / third-party [torch] / internal [townlet.policy.ppo]
- **Related modules**: townlet.policy.ppo
- **Lines of code**: 65
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_compute_gae_single_step() -> None` — No docstring provided.
- `test_value_baseline_from_old_preds_handles_bootstrap() -> None` — No docstring provided.
- `test_policy_surrogate_clipping_behaviour() -> None` — No docstring provided.
- `test_clipped_value_loss_respects_clip() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: torch
- Internal: townlet.policy.ppo

### Code Quality Notes
- Missing module docstring.


## tests/test_promotion_cli.py

- **File path**: `tests/test_promotion_cli.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [json, pathlib, subprocess, sys] / third-party [pytest] / internal [None]
- **Related modules**: None
- **Lines of code**: 52
- **Environment variables**: None detected

### Classes
- None

### Functions
- `write_summary(tmp_path: Path, accuracy: float, threshold: float = 0.9) -> Path` — No docstring provided.
- `test_promotion_cli_pass(tmp_path: Path) -> None` — No docstring provided.
- `test_promotion_cli_fail(tmp_path: Path) -> None` — No docstring provided.
- `test_promotion_drill(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- `PYTHON` = Path(sys.executable)
- `SCRIPT` = Path('scripts/promotion_evaluate.py')

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: None

### Code Quality Notes
- Missing module docstring.


## tests/test_promotion_evaluate_cli.py

- **File path**: `tests/test_promotion_evaluate_cli.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, json, pathlib, subprocess, sys] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 84
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_run(*args: str) -> subprocess.CompletedProcess[str]` — No docstring provided.
- `test_promotion_evaluate_promote(tmp_path: Path) -> None` — No docstring provided.
- `test_promotion_evaluate_hold_flags(tmp_path: Path) -> None` — No docstring provided.
- `test_promotion_evaluate_dry_run(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- `SCRIPT` = Path('scripts/promotion_evaluate.py').resolve()

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing module docstring.


## tests/test_promotion_manager.py

- **File path**: `tests/test_promotion_manager.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [json, pathlib] / third-party [None] / internal [townlet.config, townlet.stability.promotion]
- **Related modules**: townlet.config, townlet.stability.promotion
- **Lines of code**: 110
- **Environment variables**: None detected

### Classes
- None

### Functions
- `make_manager(log_path: Path | None = None) -> PromotionManager` — No docstring provided.
- `promotion_metrics(pass_streak: int, required: int, ready: bool, last_result: str | None = None, last_tick: int | None = None) -> dict[str, object]` — No docstring provided.
- `test_promotion_state_transitions() -> None` — No docstring provided.
- `test_promotion_manager_export_import() -> None` — No docstring provided.
- `test_mark_promoted_and_rollback() -> None` — No docstring provided.
- `test_rollback_without_metadata_reverts_to_initial() -> None` — No docstring provided.
- `test_promotion_log_written(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.stability.promotion

### Code Quality Notes
- Missing module docstring.


## tests/test_queue_fairness.py

- **File path**: `tests/test_queue_fairness.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [pytest] / internal [townlet.config, townlet.world.queue_manager]
- **Related modules**: townlet.config, townlet.world.queue_manager
- **Lines of code**: 89
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_make_queue_manager() -> QueueManager` — No docstring provided.
- `test_cooldown_blocks_repeat_entry_and_tracks_metric() -> None` — No docstring provided.
- `test_ghost_step_promotes_waiter_after_blockages(ghost_limit: int) -> None` — No docstring provided.
- `test_queue_snapshot_reflects_waiting_order() -> None` — No docstring provided.
- `test_queue_performance_metrics_accumulate_time() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.world.queue_manager

### Code Quality Notes
- Missing module docstring.


## tests/test_queue_manager.py

- **File path**: `tests/test_queue_manager.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [pytest] / internal [townlet.config, townlet.world.queue_manager]
- **Related modules**: townlet.config, townlet.world.queue_manager
- **Lines of code**: 92
- **Environment variables**: None detected

### Classes
- None

### Functions
- `queue_manager() -> QueueManager` — No docstring provided.
- `test_queue_cooldown_enforced(queue_manager: QueueManager) -> None` — No docstring provided.
- `test_queue_prioritises_wait_time(queue_manager: QueueManager) -> None` — No docstring provided.
- `test_ghost_step_trigger(queue_manager: QueueManager) -> None` — No docstring provided.
- `test_requeue_to_tail_rotates_agent(queue_manager: QueueManager) -> None` — No docstring provided.
- `test_record_blocked_attempt_counts_and_triggers(queue_manager: QueueManager) -> None` — No docstring provided.
- `test_cooldown_expiration_clears_entries(queue_manager: QueueManager) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.world.queue_manager

### Code Quality Notes
- Missing module docstring.


## tests/test_queue_metrics.py

- **File path**: `tests/test_queue_metrics.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [None] / internal [townlet.config, townlet.world.grid]
- **Related modules**: townlet.config, townlet.world.grid
- **Lines of code**: 63
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_make_world() -> WorldState` — No docstring provided.
- `test_queue_metrics_capture_ghost_step_and_rotation() -> None` — No docstring provided.
- `test_nightly_reset_preserves_queue_metrics() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_queue_resume.py

- **File path**: `tests/test_queue_resume.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib, random] / third-party [pytest] / internal [townlet.config, townlet.core.sim_loop, townlet.world.grid]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid
- **Lines of code**: 55
- **Environment variables**: None detected

### Classes
- None

### Functions
- `base_config()` — No docstring provided.
- `_setup_loop(config) -> SimulationLoop` — No docstring provided.
- `test_queue_metrics_resume(tmp_path: Path, base_config) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_relationship_integration.py

- **File path**: `tests/test_relationship_integration.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [pytest] / internal [townlet.agents.models, townlet.config, townlet.world.grid]
- **Related modules**: townlet.agents.models, townlet.config, townlet.world.grid
- **Lines of code**: 66
- **Environment variables**: None detected

### Classes
- None

### Functions
- `base_config() -> SimulationConfig` — No docstring provided.
- `_with_relationship_modifiers(config: SimulationConfig, enabled: bool) -> SimulationConfig` — No docstring provided.
- `_build_world(config: SimulationConfig) -> WorldState` — No docstring provided.
- `_familiarity(world: WorldState, owner: str, other: str) -> float` — No docstring provided.
- `test_chat_success_personality_bonus_applied(base_config: SimulationConfig) -> None` — No docstring provided.
- `test_chat_success_parity_when_disabled(base_config: SimulationConfig) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.agents.models, townlet.config, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_relationship_ledger.py

- **File path**: `tests/test_relationship_ledger.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__] / third-party [pytest] / internal [townlet.world.relationships]
- **Related modules**: townlet.world.relationships
- **Lines of code**: 98
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_apply_delta_clamps_and_prunes() -> None` — No docstring provided.
- `test_decay_removes_zero_ties() -> None` — No docstring provided.
- `test_eviction_hook_invoked_for_capacity() -> None` — No docstring provided.
- `test_eviction_hook_invoked_for_decay() -> None` — No docstring provided.
- `test_decay_reduces_values_before_eviction() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.world.relationships

### Code Quality Notes
- Missing module docstring.


## tests/test_relationship_metrics.py

- **File path**: `tests/test_relationship_metrics.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [pytest] / internal [townlet.config, townlet.telemetry.relationship_metrics, townlet.world.grid]
- **Related modules**: townlet.config, townlet.telemetry.relationship_metrics, townlet.world.grid
- **Lines of code**: 376
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_record_eviction_tracks_counts() -> None` — No docstring provided.
- `test_window_rolls_and_history_records_samples() -> None` — No docstring provided.
- `test_latest_payload_round_trips_via_ingest() -> None` — No docstring provided.
- `test_invalid_configuration_raises() -> None` — No docstring provided.
- `test_world_relationship_metrics_records_evictions() -> None` — No docstring provided.
- `test_world_relationship_update_symmetry() -> None` — No docstring provided.
- `test_queue_events_modify_relationships() -> None` — No docstring provided.
- `test_apply_actions_chat_updates_relationships() -> None` — No docstring provided.
- `test_friend_handover_priority() -> None` — No docstring provided.
- `test_shared_meal_updates_relationship() -> None` — No docstring provided.
- `test_absence_triggers_took_my_shift_relationships() -> None` — No docstring provided.
- `test_late_help_creates_positive_relationship() -> None` — No docstring provided.
- `test_chat_outcomes_adjust_relationships() -> None` — No docstring provided.
- `test_relationship_tie_helper_returns_current_values() -> None` — No docstring provided.
- `test_consume_chat_events_is_single_use() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.telemetry.relationship_metrics, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_relationship_personality_modifiers.py

- **File path**: `tests/test_relationship_personality_modifiers.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__] / third-party [pytest] / internal [townlet.agents]
- **Related modules**: townlet.agents
- **Lines of code**: 67
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_modifiers_disabled_returns_baseline() -> None` — No docstring provided.
- `test_forgiveness_scales_negative_values() -> None` — No docstring provided.
- `test_extroversion_adds_chat_bonus() -> None` — No docstring provided.
- `test_ambition_scales_conflict_rivalry() -> None` — No docstring provided.
- `test_unforgiving_agent_intensifies_negative_hits() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.agents

### Code Quality Notes
- Missing module docstring.


## tests/test_reward_engine.py

- **File path**: `tests/test_reward_engine.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [pytest] / internal [townlet.config, townlet.rewards.engine, townlet.world.grid]
- **Related modules**: townlet.config, townlet.rewards.engine, townlet.world.grid
- **Lines of code**: 331
- **Environment variables**: None detected

### Classes
- **StubSnapshot(object)** — No docstring provided.
  - Methods:
    - `__init__(self, needs: dict[str, float], wallet: float) -> None` — No docstring provided.
- **StubWorld(object)** — No docstring provided.
  - Methods:
    - `__init__(self, config, snapshot: StubSnapshot, context: dict[str, float]) -> None` — No docstring provided.
    - `consume_chat_events(self)` — No docstring provided.
    - `agent_context(self, agent_id: str) -> dict[str, float]` — No docstring provided.
    - `relationship_tie(self, subject: str, target: str)` — No docstring provided.
    - `rivalry_top(self, agent_id: str, limit: int)` — No docstring provided.

### Functions
- `_make_world(hunger: float = 0.5) -> WorldState` — No docstring provided.
- `test_reward_negative_with_high_deficit() -> None` — No docstring provided.
- `test_reward_clipped_by_config() -> None` — No docstring provided.
- `test_survival_tick_positive_when_balanced() -> None` — No docstring provided.
- `test_chat_reward_applied_for_successful_conversation() -> None` — No docstring provided.
- `test_chat_reward_skipped_when_needs_override_triggers() -> None` — No docstring provided.
- `test_chat_events_ignored_when_social_stage_disabled() -> None` — No docstring provided.
- `test_chat_reward_blocked_within_termination_window() -> None` — No docstring provided.
- `test_chat_failure_penalty() -> None` — No docstring provided.
- `test_rivalry_avoidance_reward() -> None` — No docstring provided.
- `test_episode_clip_enforced() -> None` — No docstring provided.
- `test_wage_and_punctuality_bonus() -> None` — No docstring provided.
- `test_terminal_penalty_applied_for_faint() -> None` — No docstring provided.
- `test_terminal_penalty_applied_for_eviction() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.rewards.engine, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_reward_summary.py

- **File path**: `tests/test_reward_summary.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [json, pathlib] / third-party [None] / internal [scripts.reward_summary]
- **Related modules**: scripts.reward_summary
- **Lines of code**: 49
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_component_stats_mean_and_extremes() -> None` — No docstring provided.
- `test_reward_aggregator_tracks_components(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: scripts.reward_summary

### Code Quality Notes
- Missing module docstring.


## tests/test_rivalry_ledger.py

- **File path**: `tests/test_rivalry_ledger.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [None] / third-party [pytest] / internal [townlet.world.rivalry]
- **Related modules**: townlet.world.rivalry
- **Lines of code**: 38
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_increment_and_clamp_and_eviction() -> None` — No docstring provided.
- `test_decay_and_eviction_threshold() -> None` — No docstring provided.
- `test_should_avoid_toggle() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.world.rivalry

### Code Quality Notes
- Missing module docstring.


## tests/test_rivalry_state.py

- **File path**: `tests/test_rivalry_state.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__] / third-party [None] / internal [townlet.world.rivalry]
- **Related modules**: townlet.world.rivalry
- **Lines of code**: 43
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_apply_conflict_clamps_to_max() -> None` — No docstring provided.
- `test_decay_evicts_low_scores() -> None` — No docstring provided.
- `test_should_avoid_threshold() -> None` — No docstring provided.
- `test_encode_features_fixed_width() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.world.rivalry

### Code Quality Notes
- Missing module docstring.


## tests/test_rollout_buffer.py

- **File path**: `tests/test_rollout_buffer.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, json, pathlib] / third-party [numpy, pytest] / internal [townlet.config, townlet.policy.rollout, townlet.policy.runner]
- **Related modules**: townlet.config, townlet.policy.rollout, townlet.policy.runner
- **Lines of code**: 85
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_dummy_frame(agent_id: str, reward: float = 0.0, done: bool = False) -> dict[str, object]` — No docstring provided.
- `test_rollout_buffer_grouping_to_samples() -> None` — No docstring provided.
- `test_training_harness_capture_rollout(tmp_path: Path) -> None` — No docstring provided.
- `test_rollout_buffer_empty_build_dataset_raises() -> None` — No docstring provided.
- `test_rollout_buffer_single_timestep_metrics() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy, pytest
- Internal: townlet.config, townlet.policy.rollout, townlet.policy.runner

### Code Quality Notes
- Missing module docstring.


## tests/test_rollout_capture.py

- **File path**: `tests/test_rollout_capture.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, json, pathlib, subprocess, sys] / third-party [numpy, pytest] / internal [townlet.config]
- **Related modules**: townlet.config
- **Lines of code**: 109
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_capture_rollout_scenarios(tmp_path: Path, config_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- `SCENARIO_CONFIGS` = [Path('configs/scenarios/kitchen_breakfast.yaml'), Path('configs/scenarios/queue_conflict.yaml'), Path('configs/scenarios/employment_punctuality.yaml'), Path('configs/scenarios/rivalry_decay.yaml'), Path('configs/scenarios/observation_baseline.yaml')]
- `GOLDEN_STATS_PATH` = Path('docs/samples/rollout_scenario_stats.json')
- `GOLDEN_STATS` = json.loads(GOLDEN_STATS_PATH.read_text()) if GOLDEN_STATS_PATH.exists() else {}

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy, pytest
- Internal: townlet.config

### Code Quality Notes
- Missing module docstring.


## tests/test_run_anneal_rehearsal.py

- **File path**: `tests/test_run_anneal_rehearsal.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [importlib.util, pathlib, sys] / third-party [pytest] / internal [townlet.policy.models]
- **Related modules**: townlet.policy.models
- **Lines of code**: 33
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_run_anneal_rehearsal_pass(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.policy.models

### Code Quality Notes
- Missing module docstring.


## tests/test_run_simulation_cli.py

- **File path**: `tests/test_run_simulation_cli.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib, sys] / third-party [None] / internal [scripts, townlet.config, townlet.core.sim_loop]
- **Related modules**: scripts, townlet.config, townlet.core.sim_loop
- **Lines of code**: 46
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_run_simulation_cli_iterates_ticks(monkeypatch)` — No docstring provided.
- `test_simulation_loop_run_for_advances_ticks()` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: scripts, townlet.config, townlet.core.sim_loop

### Code Quality Notes
- Missing module docstring.


## tests/test_scripted_behavior.py

- **File path**: `tests/test_scripted_behavior.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [numpy] / internal [townlet.config, townlet.core.sim_loop, townlet.policy.behavior, townlet.world.grid]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.policy.behavior, townlet.world.grid
- **Lines of code**: 85
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_scripted_behavior_determinism() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy
- Internal: townlet.config, townlet.core.sim_loop, townlet.policy.behavior, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_sim_loop_snapshot.py

- **File path**: `tests/test_sim_loop_snapshot.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, json, pathlib, random] / third-party [pytest] / internal [townlet.config, townlet.core.sim_loop, townlet.snapshots.state, townlet.world.grid]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.snapshots.state, townlet.world.grid
- **Lines of code**: 218
- **Environment variables**: None detected

### Classes
- None

### Functions
- `base_config()` — No docstring provided.
- `test_simulation_loop_snapshot_round_trip(tmp_path: Path, base_config) -> None` — No docstring provided.
- `test_save_snapshot_uses_config_root_and_identity_override(tmp_path: Path, base_config) -> None` — No docstring provided.
- `test_simulation_resume_equivalence(tmp_path: Path, base_config) -> None` — No docstring provided.
- `test_policy_transitions_resume(tmp_path: Path, base_config) -> None` — No docstring provided.
- `_normalise_snapshot(snapshot: dict[str, object]) -> dict[str, object]` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.core.sim_loop, townlet.snapshots.state, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_sim_loop_structure.py

- **File path**: `tests/test_sim_loop_structure.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [None] / internal [townlet.config, townlet.core.sim_loop]
- **Related modules**: townlet.config, townlet.core.sim_loop
- **Lines of code**: 14
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_simulation_loop_runs_one_tick(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.core.sim_loop

### Code Quality Notes
- Missing module docstring.


## tests/test_snapshot_manager.py

- **File path**: `tests/test_snapshot_manager.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, json, pathlib, random] / third-party [pytest] / internal [townlet.config, townlet.scheduler.perturbations, townlet.snapshots.state, townlet.telemetry.publisher, townlet.utils, townlet.world.grid]
- **Related modules**: townlet.config, townlet.scheduler.perturbations, townlet.snapshots.state, townlet.telemetry.publisher, townlet.utils, townlet.world.grid
- **Lines of code**: 353
- **Environment variables**: None detected

### Classes
- None

### Functions
- `sample_config() -> SimulationConfig` — No docstring provided.
- `test_snapshot_round_trip(tmp_path: Path, sample_config) -> None` — No docstring provided.
- `test_snapshot_config_mismatch_raises(tmp_path: Path, sample_config) -> None` — No docstring provided.
- `test_snapshot_missing_relationships_field_rejected(tmp_path: Path, sample_config) -> None` — No docstring provided.
- `test_snapshot_schema_version_mismatch(tmp_path: Path, sample_config) -> None` — No docstring provided.
- `_config_with_snapshot_updates(config: SimulationConfig, updates: dict[str, object]) -> SimulationConfig` — No docstring provided.
- `test_snapshot_mismatch_allowed_when_guardrail_disabled(tmp_path: Path, sample_config: SimulationConfig) -> None` — No docstring provided.
- `test_snapshot_schema_downgrade_honours_allow_flag(tmp_path: Path, sample_config: SimulationConfig) -> None` — No docstring provided.
- `test_world_relationship_snapshot_round_trip(tmp_path: Path, sample_config: SimulationConfig) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.scheduler.perturbations, townlet.snapshots.state, townlet.telemetry.publisher, townlet.utils, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_snapshot_migrations.py

- **File path**: `tests/test_snapshot_migrations.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, dataclasses, pathlib] / third-party [pytest] / internal [townlet.config, townlet.snapshots, townlet.snapshots.migrations]
- **Related modules**: townlet.config, townlet.snapshots, townlet.snapshots.migrations
- **Lines of code**: 82
- **Environment variables**: None detected

### Classes
- None

### Functions
- `sample_config() -> SimulationConfig` — No docstring provided.
- `reset_registry() -> None` — No docstring provided.
- `_basic_state(config: SimulationConfig) -> SnapshotState` — No docstring provided.
- `test_snapshot_migration_applied(tmp_path: Path, sample_config: SimulationConfig) -> None` — No docstring provided.
- `test_snapshot_migration_multi_step(tmp_path: Path, sample_config: SimulationConfig) -> None` — No docstring provided.
- `test_snapshot_migration_missing_path_raises(tmp_path: Path, sample_config: SimulationConfig) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.snapshots, townlet.snapshots.migrations

### Code Quality Notes
- Missing module docstring.


## tests/test_stability_monitor.py

- **File path**: `tests/test_stability_monitor.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [None] / internal [townlet.config, townlet.stability.monitor]
- **Related modules**: townlet.config, townlet.stability.monitor
- **Lines of code**: 212
- **Environment variables**: None detected

### Classes
- None

### Functions
- `make_monitor() -> StabilityMonitor` — No docstring provided.
- `_track_minimal(monitor: StabilityMonitor, *, tick: int, embedding_warning: bool = False, queue_alert: bool = False) -> None` — No docstring provided.
- `test_starvation_spike_alert_triggers_after_streak() -> None` — No docstring provided.
- `test_option_thrash_alert_averages_over_window() -> None` — No docstring provided.
- `test_reward_variance_alert_exports_state() -> None` — No docstring provided.
- `test_queue_fairness_alerts_include_metrics() -> None` — No docstring provided.
- `test_rivalry_spike_alert_triggers_on_intensity() -> None` — No docstring provided.
- `test_promotion_window_tracking() -> None` — No docstring provided.
- `test_promotion_window_respects_allowed_alerts() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.stability.monitor

### Code Quality Notes
- Missing module docstring.


## tests/test_stability_telemetry.py

- **File path**: `tests/test_stability_telemetry.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [pytest] / internal [townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid]
- **Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid
- **Lines of code**: 47
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_stability_alerts_exposed_via_telemetry_snapshot(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_telemetry_client.py

- **File path**: `tests/test_telemetry_client.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [collections.abc, pathlib] / third-party [pytest] / internal [townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet_ui.telemetry]
- **Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet_ui.telemetry
- **Lines of code**: 85
- **Environment variables**: None detected

### Classes
- None

### Functions
- `make_simulation(enforce_job_loop: bool = True) -> SimulationLoop` — No docstring provided.
- `test_telemetry_client_parses_console_snapshot() -> None` — No docstring provided.
- `test_telemetry_client_warns_on_newer_schema(monkeypatch: pytest.MonkeyPatch) -> None` — No docstring provided.
- `test_telemetry_client_raises_on_major_mismatch() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet_ui.telemetry

### Code Quality Notes
- Missing module docstring.


## tests/test_telemetry_jobs.py

- **File path**: `tests/test_telemetry_jobs.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [pytest] / internal [townlet.config, townlet.core.sim_loop, townlet.stability.monitor, townlet.world.grid]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.stability.monitor, townlet.world.grid
- **Lines of code**: 55
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_telemetry_captures_job_snapshot() -> None` — No docstring provided.
- `test_stability_monitor_lateness_alert() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.core.sim_loop, townlet.stability.monitor, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_telemetry_narration.py

- **File path**: `tests/test_telemetry_narration.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [None] / internal [townlet.config, townlet.telemetry.narration, townlet.telemetry.publisher, townlet.world.grid]
- **Related modules**: townlet.config, townlet.telemetry.narration, townlet.telemetry.publisher, townlet.world.grid
- **Lines of code**: 243
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_narration_rate_limiter_enforces_cooldowns() -> None` — No docstring provided.
- `test_narration_rate_limiter_priority_bypass() -> None` — No docstring provided.
- `test_telemetry_publisher_emits_queue_conflict_narration(tmp_path: Path) -> None` — No docstring provided.
- `test_relationship_friendship_narration_emits_for_new_tie() -> None` — No docstring provided.
- `test_relationship_friendship_respects_configured_threshold() -> None` — No docstring provided.
- `test_relationship_rivalry_narration_tracks_threshold() -> None` — No docstring provided.
- `test_relationship_rivalry_respects_configured_thresholds() -> None` — No docstring provided.
- `test_social_alert_narrations_for_chat_and_avoidance() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.telemetry.narration, townlet.telemetry.publisher, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_telemetry_new_events.py

- **File path**: `tests/test_telemetry_new_events.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [None] / internal [townlet.config, townlet.core.sim_loop, townlet.world.grid]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid
- **Lines of code**: 352
- **Environment variables**: None detected

### Classes
- None

### Functions
- `make_loop() -> SimulationLoop` — No docstring provided.
- `test_shower_events_in_telemetry() -> None` — No docstring provided.
- `test_shower_complete_narration() -> None` — No docstring provided.
- `test_sleep_events_in_telemetry() -> None` — No docstring provided.
- `test_relationship_summary_and_social_events() -> None` — No docstring provided.
- `test_affordance_runtime_running_snapshot() -> None` — No docstring provided.
- `test_rivalry_events_surface_in_telemetry() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_telemetry_stream_smoke.py

- **File path**: `tests/test_telemetry_stream_smoke.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, json, pathlib] / third-party [None] / internal [townlet.config, townlet.core.sim_loop, townlet.world.grid, townlet_ui.telemetry]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid, townlet_ui.telemetry
- **Lines of code**: 51
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_ensure_agents(loop: SimulationLoop) -> None` — No docstring provided.
- `test_file_transport_stream_smoke(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.grid, townlet_ui.telemetry

### Code Quality Notes
- Missing module docstring.


## tests/test_telemetry_summary.py

- **File path**: `tests/test_telemetry_summary.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, importlib.util, pathlib, sys] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 69
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_summary_includes_new_events(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- Missing module docstring.


## tests/test_telemetry_transport.py

- **File path**: `tests/test_telemetry_transport.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, json, pathlib, time] / third-party [pytest] / internal [townlet.config, townlet.core.sim_loop, townlet.telemetry.transport, townlet.world.grid]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.telemetry.transport, townlet.world.grid
- **Lines of code**: 289
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_ensure_agents(loop: SimulationLoop) -> None` — No docstring provided.
- `test_transport_buffer_drop_until_capacity() -> None` — No docstring provided.
- `test_telemetry_publisher_flushes_payload(monkeypatch: pytest.MonkeyPatch) -> None` — No docstring provided.
- `test_telemetry_publisher_retries_on_failure(monkeypatch: pytest.MonkeyPatch) -> None` — No docstring provided.
- `test_telemetry_worker_metrics_and_stop(monkeypatch: pytest.MonkeyPatch) -> None` — No docstring provided.
- `test_tcp_transport_wraps_socket_with_tls(monkeypatch: pytest.MonkeyPatch) -> None` — No docstring provided.
- `test_create_transport_plaintext_warning(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None` — No docstring provided.
- `test_create_transport_plaintext_disallowed() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.core.sim_loop, townlet.telemetry.transport, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_telemetry_validator.py

- **File path**: `tests/test_telemetry_validator.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, json, pathlib] / third-party [pytest] / internal [scripts.validate_ppo_telemetry]
- **Related modules**: scripts.validate_ppo_telemetry
- **Lines of code**: 119
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_write_ndjson(path: Path, record: dict[str, float]) -> None` — No docstring provided.
- `test_validate_ppo_telemetry_accepts_valid_log(tmp_path: Path) -> None` — No docstring provided.
- `test_validate_ppo_telemetry_raises_for_missing_conflict(tmp_path: Path) -> None` — No docstring provided.
- `test_validate_ppo_telemetry_accepts_version_1_1(tmp_path: Path) -> None` — No docstring provided.
- `test_validate_ppo_telemetry_v1_1_missing_field_raises(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- `VALID_RECORD` = {'epoch': 1.0, 'updates': 2.0, 'transitions': 4.0, 'loss_policy': 0.1, 'loss_value': 0.2, 'loss_entropy': 0.3, 'loss_total': 0.4, 'clip_fraction': 0.1, 'adv_mean': 0.0, 'adv_std': 0.1, 'adv_zero_std_batches': 0.0, 'adv_min_std': 0.1, 'clip_triggered_minibatches': 0.0, 'clip_fraction_max': 0.1, 'grad_norm': 1.5, 'kl_divergence': 0.01, 'telemetry_version': 1.0, 'lr': 0.0003, 'steps': 4.0, 'baseline_sample_count': 2.0, 'baseline_reward_mean': 0.25, 'baseline_reward_sum': 1.0, 'baseline_reward_sum_mean': 0.5, 'baseline_log_prob_mean': -0.2, 'conflict.rivalry_max_mean_avg': 0.05, 'conflict.rivalry_max_max_avg': 0.1, 'conflict.rivalry_avoid_count_mean_avg': 0.0, 'conflict.rivalry_avoid_count_max_avg': 0.0}

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: scripts.validate_ppo_telemetry

### Code Quality Notes
- Missing module docstring.


## tests/test_telemetry_watch.py

- **File path**: `tests/test_telemetry_watch.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [pytest] / internal [scripts.telemetry_watch]
- **Related modules**: scripts.telemetry_watch
- **Lines of code**: 64
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_parse_health_line() -> None` — No docstring provided.
- `test_stream_health_records(tmp_path: Path) -> None` — No docstring provided.
- `test_health_thresholds_raise() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: scripts.telemetry_watch

### Code Quality Notes
- Missing module docstring.


## tests/test_training_anneal.py

- **File path**: `tests/test_training_anneal.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, json, pathlib] / third-party [numpy, pytest] / internal [townlet.config, townlet.policy.models, townlet.policy.replay, townlet.policy.runner]
- **Related modules**: townlet.config, townlet.policy.models, townlet.policy.replay, townlet.policy.runner
- **Lines of code**: 108
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_write_sample(output_dir: Path, stem: str, timesteps: int, action_dim: int = 2) -> tuple[Path, Path]` — No docstring provided.
- `test_run_anneal_bc_then_ppo(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy, pytest
- Internal: townlet.config, townlet.policy.models, townlet.policy.replay, townlet.policy.runner

### Code Quality Notes
- Missing module docstring.


## tests/test_training_cli.py

- **File path**: `tests/test_training_cli.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, argparse, pathlib] / third-party [None] / internal [scripts, townlet.config]
- **Related modules**: scripts, townlet.config
- **Lines of code**: 81
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_make_namespace(**kwargs: object) -> Namespace` — No docstring provided.
- `test_collect_ppo_overrides_handles_values() -> None` — No docstring provided.
- `test_apply_ppo_overrides_creates_config_when_missing() -> None` — No docstring provided.
- `test_apply_ppo_overrides_updates_existing_model() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: scripts, townlet.config

### Code Quality Notes
- Missing module docstring.


## tests/test_training_replay.py

- **File path**: `tests/test_training_replay.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, json, math, pathlib, subprocess, sys] / third-party [numpy, pytest, torch] / internal [townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.policy.models, townlet.policy.replay, townlet.policy.replay_buffer, townlet.policy.runner, townlet.world.grid]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.policy.models, townlet.policy.replay, townlet.policy.replay_buffer, townlet.policy.runner, townlet.world.grid
- **Lines of code**: 955
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_validate_numeric(value: object) -> None` — No docstring provided.
- `_assert_ppo_log_schema(summary: dict[str, object], require_baseline: bool) -> None` — No docstring provided.
- `_load_expected_stats(config_path: Path) -> dict[str, dict[str, float]]` — No docstring provided.
- `_aggregate_expected_metrics(sample_stats: dict[str, dict[str, float]]) -> dict[str, float]` — No docstring provided.
- `_make_sample(base_dir: Path, rivalry_increment: float, avoid_threshold: float, suffix: str) -> tuple[Path, Path]` — No docstring provided.
- `_make_social_sample() -> ReplaySample` — No docstring provided.
- `test_training_harness_replay_stats(tmp_path: Path) -> None` — No docstring provided.
- `test_replay_dataset_batch_iteration(tmp_path: Path) -> None` — No docstring provided.
- `test_replay_loader_schema_guard(tmp_path: Path) -> None` — No docstring provided.
- `test_replay_dataset_streaming(tmp_path: Path) -> None` — No docstring provided.
- `test_replay_loader_missing_training_arrays(tmp_path: Path) -> None` — No docstring provided.
- `test_replay_loader_value_length_mismatch(tmp_path: Path) -> None` — No docstring provided.
- `test_training_harness_run_ppo_on_capture(tmp_path: Path, config_path: Path) -> None` — No docstring provided.
- `test_training_harness_run_ppo(tmp_path: Path) -> None` — No docstring provided.
- `test_run_ppo_rejects_nan_advantages(tmp_path: Path) -> None` — No docstring provided.
- `test_training_harness_log_sampling_and_rotation(tmp_path: Path) -> None` — No docstring provided.
- `test_training_harness_run_rollout_ppo(tmp_path: Path) -> None` — No docstring provided.
- `test_training_harness_ppo_conflict_telemetry(tmp_path: Path) -> None` — No docstring provided.
- `test_training_harness_run_rollout_ppo_multiple_cycles(tmp_path: Path) -> None` — No docstring provided.
- `test_training_harness_rollout_capture_and_train_cycles(tmp_path: Path) -> None` — No docstring provided.
- `test_training_harness_streaming_log_offsets(tmp_path: Path) -> None` — No docstring provided.
- `test_training_harness_rollout_queue_conflict_metrics(tmp_path: Path) -> None` — No docstring provided.
- `test_ppo_social_chat_drift(tmp_path: Path) -> None` — No docstring provided.
- `test_policy_runtime_collects_frames(tmp_path: Path) -> None` — No docstring provided.

### Constants and Configuration
- `SCENARIO_CONFIGS` = [Path('configs/scenarios/kitchen_breakfast.yaml'), Path('configs/scenarios/queue_conflict.yaml'), Path('configs/scenarios/employment_punctuality.yaml'), Path('configs/scenarios/rivalry_decay.yaml'), Path('configs/scenarios/observation_baseline.yaml')]
- `GOLDEN_STATS_PATH` = Path('docs/samples/rollout_scenario_stats.json')
- `GOLDEN_STATS` = json.loads(GOLDEN_STATS_PATH.read_text()) if GOLDEN_STATS_PATH.exists() else {}
- `REQUIRED_PPO_KEYS` = {'epoch', 'updates', 'transitions', 'loss_policy', 'loss_value', 'loss_entropy', 'loss_total', 'clip_fraction', 'adv_mean', 'adv_std', 'adv_zero_std_batches', 'adv_min_std', 'clip_triggered_minibatches', 'clip_fraction_max', 'grad_norm', 'kl_divergence', 'telemetry_version', 'lr', 'steps', 'epoch_duration_sec', 'data_mode', 'cycle_id', 'batch_entropy_mean', 'batch_entropy_std', 'grad_norm_max', 'kl_divergence_max', 'reward_advantage_corr', 'rollout_ticks', 'log_stream_offset', 'queue_conflict_events', 'queue_conflict_intensity_sum', 'shared_meal_events', 'late_help_events', 'shift_takeover_events', 'chat_success_events', 'chat_failure_events', 'chat_quality_mean'}
- `REQUIRED_PPO_NUMERIC_KEYS` = REQUIRED_PPO_KEYS - {'data_mode'}
- `BASELINE_KEYS_REQUIRED` = {'baseline_sample_count', 'baseline_reward_sum', 'baseline_reward_sum_mean', 'baseline_reward_mean'}
- `BASELINE_KEYS_OPTIONAL` = {'baseline_log_prob_mean'}
- `ALLOWED_KEY_PREFIXES` = ('conflict.',)

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: numpy, pytest, torch
- Internal: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.policy.models, townlet.policy.replay, townlet.policy.replay_buffer, townlet.policy.runner, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_ui_telemetry.py

- **File path**: `tests/test_ui_telemetry.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [None] / third-party [None] / internal [townlet_ui.telemetry]
- **Related modules**: townlet_ui.telemetry
- **Lines of code**: 112
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_telemetry_client_parses_agent_needs_and_perturbations() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet_ui.telemetry

### Code Quality Notes
- Missing module docstring.


## tests/test_utils_rng.py

- **File path**: `tests/test_utils_rng.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, random] / third-party [pytest] / internal [townlet.utils]
- **Related modules**: townlet.utils
- **Lines of code**: 22
- **Environment variables**: None detected

### Classes
- None

### Functions
- `test_encode_decode_rng_state_round_trip() -> None` — No docstring provided.
- `test_decode_rng_state_invalid_payload() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.utils

### Code Quality Notes
- Missing module docstring.


## tests/test_world_local_view.py

- **File path**: `tests/test_world_local_view.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [None] / internal [townlet.config, townlet.core.sim_loop, townlet.world.grid]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid
- **Lines of code**: 90
- **Environment variables**: None detected

### Classes
- None

### Functions
- `make_loop() -> SimulationLoop` — No docstring provided.
- `tile_for_position(tiles, position)` — No docstring provided.
- `test_local_view_includes_objects_and_agents() -> None` — No docstring provided.
- `test_agent_context_defaults() -> None` — No docstring provided.
- `test_world_snapshot_returns_defensive_copies() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_world_nightly_reset.py

- **File path**: `tests/test_world_nightly_reset.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, pathlib] / third-party [None] / internal [townlet.config, townlet.core.sim_loop, townlet.world.grid]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid
- **Lines of code**: 74
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_setup_world() -> WorldState` — No docstring provided.
- `test_apply_nightly_reset_returns_agents_home() -> None` — No docstring provided.
- `test_simulation_loop_triggers_nightly_reset() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_world_queue_integration.py

- **File path**: `tests/test_world_queue_integration.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [pytest] / internal [townlet.config, townlet.core.sim_loop, townlet.world.grid]
- **Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid
- **Lines of code**: 280
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_make_world() -> WorldState` — No docstring provided.
- `test_queue_assignment_flow() -> None` — No docstring provided.
- `test_queue_ghost_step_promotes_waiter() -> None` — No docstring provided.
- `test_affordance_completion_applies_effects() -> None` — No docstring provided.
- `test_eat_meal_adjusts_needs_and_wallet() -> None` — No docstring provided.
- `test_affordance_failure_skips_effects() -> None` — No docstring provided.
- `test_affordances_loaded_from_yaml() -> None` — No docstring provided.
- `test_affordance_events_emitted() -> None` — No docstring provided.
- `test_need_decay_applied_each_tick() -> None` — No docstring provided.
- `test_eat_meal_deducts_wallet_and_stock() -> None` — No docstring provided.
- `test_wage_income_applied_on_shift() -> None` — No docstring provided.
- `test_stove_restock_event_emitted() -> None` — No docstring provided.
- `test_scripted_behavior_handles_sleep() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tests/test_world_rivalry.py

- **File path**: `tests/test_world_rivalry.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [pathlib] / third-party [pytest] / internal [townlet.config, townlet.world.grid]
- **Related modules**: townlet.config, townlet.world.grid
- **Lines of code**: 94
- **Environment variables**: None detected

### Classes
- None

### Functions
- `_make_world() -> WorldState` — No docstring provided.
- `test_register_rivalry_conflict_updates_snapshot() -> None` — No docstring provided.
- `test_rivalry_events_record_reason() -> None` — No docstring provided.
- `test_rivalry_decays_over_time() -> None` — No docstring provided.
- `test_queue_conflict_event_emitted_with_intensity() -> None` — No docstring provided.

### Constants and Configuration
- None detected

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: pytest
- Internal: townlet.config, townlet.world.grid

### Code Quality Notes
- Missing module docstring.


## tmp/analyze_modules.py

- **File path**: `tmp/analyze_modules.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, ast, collections, dataclasses, json, os, pathlib, typing] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 535
- **Environment variables**: None detected

### Classes
- **FunctionInfo(object)** — No docstring provided.
  - Attributes:
    - `name` (type=str)
    - `signature` (type=str)
    - `lineno` (type=int)
    - `docstring` (type=str | None)
    - `params` (type=list[dict[str, Any]])
    - `return_type` (type=str | None)
    - `is_async` (type=bool, default=False)
  - Methods: None
- **ClassInfo(object)** — No docstring provided.
  - Attributes:
    - `name` (type=str)
    - `bases` (type=list[str], default=field(default_factory=list))
    - `decorators` (type=list[str], default=field(default_factory=list))
    - `lineno` (type=int, default=0)
    - `docstring` (type=str | None, default=None)
    - `methods` (type=list[FunctionInfo], default=field(default_factory=list))
    - `attributes` (type=list[dict[str, Any]], default=field(default_factory=list))
  - Methods: None
- **ModuleInfo(object)** — No docstring provided.
  - Attributes:
    - `path` (type=Path)
    - `module` (type=str)
    - `module_name` (type=str)
    - `docstring` (type=str | None)
    - `imports` (type=dict[str, set[str]])
    - `classes` (type=list[ClassInfo])
    - `functions` (type=list[FunctionInfo])
    - `constants` (type=list[dict[str, Any]])
    - `env_vars` (type=list[str])
    - `todos` (type=list[int])
    - `has_logging` (type=bool)
    - `has_type_hints` (type=bool)
    - `has_dataclasses` (type=bool)
    - `lines` (type=int)
  - Methods: None

### Functions
- `unparse(node: ast.AST | None) -> str | None` — No docstring provided.
- `_format_param_entry(name: str, annotation: str | None, default: str | None) -> str` — No docstring provided.
- `build_signature(arguments: ast.arguments) -> tuple[str, list[dict[str, Any]]]` — No docstring provided.
- `format_return(annotation: ast.expr | None) -> str` — No docstring provided.
- `module_name_from_path(path: Path) -> str` — No docstring provided.
- `classify_import(module: str) -> str` — No docstring provided.
- `collect_imports(tree: ast.AST, package_parts: list[str]) -> dict[str, set[str]]` — No docstring provided.
- `gather_class_attributes(body: list[ast.stmt]) -> list[dict[str, Any]]` — No docstring provided.
- `gather_constants(body: list[ast.stmt]) -> list[dict[str, Any]]` — No docstring provided.
- `detect_env_usage(tree: ast.AST) -> list[str]` — No docstring provided.
- `gather_functions(body: Iterable[ast.stmt]) -> list[FunctionInfo]` — No docstring provided.
- `analyze_module(path: Path) -> ModuleInfo` — No docstring provided.
- `find_python_files(root: Path) -> list[Path]` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- `PROJECT_ROOT` = Path(__file__).resolve().parents[1]
- `PACKAGE_PREFIXES` = {'townlet', 'townlet_ui', 'scripts'}
- `STD_LIB_MODULES` = {'__future__', 'abc', 'argparse', 'asyncio', 'base64', 'bisect', 'collections', 'collections.abc', 'contextlib', 'copy', 'dataclasses', 'datetime', 'decimal', 'enum', 'functools', 'hashlib', 'heapq', 'itertools', 'json', 'logging', 'math', 'os', 'pathlib', 'random', 'statistics', 'textwrap', 'time', 'typing', 'typing_extensions', 'uuid', 'weakref'}
- `NON_STANDARD_PREFIXES` = ('townlet', 'townlet_ui', 'scripts')

  TODO markers:
  - if "TODO" in line:

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- TODO markers present; implementation incomplete.
- Missing module docstring.


## tmp/render_module_docs.py

- **File path**: `tmp/render_module_docs.py`
- **Purpose**: No module docstring provided.
- **Dependencies**: stdlib [__future__, json, pathlib, typing] / third-party [None] / internal [None]
- **Related modules**: None
- **Lines of code**: 232
- **Environment variables**: None detected

### Classes
- None

### Functions
- `summarise_docstring(text: str | None, fallback: str) -> str` — No docstring provided.
- `format_list(values: list[str]) -> str` — No docstring provided.
- `indent(text: str, level: int = 1) -> str` — No docstring provided.
- `build_class_section(cls: dict[str, Any]) -> str` — No docstring provided.
- `build_function_section(fn: dict[str, Any]) -> str` — No docstring provided.
- `collect_inputs(module: dict[str, Any]) -> list[str]` — No docstring provided.
- `collect_outputs(module: dict[str, Any]) -> list[str]` — No docstring provided.
- `build_code_quality_notes(module: dict[str, Any]) -> list[str]` — No docstring provided.
- `main() -> None` — No docstring provided.

### Constants and Configuration
- `PROJECT_ROOT` = Path(__file__).resolve().parents[1]
- `METADATA_PATH` = PROJECT_ROOT / 'audit' / 'module_metadata.json'
- `OUTPUT_PATH` = PROJECT_ROOT / 'audit' / 'MODULE_DOCUMENTATION.md'

  TODO markers:
  - notes.append(f"Contains TODO markers at lines {', '.join(str(t) for t in todo_lines)}.")

### Data Flow
- Inputs: Derived from function arguments and class constructors; refer to method signatures above.
- Transformations: See method and function docstrings for intended behaviour.
- Outputs: Return values documented per function/method; side-effects depend on implementation.

### Integration Points
- External: None
- Internal: None

### Code Quality Notes
- TODO markers present; implementation incomplete.
- Missing module docstring.

