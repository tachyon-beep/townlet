## scripts/audit_bc_datasets.py

**Purpose**: Audit behaviour cloning datasets for checksum and metadata freshness.
**Dependencies**:
- Standard Library: __future__, argparse, datetime, hashlib, json, pathlib, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring.
  - Parameters: —
  - Returns: argparse.Namespace
- `load_versions(path) -> Mapping[str, Mapping[str, object]]` — No function docstring. Raises: FileNotFoundError(path), ValueError('versions.json must contain a JSON object').
  - Parameters: path
  - Returns: Mapping[str, Mapping[str, object]]
- `audit_dataset(name, payload) -> dict[str, object]` — No function docstring. Side effects: filesystem.
  - Parameters: name, payload
  - Returns: dict[str, object]
- `audit_catalog(versions_path) -> dict[str, object]` — No function docstring.
  - Parameters: versions_path
  - Returns: dict[str, object]
- `main() -> None` — No function docstring. Side effects: stdout. Raises: SystemExit(1).
  - Parameters: —
  - Returns: None

### Constants and Configuration
- `DEFAULT_VERSIONS_PATH` = "Path('data/bc_datasets/versions.json')"
- `REQUIRED_VERSION_KEYS` = ["captures_dir", "checksums", "manifest"]

### Data Flow
- Inputs: name, path, payload, versions_path
- Outputs: Mapping[str, Mapping[str, object]], None, argparse.Namespace, dict[str, object]
- Internal interactions: —
- External interactions: Path, argparse.ArgumentParser, audit_catalog, audit_dataset, captures_dir.exists, checksum_data.items, checksum_failures.append, checksums_path.exists, checksums_path.read_text, data.items, datasets.items, datetime.utcnow, … (24 more)

### Integration Points
- Runtime calls: Path, argparse.ArgumentParser, audit_catalog, audit_dataset, captures_dir.exists, checksum_data.items, checksum_failures.append, checksums_path.exists, checksums_path.read_text, data.items, datasets.items, datetime.utcnow, … (24 more)

### Code Quality Notes
- Missing function docstrings: parse_args, load_versions, audit_dataset, audit_catalog, main


## scripts/bc_metrics_summary.py

**Purpose**: Summarise behaviour cloning evaluation metrics.
**Dependencies**:
- Standard Library: __future__, argparse, json, pathlib
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring.
  - Parameters: —
  - Returns: argparse.Namespace
- `load_metrics(path) -> list[dict[str, float]]` — No function docstring. Raises: ValueError('Metrics file must be JSON object or list').
  - Parameters: path
  - Returns: list[dict[str, float]]
- `summarise(metrics) -> dict[str, float]` — No function docstring.
  - Parameters: metrics
  - Returns: dict[str, float]
- `main() -> None` — No function docstring. Side effects: stdout.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: metrics, path
- Outputs: None, argparse.Namespace, dict[str, float], list[dict[str, float]]
- Internal interactions: —
- External interactions: argparse.ArgumentParser, entry.get, join, json.dumps, json.loads, lines.append, load_metrics, parse_args, parser.add_argument, parser.parse_args, path.read_text, summarise, … (1 more)

### Integration Points
- Runtime calls: argparse.ArgumentParser, entry.get, join, json.dumps, json.loads, lines.append, load_metrics, parse_args, parser.add_argument, parser.parse_args, path.read_text, summarise, … (1 more)

### Code Quality Notes
- Missing function docstrings: parse_args, load_metrics, summarise, main


## scripts/benchmark_tick.py

**Purpose**: Simple benchmark to estimate average tick duration.
**Dependencies**:
- Standard Library: __future__, argparse, pathlib, time
- Third-Party: —
- Internal: townlet.config, townlet.core.sim_loop
**Related modules**: townlet.config, townlet.core.sim_loop

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring.
  - Parameters: —
  - Returns: argparse.Namespace
- `benchmark(config_path, ticks, enforce) -> float` — No function docstring.
  - Parameters: config_path, ticks, enforce
  - Returns: float
- `main() -> None` — No function docstring. Side effects: stdout.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: config_path, enforce, ticks
- Outputs: None, argparse.Namespace, float
- Internal interactions: —
- External interactions: SimulationLoop, argparse.ArgumentParser, benchmark, load_config, loop.run, parse_args, parser.add_argument, parser.parse_args, time.perf_counter

### Integration Points
- Runtime calls: SimulationLoop, argparse.ArgumentParser, benchmark, load_config, loop.run, parse_args, parser.add_argument, parser.parse_args, time.perf_counter

### Code Quality Notes
- Missing function docstrings: parse_args, benchmark, main


## scripts/capture_rollout.py

**Purpose**: CLI to capture Townlet rollout trajectories into replay samples.
**Dependencies**:
- Standard Library: __future__, argparse, datetime, json, pathlib, typing
- Third-Party: numpy
- Internal: townlet.config.loader, townlet.core.sim_loop, townlet.policy.metrics, townlet.policy.replay, townlet.policy.scenario_utils
**Related modules**: townlet.config.loader, townlet.core.sim_loop, townlet.policy.metrics, townlet.policy.replay, townlet.policy.scenario_utils

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring.
  - Parameters: —
  - Returns: argparse.Namespace
- `main() -> None` — No function docstring. Side effects: stdout.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None, argparse.Namespace
- Internal interactions: —
- External interactions: SimulationLoop, append, apply_scenario, argparse.ArgumentParser, args.config.resolve, by_agent.items, by_agent.setdefault, compute_sample_metrics, datetime.now, frame.get, frames_to_replay_sample, isoformat, … (18 more)

### Integration Points
- Runtime calls: SimulationLoop, append, apply_scenario, argparse.ArgumentParser, args.config.resolve, by_agent.items, by_agent.setdefault, compute_sample_metrics, datetime.now, frame.get, frames_to_replay_sample, isoformat, … (18 more)
- Third-party libraries: numpy

### Code Quality Notes
- Missing function docstrings: parse_args, main


## scripts/capture_rollout_suite.py

**Purpose**: Run rollout capture across a suite of configs.
**Dependencies**:
- Standard Library: __future__, argparse, pathlib, subprocess, sys, typing
- Third-Party: —
- Internal: townlet.config.loader
**Related modules**: townlet.config.loader

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: argparse.Namespace
- `run_capture(config, ticks, output, auto_seed, agent_filter, compress, retries) -> None` — No function docstring. Raises: re-raise.
  - Parameters: config, ticks, output, auto_seed, agent_filter, compress, retries
  - Returns: None
- `main() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: agent_filter, auto_seed, compress, config, output, retries, ticks
- Outputs: None, argparse.Namespace
- Internal interactions: —
- External interactions: Path, argparse.ArgumentParser, cmd.append, cmd.extend, load_config, output.mkdir, parse_args, parser.add_argument, parser.parse_args, run_capture, subprocess.run

### Integration Points
- Runtime calls: Path, argparse.ArgumentParser, cmd.append, cmd.extend, load_config, output.mkdir, parse_args, parser.add_argument, parser.parse_args, run_capture, subprocess.run

### Code Quality Notes
- Missing function docstrings: parse_args, run_capture, main


## scripts/capture_scripted.py

**Purpose**: Capture scripted trajectories for behaviour cloning datasets.
**Dependencies**:
- Standard Library: __future__, argparse, collections, json, pathlib, typing
- Third-Party: numpy
- Internal: townlet.config, townlet.core.sim_loop, townlet.policy.replay, townlet.policy.scenario_utils, townlet.policy.scripted
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.policy.replay, townlet.policy.scenario_utils, townlet.policy.scripted

### Classes
- None defined.

### Functions
- `parse_args(argv) -> argparse.Namespace` — No function docstring.
  - Parameters: argv
  - Returns: argparse.Namespace
- `_build_frame(adapter, agent_id, observation, reward, terminated, trajectory_id) -> Dict[str, object]` — No function docstring.
  - Parameters: adapter, agent_id, observation, reward, terminated, trajectory_id
  - Returns: Dict[str, object]
- `main(argv) -> None` — No function docstring.
  - Parameters: argv
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: adapter, agent_id, argv, observation, reward, terminated, trajectory_id
- Outputs: Dict[str, object], None, argparse.Namespace
- Internal interactions: —
- External interactions: ScriptedPolicyAdapter, SimulationLoop, _build_frame, adapter.last_actions.get, adapter.last_terminated.get, append, argparse.ArgumentParser, args.tags.split, artifacts.observations.items, artifacts.rewards.get, defaultdict, frames_by_agent.items, … (17 more)

### Integration Points
- Runtime calls: ScriptedPolicyAdapter, SimulationLoop, _build_frame, adapter.last_actions.get, adapter.last_terminated.get, append, argparse.ArgumentParser, args.tags.split, artifacts.observations.items, artifacts.rewards.get, defaultdict, frames_by_agent.items, … (17 more)
- Third-party libraries: numpy

### Code Quality Notes
- Missing function docstrings: parse_args, _build_frame, main


## scripts/console_dry_run.py

**Purpose**: Employment console dry-run harness.
**Dependencies**:
- Standard Library: __future__, pathlib, tempfile
- Third-Party: —
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.snapshots, townlet.snapshots.state, townlet.world.grid
**Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.snapshots, townlet.snapshots.state, townlet.world.grid

### Classes
- None defined.

### Functions
- `main() -> None` — No function docstring. Side effects: filesystem, stdout.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None
- Internal interactions: —
- External interactions: AgentSnapshot, ConsoleCommand, Path, SimulationLoop, as_dict, audit_path.exists, audit_path.read_text, create_console_router, load_config, loop.lifecycle.evaluate, loop.save_snapshot, loop.step, … (11 more)

### Integration Points
- Runtime calls: AgentSnapshot, ConsoleCommand, Path, SimulationLoop, as_dict, audit_path.exists, audit_path.read_text, create_console_router, load_config, loop.lifecycle.evaluate, loop.save_snapshot, loop.step, … (11 more)

### Code Quality Notes
- Missing function docstrings: main


## scripts/curate_trajectories.py

**Purpose**: Filter and summarise behaviour-cloning trajectories.
**Dependencies**:
- Standard Library: __future__, argparse, dataclasses, json, pathlib, typing
- Third-Party: numpy
- Internal: townlet.policy.replay
**Related modules**: townlet.policy.replay

### Classes
- **EvaluationResult** (bases: object; decorators: dataclass) — No class docstring.
  - Attributes: sample_path: Path = None, meta_path: Path = None, metrics: Mapping[str, float] = None, accepted: bool = None
  - Methods: None.

### Functions
- `parse_args(argv) -> argparse.Namespace` — No function docstring.
  - Parameters: argv
  - Returns: argparse.Namespace
- `_pair_files(directory) -> Iterable[tuple[Path, Path]]` — No function docstring.
  - Parameters: directory
  - Returns: Iterable[tuple[Path, Path]]
- `evaluate_sample(npz_path, json_path) -> EvaluationResult` — No function docstring.
  - Parameters: npz_path, json_path
  - Returns: EvaluationResult
- `curate(result) -> EvaluationResult` — No function docstring.
  - Parameters: result
  - Returns: EvaluationResult
- `write_manifest(results, output) -> None` — No function docstring.
  - Parameters: results, output
  - Returns: None
- `summarise(results) -> Mapping[str, float]` — No function docstring.
  - Parameters: results
  - Returns: Mapping[str, float]
- `main(argv) -> None` — No function docstring. Side effects: stdout.
  - Parameters: argv
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: argv, directory, json_path, npz_path, output, result, results
- Outputs: EvaluationResult, Iterable[tuple[Path, Path]], Mapping[str, float], None, argparse.Namespace
- Internal interactions: —
- External interactions: EvaluationResult, _pair_files, argparse.ArgumentParser, curate, directory.glob, evaluate_sample, json.dumps, json_path.with_suffix, load_replay_sample, manifest.append, np.count_nonzero, np.sum, … (11 more)

### Integration Points
- Runtime calls: EvaluationResult, _pair_files, argparse.ArgumentParser, curate, directory.glob, evaluate_sample, json.dumps, json_path.with_suffix, load_replay_sample, manifest.append, np.count_nonzero, np.sum, … (11 more)
- Third-party libraries: numpy

### Code Quality Notes
- Missing function docstrings: parse_args, _pair_files, evaluate_sample, curate, write_manifest, summarise, main


## scripts/inspect_affordances.py

**Purpose**: Inspect affordance runtime state from configs or snapshots.
**Dependencies**:
- Standard Library: __future__, argparse, contextlib, dataclasses, io, json, pathlib, typing
- Third-Party: —
- Internal: townlet.config, townlet.core.sim_loop
**Related modules**: townlet.config, townlet.core.sim_loop

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring.
  - Parameters: —
  - Returns: argparse.Namespace
- `_normalise_running_payload(running) -> dict[str, Any]` — No function docstring.
  - Parameters: running
  - Returns: dict[str, Any]
- `inspect_snapshot(path) -> dict[str, Any]` — No function docstring.
  - Parameters: path
  - Returns: dict[str, Any]
- `inspect_config(path, ticks) -> dict[str, Any]` — No function docstring.
  - Parameters: path, ticks
  - Returns: dict[str, Any]
- `render_text(report) -> str` — No function docstring.
  - Parameters: report
  - Returns: str
- `main() -> None` — No function docstring. Side effects: filesystem, stdout.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: path, report, running, ticks
- Outputs: None, argparse.Namespace, dict[str, Any], str
- Internal interactions: —
- External interactions: Path, SimulationLoop, _NullTransport, _normalise_running_payload, argparse.ArgumentParser, asdict, contextlib.redirect_stdout, document.get, group.add_argument, inspect_config, inspect_snapshot, io.StringIO, … (21 more)

### Integration Points
- Runtime calls: Path, SimulationLoop, _NullTransport, _normalise_running_payload, argparse.ArgumentParser, asdict, contextlib.redirect_stdout, document.get, group.add_argument, inspect_config, inspect_snapshot, io.StringIO, … (21 more)

### Code Quality Notes
- Missing function docstrings: parse_args, _normalise_running_payload, inspect_snapshot, inspect_config, render_text, main


## scripts/manage_phase_c.py

**Purpose**: Helper script to toggle Phase C social reward stages in configs.
**Dependencies**:
- Standard Library: __future__, argparse, pathlib, typing
- Third-Party: yaml
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring.
  - Parameters: —
  - Returns: argparse.Namespace
- `load_config(path) -> Dict[str, Any]` — No function docstring. Raises: FileNotFoundError(path), ValueError(f'Config at {path} must be a mapping').
  - Parameters: path
  - Returns: Dict[str, Any]
- `ensure_nested(mapping, keys) -> Dict[str, Any]` — No function docstring.
  - Parameters: mapping, keys
  - Returns: Dict[str, Any]
- `write_config(data) -> None` — No function docstring. Side effects: stdout.
  - Parameters: data
  - Returns: None
- `handle_set_stage(args) -> None` — No function docstring.
  - Parameters: args
  - Returns: None
- `parse_schedule_entries(entries) -> List[Dict[str, Any]]` — No function docstring. Raises: ValueError('Cycle must be non-negative'), ValueError(f"Cycle must be an integer: '{cycle_text}'"), ValueError(f"Invalid social reward stage '{stage}'"), ValueError(f"Schedule entry '{entry}' must be in cycle:stage form").
  - Parameters: entries
  - Returns: List[Dict[str, Any]]
- `handle_schedule(args) -> None` — No function docstring.
  - Parameters: args
  - Returns: None
- `main() -> None` — No function docstring. Raises: ValueError(f'Unsupported command: {args.command}').
  - Parameters: —
  - Returns: None

### Constants and Configuration
- `VALID_STAGES` = ["C1", "C2", "C3", "OFF"]

### Data Flow
- Inputs: args, data, entries, keys, mapping, path
- Outputs: Dict[str, Any], List[Dict[str, Any]], None, argparse.Namespace
- Internal interactions: —
- External interactions: argparse.ArgumentParser, current.get, cycle_text.strip, ensure_nested, entry.split, handle_schedule, handle_set_stage, load_config, parse_args, parse_schedule_entries, parsed.append, parser.add_subparsers, … (16 more)

### Integration Points
- Runtime calls: argparse.ArgumentParser, current.get, cycle_text.strip, ensure_nested, entry.split, handle_schedule, handle_set_stage, load_config, parse_args, parse_schedule_entries, parsed.append, parser.add_subparsers, … (16 more)
- Third-party libraries: yaml

### Code Quality Notes
- Missing function docstrings: parse_args, load_config, ensure_nested, write_config, handle_set_stage, parse_schedule_entries, handle_schedule, main


## scripts/merge_rollout_metrics.py

**Purpose**: Merge captured rollout metrics into the golden stats JSON.
**Dependencies**:
- Standard Library: __future__, argparse, json, pathlib
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring.
  - Parameters: —
  - Returns: argparse.Namespace
- `_load_metrics_from_dir(scenario_dir) -> dict[str, dict[str, float]] | None` — No function docstring. Raises: ValueError(f'Metrics file {metrics_path} must contain an object').
  - Parameters: scenario_dir
  - Returns: dict[str, dict[str, float]] | None
- `_collect_input_metrics(root, allow_template) -> dict[str, dict[str, dict[str, float]]]` — No function docstring.
  - Parameters: root, allow_template
  - Returns: dict[str, dict[str, dict[str, float]]]
- `main() -> None` — No function docstring. Side effects: stdout. Raises: FileNotFoundError(args.input_root), ValueError(f'Golden stats file {golden_path} must contain an object').
  - Parameters: —
  - Returns: None

### Constants and Configuration
- `DEFAULT_GOLDEN_PATH` = "Path('docs/samples/rollout_scenario_stats.json')"
- `METRICS_FILENAME` = 'rollout_sample_metrics.json'

### Data Flow
- Inputs: allow_template, root, scenario_dir
- Outputs: None, argparse.Namespace, dict[str, dict[str, dict[str, float]]], dict[str, dict[str, float]] | None
- Internal interactions: —
- External interactions: _collect_input_metrics, _load_metrics_from_dir, argparse.ArgumentParser, args.input_root.exists, capture_metrics.items, data.get, golden_path.exists, golden_path.read_text, json.dumps, json.loads, metrics_path.exists, metrics_path.read_text, … (9 more)

### Integration Points
- Runtime calls: _collect_input_metrics, _load_metrics_from_dir, argparse.ArgumentParser, args.input_root.exists, capture_metrics.items, data.get, golden_path.exists, golden_path.read_text, json.dumps, json.loads, metrics_path.exists, metrics_path.read_text, … (9 more)

### Code Quality Notes
- Missing function docstrings: parse_args, _load_metrics_from_dir, _collect_input_metrics, main


## scripts/observer_ui.py

**Purpose**: Launch the Townlet observer dashboard against a local simulation.
**Dependencies**:
- Standard Library: __future__, argparse, pathlib
- Third-Party: —
- Internal: townlet.config, townlet.core.sim_loop, townlet_ui.dashboard
**Related modules**: townlet.config, townlet.core.sim_loop, townlet_ui.dashboard

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring.
  - Parameters: —
  - Returns: argparse.Namespace
- `main() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None, argparse.Namespace
- Internal interactions: —
- External interactions: SimulationLoop, argparse.ArgumentParser, load_config, parse_args, parser.add_argument, parser.parse_args, run_dashboard

### Integration Points
- Runtime calls: SimulationLoop, argparse.ArgumentParser, load_config, parse_args, parser.add_argument, parser.parse_args, run_dashboard

### Code Quality Notes
- Missing function docstrings: parse_args, main


## scripts/ppo_telemetry_plot.py

**Purpose**: Quick-look plotting utility for PPO telemetry JSONL logs.
**Dependencies**:
- Standard Library: __future__, argparse, json, pathlib, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: argparse.Namespace
- `load_entries(log_path) -> list[dict[str, Any]]` — No function docstring. Raises: FileNotFoundError(log_path), ValueError(f'No telemetry entries found in {log_path}').
  - Parameters: log_path
  - Returns: list[dict[str, Any]]
- `summarise(entries) -> None` — No function docstring. Side effects: stdout.
  - Parameters: entries
  - Returns: None
- `plot(entries, show, output) -> None` — No function docstring. Side effects: stdout.
  - Parameters: entries, show, output
  - Returns: None
- `main() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: entries, log_path, output, show
- Outputs: None, argparse.Namespace, list[dict[str, Any]]
- Internal interactions: —
- External interactions: Path, argparse.ArgumentParser, ax1.plot, ax1.set_title, ax1.set_xlabel, ax1.set_ylabel, ax1.tick_params, ax1.twinx, ax2.plot, ax2.set_ylabel, ax2.tick_params, entries.append, … (17 more)

### Integration Points
- Runtime calls: Path, argparse.ArgumentParser, ax1.plot, ax1.set_title, ax1.set_xlabel, ax1.set_ylabel, ax1.tick_params, ax1.twinx, ax2.plot, ax2.set_ylabel, ax2.tick_params, entries.append, … (17 more)

### Code Quality Notes
- Missing function docstrings: parse_args, load_entries, summarise, plot, main


## scripts/profile_observation_tensor.py

**Purpose**: Profile observation tensor dimensions for a given config.
**Dependencies**:
- Standard Library: __future__, argparse, json, pathlib, statistics
- Third-Party: numpy
- Internal: townlet.config, townlet.observations.builder, townlet.world
**Related modules**: townlet.config, townlet.observations.builder, townlet.world

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring.
  - Parameters: —
  - Returns: argparse.Namespace
- `bootstrap_world(config_path, agent_count) -> tuple[WorldState, ObservationBuilder]` — No function docstring.
  - Parameters: config_path, agent_count
  - Returns: tuple[WorldState, ObservationBuilder]
- `profile(world, builder, ticks) -> dict[str, object]` — No function docstring.
  - Parameters: world, builder, ticks
  - Returns: dict[str, object]
- `main() -> None` — No function docstring. Side effects: stdout.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: agent_count, builder, config_path, ticks, world
- Outputs: None, argparse.Namespace, dict[str, object], tuple[WorldState, ObservationBuilder]
- Internal interactions: —
- External interactions: AgentSnapshot, ObservationBuilder, WorldState.from_config, argparse.ArgumentParser, args.output.write_text, batch.values, bootstrap_world, builder._feature_index.items, builder.build_batch, feature_dims.append, get, json.dumps, … (10 more)

### Integration Points
- Runtime calls: AgentSnapshot, ObservationBuilder, WorldState.from_config, argparse.ArgumentParser, args.output.write_text, batch.values, bootstrap_world, builder._feature_index.items, builder.build_batch, feature_dims.append, get, json.dumps, … (10 more)
- Third-party libraries: numpy

### Code Quality Notes
- Missing function docstrings: parse_args, bootstrap_world, profile, main


## scripts/promotion_drill.py

**Purpose**: Run a scripted promotion/rollback drill and capture artefacts.
**Dependencies**:
- Standard Library: __future__, argparse, json, pathlib, typing
- Third-Party: —
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop
**Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop

### Classes
- None defined.

### Functions
- `_ensure_candidate_ready(loop) -> None` — No function docstring.
  - Parameters: loop
  - Returns: None
- `run_drill(config_path, output_dir, checkpoint) -> dict[str, Any]` — No function docstring.
  - Parameters: config_path, output_dir, checkpoint
  - Returns: dict[str, Any]
- `main(argv) -> int` — No function docstring. Side effects: filesystem, stdout.
  - Parameters: argv
  - Returns: int

### Constants and Configuration
- None.

### Data Flow
- Inputs: argv, checkpoint, config_path, loop, output_dir
- Outputs: None, dict[str, Any], int
- Internal interactions: —
- External interactions: ConsoleCommand, Path, SimulationLoop, _ensure_candidate_ready, argparse.ArgumentParser, args.checkpoint.expanduser, args.config.expanduser, args.output.expanduser, create_console_router, json.dumps, load_config, loop.promotion.snapshot, … (7 more)

### Integration Points
- Runtime calls: ConsoleCommand, Path, SimulationLoop, _ensure_candidate_ready, argparse.ArgumentParser, args.checkpoint.expanduser, args.config.expanduser, args.output.expanduser, create_console_router, json.dumps, load_config, loop.promotion.snapshot, … (7 more)

### Code Quality Notes
- Missing function docstrings: _ensure_candidate_ready, run_drill, main


## scripts/promotion_evaluate.py

**Purpose**: Evaluate promotion readiness from anneal results payloads.
**Dependencies**:
- Standard Library: __future__, argparse, json, pathlib, sys, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `parse_args(argv) -> argparse.Namespace` — No function docstring.
  - Parameters: argv
  - Returns: argparse.Namespace
- `_load_payload(path) -> Dict[str, Any]` — No function docstring. Raises: ValueError('No input provided on stdin').
  - Parameters: path
  - Returns: Dict[str, Any]
- `_derive_status(results) -> str` — No function docstring.
  - Parameters: results
  - Returns: str
- `_collect_reasons(results) -> List[str]` — No function docstring.
  - Parameters: results
  - Returns: List[str]
- `evaluate(payload) -> Dict[str, Any]` — No function docstring. Raises: ValueError("Payload must include a 'results' array or BC fields").
  - Parameters: payload
  - Returns: Dict[str, Any]
- `_print_human(summary) -> None` — No function docstring. Side effects: stdout.
  - Parameters: summary
  - Returns: None
- `main(argv) -> int` — No function docstring. Side effects: stdout.
  - Parameters: argv
  - Returns: int

### Constants and Configuration
- `DEFAULT_INPUT_PATH` = "Path('artifacts/m7/anneal_results.json')"

### Data Flow
- Inputs: argv, path, payload, results, summary
- Outputs: Dict[str, Any], List[str], None, argparse.Namespace, int, str
- Internal interactions: —
- External interactions: _collect_reasons, _derive_status, _load_payload, _print_human, argparse.ArgumentParser, data.strip, evaluate, join, json.dumps, json.loads, lines.append, lines.extend, … (13 more)

### Integration Points
- Runtime calls: _collect_reasons, _derive_status, _load_payload, _print_human, argparse.ArgumentParser, data.strip, evaluate, join, json.dumps, json.loads, lines.append, lines.extend, … (13 more)

### Code Quality Notes
- Missing function docstrings: parse_args, _load_payload, _derive_status, _collect_reasons, evaluate, _print_human, main


## scripts/reward_summary.py

**Purpose**: Summarise reward breakdown telemetry for operations teams.
**Dependencies**:
- Standard Library: __future__, argparse, collections, dataclasses, json, pathlib, sys, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- **ComponentStats** (bases: object; decorators: dataclass) — No class docstring.
  - Attributes: count: int = 0, total: float = 0.0, minimum: float = "float('inf')", maximum: float = "float('-inf')"
  - Methods:
    - `update(self, value) -> None` — No method docstring.
    - `mean(self) -> float` — No method docstring.
    - `as_dict(self) -> dict[str, float | int]` — No method docstring.
- **RewardAggregator** (bases: object; decorators: —) — Aggregate reward breakdowns from telemetry payloads.
  - Methods:
    - `__init__(self) -> None` — No method docstring.
    - `add_payload(self, payload, source) -> None` — No method docstring.
    - `summary(self) -> dict[str, object]` — No method docstring.

### Functions
- `_is_number(value) -> bool` — No function docstring.
  - Parameters: value
  - Returns: bool
- `iter_payloads(path) -> Iterator[tuple[Mapping[str, object], str]]` — No function docstring. Raises: ValueError(f'{path}: expected JSON object or array'), ValueError(f'{path}:{idx}: expected JSON object'), ValueError(f'{path}[{idx}] expected JSON object').
  - Parameters: path
  - Returns: Iterator[tuple[Mapping[str, object], str]]
- `collect_statistics(paths) -> RewardAggregator` — No function docstring.
  - Parameters: paths
  - Returns: RewardAggregator
- `render_text(summary) -> str` — No function docstring.
  - Parameters: summary
  - Returns: str
- `render_markdown(summary) -> str` — No function docstring.
  - Parameters: summary
  - Returns: str
- `render_json(summary) -> str` — No function docstring.
  - Parameters: summary
  - Returns: str
- `parse_args(argv) -> argparse.Namespace` — No function docstring.
  - Parameters: argv
  - Returns: argparse.Namespace
- `main(argv) -> int` — No function docstring. Side effects: stdout.
  - Parameters: argv
  - Returns: int

### Constants and Configuration
- None.

### Data Flow
- Inputs: argv, path, paths, summary, value
- Outputs: Iterator[tuple[Mapping[str, object], str]], RewardAggregator, argparse.Namespace, bool, int, str
- Internal interactions: —
- External interactions: RewardAggregator, agents.get, agents.items, aggregator.add_payload, argparse.ArgumentParser, breakdown.items, collect_statistics, components.items, defaultdict, get, info.get, iter_payloads, … (28 more)

### Integration Points
- Runtime calls: RewardAggregator, agents.get, agents.items, aggregator.add_payload, argparse.ArgumentParser, breakdown.items, collect_statistics, components.items, defaultdict, get, info.get, iter_payloads, … (28 more)

### Code Quality Notes
- Missing function docstrings: _is_number, iter_payloads, collect_statistics, render_text, render_markdown, render_json, parse_args, main
- Missing method docstrings: ComponentStats.update, ComponentStats.mean, ComponentStats.as_dict, RewardAggregator.__init__, RewardAggregator.add_payload, RewardAggregator.summary


## scripts/run_anneal_rehearsal.py

**Purpose**: Run BC + anneal rehearsal using production manifests and capture artefacts.
**Dependencies**:
- Standard Library: __future__, argparse, json, pathlib, typing
- Third-Party: —
- Internal: townlet.config, townlet.policy.replay, townlet.policy.runner
**Related modules**: townlet.config, townlet.policy.replay, townlet.policy.runner

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: argparse.Namespace
- `run_rehearsal(config_path, manifest_path, log_dir) -> Dict[str, object]` — No function docstring.
  - Parameters: config_path, manifest_path, log_dir
  - Returns: Dict[str, object]
- `evaluate_summary(summary) -> Dict[str, object]` — No function docstring. Side effects: filesystem. Raises: ModuleNotFoundError('Could not load promotion_evaluate module').
  - Parameters: summary
  - Returns: Dict[str, object]
- `main() -> None` — No function docstring. Side effects: stdout. Raises: SystemExit(1).
  - Parameters: —
  - Returns: None

### Constants and Configuration
- `DEFAULT_CONFIG` = "Path('artifacts/m5/acceptance/config_idle_v1.yaml')"
- `DEFAULT_MANIFEST` = "Path('data/bc_datasets/manifests/idle_v1.json')"
- `DEFAULT_LOG_DIR` = "Path('artifacts/m5/acceptance/logs')"

### Data Flow
- Inputs: config_path, log_dir, manifest_path, summary
- Outputs: Dict[str, object], None, argparse.Namespace
- Internal interactions: —
- External interactions: Path, ReplayDatasetConfig.from_manifest, TrainingHarness, _promotion_eval.evaluate, argparse.ArgumentParser, args.summary.write_text, bc_stage.get, combined.update, evaluate_summary, final.get, harness.evaluate_anneal_results, harness.promotion.snapshot, … (15 more)

### Integration Points
- Runtime calls: Path, ReplayDatasetConfig.from_manifest, TrainingHarness, _promotion_eval.evaluate, argparse.ArgumentParser, args.summary.write_text, bc_stage.get, combined.update, evaluate_summary, final.get, harness.evaluate_anneal_results, harness.promotion.snapshot, … (15 more)

### Code Quality Notes
- Missing function docstrings: parse_args, run_rehearsal, evaluate_summary, main


## scripts/run_employment_smoke.py

**Purpose**: Employment loop smoke test runner for R2 mitigation.
**Dependencies**:
- Standard Library: __future__, argparse, json, pathlib, typing
- Third-Party: —
- Internal: townlet.config, townlet.core.sim_loop
**Related modules**: townlet.config, townlet.core.sim_loop

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: argparse.Namespace
- `run_smoke(config_path, ticks, enforce) -> Dict[str, Any]` — No function docstring.
  - Parameters: config_path, ticks, enforce
  - Returns: Dict[str, Any]
- `main() -> None` — No function docstring. Side effects: stdout.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: config_path, enforce, ticks
- Outputs: Dict[str, Any], None, argparse.Namespace
- Internal interactions: —
- External interactions: Path, SimulationLoop, alerts.append, argparse.ArgumentParser, args.metrics_output.write_text, conflict_events.append, employment_events.append, event.get, event_name.startswith, json.dumps, load_config, loop.step, … (8 more)

### Integration Points
- Runtime calls: Path, SimulationLoop, alerts.append, argparse.ArgumentParser, args.metrics_output.write_text, conflict_events.append, employment_events.append, event.get, event_name.startswith, json.dumps, load_config, loop.step, … (8 more)

### Code Quality Notes
- Missing function docstrings: parse_args, run_smoke, main


## scripts/run_mixed_soak.py

**Purpose**: Run alternating replay/rollout PPO cycles for soak testing.
**Dependencies**:
- Standard Library: __future__, argparse, pathlib, sys
- Third-Party: —
- Internal: townlet.config.loader, townlet.policy.replay, townlet.policy.runner
**Related modules**: townlet.config.loader, townlet.policy.replay, townlet.policy.runner

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring.
  - Parameters: —
  - Returns: argparse.Namespace
- `main() -> None` — No function docstring. Side effects: stdout.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- `ROOT` = 'Path(__file__).resolve().parents[1]'
- `SRC` = "ROOT / 'src'"

### Data Flow
- Inputs: —
- Outputs: None, argparse.Namespace
- Internal interactions: —
- External interactions: ReplayDatasetConfig.from_capture_dir, TrainingHarness, argparse.ArgumentParser, harness.run_ppo, harness.run_rollout_ppo, load_config, log_path.exists, log_path.unlink, output_dir.mkdir, parse_args, parser.add_argument, parser.parse_args

### Integration Points
- Runtime calls: ReplayDatasetConfig.from_capture_dir, TrainingHarness, argparse.ArgumentParser, harness.run_ppo, harness.run_rollout_ppo, load_config, log_path.exists, log_path.unlink, output_dir.mkdir, parse_args, parser.add_argument, parser.parse_args

### Code Quality Notes
- Missing function docstrings: parse_args, main


## scripts/run_replay.py

**Purpose**: Utility to replay observation/telemetry samples for analysis or tutorials.
**Dependencies**:
- Standard Library: __future__, argparse, json, pathlib, typing
- Third-Party: numpy
- Internal: townlet.policy.replay
**Related modules**: townlet.policy.replay

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring.
  - Parameters: —
  - Returns: argparse.Namespace
- `render_observation(sample) -> None` — No function docstring. Side effects: stdout.
  - Parameters: sample
  - Returns: None
- `inspect_telemetry(path) -> None` — No function docstring. Side effects: stdout.
  - Parameters: path
  - Returns: None
- `main() -> None` — No function docstring. Side effects: stdout.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: path, sample
- Outputs: None, argparse.Namespace
- Internal interactions: —
- External interactions: argparse.ArgumentParser, conflict.get, data.get, event.get, feature_names.index, get, inspect_telemetry, json.loads, load_replay_sample, parse_args, parser.add_argument, parser.parse_args, … (4 more)

### Integration Points
- Runtime calls: argparse.ArgumentParser, conflict.get, data.get, event.get, feature_names.index, get, inspect_telemetry, json.loads, load_replay_sample, parse_args, parser.add_argument, parser.parse_args, … (4 more)
- Third-party libraries: numpy

### Code Quality Notes
- Missing function docstrings: parse_args, render_observation, inspect_telemetry, main


## scripts/run_simulation.py

**Purpose**: Run a headless Townlet simulation loop for debugging.
**Dependencies**:
- Standard Library: __future__, argparse, pathlib
- Third-Party: —
- Internal: townlet.config.loader, townlet.core.sim_loop
**Related modules**: townlet.config.loader, townlet.core.sim_loop

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring.
  - Parameters: —
  - Returns: argparse.Namespace
- `main() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None, argparse.Namespace
- Internal interactions: —
- External interactions: SimulationLoop, argparse.ArgumentParser, load_config, loop.run, parse_args, parser.add_argument, parser.parse_args

### Integration Points
- Runtime calls: SimulationLoop, argparse.ArgumentParser, load_config, loop.run, parse_args, parser.add_argument, parser.parse_args

### Code Quality Notes
- Missing function docstrings: parse_args, main


## scripts/run_training.py

**Purpose**: CLI entry point for training Townlet policies.
**Dependencies**:
- Standard Library: __future__, argparse, json, pathlib
- Third-Party: —
- Internal: townlet.config, townlet.config.loader, townlet.policy.replay, townlet.policy.runner
**Related modules**: townlet.config, townlet.config.loader, townlet.policy.replay, townlet.policy.runner

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring.
  - Parameters: —
  - Returns: argparse.Namespace
- `_collect_ppo_overrides(args) -> dict[str, object]` — No function docstring.
  - Parameters: args
  - Returns: dict[str, object]
- `_apply_ppo_overrides(config, overrides) -> None` — No function docstring.
  - Parameters: config, overrides
  - Returns: None
- `_build_dataset_config_from_args(args, default_manifest) -> ReplayDatasetConfig | None` — No function docstring.
  - Parameters: args, default_manifest
  - Returns: ReplayDatasetConfig | None
- `main() -> None` — No function docstring. Side effects: stdout. Raises: SystemExit(1), ValueError('Anneal mode requires --bc-manifest or config.training.bc.manifest'), ValueError('Anneal mode requires replay dataset via --capture-dir, --replay-manifest, --replay-sample, or config.training.replay_manifest'), ValueError('BC mode requires --bc-manifest or config.training.bc.manifest'), ValueError('Mixed mode requires replay dataset via --capture-dir, --replay-manifest, --replay-sample, or config.training.replay_manifest'), ValueError('Mixed mode requires rollout capture; set --rollout-ticks or config.training.rollout_ticks'), ValueError('No agents available for rollout capture. Provide a scenario with agents or rerun with --rollout-auto-seed-agents.'), ValueError('Replay mode requires --capture-dir, --replay-manifest, --replay-sample, or config.training.replay_manifest'), ValueError('Rollout mode does not use replay manifests'), ValueError('Rollout mode requires rollout capture; set --rollout-ticks or config.training.rollout_ticks'), ValueError('Rollout modes expect live capture; remove --capture-dir'), ValueError('Specify either --capture-dir or --replay-manifest, not both'), ValueError('rollout_ticks must be positive for rollout/mixed modes'), ValueError(f"Unsupported training mode '{mode}'"), re-raise.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: args, config, default_manifest, overrides
- Outputs: None, ReplayDatasetConfig | None, argparse.Namespace, dict[str, object]
- Internal interactions: —
- External interactions: PPOConfig, ReplayDatasetConfig, ReplayDatasetConfig.from_capture_dir, ReplayDatasetConfig.from_manifest, TrainingHarness, _apply_ppo_overrides, _build_dataset_config_from_args, _collect_ppo_overrides, argparse.ArgumentParser, base.model_copy, buffer.build_dataset, harness.capture_rollout, … (18 more)

### Integration Points
- Runtime calls: PPOConfig, ReplayDatasetConfig, ReplayDatasetConfig.from_capture_dir, ReplayDatasetConfig.from_manifest, TrainingHarness, _apply_ppo_overrides, _build_dataset_config_from_args, _collect_ppo_overrides, argparse.ArgumentParser, base.model_copy, buffer.build_dataset, harness.capture_rollout, … (18 more)

### Code Quality Notes
- Missing function docstrings: parse_args, _collect_ppo_overrides, _apply_ppo_overrides, _build_dataset_config_from_args, main


## scripts/telemetry_check.py

**Purpose**: Validate Townlet telemetry payloads against known schema versions.
**Dependencies**:
- Standard Library: __future__, argparse, json, pathlib, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring.
  - Parameters: —
  - Returns: argparse.Namespace
- `load_payload(path) -> Dict[str, Any]` — No function docstring. Raises: ValueError('Telemetry payload must be a JSON object').
  - Parameters: path
  - Returns: Dict[str, Any]
- `validate(payload, schema_version) -> None` — No function docstring. Raises: ValueError('Payload missing employment metrics section'), ValueError(f"Agent '{agent_id}' missing job keys: {sorted(missing_agent)} (schema {schema_version})"), ValueError(f"Unsupported schema_version '{schema_version}'. Known: {sorted(SUPPORTED_SCHEMAS)}"), ValueError(f'Employment metrics missing keys: {sorted(missing_employment)}').
  - Parameters: payload, schema_version
  - Returns: None
- `main() -> None` — No function docstring. Side effects: stdout. Raises: ValueError('Could not determine schema_version; specify with --schema').
  - Parameters: —
  - Returns: None

### Constants and Configuration
- `SUPPORTED_SCHEMAS` = {"0.2.0": {"employment_keys": ["daily_exit_cap", "exits_today", "pending", "pending_count", "queue_limit", "review_window"], "job_required_keys": ["attendance_ratio", "job_id", "late_ticks_today", "on_shift", "shift_state", "wages_withheld", "wallet"]}}

### Data Flow
- Inputs: path, payload, schema_version
- Outputs: Dict[str, Any], None, argparse.Namespace
- Internal interactions: —
- External interactions: SUPPORTED_SCHEMAS.get, agent_payload.keys, argparse.ArgumentParser, employment.keys, jobs.items, json.loads, load_payload, parse_args, parser.add_argument, parser.parse_args, path.read_text, payload.get, … (1 more)

### Integration Points
- Runtime calls: SUPPORTED_SCHEMAS.get, agent_payload.keys, argparse.ArgumentParser, employment.keys, jobs.items, json.loads, load_payload, parse_args, parser.add_argument, parser.parse_args, path.read_text, payload.get, … (1 more)

### Code Quality Notes
- Missing function docstrings: parse_args, load_payload, validate, main


## scripts/telemetry_summary.py

**Purpose**: Produce summaries for PPO telemetry logs.
**Dependencies**:
- Standard Library: __future__, argparse, json, pathlib, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring.
  - Parameters: —
  - Returns: argparse.Namespace
- `load_records(path) -> list[dict[str, object]]` — No function docstring. Raises: ValueError(f'{path}: no telemetry records found'), ValueError(f'{path}:{line_number}: expected JSON object'), ValueError(f'{path}:{line_number}: invalid JSON – {err}').
  - Parameters: path
  - Returns: list[dict[str, object]]
- `load_baseline(path) -> dict[str, float] | None` — No function docstring. Raises: ValueError('Baseline must be a JSON object').
  - Parameters: path
  - Returns: dict[str, float] | None
- `summarise(records, baseline) -> dict[str, object]` — No function docstring.
  - Parameters: records, baseline
  - Returns: dict[str, object]
- `_format_optional_float(value, precision) -> str` — No function docstring.
  - Parameters: value, precision
  - Returns: str
- `render_text(summary) -> str` — No function docstring.
  - Parameters: summary
  - Returns: str
- `render_markdown(summary) -> str` — No function docstring.
  - Parameters: summary
  - Returns: str
- `render(summary, fmt) -> str` — No function docstring.
  - Parameters: summary, fmt
  - Returns: str
- `main() -> None` — No function docstring. Side effects: stdout.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: baseline, fmt, path, precision, records, summary, value
- Outputs: None, argparse.Namespace, dict[str, float] | None, dict[str, object], list[dict[str, object]], str
- Internal interactions: —
- External interactions: _format_optional_float, anneal.get, argparse.ArgumentParser, baseline.items, data.items, drift.items, join, json.dumps, json.loads, latest_anneal.get, line.strip, lines.append, … (16 more)

### Integration Points
- Runtime calls: _format_optional_float, anneal.get, argparse.ArgumentParser, baseline.items, data.items, drift.items, join, json.dumps, json.loads, latest_anneal.get, line.strip, lines.append, … (16 more)

### Code Quality Notes
- Missing function docstrings: parse_args, load_records, load_baseline, summarise, _format_optional_float, render_text, render_markdown, render, main


## scripts/telemetry_watch.py

**Purpose**: Tail PPO telemetry logs and alert on metric thresholds.
**Dependencies**:
- Standard Library: __future__, argparse, json, pathlib, sys, time, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `build_parser() -> argparse.ArgumentParser` — No function docstring.
  - Parameters: —
  - Returns: argparse.ArgumentParser
- `parse_args() -> argparse.Namespace` — No function docstring.
  - Parameters: —
  - Returns: argparse.Namespace
- `parse_args_from_list(argv) -> argparse.Namespace` — No function docstring.
  - Parameters: argv
  - Returns: argparse.Namespace
- `stream_records(path, follow, interval) -> Iterator[dict[str, float]]` — No function docstring. Raises: FileNotFoundError(path), ValueError(f'{path}: expected JSON object, got {type(payload).__name__}'), ValueError(f'{path}: telemetry record missing keys: {sorted(missing)}').
  - Parameters: path, follow, interval
  - Returns: Iterator[dict[str, float]]
- `_parse_health_line(line) -> dict[str, float]` — No function docstring. Raises: ValueError("log line does not start with 'tick_health'"), ValueError('empty log line'), ValueError(f'health log missing fields: {sorted(missing)}').
  - Parameters: line
  - Returns: dict[str, float]
- `stream_health_records(path, follow, interval) -> Iterator[dict[str, float]]` — No function docstring. Raises: FileNotFoundError(path).
  - Parameters: path, follow, interval
  - Returns: Iterator[dict[str, float]]
- `check_thresholds(record, args) -> None` — No function docstring. Raises: SystemExit(f'Epoch {epoch}: anneal queue_conflict_events {record['queue_conflict_events']:.1f} below threshold {queue_min}'), SystemExit(f'Epoch {epoch}: anneal queue_conflict_intensity_sum {record['queue_conflict_intensity_sum']:.2f} below threshold {intensity_min}'), SystemExit(f'Epoch {epoch}: anneal_bc_accuracy {bc_accuracy:.3f} below threshold {args.anneal_bc_min}'), SystemExit(f'Epoch {epoch}: batch_entropy_mean {record['batch_entropy_mean']:.6f} below threshold {args.entropy_threshold}'), SystemExit(f'Epoch {epoch}: chat_quality_mean {record['chat_quality_mean']:.3f} below threshold {args.chat_quality_min}'), SystemExit(f'Epoch {epoch}: grad_norm {record['grad_norm']:.6f} exceeds threshold {args.grad_threshold}'), SystemExit(f'Epoch {epoch}: kl_divergence {record['kl_divergence']:.6f} exceeds threshold {args.kl_threshold}'), SystemExit(f'Epoch {epoch}: late_help_events {record['late_help_events']:.1f} below threshold {args.late_help_min}'), SystemExit(f'Epoch {epoch}: loss_total {record['loss_total']:.6f} drifts beyond ±{loss_limit * 100:.1f}% of baseline {loss_baseline:.6f}'), SystemExit(f'Epoch {epoch}: loss_total {record['loss_total']:.6f} exceeds threshold {args.loss_threshold}'), SystemExit(f'Epoch {epoch}: queue_conflict_events {record['queue_conflict_events']:.1f} below threshold {args.queue_events_min}'), SystemExit(f'Epoch {epoch}: queue_conflict_intensity_sum {record['queue_conflict_intensity_sum']:.2f} below threshold {args.queue_intensity_min}'), SystemExit(f'Epoch {epoch}: reward_advantage_corr {record['reward_advantage_corr']:.6f} below threshold {args.reward_corr_threshold}'), SystemExit(f'Epoch {epoch}: shared_meal_events {record['shared_meal_events']:.1f} below threshold {args.shared_meal_min}'), SystemExit(f'Epoch {epoch}: shift_takeover_events {record['shift_takeover_events']:.1f} exceeds threshold {args.shift_takeover_max}'), SystemExit(f'Epoch {epoch}: shower_complete_events {record['shower_complete_events']:.1f} below threshold {args.shower_complete_min}'), SystemExit(f'Epoch {epoch}: sleep_complete_events {record['sleep_complete_events']:.1f} below threshold {args.sleep_complete_min}'), SystemExit(f'Epoch {epoch}: utility_outage_events {record['utility_outage_events']:.1f} exceeds threshold {args.utility_outage_max}').
  - Parameters: record, args
  - Returns: None
- `check_health_thresholds(record, args) -> None` — No function docstring. Raises: SystemExit(f'Tick {tick}: active perturbations {record.get('perturbations_active', 0.0):.0f} exceeds threshold {args.perturbations_active_max}'), SystemExit(f'Tick {tick}: dropped telemetry {record.get('dropped', 0.0):.0f} exceeds threshold {args.telemetry_dropped_max}'), SystemExit(f'Tick {tick}: duration_ms {record['duration_ms']:.2f} exceeds threshold {args.tick_duration_max}'), SystemExit(f'Tick {tick}: employment exit queue {record.get('exit_queue', 0.0):.0f} exceeds threshold {args.exit_queue_max}'), SystemExit(f'Tick {tick}: pending perturbations {record.get('perturbations_pending', 0.0):.0f} exceeds threshold {args.perturbations_pending_max}'), SystemExit(f'Tick {tick}: telemetry queue {record.get('queue', 0.0):.0f} exceeds threshold {args.telemetry_queue_max}').
  - Parameters: record, args
  - Returns: None
- `main(args) -> None` — No function docstring. Side effects: stdout. Raises: re-raise.
  - Parameters: args
  - Returns: None

### Constants and Configuration
- `MODES` = ["health", "ppo"]
- `REQUIRED_KEYS` = ["batch_entropy_mean", "chat_failure_events", "chat_quality_mean", "chat_success_events", "data_mode", "epoch", "grad_norm", "kl_divergence", "late_help_events", "log_stream_offset", "loss_total", "queue_conflict_events", "queue_conflict_intensity_sum", "reward_advantage_corr", "shared_meal_events", "shift_takeover_events"]
- `OPTIONAL_NUMERIC_KEYS` = ["anneal_bc_accuracy", "anneal_bc_threshold", "anneal_cycle", "anneal_intensity_baseline", "anneal_loss_baseline", "anneal_queue_baseline"]
- `OPTIONAL_BOOL_KEYS` = ["anneal_bc_passed", "anneal_intensity_flag", "anneal_loss_flag", "anneal_queue_flag"]
- `OPTIONAL_TEXT_KEYS` = ["anneal_dataset", "anneal_stage"]
- `OPTIONAL_EVENT_KEYS` = ["shower_complete_events", "sleep_complete_events", "utility_outage_events"]

### Data Flow
- Inputs: args, argv, follow, interval, line, path, record
- Outputs: Iterator[dict[str, float]], None, argparse.ArgumentParser, argparse.Namespace, dict[str, float]
- Internal interactions: —
- External interactions: _parse_health_line, argparse.ArgumentParser, build_parser, check_health_thresholds, check_thresholds, handle.readline, handle.seek, handle.tell, json.dumps, json.loads, key.strip, line.strip, … (16 more)

### Integration Points
- Runtime calls: _parse_health_line, argparse.ArgumentParser, build_parser, check_health_thresholds, check_thresholds, handle.readline, handle.seek, handle.tell, json.dumps, json.loads, key.strip, line.strip, … (16 more)

### Code Quality Notes
- Missing function docstrings: build_parser, parse_args, parse_args_from_list, stream_records, _parse_health_line, stream_health_records, check_thresholds, check_health_thresholds, main


## scripts/validate_affordances.py

**Purpose**: Validate affordance manifest files for schema compliance.
**Dependencies**:
- Standard Library: __future__, argparse, pathlib, sys, typing
- Third-Party: —
- Internal: townlet.config.affordance_manifest, townlet.world.preconditions
**Related modules**: townlet.config.affordance_manifest, townlet.world.preconditions

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring.
  - Parameters: —
  - Returns: argparse.Namespace
- `discover_manifests(inputs) -> List[Path]` — No function docstring. Side effects: filesystem, stdout.
  - Parameters: inputs
  - Returns: List[Path]
- `validate_manifest(path) -> AffordanceManifest` — No function docstring. Raises: RuntimeError(f"Manifest {path} invalid: affordance '{affordance.affordance_id}' preconditions failed to compile ({exc})"), RuntimeError(f'Manifest not found: {path}'), RuntimeError(f'Manifest {path} invalid: {exc}').
  - Parameters: path
  - Returns: AffordanceManifest
- `main() -> int` — No function docstring. Side effects: stdout.
  - Parameters: —
  - Returns: int

### Constants and Configuration
- `DEFAULT_SEARCH_ROOT` = "Path('configs/affordances')"

### Data Flow
- Inputs: inputs, path
- Outputs: AffordanceManifest, List[Path], argparse.Namespace, int
- Internal interactions: —
- External interactions: Path, argparse.ArgumentParser, compile_preconditions, discover_manifests, expanduser, failures.append, load_affordance_manifest, manifests.append, parse_args, parser.add_argument, parser.parse_args, path.is_dir, … (5 more)

### Integration Points
- Runtime calls: Path, argparse.ArgumentParser, compile_preconditions, discover_manifests, expanduser, failures.append, load_affordance_manifest, manifests.append, parse_args, parser.add_argument, parser.parse_args, path.is_dir, … (5 more)

### Code Quality Notes
- Missing function docstrings: parse_args, discover_manifests, validate_manifest, main


## scripts/validate_ppo_telemetry.py

**Purpose**: Validate PPO telemetry NDJSON logs and report baseline drift.
**Dependencies**:
- Standard Library: __future__, argparse, json, math, pathlib, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `parse_args() -> argparse.Namespace` — No function docstring.
  - Parameters: —
  - Returns: argparse.Namespace
- `_ensure_numeric(key, value) -> None` — No function docstring. Raises: ValueError(f"Field '{key}' must be a finite number, got {value!r}").
  - Parameters: key, value
  - Returns: None
- `_load_records(path) -> List[dict[str, object]]` — No function docstring. Raises: ValueError(f'{path}: no telemetry records found'), ValueError(f'{path}:{line_number}: expected JSON object, got {type(payload).__name__}'), ValueError(f'{path}:{line_number}: invalid JSON: {err}').
  - Parameters: path
  - Returns: List[dict[str, object]]
- `_validate_record(record, source) -> None` — No function docstring. Raises: ValueError(f"{source}: field '{key}' must be a string"), ValueError(f'{source}: missing conflict telemetry keys: {sorted(conflict_missing)}'), ValueError(f'{source}: missing required telemetry keys: {sorted(missing)}'), ValueError(f'{source}: telemetry_version 1.1 requires numeric keys: {sorted(numeric_missing)}'), ValueError(f'{source}: telemetry_version 1.1 requires string keys: {sorted(string_missing)}'), ValueError(f'{source}: telemetry_version {version} should not include v1.1-only keys: {sorted(unexpected_v1_1)}').
  - Parameters: record, source
  - Returns: None
- `_load_baseline(path) -> dict[str, float] | None` — No function docstring. Raises: ValueError('Baseline file does not provide recognised baseline_* keys'), ValueError('Baseline file must contain a JSON object').
  - Parameters: path
  - Returns: dict[str, float] | None
- `_relative_delta(delta, base_value) -> float | None` — No function docstring.
  - Parameters: delta, base_value
  - Returns: float | None
- `_report_drift(records, baseline, threshold, include_relative) -> None` — No function docstring. Side effects: stdout. Raises: ValueError(f'Baseline drift exceeds threshold {threshold}: {pairs}').
  - Parameters: records, baseline, threshold, include_relative
  - Returns: None
- `validate_logs(paths, baseline_path, drift_threshold, include_relative) -> None` — No function docstring. Side effects: stdout.
  - Parameters: paths, baseline_path, drift_threshold, include_relative
  - Returns: None
- `main() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- `BASE_REQUIRED_KEYS` = ["adv_mean", "adv_min_std", "adv_std", "adv_zero_std_batches", "clip_fraction", "clip_fraction_max", "clip_triggered_minibatches", "epoch", "grad_norm", "kl_divergence", "loss_entropy", "loss_policy", "loss_total", "loss_value", "lr", "steps", "telemetry_version", "transitions", "updates"]
- `CONFLICT_KEYS` = ["conflict.rivalry_avoid_count_max_avg", "conflict.rivalry_avoid_count_mean_avg", "conflict.rivalry_max_max_avg", "conflict.rivalry_max_mean_avg"]
- `BASELINE_KEYS` = ["baseline_reward_mean", "baseline_reward_sum", "baseline_reward_sum_mean", "baseline_sample_count"]
- `REQUIRED_V1_1_NUMERIC_KEYS` = ["batch_entropy_mean", "batch_entropy_std", "cycle_id", "epoch_duration_sec", "grad_norm_max", "kl_divergence_max", "log_stream_offset", "queue_conflict_events", "queue_conflict_intensity_sum", "reward_advantage_corr", "rollout_ticks"]
- `REQUIRED_V1_1_STRING_KEYS` = ["data_mode"]

### Data Flow
- Inputs: base_value, baseline, baseline_path, delta, drift_threshold, include_relative, key, path, paths, record, records, source, threshold, value
- Outputs: List[dict[str, object]], None, argparse.Namespace, dict[str, float] | None, float | None
- Internal interactions: —
- External interactions: _ensure_numeric, _load_baseline, _load_records, _relative_delta, _report_drift, _validate_record, argparse.ArgumentParser, deltas.get, exceeded.items, header.extend, join, json.loads, … (12 more)

### Integration Points
- Runtime calls: _ensure_numeric, _load_baseline, _load_records, _relative_delta, _report_drift, _validate_record, argparse.ArgumentParser, deltas.get, exceeded.items, header.extend, join, json.loads, … (12 more)

### Code Quality Notes
- Missing function docstrings: parse_args, _ensure_numeric, _load_records, _validate_record, _load_baseline, _relative_delta, _report_drift, validate_logs, main


## src/townlet/__init__.py

**Purpose**: Townlet simulation package.
**Dependencies**:
- Standard Library: __future__
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: —

### Integration Points
- None noted.

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/agents/__init__.py

**Purpose**: Agent state models.
**Dependencies**:
- Standard Library: __future__
- Third-Party: relationship_modifiers
- Internal: models
**Related modules**: models

### Classes
- None defined.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: —

### Integration Points
- Third-party libraries: relationship_modifiers

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/agents/models.py

**Purpose**: Agent-related dataclasses and helpers.
**Dependencies**:
- Standard Library: __future__, dataclasses
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- **Personality** (bases: object; decorators: dataclass) — No class docstring.
  - Attributes: extroversion: float = None, forgiveness: float = None, ambition: float = None
  - Methods: None.
- **RelationshipEdge** (bases: object; decorators: dataclass) — No class docstring.
  - Attributes: other_id: str = None, trust: float = None, familiarity: float = None, rivalry: float = None
  - Methods: None.
- **AgentState** (bases: object; decorators: dataclass) — Canonical agent state used across modules.
  - Attributes: agent_id: str = None, needs: dict[str, float] = None, wallet: float = None, personality: Personality = None, relationships: list[RelationshipEdge] = 'field(default_factory=list)'
  - Methods: None.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: —

### Integration Points
- None noted.

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/agents/relationship_modifiers.py

**Purpose**: Relationship delta adjustment helpers respecting personality flags.
**Dependencies**:
- Standard Library: __future__, dataclasses, typing
- Third-Party: —
- Internal: townlet.agents.models
**Related modules**: townlet.agents.models

### Classes
- **RelationshipDelta** (bases: object; decorators: dataclass(frozen=True)) — Represents trust/familiarity/rivalry deltas for a single event.
  - Attributes: trust: float = 0.0, familiarity: float = 0.0, rivalry: float = 0.0
  - Methods: None.

### Functions
- `apply_personality_modifiers() -> RelationshipDelta` — Adjust ``delta`` based on personality traits when enabled.  When ``enabled`` is ``False`` the input delta is returned unchanged so tests can assert parity with the pre-personality behaviour. This hook allows the relationship system to opt-in once the feature flag is flipped.
  - Parameters: —
  - Returns: RelationshipDelta
- `_apply_forgiveness(value, forgiveness) -> float` — No function docstring.
  - Parameters: value, forgiveness
  - Returns: float
- `_apply_extroversion(value, extroversion) -> float` — No function docstring.
  - Parameters: value, extroversion
  - Returns: float
- `_apply_ambition(value, ambition) -> float` — No function docstring.
  - Parameters: value, ambition
  - Returns: float
- `_clamp(value, low, high) -> float` — No function docstring.
  - Parameters: value, low, high
  - Returns: float

### Constants and Configuration
- None.

### Data Flow
- Inputs: ambition, extroversion, forgiveness, high, low, value
- Outputs: RelationshipDelta, float
- Internal interactions: —
- External interactions: RelationshipDelta, _apply_ambition, _apply_extroversion, _apply_forgiveness, _clamp

### Integration Points
- Runtime calls: RelationshipDelta, _apply_ambition, _apply_extroversion, _apply_forgiveness, _clamp

### Code Quality Notes
- Missing function docstrings: _apply_forgiveness, _apply_extroversion, _apply_ambition, _clamp


## src/townlet/config/__init__.py

**Purpose**: Config utilities for Townlet.
**Dependencies**:
- Standard Library: __future__
- Third-Party: loader
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: —

### Integration Points
- Third-party libraries: loader

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/config/affordance_manifest.py

**Purpose**: Utilities for validating affordance manifest files.
**Dependencies**:
- Standard Library: __future__, collections.abc, dataclasses, hashlib, logging, pathlib
- Third-Party: yaml
- Internal: —
**Related modules**: —

### Classes
- **ManifestObject** (bases: object; decorators: dataclass(frozen=True)) — Represents an interactive object entry from the manifest.
  - Attributes: object_id: str = None, object_type: str = None, stock: dict[str, int] = None, position: tuple[int, int] | None = None
  - Methods: None.
- **ManifestAffordance** (bases: object; decorators: dataclass(frozen=True)) — Represents an affordance definition with preconditions and hooks.
  - Attributes: affordance_id: str = None, object_type: str = None, duration: int = None, effects: dict[str, float] = None, preconditions: list[str] = None, hooks: dict[str, list[str]] = None
  - Methods: None.
- **AffordanceManifest** (bases: object; decorators: dataclass(frozen=True)) — Normalised manifest contents and checksum metadata.
  - Attributes: path: Path = None, checksum: str = None, objects: list[ManifestObject] = None, affordances: list[ManifestAffordance] = None
  - Methods:
    - `object_count(self) -> int` — No method docstring.
    - `affordance_count(self) -> int` — No method docstring.
- **AffordanceManifestError** (bases: ValueError; decorators: —) — Raised when an affordance manifest fails validation.
  - Methods: None.

### Functions
- `load_affordance_manifest(path) -> AffordanceManifest` — Load and validate an affordance manifest, returning structured entries.  Args:     path: Path to the YAML manifest file.  Raises:     FileNotFoundError: If the manifest does not exist.     AffordanceManifestError: If schema validation or duplicate detection fails. Raises: AffordanceManifestError(f"Entry {index} in {path} has unsupported type '{entry_type}'"), AffordanceManifestError(f'Affordance manifest {path} must be a list of entries'), AffordanceManifestError(f'Entry {index} in {path} must be a mapping, found {type(entry).__name__}'), FileNotFoundError(f'Affordance manifest not found: {path}').
  - Parameters: path
  - Returns: AffordanceManifest
- `_parse_object_entry(entry, path, index) -> ManifestObject` — No function docstring. Raises: AffordanceManifestError(f"Entry {index} ({object_id}) in {path} has invalid 'stock' field"), AffordanceManifestError(f"Entry {index} ({object_id}) in {path} has negative stock for '{key}'"), AffordanceManifestError(f"Entry {index} ({object_id}) in {path} has non-integer stock for '{key}'"), AffordanceManifestError(f'Entry {index} ({object_id}) in {path} has non-string stock key').
  - Parameters: entry, path, index
  - Returns: ManifestObject
- `_parse_affordance_entry(entry, path, index) -> ManifestAffordance` — No function docstring. Raises: AffordanceManifestError(f"Entry {index} ({affordance_id}) in {path} has invalid 'hooks' mapping"), AffordanceManifestError(f"Entry {index} ({affordance_id}) in {path} has non-numeric effect for '{name}'"), AffordanceManifestError(f"Entry {index} ({affordance_id}) in {path} has unknown hook '{key}'"), AffordanceManifestError(f"Entry {index} ({affordance_id}) in {path} is missing 'duration'"), AffordanceManifestError(f"Entry {index} ({affordance_id}) in {path} must define non-empty 'effects'"), AffordanceManifestError(f'Entry {index} ({affordance_id}) in {path} has non-integer duration'), AffordanceManifestError(f'Entry {index} ({affordance_id}) in {path} has non-string effect name'), AffordanceManifestError(f'Entry {index} ({affordance_id}) in {path} must have duration > 0').
  - Parameters: entry, path, index
  - Returns: ManifestAffordance
- `_parse_position(value) -> tuple[int, int] | None` — No function docstring. Raises: AffordanceManifestError(f'Entry {index} ({entry_id}) in {path} has invalid position (expected [x, y])'), AffordanceManifestError(f'Entry {index} ({entry_id}) in {path} has non-integer position coordinates').
  - Parameters: value
  - Returns: tuple[int, int] | None
- `_parse_string_list(value) -> list[str]` — No function docstring. Raises: AffordanceManifestError(f"Entry {index} ({entry_id}) in {path} has empty string in '{field}'"), AffordanceManifestError(f"Entry {index} ({entry_id}) in {path} has invalid '{field}' list"), AffordanceManifestError(f"Entry {index} ({entry_id}) in {path} has non-string value in '{field}'").
  - Parameters: value
  - Returns: list[str]
- `_require_string(entry, field, path, index) -> str` — No function docstring. Raises: AffordanceManifestError(f"Entry {index} in {path} is missing required field '{field}'"), AffordanceManifestError(f"Entry {index} in {path} must provide non-empty string for '{field}'").
  - Parameters: entry, field, path, index
  - Returns: str
- `_ensure_unique(entry_id, seen, path, index) -> None` — No function docstring. Raises: AffordanceManifestError(f"Entry {index} in {path} has duplicate id '{entry_id}'").
  - Parameters: entry_id, seen, path, index
  - Returns: None

### Constants and Configuration
- `_ALLOWED_HOOK_KEYS` = ["after", "before", "fail"]

### Data Flow
- Inputs: entry, entry_id, field, index, path, seen, value
- Outputs: AffordanceManifest, ManifestAffordance, ManifestObject, None, list[str], str, tuple[int, int] | None
- Internal interactions: —
- External interactions: AffordanceManifest, AffordanceManifestError, ManifestAffordance, ManifestObject, _ensure_unique, _parse_affordance_entry, _parse_object_entry, _parse_position, _parse_string_list, _require_string, affordances.append, effects_raw.items, … (16 more)

### Integration Points
- Runtime calls: AffordanceManifest, AffordanceManifestError, ManifestAffordance, ManifestObject, _ensure_unique, _parse_affordance_entry, _parse_object_entry, _parse_position, _parse_string_list, _require_string, affordances.append, effects_raw.items, … (16 more)
- Third-party libraries: yaml

### Code Quality Notes
- Missing function docstrings: _parse_object_entry, _parse_affordance_entry, _parse_position, _parse_string_list, _require_string, _ensure_unique
- Missing method docstrings: AffordanceManifest.object_count, AffordanceManifest.affordance_count


## src/townlet/config/loader.py

**Purpose**: Configuration loader and validation layer.
**Dependencies**:
- Standard Library: __future__, collections.abc, enum, importlib, pathlib, re, typing
- Third-Party: pydantic, yaml
- Internal: —
**Related modules**: —

### Classes
- **StageFlags** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: relationships: RelationshipStage = 'OFF', social_rewards: SocialRewardStage = 'OFF'
  - Methods: None.
- **SystemFlags** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: lifecycle: LifecycleToggle = 'on', observations: ObservationVariant = 'hybrid'
  - Methods: None.
- **TrainingFlags** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: curiosity: CuriosityToggle = 'phase_A'
  - Methods: None.
- **PolicyRuntimeConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: option_commit_ticks: int = 'Field(15, ge=0, le=100000)'
  - Methods: None.
- **ConsoleFlags** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: mode: ConsoleMode = 'viewer'
  - Methods: None.
- **FeatureFlags** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: stages: StageFlags = None, systems: SystemFlags = None, training: TrainingFlags = None, console: ConsoleFlags = None, relationship_modifiers: bool = False
  - Methods: None.
- **NeedsWeights** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: hunger: float = 'Field(1.0, ge=0.5, le=2.0)', hygiene: float = 'Field(0.6, ge=0.2, le=1.0)', energy: float = 'Field(0.8, ge=0.4, le=1.5)'
  - Methods: None.
- **SocialRewardWeights** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: C1_chat_base: float = 'Field(0.01, ge=0.0, le=0.05)', C1_coeff_trust: float = 'Field(0.3, ge=0.0, le=1.0)', C1_coeff_fam: float = 'Field(0.2, ge=0.0, le=1.0)', C2_avoid_conflict: float = 'Field(0.005, ge=0.0, le=0.02)'
  - Methods: None.
- **RewardClips** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: clip_per_tick: float = 'Field(0.2, ge=0.01, le=1.0)', clip_per_episode: float = 'Field(50, ge=1, le=200)', no_positive_within_death_ticks: int = 'Field(10, ge=0, le=200)'
  - Methods: None.
- **RewardsConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: needs_weights: NeedsWeights = None, decay_rates: dict[str, float] = "Field(default_factory=lambda: {'hunger': 0.01, 'hygiene': 0.005, 'energy': 0.008})", punctuality_bonus: float = 'Field(0.05, ge=0.0, le=0.1)', wage_rate: float = 'Field(0.01, ge=0.0, le=0.05)', survival_tick: float = 'Field(0.002, ge=0.0, le=0.01)', faint_penalty: float = 'Field(-1.0, ge=-5.0, le=0.0)', eviction_penalty: float = 'Field(-2.0, ge=-5.0, le=0.0)', social: SocialRewardWeights = 'SocialRewardWeights()', clip: RewardClips = 'RewardClips()'
  - Methods:
    - `_sanity_check_punctuality(self) -> 'RewardsConfig'` — No method docstring. Raises: ValueError('Punctuality bonus must remain below hunger weight (see REQUIREMENTS#6).').
- **ShapingConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: use_potential: bool = True
  - Methods: None.
- **CuriosityConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: phase_A_weight: float = 'Field(0.02, ge=0.0, le=0.1)', decay_by_milestone: Literal['M2', 'never'] = 'M2'
  - Methods: None.
- **QueueFairnessConfig** (bases: BaseModel; decorators: —) — Queue fairness tuning parameters (see REQUIREMENTS#5).
  - Attributes: cooldown_ticks: int = 'Field(60, ge=0, le=600)', ghost_step_after: int = 'Field(3, ge=0, le=100)', age_priority_weight: float = 'Field(0.1, ge=0.0, le=1.0)'
  - Methods: None.
- **RivalryConfig** (bases: BaseModel; decorators: —) — Conflict/rivalry tuning knobs (see REQUIREMENTS#5).
  - Attributes: increment_per_conflict: float = 'Field(0.15, ge=0.0, le=1.0)', decay_per_tick: float = 'Field(0.005, ge=0.0, le=1.0)', min_value: float = 'Field(0.0, ge=0.0, le=1.0)', max_value: float = 'Field(1.0, ge=0.0, le=1.0)', avoid_threshold: float = 'Field(0.7, ge=0.0, le=1.0)', eviction_threshold: float = 'Field(0.05, ge=0.0, le=1.0)', max_edges: int = 'Field(6, ge=1, le=32)', ghost_step_boost: float = 'Field(1.5, ge=0.0, le=5.0)', handover_boost: float = 'Field(0.4, ge=0.0, le=5.0)', queue_length_boost: float = 'Field(0.25, ge=0.0, le=2.0)'
  - Methods:
    - `_validate_ranges(self) -> 'RivalryConfig'` — No method docstring. Raises: ValueError('rivalry.avoid_threshold must lie within [min_value, max_value]'), ValueError('rivalry.eviction_threshold must lie within [min_value, max_value]'), ValueError('rivalry.min_value must be <= max_value').
- **ConflictConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: rivalry: RivalryConfig = 'RivalryConfig()'
  - Methods: None.
- **PPOConfig** (bases: BaseModel; decorators: —) — Config for PPO training hyperparameters.
  - Attributes: learning_rate: float = 'Field(0.0003, gt=0.0)', clip_param: float = 'Field(0.2, ge=0.0, le=1.0)', value_loss_coef: float = 'Field(0.5, ge=0.0)', entropy_coef: float = 'Field(0.01, ge=0.0)', num_epochs: int = 'Field(4, ge=1, le=64)', mini_batch_size: int = 'Field(32, ge=1)', gae_lambda: float = 'Field(0.95, ge=0.0, le=1.0)', gamma: float = 'Field(0.99, ge=0.0, le=1.0)', max_grad_norm: float = 'Field(0.5, ge=0.0)', value_clip: float = 'Field(0.2, ge=0.0, le=1.0)', advantage_normalization: bool = True, num_mini_batches: int = 'Field(4, ge=1, le=1024)'
  - Methods: None.
- **EmbeddingAllocatorConfig** (bases: BaseModel; decorators: —) — Embedding slot reuse guardrails (see REQUIREMENTS#3).
  - Attributes: cooldown_ticks: int = 'Field(2000, ge=0, le=10000)', reuse_warning_threshold: float = 'Field(0.05, ge=0.0, le=0.5)', log_forced_reuse: bool = True, max_slots: int = 'Field(64, ge=1, le=256)'
  - Methods: None.
- **HybridObservationConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: local_window: int = 'Field(11, ge=3)', include_targets: bool = False, time_ticks_per_day: int = 'Field(1440, ge=1)'
  - Methods:
    - `_validate_window(self) -> 'HybridObservationConfig'` — No method docstring. Raises: ValueError('observations.hybrid.local_window must be odd to center on agent').
- **SocialSnippetConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: top_friends: int = 'Field(2, ge=0, le=8)', top_rivals: int = 'Field(2, ge=0, le=8)', embed_dim: int = 'Field(8, ge=1, le=32)', include_aggregates: bool = True
  - Methods:
    - `_validate_totals(self) -> 'SocialSnippetConfig'` — No method docstring. Raises: ValueError('Sum of top_friends and top_rivals must be <= 8 for tensor budget').
- **ObservationsConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: hybrid: HybridObservationConfig = 'HybridObservationConfig()', social_snippet: SocialSnippetConfig = 'SocialSnippetConfig()'
  - Methods: None.
- **StarvationCanaryConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: window_ticks: int = 'Field(1000, ge=1, le=100000)', max_incidents: int = 'Field(0, ge=0, le=10000)', hunger_threshold: float = 'Field(0.05, ge=0.0, le=1.0)', min_duration_ticks: int = 'Field(30, ge=1, le=10000)'
  - Methods: None.
- **RewardVarianceCanaryConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: window_ticks: int = 'Field(1000, ge=1, le=100000)', max_variance: float = 'Field(0.25, ge=0.0)', min_samples: int = 'Field(20, ge=1, le=100000)'
  - Methods: None.
- **OptionThrashCanaryConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: window_ticks: int = 'Field(600, ge=1, le=100000)', max_switch_rate: float = 'Field(0.25, ge=0.0, le=10.0)', min_samples: int = 'Field(10, ge=1, le=100000)'
  - Methods: None.
- **PromotionGateConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: required_passes: int = 'Field(2, ge=1, le=10)', window_ticks: int = 'Field(1000, ge=1, le=100000)', allowed_alerts: tuple[str, ...] = [], model_config: Any = "ConfigDict(extra='forbid')"
  - Methods:
    - `_coerce_allowed(cls, value) -> object` — No method docstring.
    - `_normalise(self) -> 'PromotionGateConfig'` — No method docstring.
- **LifecycleConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: respawn_delay_ticks: int = 'Field(0, ge=0, le=100000)'
  - Methods: None.
- **StabilityConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: affordance_fail_threshold: int = 'Field(5, ge=0, le=100)', lateness_threshold: int = 'Field(3, ge=0, le=100)', starvation: StarvationCanaryConfig = 'StarvationCanaryConfig()', reward_variance: RewardVarianceCanaryConfig = 'RewardVarianceCanaryConfig()', option_thrash: OptionThrashCanaryConfig = 'OptionThrashCanaryConfig()', promotion: PromotionGateConfig = 'PromotionGateConfig()'
  - Methods:
    - `as_dict(self) -> dict[str, object]` — No method docstring.
- **IntRange** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: min: int = 'Field(ge=0)', max: int = 'Field(ge=0)', model_config: Any = "ConfigDict(extra='forbid')"
  - Methods:
    - `_coerce(cls, value) -> dict[str, int]` — No method docstring. Raises: TypeError(f'Unsupported range value: {value!r}'), ValueError('Range list must contain exactly two values').
    - `_validate_bounds(self) -> 'IntRange'` — No method docstring. Raises: ValueError('Range max must be >= min').
- **FloatRange** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: min: float = None, max: float = None, model_config: Any = "ConfigDict(extra='forbid')"
  - Methods:
    - `_coerce(cls, value) -> dict[str, float]` — No method docstring. Raises: TypeError(f'Unsupported float range value: {value!r}'), ValueError('Float range list must contain exactly two values').
    - `_validate_bounds(self) -> 'FloatRange'` — No method docstring. Raises: ValueError('Float range max must be >= min').
- **PerturbationKind** (bases: str, Enum; decorators: —) — No class docstring.
  - Attributes: PRICE_SPIKE: Any = 'price_spike', BLACKOUT: Any = 'blackout', OUTAGE: Any = 'outage', ARRANGED_MEET: Any = 'arranged_meet'
  - Methods: None.
- **BasePerturbationEventConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: kind: PerturbationKind = None, probability_per_day: float = "Field(0.0, ge=0.0, alias='prob_per_day')", cooldown_ticks: int = 'Field(0, ge=0)', duration: IntRange = 'Field(default_factory=lambda: IntRange(min=0, max=0))', model_config: Any = "ConfigDict(extra='forbid', populate_by_name=True)"
  - Methods:
    - `_normalise_duration(cls, values) -> dict[str, object]` — No method docstring.
- **PriceSpikeEventConfig** (bases: BasePerturbationEventConfig; decorators: —) — No class docstring.
  - Attributes: kind: Literal[PerturbationKind.PRICE_SPIKE] = 'PerturbationKind.PRICE_SPIKE', magnitude: FloatRange = 'Field(default_factory=lambda: FloatRange(min=1.0, max=1.0))', targets: list[str] = 'Field(default_factory=list)'
  - Methods:
    - `_normalise_magnitude(cls, values) -> dict[str, object]` — No method docstring.
- **BlackoutEventConfig** (bases: BasePerturbationEventConfig; decorators: —) — No class docstring.
  - Attributes: kind: Literal[PerturbationKind.BLACKOUT] = 'PerturbationKind.BLACKOUT', utility: Literal['power'] = 'power'
  - Methods: None.
- **OutageEventConfig** (bases: BasePerturbationEventConfig; decorators: —) — No class docstring.
  - Attributes: kind: Literal[PerturbationKind.OUTAGE] = 'PerturbationKind.OUTAGE', utility: Literal['water'] = 'water'
  - Methods: None.
- **ArrangedMeetEventConfig** (bases: BasePerturbationEventConfig; decorators: —) — No class docstring.
  - Attributes: kind: Literal[PerturbationKind.ARRANGED_MEET] = 'PerturbationKind.ARRANGED_MEET', target: str = "Field(default='top_rivals')", location: str = "Field(default='cafe')", max_participants: int = 'Field(2, ge=2)'
  - Methods: None.
- **PerturbationSchedulerConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: max_concurrent_events: int = 'Field(1, ge=1)', global_cooldown_ticks: int = 'Field(0, ge=0)', per_agent_cooldown_ticks: int = 'Field(0, ge=0)', grace_window_ticks: int = 'Field(60, ge=0)', window_ticks: int = 'Field(1440, ge=1)', max_events_per_window: int = 'Field(1, ge=0)', events: dict[str, PerturbationEventConfig] = 'Field(default_factory=dict)', model_config: Any = "ConfigDict(extra='allow', populate_by_name=True)"
  - Methods:
    - `event_list(self) -> list[PerturbationEventConfig]` — No method docstring.
- **AffordanceRuntimeConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: factory: str | None = None, instrumentation: Literal['off', 'timings'] = 'off', options: dict[str, object] = 'Field(default_factory=dict)', model_config: Any = "ConfigDict(extra='allow')"
  - Methods: None.
- **AffordanceConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: affordances_file: str = "Field('configs/affordances/core.yaml')", runtime: AffordanceRuntimeConfig = 'AffordanceRuntimeConfig()'
  - Methods: None.
- **EmploymentConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: grace_ticks: int = 'Field(5, ge=0, le=120)', absent_cutoff: int = 'Field(30, ge=0, le=600)', absence_slack: int = 'Field(20, ge=0, le=600)', late_tick_penalty: float = 'Field(0.005, ge=0.0, le=1.0)', absence_penalty: float = 'Field(0.2, ge=0.0, le=5.0)', max_absent_shifts: int = 'Field(3, ge=0, le=20)', attendance_window: int = 'Field(3, ge=1, le=14)', daily_exit_cap: int = 'Field(2, ge=0, le=50)', exit_queue_limit: int = 'Field(8, ge=0, le=100)', exit_review_window: int = 'Field(1440, ge=1, le=100000)', enforce_job_loop: bool = False
  - Methods: None.
- **BehaviorConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: hunger_threshold: float = 'Field(0.4, ge=0.0, le=1.0)', hygiene_threshold: float = 'Field(0.4, ge=0.0, le=1.0)', energy_threshold: float = 'Field(0.4, ge=0.0, le=1.0)', job_arrival_buffer: int = 'Field(20, ge=0)'
  - Methods: None.
- **SocialRewardScheduleEntry** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: cycle: int = 'Field(0, ge=0)', stage: SocialRewardStage = None
  - Methods: None.
- **BCTrainingSettings** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: manifest: Path | None = None, learning_rate: float = 'Field(0.001, gt=0.0)', batch_size: int = 'Field(64, ge=1)', epochs: int = 'Field(10, ge=1)', weight_decay: float = 'Field(0.0, ge=0.0)', device: str = 'cpu'
  - Methods: None.
- **AnnealStage** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: cycle: int = 'Field(0, ge=0)', mode: Literal['bc', 'ppo'] = 'ppo', epochs: int = 'Field(1, ge=1)', bc_weight: float = 'Field(1.0, ge=0.0, le=1.0)'
  - Methods: None.
- **NarrationThrottleConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: global_cooldown_ticks: int = 'Field(30, ge=0, le=10000)', category_cooldown_ticks: dict[str, int] = 'Field(default_factory=dict)', dedupe_window_ticks: int = 'Field(20, ge=0, le=10000)', global_window_ticks: int = 'Field(600, ge=1, le=10000)', global_window_limit: int = 'Field(10, ge=1, le=1000)', priority_categories: list[str] = 'Field(default_factory=list)'
  - Methods:
    - `get_category_cooldown(self, category) -> int` — No method docstring.
- **TelemetryRetryPolicy** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: max_attempts: int = 'Field(default=3, ge=0, le=10)', backoff_seconds: float = 'Field(default=0.5, ge=0.0, le=30.0)'
  - Methods: None.
- **TelemetryBufferConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: max_batch_size: int = 'Field(default=32, ge=1, le=500)', max_buffer_bytes: int = 'Field(default=256000, ge=1024, le=16777216)', flush_interval_ticks: int = 'Field(default=1, ge=1, le=10000)'
  - Methods: None.
- **TelemetryTransportConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: type: TelemetryTransportType = 'stdout', endpoint: str | None = None, file_path: Path | None = None, connect_timeout_seconds: float = 'Field(default=5.0, ge=0.0, le=60.0)', send_timeout_seconds: float = 'Field(default=1.0, ge=0.0, le=60.0)', retry: TelemetryRetryPolicy = 'TelemetryRetryPolicy()', buffer: TelemetryBufferConfig = 'TelemetryBufferConfig()', worker_poll_seconds: float = 'Field(default=0.5, ge=0.01, le=10.0)'
  - Methods:
    - `_validate_transport(self) -> 'TelemetryTransportConfig'` — No method docstring. Raises: ValueError("telemetry.transport.endpoint is required when type is 'tcp'"), ValueError("telemetry.transport.file_path is required when type is 'file'"), ValueError('telemetry.transport.endpoint is not supported for stdout transport'), ValueError('telemetry.transport.file_path must be omitted for stdout transport'), ValueError('telemetry.transport.file_path must be omitted for tcp transport'), ValueError('telemetry.transport.file_path must not be blank'), ValueError(f'Unsupported telemetry transport type: {transport_type}').
- **TelemetryConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: narration: NarrationThrottleConfig = 'NarrationThrottleConfig()', transport: TelemetryTransportConfig = 'TelemetryTransportConfig()'
  - Methods: None.
- **ConsoleAuthTokenConfig** (bases: BaseModel; decorators: —) — Configuration entry for a single console authentication token.
  - Attributes: label: str | None = None, role: ConsoleMode = 'viewer', token: str | None = None, token_env: str | None = None
  - Methods:
    - `_validate_token_source(self) -> 'ConsoleAuthTokenConfig'` — No method docstring. Raises: ValueError("console.auth.tokens entries must define exactly one of 'token' or 'token_env'"), ValueError('console.auth.tokens.token must not be blank'), ValueError('console.auth.tokens.token_env must not be blank').
- **ConsoleAuthConfig** (bases: BaseModel; decorators: —) — Authentication settings for console and telemetry command ingress.
  - Attributes: enabled: bool = False, require_auth_for_viewer: bool = True, tokens: list[ConsoleAuthTokenConfig] = 'Field(default_factory=list)'
  - Methods:
    - `_validate_tokens(self) -> 'ConsoleAuthConfig'` — No method docstring. Raises: ValueError('console.auth.tokens must be provided when auth is enabled').
- **SnapshotStorageConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: root: Path = "Field(default=Path('snapshots'))"
  - Methods:
    - `_validate_root(self) -> 'SnapshotStorageConfig'` — No method docstring. Raises: ValueError('snapshot.storage.root must not be empty').
- **SnapshotAutosaveConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: cadence_ticks: int | None = 'Field(default=None, ge=1)', retain: int = 'Field(default=3, ge=1, le=1000)'
  - Methods:
    - `_validate_cadence(self) -> 'SnapshotAutosaveConfig'` — No method docstring. Raises: ValueError('snapshot.autosave.cadence_ticks must be at least 100 ticks when enabled').
- **SnapshotIdentityConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: policy_hash: str | None = None, policy_artifact: Path | None = None, observation_variant: ObservationVariant | Literal['infer'] = 'infer', anneal_ratio: float | None = 'Field(default=None, ge=0.0, le=1.0)', _HEX40: Any = "re.compile('^[0-9a-fA-F]{40}$')", _HEX64: Any = "re.compile('^[0-9a-fA-F]{64}$')", _BASE64: Any = "re.compile('^[A-Za-z0-9+/=]{32,88}$')"
  - Methods:
    - `_validate_policy_hash(self) -> 'SnapshotIdentityConfig'` — No method docstring. Raises: ValueError('snapshot.identity.policy_hash must be a 40/64-char hex or base64-encoded digest'), ValueError('snapshot.identity.policy_hash must not be blank if provided').
    - `_validate_variant(self) -> 'SnapshotIdentityConfig'` — No method docstring. Raises: ValueError("snapshot.identity.observation_variant must be one of %s or 'infer'" % sorted(supported)).
- **SnapshotMigrationsConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: handlers: dict[str, str] = 'Field(default_factory=dict)', auto_apply: bool = False, allow_minor: bool = False
  - Methods:
    - `_validate_handlers(self) -> 'SnapshotMigrationsConfig'` — No method docstring. Raises: ValueError('snapshot.migrations.handlers keys must not be empty'), ValueError('snapshot.migrations.handlers values must not be empty').
- **SnapshotGuardrailsConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: require_exact_config: bool = True, allow_downgrade: bool = False, allowed_paths: list[Path] = 'Field(default_factory=list)'
  - Methods: None.
- **SnapshotConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: storage: SnapshotStorageConfig = 'SnapshotStorageConfig()', autosave: SnapshotAutosaveConfig = 'SnapshotAutosaveConfig()', identity: SnapshotIdentityConfig = 'SnapshotIdentityConfig()', migrations: SnapshotMigrationsConfig = 'SnapshotMigrationsConfig()', guardrails: SnapshotGuardrailsConfig = 'SnapshotGuardrailsConfig()'
  - Methods:
    - `_validate_observation_override(self) -> 'SnapshotConfig'` — No method docstring. Raises: ValueError("snapshot.identity.observation_variant must be one of ['hybrid', 'full', 'compact', 'infer']").
- **TrainingConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: source: TrainingSource = 'replay', rollout_ticks: int = 'Field(100, ge=0)', rollout_auto_seed_agents: bool = False, replay_manifest: Path | None = None, social_reward_stage_override: SocialRewardStage | None = None, social_reward_schedule: list['SocialRewardScheduleEntry'] = 'Field(default_factory=list)', bc: BCTrainingSettings = 'BCTrainingSettings()', anneal_schedule: list[AnnealStage] = 'Field(default_factory=list)', anneal_accuracy_threshold: float = 'Field(0.9, ge=0.0, le=1.0)', anneal_enable_policy_blend: bool = False
  - Methods: None.
- **JobSpec** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: start_tick: int = 0, end_tick: int = 0, wage_rate: float = 0.0, lateness_penalty: float = 0.0, location: tuple[int, int] | None = None
  - Methods: None.
- **SimulationConfig** (bases: BaseModel; decorators: —) — No class docstring.
  - Attributes: config_id: str = None, features: FeatureFlags = None, rewards: RewardsConfig = None, economy: dict[str, float] = "Field(default_factory=lambda: {'meal_cost': 0.4, 'cook_energy_cost': 0.05, 'cook_hygiene_cost': 0.02, 'wage_income': 0.02, 'ingredients_cost': 0.15, 'stove_stock_replenish': 2})", jobs: dict[str, JobSpec] = "Field(default_factory=lambda: {'grocer': JobSpec(start_tick=180, end_tick=360, wage_rate=0.02, lateness_penalty=0.1, location=(0, 0)), 'barista': JobSpec(start_tick=400, end_tick=560, wage_rate=0.025, lateness_penalty=0.12, location=(1, 0))})", shaping: ShapingConfig | None = None, curiosity: CuriosityConfig | None = None, queue_fairness: QueueFairnessConfig = 'QueueFairnessConfig()', conflict: ConflictConfig = 'ConflictConfig()', ppo: PPOConfig | None = None, training: TrainingConfig = 'TrainingConfig()', embedding_allocator: EmbeddingAllocatorConfig = 'EmbeddingAllocatorConfig()', … (12 more)
  - Methods:
    - `_validate_observation_variant(self) -> 'SimulationConfig'` — No method docstring. Raises: ValueError("Observation variant '%s' is not supported yet; supported variants: %s" % (variant, sorted(supported))).
    - `observation_variant(self) -> ObservationVariant` — No method docstring.
    - `require_observation_variant(self, expected) -> None` — No method docstring. Raises: ValueError('Observation variant mismatch: expected %s, got %s' % (expected, self.observation_variant)).
    - `snapshot_root(self) -> Path` — No method docstring. Side effects: filesystem.
    - `snapshot_allowed_roots(self) -> tuple[Path, ...]` — No method docstring. Side effects: filesystem.
    - `build_snapshot_identity(self) -> dict[str, object]` — No method docstring.
    - `register_snapshot_migrations(self) -> None` — No method docstring. Raises: AttributeError(f"Snapshot migration handler '{attribute}' not found in module '{module_name}'"), ImportError(f"Failed to import snapshot migration module '{module_name}'"), ValueError("snapshot.migrations.handlers entries must use 'module:function' format").

### Functions
- `load_config(path) -> SimulationConfig` — Load and validate a Townlet YAML configuration file. Raises: FileNotFoundError(path), ValueError(header + str(exc)).
  - Parameters: path
  - Returns: SimulationConfig

### Constants and Configuration
- None.

### Data Flow
- Inputs: path
- Outputs: SimulationConfig
- Internal interactions: —
- External interactions: Path, SimulationConfig.model_validate, handler_path.partition, handlers.items, importlib.import_module, model_validator, object.__setattr__, path.exists, path.expanduser, path.read_text, register_migration, resolve, … (19 more)

### Integration Points
- Runtime calls: Path, SimulationConfig.model_validate, handler_path.partition, handlers.items, importlib.import_module, model_validator, object.__setattr__, path.exists, path.expanduser, path.read_text, register_migration, resolve, … (19 more)
- Third-party libraries: pydantic, yaml

### Code Quality Notes
- Missing method docstrings: RewardsConfig._sanity_check_punctuality, RivalryConfig._validate_ranges, HybridObservationConfig._validate_window, SocialSnippetConfig._validate_totals, PromotionGateConfig._coerce_allowed, PromotionGateConfig._normalise, StabilityConfig.as_dict, IntRange._coerce, IntRange._validate_bounds, FloatRange._coerce, FloatRange._validate_bounds, BasePerturbationEventConfig._normalise_duration, PriceSpikeEventConfig._normalise_magnitude, PerturbationSchedulerConfig.event_list, NarrationThrottleConfig.get_category_cooldown, TelemetryTransportConfig._validate_transport, ConsoleAuthTokenConfig._validate_token_source, ConsoleAuthConfig._validate_tokens, SnapshotStorageConfig._validate_root, SnapshotAutosaveConfig._validate_cadence, SnapshotIdentityConfig._validate_policy_hash, SnapshotIdentityConfig._validate_variant, SnapshotMigrationsConfig._validate_handlers, SnapshotConfig._validate_observation_override, SimulationConfig._validate_observation_variant, SimulationConfig.observation_variant, SimulationConfig.require_observation_variant, SimulationConfig.snapshot_root, SimulationConfig.snapshot_allowed_roots, SimulationConfig.build_snapshot_identity, SimulationConfig.register_snapshot_migrations


## src/townlet/console/__init__.py

**Purpose**: Console command handling exports.
**Dependencies**:
- Standard Library: __future__, importlib, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `__getattr__(name) -> Any` — No function docstring. Raises: AttributeError(name).
  - Parameters: name
  - Returns: Any

### Constants and Configuration
- None.

### Data Flow
- Inputs: name
- Outputs: Any
- Internal interactions: —
- External interactions: import_module

### Integration Points
- Runtime calls: import_module

### Code Quality Notes
- Missing function docstrings: __getattr__


## src/townlet/console/auth.py

**Purpose**: Authentication helpers for console and telemetry command ingress.
**Dependencies**:
- Standard Library: __future__, dataclasses, os, secrets, typing
- Third-Party: —
- Internal: townlet.config
**Related modules**: townlet.config

### Classes
- **AuthPrincipal** (bases: object; decorators: dataclass(frozen=True)) — Represents an authenticated caller.
  - Attributes: role: ConsoleMode = None, label: str | None = None
  - Methods: None.
- **ConsoleAuthenticationError** (bases: Exception; decorators: —) — Raised when authentication of a console command fails.
  - Methods:
    - `__init__(self, message, identity) -> None` — No method docstring.
- **ConsoleAuthenticator** (bases: object; decorators: —) — Authenticates console command payloads using configured tokens.
  - Methods:
    - `__init__(self, config) -> None` — No method docstring.
    - `_load_tokens(self, entries) -> None` — No method docstring. Side effects: os. Raises: ValueError('Duplicate console auth token detected'), ValueError(f"console.auth token_env '{env_name}' is not set or is empty").
    - `_to_mapping(command) -> dict[str, Any]` — No method docstring. Raises: TypeError('Console command payload must be a mapping or attribute-based object').
    - `_identity(payload) -> dict[str, str | None]` — No method docstring.
    - `_normalise_role(value) -> ConsoleMode` — No method docstring.
    - `authorise(self, command) -> tuple[dict[str, Any], AuthPrincipal | None]` — No method docstring. Raises: ConsoleAuthenticationError('Invalid authentication token', identity), ConsoleAuthenticationError('Missing authentication token', identity).

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: AuthPrincipal, ConsoleAuthenticationError, __init__, attrs.items, auth_section.get, key.startswith, os.getenv, payload.get, raw.strip, safe_payload.pop, secrets.compare_digest, self._identity, … (5 more)

### Integration Points
- Runtime calls: AuthPrincipal, ConsoleAuthenticationError, __init__, attrs.items, auth_section.get, key.startswith, os.getenv, payload.get, raw.strip, safe_payload.pop, secrets.compare_digest, self._identity, … (5 more)

### Code Quality Notes
- Missing method docstrings: ConsoleAuthenticationError.__init__, ConsoleAuthenticator.__init__, ConsoleAuthenticator._load_tokens, ConsoleAuthenticator._to_mapping, ConsoleAuthenticator._identity, ConsoleAuthenticator._normalise_role, ConsoleAuthenticator.authorise


## src/townlet/console/command.py

**Purpose**: Console command envelope and result helpers.
**Dependencies**:
- Standard Library: __future__, dataclasses, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- **ConsoleCommandError** (bases: RuntimeError; decorators: —) — Raised by handlers when a command should return an error response.
  - Methods:
    - `__init__(self, code, message) -> None` — No method docstring.
- **ConsoleCommandEnvelope** (bases: object; decorators: dataclass(frozen=True)) — Normalised representation of an incoming console command payload.
  - Attributes: name: str = None, args: list[Any] = 'field(default_factory=list)', kwargs: dict[str, Any] = 'field(default_factory=dict)', cmd_id: str | None = None, issuer: str | None = None, mode: str = 'viewer', timestamp_ms: int | None = None, metadata: dict[str, Any] = 'field(default_factory=dict)', raw: Mapping[str, Any] | None = None
  - Methods:
    - `from_payload(cls, payload) -> 'ConsoleCommandEnvelope'` — Parse a payload emitted by the console transport. Raises: ConsoleCommandError('usage', "console command 'args' must be a list"), ConsoleCommandError('usage', "console command 'cmd_id' must be a string"), ConsoleCommandError('usage', "console command 'issuer' must be a string"), ConsoleCommandError('usage', "console command 'kwargs' must be a mapping"), ConsoleCommandError('usage', "console command missing 'name'"), ConsoleCommandError('usage', 'console command metadata must be a mapping'), ConsoleCommandError('usage', 'console command payload must be a mapping'), ConsoleCommandError('usage', 'console command timestamp must be integer milliseconds').
- **ConsoleCommandResult** (bases: object; decorators: dataclass) — Standard response emitted after processing a console command.
  - Attributes: name: str = None, status: str = None, result: dict[str, Any] | None = None, error: dict[str, Any] | None = None, cmd_id: str | None = None, issuer: str | None = None, tick: int | None = None, latency_ms: int | None = None
  - Methods:
    - `ok(cls, envelope, payload) -> 'ConsoleCommandResult'` — No method docstring.
    - `from_error(cls, envelope, code, message) -> 'ConsoleCommandResult'` — No method docstring.
    - `clone(self) -> 'ConsoleCommandResult'` — No method docstring.
    - `to_dict(self) -> dict[str, Any]` — No method docstring.

### Functions
- None defined.

### Constants and Configuration
- `_VALID_MODES` = ["admin", "viewer"]

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: ConsoleCommandError, ConsoleCommandResult, __init__, cls, mapping.get, meta.items, mode_value.lower, raw_kwargs.items

### Integration Points
- Runtime calls: ConsoleCommandError, ConsoleCommandResult, __init__, cls, mapping.get, meta.items, mode_value.lower, raw_kwargs.items

### Code Quality Notes
- Missing method docstrings: ConsoleCommandError.__init__, ConsoleCommandResult.ok, ConsoleCommandResult.from_error, ConsoleCommandResult.clone, ConsoleCommandResult.to_dict


## src/townlet/console/handlers.py

**Purpose**: Console validation scaffolding.
**Dependencies**:
- Standard Library: __future__, dataclasses, json, pathlib, typing
- Third-Party: —
- Internal: townlet.snapshots, townlet.stability.promotion
**Related modules**: townlet.snapshots, townlet.stability.promotion

### Classes
- **ConsoleCommand** (bases: object; decorators: dataclass) — Represents a parsed console command ready for execution.
  - Attributes: name: str = None, args: tuple[object, ...] = None, kwargs: dict[str, object] = None
  - Methods: None.
- **ConsoleHandler** (bases: Protocol; decorators: —) — No class docstring.
  - Methods:
    - `__call__(self, command) -> object` — No method docstring.
- **ConsoleRouter** (bases: object; decorators: —) — Routes validated commands to subsystem handlers.
  - Methods:
    - `__init__(self) -> None` — No method docstring.
    - `register(self, name, handler) -> None` — No method docstring.
    - `dispatch(self, command) -> object` — No method docstring. Raises: KeyError(f'Unknown console command: {command.name}').
- **EventStream** (bases: object; decorators: —) — Simple subscriber that records the latest simulation events.
  - Methods:
    - `__init__(self) -> None` — No method docstring.
    - `connect(self, publisher) -> None` — No method docstring.
    - `_record(self, events) -> None` — No method docstring.
    - `latest(self) -> list[dict[str, object]]` — No method docstring.
- **TelemetryBridge** (bases: object; decorators: —) — Provides access to the latest telemetry snapshots for console consumers.
  - Methods:
    - `__init__(self, publisher) -> None` — No method docstring.
    - `snapshot(self) -> dict[str, dict[str, object]]` — No method docstring.

### Functions
- `create_console_router(publisher, world, scheduler, promotion) -> ConsoleRouter` — No function docstring. Side effects: filesystem. Raises: RuntimeError('employment_exit requires world access').
  - Parameters: publisher, world, scheduler, promotion
  - Returns: ConsoleRouter
- `_schema_metadata(publisher) -> tuple[str, str | None]` — No function docstring.
  - Parameters: publisher
  - Returns: tuple[str, str | None]

### Constants and Configuration
- `SUPPORTED_SCHEMA_PREFIX` = '0.9'
- `SUPPORTED_SCHEMA_LABEL` = "f'{SUPPORTED_SCHEMA_PREFIX}.x'"

### Data Flow
- Inputs: promotion, publisher, scheduler, world
- Outputs: ConsoleRouter, tuple[str, str | None]
- Internal interactions: —
- External interactions: ConsoleRouter, Path, SnapshotManager, TelemetryBridge, _apply_release_metadata, _attach_metadata, _is_path_allowed, _parse_snapshot_path, _refresh_promotion_metrics, _require_config, _resolve_snapshot_input, _schema_metadata, … (113 more)

### Integration Points
- Runtime calls: ConsoleRouter, Path, SnapshotManager, TelemetryBridge, _apply_release_metadata, _attach_metadata, _is_path_allowed, _parse_snapshot_path, _refresh_promotion_metrics, _require_config, _resolve_snapshot_input, _schema_metadata, … (113 more)

### Code Quality Notes
- Missing function docstrings: create_console_router, _schema_metadata
- Missing method docstrings: ConsoleHandler.__call__, ConsoleRouter.__init__, ConsoleRouter.register, ConsoleRouter.dispatch, EventStream.__init__, EventStream.connect, EventStream._record, EventStream.latest, TelemetryBridge.__init__, TelemetryBridge.snapshot


## src/townlet/core/__init__.py

**Purpose**: Core orchestration utilities.
**Dependencies**:
- Standard Library: __future__
- Third-Party: sim_loop
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: —

### Integration Points
- Third-party libraries: sim_loop

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/core/sim_loop.py

**Purpose**: Top-level simulation loop wiring.
**Dependencies**:
- Standard Library: __future__, collections.abc, dataclasses, hashlib, importlib, logging, pathlib, random, time, typing
- Third-Party: —
- Internal: townlet.config, townlet.lifecycle.manager, townlet.observations.builder, townlet.policy.runner, townlet.rewards.engine, townlet.scheduler.perturbations, townlet.snapshots, townlet.stability.monitor, townlet.stability.promotion, townlet.telemetry.publisher, townlet.utils, townlet.world.affordances, townlet.world.grid
**Related modules**: townlet.config, townlet.lifecycle.manager, townlet.observations.builder, townlet.policy.runner, townlet.rewards.engine, townlet.scheduler.perturbations, townlet.snapshots, townlet.stability.monitor, townlet.stability.promotion, townlet.telemetry.publisher, townlet.utils, townlet.world.affordances, townlet.world.grid

### Classes
- **TickArtifacts** (bases: object; decorators: dataclass) — Collects per-tick data for logging and testing.
  - Attributes: observations: dict[str, object] = None, rewards: dict[str, float] = None
  - Methods: None.
- **SimulationLoop** (bases: object; decorators: —) — Orchestrates the Townlet simulation tick-by-tick.
  - Methods:
    - `__init__(self, config) -> None` — No method docstring.
    - `_build_components(self) -> None` — No method docstring. Side effects: filesystem.
    - `reset(self) -> None` — Reset the simulation loop to its initial state.
    - `set_anneal_ratio(self, ratio) -> None` — No method docstring.
    - `save_snapshot(self, root) -> Path` — Persist the current world relationships and tick to ``root``. Side effects: filesystem.
    - `load_snapshot(self, path) -> None` — Restore world relationships and tick from the snapshot at ``path``.
    - `run(self, max_ticks) -> Iterable[TickArtifacts]` — Run the loop until `max_ticks` or indefinitely.
    - `step(self) -> TickArtifacts` — No method docstring.
    - `_load_affordance_runtime_factory(self, runtime_config) -> Callable[[WorldState, AffordanceRuntimeContext], DefaultAffordanceRuntime] | None` — No method docstring.
    - `_import_symbol(path) -> None` — No method docstring. Raises: AttributeError(f"Runtime factory '{attribute}' not found in module '{module_name}'"), ValueError(f"Invalid runtime factory path '{path}'. Use 'module:callable' format.").
    - `_derive_seed(self, stream) -> int` — No method docstring.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: LifecycleManager, ObservationBuilder, Path, PerturbationScheduler, PolicyRuntime, PromotionManager, RewardEngine, SnapshotManager, StabilityMonitor, TelemetryPublisher, TickArtifacts, WorldState.from_config, … (86 more)

### Integration Points
- Runtime calls: LifecycleManager, ObservationBuilder, Path, PerturbationScheduler, PolicyRuntime, PromotionManager, RewardEngine, SnapshotManager, StabilityMonitor, TelemetryPublisher, TickArtifacts, WorldState.from_config, … (86 more)

### Code Quality Notes
- Missing method docstrings: SimulationLoop.__init__, SimulationLoop._build_components, SimulationLoop.set_anneal_ratio, SimulationLoop.step, SimulationLoop._load_affordance_runtime_factory, SimulationLoop._import_symbol, SimulationLoop._derive_seed


## src/townlet/lifecycle/__init__.py

**Purpose**: Lifecycle management utilities.
**Dependencies**:
- Standard Library: __future__
- Third-Party: —
- Internal: manager
**Related modules**: manager

### Classes
- None defined.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: —

### Integration Points
- None noted.

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/lifecycle/manager.py

**Purpose**: Agent lifecycle enforcement (exits, spawns, cooldowns).
**Dependencies**:
- Standard Library: __future__, dataclasses, typing
- Third-Party: —
- Internal: townlet.config, townlet.world.grid
**Related modules**: townlet.config, townlet.world.grid

### Classes
- **_RespawnTicket** (bases: object; decorators: dataclass) — No class docstring.
  - Attributes: agent_id: str = None, scheduled_tick: int = None, blueprint: dict[str, Any] = None
  - Methods: None.
- **LifecycleManager** (bases: object; decorators: —) — Centralises lifecycle checks as outlined in the conceptual design snapshot.
  - Methods:
    - `__init__(self, config) -> None` — No method docstring.
    - `evaluate(self, world, tick) -> dict[str, bool]` — Return a map of agent_id -> terminated flag.
    - `finalize(self, world, tick, terminated) -> None` — No method docstring.
    - `process_respawns(self, world, tick) -> None` — No method docstring.
    - `set_respawn_delay(self, ticks) -> None` — No method docstring.
    - `set_mortality_enabled(self, enabled) -> None` — No method docstring.
    - `export_state(self) -> dict[str, int]` — No method docstring.
    - `import_state(self, payload) -> None` — No method docstring.
    - `reset_state(self) -> None` — No method docstring.
    - `termination_reasons(self) -> dict[str, str]` — Return termination reasons captured during the last evaluation.
    - `_evaluate_employment(self, world, tick) -> dict[str, bool]` — No method docstring.
    - `_employment_execute_exit(self, world, agent_id, tick) -> bool` — No method docstring.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: _RespawnTicket, blueprint.get, payload.get, remaining.append, self._employment_execute_exit, self._evaluate_employment, self._pending_respawns.append, self._termination_reasons.setdefault, snapshot.needs.get, terminated.items, terminated.setdefault, terminated.update, … (13 more)

### Integration Points
- Runtime calls: _RespawnTicket, blueprint.get, payload.get, remaining.append, self._employment_execute_exit, self._evaluate_employment, self._pending_respawns.append, self._termination_reasons.setdefault, snapshot.needs.get, terminated.items, terminated.setdefault, terminated.update, … (13 more)

### Code Quality Notes
- Missing method docstrings: LifecycleManager.__init__, LifecycleManager.finalize, LifecycleManager.process_respawns, LifecycleManager.set_respawn_delay, LifecycleManager.set_mortality_enabled, LifecycleManager.export_state, LifecycleManager.import_state, LifecycleManager.reset_state, LifecycleManager._evaluate_employment, LifecycleManager._employment_execute_exit


## src/townlet/observations/__init__.py

**Purpose**: Observation builders and utilities.
**Dependencies**:
- Standard Library: __future__
- Third-Party: —
- Internal: builder
**Related modules**: builder

### Classes
- None defined.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: —

### Integration Points
- None noted.

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/observations/builder.py

**Purpose**: Observation encoding across variants.
**Dependencies**:
- Standard Library: __future__, collections.abc, hashlib, math, typing
- Third-Party: numpy
- Internal: townlet.config
**Related modules**: townlet.config

### Classes
- **ObservationBuilder** (bases: object; decorators: —) — Constructs per-agent observation payloads.
  - Attributes: MAP_CHANNELS: Any = [self, agents, objects, reservations], SHIFT_STATES: Any = [pre_shift, on_time, late, absent, post_shift]
  - Methods:
    - `__init__(self, config) -> None` — No method docstring. Raises: ValueError('Social snippet requires relationships stage enabled').
    - `build_batch(self, world, terminated) -> dict[str, dict[str, np.ndarray]]` — Return a mapping from agent_id to observation payloads.
    - `_encode_common_features(self, features) -> None` — No method docstring.
    - `_encode_rivalry(self, features, world, snapshot) -> None` — No method docstring.
    - `_encode_environmental_flags(self, features, world, snapshot) -> None` — No method docstring.
    - `_encode_path_hint(self, features, world, snapshot) -> None` — No method docstring.
    - `_build_single(self, world, snapshot, slot) -> dict[str, np.ndarray | dict[str, object]]` — No method docstring.
    - `_map_from_view(self, channels, local_view, window, center, snapshot) -> np.ndarray` — No method docstring.
    - `_build_hybrid(self, world, snapshot, slot) -> dict[str, np.ndarray | dict[str, object]]` — No method docstring.
    - `_build_full(self, world, snapshot, slot) -> dict[str, np.ndarray | dict[str, object]]` — No method docstring.
    - `_build_compact(self, world, snapshot, slot) -> dict[str, np.ndarray | dict[str, object]]` — No method docstring.
    - `_build_social_vector(self, world, snapshot) -> np.ndarray` — No method docstring.
    - `_collect_social_slots(self, world, snapshot) -> list[dict[str, float]]` — No method docstring.
    - `_resolve_relationships(self, world, agent_id) -> list[dict[str, float]]` — No method docstring.
    - `_encode_landmarks(self, features, world, snapshot) -> None` — No method docstring.
    - `_encode_relationship(self, entry) -> dict[str, float]` — No method docstring.
    - `_empty_relationship_entry(self) -> dict[str, float]` — No method docstring.
    - `_embed_agent_id(self, other_id) -> np.ndarray` — No method docstring.
    - `_compute_aggregates(self, trust_values, rivalry_values) -> tuple[float, float, float, float]` — No method docstring.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: base_feature_names.extend, base_feature_names.index, channels.index, context.get, cos, data.get, digest, entries.append, entry.get, fallback_entries.append, hashlib.blake2s, int.from_bytes, … (58 more)

### Integration Points
- Runtime calls: base_feature_names.extend, base_feature_names.index, channels.index, context.get, cos, data.get, digest, entries.append, entry.get, fallback_entries.append, hashlib.blake2s, int.from_bytes, … (58 more)
- Third-party libraries: numpy

### Code Quality Notes
- Contains TODO markers.
- Missing method docstrings: ObservationBuilder.__init__, ObservationBuilder._encode_common_features, ObservationBuilder._encode_rivalry, ObservationBuilder._encode_environmental_flags, ObservationBuilder._encode_path_hint, ObservationBuilder._build_single, ObservationBuilder._map_from_view, ObservationBuilder._build_hybrid, ObservationBuilder._build_full, ObservationBuilder._build_compact, ObservationBuilder._build_social_vector, ObservationBuilder._collect_social_slots, ObservationBuilder._resolve_relationships, ObservationBuilder._encode_landmarks, ObservationBuilder._encode_relationship, ObservationBuilder._empty_relationship_entry, ObservationBuilder._embed_agent_id, ObservationBuilder._compute_aggregates


## src/townlet/observations/embedding.py

**Purpose**: Embedding slot allocation with cooldown logging.
**Dependencies**:
- Standard Library: __future__, dataclasses
- Third-Party: —
- Internal: townlet.config
**Related modules**: townlet.config

### Classes
- **_SlotState** (bases: object; decorators: dataclass) — Tracks release metadata for a slot.
  - Attributes: released_at_tick: int | None = None
  - Methods: None.
- **EmbeddingAllocator** (bases: object; decorators: —) — Assigns stable embedding slots to agents with a reuse cooldown.
  - Methods:
    - `__init__(self, config) -> None` — No method docstring.
    - `allocate(self, agent_id, tick) -> int` — Return the embedding slot for the agent, allocating if necessary.
    - `release(self, agent_id, tick) -> None` — Release the slot held by the agent.
    - `has_assignment(self, agent_id) -> bool` — Return whether the allocator still tracks the agent.
    - `metrics(self) -> dict[str, float]` — Expose allocation metrics for telemetry.
    - `export_state(self) -> dict[str, object]` — Serialise allocator bookkeeping for snapshot persistence.
    - `import_state(self, payload) -> None` — Restore allocator bookkeeping from snapshot data.
    - `_select_slot(self, tick) -> tuple[int, bool]` — No method docstring. Raises: RuntimeError('No embedding slots available; increase max_slots').

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: _SlotState, assignments.items, metrics.get, payload.get, self._assignments.get, self._assignments.pop, self._assignments.values, self._available.add, self._available.discard, self._select_slot, self._slot_state.items, self._slot_state.values, … (1 more)

### Integration Points
- Runtime calls: _SlotState, assignments.items, metrics.get, payload.get, self._assignments.get, self._assignments.pop, self._assignments.values, self._available.add, self._available.discard, self._select_slot, self._slot_state.items, self._slot_state.values, … (1 more)

### Code Quality Notes
- Missing method docstrings: EmbeddingAllocator.__init__, EmbeddingAllocator._select_slot


## src/townlet/policy/__init__.py

**Purpose**: Policy integration layer.
**Dependencies**:
- Standard Library: __future__
- Third-Party: bc, runner
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: —

### Integration Points
- Third-party libraries: bc, runner

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/policy/bc.py

**Purpose**: Behaviour cloning utilities.
**Dependencies**:
- Standard Library: __future__, collections.abc, dataclasses, json, pathlib
- Third-Party: numpy
- Internal: townlet.policy.models, townlet.policy.replay
**Related modules**: townlet.policy.models, townlet.policy.replay

### Classes
- **BCTrainingConfig** (bases: object; decorators: dataclass) — No class docstring.
  - Attributes: learning_rate: float = 0.001, batch_size: int = 64, epochs: int = 5, weight_decay: float = 0.0, device: str = 'cpu'
  - Methods: None.
- **BCDatasetConfig** (bases: object; decorators: dataclass) — No class docstring.
  - Attributes: manifest: Path = None
  - Methods: None.
- **BCTrajectoryDataset** (bases: Dataset; decorators: —) — Torch dataset flattening replay samples for behaviour cloning.
  - Methods:
    - `__init__(self, samples) -> None` — No method docstring. Raises: TorchNotAvailableError('PyTorch required for BC training'), ValueError('BC dataset requires at least one frame').
    - `__len__(self) -> int` — No method docstring.
    - `__getitem__(self, index) -> None` — No method docstring.
- **BCTrainer** (bases: object; decorators: —) — Lightweight supervised trainer for behaviour cloning.
  - Methods:
    - `__init__(self, config, policy_config) -> None` — No method docstring. Raises: TorchNotAvailableError('PyTorch required for BC training').
    - `fit(self, dataset) -> Mapping[str, float]` — No method docstring.
    - `evaluate(self, dataset) -> Mapping[str, float]` — No method docstring.

### Functions
- `load_bc_samples(manifest_path) -> list[ReplaySample]` — No function docstring. Side effects: filesystem. Raises: ValueError('BC manifest contained no valid samples'), ValueError('BC manifest must be a list').
  - Parameters: manifest_path
  - Returns: list[ReplaySample]
- `evaluate_bc_policy(model, dataset, device) -> Mapping[str, float]` — No function docstring. Raises: TorchNotAvailableError('PyTorch required for BC evaluation').
  - Parameters: model, dataset, device
  - Returns: Mapping[str, float]

### Constants and Configuration
- None.

### Data Flow
- Inputs: dataset, device, manifest_path, model
- Outputs: Mapping[str, float], list[ReplaySample]
- Internal interactions: —
- External interactions: ConflictAwarePolicyNetwork, DataLoader, Path, TorchNotAvailableError, action_batch.to, actions.append, astype, entry.get, exists, feature_batch.to, features.append, item, … (36 more)

### Integration Points
- Runtime calls: ConflictAwarePolicyNetwork, DataLoader, Path, TorchNotAvailableError, action_batch.to, actions.append, astype, entry.get, exists, feature_batch.to, features.append, item, … (36 more)
- Third-party libraries: numpy

### Code Quality Notes
- Missing function docstrings: load_bc_samples, evaluate_bc_policy
- Missing method docstrings: BCTrajectoryDataset.__init__, BCTrajectoryDataset.__len__, BCTrajectoryDataset.__getitem__, BCTrainer.__init__, BCTrainer.fit, BCTrainer.evaluate


## src/townlet/policy/behavior.py

**Purpose**: Behavior controller interfaces for scripted decision logic.
**Dependencies**:
- Standard Library: __future__, dataclasses, typing
- Third-Party: —
- Internal: townlet.config, townlet.world.grid
**Related modules**: townlet.config, townlet.world.grid

### Classes
- **AgentIntent** (bases: object; decorators: dataclass) — Represents the next action an agent wishes to perform.
  - Attributes: kind: str = None, object_id: Optional[str] = None, affordance_id: Optional[str] = None, blocked: bool = False, position: Optional[tuple[int, int]] = None
  - Methods: None.
- **BehaviorController** (bases: Protocol; decorators: —) — Defines the interface for agent decision logic.
  - Methods:
    - `decide(self, world, agent_id) -> AgentIntent` — No method docstring.
- **IdleBehavior** (bases: BehaviorController; decorators: —) — Default no-op behavior that keeps agents idle.
  - Methods:
    - `decide(self, world, agent_id) -> AgentIntent` — No method docstring.
- **ScriptedBehavior** (bases: BehaviorController; decorators: —) — Simple rule-based controller used before RL policies are available.
  - Methods:
    - `__init__(self, config) -> None` — No method docstring.
    - `decide(self, world, agent_id) -> AgentIntent` — No method docstring.
    - `_cleanup_pending(self, world, agent_id) -> None` — No method docstring.
    - `_maybe_move_to_job(self, world, agent_id, snapshot) -> Optional[AgentIntent]` — No method docstring.
    - `_satisfy_needs(self, world, agent_id, snapshot) -> Optional[AgentIntent]` — No method docstring.
    - `_rivals_in_queue(self, world, agent_id, object_id) -> bool` — No method docstring.
    - `_plan_meal(self, world, agent_id) -> Optional[AgentIntent]` — No method docstring.
    - `_find_object_of_type(self, world, object_type) -> Optional[str]` — No method docstring.

### Functions
- `build_behavior(config) -> BehaviorController` — No function docstring.
  - Parameters: config
  - Returns: BehaviorController

### Constants and Configuration
- None.

### Data Flow
- Inputs: config
- Outputs: BehaviorController
- Internal interactions: —
- External interactions: AgentIntent, ScriptedBehavior, fridge.stock.get, self._cleanup_pending, self._find_object_of_type, self._maybe_move_to_job, self._plan_meal, self._rivals_in_queue, self._satisfy_needs, self.config.jobs.get, self.pending.get, self.pending.pop, … (9 more)

### Integration Points
- Runtime calls: AgentIntent, ScriptedBehavior, fridge.stock.get, self._cleanup_pending, self._find_object_of_type, self._maybe_move_to_job, self._plan_meal, self._rivals_in_queue, self._satisfy_needs, self.config.jobs.get, self.pending.get, self.pending.pop, … (9 more)

### Code Quality Notes
- Missing function docstrings: build_behavior
- Missing method docstrings: BehaviorController.decide, IdleBehavior.decide, ScriptedBehavior.__init__, ScriptedBehavior.decide, ScriptedBehavior._cleanup_pending, ScriptedBehavior._maybe_move_to_job, ScriptedBehavior._satisfy_needs, ScriptedBehavior._rivals_in_queue, ScriptedBehavior._plan_meal, ScriptedBehavior._find_object_of_type


## src/townlet/policy/metrics.py

**Purpose**: Utility helpers for replay and rollout metrics.
**Dependencies**:
- Standard Library: __future__, json, typing
- Third-Party: numpy, replay
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `compute_sample_metrics(sample) -> dict[str, float]` — Compute summary metrics for a replay sample.
  - Parameters: sample
  - Returns: dict[str, float]

### Constants and Configuration
- None.

### Data Flow
- Inputs: sample
- Outputs: dict[str, float]
- Internal interactions: —
- External interactions: action_ids.max, action_lookup_meta.items, add_stats, id_to_payload.get, json.loads, kind_counts.get, kind_counts.items, names.index, np.array, np.bincount, np.clip, np.count_nonzero, … (8 more)

### Integration Points
- Runtime calls: action_ids.max, action_lookup_meta.items, add_stats, id_to_payload.get, json.loads, kind_counts.get, kind_counts.items, names.index, np.array, np.bincount, np.clip, np.count_nonzero, … (8 more)
- Third-party libraries: numpy, replay

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/policy/models.py

**Purpose**: Torch-based policy/value networks for Townlet PPO.
**Dependencies**:
- Standard Library: __future__, dataclasses
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- **TorchNotAvailableError** (bases: RuntimeError; decorators: —) — Raised when a Torch-dependent component is used without PyTorch.
  - Methods: None.
- **ConflictAwarePolicyConfig** (bases: object; decorators: dataclass) — No class docstring.
  - Attributes: feature_dim: int = None, map_shape: tuple[int, int, int] = None, action_dim: int = None, hidden_dim: int = 256
  - Methods: None.

### Functions
- `torch_available() -> bool` — Return True if PyTorch is available in the runtime.
  - Parameters: —
  - Returns: bool

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: bool
- Internal interactions: —
- External interactions: —

### Integration Points
- None noted.

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/policy/ppo/__init__.py

**Purpose**: PPO utilities package.
**Dependencies**:
- Standard Library: —
- Third-Party: —
- Internal: utils
**Related modules**: utils

### Classes
- None defined.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: —

### Integration Points
- None noted.

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/policy/ppo/utils.py

**Purpose**: Utility functions for PPO advantage and loss computation.
**Dependencies**:
- Standard Library: __future__, dataclasses
- Third-Party: torch
- Internal: —
**Related modules**: —

### Classes
- **AdvantageReturns** (bases: object; decorators: dataclass) — Container for PPO advantage and return tensors.
  - Attributes: advantages: torch.Tensor = None, returns: torch.Tensor = None
  - Methods: None.

### Functions
- `compute_gae(rewards, value_preds, dones, gamma, gae_lambda) -> AdvantageReturns` — Compute Generalized Advantage Estimation (GAE).  Args:     rewards: Tensor shaped (batch, timesteps).     value_preds: Tensor shaped (batch, timesteps) or (batch, timesteps + 1).     dones: Tensor shaped (batch, timesteps) with 1.0 when episode terminates.     gamma: Discount factor.     gae_lambda: GAE smoothing coefficient.  Returns:     AdvantageReturns with tensors shaped (batch, timesteps). Raises: ValueError('Rewards and dones must be 2D tensors (batch, timesteps)'), ValueError('value_preds must align with rewards (same length) or provide bootstrap value for the final timestep'), ValueError('value_preds must be a 2D tensor (batch, steps or steps+1)').
  - Parameters: rewards, value_preds, dones, gamma, gae_lambda
  - Returns: AdvantageReturns
- `normalize_advantages(advantages, eps) -> torch.Tensor` — Normalize advantage estimates to zero mean/unit variance.
  - Parameters: advantages, eps
  - Returns: torch.Tensor
- `value_baseline_from_old_preds(value_preds, timesteps) -> torch.Tensor` — Extract baseline values aligned with each timestep from stored predictions. Raises: ValueError('value_preds must be 2D (batch, steps)'), ValueError('value_preds must provide estimates for each timestep or include a bootstrap value').
  - Parameters: value_preds, timesteps
  - Returns: torch.Tensor
- `clipped_value_loss(new_values, returns, old_values, value_clip) -> torch.Tensor` — Compute the clipped value loss term. Raises: ValueError('new_values, returns, and old_values must share the same shape').
  - Parameters: new_values, returns, old_values, value_clip
  - Returns: torch.Tensor
- `policy_surrogate(new_log_probs, old_log_probs, advantages, clip_param) -> tuple[torch.Tensor, torch.Tensor]` — Compute PPO clipped policy loss and clip fraction. Raises: ValueError('log_probs and advantages must share identical shape').
  - Parameters: new_log_probs, old_log_probs, advantages, clip_param
  - Returns: tuple[torch.Tensor, torch.Tensor]

### Constants and Configuration
- None.

### Data Flow
- Inputs: advantages, clip_param, dones, eps, gae_lambda, gamma, new_log_probs, new_values, old_log_probs, old_values, returns, rewards, timesteps, value_clip, value_preds
- Outputs: AdvantageReturns, torch.Tensor, tuple[torch.Tensor, torch.Tensor]
- Internal interactions: —
- External interactions: AdvantageReturns, advantages.mean, advantages.std, mean, ratio.gt, ratio.lt, torch.clamp, torch.exp, torch.isnan, torch.max, torch.min, torch.zeros, … (2 more)

### Integration Points
- Runtime calls: AdvantageReturns, advantages.mean, advantages.std, mean, ratio.gt, ratio.lt, torch.clamp, torch.exp, torch.isnan, torch.max, torch.min, torch.zeros, … (2 more)
- Third-party libraries: torch

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/policy/replay.py

**Purpose**: Utilities for replaying observation/telemetry samples.
**Dependencies**:
- Standard Library: __future__, collections.abc, dataclasses, json, pathlib, typing
- Third-Party: numpy, yaml
- Internal: —
**Related modules**: —

### Classes
- **ReplaySample** (bases: object; decorators: dataclass) — Container for observation samples used in training replays.
  - Attributes: map: np.ndarray = None, features: np.ndarray = None, actions: np.ndarray = None, old_log_probs: np.ndarray = None, value_preds: np.ndarray = None, rewards: np.ndarray = None, dones: np.ndarray = None, metadata: dict[str, Any] = None
  - Methods:
    - `__post_init__(self) -> None` — No method docstring. Raises: TypeError(f'ReplaySample.{field_name} must be a numpy array'), ValueError('ReplaySample requires at least one timestep array'), ValueError('ReplaySample.features must have shape (feature_dim,) or (timesteps, feature_dim)'), ValueError('ReplaySample.map must have shape (channels, H, W) or (timesteps, channels, H, W)'), ValueError(f'ReplaySample training arrays must share timestep length; expected {timesteps}, got {step_len} for {field_name}'), ValueError(f'ReplaySample.features timestep count must match training arrays; expected {timesteps}, got {self.features.shape[0]}'), ValueError(f'ReplaySample.map timestep count must match training arrays; expected {timesteps}, got {self.map.shape[0]}'), ValueError(f'ReplaySample.value_preds must have length matching timesteps or timesteps + 1; got {value_steps} for {timesteps} step(s)'), ValueError(f'ReplaySample.{field_name} must be 1D or 2D, got shape {value.shape}').
    - `feature_names(self) -> Optional[list[str]]` — No method docstring.
    - `conflict_stats(self) -> dict[str, float]` — No method docstring.
- **ReplayBatch** (bases: object; decorators: dataclass) — Mini-batch representation composed from replay samples.
  - Attributes: maps: np.ndarray = None, features: np.ndarray = None, actions: np.ndarray = None, old_log_probs: np.ndarray = None, value_preds: np.ndarray = None, rewards: np.ndarray = None, dones: np.ndarray = None, metadata: dict[str, Any] = None
  - Methods:
    - `__post_init__(self) -> None` — No method docstring. Raises: ValueError('features must have shape (batch, feature_dim) or (batch, timesteps, feature_dim)'), ValueError('map and feature batch sizes must match'), ValueError('maps must have shape (batch, channels, height, width) or (batch, timesteps, channels, height, width)'), ValueError('value_preds must have length matching timesteps or timesteps + 1 in batch'), ValueError('value_preds must have shape (batch, timesteps) or (batch, timesteps + 1)'), ValueError(f'{field_name} batch size mismatch: expected {batch_size}, got {array.shape[0]}'), ValueError(f'{field_name} must have shape (batch, timesteps) after stacking'), ValueError(f'{field_name} timestep mismatch: expected {expected}, got {current}').
    - `conflict_stats(self) -> dict[str, float]` — No method docstring.
- **ReplayDatasetConfig** (bases: object; decorators: dataclass) — Configuration for building replay datasets.
  - Attributes: entries: list[tuple[Path, Optional[Path]]] = None, batch_size: int = 1, shuffle: bool = False, seed: Optional[int] = None, drop_last: bool = False, streaming: bool = False, metrics_map: Optional[dict[str, dict[str, float]]] = None, label: Optional[str] = None
  - Methods:
    - `from_manifest(cls, manifest_path, batch_size, shuffle, seed, drop_last, streaming) -> 'ReplayDatasetConfig'` — No method docstring.
    - `from_capture_dir(cls, capture_dir, batch_size, shuffle, seed, drop_last, streaming) -> 'ReplayDatasetConfig'` — No method docstring. Raises: FileNotFoundError(manifest_path).
- **ReplayDataset** (bases: object; decorators: —) — Iterable dataset producing conflict-aware replay batches.
  - Methods:
    - `__init__(self, config) -> None` — No method docstring. Raises: ValueError('batch_size must be positive').
    - `_ensure_homogeneous(self, samples) -> None` — No method docstring. Raises: ValueError('Replay samples have mismatched shapes; cannot batch'), ValueError(f'Replay samples have mismatched {field_name} shapes; cannot batch').
    - `__len__(self) -> int` — No method docstring.
    - `__iter__(self) -> Iterator[ReplayBatch]` — No method docstring.
    - `_fetch_sample(self, index) -> ReplaySample` — No method docstring. Raises: ValueError('Replay samples have mismatched shapes; cannot batch'), ValueError('Replay samples have mismatched timestep length; cannot batch'), ValueError('Replay samples have mismatched value baseline length; cannot batch'), ValueError(f'Replay samples have mismatched {field_name} shapes; cannot batch').
    - `_ensure_sample_metrics(self, sample, entry) -> None` — No method docstring.
    - `_aggregate_metrics(self) -> dict[str, float]` — No method docstring.

### Functions
- `_ensure_conflict_features(metadata) -> None` — No function docstring. Raises: ValueError('Replay sample metadata missing feature_names list'), ValueError(f'Replay sample missing conflict feature(s): {missing}').
  - Parameters: metadata
  - Returns: None
- `load_replay_sample(sample_path, meta_path) -> ReplaySample` — Load observation tensors and metadata for replay-driven training scaffolds. Raises: FileNotFoundError(sample_path), ValueError(f'Replay sample {sample_path} missing required arrays'), ValueError(f'Replay sample {sample_path} missing training array(s): {missing_training}').
  - Parameters: sample_path, meta_path
  - Returns: ReplaySample
- `build_batch(samples) -> ReplayBatch` — Stack multiple replay samples into a batch for training consumers. Raises: ValueError('at least one sample required to build batch').
  - Parameters: samples
  - Returns: ReplayBatch
- `_resolve_manifest_path(path_spec, base) -> Path` — Resolve manifest path specs that may be absolute or repo-relative. Side effects: filesystem.
  - Parameters: path_spec, base
  - Returns: Path
- `_load_manifest(manifest_path) -> list[tuple[Path, Optional[Path]]]` — No function docstring. Side effects: filesystem. Raises: FileNotFoundError(manifest_path), ValueError("Manifest entry missing 'sample' field"), ValueError("Replay manifest must be a list or mapping with 'samples'"), ValueError("Replay manifest payload missing 'samples' list"), ValueError('Manifest entry must be string or mapping'), ValueError('Replay manifest contains no entries').
  - Parameters: manifest_path
  - Returns: list[tuple[Path, Optional[Path]]]
- `frames_to_replay_sample(frames) -> ReplaySample` — Convert collected trajectory frames into a replay sample. Raises: ValueError('frames sequence cannot be empty').
  - Parameters: frames
  - Returns: ReplaySample

### Constants and Configuration
- `REQUIRED_CONFLICT_FEATURES` (tuple[str, ...]) = ["rivalry_max", "rivalry_avoid_count"]
- `STEP_ARRAY_FIELDS` (tuple[str, ...]) = ["actions", "old_log_probs", "rewards", "dones"]
- `TRAINING_ARRAY_FIELDS` (tuple[str, ...]) = "STEP_ARRAY_FIELDS + ('value_preds',)"

### Data Flow
- Inputs: base, frames, manifest_path, meta_path, metadata, path_spec, sample_path, samples
- Outputs: None, Path, ReplayBatch, ReplaySample, list[tuple[Path, Optional[Path]]]
- Internal interactions: —
- External interactions: Path, Path.cwd, ReplayBatch, ReplaySample, _ensure_conflict_features, _load_manifest, _resolve_manifest_path, action_ids.append, actions.max, base_arrays.items, build_batch, candidate_path.exists, … (59 more)

### Integration Points
- Runtime calls: Path, Path.cwd, ReplayBatch, ReplaySample, _ensure_conflict_features, _load_manifest, _resolve_manifest_path, action_ids.append, actions.max, base_arrays.items, build_batch, candidate_path.exists, … (59 more)
- Third-party libraries: numpy, yaml

### Code Quality Notes
- Missing function docstrings: _ensure_conflict_features, _load_manifest
- Missing method docstrings: ReplaySample.__post_init__, ReplaySample.feature_names, ReplaySample.conflict_stats, ReplayBatch.__post_init__, ReplayBatch.conflict_stats, ReplayDatasetConfig.from_manifest, ReplayDatasetConfig.from_capture_dir, ReplayDataset.__init__, ReplayDataset._ensure_homogeneous, ReplayDataset.__len__, ReplayDataset.__iter__, ReplayDataset._fetch_sample, ReplayDataset._ensure_sample_metrics, ReplayDataset._aggregate_metrics


## src/townlet/policy/replay_buffer.py

**Purpose**: In-memory replay dataset used for rollout captures.
**Dependencies**:
- Standard Library: __future__, collections.abc, dataclasses
- Third-Party: —
- Internal: townlet.policy.replay
**Related modules**: townlet.policy.replay

### Classes
- **InMemoryReplayDatasetConfig** (bases: object; decorators: dataclass) — No class docstring.
  - Attributes: entries: Sequence[ReplaySample] = None, batch_size: int = 1, drop_last: bool = False, rollout_ticks: int = 0, label: str | None = None
  - Methods: None.
- **InMemoryReplayDataset** (bases: object; decorators: —) — No class docstring.
  - Methods:
    - `__init__(self, config) -> None` — No method docstring. Raises: ValueError('In-memory dataset requires samples'), ValueError('batch_size must be positive').
    - `_validate_shapes(self) -> None` — No method docstring. Raises: ValueError('In-memory samples have mismatched shapes').
    - `__iter__(self) -> Iterator[ReplayBatch]` — No method docstring.
    - `__len__(self) -> int` — No method docstring.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: build_batch, self._validate_shapes

### Integration Points
- Runtime calls: build_batch, self._validate_shapes

### Code Quality Notes
- Missing method docstrings: InMemoryReplayDataset.__init__, InMemoryReplayDataset._validate_shapes, InMemoryReplayDataset.__iter__, InMemoryReplayDataset.__len__


## src/townlet/policy/rollout.py

**Purpose**: Rollout buffer scaffolding for future live PPO integration.
**Dependencies**:
- Standard Library: __future__, collections.abc, dataclasses, json, pathlib
- Third-Party: numpy
- Internal: townlet.policy.metrics, townlet.policy.replay, townlet.policy.replay_buffer
**Related modules**: townlet.policy.metrics, townlet.policy.replay, townlet.policy.replay_buffer

### Classes
- **AgentRollout** (bases: object; decorators: dataclass) — No class docstring.
  - Attributes: agent_id: str = None, frames: list[dict[str, object]] = 'field(default_factory=list)'
  - Methods:
    - `append(self, frame) -> None` — No method docstring.
    - `to_replay_sample(self) -> ReplaySample` — No method docstring.
- **RolloutBuffer** (bases: object; decorators: —) — Collects trajectory frames and exposes helpers to save or replay them.
  - Methods:
    - `__init__(self) -> None` — No method docstring.
    - `record_events(self, events) -> None` — No method docstring.
    - `extend(self, frames) -> None` — No method docstring.
    - `__len__(self) -> int` — No method docstring.
    - `by_agent(self) -> dict[str, AgentRollout]` — No method docstring.
    - `to_samples(self) -> dict[str, ReplaySample]` — No method docstring.
    - `save(self, output_dir, prefix, compress) -> None` — No method docstring.
    - `build_dataset(self, batch_size, drop_last) -> InMemoryReplayDataset` — No method docstring. Raises: ValueError('Rollout buffer contains no frames; cannot build dataset').
    - `is_empty(self) -> bool` — No method docstring.
    - `set_tick_count(self, ticks) -> None` — No method docstring.
    - `_aggregate_metrics(self, samples) -> dict[str, float]` — No method docstring.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: AgentRollout, InMemoryReplayDataset, InMemoryReplayDatasetConfig, append, compute_sample_metrics, counts.get, event.get, frame.get, frames_to_replay_sample, grouped.setdefault, items, json.dumps, … (22 more)

### Integration Points
- Runtime calls: AgentRollout, InMemoryReplayDataset, InMemoryReplayDatasetConfig, append, compute_sample_metrics, counts.get, event.get, frame.get, frames_to_replay_sample, grouped.setdefault, items, json.dumps, … (22 more)
- Third-party libraries: numpy

### Code Quality Notes
- Missing method docstrings: AgentRollout.append, AgentRollout.to_replay_sample, RolloutBuffer.__init__, RolloutBuffer.record_events, RolloutBuffer.extend, RolloutBuffer.__len__, RolloutBuffer.by_agent, RolloutBuffer.to_samples, RolloutBuffer.save, RolloutBuffer.build_dataset, RolloutBuffer.is_empty, RolloutBuffer.set_tick_count, RolloutBuffer._aggregate_metrics


## src/townlet/policy/runner.py

**Purpose**: Policy orchestration scaffolding.
**Dependencies**:
- Standard Library: __future__, collections.abc, json, math, pathlib, random, statistics, time, typing
- Third-Party: numpy
- Internal: townlet.config, townlet.policy.bc, townlet.policy.behavior, townlet.policy.models, townlet.policy.ppo.utils, townlet.policy.replay, townlet.policy.replay_buffer, townlet.policy.rollout, townlet.stability.promotion, townlet.world.grid
**Related modules**: townlet.config, townlet.policy.bc, townlet.policy.behavior, townlet.policy.models, townlet.policy.ppo.utils, townlet.policy.replay, townlet.policy.replay_buffer, townlet.policy.rollout, townlet.stability.promotion, townlet.world.grid

### Classes
- **PolicyRuntime** (bases: object; decorators: —) — Bridges the simulation with PPO/backends via PettingZoo.
  - Methods:
    - `__init__(self, config) -> None` — No method docstring.
    - `seed_anneal_rng(self, seed) -> None` — No method docstring.
    - `set_anneal_ratio(self, ratio) -> None` — No method docstring.
    - `enable_anneal_blend(self, enabled) -> None` — No method docstring.
    - `register_ctx_reset_callback(self, callback) -> None` — No method docstring.
    - `set_policy_action_provider(self, provider) -> None` — No method docstring.
    - `decide(self, world, tick) -> dict[str, object]` — Return a primitive action per agent.
    - `post_step(self, rewards, terminated) -> None` — Record rewards and termination signals into buffers.
    - `flush_transitions(self, observations) -> list[dict[str, object]]` — Combine stored transition data with observations and return trajectory frames.
    - `collect_trajectory(self, clear) -> list[dict[str, object]]` — Return accumulated trajectory frames and reset internal buffer.
    - `consume_option_switch_counts(self) -> dict[str, int]` — Return per-agent option switch counts accumulated since last call.
    - `acquire_possession(self, agent_id) -> bool` — No method docstring.
    - `release_possession(self, agent_id) -> bool` — No method docstring.
    - `is_possessed(self, agent_id) -> bool` — No method docstring.
    - `possessed_agents(self) -> list[str]` — No method docstring.
    - `reset_state(self) -> None` — Reset transient buffers so snapshot loads don’t duplicate data.
    - `_select_intent_with_blend(self, world, agent_id, scripted) -> AgentIntent` — No method docstring.
    - `_clone_intent(intent) -> AgentIntent` — No method docstring.
    - `_intents_match(lhs, rhs) -> bool` — No method docstring.
    - `_enforce_option_commit(self, agent_id, tick, intent) -> tuple[AgentIntent, bool]` — No method docstring.
    - `_annotate_with_policy_outputs(self, frame) -> None` — No method docstring.
    - `_update_policy_snapshot(self, frames) -> None` — No method docstring.
    - `latest_policy_snapshot(self) -> dict[str, dict[str, object]]` — No method docstring.
    - `active_policy_hash(self) -> str | None` — Return the configured policy hash, if any.
    - `set_policy_hash(self, value) -> None` — Set the policy hash after loading a checkpoint.
    - `current_anneal_ratio(self) -> float | None` — Return the latest anneal ratio (0..1) if tracking available.
    - `set_anneal_ratio(self, ratio) -> None` — No method docstring.
    - `_ensure_policy_network(self, map_shape, feature_dim, action_dim) -> bool` — No method docstring.
    - `_build_policy_network(self, feature_dim, map_shape, action_dim) -> ConflictAwarePolicyNetwork` — No method docstring.
- **TrainingHarness** (bases: object; decorators: —) — Coordinates RL training sessions.
  - Methods:
    - `__init__(self, config) -> None` — No method docstring.
    - `run(self) -> None` — Entry point for CLI training runs based on config.training.source. Raises: NotImplementedError("Training mode '%s' is not supported via run(); use scripts/run_training.py with --mode." % mode).
    - `current_anneal_ratio(self) -> float | None` — No method docstring.
    - `set_anneal_ratio(self, ratio) -> None` — No method docstring.
    - `run_replay(self, sample_path, meta_path) -> dict[str, float]` — Load a replay observation sample and surface conflict-aware stats. Side effects: stdout.
    - `run_replay_batch(self, pairs) -> dict[str, float]` — No method docstring. Raises: ValueError('Replay batch requires at least one entry').
    - `run_replay_dataset(self, dataset_config) -> dict[str, float]` — No method docstring. Side effects: stdout. Raises: ValueError('Replay dataset yielded no batches').
    - `capture_rollout(self, ticks, auto_seed_agents, output_dir, prefix, compress) -> RolloutBuffer` — Run the simulation loop for a fixed number of ticks and collect frames. Raises: ValueError('No agents available for rollout capture. Provide a scenario or use auto seeding.'), ValueError('ticks must be positive to capture a rollout').
    - `run_rollout_ppo(self, ticks, batch_size, auto_seed_agents, output_dir, prefix, compress, epochs, log_path, log_frequency, max_log_entries) -> dict[str, float]` — No method docstring.
    - `_load_bc_dataset(self, manifest) -> BCTrajectoryDataset` — No method docstring.
    - `run_bc_training(self) -> dict[str, float]` — No method docstring. Side effects: filesystem. Raises: TorchNotAvailableError('PyTorch is required for behaviour cloning training'), ValueError('BC manifest is required for behaviour cloning').
    - `run_anneal(self) -> list[dict[str, object]]` — No method docstring. Side effects: filesystem. Raises: ValueError('Replay manifest required for PPO stages in anneal'), ValueError('anneal_schedule is empty; configure training.anneal_schedule in config').
    - `run_ppo(self, dataset_config, epochs, log_path, log_frequency, max_log_entries, in_memory_dataset) -> dict[str, float]` — No method docstring. Side effects: stdout. Raises: TorchNotAvailableError('PyTorch is required for PPO training. Install torch to proceed.'), ValueError('Derived action_dim must be positive'), ValueError('No PPO mini-batch updates were performed'), ValueError('PPO %s contained NaN/inf (dataset=%s, batch=%s)' % (name, dataset_label_str, batch_index)), ValueError('PPO advantages produced invalid std (dataset=%s, batch=%s)' % (dataset_label_str, batch_index)), ValueError('PPO mini-batch advantages produced invalid std (dataset=%s, batch=%s)' % (dataset_label_str, batch_index)), ValueError('Replay batch missing map shape metadata'), ValueError('Replay dataset yielded no batches'), ValueError('dataset_config is required when in_memory_dataset is not provided').
    - `evaluate_anneal_results(self, results) -> str` — No method docstring.
    - `last_anneal_status(self) -> str | None` — No method docstring.
    - `_record_promotion_evaluation(self) -> None` — No method docstring.
    - `_select_social_reward_stage(self, cycle_id) -> str | None` — No method docstring.
    - `_apply_social_reward_stage(self, cycle_id) -> None` — No method docstring.
    - `_summarise_batch(self, batch, batch_index) -> dict[str, float]` — No method docstring.
    - `build_replay_dataset(self, config) -> ReplayDataset` — No method docstring.
    - `build_policy_network(self, feature_dim, map_shape, action_dim, hidden_dim) -> ConflictAwarePolicyNetwork` — No method docstring. Raises: TorchNotAvailableError('PyTorch is required to build the policy network. Install torch or disable PPO.').

### Functions
- `_softmax(logits) -> np.ndarray` — No function docstring.
  - Parameters: logits
  - Returns: np.ndarray
- `_pretty_action(action_repr) -> str` — No function docstring.
  - Parameters: action_repr
  - Returns: str

### Constants and Configuration
- `PPO_TELEMETRY_VERSION` = 1.2
- `ANNEAL_BC_MIN_DEFAULT` = 0.9
- `ANNEAL_LOSS_TOLERANCE_DEFAULT` = 0.1
- `ANNEAL_QUEUE_TOLERANCE_DEFAULT` = 0.15

### Data Flow
- Inputs: action_repr, logits
- Outputs: np.ndarray, str
- Internal interactions: —
- External interactions: AgentIntent, BCTrainer, BCTrainingParams, BCTrajectoryDataset, Categorical, ConflictAwarePolicyConfig, ConflictAwarePolicyNetwork, PPOConfig, Path, PromotionManager, ReplayDataset, ReplayDatasetConfig, … (203 more)

### Integration Points
- Runtime calls: AgentIntent, BCTrainer, BCTrainingParams, BCTrajectoryDataset, Categorical, ConflictAwarePolicyConfig, ConflictAwarePolicyNetwork, PPOConfig, Path, PromotionManager, ReplayDataset, ReplayDatasetConfig, … (203 more)
- Third-party libraries: numpy

### Code Quality Notes
- Missing function docstrings: _softmax, _pretty_action
- Missing method docstrings: PolicyRuntime.__init__, PolicyRuntime.seed_anneal_rng, PolicyRuntime.set_anneal_ratio, PolicyRuntime.enable_anneal_blend, PolicyRuntime.register_ctx_reset_callback, PolicyRuntime.set_policy_action_provider, PolicyRuntime.acquire_possession, PolicyRuntime.release_possession, PolicyRuntime.is_possessed, PolicyRuntime.possessed_agents, PolicyRuntime._select_intent_with_blend, PolicyRuntime._clone_intent, PolicyRuntime._intents_match, PolicyRuntime._enforce_option_commit, PolicyRuntime._annotate_with_policy_outputs, PolicyRuntime._update_policy_snapshot, PolicyRuntime.latest_policy_snapshot, PolicyRuntime.set_anneal_ratio, PolicyRuntime._ensure_policy_network, PolicyRuntime._build_policy_network, TrainingHarness.__init__, TrainingHarness.current_anneal_ratio, TrainingHarness.set_anneal_ratio, TrainingHarness.run_replay_batch, TrainingHarness.run_replay_dataset, TrainingHarness.run_rollout_ppo, TrainingHarness._load_bc_dataset, TrainingHarness.run_bc_training, TrainingHarness.run_anneal, TrainingHarness.run_ppo, TrainingHarness.evaluate_anneal_results, TrainingHarness.last_anneal_status, TrainingHarness._record_promotion_evaluation, TrainingHarness._select_social_reward_stage, TrainingHarness._apply_social_reward_stage, TrainingHarness._summarise_batch, TrainingHarness.build_replay_dataset, TrainingHarness.build_policy_network


## src/townlet/policy/scenario_utils.py

**Purpose**: Helpers for applying scenario initialisation to simulation loops.
**Dependencies**:
- Standard Library: __future__, logging, typing
- Third-Party: —
- Internal: townlet.core.sim_loop, townlet.policy.behavior, townlet.world.grid
**Related modules**: townlet.core.sim_loop, townlet.policy.behavior, townlet.world.grid

### Classes
- **ScenarioBehavior** (bases: object; decorators: —) — Wraps an existing behavior controller with scripted schedules.
  - Methods:
    - `__init__(self, base_behavior, schedules) -> None` — No method docstring.
    - `decide(self, world, agent_id) -> None` — No method docstring.

### Functions
- `apply_scenario(loop, scenario) -> None` — No function docstring. Raises: ValueError(f'Invalid object position for {obj['id']}: {raw}').
  - Parameters: loop, scenario
  - Returns: None
- `seed_default_agents(loop) -> None` — No function docstring.
  - Parameters: loop
  - Returns: None
- `has_agents(loop) -> bool` — No function docstring.
  - Parameters: loop
  - Returns: bool

### Constants and Configuration
- None.

### Data Flow
- Inputs: loop, scenario
- Outputs: None, bool
- Internal interactions: —
- External interactions: AgentIntent, AgentSnapshot, ScenarioBehavior, agent.get, data.get, data.pop, dict.fromkeys, intents.append, logger.info, loop.world.objects.get, loop.world.register_affordance, loop.world.register_object, … (7 more)

### Integration Points
- Runtime calls: AgentIntent, AgentSnapshot, ScenarioBehavior, agent.get, data.get, data.pop, dict.fromkeys, intents.append, logger.info, loop.world.objects.get, loop.world.register_affordance, loop.world.register_object, … (7 more)

### Code Quality Notes
- Missing function docstrings: apply_scenario, seed_default_agents, has_agents
- Missing method docstrings: ScenarioBehavior.__init__, ScenarioBehavior.decide


## src/townlet/policy/scripted.py

**Purpose**: Simple scripted policy helpers for trajectory capture.
**Dependencies**:
- Standard Library: __future__, dataclasses
- Third-Party: —
- Internal: townlet.world.grid
**Related modules**: townlet.world.grid

### Classes
- **ScriptedPolicy** (bases: object; decorators: —) — Base class for scripted policies used during BC trajectory capture.
  - Attributes: name: str = 'scripted'
  - Methods:
    - `decide(self, world, tick) -> dict[str, dict]` — No method docstring. Raises: NotImplementedError.
    - `describe(self) -> str` — No method docstring.
    - `trajectory_prefix(self) -> str` — No method docstring.
- **IdlePolicy** (bases: ScriptedPolicy; decorators: dataclass) — Default scripted policy: all agents wait every tick.
  - Attributes: name: str = 'idle'
  - Methods:
    - `decide(self, world, tick) -> dict[str, dict]` — No method docstring.
- **ScriptedPolicyAdapter** (bases: object; decorators: —) — Adapter so SimulationLoop can call scripted policies.
  - Methods:
    - `__init__(self, scripted_policy) -> None` — No method docstring.
    - `decide(self, world, tick) -> dict[str, dict]` — No method docstring.
    - `post_step(self, rewards, terminated) -> None` — No method docstring.
    - `flush_transitions(self, observations) -> None` — No method docstring.
    - `collect_trajectory(self) -> None` — No method docstring.
    - `latest_policy_snapshot(self) -> dict[str, dict[str, object]]` — No method docstring.
    - `possessed_agents(self) -> list[str]` — No method docstring.
    - `consume_option_switch_counts(self) -> dict[str, int]` — No method docstring.
    - `active_policy_hash(self) -> str | None` — No method docstring.
    - `set_policy_hash(self, value) -> None` — No method docstring.
    - `current_anneal_ratio(self) -> float | None` — No method docstring.
    - `set_anneal_ratio(self, ratio) -> None` — No method docstring.
    - `enable_anneal_blend(self, _) -> None` — No method docstring.

### Functions
- `get_scripted_policy(name) -> ScriptedPolicy` — Factory for scripted policies; extend with richer behaviours as needed. Raises: ValueError(f'Unknown scripted policy: {name}').
  - Parameters: name
  - Returns: ScriptedPolicy

### Constants and Configuration
- None.

### Data Flow
- Inputs: name
- Outputs: ScriptedPolicy
- Internal interactions: —
- External interactions: IdlePolicy, action.get, actions.get, lower, name.strip, rewards.get, self._latest_snapshot.items, self.last_actions.items, self.last_actions.keys, self.scripted_policy.decide, terminated.get, world.agents.keys

### Integration Points
- Runtime calls: IdlePolicy, action.get, actions.get, lower, name.strip, rewards.get, self._latest_snapshot.items, self.last_actions.items, self.last_actions.keys, self.scripted_policy.decide, terminated.get, world.agents.keys

### Code Quality Notes
- Missing method docstrings: ScriptedPolicy.decide, ScriptedPolicy.describe, ScriptedPolicy.trajectory_prefix, IdlePolicy.decide, ScriptedPolicyAdapter.__init__, ScriptedPolicyAdapter.decide, ScriptedPolicyAdapter.post_step, ScriptedPolicyAdapter.flush_transitions, ScriptedPolicyAdapter.collect_trajectory, ScriptedPolicyAdapter.latest_policy_snapshot, ScriptedPolicyAdapter.possessed_agents, ScriptedPolicyAdapter.consume_option_switch_counts, ScriptedPolicyAdapter.active_policy_hash, ScriptedPolicyAdapter.set_policy_hash, ScriptedPolicyAdapter.current_anneal_ratio, ScriptedPolicyAdapter.set_anneal_ratio, ScriptedPolicyAdapter.enable_anneal_blend


## src/townlet/rewards/__init__.py

**Purpose**: Reward computation utilities.
**Dependencies**:
- Standard Library: __future__
- Third-Party: engine
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: —

### Integration Points
- Third-party libraries: engine

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/rewards/engine.py

**Purpose**: Reward calculation guardrails and aggregation.
**Dependencies**:
- Standard Library: __future__, collections.abc
- Third-Party: —
- Internal: townlet.config, townlet.world.grid
**Related modules**: townlet.config, townlet.world.grid

### Classes
- **RewardEngine** (bases: object; decorators: —) — Compute per-agent rewards with clipping and guardrails.
  - Methods:
    - `__init__(self, config) -> None` — No method docstring.
    - `compute(self, world, terminated, reasons) -> dict[str, float]` — No method docstring.
    - `_consume_chat_events(self, world) -> Iterable[dict[str, object]]` — No method docstring.
    - `_social_rewards_enabled(self) -> bool` — No method docstring.
    - `_compute_chat_rewards(self, world, events) -> dict[str, float]` — No method docstring.
    - `_needs_override(self, snapshot) -> bool` — No method docstring.
    - `_is_blocked(self, agent_id, tick, window) -> bool` — No method docstring.
    - `_prune_termination_blocks(self, tick, window) -> None` — No method docstring.
    - `_compute_wage_bonus(self, agent_id, world, wage_rate) -> float` — No method docstring.
    - `_compute_punctuality_bonus(self, agent_id, world, bonus_rate) -> float` — No method docstring.
    - `_compute_terminal_penalty(self, agent_id, terminated, reasons) -> float` — No method docstring.
    - `_reset_episode_totals(self, terminated, world) -> None` — No method docstring.
    - `latest_reward_breakdown(self) -> dict[str, dict[str, float]]` — No method docstring.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: consumer, ctx.get, event.get, reasons.get, rewards.get, self._compute_chat_rewards, self._compute_punctuality_bonus, self._compute_terminal_penalty, self._compute_wage_bonus, self._consume_chat_events, self._episode_totals.get, self._episode_totals.pop, … (19 more)

### Integration Points
- Runtime calls: consumer, ctx.get, event.get, reasons.get, rewards.get, self._compute_chat_rewards, self._compute_punctuality_bonus, self._compute_terminal_penalty, self._compute_wage_bonus, self._consume_chat_events, self._episode_totals.get, self._episode_totals.pop, … (19 more)

### Code Quality Notes
- Missing method docstrings: RewardEngine.__init__, RewardEngine.compute, RewardEngine._consume_chat_events, RewardEngine._social_rewards_enabled, RewardEngine._compute_chat_rewards, RewardEngine._needs_override, RewardEngine._is_blocked, RewardEngine._prune_termination_blocks, RewardEngine._compute_wage_bonus, RewardEngine._compute_punctuality_bonus, RewardEngine._compute_terminal_penalty, RewardEngine._reset_episode_totals, RewardEngine.latest_reward_breakdown


## src/townlet/scheduler/__init__.py

**Purpose**: Schedulers for perturbations and timers.
**Dependencies**:
- Standard Library: __future__
- Third-Party: perturbations
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: —

### Integration Points
- Third-party libraries: perturbations

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/scheduler/perturbations.py

**Purpose**: Perturbation scheduler scaffolding.
**Dependencies**:
- Standard Library: __future__, collections.abc, dataclasses, random, typing
- Third-Party: —
- Internal: townlet.config, townlet.utils, townlet.world.grid
**Related modules**: townlet.config, townlet.utils, townlet.world.grid

### Classes
- **ScheduledPerturbation** (bases: object; decorators: dataclass) — Represents a perturbation that is pending or active in the world.
  - Attributes: event_id: str = None, spec_name: str = None, kind: PerturbationKind = None, started_at: int = None, ends_at: int = None, payload: dict[str, object] = 'field(default_factory=dict)', targets: list[str] = 'field(default_factory=list)'
  - Methods: None.
- **PerturbationScheduler** (bases: object; decorators: —) — Injects bounded random events into the world.
  - Methods:
    - `__init__(self, config) -> None` — No method docstring.
    - `pending_count(self) -> int` — No method docstring.
    - `active_count(self) -> int` — No method docstring.
    - `tick(self, world, current_tick) -> None` — No method docstring.
    - `_expire_active(self, current_tick, world) -> None` — No method docstring.
    - `_expire_cooldowns(self, current_tick) -> None` — No method docstring.
    - `_expire_window_events(self, current_tick) -> None` — No method docstring.
    - `_drain_pending(self, world, current_tick) -> None` — No method docstring.
    - `_maybe_schedule(self, world, current_tick) -> None` — No method docstring.
    - `schedule_manual(self, world, spec_name, current_tick) -> ScheduledPerturbation` — No method docstring. Raises: KeyError(spec_name), ValueError('Unable to schedule perturbation; insufficient targets').
    - `cancel_event(self, world, event_id) -> bool` — No method docstring.
    - `_activate(self, world, event) -> None` — No method docstring.
    - `_apply_event(self, world, event) -> None` — No method docstring.
    - `_on_event_concluded(self, world, event) -> None` — No method docstring.
    - `seed(self, value) -> None` — No method docstring.
    - `_can_fire_spec(self, name, spec, current_tick) -> bool` — No method docstring.
    - `_per_tick_probability(self, spec) -> float` — No method docstring.
    - `_generate_event(self, name, spec, current_tick, world) -> Optional[ScheduledPerturbation]` — No method docstring.
    - `_eligible_agents(self, world, current_tick) -> list[str]` — No method docstring.
    - `enqueue(self, events) -> None` — No method docstring.
    - `pending(self) -> list[ScheduledPerturbation]` — No method docstring.
    - `active(self) -> dict[str, ScheduledPerturbation]` — No method docstring.
    - `export_state(self) -> dict[str, object]` — No method docstring.
    - `import_state(self, payload) -> None` — No method docstring.
    - `reset_state(self) -> None` — No method docstring.
    - `allocate_event_id(self) -> str` — No method docstring.
    - `spec_for(self, name) -> Optional[PerturbationEventConfig]` — No method docstring.
    - `rng_state(self) -> tuple` — No method docstring.
    - `set_rng_state(self, state) -> None` — No method docstring.
    - `rng(self) -> random.Random` — No method docstring.
    - `_coerce_event(self, data) -> ScheduledPerturbation` — No method docstring.
    - `_serialize_event(event) -> dict[str, object]` — No method docstring.
    - `serialize_event(self, event) -> dict[str, object]` — No method docstring.
    - `latest_state(self) -> dict[str, object]` — No method docstring.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: PerturbationKind, ScheduledPerturbation, active_payload.items, agent_cooldowns.items, data.get, decode_rng_state, encode_rng_state, event.payload.get, event_cooldowns.items, payload.get, payload.setdefault, random.Random, … (44 more)

### Integration Points
- Runtime calls: PerturbationKind, ScheduledPerturbation, active_payload.items, agent_cooldowns.items, data.get, decode_rng_state, encode_rng_state, event.payload.get, event_cooldowns.items, payload.get, payload.setdefault, random.Random, … (44 more)

### Code Quality Notes
- Missing method docstrings: PerturbationScheduler.__init__, PerturbationScheduler.pending_count, PerturbationScheduler.active_count, PerturbationScheduler.tick, PerturbationScheduler._expire_active, PerturbationScheduler._expire_cooldowns, PerturbationScheduler._expire_window_events, PerturbationScheduler._drain_pending, PerturbationScheduler._maybe_schedule, PerturbationScheduler.schedule_manual, PerturbationScheduler.cancel_event, PerturbationScheduler._activate, PerturbationScheduler._apply_event, PerturbationScheduler._on_event_concluded, PerturbationScheduler.seed, PerturbationScheduler._can_fire_spec, PerturbationScheduler._per_tick_probability, PerturbationScheduler._generate_event, PerturbationScheduler._eligible_agents, PerturbationScheduler.enqueue, PerturbationScheduler.pending, PerturbationScheduler.active, PerturbationScheduler.export_state, PerturbationScheduler.import_state, PerturbationScheduler.reset_state, PerturbationScheduler.allocate_event_id, PerturbationScheduler.spec_for, PerturbationScheduler.rng_state, PerturbationScheduler.set_rng_state, PerturbationScheduler.rng, PerturbationScheduler._coerce_event, PerturbationScheduler._serialize_event, PerturbationScheduler.serialize_event, PerturbationScheduler.latest_state


## src/townlet/snapshots/__init__.py

**Purpose**: Snapshot and restore helpers.
**Dependencies**:
- Standard Library: __future__
- Third-Party: migrations, state
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: —

### Integration Points
- Third-party libraries: migrations, state

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/snapshots/migrations.py

**Purpose**: Snapshot migration registry and helpers.
**Dependencies**:
- Standard Library: __future__, collections, collections.abc, dataclasses, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- **MigrationNotFoundError** (bases: Exception; decorators: —) — Raised when no migration path exists between config identifiers.
  - Methods: None.
- **MigrationExecutionError** (bases: Exception; decorators: —) — Raised when a migration handler fails or leaves the snapshot unchanged.
  - Methods: None.
- **MigrationEdge** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: source: str = None, target: str = None, handler: MigrationHandler = None
  - Methods:
    - `identifier(self) -> str` — No method docstring.
- **SnapshotMigrationRegistry** (bases: object; decorators: —) — Maintains registered snapshot migrations keyed by config identifiers.
  - Methods:
    - `__init__(self) -> None` — No method docstring.
    - `register(self, from_config, to_config, handler) -> None` — No method docstring.
    - `clear(self) -> None` — No method docstring.
    - `_neighbours(self, node) -> Iterable[MigrationEdge]` — No method docstring.
    - `find_path(self, start, goal) -> list[MigrationEdge]` — No method docstring. Raises: MigrationNotFoundError(f'No snapshot migration path from {start} to {goal}').
    - `apply_path(self, path, state, config) -> tuple['SnapshotState', list[str]]` — No method docstring. Raises: MigrationExecutionError(f'Migration {edge.identifier} did not update config_id from {current.config_id}').

### Functions
- `register_migration(from_config, to_config, handler) -> None` — Register a snapshot migration handler.
  - Parameters: from_config, to_config, handler
  - Returns: None
- `clear_registry() -> None` — Reset registry (intended for test teardown).
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: from_config, handler, to_config
- Outputs: None
- Internal interactions: —
- External interactions: MigrationEdge, MigrationExecutionError, MigrationNotFoundError, applied.append, deque, edge.handler, queue.append, queue.popleft, registry.clear, registry.register, self._graph.clear, self._graph.get, … (4 more)

### Integration Points
- Runtime calls: MigrationEdge, MigrationExecutionError, MigrationNotFoundError, applied.append, deque, edge.handler, queue.append, queue.popleft, registry.clear, registry.register, self._graph.clear, self._graph.get, … (4 more)

### Code Quality Notes
- Missing method docstrings: MigrationEdge.identifier, SnapshotMigrationRegistry.__init__, SnapshotMigrationRegistry.register, SnapshotMigrationRegistry.clear, SnapshotMigrationRegistry._neighbours, SnapshotMigrationRegistry.find_path, SnapshotMigrationRegistry.apply_path


## src/townlet/snapshots/state.py

**Purpose**: Snapshot persistence scaffolding.
**Dependencies**:
- Standard Library: __future__, collections.abc, dataclasses, json, logging, pathlib, random, typing
- Third-Party: —
- Internal: townlet.agents.models, townlet.config, townlet.lifecycle.manager, townlet.scheduler.perturbations, townlet.snapshots.migrations, townlet.utils, townlet.world.grid
**Related modules**: townlet.agents.models, townlet.config, townlet.lifecycle.manager, townlet.scheduler.perturbations, townlet.snapshots.migrations, townlet.utils, townlet.world.grid

### Classes
- **SnapshotState** (bases: object; decorators: dataclass) — No class docstring.
  - Attributes: config_id: str = None, tick: int = None, agents: dict[str, dict[str, object]] = 'field(default_factory=dict)', objects: dict[str, dict[str, object]] = 'field(default_factory=dict)', queues: dict[str, object] = 'field(default_factory=dict)', embeddings: dict[str, object] = 'field(default_factory=dict)', employment: dict[str, object] = 'field(default_factory=dict)', lifecycle: dict[str, object] = 'field(default_factory=dict)', rng_state: Optional[str] = None, rng_streams: dict[str, str] = 'field(default_factory=dict)', telemetry: dict[str, object] = 'field(default_factory=dict)', console_buffer: list[object] = 'field(default_factory=list)', … (7 more)
  - Methods:
    - `as_dict(self) -> dict[str, object]` — No method docstring.
    - `from_dict(cls, payload) -> 'SnapshotState'` — No method docstring. Raises: ValueError('Relationship edges must be mappings'), ValueError('Snapshot agents field must be a mapping'), ValueError('Snapshot objects field must be a mapping'), ValueError('Snapshot payload missing relationships field'), ValueError('Snapshot payload missing required fields'), ValueError('Snapshot relationships field must be a mapping').
- **SnapshotManager** (bases: object; decorators: —) — Handles save/load of simulation state and RNG streams.
  - Methods:
    - `__init__(self, root) -> None` — No method docstring. Side effects: filesystem.
    - `save(self, state) -> Path` — No method docstring. Raises: ValueError('Snapshot target escaped configured root').
    - `load(self, path, config) -> SnapshotState` — No method docstring. Side effects: filesystem. Raises: FileNotFoundError(resolved), ValueError('Snapshot config_id mismatch: expected %s, got %s (auto-migration disabled)' % (config.config_id, state.config_id)), ValueError('Snapshot config_id mismatch: expected %s, got %s' % (config.config_id, state.config_id)), ValueError('Snapshot document missing state payload'), ValueError('Snapshot migration chain did not reach target config_id %s (ended at %s)' % (config.config_id, state.config_id)), ValueError('Snapshot migration failed'), ValueError('Snapshot missing schema_version string'), ValueError('Snapshot path outside manager root'), ValueError('Snapshot schema version %s is newer than supported %s (enable snapshot.guardrails.allow_downgrade to override)' % (schema_version, SNAPSHOT_SCHEMA_VERSION)), ValueError(f'Unsupported snapshot schema version: {schema_version}').

### Functions
- `_parse_version(value) -> tuple[int, ...]` — No function docstring.
  - Parameters: value
  - Returns: tuple[int, ...]
- `snapshot_from_world(config, world) -> SnapshotState` — Capture the current world state into a snapshot payload.
  - Parameters: config, world
  - Returns: SnapshotState
- `apply_snapshot_to_world(world, snapshot) -> None` — Restore world, queue, embeddings, and lifecycle state from snapshot.
  - Parameters: world, snapshot
  - Returns: None
- `apply_snapshot_to_telemetry(telemetry, snapshot) -> None` — No function docstring.
  - Parameters: telemetry, snapshot
  - Returns: None

### Constants and Configuration
- `SNAPSHOT_SCHEMA_VERSION` = '1.6'

### Data Flow
- Inputs: config, snapshot, telemetry, value, world
- Outputs: None, SnapshotState, tuple[int, ...]
- Internal interactions: —
- External interactions: AgentSnapshot, InteractiveObject, Path, Personality, SnapshotState, SnapshotState.from_dict, _parse_version, active_payload.items, affordances_payload.items, agents_obj.items, applied_list.extend, cls, … (83 more)

### Integration Points
- Runtime calls: AgentSnapshot, InteractiveObject, Path, Personality, SnapshotState, SnapshotState.from_dict, _parse_version, active_payload.items, affordances_payload.items, agents_obj.items, applied_list.extend, cls, … (83 more)

### Code Quality Notes
- Missing function docstrings: _parse_version, apply_snapshot_to_telemetry
- Missing method docstrings: SnapshotState.as_dict, SnapshotState.from_dict, SnapshotManager.__init__, SnapshotManager.save, SnapshotManager.load


## src/townlet/stability/__init__.py

**Purpose**: Stability guardrails.
**Dependencies**:
- Standard Library: __future__
- Third-Party: monitor, promotion
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: —

### Integration Points
- Third-party libraries: monitor, promotion

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/stability/monitor.py

**Purpose**: Monitors KPIs and promotion guardrails.
**Dependencies**:
- Standard Library: __future__, collections, collections.abc
- Third-Party: —
- Internal: townlet.config
**Related modules**: townlet.config

### Classes
- **StabilityMonitor** (bases: object; decorators: —) — Tracks rolling metrics and canaries.
  - Methods:
    - `__init__(self, config) -> None` — No method docstring.
    - `_promotion_snapshot(self) -> dict[str, object]` — No method docstring.
    - `_finalise_promotion_window(self, window_end) -> None` — No method docstring.
    - `_update_promotion_window(self, tick, alerts) -> None` — No method docstring.
    - `track(self) -> None` — No method docstring.
    - `latest_metrics(self) -> dict[str, object]` — No method docstring.
    - `export_state(self) -> dict[str, object]` — No method docstring.
    - `import_state(self, payload) -> None` — No method docstring.
    - `reset_state(self) -> None` — No method docstring.
    - `_update_starvation_state(self) -> int` — No method docstring.
    - `_update_reward_samples(self) -> tuple[float | None, float | None, int]` — No method docstring.
    - `_threshold_snapshot(self) -> dict[str, object]` — No method docstring.
    - `_update_option_samples(self) -> float | None` — No method docstring.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: agent_info.get, alerts.append, deque, e.get, embedding_metrics.get, employment_metrics.get, event.get, hunger_levels.items, job_snapshot.values, option_switch_counts.values, payload.get, previous_queue_metrics.get, … (31 more)

### Integration Points
- Runtime calls: agent_info.get, alerts.append, deque, e.get, embedding_metrics.get, employment_metrics.get, event.get, hunger_levels.items, job_snapshot.values, option_switch_counts.values, payload.get, previous_queue_metrics.get, … (31 more)

### Code Quality Notes
- Missing method docstrings: StabilityMonitor.__init__, StabilityMonitor._promotion_snapshot, StabilityMonitor._finalise_promotion_window, StabilityMonitor._update_promotion_window, StabilityMonitor.track, StabilityMonitor.latest_metrics, StabilityMonitor.export_state, StabilityMonitor.import_state, StabilityMonitor.reset_state, StabilityMonitor._update_starvation_state, StabilityMonitor._update_reward_samples, StabilityMonitor._threshold_snapshot, StabilityMonitor._update_option_samples


## src/townlet/stability/promotion.py

**Purpose**: Promotion gate state tracking.
**Dependencies**:
- Standard Library: __future__, collections, collections.abc, json, pathlib
- Third-Party: —
- Internal: townlet.config
**Related modules**: townlet.config

### Classes
- **PromotionManager** (bases: object; decorators: —) — Tracks promotion readiness and release/shadow state.
  - Methods:
    - `__init__(self, config, log_path) -> None` — No method docstring.
    - `update_from_metrics(self, metrics) -> None` — Update state based on the latest stability metrics.
    - `mark_promoted(self) -> None` — Record a promotion event and update release metadata.
    - `register_rollback(self) -> None` — Record a rollback event and return to monitoring state.
    - `record_manual_swap(self) -> dict[str, object]` — Record a manual policy swap without altering candidate readiness.
    - `set_candidate_metadata(self, metadata) -> None` — No method docstring.
    - `snapshot(self) -> dict[str, object]` — No method docstring.
    - `export_state(self) -> dict[str, object]` — No method docstring.
    - `import_state(self, payload) -> None` — No method docstring.
    - `reset(self) -> None` — No method docstring.
    - `_log_event(self, record) -> None` — No method docstring.
    - `_normalise_release(self, metadata) -> dict[str, object]` — No method docstring.
    - `_resolve_rollback_target(self, metadata) -> dict[str, object]` — No method docstring.
    - `_latest_promoted_release(self) -> dict[str, object] | None` — No method docstring.
    - `state(self) -> str` — No method docstring.
    - `candidate_ready(self) -> bool` — No method docstring.
    - `pass_streak(self) -> int` — No method docstring.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: base.items, deque, entry.get, handle.write, json.dumps, metadata.items, metrics.get, payload.get, promotion_block.get, self._history.append, self._history.clear, self._latest_promoted_release, … (6 more)

### Integration Points
- Runtime calls: base.items, deque, entry.get, handle.write, json.dumps, metadata.items, metrics.get, payload.get, promotion_block.get, self._history.append, self._history.clear, self._latest_promoted_release, … (6 more)

### Code Quality Notes
- Missing method docstrings: PromotionManager.__init__, PromotionManager.set_candidate_metadata, PromotionManager.snapshot, PromotionManager.export_state, PromotionManager.import_state, PromotionManager.reset, PromotionManager._log_event, PromotionManager._normalise_release, PromotionManager._resolve_rollback_target, PromotionManager._latest_promoted_release, PromotionManager.state, PromotionManager.candidate_ready, PromotionManager.pass_streak


## src/townlet/telemetry/__init__.py

**Purpose**: Telemetry publication surfaces.
**Dependencies**:
- Standard Library: __future__
- Third-Party: publisher
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: —

### Integration Points
- Third-party libraries: publisher

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/telemetry/narration.py

**Purpose**: Narration throttling utilities.
**Dependencies**:
- Standard Library: __future__, collections
- Third-Party: —
- Internal: townlet.config
**Related modules**: townlet.config

### Classes
- **NarrationRateLimiter** (bases: object; decorators: —) — Apply global and per-category narration cooldowns with dedupe.
  - Methods:
    - `__init__(self, config) -> None` — No method docstring.
    - `begin_tick(self, tick) -> None` — No method docstring.
    - `allow(self, category) -> bool` — Return True if a narration may be emitted for the given category.
    - `export_state(self) -> dict[str, object]` — No method docstring.
    - `import_state(self, payload) -> None` — No method docstring.
    - `_expire_recent_entries(self) -> None` — No method docstring.
    - `_expire_window(self) -> None` — No method docstring.
    - `_check_global_cooldown(self) -> bool` — No method docstring.
    - `_check_category_cooldown(self, category) -> bool` — No method docstring.
    - `_check_window_limit(self) -> bool` — No method docstring.
    - `_record_emission(self, category, dedupe_key) -> None` — No method docstring.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: deque, last_category.items, payload.get, recent.items, self._check_category_cooldown, self._check_global_cooldown, self._check_window_limit, self._expire_recent_entries, self._expire_window, self._last_category_tick.get, self._recent_entries.clear, self._recent_entries.get, … (6 more)

### Integration Points
- Runtime calls: deque, last_category.items, payload.get, recent.items, self._check_category_cooldown, self._check_global_cooldown, self._check_window_limit, self._expire_recent_entries, self._expire_window, self._last_category_tick.get, self._recent_entries.clear, self._recent_entries.get, … (6 more)

### Code Quality Notes
- Missing method docstrings: NarrationRateLimiter.__init__, NarrationRateLimiter.begin_tick, NarrationRateLimiter.export_state, NarrationRateLimiter.import_state, NarrationRateLimiter._expire_recent_entries, NarrationRateLimiter._expire_window, NarrationRateLimiter._check_global_cooldown, NarrationRateLimiter._check_category_cooldown, NarrationRateLimiter._check_window_limit, NarrationRateLimiter._record_emission


## src/townlet/telemetry/publisher.py

**Purpose**: Telemetry pipelines and console bridge.
**Dependencies**:
- Standard Library: __future__, collections, collections.abc, dataclasses, json, logging, pathlib, threading, time, typing
- Third-Party: —
- Internal: townlet.config, townlet.console.auth, townlet.console.command, townlet.telemetry.narration, townlet.telemetry.transport
**Related modules**: townlet.config, townlet.console.auth, townlet.console.command, townlet.telemetry.narration, townlet.telemetry.transport

### Classes
- **TelemetryPublisher** (bases: object; decorators: —) — Publishes observer snapshots and consumes console commands.
  - Methods:
    - `__init__(self, config) -> None` — No method docstring. Side effects: filesystem.
    - `queue_console_command(self, command) -> None` — No method docstring.
    - `drain_console_buffer(self) -> Iterable[object]` — No method docstring.
    - `export_state(self) -> dict[str, object]` — No method docstring.
    - `import_state(self, payload) -> None` — No method docstring.
    - `export_console_buffer(self) -> list[object]` — No method docstring.
    - `import_console_buffer(self, buffer) -> None` — No method docstring.
    - `record_console_results(self, results) -> None` — No method docstring.
    - `latest_console_results(self) -> list[dict[str, Any]]` — No method docstring.
    - `console_history(self) -> list[dict[str, Any]]` — No method docstring.
    - `record_possessed_agents(self, agents) -> None` — No method docstring.
    - `latest_possessed_agents(self) -> list[str]` — No method docstring.
    - `latest_precondition_failures(self) -> list[dict[str, object]]` — No method docstring.
    - `latest_transport_status(self) -> dict[str, object]` — Return transport health and backlog counters for observability.
    - `record_health_metrics(self, metrics) -> None` — No method docstring.
    - `latest_health_status(self) -> dict[str, object]` — No method docstring.
    - `_build_transport_client(self) -> None` — No method docstring. Raises: RuntimeError(message).
    - `_reset_transport_client(self) -> None` — No method docstring.
    - `_send_with_retry(self, payload, tick) -> bool` — No method docstring.
    - `_flush_transport_buffer(self, tick) -> None` — No method docstring.
    - `_flush_loop(self) -> None` — No method docstring.
    - `_enqueue_stream_payload(self, payload) -> None` — No method docstring.
    - `_build_stream_payload(self, tick) -> dict[str, Any]` — No method docstring.
    - `close(self) -> None` — No method docstring.
    - `stop_worker(self) -> None` — Stop the background flush worker without closing transports.
    - `_capture_affordance_runtime(self) -> None` — No method docstring.
    - `publish_tick(self) -> None` — No method docstring.
    - `latest_queue_metrics(self) -> dict[str, int] | None` — Expose the most recent queue-related telemetry counters.
    - `latest_queue_history(self) -> list[dict[str, object]]` — No method docstring.
    - `latest_rivalry_events(self) -> list[dict[str, object]]` — No method docstring.
    - `latest_affordance_runtime(self) -> dict[str, object]` — No method docstring.
    - `update_anneal_status(self, status) -> None` — Record the latest anneal status payload for observer dashboards.
    - `kpi_history(self) -> dict[str, list[float]]` — No method docstring.
    - `latest_conflict_snapshot(self) -> dict[str, object]` — Return the conflict-focused telemetry payload (queues + rivalry).
    - `latest_affordance_manifest(self) -> dict[str, object]` — Expose the most recent affordance manifest metadata.
    - `latest_reward_breakdown(self) -> dict[str, dict[str, float]]` — No method docstring.
    - `latest_stability_inputs(self) -> dict[str, object]` — No method docstring.
    - `record_stability_metrics(self, metrics) -> None` — No method docstring.
    - `latest_stability_metrics(self) -> dict[str, object]` — No method docstring.
    - `latest_promotion_state(self) -> dict[str, object] | None` — No method docstring.
    - `_append_console_audit(self, payload) -> None` — No method docstring.
    - `latest_stability_alerts(self) -> list[str]` — No method docstring.
    - `latest_perturbations(self) -> dict[str, object]` — No method docstring.
    - `update_policy_identity(self, identity) -> None` — No method docstring.
    - `latest_policy_identity(self) -> dict[str, object] | None` — No method docstring.
    - `record_snapshot_migrations(self, applied) -> None` — No method docstring.
    - `latest_snapshot_migrations(self) -> list[str]` — No method docstring.
    - `_normalize_perturbations_payload(self, payload) -> dict[str, object]` — No method docstring.
    - `latest_policy_snapshot(self) -> dict[str, dict[str, object]]` — No method docstring.
    - `latest_anneal_status(self) -> dict[str, object] | None` — No method docstring.
    - `latest_relationship_metrics(self) -> dict[str, object] | None` — Expose relationship churn payload captured during publish.
    - `latest_relationship_snapshot(self) -> dict[str, dict[str, dict[str, float]]]` — No method docstring.
    - `latest_relationship_updates(self) -> list[dict[str, object]]` — No method docstring.
    - `update_relationship_metrics(self, payload) -> None` — Allow external callers to seed the latest relationship metrics.
    - `latest_relationship_overlay(self) -> dict[str, list[dict[str, object]]]` — No method docstring.
    - `latest_narrations(self) -> list[dict[str, object]]` — Expose narration entries emitted during the latest publish call.
    - `latest_embedding_metrics(self) -> dict[str, float] | None` — Expose embedding allocator counters.
    - `latest_events(self) -> Iterable[dict[str, object]]` — Return the most recent event batch.
    - `latest_narration_state(self) -> dict[str, object]` — Return the narration limiter state for snapshot export.
    - `register_event_subscriber(self, subscriber) -> None` — Register a callback to receive each tick's event batch.
    - `latest_job_snapshot(self) -> dict[str, dict[str, object]]` — No method docstring.
    - `latest_economy_snapshot(self) -> dict[str, dict[str, object]]` — No method docstring.
    - `latest_employment_metrics(self) -> dict[str, object]` — No method docstring.
    - `schema(self) -> str` — No method docstring.
    - `_capture_relationship_snapshot(self, world) -> dict[str, dict[str, dict[str, float]]]` — No method docstring.
    - `_compute_relationship_updates(self, previous, current) -> list[dict[str, object]]` — No method docstring.
    - `_build_relationship_overlay(self) -> dict[str, list[dict[str, object]]]` — No method docstring.
    - `_process_narrations(self, events, tick) -> None` — No method docstring.
    - `_handle_queue_conflict_narration(self, event, tick) -> None` — No method docstring.
    - `_handle_shower_power_outage_narration(self, event, tick) -> None` — No method docstring.
    - `_handle_shower_complete_narration(self, event, tick) -> None` — No method docstring.
    - `_handle_sleep_complete_narration(self, event, tick) -> None` — No method docstring.
    - `_copy_relationship_snapshot(snapshot) -> dict[str, dict[str, dict[str, float]]]` — No method docstring.
    - `_update_kpi_history(self, world) -> None` — No method docstring.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: ConsoleAuthenticator, ConsoleCommandEnvelope, ConsoleCommandResult.from_error, NarrationRateLimiter, Path, TransportBuffer, _push, active.items, agent_payload.items, append, asdict, batch.append, … (155 more)

### Integration Points
- Runtime calls: ConsoleAuthenticator, ConsoleCommandEnvelope, ConsoleCommandResult.from_error, NarrationRateLimiter, Path, TransportBuffer, _push, active.items, agent_payload.items, append, asdict, batch.append, … (155 more)

### Code Quality Notes
- Missing method docstrings: TelemetryPublisher.__init__, TelemetryPublisher.queue_console_command, TelemetryPublisher.drain_console_buffer, TelemetryPublisher.export_state, TelemetryPublisher.import_state, TelemetryPublisher.export_console_buffer, TelemetryPublisher.import_console_buffer, TelemetryPublisher.record_console_results, TelemetryPublisher.latest_console_results, TelemetryPublisher.console_history, TelemetryPublisher.record_possessed_agents, TelemetryPublisher.latest_possessed_agents, TelemetryPublisher.latest_precondition_failures, TelemetryPublisher.record_health_metrics, TelemetryPublisher.latest_health_status, TelemetryPublisher._build_transport_client, TelemetryPublisher._reset_transport_client, TelemetryPublisher._send_with_retry, TelemetryPublisher._flush_transport_buffer, TelemetryPublisher._flush_loop, TelemetryPublisher._enqueue_stream_payload, TelemetryPublisher._build_stream_payload, TelemetryPublisher.close, TelemetryPublisher._capture_affordance_runtime, TelemetryPublisher.publish_tick, TelemetryPublisher.latest_queue_history, TelemetryPublisher.latest_rivalry_events, TelemetryPublisher.latest_affordance_runtime, TelemetryPublisher.kpi_history, TelemetryPublisher.latest_reward_breakdown, TelemetryPublisher.latest_stability_inputs, TelemetryPublisher.record_stability_metrics, TelemetryPublisher.latest_stability_metrics, TelemetryPublisher.latest_promotion_state, TelemetryPublisher._append_console_audit, TelemetryPublisher.latest_stability_alerts, TelemetryPublisher.latest_perturbations, TelemetryPublisher.update_policy_identity, TelemetryPublisher.latest_policy_identity, TelemetryPublisher.record_snapshot_migrations, TelemetryPublisher.latest_snapshot_migrations, TelemetryPublisher._normalize_perturbations_payload, TelemetryPublisher.latest_policy_snapshot, TelemetryPublisher.latest_anneal_status, TelemetryPublisher.latest_relationship_snapshot, TelemetryPublisher.latest_relationship_updates, TelemetryPublisher.latest_relationship_overlay, TelemetryPublisher.latest_job_snapshot, TelemetryPublisher.latest_economy_snapshot, TelemetryPublisher.latest_employment_metrics, TelemetryPublisher.schema, TelemetryPublisher._capture_relationship_snapshot, TelemetryPublisher._compute_relationship_updates, TelemetryPublisher._build_relationship_overlay, TelemetryPublisher._process_narrations, TelemetryPublisher._handle_queue_conflict_narration, TelemetryPublisher._handle_shower_power_outage_narration, TelemetryPublisher._handle_shower_complete_narration, TelemetryPublisher._handle_sleep_complete_narration, TelemetryPublisher._copy_relationship_snapshot, TelemetryPublisher._update_kpi_history


## src/townlet/telemetry/relationship_metrics.py

**Purpose**: Helpers for tracking relationship churn and eviction telemetry.
**Dependencies**:
- Standard Library: __future__, collections, collections.abc, dataclasses
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- **RelationshipEvictionSample** (bases: object; decorators: dataclass) — Aggregated eviction counts captured for a completed window.
  - Attributes: window_start: int = None, window_end: int = None, total_evictions: int = None, per_owner: dict[str, int] = None, per_reason: dict[str, int] = None
  - Methods:
    - `to_payload(self) -> dict[str, object]` — Serialise the sample into a telemetry-friendly payload.
- **RelationshipChurnAccumulator** (bases: object; decorators: —) — Tracks relationship eviction activity over fixed tick windows.
  - Methods:
    - `__init__(self) -> None` — No method docstring. Raises: ValueError('max_samples must be positive'), ValueError('window_ticks must be positive').
    - `record_eviction(self) -> None` — Record an eviction event for churn tracking.  Parameters ---------- tick:     Simulation tick when the eviction occurred. owner_id:     Agent whose relationship ledger evicted ``evicted_id``. evicted_id:     Agent removed from the ledger (unused for aggregation but captured     to support future diagnostics). reason:     Optional categorical tag (e.g. ``capacity`` or ``decay``) to aid in     telemetry analysis. ``None`` is grouped under ``"unknown"``. Raises: ValueError('tick must be non-negative').
    - `_roll_window(self, tick) -> None` — No method docstring.
    - `snapshot(self) -> dict[str, object]` — Return aggregates for the active window.
    - `history(self) -> Iterable[RelationshipEvictionSample]` — Return a snapshot of the recorded history.
    - `history_payload(self) -> list[dict[str, object]]` — Convert history samples into telemetry payloads.
    - `latest_payload(self) -> dict[str, object]` — Return the live window payload for telemetry publishing.
    - `ingest_payload(self, payload) -> None` — Restore the accumulator from an external payload.  This helper allows soak harnesses to persist state across sessions. Raises: ValueError('window_end must be >= window_start').

### Functions
- `_advance_window() -> int` — Move the window start forward until it covers ``current_tick``.
  - Parameters: —
  - Returns: int

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: int
- Internal interactions: —
- External interactions: Counter, RelationshipEvictionSample, _advance_window, deque, entry.get, history.append, items, owners.items, payload.get, reasons.items, sample.to_payload, self._history.append, … (5 more)

### Integration Points
- Runtime calls: Counter, RelationshipEvictionSample, _advance_window, deque, entry.get, history.append, items, owners.items, payload.get, reasons.items, sample.to_payload, self._history.append, … (5 more)

### Code Quality Notes
- Missing method docstrings: RelationshipChurnAccumulator.__init__, RelationshipChurnAccumulator._roll_window


## src/townlet/telemetry/transport.py

**Purpose**: Transport primitives for telemetry publishing.
**Dependencies**:
- Standard Library: __future__, collections, pathlib, socket, sys, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- **TelemetryTransportError** (bases: RuntimeError; decorators: —) — Raised when telemetry messages cannot be delivered.
  - Methods: None.
- **TransportClient** (bases: Protocol; decorators: —) — Common interface for transport implementations.
  - Methods:
    - `send(self, payload) -> None` — No method docstring. Raises: NotImplementedError.
    - `close(self) -> None` — No method docstring. Raises: NotImplementedError.
- **StdoutTransport** (bases: object; decorators: —) — Writes telemetry payloads to stdout (for development/debug).
  - Methods:
    - `__init__(self) -> None` — No method docstring.
    - `send(self, payload) -> None` — No method docstring.
    - `close(self) -> None` — No method docstring.
- **FileTransport** (bases: object; decorators: —) — Appends newline-delimited payloads to a local file.
  - Methods:
    - `__init__(self, path) -> None` — No method docstring.
    - `send(self, payload) -> None` — No method docstring.
    - `close(self) -> None` — No method docstring.
- **TcpTransport** (bases: object; decorators: —) — Sends telemetry payloads to a TCP endpoint.
  - Methods:
    - `__init__(self, endpoint) -> None` — No method docstring. Raises: TelemetryTransportError('telemetry.transport.endpoint must use host:port format'), TelemetryTransportError('telemetry.transport.endpoint port must be an integer').
    - `_connect(self) -> None` — No method docstring. Raises: TelemetryTransportError(f'Failed to connect to telemetry endpoint {host}:{port}: {exc}').
    - `send(self, payload) -> None` — No method docstring. Raises: TelemetryTransportError(str(exc)).
    - `close(self) -> None` — No method docstring.
- **TransportBuffer** (bases: object; decorators: —) — Accumulates payloads prior to flushing to the transport.
  - Methods:
    - `__init__(self) -> None` — No method docstring.
    - `append(self, payload) -> None` — No method docstring.
    - `popleft(self) -> bytes` — No method docstring.
    - `clear(self) -> None` — No method docstring.
    - `__len__(self) -> int` — No method docstring.
    - `total_bytes(self) -> int` — No method docstring.
    - `is_over_capacity(self) -> bool` — No method docstring.
    - `drop_until_within_capacity(self) -> int` — Drop oldest payloads until buffer fits limits; returns drop count.

### Functions
- `create_transport() -> TransportClient` — Factory helper for `TelemetryPublisher`. Raises: TelemetryTransportError('telemetry.transport.endpoint is required when using tcp transport'), TelemetryTransportError('telemetry.transport.file_path is required when using file transport'), TelemetryTransportError(f'Unsupported telemetry transport type: {transport_type}').
  - Parameters: —
  - Returns: TransportClient

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: TransportClient
- Internal interactions: —
- External interactions: FileTransport, StdoutTransport, TcpTransport, TelemetryTransportError, deque, endpoint.partition, host.strip, path.expanduser, self._connect, self._handle.close, self._handle.flush, self._handle.write, … (11 more)

### Integration Points
- Runtime calls: FileTransport, StdoutTransport, TcpTransport, TelemetryTransportError, deque, endpoint.partition, host.strip, path.expanduser, self._connect, self._handle.close, self._handle.flush, self._handle.write, … (11 more)

### Code Quality Notes
- Missing method docstrings: TransportClient.send, TransportClient.close, StdoutTransport.__init__, StdoutTransport.send, StdoutTransport.close, FileTransport.__init__, FileTransport.send, FileTransport.close, TcpTransport.__init__, TcpTransport._connect, TcpTransport.send, TcpTransport.close, TransportBuffer.__init__, TransportBuffer.append, TransportBuffer.popleft, TransportBuffer.clear, TransportBuffer.__len__, TransportBuffer.total_bytes, TransportBuffer.is_over_capacity


## src/townlet/utils/__init__.py

**Purpose**: Utility helpers for Townlet.
**Dependencies**:
- Standard Library: —
- Third-Party: rng
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: —

### Integration Points
- Third-party libraries: rng

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/utils/rng.py

**Purpose**: Utility helpers for serialising deterministic RNG state.
**Dependencies**:
- Standard Library: __future__, base64, pickle, random
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `encode_rng_state(state) -> str` — Encode a Python ``random`` state tuple into a base64 string.
  - Parameters: state
  - Returns: str
- `decode_rng_state(payload) -> tuple[object, ...]` — Decode a base64-encoded RNG state back into a Python tuple.
  - Parameters: payload
  - Returns: tuple[object, ...]
- `encode_rng(rng) -> str` — Capture the current state of ``rng`` as a serialisable string.
  - Parameters: rng
  - Returns: str

### Constants and Configuration
- None.

### Data Flow
- Inputs: payload, rng, state
- Outputs: str, tuple[object, ...]
- Internal interactions: —
- External interactions: base64.b64decode, base64.b64encode, decode, encode_rng_state, payload.encode, pickle.dumps, pickle.loads, rng.getstate

### Integration Points
- Runtime calls: base64.b64decode, base64.b64encode, decode, encode_rng_state, payload.encode, pickle.dumps, pickle.loads, rng.getstate

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/world/__init__.py

**Purpose**: World modelling primitives.
**Dependencies**:
- Standard Library: __future__
- Third-Party: employment, queue_manager, relationships
- Internal: grid
**Related modules**: grid

### Classes
- None defined.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: —

### Integration Points
- Third-party libraries: employment, queue_manager, relationships

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/world/affordances.py

**Purpose**: Affordance runtime scaffolding pending extraction from `world.grid`.
**Dependencies**:
- Standard Library: __future__, dataclasses, logging, time, typing
- Third-Party: —
- Internal: townlet.world.preconditions, townlet.world.queue_manager
**Related modules**: townlet.world.preconditions, townlet.world.queue_manager

### Classes
- **AffordanceRuntimeContext** (bases: object; decorators: dataclass(slots=True)) — Dependencies supplied to the affordance runtime.
  - Attributes: world: 'WorldState' = None, queue_manager: QueueManager = None, objects: MutableMapping[str, Any] = None, affordances: MutableMapping[str, Any] = None, running_affordances: MutableMapping[str, Any] = None, active_reservations: MutableMapping[str, str] = None, emit_event: Callable[[str, dict[str, object]], None] = None, sync_reservation: Callable[[str], None] = None, apply_affordance_effects: Callable[[str, dict[str, float]], None] = None, dispatch_hooks: Callable[[str, Iterable[str]], bool] = None, record_queue_conflict: Callable[..., None] = None, apply_need_decay: Callable[[], None] = None, … (2 more)
  - Methods: None.
- **RunningAffordanceState** (bases: object; decorators: dataclass(slots=True)) — Serialized view of a running affordance for telemetry/tests.
  - Attributes: agent_id: str = None, object_id: str = None, affordance_id: str = None, duration_remaining: int = None, effects: dict[str, float] = 'field(default_factory=dict)'
  - Methods: None.
- **HookPayload** (bases: TypedDict; decorators: —) — Structured affordance hook payload shared across stages.
  - Attributes: stage: Literal['before', 'after', 'fail'] = None, hook: str = None, tick: int = None, agent_id: str = None, object_id: str = None, affordance_id: str = None, world: 'WorldState' = None, spec: Any = None, effects: dict[str, float] = None, reason: str = None, condition: str = None, context: dict[str, object] = None
  - Methods: None.
- **AffordanceOutcome** (bases: object; decorators: dataclass(slots=True)) — Represents the result of an affordance-related agent action.
  - Attributes: agent_id: str = None, kind: str = None, success: bool = None, duration: int = None, object_id: str | None = None, affordance_id: str | None = None, tick: int | None = None, metadata: dict[str, object] = 'field(default_factory=dict)'
  - Methods: None.
- **AffordanceRuntime** (bases: Protocol; decorators: —) — Protocol describing the affordance runtime contract.
  - Methods:
    - `bind(self) -> None` — Attach the runtime to the provided world context.
    - `apply_actions(self, actions) -> None` — Process agent actions that may start or queue affordances.
    - `resolve(self) -> None` — Advance running affordances and emit telemetry/hook events.
    - `running_snapshot(self) -> dict[str, RunningAffordanceState]` — Return the serialisable state of all running affordances.
    - `clear(self) -> None` — Reset runtime state (used on snapshot restore or world reset).
- **DefaultAffordanceRuntime** (bases: object; decorators: —) — Default affordance runtime bound to an injected context.
  - Methods:
    - `__init__(self, context) -> None` — No method docstring.
    - `context(self) -> AffordanceRuntimeContext` — No method docstring.
    - `world(self) -> 'WorldState'` — No method docstring.
    - `running_affordances(self) -> MutableMapping[str, Any]` — No method docstring.
    - `instrumentation_level(self) -> str` — No method docstring.
    - `options(self) -> dict[str, object]` — No method docstring.
    - `remove_agent(self, agent_id) -> None` — Drop any running affordances owned by `agent_id`.
    - `start(self, agent_id, object_id, affordance_id) -> tuple[bool, dict[str, object]]` — No method docstring. Raises: RuntimeError(f"Affordance '{affordance_id}' incompatible with object '{object_id}'").
    - `release(self, agent_id, object_id) -> tuple[str | None, dict[str, object]]` — No method docstring.
    - `handle_blocked(self, object_id, tick) -> None` — No method docstring.
    - `resolve(self) -> None` — No method docstring.
    - `_instrumentation_enabled(self) -> bool` — No method docstring.
    - `running_snapshot(self) -> dict[str, RunningAffordanceState]` — No method docstring.
    - `clear(self) -> None` — No method docstring.
    - `export_state(self) -> dict[str, object]` — No method docstring.
    - `import_state(self, payload) -> None` — No method docstring.

### Functions
- `snapshot_running_affordance() -> RunningAffordanceState` — Create a serializable snapshot for a running affordance entry.
  - Parameters: —
  - Returns: RunningAffordanceState
- `build_hook_payload() -> HookPayload` — Compose the base payload forwarded to affordance hook handlers.
  - Parameters: —
  - Returns: HookPayload
- `apply_affordance_outcome(snapshot, outcome) -> None` — Update agent snapshot bookkeeping based on the supplied outcome.
  - Parameters: snapshot, outcome
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: outcome, snapshot
- Outputs: HookPayload, None, RunningAffordanceState
- Internal interactions: —
- External interactions: HookPayload, RunningAffordanceState, active_reservations.items, affordances.get, ctx.affordances.get, ctx.apply_affordance_effects, ctx.apply_need_decay, ctx.build_precondition_context, ctx.dispatch_hooks, ctx.emit_event, ctx.snapshot_precondition_context, ctx.sync_reservation, … (30 more)

### Integration Points
- Runtime calls: HookPayload, RunningAffordanceState, active_reservations.items, affordances.get, ctx.affordances.get, ctx.apply_affordance_effects, ctx.apply_need_decay, ctx.build_precondition_context, ctx.dispatch_hooks, ctx.emit_event, ctx.snapshot_precondition_context, ctx.sync_reservation, … (30 more)

### Code Quality Notes
- Contains TODO markers.
- Missing method docstrings: DefaultAffordanceRuntime.__init__, DefaultAffordanceRuntime.context, DefaultAffordanceRuntime.world, DefaultAffordanceRuntime.running_affordances, DefaultAffordanceRuntime.instrumentation_level, DefaultAffordanceRuntime.options, DefaultAffordanceRuntime.start, DefaultAffordanceRuntime.release, DefaultAffordanceRuntime.handle_blocked, DefaultAffordanceRuntime.resolve, DefaultAffordanceRuntime._instrumentation_enabled, DefaultAffordanceRuntime.running_snapshot, DefaultAffordanceRuntime.clear, DefaultAffordanceRuntime.export_state, DefaultAffordanceRuntime.import_state


## src/townlet/world/console_bridge.py

**Purpose**: Console command management for WorldState.
**Dependencies**:
- Standard Library: __future__, collections, dataclasses, logging, typing
- Third-Party: —
- Internal: townlet.console.command
**Related modules**: townlet.console.command

### Classes
- **ConsoleHandlerEntry** (bases: object; decorators: dataclass) — No class docstring.
  - Attributes: handler: Callable[[ConsoleCommandEnvelope], ConsoleCommandResult] = None, mode: str = None, require_cmd_id: bool = None
  - Methods: None.
- **ConsoleBridge** (bases: object; decorators: —) — Maintains console handlers and result history for a world instance.
  - Methods:
    - `__init__(self) -> None` — No method docstring.
    - `register_handler(self, name, handler) -> None` — No method docstring.
    - `handlers(self) -> Mapping[str, ConsoleHandlerEntry]` — No method docstring.
    - `record_result(self, result) -> None` — No method docstring.
    - `consume_results(self) -> list[ConsoleCommandResult]` — No method docstring.
    - `cached_result(self, cmd_id) -> ConsoleCommandResult | None` — No method docstring.
    - `apply(self, operations) -> None` — No method docstring.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: ConsoleCommandEnvelope, ConsoleCommandEnvelope.from_payload, ConsoleCommandResult.from_error, ConsoleHandlerEntry, OrderedDict, cached.clone, deque, entry.handler, logger.exception, logger.warning, result.clone, self._cmd_history.get, … (6 more)

### Integration Points
- Runtime calls: ConsoleCommandEnvelope, ConsoleCommandEnvelope.from_payload, ConsoleCommandResult.from_error, ConsoleHandlerEntry, OrderedDict, cached.clone, deque, entry.handler, logger.exception, logger.warning, result.clone, self._cmd_history.get, … (6 more)

### Code Quality Notes
- Missing method docstrings: ConsoleBridge.__init__, ConsoleBridge.register_handler, ConsoleBridge.handlers, ConsoleBridge.record_result, ConsoleBridge.consume_results, ConsoleBridge.cached_result, ConsoleBridge.apply


## src/townlet/world/employment.py

**Purpose**: Employment domain logic extracted from WorldState.
**Dependencies**:
- Standard Library: __future__, collections, logging, typing
- Third-Party: —
- Internal: townlet.config
**Related modules**: townlet.config

### Classes
- **EmploymentEngine** (bases: object; decorators: —) — Manages employment state, queues, and shift bookkeeping.
  - Methods:
    - `__init__(self, config, emit_event) -> None` — No method docstring.
    - `exits_today(self) -> int` — No method docstring.
    - `assign_jobs_to_agents(self, world) -> None` — No method docstring.
    - `apply_job_state(self, world) -> None` — No method docstring.
    - `_apply_job_state_legacy(self, world) -> None` — No method docstring.
    - `_apply_job_state_enforced(self, world) -> None` — No method docstring.
    - `context_defaults(self) -> dict[str, Any]` — No method docstring.
    - `get_employment_context(self, world, agent_id) -> dict[str, Any]` — No method docstring.
    - `employment_context_wages(self, agent_id) -> float` — No method docstring.
    - `employment_context_punctuality(self, agent_id) -> float` — No method docstring.
    - `_employment_idle_state(self, world, snapshot, ctx) -> None` — No method docstring.
    - `_employment_prepare_state(self, snapshot, ctx) -> None` — No method docstring.
    - `_employment_begin_shift(self, ctx, start, end) -> None` — No method docstring.
    - `_employment_determine_state(self) -> str` — No method docstring.
    - `_employment_apply_state_effects(self) -> None` — No method docstring.
    - `_employment_finalize_shift(self, world, snapshot, ctx, employment_cfg, job_id) -> None` — No method docstring.
    - `_employment_coworkers_on_shift(self, world, snapshot) -> list[str]` — No method docstring.
    - `enqueue_exit(self, world, agent_id, tick) -> None` — No method docstring.
    - `remove_from_queue(self, world, agent_id) -> None` — No method docstring.
    - `queue_snapshot(self) -> dict[str, Any]` — No method docstring.
    - `request_manual_exit(self, world, agent_id, tick) -> bool` — No method docstring.
    - `defer_exit(self, world, agent_id) -> bool` — No method docstring.
    - `export_state(self) -> dict[str, object]` — Return a serialisable snapshot of the employment domain state.
    - `import_state(self, payload) -> None` — Restore employment state from a snapshot payload.
    - `reset_exits_today(self) -> None` — No method docstring.
    - `set_exits_today(self, value) -> None` — No method docstring.
    - `increment_exits_today(self) -> None` — No method docstring.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: append, coworkers.append, ctx.get, deque, logger.debug, logger.isEnabledFor, payload.get, popleft, self._apply_job_state_enforced, self._apply_job_state_legacy, self._config.economy.get, self._emit_event, … (28 more)

### Integration Points
- Runtime calls: append, coworkers.append, ctx.get, deque, logger.debug, logger.isEnabledFor, payload.get, popleft, self._apply_job_state_enforced, self._apply_job_state_legacy, self._config.economy.get, self._emit_event, … (28 more)

### Code Quality Notes
- Missing method docstrings: EmploymentEngine.__init__, EmploymentEngine.exits_today, EmploymentEngine.assign_jobs_to_agents, EmploymentEngine.apply_job_state, EmploymentEngine._apply_job_state_legacy, EmploymentEngine._apply_job_state_enforced, EmploymentEngine.context_defaults, EmploymentEngine.get_employment_context, EmploymentEngine.employment_context_wages, EmploymentEngine.employment_context_punctuality, EmploymentEngine._employment_idle_state, EmploymentEngine._employment_prepare_state, EmploymentEngine._employment_begin_shift, EmploymentEngine._employment_determine_state, EmploymentEngine._employment_apply_state_effects, EmploymentEngine._employment_finalize_shift, EmploymentEngine._employment_coworkers_on_shift, EmploymentEngine.enqueue_exit, EmploymentEngine.remove_from_queue, EmploymentEngine.queue_snapshot, EmploymentEngine.request_manual_exit, EmploymentEngine.defer_exit, EmploymentEngine.reset_exits_today, EmploymentEngine.set_exits_today, EmploymentEngine.increment_exits_today


## src/townlet/world/grid.py

**Purpose**: Grid world representation and affordance integration.
**Dependencies**:
- Standard Library: __future__, collections, collections.abc, copy, dataclasses, logging, os, pathlib, random, time, typing
- Third-Party: —
- Internal: townlet.agents.models, townlet.agents.relationship_modifiers, townlet.config, townlet.config.affordance_manifest, townlet.console.command, townlet.observations.embedding, townlet.telemetry.relationship_metrics, townlet.world.affordances, townlet.world.console_bridge, townlet.world.employment, townlet.world.hooks, townlet.world.preconditions, townlet.world.queue_conflict, townlet.world.queue_manager, townlet.world.relationships, townlet.world.rivalry
**Related modules**: townlet.agents.models, townlet.agents.relationship_modifiers, townlet.config, townlet.config.affordance_manifest, townlet.console.command, townlet.observations.embedding, townlet.telemetry.relationship_metrics, townlet.world.affordances, townlet.world.console_bridge, townlet.world.employment, townlet.world.hooks, townlet.world.preconditions, townlet.world.queue_conflict, townlet.world.queue_manager, townlet.world.relationships, townlet.world.rivalry

### Classes
- **HookRegistry** (bases: object; decorators: —) — Registers named affordance hooks and returns handlers on demand.
  - Methods:
    - `__init__(self) -> None` — No method docstring.
    - `register(self, name, handler) -> None` — No method docstring. Raises: TypeError('Hook handler must be callable'), ValueError('Hook name must be a non-empty string').
    - `handlers_for(self, name) -> tuple[Callable[[dict[str, Any]], None], ...]` — No method docstring.
    - `clear(self, name) -> None` — No method docstring.
- **AgentSnapshot** (bases: object; decorators: dataclass) — Minimal agent view used for scaffolding.
  - Attributes: agent_id: str = None, position: tuple[int, int] = None, needs: dict[str, float] = None, wallet: float = 0.0, home_position: tuple[int, int] | None = None, origin_agent_id: str | None = None, personality: Personality = 'field(default_factory=_default_personality)', inventory: dict[str, int] = 'field(default_factory=dict)', job_id: str | None = None, on_shift: bool = False, lateness_counter: int = 0, last_late_tick: int = -1, … (10 more)
  - Methods:
    - `__post_init__(self) -> None` — No method docstring.
- **InteractiveObject** (bases: object; decorators: dataclass) — Represents an interactive world object with optional occupancy.
  - Attributes: object_id: str = None, object_type: str = None, occupied_by: str | None = None, stock: dict[str, int] = 'field(default_factory=dict)', position: tuple[int, int] | None = None
  - Methods: None.
- **RunningAffordance** (bases: object; decorators: dataclass) — Tracks an affordance currently executing on an object.
  - Attributes: agent_id: str = None, affordance_id: str = None, duration_remaining: int = None, effects: dict[str, float] = None
  - Methods: None.
- **AffordanceSpec** (bases: object; decorators: dataclass) — Static affordance definition loaded from configuration.
  - Attributes: affordance_id: str = None, object_type: str = None, duration: int = None, effects: dict[str, float] = None, preconditions: list[str] = 'field(default_factory=list)', hooks: dict[str, list[str]] = 'field(default_factory=dict)', compiled_preconditions: tuple[CompiledPrecondition, ...] = 'field(default_factory=tuple, repr=False)'
  - Methods: None.
- **WorldState** (bases: object; decorators: dataclass) — Holds mutable world state for the simulation tick.
  - Attributes: config: SimulationConfig = None, agents: dict[str, AgentSnapshot] = 'field(default_factory=dict)', tick: int = 0, queue_manager: QueueManager = 'field(init=False)', embedding_allocator: EmbeddingAllocator = 'field(init=False)', _active_reservations: dict[str, str] = 'field(init=False, default_factory=dict)', objects: dict[str, InteractiveObject] = 'field(init=False, default_factory=dict)', affordances: dict[str, AffordanceSpec] = 'field(init=False, default_factory=dict)', _running_affordances: dict[str, RunningAffordance] = 'field(init=False, default_factory=dict)', _pending_events: dict[int, list[dict[str, Any]]] = 'field(init=False, default_factory=dict)', store_stock: dict[str, dict[str, int]] = 'field(init=False, default_factory=dict)', _job_keys: list[str] = 'field(init=False, default_factory=list)', … (18 more)
  - Methods:
    - `from_config(cls, config) -> 'WorldState'` — Bootstrap the initial world from config.
    - `__post_init__(self) -> None` — No method docstring. Side effects: os.
    - `affordance_runtime(self) -> DefaultAffordanceRuntime` — No method docstring.
    - `runtime_instrumentation_level(self) -> str` — No method docstring.
    - `generate_agent_id(self, base_id) -> str` — No method docstring.
    - `apply_console(self, operations) -> None` — Apply console operations before the tick sequence runs.
    - `attach_rng(self, rng) -> None` — Attach a deterministic RNG used for world-level randomness.
    - `rng(self) -> random.Random` — No method docstring.
    - `get_rng_state(self) -> tuple[Any, ...]` — No method docstring.
    - `set_rng_state(self, state) -> None` — No method docstring.
    - `register_console_handler(self, name, handler) -> None` — Register a console handler for queued commands.
    - `register_affordance_hook(self, name, handler) -> None` — Register a callable invoked when a manifest hook fires.
    - `clear_affordance_hooks(self, name) -> None` — Clear registered affordance hooks (used primarily for tests).
    - `consume_console_results(self) -> list[ConsoleCommandResult]` — Return and clear buffered console results.
    - `_record_console_result(self, result) -> None` — No method docstring.
    - `_dispatch_affordance_hooks(self, stage, hook_names) -> bool` — No method docstring.
    - `_build_precondition_context(self) -> dict[str, Any]` — No method docstring.
    - `_snapshot_precondition_context(self, context) -> dict[str, Any]` — No method docstring.
    - `_register_default_console_handlers(self) -> None` — No method docstring.
    - `_console_noop_handler(self, envelope) -> ConsoleCommandResult` — No method docstring.
    - `_console_employment_status(self, envelope) -> ConsoleCommandResult` — No method docstring.
    - `_console_affordance_status(self, envelope) -> ConsoleCommandResult` — No method docstring.
    - `_console_employment_exit(self, envelope) -> ConsoleCommandResult` — No method docstring. Raises: ConsoleCommandError('usage', 'Unknown employment_exit action', details={'action': action}), ConsoleCommandError('usage', 'employment_exit <approve|defer> <agent_id>'), ConsoleCommandError('usage', 'employment_exit <review|approve|defer> [agent_id]').
    - `_assign_job_if_missing(self, snapshot) -> None` — No method docstring.
    - `remove_agent(self, agent_id, tick) -> dict[str, Any] | None` — No method docstring.
    - `respawn_agent(self, blueprint) -> None` — No method docstring.
    - `_sync_agent_spawn(self, snapshot) -> None` — No method docstring.
    - `_console_spawn_agent(self, envelope) -> ConsoleCommandResult` — No method docstring. Raises: ConsoleCommandError('conflict', 'agent already exists', details={'agent_id': agent_id}), ConsoleCommandError('invalid_args', 'home_position must be [x, y]'), ConsoleCommandError('invalid_args', 'home_position must be integers'), ConsoleCommandError('invalid_args', 'home_position not walkable', details={'home_position': [hx, hy]}), ConsoleCommandError('invalid_args', 'needs must be a mapping'), ConsoleCommandError('invalid_args', 'position must be [x, y]'), ConsoleCommandError('invalid_args', 'position must be integers'), ConsoleCommandError('invalid_args', 'position not walkable', details={'position': [x, y]}), ConsoleCommandError('invalid_args', 'spawn payload must be a mapping'), ConsoleCommandError('invalid_args', 'spawn requires agent_id').
    - `_console_teleport_agent(self, envelope) -> ConsoleCommandResult` — No method docstring. Raises: ConsoleCommandError('invalid_args', 'position must be [x, y]'), ConsoleCommandError('invalid_args', 'position must be integers'), ConsoleCommandError('invalid_args', 'position not walkable', details={'position': [x, y]}), ConsoleCommandError('invalid_args', 'teleport payload must be a mapping'), ConsoleCommandError('invalid_args', 'teleport requires agent_id'), ConsoleCommandError('not_found', 'agent not found', details={'agent_id': agent_id}).
    - `_release_queue_membership(self, agent_id) -> None` — No method docstring.
    - `_sync_reservation_for_agent(self, agent_id) -> None` — No method docstring.
    - `_is_position_walkable(self, position) -> bool` — No method docstring.
    - `kill_agent(self, agent_id) -> bool` — No method docstring.
    - `_console_set_need(self, envelope) -> ConsoleCommandResult` — No method docstring. Raises: ConsoleCommandError('invalid_args', 'need values must be numeric', details={'need': key}), ConsoleCommandError('invalid_args', 'needs must be a mapping of need names to values'), ConsoleCommandError('invalid_args', 'setneed payload must be a mapping'), ConsoleCommandError('invalid_args', 'setneed requires agent_id'), ConsoleCommandError('invalid_args', 'unknown need', details={'need': key}), ConsoleCommandError('not_found', 'agent not found', details={'agent_id': agent_id}).
    - `_console_set_price(self, envelope) -> ConsoleCommandResult` — No method docstring. Raises: ConsoleCommandError('invalid_args', 'price payload must be a mapping'), ConsoleCommandError('invalid_args', 'price requires key'), ConsoleCommandError('invalid_args', 'value must be numeric', details={'key': key}), ConsoleCommandError('not_found', 'unknown economy key', details={'key': key}).
    - `_console_force_chat(self, envelope) -> ConsoleCommandResult` — No method docstring. Raises: ConsoleCommandError('invalid_args', 'force_chat payload must be a mapping'), ConsoleCommandError('invalid_args', 'force_chat requires speaker and listener'), ConsoleCommandError('invalid_args', 'quality must be numeric', details={'quality': quality}), ConsoleCommandError('invalid_args', 'speaker and listener must differ'), ConsoleCommandError('not_found', 'listener not found', details={'agent_id': listener}), ConsoleCommandError('not_found', 'speaker not found', details={'agent_id': speaker}).
    - `_console_set_relationship(self, envelope) -> ConsoleCommandResult` — No method docstring. Raises: ConsoleCommandError('invalid_args', 'agent_a and agent_b must differ'), ConsoleCommandError('invalid_args', 'relationship values must be numeric'), ConsoleCommandError('invalid_args', 'set_rel payload must be a mapping'), ConsoleCommandError('invalid_args', 'set_rel requires agent_a and agent_b'), ConsoleCommandError('invalid_args', 'set_rel requires at least one of trust/familiarity/rivalry'), ConsoleCommandError('not_found', 'agent_a not found', details={'agent_id': agent_a}), ConsoleCommandError('not_found', 'agent_b not found', details={'agent_id': agent_b}).
    - `register_object(self) -> None` — Register or update an interactive object in the world.
    - `_index_object_position(self, object_id, position) -> None` — No method docstring.
    - `_unindex_object_position(self, object_id, position) -> None` — No method docstring.
    - `register_affordance(self) -> None` — Register an affordance available in the world. Raises: RuntimeError(f"Failed to compile preconditions for affordance '{affordance_id}': {exc}").
    - `apply_actions(self, actions) -> None` — Apply agent actions for the current tick.
    - `resolve_affordances(self, current_tick) -> None` — Resolve queued affordances and hooks.
    - `running_affordances_snapshot(self) -> dict[str, RunningAffordanceState]` — Return a serializable view of running affordances (for tests/telemetry).
    - `request_ctx_reset(self, agent_id) -> None` — Mark an agent so the next observation toggles ctx_reset_flag.
    - `consume_ctx_reset_requests(self) -> set[str]` — Return and clear pending ctx-reset requests.
    - `snapshot(self) -> dict[str, AgentSnapshot]` — Return a shallow copy of the agent dictionary for observers.
    - `local_view(self, agent_id, radius) -> dict[str, Any]` — Return local neighborhood information for observation builders.
    - `agent_context(self, agent_id) -> dict[str, object]` — Return scalar context fields for the requested agent.
    - `active_reservations(self) -> dict[str, str]` — Expose a copy of active reservations for diagnostics/tests.
    - `drain_events(self) -> list[dict[str, Any]]` — Return all pending events accumulated up to the current tick.
    - `_record_queue_conflict(self) -> None` — No method docstring.
    - `register_rivalry_conflict(self, agent_a, agent_b) -> None` — No method docstring.
    - `_apply_rivalry_conflict(self, agent_a, agent_b) -> None` — No method docstring.
    - `rivalry_snapshot(self) -> dict[str, dict[str, float]]` — Expose rivalry ledgers for telemetry/diagnostics.
    - `relationships_snapshot(self) -> dict[str, dict[str, dict[str, float]]]` — No method docstring.
    - `relationship_tie(self, agent_id, other_id) -> RelationshipTie | None` — Return the current relationship tie between two agents, if any.
    - `consume_chat_events(self) -> list[dict[str, Any]]` — Return chat events staged for reward calculations and clear the buffer.
    - `rivalry_value(self, agent_id, other_id) -> float` — Return the rivalry score between two agents, if present.
    - `rivalry_should_avoid(self, agent_id, other_id) -> bool` — No method docstring.
    - `rivalry_top(self, agent_id, limit) -> list[tuple[str, float]]` — No method docstring.
    - `consume_rivalry_events(self) -> list[dict[str, Any]]` — Return rivalry events recorded since the last call.
    - `_get_rivalry_ledger(self, agent_id) -> RivalryLedger` — No method docstring.
    - `_get_relationship_ledger(self, agent_id) -> RelationshipLedger` — No method docstring.
    - `_relationship_parameters(self) -> RelationshipParameters` — No method docstring.
    - `_personality_for(self, agent_id) -> Personality` — No method docstring.
    - `_apply_relationship_delta(self, owner_id, other_id) -> None` — No method docstring.
    - `_rivalry_parameters(self) -> RivalryParameters` — No method docstring.
    - `_decay_rivalry_ledgers(self) -> None` — No method docstring.
    - `_decay_relationship_ledgers(self) -> None` — No method docstring.
    - `_record_relationship_eviction(self, owner_id, other_id, reason) -> None` — No method docstring.
    - `relationship_metrics_snapshot(self) -> dict[str, object]` — No method docstring.
    - `load_relationship_snapshot(self, snapshot) -> None` — Restore relationship ledgers from persisted snapshot data.
    - `update_relationship(self, agent_a, agent_b) -> None` — No method docstring.
    - `record_chat_success(self, speaker, listener, quality) -> None` — No method docstring.
    - `record_chat_failure(self, speaker, listener) -> None` — No method docstring.
    - `_sync_reservation(self, object_id) -> None` — No method docstring.
    - `_handle_blocked(self, object_id, tick) -> None` — No method docstring.
    - `_start_affordance(self, agent_id, object_id, affordance_id) -> bool` — No method docstring.
    - `_apply_affordance_effects(self, agent_id, effects) -> None` — No method docstring.
    - `_emit_event(self, event, payload) -> None` — No method docstring.
    - `_load_affordance_definitions(self) -> None` — No method docstring. Side effects: filesystem. Raises: RuntimeError(f'Affordance manifest not found at {manifest_path}.'), RuntimeError(f'Failed to load affordance manifest {manifest_path}: {error}').
    - `affordance_manifest_metadata(self) -> dict[str, object]` — Expose manifest metadata (path, checksum, counts) for telemetry.
    - `find_nearest_object_of_type(self, object_type, origin) -> tuple[int, int] | None` — No method docstring.
    - `_apply_need_decay(self) -> None` — No method docstring.
    - `apply_nightly_reset(self) -> list[str]` — Return agents home, refresh needs, and reset employment flags.
    - `_assign_jobs_to_agents(self) -> None` — No method docstring.
    - `_apply_job_state(self) -> None` — No method docstring.
    - `_apply_job_state_legacy(self) -> None` — No method docstring.
    - `_apply_job_state_enforced(self) -> None` — No method docstring.
    - `_employment_context_defaults(self) -> dict[str, Any]` — No method docstring.
    - `_get_employment_context(self, agent_id) -> dict[str, Any]` — No method docstring.
    - `_employment_context_wages(self, agent_id) -> float` — No method docstring.
    - `_employment_context_punctuality(self, agent_id) -> float` — No method docstring.
    - `_employment_idle_state(self, snapshot, ctx) -> None` — No method docstring.
    - `_employment_prepare_state(self, snapshot, ctx) -> None` — No method docstring.
    - `_employment_begin_shift(self, ctx, start, end) -> None` — No method docstring.
    - `_employment_determine_state(self) -> str` — No method docstring.
    - `_employment_apply_state_effects(self) -> None` — No method docstring.
    - `_employment_finalize_shift(self) -> None` — No method docstring.
    - `_employment_coworkers_on_shift(self, snapshot) -> list[str]` — No method docstring.
    - `_employment_enqueue_exit(self, agent_id, tick) -> None` — No method docstring.
    - `_employment_remove_from_queue(self, agent_id) -> None` — No method docstring.
    - `employment_queue_snapshot(self) -> dict[str, Any]` — No method docstring.
    - `employment_request_manual_exit(self, agent_id, tick) -> bool` — No method docstring.
    - `employment_defer_exit(self, agent_id) -> bool` — No method docstring.
    - `employment_exits_today(self) -> int` — No method docstring.
    - `set_employment_exits_today(self, value) -> None` — No method docstring.
    - `reset_employment_exits_today(self) -> None` — No method docstring.
    - `increment_employment_exits_today(self) -> None` — No method docstring.
    - `_update_basket_metrics(self) -> None` — No method docstring.
    - `_restock_economy(self) -> None` — No method docstring.

### Functions
- `_default_personality() -> Personality` — Provide a neutral personality for agents lacking explicit traits.
  - Parameters: —
  - Returns: Personality

### Constants and Configuration
- `_CONSOLE_HISTORY_LIMIT` = 512
- `_CONSOLE_RESULT_BUFFER_LIMIT` = 256
- `_BASE_NEEDS` (tuple[str, ...]) = ["hunger", "hygiene", "energy"]

### Data Flow
- Inputs: —
- Outputs: Personality
- Internal interactions: —
- External interactions: AffordanceOutcome, AffordanceRuntimeContext, AffordanceSpec, AgentSnapshot, ConsoleBridge, ConsoleCommandError, ConsoleCommandResult.ok, DefaultAffordanceRuntime, EmbeddingAllocator, EmploymentEngine, HookRegistry, InteractiveObject, … (239 more)

### Integration Points
- Reads environment variables.
- Runtime calls: AffordanceOutcome, AffordanceRuntimeContext, AffordanceSpec, AgentSnapshot, ConsoleBridge, ConsoleCommandError, ConsoleCommandResult.ok, DefaultAffordanceRuntime, EmbeddingAllocator, EmploymentEngine, HookRegistry, InteractiveObject, … (239 more)

### Code Quality Notes
- Missing method docstrings: HookRegistry.__init__, HookRegistry.register, HookRegistry.handlers_for, HookRegistry.clear, AgentSnapshot.__post_init__, WorldState.__post_init__, WorldState.affordance_runtime, WorldState.runtime_instrumentation_level, WorldState.generate_agent_id, WorldState.rng, WorldState.get_rng_state, WorldState.set_rng_state, WorldState._record_console_result, WorldState._dispatch_affordance_hooks, WorldState._build_precondition_context, WorldState._snapshot_precondition_context, WorldState._register_default_console_handlers, WorldState._console_noop_handler, WorldState._console_employment_status, WorldState._console_affordance_status, WorldState._console_employment_exit, WorldState._assign_job_if_missing, WorldState.remove_agent, WorldState.respawn_agent, WorldState._sync_agent_spawn, WorldState._console_spawn_agent, WorldState._console_teleport_agent, WorldState._release_queue_membership, WorldState._sync_reservation_for_agent, WorldState._is_position_walkable, WorldState.kill_agent, WorldState._console_set_need, WorldState._console_set_price, WorldState._console_force_chat, WorldState._console_set_relationship, WorldState._index_object_position, WorldState._unindex_object_position, WorldState._record_queue_conflict, WorldState.register_rivalry_conflict, WorldState._apply_rivalry_conflict, WorldState.relationships_snapshot, WorldState.rivalry_should_avoid, WorldState.rivalry_top, WorldState._get_rivalry_ledger, WorldState._get_relationship_ledger, WorldState._relationship_parameters, WorldState._personality_for, WorldState._apply_relationship_delta, WorldState._rivalry_parameters, WorldState._decay_rivalry_ledgers, WorldState._decay_relationship_ledgers, WorldState._record_relationship_eviction, WorldState.relationship_metrics_snapshot, WorldState.update_relationship, WorldState.record_chat_success, WorldState.record_chat_failure, WorldState._sync_reservation, WorldState._handle_blocked, WorldState._start_affordance, WorldState._apply_affordance_effects, WorldState._emit_event, WorldState._load_affordance_definitions, WorldState.find_nearest_object_of_type, WorldState._apply_need_decay, WorldState._assign_jobs_to_agents, WorldState._apply_job_state, WorldState._apply_job_state_legacy, WorldState._apply_job_state_enforced, WorldState._employment_context_defaults, WorldState._get_employment_context, WorldState._employment_context_wages, WorldState._employment_context_punctuality, WorldState._employment_idle_state, WorldState._employment_prepare_state, WorldState._employment_begin_shift, WorldState._employment_determine_state, WorldState._employment_apply_state_effects, WorldState._employment_finalize_shift, WorldState._employment_coworkers_on_shift, WorldState._employment_enqueue_exit, WorldState._employment_remove_from_queue, WorldState.employment_queue_snapshot, WorldState.employment_request_manual_exit, WorldState.employment_defer_exit, WorldState.employment_exits_today, WorldState.set_employment_exits_today, WorldState.reset_employment_exits_today, WorldState.increment_employment_exits_today, WorldState._update_basket_metrics, WorldState._restock_economy


## src/townlet/world/hooks/__init__.py

**Purpose**: Affordance hook plug-in namespace.
**Dependencies**:
- Standard Library: __future__, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `load_modules(world, module_paths) -> None` — Import hook modules and let them register against the given world.
  - Parameters: world, module_paths
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: module_paths, world
- Outputs: None
- Internal interactions: —
- External interactions: import_module, register

### Integration Points
- Runtime calls: import_module, register

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet/world/hooks/default.py

**Purpose**: Built-in affordance hook handlers.
**Dependencies**:
- Standard Library: __future__, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `register_hooks(world) -> None` — Register built-in affordance hooks with the provided world.
  - Parameters: world
  - Returns: None
- `_on_attempt_shower(context) -> None` — No function docstring.
  - Parameters: context
  - Returns: None
- `_on_finish_shower(context) -> None` — No function docstring.
  - Parameters: context
  - Returns: None
- `_on_no_power(context) -> None` — No function docstring.
  - Parameters: context
  - Returns: None
- `_on_attempt_eat(context) -> None` — No function docstring.
  - Parameters: context
  - Returns: None
- `_on_finish_eat(context) -> None` — No function docstring.
  - Parameters: context
  - Returns: None
- `_on_attempt_cook(context) -> None` — No function docstring.
  - Parameters: context
  - Returns: None
- `_on_finish_cook(context) -> None` — No function docstring.
  - Parameters: context
  - Returns: None
- `_on_cook_fail(context) -> None` — No function docstring.
  - Parameters: context
  - Returns: None
- `_on_attempt_sleep(context) -> None` — No function docstring.
  - Parameters: context
  - Returns: None
- `_on_finish_sleep(context) -> None` — No function docstring.
  - Parameters: context
  - Returns: None
- `_abort_affordance(world, spec, agent_id, object_id, reason) -> None` — No function docstring.
  - Parameters: world, spec, agent_id, object_id, reason
  - Returns: None

### Constants and Configuration
- `_AFFORDANCE_FAIL_EVENT` = 'affordance_fail'
- `_SHOWER_COMPLETE_EVENT` = 'shower_complete'
- `_SHOWER_POWER_EVENT` = 'shower_power_outage'
- `_SLEEP_COMPLETE_EVENT` = 'sleep_complete'

### Data Flow
- Inputs: agent_id, context, object_id, reason, spec, world
- Outputs: None
- Internal interactions: —
- External interactions: _abort_affordance, obj.stock.get, obj.stock.setdefault, participants.add, record.get, snapshot.inventory.get, spec.hooks.get, world._dispatch_affordance_hooks, world._emit_event, world._recent_meal_participants.get, world._sync_reservation, world.affordance_runtime.running_affordances.pop, … (6 more)

### Integration Points
- Runtime calls: _abort_affordance, obj.stock.get, obj.stock.setdefault, participants.add, record.get, snapshot.inventory.get, spec.hooks.get, world._dispatch_affordance_hooks, world._emit_event, world._recent_meal_participants.get, world._sync_reservation, world.affordance_runtime.running_affordances.pop, … (6 more)

### Code Quality Notes
- Missing function docstrings: _on_attempt_shower, _on_finish_shower, _on_no_power, _on_attempt_eat, _on_finish_eat, _on_attempt_cook, _on_finish_cook, _on_cook_fail, _on_attempt_sleep, _on_finish_sleep, _abort_affordance


## src/townlet/world/preconditions.py

**Purpose**: Affordance precondition compilation and evaluation helpers.
**Dependencies**:
- Standard Library: __future__, ast, dataclasses, re, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- **PreconditionSyntaxError** (bases: ValueError; decorators: —) — Raised when a manifest precondition has invalid syntax.
  - Methods: None.
- **PreconditionEvaluationError** (bases: RuntimeError; decorators: —) — Raised when evaluation fails due to missing context or type errors.
  - Methods: None.
- **CompiledPrecondition** (bases: object; decorators: dataclass(frozen=True)) — Stores the parsed AST and metadata for a precondition.
  - Attributes: source: str = None, tree: ast.AST = None, identifiers: tuple[str, ...] = None
  - Methods: None.
- **_IdentifierCollector** (bases: ast.NodeVisitor; decorators: —) — No class docstring.
  - Methods:
    - `__init__(self) -> None` — No method docstring.
    - `visit_Name(self, node) -> None` — Collect bare identifiers used in the expression.

### Functions
- `_normalize_expression(expression) -> str` — No function docstring.
  - Parameters: expression
  - Returns: str
- `_validate_tree(tree, source) -> tuple[str, ...]` — No function docstring. Raises: PreconditionSyntaxError(f"Function calls are not permitted in precondition '{source}'"), PreconditionSyntaxError(f"Unsupported boolean operator in precondition '{source}'"), PreconditionSyntaxError(f"Unsupported comparison operator in precondition '{source}'"), PreconditionSyntaxError(f"Unsupported syntax in precondition '{source}': {type(node).__name__}"), PreconditionSyntaxError(f"Unsupported unary operator in precondition '{source}'").
  - Parameters: tree, source
  - Returns: tuple[str, ...]
- `compile_preconditions(expressions) -> tuple[CompiledPrecondition, ...]` — Compile manifest preconditions, raising on syntax errors. Raises: PreconditionSyntaxError(f"Invalid syntax in precondition '{expression}': {exc.msg}").
  - Parameters: expressions
  - Returns: tuple[CompiledPrecondition, ...]
- `compile_precondition(expression) -> CompiledPrecondition` — Compile a single precondition expression.
  - Parameters: expression
  - Returns: CompiledPrecondition
- `_resolve_name(name, context) -> Any` — No function docstring.
  - Parameters: name, context
  - Returns: Any
- `_resolve_attr(value, attr) -> Any` — No function docstring.
  - Parameters: value, attr
  - Returns: Any
- `_resolve_subscript(value, key) -> Any` — No function docstring.
  - Parameters: value, key
  - Returns: Any
- `_evaluate(node, context) -> Any` — No function docstring. Raises: PreconditionEvaluationError('Slices are not supported in preconditions'), PreconditionEvaluationError(f'Unsupported AST node during evaluation: {type(node).__name__}'), PreconditionEvaluationError(f'Unsupported boolean operator: {type(node.op).__name__}'), PreconditionEvaluationError(f'Unsupported unary operator: {type(node.op).__name__}').
  - Parameters: node, context
  - Returns: Any
- `_apply_compare(operator, left, right) -> bool` — No function docstring. Raises: PreconditionEvaluationError(f'Unsupported comparison operator: {type(operator).__name__}').
  - Parameters: operator, left, right
  - Returns: bool
- `evaluate_preconditions(preconditions, context) -> tuple[bool, CompiledPrecondition | None]` — Evaluate compiled preconditions against the provided context.  Returns ------- tuple     ``(True, None)`` if all preconditions pass, otherwise ``(False, failed)``     where ``failed`` references the first failing precondition.
  - Parameters: preconditions, context
  - Returns: tuple[bool, CompiledPrecondition | None]

### Constants and Configuration
- `_ALLOWED_COMPARE_OPS` = '(ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn)'
- `_ALLOWED_BOOL_OPS` = '(ast.And, ast.Or)'
- `_ALLOWED_UNARY_OPS` = '(ast.Not, ast.USub, ast.UAdd)'
- `_ALLOWED_NODE_TYPES` = '(ast.Expression, ast.BoolOp, ast.Compare, ast.Name, ast.Attribute, ast.Subscript, ast.Constant, ast.UnaryOp, ast.Tuple, ast.List, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn, ast.And, ast.Or, ast.Load, ast.USub, ast.UAdd, ast.Not)'

### Data Flow
- Inputs: attr, context, expression, expressions, key, left, name, node, operator, preconditions, right, source, tree, value
- Outputs: Any, CompiledPrecondition, bool, str, tuple[CompiledPrecondition, ...], tuple[bool, CompiledPrecondition | None], tuple[str, ...]
- Internal interactions: —
- External interactions: CompiledPrecondition, PreconditionEvaluationError, PreconditionSyntaxError, _IdentifierCollector, _apply_compare, _evaluate, _name_pattern.sub, _name_replacements.get, _normalize_expression, _resolve_attr, _resolve_name, _resolve_subscript, … (12 more)

### Integration Points
- Runtime calls: CompiledPrecondition, PreconditionEvaluationError, PreconditionSyntaxError, _IdentifierCollector, _apply_compare, _evaluate, _name_pattern.sub, _name_replacements.get, _normalize_expression, _resolve_attr, _resolve_name, _resolve_subscript, … (12 more)

### Code Quality Notes
- Missing function docstrings: _normalize_expression, _validate_tree, _resolve_name, _resolve_attr, _resolve_subscript, _evaluate, _apply_compare
- Missing method docstrings: _IdentifierCollector.__init__


## src/townlet/world/queue_conflict.py

**Purpose**: Queue conflict and rivalry event tracking.
**Dependencies**:
- Standard Library: __future__, collections, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- **QueueConflictTracker** (bases: object; decorators: —) — Tracks queue conflict outcomes and rivalry/chat events.
  - Methods:
    - `__init__(self) -> None` — No method docstring.
    - `record_queue_conflict(self) -> None` — No method docstring.
    - `record_chat_event(self, payload) -> None` — No method docstring.
    - `consume_chat_events(self) -> list[dict[str, object]]` — No method docstring.
    - `record_rivalry_event(self) -> None` — No method docstring.
    - `consume_rivalry_events(self) -> list[dict[str, object]]` — No method docstring.
    - `reset(self) -> None` — No method docstring.
    - `remove_agent(self, agent_id) -> None` — No method docstring.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: deque, entry.get, event.get, self._chat_events.append, self._chat_events.clear, self._record_rivalry_conflict_cb, self._rivalry_events.append, self._rivalry_events.clear, self.record_rivalry_event, world._emit_event, world.update_relationship

### Integration Points
- Runtime calls: deque, entry.get, event.get, self._chat_events.append, self._chat_events.clear, self._record_rivalry_conflict_cb, self._rivalry_events.append, self._rivalry_events.clear, self.record_rivalry_event, world._emit_event, world.update_relationship

### Code Quality Notes
- Missing method docstrings: QueueConflictTracker.__init__, QueueConflictTracker.record_queue_conflict, QueueConflictTracker.record_chat_event, QueueConflictTracker.consume_chat_events, QueueConflictTracker.record_rivalry_event, QueueConflictTracker.consume_rivalry_events, QueueConflictTracker.reset, QueueConflictTracker.remove_agent


## src/townlet/world/queue_manager.py

**Purpose**: Queue management with fairness guardrails.
**Dependencies**:
- Standard Library: __future__, dataclasses, time
- Third-Party: —
- Internal: townlet.config
**Related modules**: townlet.config

### Classes
- **QueueEntry** (bases: object; decorators: dataclass) — Represents an agent waiting to access an interactive object.
  - Attributes: agent_id: str = None, joined_tick: int = None
  - Methods: None.
- **QueueManager** (bases: object; decorators: —) — Coordinates reservations and fairness across interactive queues.
  - Methods:
    - `__init__(self, config) -> None` — No method docstring.
    - `on_tick(self, tick) -> None` — Expire cooldown entries whose window has elapsed.
    - `request_access(self, object_id, agent_id, tick) -> bool` — Attempt to reserve the object for the agent.  Returns True if the agent is granted the reservation immediately, otherwise the agent is queued and False is returned.
    - `release(self, object_id, agent_id, tick) -> None` — Release the reservation and optionally apply cooldown.
    - `record_blocked_attempt(self, object_id) -> bool` — Register that the current head was blocked.  Returns True if a ghost-step should be triggered for the head agent.
    - `active_agent(self, object_id) -> str | None` — Return the agent currently holding the reservation, if any.
    - `queue_snapshot(self, object_id) -> list[str]` — Return the queue as an ordered list of agent IDs for debugging.
    - `metrics(self) -> dict[str, int]` — Expose counters useful for telemetry.
    - `performance_metrics(self) -> dict[str, int]` — Expose aggregated nanosecond timings and call counts.
    - `reset_performance_metrics(self) -> None` — No method docstring.
    - `requeue_to_tail(self, object_id, agent_id, tick) -> None` — Append `agent_id` to the end of the queue if not already present.
    - `remove_agent(self, agent_id, tick) -> None` — Remove `agent_id` from all queues and active reservations.
    - `export_state(self) -> dict[str, object]` — Serialise queue activity for snapshot persistence.
    - `import_state(self, payload) -> None` — Restore queue activity from persisted snapshot data.
    - `_assign_next(self, object_id, tick) -> str | None` — No method docstring.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: QueueEntry, active.items, entry.get, object_entries.append, payload.get, queue.append, queue.pop, queues_payload.items, self._active.get, self._active.items, self._assign_next, self._cooldowns.get, … (11 more)

### Integration Points
- Runtime calls: QueueEntry, active.items, entry.get, object_entries.append, payload.get, queue.append, queue.pop, queues_payload.items, self._active.get, self._active.items, self._assign_next, self._cooldowns.get, … (11 more)

### Code Quality Notes
- Missing method docstrings: QueueManager.__init__, QueueManager.reset_performance_metrics, QueueManager._assign_next


## src/townlet/world/relationships.py

**Purpose**: Relationship ledger for Phase 4 social systems.
**Dependencies**:
- Standard Library: __future__, collections.abc, dataclasses
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- **RelationshipParameters** (bases: object; decorators: dataclass) — Tuning knobs for relationship tie evolution.
  - Attributes: max_edges: int = 6, trust_decay: float = 0.0, familiarity_decay: float = 0.0, rivalry_decay: float = 0.01
  - Methods: None.
- **RelationshipTie** (bases: object; decorators: dataclass) — No class docstring.
  - Attributes: trust: float = 0.0, familiarity: float = 0.0, rivalry: float = 0.0
  - Methods:
    - `as_dict(self) -> dict[str, float]` — No method docstring.
- **RelationshipLedger** (bases: object; decorators: —) — Maintains multi-dimensional ties for a single agent.
  - Methods:
    - `__init__(self) -> None` — No method docstring.
    - `apply_delta(self, other_id) -> RelationshipTie` — No method docstring.
    - `tie_for(self, other_id) -> RelationshipTie | None` — Return the tie for ``other_id`` if it exists.
    - `decay(self) -> None` — No method docstring.
    - `snapshot(self) -> dict[str, dict[str, float]]` — No method docstring.
    - `inject(self, payload) -> None` — No method docstring.
    - `set_eviction_hook(self) -> None` — No method docstring.
    - `top_friends(self, limit) -> list[tuple[str, RelationshipTie]]` — No method docstring.
    - `top_rivals(self, limit) -> list[tuple[str, RelationshipTie]]` — No method docstring.
    - `remove_tie(self, other_id) -> None` — No method docstring.
    - `_prune_if_needed(self) -> None` — No method docstring.
    - `_emit_eviction(self, other_id) -> None` — No method docstring.

### Functions
- `_clamp(value) -> float` — No function docstring.
  - Parameters: value
  - Returns: float
- `_decay_value(value, decay) -> float` — No function docstring.
  - Parameters: value, decay
  - Returns: float

### Constants and Configuration
- None.

### Data Flow
- Inputs: decay, value
- Outputs: float
- Internal interactions: —
- External interactions: RelationshipParameters, RelationshipTie, _clamp, _decay_value, payload.items, removes.append, self._emit_eviction, self._eviction_hook, self._prune_if_needed, self._ties.clear, self._ties.get, self._ties.items, … (3 more)

### Integration Points
- Runtime calls: RelationshipParameters, RelationshipTie, _clamp, _decay_value, payload.items, removes.append, self._emit_eviction, self._eviction_hook, self._prune_if_needed, self._ties.clear, self._ties.get, self._ties.items, … (3 more)

### Code Quality Notes
- Missing function docstrings: _clamp, _decay_value
- Missing method docstrings: RelationshipTie.as_dict, RelationshipLedger.__init__, RelationshipLedger.apply_delta, RelationshipLedger.decay, RelationshipLedger.snapshot, RelationshipLedger.inject, RelationshipLedger.set_eviction_hook, RelationshipLedger.top_friends, RelationshipLedger.top_rivals, RelationshipLedger.remove_tie, RelationshipLedger._prune_if_needed, RelationshipLedger._emit_eviction


## src/townlet/world/rivalry.py

**Purpose**: Rivalry state helpers used by conflict intro scaffolding.
**Dependencies**:
- Standard Library: __future__, collections.abc, dataclasses, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- **RivalryParameters** (bases: object; decorators: dataclass) — Tuning knobs for rivalry evolution.  The defaults align with the conceptual design placeholder values and are expected to be replaced with config-backed settings during integration.
  - Attributes: increment_per_conflict: float = 0.15, decay_per_tick: float = 0.01, min_value: float = 0.0, max_value: float = 1.0, avoid_threshold: float = 0.7, eviction_threshold: float = 0.05, max_edges: int = 6
  - Methods: None.
- **RivalryLedger** (bases: object; decorators: dataclass) — Maintains rivalry scores against other agents for a single actor.
  - Attributes: owner_id: str = None, params: RivalryParameters = 'field(default_factory=RivalryParameters)', eviction_hook: Optional[Callable[[str, str, str], None]] = None, _scores: dict[str, float] = 'field(default_factory=dict)'
  - Methods:
    - `apply_conflict(self, other_id) -> float` — Increase rivalry against `other_id` based on the conflict intensity.
    - `decay(self, ticks) -> None` — Apply passive decay across all rivalry edges.
    - `inject(self, pairs) -> None` — Seed rivalry scores from persisted state for round-tripping tests.
    - `score_for(self, other_id) -> float` — No method docstring.
    - `should_avoid(self, other_id) -> bool` — Return True when rivalry exceeds the avoidance threshold.
    - `top_rivals(self, limit) -> list[tuple[str, float]]` — Return the strongest rivalry edges sorted descending.
    - `remove(self, other_id) -> None` — No method docstring.
    - `encode_features(self, limit) -> list[float]` — Encode rivalry magnitudes into a fixed-width list for observations.
    - `snapshot(self) -> dict[str, float]` — Return a copy of rivalry scores for telemetry serialization.
    - `_emit_eviction(self, other_id) -> None` — No method docstring.

### Functions
- `_clamp(value) -> float` — No function docstring.
  - Parameters: value
  - Returns: float

### Constants and Configuration
- None.

### Data Flow
- Inputs: value
- Outputs: float
- Internal interactions: —
- External interactions: _clamp, evicted.append, features.append, self._emit_eviction, self._scores.get, self._scores.items, self._scores.pop, self.eviction_hook, self.top_rivals

### Integration Points
- Runtime calls: _clamp, evicted.append, features.append, self._emit_eviction, self._scores.get, self._scores.items, self._scores.pop, self.eviction_hook, self.top_rivals

### Code Quality Notes
- Missing function docstrings: _clamp
- Missing method docstrings: RivalryLedger.score_for, RivalryLedger.remove, RivalryLedger._emit_eviction


## src/townlet_ui/__init__.py

**Purpose**: Observer UI toolkit exports.
**Dependencies**:
- Standard Library: —
- Third-Party: commands, telemetry
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: —

### Integration Points
- Third-party libraries: commands, telemetry

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## src/townlet_ui/commands.py

**Purpose**: Helper utilities for dispatching console commands asynchronously.
**Dependencies**:
- Standard Library: __future__, logging, queue, threading, typing
- Third-Party: —
- Internal: townlet.console.handlers
**Related modules**: townlet.console.handlers

### Classes
- **ConsoleCommandExecutor** (bases: object; decorators: —) — Background dispatcher that forwards console commands via a router.
  - Methods:
    - `__init__(self, router) -> None` — No method docstring. Raises: TypeError('Router must expose a dispatch method').
    - `submit(self, command) -> None` — No method docstring.
    - `shutdown(self, timeout) -> None` — No method docstring.
    - `_worker(self) -> None` — No method docstring.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: logger.exception, queue.Queue, self._queue.get, self._queue.put, self._router.dispatch, self._thread.join, self._thread.start, threading.Thread

### Integration Points
- Runtime calls: logger.exception, queue.Queue, self._queue.get, self._queue.put, self._router.dispatch, self._thread.join, self._thread.start, threading.Thread

### Code Quality Notes
- Missing method docstrings: ConsoleCommandExecutor.__init__, ConsoleCommandExecutor.submit, ConsoleCommandExecutor.shutdown, ConsoleCommandExecutor._worker


## src/townlet_ui/dashboard.py

**Purpose**: Rich-based console dashboard for Townlet observer UI.
**Dependencies**:
- Standard Library: __future__, collections.abc, math, time, typing
- Third-Party: numpy, rich.console, rich.panel, rich.table, rich.text
- Internal: townlet.console.handlers, townlet_ui.commands, townlet_ui.telemetry
**Related modules**: townlet.console.handlers, townlet_ui.commands, townlet_ui.telemetry

### Classes
- None defined.

### Functions
- `render_snapshot(snapshot, tick, refreshed) -> Iterable[Panel]` — Yield rich Panels representing the current telemetry snapshot.
  - Parameters: snapshot, tick, refreshed
  - Returns: Iterable[Panel]
- `_format_top_entries(entries) -> str` — No function docstring.
  - Parameters: entries
  - Returns: str
- `_build_narration_panel(snapshot) -> Panel` — No function docstring.
  - Parameters: snapshot
  - Returns: Panel
- `_build_anneal_panel(snapshot) -> Panel` — No function docstring.
  - Parameters: snapshot
  - Returns: Panel
- `_promotion_border_style(promotion) -> str` — No function docstring.
  - Parameters: promotion
  - Returns: str
- `_derive_promotion_reason(promotion, status) -> str` — No function docstring.
  - Parameters: promotion, status
  - Returns: str
- `_format_metadata_summary(metadata) -> str` — No function docstring.
  - Parameters: metadata
  - Returns: str
- `_build_promotion_history_panel(history, border_style) -> Panel` — No function docstring.
  - Parameters: history, border_style
  - Returns: Panel
- `_format_history_metadata(entry) -> str` — No function docstring.
  - Parameters: entry
  - Returns: str
- `_safe_format(value) -> str` — No function docstring.
  - Parameters: value
  - Returns: str
- `_format_optional_float(value) -> str` — No function docstring.
  - Parameters: value
  - Returns: str
- `_build_policy_inspector_panel(snapshot) -> Panel` — No function docstring.
  - Parameters: snapshot
  - Returns: Panel
- `_build_relationship_overlay_panel(snapshot) -> Panel` — No function docstring.
  - Parameters: snapshot
  - Returns: Panel
- `_format_delta(value, inverse) -> str` — No function docstring.
  - Parameters: value, inverse
  - Returns: str
- `_build_kpi_panel(snapshot) -> Panel` — No function docstring.
  - Parameters: snapshot
  - Returns: Panel
- `_trend_from_series(series) -> tuple[str, str]` — No function docstring.
  - Parameters: series
  - Returns: tuple[str, str]
- `_humanize_kpi(key) -> str` — No function docstring.
  - Parameters: key
  - Returns: str
- `run_dashboard(loop) -> None` — Continuously render dashboard against a SimulationLoop instance.
  - Parameters: loop
  - Returns: None
- `_build_map_panel(snapshot, obs_batch, focus_agent, show_coords) -> Panel | None` — No function docstring.
  - Parameters: snapshot, obs_batch, focus_agent, show_coords
  - Returns: Panel | None

### Constants and Configuration
- `MAP_AGENT_CHAR` = 'A'
- `MAP_CENTER_CHAR` = 'S'
- `NARRATION_CATEGORY_STYLES` (dict[str, tuple[str, str]]) = {"utility_outage": ["Utility Outage", "bold red"], "shower_complete": ["Shower Complete", "cyan"], "sleep_complete": ["Sleep Complete", "green"], "queue_conflict": ["Queue Conflict", "magenta"]}

### Data Flow
- Inputs: border_style, entries, entry, focus_agent, history, inverse, key, loop, metadata, obs_batch, promotion, refreshed, series, show_coords, snapshot, status, tick, value
- Outputs: Iterable[Panel], None, Panel, Panel | None, str, tuple[str, str]
- Internal interactions: —
- External interactions: AgentSnapshot, Console, ConsoleCommand, ConsoleCommandExecutor, Group, NARRATION_CATEGORY_STYLES.get, Panel, Panel.fit, Table, Table.grid, TelemetryClient, Text, … (75 more)

### Integration Points
- Runtime calls: AgentSnapshot, Console, ConsoleCommand, ConsoleCommandExecutor, Group, NARRATION_CATEGORY_STYLES.get, Panel, Panel.fit, Table, Table.grid, TelemetryClient, Text, … (75 more)
- Third-party libraries: numpy, rich.console, rich.panel, rich.table, rich.text

### Code Quality Notes
- Missing function docstrings: _format_top_entries, _build_narration_panel, _build_anneal_panel, _promotion_border_style, _derive_promotion_reason, _format_metadata_summary, _build_promotion_history_panel, _format_history_metadata, _safe_format, _format_optional_float, _build_policy_inspector_panel, _build_relationship_overlay_panel, _format_delta, _build_kpi_panel, _trend_from_series, _humanize_kpi, _build_map_panel


## src/townlet_ui/telemetry.py

**Purpose**: Schema-aware telemetry client utilities for observer UI components.
**Dependencies**:
- Standard Library: __future__, collections.abc, dataclasses, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- **EmploymentMetrics** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: pending: list[str] = None, pending_count: int = None, exits_today: int = None, daily_exit_cap: int = None, queue_limit: int = None, review_window: int = None
  - Methods: None.
- **QueueHistoryEntry** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: tick: int = None, cooldown_delta: int = None, ghost_step_delta: int = None, rotation_delta: int = None, totals: Mapping[str, int] = None
  - Methods: None.
- **RivalryEventEntry** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: tick: int = None, agent_a: str = None, agent_b: str = None, intensity: float = None, reason: str = None
  - Methods: None.
- **ConflictMetrics** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: queue_cooldown_events: int = None, queue_ghost_step_events: int = None, queue_rotation_events: int = None, queue_history: tuple[QueueHistoryEntry, ...] = None, rivalry_agents: int = None, rivalry_events: tuple[RivalryEventEntry, ...] = None, raw: Mapping[str, Any] = None
  - Methods: None.
- **AffordanceRuntimeSnapshot** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: running_count: int = None, running: Mapping[str, Mapping[str, Any]] = None, active_reservations: Mapping[str, str] = None, event_counts: Mapping[str, int] = None
  - Methods: None.
- **NarrationEntry** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: tick: int = None, category: str = None, message: str = None, priority: bool = None, data: Mapping[str, Any] = None
  - Methods: None.
- **RelationshipChurn** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: window_start: int = None, window_end: int = None, total_evictions: int = None, per_owner: Mapping[str, int] = None, per_reason: Mapping[str, int] = None
  - Methods: None.
- **RelationshipUpdate** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: owner: str = None, other: str = None, status: str = None, trust: float = None, familiarity: float = None, rivalry: float = None, delta_trust: float = None, delta_familiarity: float = None, delta_rivalry: float = None
  - Methods: None.
- **AgentSummary** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: agent_id: str = None, wallet: float = None, shift_state: str = None, attendance_ratio: float = None, wages_withheld: float = None, lateness_counter: int = None, on_shift: bool = None
  - Methods: None.
- **RelationshipOverlayEntry** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: other: str = None, trust: float = None, familiarity: float = None, rivalry: float = None, delta_trust: float = None, delta_familiarity: float = None, delta_rivalry: float = None
  - Methods: None.
- **PolicyInspectorAction** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: action: str = None, probability: float = None
  - Methods: None.
- **PolicyInspectorEntry** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: agent_id: str = None, tick: int = None, selected_action: str = None, log_prob: float = None, value_pred: float = None, top_actions: list[PolicyInspectorAction] = None
  - Methods: None.
- **AnnealStatus** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: stage: str = None, cycle: float | None = None, dataset: str = None, bc_accuracy: float | None = None, bc_threshold: float | None = None, bc_passed: bool = None, loss_flag: bool = None, queue_flag: bool = None, intensity_flag: bool = None, loss_baseline: float | None = None, queue_baseline: float | None = None, intensity_baseline: float | None = None
  - Methods: None.
- **TransportStatus** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: connected: bool = None, dropped_messages: int = None, last_error: str | None = None, last_success_tick: int | None = None, last_failure_tick: int | None = None, queue_length: int = None, last_flush_duration_ms: float | None = None
  - Methods: None.
- **StabilitySnapshot** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: alerts: tuple[str, ...] = None, metrics: Mapping[str, Any] = None
  - Methods: None.
- **HealthStatus** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: tick: int = None, tick_duration_ms: float = None, telemetry_queue: int = None, telemetry_dropped: int = None, perturbations_pending: int = None, perturbations_active: int = None, employment_exit_queue: int = None, raw: Mapping[str, Any] = None
  - Methods: None.
- **PromotionSnapshot** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: state: str | None = None, pass_streak: int = None, required_passes: int = None, candidate_ready: bool = None, candidate_ready_tick: int | None = None, last_result: str | None = None, last_evaluated_tick: int | None = None, candidate_metadata: Mapping[str, Any] | None = None, current_release: Mapping[str, Any] | None = None, history: tuple[Mapping[str, Any], ...] = None
  - Methods: None.
- **TelemetrySnapshot** (bases: object; decorators: dataclass(frozen=True)) — No class docstring.
  - Attributes: schema_version: str = None, schema_warning: str | None = None, employment: EmploymentMetrics = None, affordance_runtime: AffordanceRuntimeSnapshot = None, conflict: ConflictMetrics = None, narrations: list[NarrationEntry] = None, narration_state: Mapping[str, Any] = None, relationships: RelationshipChurn | None = None, relationship_snapshot: Mapping[str, Mapping[str, Mapping[str, float]]] = None, relationship_updates: list[RelationshipUpdate] = None, relationship_overlay: Mapping[str, list[RelationshipOverlayEntry]] = None, agents: list[AgentSummary] = None, … (8 more)
  - Methods: None.
- **SchemaMismatchError** (bases: RuntimeError; decorators: —) — Raised when telemetry schema is newer than the client supports.
  - Methods: None.
- **TelemetryClient** (bases: object; decorators: —) — Lightweight helper to parse telemetry payloads for the observer UI.
  - Methods:
    - `__init__(self) -> None` — No method docstring.
    - `parse_snapshot(self, payload) -> TelemetrySnapshot` — Validate and convert a telemetry payload into dataclasses. Raises: SchemaMismatchError('Telemetry payload missing schema_version').
    - `from_console(self, router) -> TelemetrySnapshot` — Fetch snapshot via console router (expects telemetry_snapshot command). Raises: TypeError('Console returned non-mapping telemetry payload'), TypeError('Console router must expose a dispatch callable').
    - `_check_schema(self, version) -> str | None` — No method docstring. Raises: SchemaMismatchError(message).
    - `_get_section(payload, key, expected) -> Mapping[str, Any]` — No method docstring. Raises: SchemaMismatchError(f"Telemetry payload missing expected section '{key}'").

### Functions
- `_maybe_float(value) -> float | None` — No function docstring.
  - Parameters: value
  - Returns: float | None
- `_coerce_float(value, default) -> float` — No function docstring.
  - Parameters: value, default
  - Returns: float
- `_coerce_mapping(value) -> Mapping[str, Any] | None` — No function docstring.
  - Parameters: value
  - Returns: Mapping[str, Any] | None
- `_coerce_history_entries(value) -> tuple[Mapping[str, Any], ...]` — No function docstring.
  - Parameters: value
  - Returns: tuple[Mapping[str, Any], ...]
- `_console_command(name) -> Any` — Helper to build console command dataclass without importing CLI package.
  - Parameters: name
  - Returns: Any

### Constants and Configuration
- `SUPPORTED_SCHEMA_PREFIX` = '0.9'

### Data Flow
- Inputs: default, name, value
- Outputs: Any, Mapping[str, Any] | None, float, float | None, tuple[Mapping[str, Any], ...]
- Internal interactions: —
- External interactions: AffordanceRuntimeSnapshot, AgentSummary, AnnealStatus, ConflictMetrics, ConsoleCommand, EmploymentMetrics, HealthStatus, NarrationEntry, PolicyInspectorAction, PolicyInspectorEntry, PromotionSnapshot, QueueHistoryEntry, … (67 more)

### Integration Points
- Runtime calls: AffordanceRuntimeSnapshot, AgentSummary, AnnealStatus, ConflictMetrics, ConsoleCommand, EmploymentMetrics, HealthStatus, NarrationEntry, PolicyInspectorAction, PolicyInspectorEntry, PromotionSnapshot, QueueHistoryEntry, … (67 more)

### Code Quality Notes
- Missing function docstrings: _maybe_float, _coerce_float, _coerce_mapping, _coerce_history_entries
- Missing method docstrings: TelemetryClient.__init__, TelemetryClient._check_schema, TelemetryClient._get_section


## tests/__init__.py

**Purpose**: Pytest coverage for   init  .
**Dependencies**:
- Standard Library: —
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- None defined.

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: —
- Internal interactions: —
- External interactions: —

### Integration Points
- None noted.

### Code Quality Notes
- No major code quality concerns flagged by static scan.


## tests/conftest.py

**Purpose**: Pytest configuration ensuring project imports resolve during tests.
**Dependencies**:
- Standard Library: __future__, pathlib, sys
- Third-Party: pytest
- Internal: tests.runtime_stubs
**Related modules**: —

### Classes
- None defined.

### Functions
- `stub_affordance_runtime_factory() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- `ROOT` = 'Path(__file__).resolve().parents[1]'
- `SRC` = "ROOT / 'src'"

### Data Flow
- Inputs: —
- Outputs: None
- Internal interactions: —
- External interactions: StubAffordanceRuntime

### Integration Points
- Runtime calls: StubAffordanceRuntime
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: stub_affordance_runtime_factory


## tests/runtime_stubs.py

**Purpose**: Stub affordance runtime implementations used by tests.
**Dependencies**:
- Standard Library: __future__, typing
- Third-Party: —
- Internal: townlet.world.affordances
**Related modules**: townlet.world.affordances

### Classes
- **StubAffordanceRuntime** (bases: object; decorators: —) — Minimal affordance runtime used for testing configuration plumbing.
  - Methods:
    - `__init__(self, context) -> None` — No method docstring.
    - `start(self, agent_id, object_id, affordance_id) -> tuple[bool, dict[str, object]]` — No method docstring.
    - `release(self, agent_id, object_id) -> tuple[str | None, dict[str, object]]` — No method docstring.
    - `resolve(self) -> None` — No method docstring.
    - `running_snapshot(self) -> dict[str, Any]` — No method docstring.
    - `clear(self) -> None` — No method docstring.
    - `remove_agent(self, agent_id) -> None` — No method docstring.
    - `handle_blocked(self, object_id, tick) -> None` — No method docstring.

### Functions
- `build_runtime() -> StubAffordanceRuntime` — Factory used by runtime configuration tests.
  - Parameters: —
  - Returns: StubAffordanceRuntime

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: StubAffordanceRuntime
- Internal interactions: —
- External interactions: StubAffordanceRuntime, self.started.append, self.started.clear

### Integration Points
- Runtime calls: StubAffordanceRuntime, self.started.append, self.started.clear

### Code Quality Notes
- Missing method docstrings: StubAffordanceRuntime.__init__, StubAffordanceRuntime.start, StubAffordanceRuntime.release, StubAffordanceRuntime.resolve, StubAffordanceRuntime.running_snapshot, StubAffordanceRuntime.clear, StubAffordanceRuntime.remove_agent, StubAffordanceRuntime.handle_blocked


## tests/test_affordance_hooks.py

**Purpose**: Pytest coverage for test affordance hooks.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: —
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Classes
- None defined.

### Functions
- `make_world() -> tuple[SimulationLoop, WorldState]` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: tuple[SimulationLoop, WorldState]
- `request_object(world, object_id, agent_id) -> None` — No function docstring.
  - Parameters: world, object_id, agent_id
  - Returns: None
- `test_affordance_before_after_hooks_fire_once() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_affordance_fail_hook_runs_once_per_failure() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_shower_requires_power() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_shower_completion_emits_event() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_sleep_slots_cycle_and_completion_event() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_sleep_attempt_fails_when_no_slots() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_runtime_running_snapshot_and_remove_agent() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_affordance_outcome_log_is_capped() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: agent_id, object_id, world
- Outputs: None, tuple[SimulationLoop, WorldState]
- Internal interactions: —
- External interactions: AgentSnapshot, Path, SimulationLoop, bed.stock.setdefault, ctx.get, hook_log.append, inventory.get, load_config, make_world, request_object, world._start_affordance, world._sync_reservation, … (12 more)

### Integration Points
- Runtime calls: AgentSnapshot, Path, SimulationLoop, bed.stock.setdefault, ctx.get, hook_log.append, inventory.get, load_config, make_world, request_object, world._start_affordance, world._sync_reservation, … (12 more)

### Code Quality Notes
- Missing function docstrings: make_world, request_object, test_affordance_before_after_hooks_fire_once, test_affordance_fail_hook_runs_once_per_failure, test_shower_requires_power, test_shower_completion_emits_event, test_sleep_slots_cycle_and_completion_event, test_sleep_attempt_fails_when_no_slots, test_runtime_running_snapshot_and_remove_agent, test_affordance_outcome_log_is_capped


## tests/test_affordance_manifest.py

**Purpose**: Pytest coverage for test affordance manifest.
**Dependencies**:
- Standard Library: __future__, hashlib, pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.telemetry.publisher, townlet.world.grid
**Related modules**: townlet.config, townlet.telemetry.publisher, townlet.world.grid

### Classes
- None defined.

### Functions
- `_configure_with_manifest(manifest_path) -> SimulationConfig` — No function docstring. Side effects: filesystem.
  - Parameters: manifest_path
  - Returns: SimulationConfig
- `test_affordance_manifest_loads_and_exposes_metadata(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_affordance_manifest_duplicate_ids_fail(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_affordance_manifest_missing_duration_fails(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_affordance_manifest_checksum_exposed_in_telemetry(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: manifest_path, tmp_path
- Outputs: None, SimulationConfig
- Internal interactions: —
- External interactions: Path, SimulationConfig.model_validate, TelemetryPublisher, WorldState.from_config, _configure_with_manifest, config.model_dump, hashlib.sha256, hexdigest, load_config, manifest.read_bytes, manifest.write_text, publisher.latest_affordance_manifest, … (3 more)

### Integration Points
- Runtime calls: Path, SimulationConfig.model_validate, TelemetryPublisher, WorldState.from_config, _configure_with_manifest, config.model_dump, hashlib.sha256, hexdigest, load_config, manifest.read_bytes, manifest.write_text, publisher.latest_affordance_manifest, … (3 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: _configure_with_manifest, test_affordance_manifest_loads_and_exposes_metadata, test_affordance_manifest_duplicate_ids_fail, test_affordance_manifest_missing_duration_fails, test_affordance_manifest_checksum_exposed_in_telemetry


## tests/test_affordance_preconditions.py

**Purpose**: Pytest coverage for test affordance preconditions.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet.world.preconditions
**Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid, townlet.world.preconditions

### Classes
- None defined.

### Functions
- `_make_loop() -> tuple[SimulationLoop, object]` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: tuple[SimulationLoop, object]
- `_request_object(world, object_id, agent_id) -> None` — No function docstring.
  - Parameters: world, object_id, agent_id
  - Returns: None
- `test_compile_preconditions_normalises_booleans() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_compile_preconditions_rejects_function_calls() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_evaluate_preconditions_supports_nested_attributes() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_precondition_failure_blocks_affordance_and_emits_event() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_precondition_success_allows_affordance_start() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: agent_id, object_id, world
- Outputs: None, tuple[SimulationLoop, object]
- Internal interactions: —
- External interactions: AgentSnapshot, ConsoleCommand, Path, SimulationLoop, _make_loop, _request_object, compile_preconditions, create_console_router, evaluate_preconditions, load_config, loop.telemetry.latest_precondition_failures, loop.telemetry.publish_tick, … (7 more)

### Integration Points
- Runtime calls: AgentSnapshot, ConsoleCommand, Path, SimulationLoop, _make_loop, _request_object, compile_preconditions, create_console_router, evaluate_preconditions, load_config, loop.telemetry.latest_precondition_failures, loop.telemetry.publish_tick, … (7 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: _make_loop, _request_object, test_compile_preconditions_normalises_booleans, test_compile_preconditions_rejects_function_calls, test_evaluate_preconditions_supports_nested_attributes, test_precondition_failure_blocks_affordance_and_emits_event, test_precondition_success_allows_affordance_start


## tests/test_affordance_runtime_config.py

**Purpose**: Pytest coverage for test affordance runtime config.
**Dependencies**:
- Standard Library: __future__, json, pathlib, subprocess, sys
- Third-Party: pytest
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.affordances
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.affordances

### Classes
- None defined.

### Functions
- `test_runtime_config_factory_and_instrumentation(instrumentation, tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: instrumentation, tmp_path
  - Returns: None
- `test_runtime_factory_injection_via_fixture(stub_affordance_runtime_factory) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: stub_affordance_runtime_factory
  - Returns: None
- `test_inspect_affordances_cli_snapshot(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_inspect_affordances_cli_config(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: instrumentation, stub_affordance_runtime_factory, tmp_path
- Outputs: None
- Internal interactions: —
- External interactions: Path, SimulationLoop, json.loads, load_config, loop.save_snapshot, loop.step, pytest.mark.parametrize, subprocess.run

### Integration Points
- Runtime calls: Path, SimulationLoop, json.loads, load_config, loop.save_snapshot, loop.step, pytest.mark.parametrize, subprocess.run
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: test_runtime_config_factory_and_instrumentation, test_runtime_factory_injection_via_fixture, test_inspect_affordances_cli_snapshot, test_inspect_affordances_cli_config


## tests/test_basket_telemetry.py

**Purpose**: Pytest coverage for test basket telemetry.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: —
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Classes
- None defined.

### Functions
- `test_basket_cost_in_telemetry_snapshot() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None
- Internal interactions: —
- External interactions: AgentSnapshot, Path, SimulationLoop, load_config, loop.step, publisher.latest_job_snapshot, world._assign_jobs_to_agents

### Integration Points
- Runtime calls: AgentSnapshot, Path, SimulationLoop, load_config, loop.step, publisher.latest_job_snapshot, world._assign_jobs_to_agents

### Code Quality Notes
- Missing function docstrings: test_basket_cost_in_telemetry_snapshot


## tests/test_bc_capture_prototype.py

**Purpose**: Pytest coverage for test bc capture prototype.
**Dependencies**:
- Standard Library: __future__, json, pathlib
- Third-Party: numpy
- Internal: townlet.policy.replay
**Related modules**: townlet.policy.replay

### Classes
- None defined.

### Functions
- `test_synthetic_bc_capture_round_trip(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: tmp_path
- Outputs: None
- Internal interactions: —
- External interactions: frames.append, frames_to_replay_sample, json.dumps, load_replay_sample, meta_path.write_text, np.linspace, np.savez, np.testing.assert_allclose, np.zeros, output_dir.mkdir, reloaded.actions.tolist, sample.actions.tolist, … (1 more)

### Integration Points
- Runtime calls: frames.append, frames_to_replay_sample, json.dumps, load_replay_sample, meta_path.write_text, np.linspace, np.savez, np.testing.assert_allclose, np.zeros, output_dir.mkdir, reloaded.actions.tolist, sample.actions.tolist, … (1 more)
- Third-party libraries: numpy

### Code Quality Notes
- Missing function docstrings: test_synthetic_bc_capture_round_trip


## tests/test_bc_trainer.py

**Purpose**: Pytest coverage for test bc trainer.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: numpy, pytest
- Internal: townlet.policy, townlet.policy.models, townlet.policy.replay
**Related modules**: townlet.policy, townlet.policy.models, townlet.policy.replay

### Classes
- None defined.

### Functions
- `test_bc_trainer_overfits_toy_dataset(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_bc_evaluate_accuracy(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: tmp_path
- Outputs: None
- Internal interactions: —
- External interactions: BCTrainer, BCTrainingConfig, BCTrajectoryDataset, ConflictAwarePolicyConfig, frames.append, frames_to_replay_sample, np.zeros, pytest.mark.skipif, samples.append, torch_available, trainer.evaluate, trainer.fit

### Integration Points
- Runtime calls: BCTrainer, BCTrainingConfig, BCTrajectoryDataset, ConflictAwarePolicyConfig, frames.append, frames_to_replay_sample, np.zeros, pytest.mark.skipif, samples.append, torch_available, trainer.evaluate, trainer.fit
- Third-party libraries: numpy, pytest

### Code Quality Notes
- Missing function docstrings: test_bc_trainer_overfits_toy_dataset, test_bc_evaluate_accuracy


## tests/test_behavior_rivalry.py

**Purpose**: Pytest coverage for test behavior rivalry.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.policy.behavior, townlet.world.grid
**Related modules**: townlet.config, townlet.policy.behavior, townlet.world.grid

### Classes
- None defined.

### Functions
- `_make_world() -> WorldState` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: WorldState
- `test_scripted_behavior_avoids_queue_with_rival() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_scripted_behavior_requests_when_no_rival() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_behavior_retries_after_rival_leaves() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None, WorldState
- Internal interactions: —
- External interactions: AgentSnapshot, Path, ScriptedBehavior, WorldState.from_config, _make_world, behavior.decide, behavior.pending.pop, load_config, world.queue_manager.release, world.queue_manager.request_access, world.register_object, world.register_rivalry_conflict

### Integration Points
- Runtime calls: AgentSnapshot, Path, ScriptedBehavior, WorldState.from_config, _make_world, behavior.decide, behavior.pending.pop, load_config, world.queue_manager.release, world.queue_manager.request_access, world.register_object, world.register_rivalry_conflict
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: _make_world, test_scripted_behavior_avoids_queue_with_rival, test_scripted_behavior_requests_when_no_rival, test_behavior_retries_after_rival_leaves


## tests/test_capture_scripted_cli.py

**Purpose**: Pytest coverage for test capture scripted cli.
**Dependencies**:
- Standard Library: json, pathlib, runpy
- Third-Party: —
- Internal: townlet.policy.replay
**Related modules**: townlet.policy.replay

### Classes
- None defined.

### Functions
- `test_capture_scripted_idle(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: tmp_path
- Outputs: None
- Internal interactions: —
- External interactions: load_replay_sample, main, output_dir.glob, runpy.run_path

### Integration Points
- Runtime calls: load_replay_sample, main, output_dir.glob, runpy.run_path

### Code Quality Notes
- Missing function docstrings: test_capture_scripted_idle


## tests/test_cli_validate_affordances.py

**Purpose**: Pytest coverage for test cli validate affordances.
**Dependencies**:
- Standard Library: __future__, pathlib, subprocess, sys
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `_run() -> subprocess.CompletedProcess[str]` — No function docstring.
  - Parameters: —
  - Returns: subprocess.CompletedProcess[str]
- `test_validate_affordances_cli_success(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_validate_affordances_cli_failure(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_validate_affordances_cli_bad_precondition(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_validate_affordances_cli_directory(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- `SCRIPT` = "Path('scripts/validate_affordances.py').resolve()"

### Data Flow
- Inputs: tmp_path
- Outputs: None, subprocess.CompletedProcess[str]
- Internal interactions: —
- External interactions: _run, bad.write_text, good.write_text, manifest.write_text, result.stderr.lower, subdir.mkdir, subprocess.run

### Integration Points
- Runtime calls: _run, bad.write_text, good.write_text, manifest.write_text, result.stderr.lower, subdir.mkdir, subprocess.run

### Code Quality Notes
- Missing function docstrings: _run, test_validate_affordances_cli_success, test_validate_affordances_cli_failure, test_validate_affordances_cli_bad_precondition, test_validate_affordances_cli_directory


## tests/test_config_loader.py

**Purpose**: Pytest coverage for test config loader.
**Dependencies**:
- Standard Library: pathlib, sys, types
- Third-Party: pytest, yaml
- Internal: townlet.config, townlet.snapshots.migrations
**Related modules**: townlet.config, townlet.snapshots.migrations

### Classes
- None defined.

### Functions
- `poc_config(tmp_path) -> Path` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: Path
- `test_load_config(poc_config) -> None` — No function docstring.
  - Parameters: poc_config
  - Returns: None
- `test_invalid_queue_cooldown_rejected(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_invalid_embedding_threshold_rejected(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_invalid_embedding_slot_count(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_invalid_affordance_file_absent(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_observation_variant_guard(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_ppo_config_defaults_roundtrip(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_observation_variant_full_supported(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_observation_variant_compact_supported(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_snapshot_autosave_cadence_validation(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_snapshot_identity_overrides_take_precedence(poc_config) -> None` — No function docstring.
  - Parameters: poc_config
  - Returns: None
- `test_register_snapshot_migrations_from_config(poc_config) -> None` — No function docstring.
  - Parameters: poc_config
  - Returns: None
- `test_telemetry_transport_defaults(poc_config) -> None` — No function docstring.
  - Parameters: poc_config
  - Returns: None
- `test_telemetry_file_transport_requires_path(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_telemetry_tcp_transport_requires_endpoint(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: poc_config, tmp_path
- Outputs: None, Path
- Internal interactions: —
- External interactions: Path, SimulationConfig.model_validate, clear_registry, config.affordances.affordances_file.endswith, config.model_dump, config_payload.get, config_with_handler.register_snapshot_migrations, load_config, migration_registry.find_path, override.build_snapshot_identity, payload.get, pytest.approx, … (8 more)

### Integration Points
- Runtime calls: Path, SimulationConfig.model_validate, clear_registry, config.affordances.affordances_file.endswith, config.model_dump, config_payload.get, config_with_handler.register_snapshot_migrations, load_config, migration_registry.find_path, override.build_snapshot_identity, payload.get, pytest.approx, … (8 more)
- Third-party libraries: pytest, yaml

### Code Quality Notes
- Missing function docstrings: poc_config, test_load_config, test_invalid_queue_cooldown_rejected, test_invalid_embedding_threshold_rejected, test_invalid_embedding_slot_count, test_invalid_affordance_file_absent, test_observation_variant_guard, test_ppo_config_defaults_roundtrip, test_observation_variant_full_supported, test_observation_variant_compact_supported, test_snapshot_autosave_cadence_validation, test_snapshot_identity_overrides_take_precedence, test_register_snapshot_migrations_from_config, test_telemetry_transport_defaults, test_telemetry_file_transport_requires_path, test_telemetry_tcp_transport_requires_endpoint


## tests/test_conflict_scenarios.py

**Purpose**: Pytest coverage for test conflict scenarios.
**Dependencies**:
- Standard Library: __future__, pathlib, random, types
- Third-Party: pytest
- Internal: townlet.config.loader, townlet.core.sim_loop, townlet.policy.scenario_utils, townlet.world.queue_manager
**Related modules**: townlet.config.loader, townlet.core.sim_loop, townlet.policy.scenario_utils, townlet.world.queue_manager

### Classes
- None defined.

### Functions
- `_run_scenario(config_path, ticks) -> SimulationLoop` — No function docstring. Side effects: filesystem.
  - Parameters: config_path, ticks
  - Returns: SimulationLoop
- `test_queue_conflict_scenario_produces_alerts() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_rivalry_decay_scenario_tracks_events() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_queue_manager_randomised_regression(seed) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: seed
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: config_path, seed, ticks
- Outputs: None, SimulationLoop
- Internal interactions: —
- External interactions: Path, QueueManager, SimpleNamespace, SimulationLoop, _run_scenario, apply_scenario, conflict.get, event.get, load_config, loop.step, loop.telemetry.latest_conflict_snapshot, loop.telemetry.latest_stability_alerts, … (14 more)

### Integration Points
- Runtime calls: Path, QueueManager, SimpleNamespace, SimulationLoop, _run_scenario, apply_scenario, conflict.get, event.get, load_config, loop.step, loop.telemetry.latest_conflict_snapshot, loop.telemetry.latest_stability_alerts, … (14 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: _run_scenario, test_queue_conflict_scenario_produces_alerts, test_rivalry_decay_scenario_tracks_events, test_queue_manager_randomised_regression


## tests/test_conflict_telemetry.py

**Purpose**: Pytest coverage for test conflict telemetry.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Classes
- None defined.

### Functions
- `test_conflict_snapshot_reports_rivalry_counts() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_replay_sample_matches_schema(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_conflict_export_import_preserves_history() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: tmp_path
- Outputs: None
- Internal interactions: —
- External interactions: AgentSnapshot, Path, SimulationLoop, TelemetryPublisher, entry.keys, event.get, load_config, loop.telemetry.export_state, loop.telemetry.latest_conflict_snapshot, loop.telemetry.latest_events, loop.telemetry.latest_stability_alerts, loop.telemetry.publish_tick, … (11 more)

### Integration Points
- Runtime calls: AgentSnapshot, Path, SimulationLoop, TelemetryPublisher, entry.keys, event.get, load_config, loop.telemetry.export_state, loop.telemetry.latest_conflict_snapshot, loop.telemetry.latest_events, loop.telemetry.latest_stability_alerts, loop.telemetry.publish_tick, … (11 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: test_conflict_snapshot_reports_rivalry_counts, test_replay_sample_matches_schema, test_conflict_export_import_preserves_history


## tests/test_console_auth.py

**Purpose**: Pytest coverage for test console auth.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: —
- Internal: townlet.config, townlet.telemetry.publisher
**Related modules**: townlet.config, townlet.telemetry.publisher

### Classes
- None defined.

### Functions
- `_config_with_auth() -> TelemetryPublisher` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: TelemetryPublisher
- `test_console_command_requires_token_when_enabled() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_console_command_accepts_valid_viewer_token() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_console_command_assigns_admin_role() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_console_command_rejects_invalid_token() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None, TelemetryPublisher
- Internal interactions: —
- External interactions: ConsoleAuthConfig, ConsoleAuthTokenConfig, Path, TelemetryPublisher, _config_with_auth, config.model_copy, load_config, publisher.close, publisher.drain_console_buffer, publisher.export_console_buffer, publisher.latest_console_results, publisher.queue_console_command

### Integration Points
- Runtime calls: ConsoleAuthConfig, ConsoleAuthTokenConfig, Path, TelemetryPublisher, _config_with_auth, config.model_copy, load_config, publisher.close, publisher.drain_console_buffer, publisher.export_console_buffer, publisher.latest_console_results, publisher.queue_console_command

### Code Quality Notes
- Missing function docstrings: _config_with_auth, test_console_command_requires_token_when_enabled, test_console_command_accepts_valid_viewer_token, test_console_command_assigns_admin_role, test_console_command_rejects_invalid_token


## tests/test_console_commands.py

**Purpose**: Pytest coverage for test console commands.
**Dependencies**:
- Standard Library: dataclasses, pathlib
- Third-Party: —
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.snapshots, townlet.snapshots.migrations, townlet.snapshots.state, townlet.world.grid
**Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.snapshots, townlet.snapshots.migrations, townlet.snapshots.state, townlet.world.grid

### Classes
- None defined.

### Functions
- `test_console_telemetry_snapshot_returns_payload() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_console_conflict_status_reports_history() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_console_queue_inspect_returns_queue_details() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_console_set_spawn_delay_updates_lifecycle() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_console_rivalry_dump_reports_pairs() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_console_affordance_status_reports_runtime() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_employment_console_commands_manage_queue() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_console_schema_warning_for_newer_version() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_console_perturbation_requires_admin_mode() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_console_perturbation_commands_schedule_and_cancel() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_console_arrange_meet_schedules_event() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_console_arrange_meet_unknown_spec_returns_error() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_console_snapshot_commands(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_console_snapshot_rejects_outside_roots(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: tmp_path
- Outputs: None
- Internal interactions: —
- External interactions: AgentSnapshot, ArrangedMeetEventConfig, ConsoleCommand, FloatRange, IntRange, Path, PerturbationSchedulerConfig, PriceSpikeEventConfig, SimulationLoop, SnapshotManager, SnapshotState, clear_registry, … (31 more)

### Integration Points
- Runtime calls: AgentSnapshot, ArrangedMeetEventConfig, ConsoleCommand, FloatRange, IntRange, Path, PerturbationSchedulerConfig, PriceSpikeEventConfig, SimulationLoop, SnapshotManager, SnapshotState, clear_registry, … (31 more)

### Code Quality Notes
- Missing function docstrings: test_console_telemetry_snapshot_returns_payload, test_console_conflict_status_reports_history, test_console_queue_inspect_returns_queue_details, test_console_set_spawn_delay_updates_lifecycle, test_console_rivalry_dump_reports_pairs, test_console_affordance_status_reports_runtime, test_employment_console_commands_manage_queue, test_console_schema_warning_for_newer_version, test_console_perturbation_requires_admin_mode, test_console_perturbation_commands_schedule_and_cancel, test_console_arrange_meet_schedules_event, test_console_arrange_meet_unknown_spec_returns_error, test_console_snapshot_commands, test_console_snapshot_rejects_outside_roots


## tests/test_console_dispatcher.py

**Purpose**: Pytest coverage for test console dispatcher.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid

### Classes
- None defined.

### Functions
- `employment_loop() -> SimulationLoop` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: SimulationLoop
- `_queue_command(loop, payload) -> None` — No function docstring.
  - Parameters: loop, payload
  - Returns: None
- `test_dispatcher_processes_employment_review(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_dispatcher_idempotency_reuses_history(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_dispatcher_requires_admin_mode(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_dispatcher_enforces_cmd_id_for_destructive_ops(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_spawn_command_creates_agent(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_spawn_rejects_duplicate_id(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_teleport_moves_agent(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_teleport_rejects_blocked_tile(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_setneed_updates_needs(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_setneed_rejects_unknown_need(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_price_updates_economy_and_basket(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_price_rejects_unknown_key(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_force_chat_updates_relationship(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_force_chat_requires_distinct_agents(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_set_rel_updates_ties(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_possess_acquire_and_release(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_possess_errors_on_duplicate_or_missing(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_kill_command_removes_agent(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_toggle_mortality_updates_flag(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None
- `test_set_exit_cap_updates_config(employment_loop) -> None` — No function docstring.
  - Parameters: employment_loop
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: employment_loop, loop, payload
- Outputs: None, SimulationLoop
- Internal interactions: —
- External interactions: AgentSnapshot, ConsoleCommand, Path, SimulationLoop, _queue_command, create_console_router, get, inventory.get, load_config, loop.policy.is_possessed, loop.step, loop.telemetry.latest_console_results, … (8 more)

### Integration Points
- Runtime calls: AgentSnapshot, ConsoleCommand, Path, SimulationLoop, _queue_command, create_console_router, get, inventory.get, load_config, loop.policy.is_possessed, loop.step, loop.telemetry.latest_console_results, … (8 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: employment_loop, _queue_command, test_dispatcher_processes_employment_review, test_dispatcher_idempotency_reuses_history, test_dispatcher_requires_admin_mode, test_dispatcher_enforces_cmd_id_for_destructive_ops, test_spawn_command_creates_agent, test_spawn_rejects_duplicate_id, test_teleport_moves_agent, test_teleport_rejects_blocked_tile, test_setneed_updates_needs, test_setneed_rejects_unknown_need, test_price_updates_economy_and_basket, test_price_rejects_unknown_key, test_force_chat_updates_relationship, test_force_chat_requires_distinct_agents, test_set_rel_updates_ties, test_possess_acquire_and_release, test_possess_errors_on_duplicate_or_missing, test_kill_command_removes_agent, test_toggle_mortality_updates_flag, test_set_exit_cap_updates_config


## tests/test_console_events.py

**Purpose**: Pytest coverage for test console events.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: —
- Internal: townlet.config, townlet.console.handlers, townlet.telemetry.publisher, townlet.world.grid
**Related modules**: townlet.config, townlet.console.handlers, townlet.telemetry.publisher, townlet.world.grid

### Classes
- None defined.

### Functions
- `test_event_stream_receives_published_events() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_event_stream_handles_empty_batch() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None
- Internal interactions: —
- External interactions: EventStream, Path, TelemetryPublisher, WorldState.from_config, load_config, publisher.publish_tick, stream.connect, stream.latest

### Integration Points
- Runtime calls: EventStream, Path, TelemetryPublisher, WorldState.from_config, load_config, publisher.publish_tick, stream.connect, stream.latest

### Code Quality Notes
- Missing function docstrings: test_event_stream_receives_published_events, test_event_stream_handles_empty_batch


## tests/test_console_promotion.py

**Purpose**: Pytest coverage for test console promotion.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop
**Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop

### Classes
- None defined.

### Functions
- `admin_router() -> tuple[SimulationLoop, object]` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: tuple[SimulationLoop, object]
- `make_ready(loop) -> None` — No function docstring.
  - Parameters: loop
  - Returns: None
- `test_promotion_status_command(admin_router) -> None` — No function docstring.
  - Parameters: admin_router
  - Returns: None
- `test_promote_and_rollback_commands(admin_router) -> None` — No function docstring.
  - Parameters: admin_router
  - Returns: None
- `test_policy_swap_command(admin_router, tmp_path) -> None` — No function docstring.
  - Parameters: admin_router, tmp_path
  - Returns: None
- `test_policy_swap_missing_file(admin_router) -> None` — No function docstring.
  - Parameters: admin_router
  - Returns: None
- `viewer_router() -> object` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: object
- `test_viewer_mode_forbidden(viewer_router) -> None` — No function docstring.
  - Parameters: viewer_router
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: admin_router, loop, tmp_path, viewer_router
- Outputs: None, object, tuple[SimulationLoop, object]
- Internal interactions: —
- External interactions: ConsoleCommand, Path, SimulationLoop, checkpoint.write_text, create_console_router, get, identity.get, identity_after.get, load_config, loop.policy.active_policy_hash, loop.promotion.snapshot, loop.promotion.update_from_metrics, … (6 more)

### Integration Points
- Runtime calls: ConsoleCommand, Path, SimulationLoop, checkpoint.write_text, create_console_router, get, identity.get, identity_after.get, load_config, loop.policy.active_policy_hash, loop.promotion.snapshot, loop.promotion.update_from_metrics, … (6 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: admin_router, make_ready, test_promotion_status_command, test_promote_and_rollback_commands, test_policy_swap_command, test_policy_swap_missing_file, viewer_router, test_viewer_mode_forbidden


## tests/test_curate_trajectories.py

**Purpose**: Pytest coverage for test curate trajectories.
**Dependencies**:
- Standard Library: __future__, json, pathlib, runpy
- Third-Party: numpy
- Internal: townlet.policy.replay
**Related modules**: townlet.policy.replay

### Classes
- None defined.

### Functions
- `_write_sample(output_dir, stem, rewards, timesteps) -> None` — No function docstring.
  - Parameters: output_dir, stem, rewards, timesteps
  - Returns: None
- `test_curate_trajectories(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: output_dir, rewards, stem, timesteps, tmp_path
- Outputs: None
- Internal interactions: —
- External interactions: Path, _write_sample, captures.mkdir, frames.append, frames_to_replay_sample, json.dumps, json.loads, main, manifest_path.read_text, meta_path.write_text, name.startswith, np.full, … (4 more)

### Integration Points
- Runtime calls: Path, _write_sample, captures.mkdir, frames.append, frames_to_replay_sample, json.dumps, json.loads, main, manifest_path.read_text, meta_path.write_text, name.startswith, np.full, … (4 more)
- Third-party libraries: numpy

### Code Quality Notes
- Missing function docstrings: _write_sample, test_curate_trajectories


## tests/test_embedding_allocator.py

**Purpose**: Pytest coverage for test embedding allocator.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: —
- Internal: townlet.config, townlet.observations.builder, townlet.observations.embedding, townlet.stability.monitor, townlet.telemetry.publisher, townlet.world.grid
**Related modules**: townlet.config, townlet.observations.builder, townlet.observations.embedding, townlet.stability.monitor, townlet.telemetry.publisher, townlet.world.grid

### Classes
- None defined.

### Functions
- `make_allocator() -> EmbeddingAllocator` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: EmbeddingAllocator
- `test_allocate_reuses_slot_after_cooldown() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_allocator_respects_multiple_slots() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_observation_builder_releases_on_termination() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_telemetry_exposes_allocator_metrics() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_stability_monitor_sets_alert_on_warning() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_telemetry_records_events() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_stability_alerts_on_affordance_failures() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: EmbeddingAllocator, None
- Internal interactions: —
- External interactions: AgentSnapshot, EmbeddingAllocator, ObservationBuilder, Path, StabilityMonitor, TelemetryPublisher, WorldState.from_config, allocator.allocate, allocator.metrics, allocator.release, builder.build_batch, load_config, … (7 more)

### Integration Points
- Runtime calls: AgentSnapshot, EmbeddingAllocator, ObservationBuilder, Path, StabilityMonitor, TelemetryPublisher, WorldState.from_config, allocator.allocate, allocator.metrics, allocator.release, builder.build_batch, load_config, … (7 more)

### Code Quality Notes
- Missing function docstrings: make_allocator, test_allocate_reuses_slot_after_cooldown, test_allocator_respects_multiple_slots, test_observation_builder_releases_on_termination, test_telemetry_exposes_allocator_metrics, test_stability_monitor_sets_alert_on_warning, test_telemetry_records_events, test_stability_alerts_on_affordance_failures


## tests/test_employment_loop.py

**Purpose**: Pytest coverage for test employment loop.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Classes
- None defined.

### Functions
- `make_loop_with_employment() -> SimulationLoop` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: SimulationLoop
- `advance_ticks(loop, ticks) -> None` — No function docstring.
  - Parameters: loop, ticks
  - Returns: None
- `test_on_time_shift_records_attendance() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_late_arrival_accumulates_wages_withheld() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_employment_exit_queue_respects_cap_and_manual_override() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: loop, ticks
- Outputs: None, SimulationLoop
- Internal interactions: —
- External interactions: AgentSnapshot, Path, SimulationLoop, advance_ticks, alice.inventory.get, bob.inventory.get, config.jobs.values, load_config, loop.lifecycle.evaluate, loop.step, make_loop_with_employment, manual.get, … (7 more)

### Integration Points
- Runtime calls: AgentSnapshot, Path, SimulationLoop, advance_ticks, alice.inventory.get, bob.inventory.get, config.jobs.values, load_config, loop.lifecycle.evaluate, loop.step, make_loop_with_employment, manual.get, … (7 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: make_loop_with_employment, advance_ticks, test_on_time_shift_records_attendance, test_late_arrival_accumulates_wages_withheld, test_employment_exit_queue_respects_cap_and_manual_override


## tests/test_lifecycle_manager.py

**Purpose**: Pytest coverage for test lifecycle manager.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: —
- Internal: townlet.config, townlet.lifecycle.manager, townlet.world.grid
**Related modules**: townlet.config, townlet.lifecycle.manager, townlet.world.grid

### Classes
- None defined.

### Functions
- `_make_world(respawn_delay) -> tuple[LifecycleManager, WorldState]` — No function docstring. Side effects: filesystem.
  - Parameters: respawn_delay
  - Returns: tuple[LifecycleManager, WorldState]
- `_spawn_agent(world, agent_id) -> AgentSnapshot` — No function docstring.
  - Parameters: world, agent_id
  - Returns: AgentSnapshot
- `test_respawn_after_delay() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_employment_exit_emits_event_and_resets_state() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_employment_daily_reset() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_termination_reasons_captured() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: agent_id, respawn_delay, world
- Outputs: AgentSnapshot, None, tuple[LifecycleManager, WorldState]
- Internal interactions: —
- External interactions: AgentSnapshot, LifecycleManager, Path, WorldState.from_config, _make_world, _spawn_agent, agent_id.startswith, event.get, load_config, manager.evaluate, manager.finalize, manager.process_respawns, … (9 more)

### Integration Points
- Runtime calls: AgentSnapshot, LifecycleManager, Path, WorldState.from_config, _make_world, _spawn_agent, agent_id.startswith, event.get, load_config, manager.evaluate, manager.finalize, manager.process_respawns, … (9 more)

### Code Quality Notes
- Missing function docstrings: _make_world, _spawn_agent, test_respawn_after_delay, test_employment_exit_emits_event_and_resets_state, test_employment_daily_reset, test_termination_reasons_captured


## tests/test_need_decay.py

**Purpose**: Pytest coverage for test need decay.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.lifecycle.manager, townlet.world.grid
**Related modules**: townlet.config, townlet.lifecycle.manager, townlet.world.grid

### Classes
- None defined.

### Functions
- `_make_world() -> tuple[LifecycleManager, WorldState]` — No function docstring.
  - Parameters: —
  - Returns: tuple[LifecycleManager, WorldState]
- `_spawn_agent(world) -> AgentSnapshot` — No function docstring.
  - Parameters: world
  - Returns: AgentSnapshot
- `test_need_decay_matches_config() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_need_decay_clamps_at_zero() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_lifecycle_hunger_threshold_applies() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_agent_snapshot_clamps_on_init() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- `CONFIG_PATH` = "Path('configs/examples/poc_hybrid.yaml')"

### Data Flow
- Inputs: world
- Outputs: AgentSnapshot, None, tuple[LifecycleManager, WorldState]
- Internal interactions: —
- External interactions: AgentSnapshot, LifecycleManager, WorldState.from_config, _make_world, _spawn_agent, load_config, manager.evaluate, pytest.approx, snapshot.needs.values, world._apply_need_decay, world._assign_job_if_missing, world._sync_agent_spawn, … (1 more)

### Integration Points
- Runtime calls: AgentSnapshot, LifecycleManager, WorldState.from_config, _make_world, _spawn_agent, load_config, manager.evaluate, pytest.approx, snapshot.needs.values, world._apply_need_decay, world._assign_job_if_missing, world._sync_agent_spawn, … (1 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: _make_world, _spawn_agent, test_need_decay_matches_config, test_need_decay_clamps_at_zero, test_lifecycle_hunger_threshold_applies, test_agent_snapshot_clamps_on_init


## tests/test_observation_builder.py

**Purpose**: Pytest coverage for test observation builder.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: numpy
- Internal: townlet.config, townlet.console.command, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid
**Related modules**: townlet.config, townlet.console.command, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid

### Classes
- None defined.

### Functions
- `make_world(enforce_job_loop) -> SimulationLoop` — No function docstring. Side effects: filesystem.
  - Parameters: enforce_job_loop
  - Returns: SimulationLoop
- `test_observation_builder_hybrid_map_and_features() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_observation_ctx_reset_releases_slot() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_observation_rivalry_features_reflect_conflict() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_observation_queue_and_reservation_flags() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_observation_respawn_resets_features() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_ctx_reset_flag_on_teleport_and_possession() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: enforce_job_loop
- Outputs: None, SimulationLoop
- Internal interactions: —
- External interactions: AgentSnapshot, ConsoleCommandEnvelope, Path, SimulationLoop, agent_id.startswith, bob_feature_names.index, builder.build_batch, feature_names.index, landmark_slices.get, load_config, loop.lifecycle.evaluate, loop.lifecycle.finalize, … (13 more)

### Integration Points
- Runtime calls: AgentSnapshot, ConsoleCommandEnvelope, Path, SimulationLoop, agent_id.startswith, bob_feature_names.index, builder.build_batch, feature_names.index, landmark_slices.get, load_config, loop.lifecycle.evaluate, loop.lifecycle.finalize, … (13 more)
- Third-party libraries: numpy

### Code Quality Notes
- Missing function docstrings: make_world, test_observation_builder_hybrid_map_and_features, test_observation_ctx_reset_releases_slot, test_observation_rivalry_features_reflect_conflict, test_observation_queue_and_reservation_flags, test_observation_respawn_resets_features, test_ctx_reset_flag_on_teleport_and_possession


## tests/test_observation_builder_compact.py

**Purpose**: Pytest coverage for test observation builder compact.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: numpy
- Internal: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid

### Classes
- None defined.

### Functions
- `make_compact_world() -> SimulationLoop` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: SimulationLoop
- `test_compact_observation_features_only() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None, SimulationLoop
- Internal interactions: —
- External interactions: AgentSnapshot, Path, SimulationLoop, builder.build_batch, feature_names.index, load_config, make_compact_world, metadata.get, np.isclose, world.agents.clear, world.register_object

### Integration Points
- Runtime calls: AgentSnapshot, Path, SimulationLoop, builder.build_batch, feature_names.index, load_config, make_compact_world, metadata.get, np.isclose, world.agents.clear, world.register_object
- Third-party libraries: numpy

### Code Quality Notes
- Missing function docstrings: make_compact_world, test_compact_observation_features_only


## tests/test_observation_builder_full.py

**Purpose**: Pytest coverage for test observation builder full.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: numpy
- Internal: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.world.grid

### Classes
- None defined.

### Functions
- `make_full_world() -> SimulationLoop` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: SimulationLoop
- `test_full_observation_map_and_features() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None, SimulationLoop
- Internal interactions: —
- External interactions: AgentSnapshot, Path, SimulationLoop, builder.build_batch, feature_names.index, load_config, make_full_world, metadata.get, np.isclose, world.agents.clear, world.register_object

### Integration Points
- Runtime calls: AgentSnapshot, Path, SimulationLoop, builder.build_batch, feature_names.index, load_config, make_full_world, metadata.get, np.isclose, world.agents.clear, world.register_object
- Third-party libraries: numpy

### Code Quality Notes
- Missing function docstrings: make_full_world, test_full_observation_map_and_features


## tests/test_observations_social_snippet.py

**Purpose**: Pytest coverage for test observations social snippet.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: numpy, pytest
- Internal: townlet.config, townlet.observations.builder, townlet.world.grid
**Related modules**: townlet.config, townlet.observations.builder, townlet.world.grid

### Classes
- None defined.

### Functions
- `base_config() -> SimulationConfig` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: SimulationConfig
- `_build_world(config) -> WorldState` — No function docstring.
  - Parameters: config
  - Returns: WorldState
- `test_social_snippet_vector_length(base_config) -> None` — No function docstring.
  - Parameters: base_config
  - Returns: None
- `test_relationship_stage_required(base_config) -> None` — No function docstring.
  - Parameters: base_config
  - Returns: None
- `test_disable_aggregates_via_config(base_config) -> None` — No function docstring.
  - Parameters: base_config
  - Returns: None
- `test_observation_matches_golden_fixture(base_config) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: base_config
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: base_config, config
- Outputs: None, SimulationConfig, WorldState
- Internal interactions: —
- External interactions: AgentSnapshot, ObservationBuilder, Path, SimulationConfig.model_validate, WorldState.from_config, _build_world, base_config.model_dump, builder._feature_index.items, builder.build_batch, load_config, name.startswith, np.load, … (7 more)

### Integration Points
- Runtime calls: AgentSnapshot, ObservationBuilder, Path, SimulationConfig.model_validate, WorldState.from_config, _build_world, base_config.model_dump, builder._feature_index.items, builder.build_batch, load_config, name.startswith, np.load, … (7 more)
- Third-party libraries: numpy, pytest

### Code Quality Notes
- Missing function docstrings: base_config, _build_world, test_social_snippet_vector_length, test_relationship_stage_required, test_disable_aggregates_via_config, test_observation_matches_golden_fixture


## tests/test_observer_payload.py

**Purpose**: Pytest coverage for test observer payload.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: —
- Internal: townlet.config, townlet.core.sim_loop, townlet.telemetry.publisher, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.telemetry.publisher, townlet.world.grid

### Classes
- None defined.

### Functions
- `make_loop() -> SimulationLoop` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: SimulationLoop
- `test_observer_payload_contains_job_and_economy() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_planning_payload_consistency() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None, SimulationLoop
- Internal interactions: —
- External interactions: AgentSnapshot, Path, SimulationLoop, agent_info.get, economy_snapshot.values, job_snapshot.values, load_config, loop.step, make_loop, obj_info.get, publisher.latest_economy_snapshot, publisher.latest_job_snapshot, … (2 more)

### Integration Points
- Runtime calls: AgentSnapshot, Path, SimulationLoop, agent_info.get, economy_snapshot.values, job_snapshot.values, load_config, loop.step, make_loop, obj_info.get, publisher.latest_economy_snapshot, publisher.latest_job_snapshot, … (2 more)

### Code Quality Notes
- Missing function docstrings: make_loop, test_observer_payload_contains_job_and_economy, test_planning_payload_consistency


## tests/test_observer_ui_dashboard.py

**Purpose**: Pytest coverage for test observer ui dashboard.
**Dependencies**:
- Standard Library: dataclasses, pathlib
- Third-Party: pytest, rich.console
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.policy.models, townlet_ui.dashboard, townlet_ui.telemetry
**Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.policy.models, townlet_ui.dashboard, townlet_ui.telemetry

### Classes
- None defined.

### Functions
- `make_loop() -> SimulationLoop` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: SimulationLoop
- `test_render_snapshot_produces_panels() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_run_dashboard_advances_loop(monkeypatch) -> None` — No function docstring.
  - Parameters: monkeypatch
  - Returns: None
- `test_build_map_panel_produces_table() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_narration_panel_shows_styled_categories() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_policy_inspector_snapshot_contains_entries() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_promotion_reason_logic() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_promotion_border_styles() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: monkeypatch
- Outputs: None, SimulationLoop
- Internal interactions: —
- External interactions: AgentSnapshot, AnnealStatus, Console, Path, PromotionSnapshot, SimulationLoop, TelemetryClient, _build_map_panel, _derive_promotion_reason, _promotion_border_style, console.export_text, console.print, … (23 more)

### Integration Points
- Runtime calls: AgentSnapshot, AnnealStatus, Console, Path, PromotionSnapshot, SimulationLoop, TelemetryClient, _build_map_panel, _derive_promotion_reason, _promotion_border_style, console.export_text, console.print, … (23 more)
- Third-party libraries: pytest, rich.console

### Code Quality Notes
- Missing function docstrings: make_loop, test_render_snapshot_produces_panels, test_run_dashboard_advances_loop, test_build_map_panel_produces_table, test_narration_panel_shows_styled_categories, test_policy_inspector_snapshot_contains_entries, test_promotion_reason_logic, test_promotion_border_styles


## tests/test_observer_ui_executor.py

**Purpose**: Pytest coverage for test observer ui executor.
**Dependencies**:
- Standard Library: time
- Third-Party: —
- Internal: townlet.console.handlers, townlet_ui.commands
**Related modules**: townlet.console.handlers, townlet_ui.commands

### Classes
- **DummyRouter** (bases: object; decorators: —) — No class docstring.
  - Methods:
    - `__init__(self) -> None` — No method docstring.
    - `dispatch(self, command) -> None` — No method docstring.

### Functions
- `test_console_command_executor_dispatches_async() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_console_command_executor_swallow_errors() -> None` — No function docstring. Raises: RuntimeError('boom').
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None
- Internal interactions: —
- External interactions: ConsoleCommand, ConsoleCommandExecutor, DummyRouter, FailingRouter, executor.shutdown, executor.submit, self.dispatched.append, time.sleep

### Integration Points
- Runtime calls: ConsoleCommand, ConsoleCommandExecutor, DummyRouter, FailingRouter, executor.shutdown, executor.submit, self.dispatched.append, time.sleep

### Code Quality Notes
- Missing function docstrings: test_console_command_executor_dispatches_async, test_console_command_executor_swallow_errors
- Missing method docstrings: DummyRouter.__init__, DummyRouter.dispatch


## tests/test_observer_ui_script.py

**Purpose**: Pytest coverage for test observer ui script.
**Dependencies**:
- Standard Library: pathlib, subprocess, sys
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `test_observer_ui_script_runs_single_tick(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: tmp_path
- Outputs: None
- Internal interactions: —
- External interactions: Path, resolve, subprocess.run

### Integration Points
- Runtime calls: Path, resolve, subprocess.run

### Code Quality Notes
- Missing function docstrings: test_observer_ui_script_runs_single_tick


## tests/test_perturbation_config.py

**Purpose**: Pytest coverage for test perturbation config.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: —
- Internal: townlet.config
**Related modules**: townlet.config

### Classes
- None defined.

### Functions
- `test_simulation_config_exposes_perturbations() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_price_spike_event_config_parses_ranges() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None
- Internal interactions: —
- External interactions: Path, PerturbationSchedulerConfig, config_path.exists, load_config

### Integration Points
- Runtime calls: Path, PerturbationSchedulerConfig, config_path.exists, load_config

### Code Quality Notes
- Missing function docstrings: test_simulation_config_exposes_perturbations, test_price_spike_event_config_parses_ranges


## tests/test_perturbation_scheduler.py

**Purpose**: Pytest coverage for test perturbation scheduler.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: —
- Internal: townlet.config, townlet.scheduler.perturbations, townlet.world.grid
**Related modules**: townlet.config, townlet.scheduler.perturbations, townlet.world.grid

### Classes
- None defined.

### Functions
- `_base_config() -> SimulationConfig` — No function docstring. Side effects: filesystem. Raises: RuntimeError('example config not found').
  - Parameters: —
  - Returns: SimulationConfig
- `test_manual_event_activation_and_expiry() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_auto_scheduling_respects_cooldowns() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_cancel_event_removes_from_active() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None, SimulationConfig
- Internal interactions: —
- External interactions: ArrangedMeetEventConfig, FloatRange, IntRange, Path, PerturbationScheduler, PerturbationSchedulerConfig, PriceSpikeEventConfig, WorldState.from_config, _base_config, config_path.exists, e.get, load_config, … (7 more)

### Integration Points
- Runtime calls: ArrangedMeetEventConfig, FloatRange, IntRange, Path, PerturbationScheduler, PerturbationSchedulerConfig, PriceSpikeEventConfig, WorldState.from_config, _base_config, config_path.exists, e.get, load_config, … (7 more)

### Code Quality Notes
- Missing function docstrings: _base_config, test_manual_event_activation_and_expiry, test_auto_scheduling_respects_cooldowns, test_cancel_event_removes_from_active


## tests/test_policy_anneal_blend.py

**Purpose**: Pytest coverage for test policy anneal blend.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: —
- Internal: townlet.config, townlet.policy.behavior, townlet.policy.runner, townlet.world.grid
**Related modules**: townlet.config, townlet.policy.behavior, townlet.policy.runner, townlet.world.grid

### Classes
- None defined.

### Functions
- `_make_world(option_commit_ticks) -> tuple[PolicyRuntime, WorldState]` — No function docstring. Side effects: filesystem.
  - Parameters: option_commit_ticks
  - Returns: tuple[PolicyRuntime, WorldState]
- `test_anneal_ratio_uses_provider_when_enabled() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_anneal_ratio_mix_respects_probability() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_blend_disabled_returns_scripted() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_option_commit_blocks_switch_until_expiry() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_option_commit_clears_on_termination() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_option_commit_respects_disabled_setting() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: option_commit_ticks
- Outputs: None, tuple[PolicyRuntime, WorldState]
- Internal interactions: —
- External interactions: AgentIntent, AgentSnapshot, Path, PolicyRuntime, WorldState.from_config, _make_world, entry.get, get, load_config, run_tick, runtime._option_commit_until.get, runtime._transitions.get, … (6 more)

### Integration Points
- Runtime calls: AgentIntent, AgentSnapshot, Path, PolicyRuntime, WorldState.from_config, _make_world, entry.get, get, load_config, run_tick, runtime._option_commit_until.get, runtime._transitions.get, … (6 more)

### Code Quality Notes
- Missing function docstrings: _make_world, test_anneal_ratio_uses_provider_when_enabled, test_anneal_ratio_mix_respects_probability, test_blend_disabled_returns_scripted, test_option_commit_blocks_switch_until_expiry, test_option_commit_clears_on_termination, test_option_commit_respects_disabled_setting


## tests/test_policy_models.py

**Purpose**: Pytest coverage for test policy models.
**Dependencies**:
- Standard Library: —
- Third-Party: pytest
- Internal: townlet.policy.models
**Related modules**: townlet.policy.models

### Classes
- None defined.

### Functions
- `test_conflict_policy_network_requires_torch_when_unavailable() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_conflict_policy_network_forward() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None
- Internal interactions: —
- External interactions: ConflictAwarePolicyConfig, ConflictAwarePolicyNetwork, net, pytest.mark.skipif, pytest.raises, pytest.skip, torch.randn, torch_available

### Integration Points
- Runtime calls: ConflictAwarePolicyConfig, ConflictAwarePolicyNetwork, net, pytest.mark.skipif, pytest.raises, pytest.skip, torch.randn, torch_available
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: test_conflict_policy_network_requires_torch_when_unavailable, test_conflict_policy_network_forward


## tests/test_policy_rivalry_behavior.py

**Purpose**: Pytest coverage for test policy rivalry behavior.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: pytest
- Internal: townlet.config.loader, townlet.policy.behavior, townlet.world.grid
**Related modules**: townlet.config.loader, townlet.policy.behavior, townlet.world.grid

### Classes
- None defined.

### Functions
- `base_config() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `_build_world(base_config) -> None` — No function docstring.
  - Parameters: base_config
  - Returns: None
- `_occupy(world, object_id, agent_id) -> None` — No function docstring.
  - Parameters: world, object_id, agent_id
  - Returns: None
- `test_agents_avoid_rivals_when_rivalry_high(base_config) -> None` — No function docstring.
  - Parameters: base_config
  - Returns: None
- `test_agents_request_again_after_rivalry_decay(base_config) -> None` — No function docstring.
  - Parameters: base_config
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: agent_id, base_config, object_id, world
- Outputs: None
- Internal interactions: —
- External interactions: AgentSnapshot, Path, ScriptedBehavior, WorldState.from_config, _build_world, _occupy, behaviour.decide, ledger.decay, load_config, pytest.fixture, stock.setdefault, world.objects.items, … (2 more)

### Integration Points
- Runtime calls: AgentSnapshot, Path, ScriptedBehavior, WorldState.from_config, _build_world, _occupy, behaviour.decide, ledger.decay, load_config, pytest.fixture, stock.setdefault, world.objects.items, … (2 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: base_config, _build_world, _occupy, test_agents_avoid_rivals_when_rivalry_high, test_agents_request_again_after_rivalry_decay


## tests/test_ppo_utils.py

**Purpose**: Pytest coverage for test ppo utils.
**Dependencies**:
- Standard Library: __future__
- Third-Party: torch
- Internal: townlet.policy.ppo
**Related modules**: townlet.policy.ppo

### Classes
- None defined.

### Functions
- `test_compute_gae_single_step() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_value_baseline_from_old_preds_handles_bootstrap() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_policy_surrogate_clipping_behaviour() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_clipped_value_loss_respects_clip() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None
- Internal interactions: —
- External interactions: clip_frac.item, loss.item, mean, torch.allclose, torch.clamp, torch.log, torch.max, torch.tensor, utils.clipped_value_loss, utils.compute_gae, utils.policy_surrogate, utils.value_baseline_from_old_preds

### Integration Points
- Runtime calls: clip_frac.item, loss.item, mean, torch.allclose, torch.clamp, torch.log, torch.max, torch.tensor, utils.clipped_value_loss, utils.compute_gae, utils.policy_surrogate, utils.value_baseline_from_old_preds
- Third-party libraries: torch

### Code Quality Notes
- Missing function docstrings: test_compute_gae_single_step, test_value_baseline_from_old_preds_handles_bootstrap, test_policy_surrogate_clipping_behaviour, test_clipped_value_loss_respects_clip


## tests/test_promotion_cli.py

**Purpose**: Pytest coverage for test promotion cli.
**Dependencies**:
- Standard Library: json, pathlib, subprocess, sys
- Third-Party: pytest
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `write_summary(tmp_path, accuracy, threshold) -> Path` — No function docstring.
  - Parameters: tmp_path, accuracy, threshold
  - Returns: Path
- `test_promotion_cli_pass(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_promotion_cli_fail(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_promotion_drill(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- `PYTHON` = 'Path(sys.executable)'
- `SCRIPT` = "Path('scripts/promotion_evaluate.py')"

### Data Flow
- Inputs: accuracy, threshold, tmp_path
- Outputs: None, Path
- Internal interactions: —
- External interactions: Path, config.exists, json.dumps, json.loads, pytest.skip, subprocess.run, summary.write_text, summary_file.read_text, write_summary

### Integration Points
- Runtime calls: Path, config.exists, json.dumps, json.loads, pytest.skip, subprocess.run, summary.write_text, summary_file.read_text, write_summary
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: write_summary, test_promotion_cli_pass, test_promotion_cli_fail, test_promotion_drill


## tests/test_promotion_evaluate_cli.py

**Purpose**: Pytest coverage for test promotion evaluate cli.
**Dependencies**:
- Standard Library: __future__, json, pathlib, subprocess, sys
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `_run() -> subprocess.CompletedProcess[str]` — No function docstring.
  - Parameters: —
  - Returns: subprocess.CompletedProcess[str]
- `test_promotion_evaluate_promote(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_promotion_evaluate_hold_flags(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_promotion_evaluate_dry_run(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- `SCRIPT` = "Path('scripts/promotion_evaluate.py').resolve()"

### Data Flow
- Inputs: tmp_path
- Outputs: None, subprocess.CompletedProcess[str]
- Internal interactions: —
- External interactions: _run, json.dumps, json.loads, path.write_text, subprocess.run

### Integration Points
- Runtime calls: _run, json.dumps, json.loads, path.write_text, subprocess.run

### Code Quality Notes
- Missing function docstrings: _run, test_promotion_evaluate_promote, test_promotion_evaluate_hold_flags, test_promotion_evaluate_dry_run


## tests/test_promotion_manager.py

**Purpose**: Pytest coverage for test promotion manager.
**Dependencies**:
- Standard Library: json, pathlib
- Third-Party: —
- Internal: townlet.config, townlet.stability.promotion
**Related modules**: townlet.config, townlet.stability.promotion

### Classes
- None defined.

### Functions
- `make_manager(log_path) -> PromotionManager` — No function docstring. Side effects: filesystem.
  - Parameters: log_path
  - Returns: PromotionManager
- `promotion_metrics(pass_streak, required, ready, last_result, last_tick) -> dict[str, object]` — No function docstring.
  - Parameters: pass_streak, required, ready, last_result, last_tick
  - Returns: dict[str, object]
- `test_promotion_state_transitions() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_promotion_manager_export_import() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_mark_promoted_and_rollback() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_rollback_without_metadata_reverts_to_initial() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_promotion_log_written(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: last_result, last_tick, log_path, pass_streak, ready, required, tmp_path
- Outputs: None, PromotionManager, dict[str, object]
- Internal interactions: —
- External interactions: Path, PromotionManager, get, json.loads, load_config, log_file.read_text, make_manager, manager.export_state, manager.mark_promoted, manager.register_rollback, manager.set_candidate_metadata, manager.snapshot, … (5 more)

### Integration Points
- Runtime calls: Path, PromotionManager, get, json.loads, load_config, log_file.read_text, make_manager, manager.export_state, manager.mark_promoted, manager.register_rollback, manager.set_candidate_metadata, manager.snapshot, … (5 more)

### Code Quality Notes
- Missing function docstrings: make_manager, promotion_metrics, test_promotion_state_transitions, test_promotion_manager_export_import, test_mark_promoted_and_rollback, test_rollback_without_metadata_reverts_to_initial, test_promotion_log_written


## tests/test_queue_fairness.py

**Purpose**: Pytest coverage for test queue fairness.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.world.queue_manager
**Related modules**: townlet.config, townlet.world.queue_manager

### Classes
- None defined.

### Functions
- `_make_queue_manager() -> QueueManager` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: QueueManager
- `test_cooldown_blocks_repeat_entry_and_tracks_metric() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_ghost_step_promotes_waiter_after_blockages(ghost_limit) -> None` — No function docstring.
  - Parameters: ghost_limit
  - Returns: None
- `test_queue_snapshot_reflects_waiting_order() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_queue_performance_metrics_accumulate_time() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: ghost_limit
- Outputs: None, QueueManager
- Internal interactions: —
- External interactions: Path, QueueManager, _make_queue_manager, load_config, pytest.fail, pytest.mark.parametrize, queue.active_agent, queue.metrics, queue.on_tick, queue.performance_metrics, queue.queue_snapshot, queue.record_blocked_attempt, … (2 more)

### Integration Points
- Runtime calls: Path, QueueManager, _make_queue_manager, load_config, pytest.fail, pytest.mark.parametrize, queue.active_agent, queue.metrics, queue.on_tick, queue.performance_metrics, queue.queue_snapshot, queue.record_blocked_attempt, … (2 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: _make_queue_manager, test_cooldown_blocks_repeat_entry_and_tracks_metric, test_ghost_step_promotes_waiter_after_blockages, test_queue_snapshot_reflects_waiting_order, test_queue_performance_metrics_accumulate_time


## tests/test_queue_manager.py

**Purpose**: Pytest coverage for test queue manager.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.world.queue_manager
**Related modules**: townlet.config, townlet.world.queue_manager

### Classes
- None defined.

### Functions
- `queue_manager() -> QueueManager` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: QueueManager
- `test_queue_cooldown_enforced(queue_manager) -> None` — No function docstring.
  - Parameters: queue_manager
  - Returns: None
- `test_queue_prioritises_wait_time(queue_manager) -> None` — No function docstring.
  - Parameters: queue_manager
  - Returns: None
- `test_ghost_step_trigger(queue_manager) -> None` — No function docstring.
  - Parameters: queue_manager
  - Returns: None
- `test_requeue_to_tail_rotates_agent(queue_manager) -> None` — No function docstring.
  - Parameters: queue_manager
  - Returns: None
- `test_record_blocked_attempt_counts_and_triggers(queue_manager) -> None` — No function docstring.
  - Parameters: queue_manager
  - Returns: None
- `test_cooldown_expiration_clears_entries(queue_manager) -> None` — No function docstring.
  - Parameters: queue_manager
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: queue_manager
- Outputs: None, QueueManager
- Internal interactions: —
- External interactions: Path, QueueManager, load_config, pytest.fixture, queue.count, queue_manager.active_agent, queue_manager.metrics, queue_manager.on_tick, queue_manager.queue_snapshot, queue_manager.record_blocked_attempt, queue_manager.release, queue_manager.request_access, … (1 more)

### Integration Points
- Runtime calls: Path, QueueManager, load_config, pytest.fixture, queue.count, queue_manager.active_agent, queue_manager.metrics, queue_manager.on_tick, queue_manager.queue_snapshot, queue_manager.record_blocked_attempt, queue_manager.release, queue_manager.request_access, … (1 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: queue_manager, test_queue_cooldown_enforced, test_queue_prioritises_wait_time, test_ghost_step_trigger, test_requeue_to_tail_rotates_agent, test_record_blocked_attempt_counts_and_triggers, test_cooldown_expiration_clears_entries


## tests/test_queue_metrics.py

**Purpose**: Pytest coverage for test queue metrics.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: —
- Internal: townlet.config, townlet.world.grid
**Related modules**: townlet.config, townlet.world.grid

### Classes
- None defined.

### Functions
- `_make_world() -> WorldState` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: WorldState
- `test_queue_metrics_capture_ghost_step_and_rotation() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_nightly_reset_preserves_queue_metrics() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None, WorldState
- Internal interactions: —
- External interactions: AgentSnapshot, Path, WorldState.from_config, _make_world, load_config, queue.metrics, queue.record_blocked_attempt, queue.request_access, queue.requeue_to_tail, world._assign_job_if_missing, world._sync_agent_spawn, world.agents.clear, … (3 more)

### Integration Points
- Runtime calls: AgentSnapshot, Path, WorldState.from_config, _make_world, load_config, queue.metrics, queue.record_blocked_attempt, queue.request_access, queue.requeue_to_tail, world._assign_job_if_missing, world._sync_agent_spawn, world.agents.clear, … (3 more)

### Code Quality Notes
- Missing function docstrings: _make_world, test_queue_metrics_capture_ghost_step_and_rotation, test_nightly_reset_preserves_queue_metrics


## tests/test_queue_resume.py

**Purpose**: Pytest coverage for test queue resume.
**Dependencies**:
- Standard Library: __future__, pathlib, random
- Third-Party: pytest
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Classes
- None defined.

### Functions
- `base_config() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `_setup_loop(config) -> SimulationLoop` — No function docstring.
  - Parameters: config
  - Returns: SimulationLoop
- `test_queue_metrics_resume(tmp_path, base_config) -> None` — No function docstring.
  - Parameters: tmp_path, base_config
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: base_config, config, tmp_path
- Outputs: None, SimulationLoop
- Internal interactions: —
- External interactions: AgentSnapshot, Path, SimulationLoop, _setup_loop, config_path.exists, load_config, loop.save_snapshot, pytest.fixture, pytest.skip, random.seed, resumed.load_snapshot, resumed.world.queue_manager.export_state, … (6 more)

### Integration Points
- Runtime calls: AgentSnapshot, Path, SimulationLoop, _setup_loop, config_path.exists, load_config, loop.save_snapshot, pytest.fixture, pytest.skip, random.seed, resumed.load_snapshot, resumed.world.queue_manager.export_state, … (6 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: base_config, _setup_loop, test_queue_metrics_resume


## tests/test_relationship_integration.py

**Purpose**: Pytest coverage for test relationship integration.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: pytest
- Internal: townlet.agents.models, townlet.config, townlet.world.grid
**Related modules**: townlet.agents.models, townlet.config, townlet.world.grid

### Classes
- None defined.

### Functions
- `base_config() -> SimulationConfig` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: SimulationConfig
- `_with_relationship_modifiers(config, enabled) -> SimulationConfig` — No function docstring.
  - Parameters: config, enabled
  - Returns: SimulationConfig
- `_build_world(config) -> WorldState` — No function docstring.
  - Parameters: config
  - Returns: WorldState
- `_familiarity(world, owner, other) -> float` — No function docstring.
  - Parameters: world, owner, other
  - Returns: float
- `test_chat_success_personality_bonus_applied(base_config) -> None` — No function docstring.
  - Parameters: base_config
  - Returns: None
- `test_chat_success_parity_when_disabled(base_config) -> None` — No function docstring.
  - Parameters: base_config
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: base_config, config, enabled, other, owner, world
- Outputs: None, SimulationConfig, WorldState, float
- Internal interactions: —
- External interactions: AgentSnapshot, Path, Personality, SimulationConfig.model_validate, WorldState.from_config, _build_world, _familiarity, _with_relationship_modifiers, config.model_dump, get, load_config, pytest.approx, … (4 more)

### Integration Points
- Runtime calls: AgentSnapshot, Path, Personality, SimulationConfig.model_validate, WorldState.from_config, _build_world, _familiarity, _with_relationship_modifiers, config.model_dump, get, load_config, pytest.approx, … (4 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: base_config, _with_relationship_modifiers, _build_world, _familiarity, test_chat_success_personality_bonus_applied, test_chat_success_parity_when_disabled


## tests/test_relationship_ledger.py

**Purpose**: Pytest coverage for test relationship ledger.
**Dependencies**:
- Standard Library: __future__
- Third-Party: —
- Internal: townlet.world.relationships
**Related modules**: townlet.world.relationships

### Classes
- None defined.

### Functions
- `test_apply_delta_clamps_and_prunes() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_decay_removes_zero_ties() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_eviction_hook_invoked_for_capacity() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_eviction_hook_invoked_for_decay() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None
- Internal interactions: —
- External interactions: RelationshipLedger, RelationshipParameters, events.append, ledger.apply_delta, ledger.decay, ledger.snapshot

### Integration Points
- Runtime calls: RelationshipLedger, RelationshipParameters, events.append, ledger.apply_delta, ledger.decay, ledger.snapshot

### Code Quality Notes
- Missing function docstrings: test_apply_delta_clamps_and_prunes, test_decay_removes_zero_ties, test_eviction_hook_invoked_for_capacity, test_eviction_hook_invoked_for_decay


## tests/test_relationship_metrics.py

**Purpose**: Pytest coverage for test relationship metrics.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.telemetry.relationship_metrics, townlet.world.grid
**Related modules**: townlet.config, townlet.telemetry.relationship_metrics, townlet.world.grid

### Classes
- None defined.

### Functions
- `test_record_eviction_tracks_counts() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_window_rolls_and_history_records_samples() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_latest_payload_round_trips_via_ingest() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_invalid_configuration_raises() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_world_relationship_metrics_records_evictions() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_world_relationship_update_symmetry() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_queue_events_modify_relationships() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_shared_meal_updates_relationship() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_absence_triggers_took_my_shift_relationships() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_late_help_creates_positive_relationship() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_chat_outcomes_adjust_relationships() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_relationship_tie_helper_returns_current_values() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_consume_chat_events_is_single_use() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None
- Internal interactions: —
- External interactions: AgentSnapshot, Path, RelationshipChurnAccumulator, WorldState.from_config, acc.history, acc.latest_payload, acc.record_eviction, acc.snapshot, load_config, pytest.approx, pytest.raises, restored.history, … (17 more)

### Integration Points
- Runtime calls: AgentSnapshot, Path, RelationshipChurnAccumulator, WorldState.from_config, acc.history, acc.latest_payload, acc.record_eviction, acc.snapshot, load_config, pytest.approx, pytest.raises, restored.history, … (17 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: test_record_eviction_tracks_counts, test_window_rolls_and_history_records_samples, test_latest_payload_round_trips_via_ingest, test_invalid_configuration_raises, test_world_relationship_metrics_records_evictions, test_world_relationship_update_symmetry, test_queue_events_modify_relationships, test_shared_meal_updates_relationship, test_absence_triggers_took_my_shift_relationships, test_late_help_creates_positive_relationship, test_chat_outcomes_adjust_relationships, test_relationship_tie_helper_returns_current_values, test_consume_chat_events_is_single_use


## tests/test_relationship_personality_modifiers.py

**Purpose**: Pytest coverage for test relationship personality modifiers.
**Dependencies**:
- Standard Library: __future__
- Third-Party: pytest
- Internal: townlet.agents
**Related modules**: townlet.agents

### Classes
- None defined.

### Functions
- `test_modifiers_disabled_returns_baseline() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_forgiveness_scales_negative_values() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_extroversion_adds_chat_bonus() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_ambition_scales_conflict_rivalry() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_unforgiving_agent_intensifies_negative_hits() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None
- Internal interactions: —
- External interactions: Personality, RelationshipDelta, apply_personality_modifiers, pytest.approx

### Integration Points
- Runtime calls: Personality, RelationshipDelta, apply_personality_modifiers, pytest.approx
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: test_modifiers_disabled_returns_baseline, test_forgiveness_scales_negative_values, test_extroversion_adds_chat_bonus, test_ambition_scales_conflict_rivalry, test_unforgiving_agent_intensifies_negative_hits


## tests/test_reward_engine.py

**Purpose**: Pytest coverage for test reward engine.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.rewards.engine, townlet.world.grid
**Related modules**: townlet.config, townlet.rewards.engine, townlet.world.grid

### Classes
- **StubSnapshot** (bases: object; decorators: —) — No class docstring.
  - Methods:
    - `__init__(self, needs, wallet) -> None` — No method docstring.
- **StubWorld** (bases: object; decorators: —) — No class docstring.
  - Methods:
    - `__init__(self, config, snapshot, context) -> None` — No method docstring.
    - `consume_chat_events(self) -> None` — No method docstring.
    - `agent_context(self, agent_id) -> dict[str, float]` — No method docstring.
    - `relationship_tie(self, subject, target) -> None` — No method docstring.
    - `rivalry_top(self, agent_id, limit) -> None` — No method docstring.

### Functions
- `_make_world(hunger) -> WorldState` — No function docstring. Side effects: filesystem.
  - Parameters: hunger
  - Returns: WorldState
- `test_reward_negative_with_high_deficit() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_reward_clipped_by_config() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_survival_tick_positive_when_balanced() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_chat_reward_applied_for_successful_conversation() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_chat_reward_skipped_when_needs_override_triggers() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_chat_reward_blocked_within_termination_window() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_episode_clip_enforced() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_wage_and_punctuality_bonus() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_terminal_penalty_applied_for_faint() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_terminal_penalty_applied_for_eviction() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: hunger
- Outputs: None, WorldState
- Internal interactions: —
- External interactions: AgentSnapshot, Path, RewardEngine, StubSnapshot, StubWorld, WorldState.from_config, _make_world, compute, engine.compute, engine.latest_reward_breakdown, load_config, needs.items, … (3 more)

### Integration Points
- Runtime calls: AgentSnapshot, Path, RewardEngine, StubSnapshot, StubWorld, WorldState.from_config, _make_world, compute, engine.compute, engine.latest_reward_breakdown, load_config, needs.items, … (3 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: _make_world, test_reward_negative_with_high_deficit, test_reward_clipped_by_config, test_survival_tick_positive_when_balanced, test_chat_reward_applied_for_successful_conversation, test_chat_reward_skipped_when_needs_override_triggers, test_chat_reward_blocked_within_termination_window, test_episode_clip_enforced, test_wage_and_punctuality_bonus, test_terminal_penalty_applied_for_faint, test_terminal_penalty_applied_for_eviction
- Missing method docstrings: StubSnapshot.__init__, StubWorld.__init__, StubWorld.consume_chat_events, StubWorld.agent_context, StubWorld.relationship_tie, StubWorld.rivalry_top


## tests/test_reward_summary.py

**Purpose**: Pytest coverage for test reward summary.
**Dependencies**:
- Standard Library: json, pathlib
- Third-Party: —
- Internal: scripts.reward_summary
**Related modules**: scripts.reward_summary

### Classes
- None defined.

### Functions
- `test_component_stats_mean_and_extremes() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_reward_aggregator_tracks_components(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: tmp_path
- Outputs: None
- Internal interactions: —
- External interactions: ComponentStats, aggregator.summary, collect_statistics, json.dumps, path.write_text, render_text, stats.as_dict, stats.update

### Integration Points
- Runtime calls: ComponentStats, aggregator.summary, collect_statistics, json.dumps, path.write_text, render_text, stats.as_dict, stats.update

### Code Quality Notes
- Missing function docstrings: test_component_stats_mean_and_extremes, test_reward_aggregator_tracks_components


## tests/test_rivalry_ledger.py

**Purpose**: Pytest coverage for test rivalry ledger.
**Dependencies**:
- Standard Library: —
- Third-Party: pytest
- Internal: townlet.world.rivalry
**Related modules**: townlet.world.rivalry

### Classes
- None defined.

### Functions
- `test_increment_and_clamp_and_eviction() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_decay_and_eviction_threshold() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_should_avoid_toggle() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None
- Internal interactions: —
- External interactions: RivalryLedger, RivalryParameters, ledger.apply_conflict, ledger.decay, ledger.inject, ledger.score_for, ledger.should_avoid, ledger.snapshot, pytest.approx, snapshot.values

### Integration Points
- Runtime calls: RivalryLedger, RivalryParameters, ledger.apply_conflict, ledger.decay, ledger.inject, ledger.score_for, ledger.should_avoid, ledger.snapshot, pytest.approx, snapshot.values
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: test_increment_and_clamp_and_eviction, test_decay_and_eviction_threshold, test_should_avoid_toggle


## tests/test_rivalry_state.py

**Purpose**: Pytest coverage for test rivalry state.
**Dependencies**:
- Standard Library: __future__
- Third-Party: —
- Internal: townlet.world.rivalry
**Related modules**: townlet.world.rivalry

### Classes
- None defined.

### Functions
- `test_apply_conflict_clamps_to_max() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_decay_evicts_low_scores() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_should_avoid_threshold() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_encode_features_fixed_width() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None
- Internal interactions: —
- External interactions: RivalryLedger, RivalryParameters, ledger.apply_conflict, ledger.decay, ledger.encode_features, ledger.inject, ledger.score_for, ledger.should_avoid, ledger.snapshot

### Integration Points
- Runtime calls: RivalryLedger, RivalryParameters, ledger.apply_conflict, ledger.decay, ledger.encode_features, ledger.inject, ledger.score_for, ledger.should_avoid, ledger.snapshot

### Code Quality Notes
- Missing function docstrings: test_apply_conflict_clamps_to_max, test_decay_evicts_low_scores, test_should_avoid_threshold, test_encode_features_fixed_width


## tests/test_rollout_buffer.py

**Purpose**: Pytest coverage for test rollout buffer.
**Dependencies**:
- Standard Library: __future__, json, pathlib
- Third-Party: numpy, pytest
- Internal: townlet.config, townlet.policy.rollout, townlet.policy.runner
**Related modules**: townlet.config, townlet.policy.rollout, townlet.policy.runner

### Classes
- None defined.

### Functions
- `_dummy_frame(agent_id, reward, done) -> dict[str, object]` — No function docstring.
  - Parameters: agent_id, reward, done
  - Returns: dict[str, object]
- `test_rollout_buffer_grouping_to_samples() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_training_harness_capture_rollout(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_rollout_buffer_empty_build_dataset_raises() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_rollout_buffer_single_timestep_metrics() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: agent_id, done, reward, tmp_path
- Outputs: None, dict[str, object]
- Internal interactions: —
- External interactions: Path, RolloutBuffer, TrainingHarness, _dummy_frame, baseline.get, buffer.build_dataset, buffer.extend, buffer.to_samples, harness.capture_rollout, json.loads, load_config, manifest.exists, … (8 more)

### Integration Points
- Runtime calls: Path, RolloutBuffer, TrainingHarness, _dummy_frame, baseline.get, buffer.build_dataset, buffer.extend, buffer.to_samples, harness.capture_rollout, json.loads, load_config, manifest.exists, … (8 more)
- Third-party libraries: numpy, pytest

### Code Quality Notes
- Missing function docstrings: _dummy_frame, test_rollout_buffer_grouping_to_samples, test_training_harness_capture_rollout, test_rollout_buffer_empty_build_dataset_raises, test_rollout_buffer_single_timestep_metrics


## tests/test_rollout_capture.py

**Purpose**: Pytest coverage for test rollout capture.
**Dependencies**:
- Standard Library: __future__, json, pathlib, sys
- Third-Party: numpy, pytest
- Internal: townlet.config
**Related modules**: townlet.config

### Classes
- None defined.

### Functions
- `test_capture_rollout_scenarios(tmp_path, config_path) -> None` — No function docstring.
  - Parameters: tmp_path, config_path
  - Returns: None

### Constants and Configuration
- `SCENARIO_CONFIGS` = "[Path('configs/scenarios/kitchen_breakfast.yaml'), Path('configs/scenarios/queue_conflict.yaml'), Path('configs/scenarios/employment_punctuality.yaml'), Path('configs/scenarios/rivalry_decay.yaml'), Path('configs/scenarios/observation_baseline.yaml')]"
- `GOLDEN_STATS_PATH` = "Path('docs/samples/rollout_scenario_stats.json')"
- `GOLDEN_STATS` = 'json.loads(GOLDEN_STATS_PATH.read_text()) if GOLDEN_STATS_PATH.exists() else {}'

### Data Flow
- Inputs: config_path, tmp_path
- Outputs: None
- Internal interactions: —
- External interactions: GOLDEN_STATS.get, golden.get, json.loads, load_config, manifest.exists, manifest.read_text, manifest_metadata.get, manifest_payload.get, mean, metrics_data.get, metrics_file.exists, metrics_file.read_text, … (9 more)

### Integration Points
- Runtime calls: GOLDEN_STATS.get, golden.get, json.loads, load_config, manifest.exists, manifest.read_text, manifest_metadata.get, manifest_payload.get, mean, metrics_data.get, metrics_file.exists, metrics_file.read_text, … (9 more)
- Third-party libraries: numpy, pytest

### Code Quality Notes
- Missing function docstrings: test_capture_rollout_scenarios


## tests/test_run_anneal_rehearsal.py

**Purpose**: Pytest coverage for test run anneal rehearsal.
**Dependencies**:
- Standard Library: importlib.util, pathlib, sys
- Third-Party: pytest
- Internal: townlet.policy.models
**Related modules**: townlet.policy.models

### Classes
- None defined.

### Functions
- `test_run_anneal_rehearsal_pass(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: tmp_path
- Outputs: None
- Internal interactions: —
- External interactions: Path, evaluate_summary, pytest.mark.skipif, run_rehearsal, torch_available

### Integration Points
- Runtime calls: Path, evaluate_summary, pytest.mark.skipif, run_rehearsal, torch_available
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: test_run_anneal_rehearsal_pass


## tests/test_scripted_behavior.py

**Purpose**: Pytest coverage for test scripted behavior.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: numpy
- Internal: townlet.config, townlet.core.sim_loop, townlet.policy.behavior, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.policy.behavior, townlet.world.grid

### Classes
- None defined.

### Functions
- `test_scripted_behavior_determinism() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None
- Internal interactions: —
- External interactions: AgentIntent, AgentSnapshot, Path, SimulationLoop, StubBehavior, __init__, actions_first.extend, actions_second.extend, frame.get, load_config, loop.policy.collect_trajectory, loop.step, … (1 more)

### Integration Points
- Runtime calls: AgentIntent, AgentSnapshot, Path, SimulationLoop, StubBehavior, __init__, actions_first.extend, actions_second.extend, frame.get, load_config, loop.policy.collect_trajectory, loop.step, … (1 more)
- Third-party libraries: numpy

### Code Quality Notes
- Missing function docstrings: test_scripted_behavior_determinism


## tests/test_sim_loop_snapshot.py

**Purpose**: Pytest coverage for test sim loop snapshot.
**Dependencies**:
- Standard Library: __future__, json, pathlib, random
- Third-Party: pytest
- Internal: townlet.config, townlet.core.sim_loop, townlet.snapshots.state, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.snapshots.state, townlet.world.grid

### Classes
- None defined.

### Functions
- `base_config() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_simulation_loop_snapshot_round_trip(tmp_path, base_config) -> None` — No function docstring.
  - Parameters: tmp_path, base_config
  - Returns: None
- `test_save_snapshot_uses_config_root_and_identity_override(tmp_path, base_config) -> None` — No function docstring.
  - Parameters: tmp_path, base_config
  - Returns: None
- `test_simulation_resume_equivalence(tmp_path, base_config) -> None` — No function docstring.
  - Parameters: tmp_path, base_config
  - Returns: None
- `test_policy_transitions_resume(tmp_path, base_config) -> None` — No function docstring.
  - Parameters: tmp_path, base_config
  - Returns: None
- `_normalise_snapshot(snapshot) -> dict[str, object]` — No function docstring.
  - Parameters: snapshot
  - Returns: dict[str, object]

### Constants and Configuration
- None.

### Data Flow
- Inputs: base_config, snapshot, tmp_path
- Outputs: None, dict[str, object]
- Internal interactions: —
- External interactions: AgentSnapshot, Path, SimulationConfig.model_validate, SimulationLoop, _normalise_snapshot, as_dict, base_config.model_dump, baseline.save_snapshot, baseline.step, baseline.telemetry.export_console_buffer, baseline.telemetry.export_state, baseline.telemetry.queue_console_command, … (42 more)

### Integration Points
- Runtime calls: AgentSnapshot, Path, SimulationConfig.model_validate, SimulationLoop, _normalise_snapshot, as_dict, base_config.model_dump, baseline.save_snapshot, baseline.step, baseline.telemetry.export_console_buffer, baseline.telemetry.export_state, baseline.telemetry.queue_console_command, … (42 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: base_config, test_simulation_loop_snapshot_round_trip, test_save_snapshot_uses_config_root_and_identity_override, test_simulation_resume_equivalence, test_policy_transitions_resume, _normalise_snapshot


## tests/test_sim_loop_structure.py

**Purpose**: Pytest coverage for test sim loop structure.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: —
- Internal: townlet.config, townlet.core.sim_loop
**Related modules**: townlet.config, townlet.core.sim_loop

### Classes
- None defined.

### Functions
- `test_simulation_loop_runs_one_tick(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: tmp_path
- Outputs: None
- Internal interactions: —
- External interactions: Path, SimulationLoop, load_config, loop.run

### Integration Points
- Runtime calls: Path, SimulationLoop, load_config, loop.run

### Code Quality Notes
- Missing function docstrings: test_simulation_loop_runs_one_tick


## tests/test_snapshot_manager.py

**Purpose**: Pytest coverage for test snapshot manager.
**Dependencies**:
- Standard Library: __future__, json, pathlib, random
- Third-Party: pytest
- Internal: townlet.config, townlet.scheduler.perturbations, townlet.snapshots.state, townlet.telemetry.publisher, townlet.utils, townlet.world.grid
**Related modules**: townlet.config, townlet.scheduler.perturbations, townlet.snapshots.state, townlet.telemetry.publisher, townlet.utils, townlet.world.grid

### Classes
- None defined.

### Functions
- `sample_config() -> SimulationConfig` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: SimulationConfig
- `test_snapshot_round_trip(tmp_path, sample_config) -> None` — No function docstring.
  - Parameters: tmp_path, sample_config
  - Returns: None
- `test_snapshot_config_mismatch_raises(tmp_path, sample_config) -> None` — No function docstring.
  - Parameters: tmp_path, sample_config
  - Returns: None
- `test_snapshot_missing_relationships_field_rejected(tmp_path, sample_config) -> None` — No function docstring.
  - Parameters: tmp_path, sample_config
  - Returns: None
- `test_snapshot_schema_version_mismatch(tmp_path, sample_config) -> None` — No function docstring.
  - Parameters: tmp_path, sample_config
  - Returns: None
- `_config_with_snapshot_updates(config, updates) -> SimulationConfig` — No function docstring.
  - Parameters: config, updates
  - Returns: SimulationConfig
- `test_snapshot_mismatch_allowed_when_guardrail_disabled(tmp_path, sample_config) -> None` — No function docstring.
  - Parameters: tmp_path, sample_config
  - Returns: None
- `test_snapshot_schema_downgrade_honours_allow_flag(tmp_path, sample_config) -> None` — No function docstring.
  - Parameters: tmp_path, sample_config
  - Returns: None
- `test_world_relationship_snapshot_round_trip(tmp_path, sample_config) -> None` — No function docstring.
  - Parameters: tmp_path, sample_config
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: config, sample_config, tmp_path, updates
- Outputs: None, SimulationConfig
- Internal interactions: —
- External interactions: AgentSnapshot, Path, PerturbationScheduler, ScheduledPerturbation, SimulationConfig.model_validate, SnapshotManager, SnapshotState, TelemetryPublisher, WorldState.from_config, _config_with_snapshot_updates, apply_snapshot_to_telemetry, apply_snapshot_to_world, … (49 more)

### Integration Points
- Runtime calls: AgentSnapshot, Path, PerturbationScheduler, ScheduledPerturbation, SimulationConfig.model_validate, SnapshotManager, SnapshotState, TelemetryPublisher, WorldState.from_config, _config_with_snapshot_updates, apply_snapshot_to_telemetry, apply_snapshot_to_world, … (49 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: sample_config, test_snapshot_round_trip, test_snapshot_config_mismatch_raises, test_snapshot_missing_relationships_field_rejected, test_snapshot_schema_version_mismatch, _config_with_snapshot_updates, test_snapshot_mismatch_allowed_when_guardrail_disabled, test_snapshot_schema_downgrade_honours_allow_flag, test_world_relationship_snapshot_round_trip


## tests/test_snapshot_migrations.py

**Purpose**: Pytest coverage for test snapshot migrations.
**Dependencies**:
- Standard Library: __future__, dataclasses, pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.snapshots, townlet.snapshots.migrations
**Related modules**: townlet.config, townlet.snapshots, townlet.snapshots.migrations

### Classes
- None defined.

### Functions
- `sample_config() -> SimulationConfig` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: SimulationConfig
- `reset_registry() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `_basic_state(config) -> SnapshotState` — No function docstring.
  - Parameters: config
  - Returns: SnapshotState
- `test_snapshot_migration_applied(tmp_path, sample_config) -> None` — No function docstring.
  - Parameters: tmp_path, sample_config
  - Returns: None
- `test_snapshot_migration_multi_step(tmp_path, sample_config) -> None` — No function docstring.
  - Parameters: tmp_path, sample_config
  - Returns: None
- `test_snapshot_migration_missing_path_raises(tmp_path, sample_config) -> None` — No function docstring.
  - Parameters: tmp_path, sample_config
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: config, sample_config, tmp_path
- Outputs: None, SimulationConfig, SnapshotState
- Internal interactions: —
- External interactions: Path, SnapshotManager, SnapshotState, _basic_state, clear_registry, config_path.exists, load_config, loaded.identity.get, manager.load, manager.save, pytest.fixture, pytest.raises, … (3 more)

### Integration Points
- Runtime calls: Path, SnapshotManager, SnapshotState, _basic_state, clear_registry, config_path.exists, load_config, loaded.identity.get, manager.load, manager.save, pytest.fixture, pytest.raises, … (3 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: sample_config, reset_registry, _basic_state, test_snapshot_migration_applied, test_snapshot_migration_multi_step, test_snapshot_migration_missing_path_raises


## tests/test_stability_monitor.py

**Purpose**: Pytest coverage for test stability monitor.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: —
- Internal: townlet.config, townlet.stability.monitor
**Related modules**: townlet.config, townlet.stability.monitor

### Classes
- None defined.

### Functions
- `make_monitor() -> StabilityMonitor` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: StabilityMonitor
- `_track_minimal(monitor) -> None` — No function docstring.
  - Parameters: monitor
  - Returns: None
- `test_starvation_spike_alert_triggers_after_streak() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_option_thrash_alert_averages_over_window() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_reward_variance_alert_exports_state() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_queue_fairness_alerts_include_metrics() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_rivalry_spike_alert_triggers_on_intensity() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_promotion_window_tracking() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_promotion_window_respects_allowed_alerts() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: monitor
- Outputs: None, StabilityMonitor
- Internal interactions: —
- External interactions: Path, StabilityMonitor, _track_minimal, load_config, make_monitor, monitor.export_state, monitor.latest_metrics, monitor.track, restored.import_state, restored.latest_metrics

### Integration Points
- Runtime calls: Path, StabilityMonitor, _track_minimal, load_config, make_monitor, monitor.export_state, monitor.latest_metrics, monitor.track, restored.import_state, restored.latest_metrics

### Code Quality Notes
- Missing function docstrings: make_monitor, _track_minimal, test_starvation_spike_alert_triggers_after_streak, test_option_thrash_alert_averages_over_window, test_reward_variance_alert_exports_state, test_queue_fairness_alerts_include_metrics, test_rivalry_spike_alert_triggers_on_intensity, test_promotion_window_tracking, test_promotion_window_respects_allowed_alerts


## tests/test_stability_telemetry.py

**Purpose**: Pytest coverage for test stability telemetry.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet.world.grid

### Classes
- None defined.

### Functions
- `test_stability_alerts_exposed_via_telemetry_snapshot(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: tmp_path
- Outputs: None
- Internal interactions: —
- External interactions: AgentSnapshot, ConsoleCommand, Path, SimulationLoop, config_path.exists, create_console_router, load_config, loop.step, loop.telemetry.latest_stability_alerts, loop.telemetry.latest_stability_metrics, pytest.skip, router.dispatch

### Integration Points
- Runtime calls: AgentSnapshot, ConsoleCommand, Path, SimulationLoop, config_path.exists, create_console_router, load_config, loop.step, loop.telemetry.latest_stability_alerts, loop.telemetry.latest_stability_metrics, pytest.skip, router.dispatch
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: test_stability_alerts_exposed_via_telemetry_snapshot


## tests/test_telemetry_client.py

**Purpose**: Pytest coverage for test telemetry client.
**Dependencies**:
- Standard Library: collections.abc, pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet_ui.telemetry
**Related modules**: townlet.config, townlet.console.handlers, townlet.core.sim_loop, townlet_ui.telemetry

### Classes
- None defined.

### Functions
- `make_simulation(enforce_job_loop) -> SimulationLoop` — No function docstring. Side effects: filesystem.
  - Parameters: enforce_job_loop
  - Returns: SimulationLoop
- `test_telemetry_client_parses_console_snapshot() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_telemetry_client_warns_on_newer_schema(monkeypatch) -> None` — No function docstring.
  - Parameters: monkeypatch
  - Returns: None
- `test_telemetry_client_raises_on_major_mismatch() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: enforce_job_loop, monkeypatch
- Outputs: None, SimulationLoop
- Internal interactions: —
- External interactions: AgentSnapshot, Path, SimulationLoop, TelemetryClient, client.from_console, client.parse_snapshot, create_console_router, load_config, loop.step, make_simulation, pytest.raises, snapshot.schema_version.startswith, … (1 more)

### Integration Points
- Runtime calls: AgentSnapshot, Path, SimulationLoop, TelemetryClient, client.from_console, client.parse_snapshot, create_console_router, load_config, loop.step, make_simulation, pytest.raises, snapshot.schema_version.startswith, … (1 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: make_simulation, test_telemetry_client_parses_console_snapshot, test_telemetry_client_warns_on_newer_schema, test_telemetry_client_raises_on_major_mismatch


## tests/test_telemetry_jobs.py

**Purpose**: Pytest coverage for test telemetry jobs.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.core.sim_loop, townlet.stability.monitor, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.stability.monitor, townlet.world.grid

### Classes
- None defined.

### Functions
- `test_telemetry_captures_job_snapshot() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_stability_monitor_lateness_alert() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None
- Internal interactions: —
- External interactions: AgentSnapshot, Path, SimulationLoop, StabilityMonitor, load_config, loop.step, monitor.track, publisher.latest_job_snapshot, snapshot.values, world._assign_jobs_to_agents

### Integration Points
- Runtime calls: AgentSnapshot, Path, SimulationLoop, StabilityMonitor, load_config, loop.step, monitor.track, publisher.latest_job_snapshot, snapshot.values, world._assign_jobs_to_agents
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: test_telemetry_captures_job_snapshot, test_stability_monitor_lateness_alert


## tests/test_telemetry_narration.py

**Purpose**: Pytest coverage for test telemetry narration.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.telemetry.narration, townlet.telemetry.publisher, townlet.world.grid
**Related modules**: townlet.config, townlet.telemetry.narration, townlet.telemetry.publisher, townlet.world.grid

### Classes
- None defined.

### Functions
- `test_narration_rate_limiter_enforces_cooldowns() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_narration_rate_limiter_priority_bypass() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_telemetry_publisher_emits_queue_conflict_narration(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: tmp_path
- Outputs: None
- Internal interactions: —
- External interactions: NarrationRateLimiter, NarrationThrottleConfig, Path, TelemetryPublisher, WorldState.from_config, config.telemetry.model_copy, config.telemetry.narration.model_copy, limiter.allow, limiter.begin_tick, load_config, publisher.latest_narrations, publisher.publish_tick

### Integration Points
- Runtime calls: NarrationRateLimiter, NarrationThrottleConfig, Path, TelemetryPublisher, WorldState.from_config, config.telemetry.model_copy, config.telemetry.narration.model_copy, limiter.allow, limiter.begin_tick, load_config, publisher.latest_narrations, publisher.publish_tick
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: test_narration_rate_limiter_enforces_cooldowns, test_narration_rate_limiter_priority_bypass, test_telemetry_publisher_emits_queue_conflict_narration


## tests/test_telemetry_new_events.py

**Purpose**: Pytest coverage for test telemetry new events.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: —
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Classes
- None defined.

### Functions
- `make_loop() -> SimulationLoop` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: SimulationLoop
- `test_shower_events_in_telemetry() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_shower_complete_narration() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_sleep_events_in_telemetry() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_affordance_runtime_running_snapshot() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_rivalry_events_surface_in_telemetry() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None, SimulationLoop
- Internal interactions: —
- External interactions: AgentSnapshot, Path, SimulationLoop, conflict.get, e.get, event.get, events.extend, load_config, loop.world.agents.clear, make_loop, snapshot.get, telemetry.export_state, … (13 more)

### Integration Points
- Runtime calls: AgentSnapshot, Path, SimulationLoop, conflict.get, e.get, event.get, events.extend, load_config, loop.world.agents.clear, make_loop, snapshot.get, telemetry.export_state, … (13 more)

### Code Quality Notes
- Missing function docstrings: make_loop, test_shower_events_in_telemetry, test_shower_complete_narration, test_sleep_events_in_telemetry, test_affordance_runtime_running_snapshot, test_rivalry_events_surface_in_telemetry


## tests/test_telemetry_stream_smoke.py

**Purpose**: Pytest coverage for test telemetry stream smoke.
**Dependencies**:
- Standard Library: __future__, json, pathlib
- Third-Party: —
- Internal: townlet.config, townlet.core.sim_loop, townlet_ui.telemetry
**Related modules**: townlet.config, townlet.core.sim_loop, townlet_ui.telemetry

### Classes
- None defined.

### Functions
- `_ensure_agents(loop) -> None` — No function docstring.
  - Parameters: loop
  - Returns: None
- `test_file_transport_stream_smoke(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: loop, tmp_path
- Outputs: None
- Internal interactions: —
- External interactions: AgentSnapshot, Path, SimulationLoop, TelemetryClient, _ensure_agents, json.loads, line.strip, load_config, loop.step, loop.telemetry.close, parse_snapshot, snapshot.schema_version.startswith, … (4 more)

### Integration Points
- Runtime calls: AgentSnapshot, Path, SimulationLoop, TelemetryClient, _ensure_agents, json.loads, line.strip, load_config, loop.step, loop.telemetry.close, parse_snapshot, snapshot.schema_version.startswith, … (4 more)

### Code Quality Notes
- Missing function docstrings: _ensure_agents, test_file_transport_stream_smoke


## tests/test_telemetry_summary.py

**Purpose**: Pytest coverage for test telemetry summary.
**Dependencies**:
- Standard Library: __future__, importlib.util, pathlib, sys
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `test_summary_includes_new_events(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: tmp_path
- Outputs: None
- Internal interactions: —
- External interactions: join, log.write_text, telemetry_summary.json.dumps, telemetry_summary.load_records, telemetry_summary.render_markdown, telemetry_summary.render_text, telemetry_summary.summarise

### Integration Points
- Runtime calls: join, log.write_text, telemetry_summary.json.dumps, telemetry_summary.load_records, telemetry_summary.render_markdown, telemetry_summary.render_text, telemetry_summary.summarise

### Code Quality Notes
- Missing function docstrings: test_summary_includes_new_events


## tests/test_telemetry_transport.py

**Purpose**: Pytest coverage for test telemetry transport.
**Dependencies**:
- Standard Library: __future__, json, pathlib, time
- Third-Party: pytest
- Internal: townlet.config, townlet.core.sim_loop, townlet.telemetry.transport
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.telemetry.transport

### Classes
- None defined.

### Functions
- `_ensure_agents(loop) -> None` — No function docstring.
  - Parameters: loop
  - Returns: None
- `test_transport_buffer_drop_until_capacity() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_telemetry_publisher_flushes_payload(monkeypatch) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: monkeypatch
  - Returns: None
- `test_telemetry_publisher_retries_on_failure(monkeypatch) -> None` — No function docstring. Side effects: filesystem. Raises: RuntimeError('simulated send failure').
  - Parameters: monkeypatch
  - Returns: None
- `test_telemetry_worker_metrics_and_stop(monkeypatch) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: monkeypatch
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: loop, monkeypatch
- Outputs: None
- Internal interactions: —
- External interactions: AgentSnapshot, CaptureTransport, FlakyTransport, NoopTransport, Path, SimulationLoop, TransportBuffer, _ensure_agents, buffer.append, buffer.drop_until_within_capacity, buffer.is_over_capacity, decode, … (17 more)

### Integration Points
- Runtime calls: AgentSnapshot, CaptureTransport, FlakyTransport, NoopTransport, Path, SimulationLoop, TransportBuffer, _ensure_agents, buffer.append, buffer.drop_until_within_capacity, buffer.is_over_capacity, decode, … (17 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: _ensure_agents, test_transport_buffer_drop_until_capacity, test_telemetry_publisher_flushes_payload, test_telemetry_publisher_retries_on_failure, test_telemetry_worker_metrics_and_stop


## tests/test_telemetry_validator.py

**Purpose**: Pytest coverage for test telemetry validator.
**Dependencies**:
- Standard Library: __future__, json, pathlib
- Third-Party: pytest
- Internal: scripts.validate_ppo_telemetry
**Related modules**: scripts.validate_ppo_telemetry

### Classes
- None defined.

### Functions
- `_write_ndjson(path, record) -> None` — No function docstring.
  - Parameters: path, record
  - Returns: None
- `test_validate_ppo_telemetry_accepts_valid_log(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_validate_ppo_telemetry_raises_for_missing_conflict(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_validate_ppo_telemetry_accepts_version_1_1(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_validate_ppo_telemetry_v1_1_missing_field_raises(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- `VALID_RECORD` = {"epoch": 1.0, "updates": 2.0, "transitions": 4.0, "loss_policy": 0.1, "loss_value": 0.2, "loss_entropy": 0.3, "loss_total": 0.4, "clip_fraction": 0.1, "adv_mean": 0.0, "adv_std": 0.1, "adv_zero_std_batches": 0.0, "adv_min_std": 0.1, "clip_triggered_minibatches": 0.0, "clip_fraction_max": 0.1, "grad_norm": 1.5, "kl_divergence": 0.01, "telemetry_version": 1.0, "lr": 0.0003, "steps": 4.0, "baseline_sample_count": 2.0, "baseline_reward_mean": 0.25, "baseline_reward_sum": 1.0, "baseline_reward_sum_mean": 0.5, "baseline_log_prob_mean": -0.2, "conflict.rivalry_max_mean_avg": 0.05, "conflict.rivalry_max_max_avg": 0.1, "conflict.rivalry_avoid_count_mean_avg": 0.0, "conflict.rivalry_avoid_count_max_avg": 0.0}

### Data Flow
- Inputs: path, record, tmp_path
- Outputs: None
- Internal interactions: —
- External interactions: VALID_RECORD.items, _write_ndjson, baseline_path.write_text, json.dumps, key.startswith, path.write_text, pytest.raises, validate_logs

### Integration Points
- Runtime calls: VALID_RECORD.items, _write_ndjson, baseline_path.write_text, json.dumps, key.startswith, path.write_text, pytest.raises, validate_logs
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: _write_ndjson, test_validate_ppo_telemetry_accepts_valid_log, test_validate_ppo_telemetry_raises_for_missing_conflict, test_validate_ppo_telemetry_accepts_version_1_1, test_validate_ppo_telemetry_v1_1_missing_field_raises


## tests/test_telemetry_watch.py

**Purpose**: Pytest coverage for test telemetry watch.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: pytest
- Internal: scripts.telemetry_watch
**Related modules**: scripts.telemetry_watch

### Classes
- None defined.

### Functions
- `test_parse_health_line() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_stream_health_records(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_health_thresholds_raise() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: tmp_path
- Outputs: None
- Internal interactions: —
- External interactions: _parse_health_line, check_health_thresholds, log.write_text, pytest.approx, pytest.raises, stream_health_records

### Integration Points
- Runtime calls: _parse_health_line, check_health_thresholds, log.write_text, pytest.approx, pytest.raises, stream_health_records
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: test_parse_health_line, test_stream_health_records, test_health_thresholds_raise


## tests/test_training_anneal.py

**Purpose**: Pytest coverage for test training anneal.
**Dependencies**:
- Standard Library: __future__, json, pathlib
- Third-Party: numpy, pytest
- Internal: townlet.config, townlet.policy.models, townlet.policy.replay, townlet.policy.runner
**Related modules**: townlet.config, townlet.policy.models, townlet.policy.replay, townlet.policy.runner

### Classes
- None defined.

### Functions
- `_write_sample(output_dir, stem, timesteps, action_dim) -> tuple[Path, Path]` — No function docstring.
  - Parameters: output_dir, stem, timesteps, action_dim
  - Returns: tuple[Path, Path]
- `test_run_anneal_bc_then_ppo(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: action_dim, output_dir, stem, timesteps, tmp_path
- Outputs: None, tuple[Path, Path]
- Internal interactions: —
- External interactions: AnnealStage, Path, TrainingHarness, _write_sample, bc_dir.mkdir, bc_manifest.write_text, frames.append, frames_to_replay_sample, harness.promotion.snapshot, harness.run_anneal, json.dumps, json_path.write_text, … (8 more)

### Integration Points
- Runtime calls: AnnealStage, Path, TrainingHarness, _write_sample, bc_dir.mkdir, bc_manifest.write_text, frames.append, frames_to_replay_sample, harness.promotion.snapshot, harness.run_anneal, json.dumps, json_path.write_text, … (8 more)
- Third-party libraries: numpy, pytest

### Code Quality Notes
- Missing function docstrings: _write_sample, test_run_anneal_bc_then_ppo


## tests/test_training_cli.py

**Purpose**: Pytest coverage for test training cli.
**Dependencies**:
- Standard Library: __future__, argparse, pathlib
- Third-Party: —
- Internal: scripts, townlet.config
**Related modules**: scripts, townlet.config

### Classes
- None defined.

### Functions
- `_make_namespace() -> Namespace` — No function docstring.
  - Parameters: —
  - Returns: Namespace
- `test_collect_ppo_overrides_handles_values() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_apply_ppo_overrides_creates_config_when_missing() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_apply_ppo_overrides_updates_existing_model() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: Namespace, None
- Internal interactions: —
- External interactions: Namespace, PPOConfig, Path, _make_namespace, defaults.update, load_config, run_training._apply_ppo_overrides, run_training._collect_ppo_overrides

### Integration Points
- Runtime calls: Namespace, PPOConfig, Path, _make_namespace, defaults.update, load_config, run_training._apply_ppo_overrides, run_training._collect_ppo_overrides

### Code Quality Notes
- Missing function docstrings: _make_namespace, test_collect_ppo_overrides_handles_values, test_apply_ppo_overrides_creates_config_when_missing, test_apply_ppo_overrides_updates_existing_model


## tests/test_training_replay.py

**Purpose**: Pytest coverage for test training replay.
**Dependencies**:
- Standard Library: __future__, json, math, pathlib, sys
- Third-Party: numpy, pytest
- Internal: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.policy.models, townlet.policy.replay, townlet.policy.replay_buffer, townlet.policy.runner, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.observations.builder, townlet.policy.models, townlet.policy.replay, townlet.policy.replay_buffer, townlet.policy.runner, townlet.world.grid

### Classes
- None defined.

### Functions
- `_validate_numeric(value) -> None` — No function docstring.
  - Parameters: value
  - Returns: None
- `_assert_ppo_log_schema(summary, require_baseline) -> None` — No function docstring. Raises: AssertionError(f'Unexpected PPO summary key encountered: {key}').
  - Parameters: summary, require_baseline
  - Returns: None
- `_load_expected_stats(config_path) -> dict[str, dict[str, float]]` — No function docstring.
  - Parameters: config_path
  - Returns: dict[str, dict[str, float]]
- `_aggregate_expected_metrics(sample_stats) -> dict[str, float]` — No function docstring.
  - Parameters: sample_stats
  - Returns: dict[str, float]
- `_make_sample(base_dir, rivalry_increment, avoid_threshold, suffix) -> tuple[Path, Path]` — No function docstring. Side effects: filesystem.
  - Parameters: base_dir, rivalry_increment, avoid_threshold, suffix
  - Returns: tuple[Path, Path]
- `_make_social_sample() -> ReplaySample` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: ReplaySample
- `test_training_harness_replay_stats(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_replay_dataset_batch_iteration(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_replay_loader_schema_guard(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_replay_dataset_streaming(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_replay_loader_missing_training_arrays(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_replay_loader_value_length_mismatch(tmp_path) -> None` — No function docstring.
  - Parameters: tmp_path
  - Returns: None
- `test_training_harness_run_ppo_on_capture(tmp_path, config_path) -> None` — No function docstring.
  - Parameters: tmp_path, config_path
  - Returns: None
- `test_training_harness_run_ppo(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_run_ppo_rejects_nan_advantages(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_training_harness_log_sampling_and_rotation(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_training_harness_run_rollout_ppo(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_training_harness_ppo_conflict_telemetry(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_training_harness_run_rollout_ppo_multiple_cycles(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_training_harness_rollout_capture_and_train_cycles(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_training_harness_streaming_log_offsets(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_training_harness_rollout_queue_conflict_metrics(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_ppo_social_chat_drift(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None
- `test_policy_runtime_collects_frames(tmp_path) -> None` — No function docstring. Side effects: filesystem.
  - Parameters: tmp_path
  - Returns: None

### Constants and Configuration
- `SCENARIO_CONFIGS` = "[Path('configs/scenarios/kitchen_breakfast.yaml'), Path('configs/scenarios/queue_conflict.yaml'), Path('configs/scenarios/employment_punctuality.yaml'), Path('configs/scenarios/rivalry_decay.yaml'), Path('configs/scenarios/observation_baseline.yaml')]"
- `GOLDEN_STATS_PATH` = "Path('docs/samples/rollout_scenario_stats.json')"
- `GOLDEN_STATS` = 'json.loads(GOLDEN_STATS_PATH.read_text()) if GOLDEN_STATS_PATH.exists() else {}'
- `REQUIRED_PPO_KEYS` = ["adv_mean", "adv_min_std", "adv_std", "adv_zero_std_batches", "batch_entropy_mean", "batch_entropy_std", "chat_failure_events", "chat_quality_mean", "chat_success_events", "clip_fraction", "clip_fraction_max", "clip_triggered_minibatches", "cycle_id", "data_mode", "epoch", "epoch_duration_sec", "grad_norm", "grad_norm_max", "kl_divergence", "kl_divergence_max", "late_help_events", "log_stream_offset", "loss_entropy", "loss_policy", "loss_total", "loss_value", "lr", "queue_conflict_events", "queue_conflict_intensity_sum", "reward_advantage_corr", "rollout_ticks", "shared_meal_events", "shift_takeover_events", "steps", "telemetry_version", "transitions", "updates"]
- `REQUIRED_PPO_NUMERIC_KEYS` = "REQUIRED_PPO_KEYS - {'data_mode'}"
- `BASELINE_KEYS_REQUIRED` = ["baseline_reward_mean", "baseline_reward_sum", "baseline_reward_sum_mean", "baseline_sample_count"]
- `BASELINE_KEYS_OPTIONAL` = ["baseline_log_prob_mean"]
- `ALLOWED_KEY_PREFIXES` = ["conflict."]

### Data Flow
- Inputs: avoid_threshold, base_dir, config_path, require_baseline, rivalry_increment, sample_stats, suffix, summary, tmp_path, value
- Outputs: None, ReplaySample, dict[str, dict[str, float]], dict[str, float], tuple[Path, Path]
- Internal interactions: —
- External interactions: AgentSnapshot, GOLDEN_STATS.get, InMemoryReplayDataset, InMemoryReplayDatasetConfig, ObservationBuilder, Path, ReplayDataset, ReplayDatasetConfig, ReplayDatasetConfig.from_capture_dir, ReplayDatasetConfig.from_manifest, ReplaySample, SimulationLoop, … (84 more)

### Integration Points
- Runtime calls: AgentSnapshot, GOLDEN_STATS.get, InMemoryReplayDataset, InMemoryReplayDatasetConfig, ObservationBuilder, Path, ReplayDataset, ReplayDatasetConfig, ReplayDatasetConfig.from_capture_dir, ReplayDatasetConfig.from_manifest, ReplaySample, SimulationLoop, … (84 more)
- Third-party libraries: numpy, pytest

### Code Quality Notes
- Missing function docstrings: _validate_numeric, _assert_ppo_log_schema, _load_expected_stats, _aggregate_expected_metrics, _make_sample, _make_social_sample, test_training_harness_replay_stats, test_replay_dataset_batch_iteration, test_replay_loader_schema_guard, test_replay_dataset_streaming, test_replay_loader_missing_training_arrays, test_replay_loader_value_length_mismatch, test_training_harness_run_ppo_on_capture, test_training_harness_run_ppo, test_run_ppo_rejects_nan_advantages, test_training_harness_log_sampling_and_rotation, test_training_harness_run_rollout_ppo, test_training_harness_ppo_conflict_telemetry, test_training_harness_run_rollout_ppo_multiple_cycles, test_training_harness_rollout_capture_and_train_cycles, test_training_harness_streaming_log_offsets, test_training_harness_rollout_queue_conflict_metrics, test_ppo_social_chat_drift, test_policy_runtime_collects_frames


## tests/test_utils_rng.py

**Purpose**: Pytest coverage for test utils rng.
**Dependencies**:
- Standard Library: __future__, random
- Third-Party: pytest
- Internal: townlet.utils
**Related modules**: townlet.utils

### Classes
- None defined.

### Functions
- `test_encode_decode_rng_state_round_trip() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_decode_rng_state_invalid_payload() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None
- Internal interactions: —
- External interactions: decode_rng_state, encode_rng_state, pytest.raises, random.Random, rng.getstate

### Integration Points
- Runtime calls: decode_rng_state, encode_rng_state, pytest.raises, random.Random, rng.getstate
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: test_encode_decode_rng_state_round_trip, test_decode_rng_state_invalid_payload


## tests/test_world_local_view.py

**Purpose**: Pytest coverage for test world local view.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: —
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Classes
- None defined.

### Functions
- `make_loop() -> SimulationLoop` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: SimulationLoop
- `tile_for_position(tiles, position) -> None` — No function docstring. Raises: AssertionError(f'Tile not found for position {position}').
  - Parameters: tiles, position
  - Returns: None
- `test_local_view_includes_objects_and_agents() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_agent_context_defaults() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_world_snapshot_returns_defensive_copies() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: position, tiles
- Outputs: None, SimulationLoop
- Internal interactions: —
- External interactions: AgentSnapshot, Path, SimulationLoop, load_config, loop.world.agents.clear, make_loop, tile_for_position, world.agent_context, world.local_view, world.register_object, world.snapshot

### Integration Points
- Runtime calls: AgentSnapshot, Path, SimulationLoop, load_config, loop.world.agents.clear, make_loop, tile_for_position, world.agent_context, world.local_view, world.register_object, world.snapshot

### Code Quality Notes
- Missing function docstrings: make_loop, tile_for_position, test_local_view_includes_objects_and_agents, test_agent_context_defaults, test_world_snapshot_returns_defensive_copies


## tests/test_world_nightly_reset.py

**Purpose**: Pytest coverage for test world nightly reset.
**Dependencies**:
- Standard Library: __future__, pathlib
- Third-Party: —
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Classes
- None defined.

### Functions
- `_setup_world() -> WorldState` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: WorldState
- `test_apply_nightly_reset_returns_agents_home() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_simulation_loop_triggers_nightly_reset() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None, WorldState
- Internal interactions: —
- External interactions: AgentSnapshot, Path, SimulationLoop, WorldState.from_config, _setup_world, event.get, load_config, loop.step, loop.world._assign_job_if_missing, loop.world._sync_agent_spawn, loop.world.agents.clear, world._assign_job_if_missing, … (4 more)

### Integration Points
- Runtime calls: AgentSnapshot, Path, SimulationLoop, WorldState.from_config, _setup_world, event.get, load_config, loop.step, loop.world._assign_job_if_missing, loop.world._sync_agent_spawn, loop.world.agents.clear, world._assign_job_if_missing, … (4 more)

### Code Quality Notes
- Missing function docstrings: _setup_world, test_apply_nightly_reset_returns_agents_home, test_simulation_loop_triggers_nightly_reset


## tests/test_world_queue_integration.py

**Purpose**: Pytest coverage for test world queue integration.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.core.sim_loop, townlet.world.grid
**Related modules**: townlet.config, townlet.core.sim_loop, townlet.world.grid

### Classes
- None defined.

### Functions
- `_make_world() -> WorldState` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: WorldState
- `test_queue_assignment_flow() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_queue_ghost_step_promotes_waiter() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_affordance_completion_applies_effects() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_eat_meal_adjusts_needs_and_wallet() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_affordance_failure_skips_effects() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_affordances_loaded_from_yaml() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None
- `test_affordance_events_emitted() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_need_decay_applied_each_tick() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_eat_meal_deducts_wallet_and_stock() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_wage_income_applied_on_shift() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_stove_restock_event_emitted() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_scripted_behavior_handles_sleep() -> None` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None, WorldState
- Internal interactions: —
- External interactions: AgentSnapshot, Path, SimulationLoop, WorldState.from_config, _make_world, event.get, get, load_config, loop.step, loop.world.agents.values, pytest.approx, world.active_reservations.get, … (8 more)

### Integration Points
- Runtime calls: AgentSnapshot, Path, SimulationLoop, WorldState.from_config, _make_world, event.get, get, load_config, loop.step, loop.world.agents.values, pytest.approx, world.active_reservations.get, … (8 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: _make_world, test_queue_assignment_flow, test_queue_ghost_step_promotes_waiter, test_affordance_completion_applies_effects, test_eat_meal_adjusts_needs_and_wallet, test_affordance_failure_skips_effects, test_affordances_loaded_from_yaml, test_affordance_events_emitted, test_need_decay_applied_each_tick, test_eat_meal_deducts_wallet_and_stock, test_wage_income_applied_on_shift, test_stove_restock_event_emitted, test_scripted_behavior_handles_sleep


## tests/test_world_rivalry.py

**Purpose**: Pytest coverage for test world rivalry.
**Dependencies**:
- Standard Library: pathlib
- Third-Party: pytest
- Internal: townlet.config, townlet.world.grid
**Related modules**: townlet.config, townlet.world.grid

### Classes
- None defined.

### Functions
- `_make_world() -> WorldState` — No function docstring. Side effects: filesystem.
  - Parameters: —
  - Returns: WorldState
- `test_register_rivalry_conflict_updates_snapshot() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_rivalry_events_record_reason() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_rivalry_decays_over_time() -> None` — No function docstring.
  - Parameters: —
  - Returns: None
- `test_queue_conflict_event_emitted_with_intensity() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- None.

### Data Flow
- Inputs: —
- Outputs: None, WorldState
- Internal interactions: —
- External interactions: AgentSnapshot, Path, WorldState.from_config, _make_world, event.get, load_config, pytest.approx, world.apply_actions, world.consume_rivalry_events, world.drain_events, world.register_object, world.register_rivalry_conflict, … (3 more)

### Integration Points
- Runtime calls: AgentSnapshot, Path, WorldState.from_config, _make_world, event.get, load_config, pytest.approx, world.apply_actions, world.consume_rivalry_events, world.drain_events, world.register_object, world.register_rivalry_conflict, … (3 more)
- Third-party libraries: pytest

### Code Quality Notes
- Missing function docstrings: _make_world, test_register_rivalry_conflict_updates_snapshot, test_rivalry_events_record_reason, test_rivalry_decays_over_time, test_queue_conflict_event_emitted_with_intensity


## tmp/analyze_modules.py

**Purpose**: Module scaffolding for analyze modules.
**Dependencies**:
- Standard Library: __future__, ast, collections, dataclasses, json, os, pathlib, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- **FunctionInfo** (bases: object; decorators: dataclass) — No class docstring.
  - Attributes: name: str = None, signature: str = None, lineno: int = None, docstring: str | None = None, params: list[dict[str, Any]] = None, return_type: str | None = None, is_async: bool = False
  - Methods: None.
- **ClassInfo** (bases: object; decorators: dataclass) — No class docstring.
  - Attributes: name: str = None, bases: list[str] = 'field(default_factory=list)', decorators: list[str] = 'field(default_factory=list)', lineno: int = 0, docstring: str | None = None, methods: list[FunctionInfo] = 'field(default_factory=list)', attributes: list[dict[str, Any]] = 'field(default_factory=list)'
  - Methods: None.
- **ModuleInfo** (bases: object; decorators: dataclass) — No class docstring.
  - Attributes: path: Path = None, module: str = None, module_name: str = None, docstring: str | None = None, imports: dict[str, set[str]] = None, classes: list[ClassInfo] = None, functions: list[FunctionInfo] = None, constants: list[dict[str, Any]] = None, env_vars: list[str] = None, todos: list[int] = None, has_logging: bool = None, has_type_hints: bool = None, … (2 more)
  - Methods: None.

### Functions
- `unparse(node) -> str | None` — No function docstring.
  - Parameters: node
  - Returns: str | None
- `_format_param_entry(name, annotation, default) -> str` — No function docstring.
  - Parameters: name, annotation, default
  - Returns: str
- `build_signature(arguments) -> tuple[str, list[dict[str, Any]]]` — No function docstring.
  - Parameters: arguments
  - Returns: tuple[str, list[dict[str, Any]]]
- `format_return(annotation) -> str` — No function docstring.
  - Parameters: annotation
  - Returns: str
- `module_name_from_path(path) -> str` — No function docstring.
  - Parameters: path
  - Returns: str
- `classify_import(module) -> str` — No function docstring.
  - Parameters: module
  - Returns: str
- `collect_imports(tree, package_parts) -> dict[str, set[str]]` — No function docstring.
  - Parameters: tree, package_parts
  - Returns: dict[str, set[str]]
- `gather_class_attributes(body) -> list[dict[str, Any]]` — No function docstring.
  - Parameters: body
  - Returns: list[dict[str, Any]]
- `gather_constants(body) -> list[dict[str, Any]]` — No function docstring.
  - Parameters: body
  - Returns: list[dict[str, Any]]
- `detect_env_usage(tree) -> list[str]` — No function docstring.
  - Parameters: tree
  - Returns: list[str]
- `gather_functions(body) -> list[FunctionInfo]` — No function docstring.
  - Parameters: body
  - Returns: list[FunctionInfo]
- `analyze_module(path) -> ModuleInfo` — No function docstring.
  - Parameters: path
  - Returns: ModuleInfo
- `find_python_files(root) -> list[Path]` — No function docstring.
  - Parameters: root
  - Returns: list[Path]
- `main() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- `PROJECT_ROOT` = 'Path(__file__).resolve().parents[1]'
- `PACKAGE_PREFIXES` = ["scripts", "townlet", "townlet_ui"]
- `STD_LIB_MODULES` = ["__future__", "abc", "argparse", "asyncio", "base64", "bisect", "collections", "collections.abc", "contextlib", "copy", "dataclasses", "datetime", "decimal", "enum", "functools", "hashlib", "heapq", "itertools", "json", "logging", "math", "os", "pathlib", "random", "statistics", "textwrap", "time", "typing", "typing_extensions", "uuid", "weakref"]
- `NON_STANDARD_PREFIXES` = ["townlet", "townlet_ui", "scripts"]

### Data Flow
- Inputs: annotation, arguments, body, default, module, name, node, package_parts, path, root, tree
- Outputs: ModuleInfo, None, dict[str, set[str]], list[FunctionInfo], list[Path], list[dict[str, Any]], list[str], str, str | None, tuple[str, list[dict[str, Any]]]
- Internal interactions: —
- External interactions: ClassInfo, FunctionInfo, ModuleInfo, _format_param_entry, add, analyze_module, ast.get_docstring, ast.parse, ast.unparse, ast.walk, attributes.append, bases.append, … (42 more)

### Integration Points
- Runtime calls: ClassInfo, FunctionInfo, ModuleInfo, _format_param_entry, add, analyze_module, ast.get_docstring, ast.parse, ast.unparse, ast.walk, attributes.append, bases.append, … (42 more)

### Code Quality Notes
- Contains TODO markers.
- Missing function docstrings: unparse, _format_param_entry, build_signature, format_return, module_name_from_path, classify_import, collect_imports, gather_class_attributes, gather_constants, detect_env_usage, gather_functions, analyze_module, find_python_files, main


## tmp/render_module_docs.py

**Purpose**: Module scaffolding for render module docs.
**Dependencies**:
- Standard Library: __future__, json, pathlib, typing
- Third-Party: —
- Internal: —
**Related modules**: —

### Classes
- None defined.

### Functions
- `summarise_docstring(text, fallback) -> str` — No function docstring.
  - Parameters: text, fallback
  - Returns: str
- `format_list(values) -> str` — No function docstring.
  - Parameters: values
  - Returns: str
- `indent(text, level) -> str` — No function docstring.
  - Parameters: text, level
  - Returns: str
- `build_class_section(cls) -> str` — No function docstring.
  - Parameters: cls
  - Returns: str
- `build_function_section(fn) -> str` — No function docstring.
  - Parameters: fn
  - Returns: str
- `collect_inputs(module) -> list[str]` — No function docstring.
  - Parameters: module
  - Returns: list[str]
- `collect_outputs(module) -> list[str]` — No function docstring.
  - Parameters: module
  - Returns: list[str]
- `build_code_quality_notes(module) -> list[str]` — No function docstring.
  - Parameters: module
  - Returns: list[str]
- `main() -> None` — No function docstring.
  - Parameters: —
  - Returns: None

### Constants and Configuration
- `PROJECT_ROOT` = 'Path(__file__).resolve().parents[1]'
- `METADATA_PATH` = "PROJECT_ROOT / 'audit' / 'module_metadata.json'"
- `OUTPUT_PATH` = "PROJECT_ROOT / 'audit' / 'MODULE_DOCUMENTATION.md'"

### Data Flow
- Inputs: cls, fallback, fn, level, module, text, values
- Outputs: None, list[str], str
- Internal interactions: —
- External interactions: METADATA_PATH.read_text, OUTPUT_PATH.write_text, attr.get, build_class_section, build_code_quality_notes, build_function_section, cls.get, collect_inputs, collect_outputs, constant.get, fn.get, format_list, … (20 more)

### Integration Points
- Runtime calls: METADATA_PATH.read_text, OUTPUT_PATH.write_text, attr.get, build_class_section, build_code_quality_notes, build_function_section, cls.get, collect_inputs, collect_outputs, constant.get, fn.get, format_list, … (20 more)

### Code Quality Notes
- Contains TODO markers.
- Missing function docstrings: summarise_docstring, format_list, indent, build_class_section, build_function_section, collect_inputs, collect_outputs, build_code_quality_notes, main
