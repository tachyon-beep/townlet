from __future__ import annotations

import json
import time
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from townlet.config import load_config
from townlet.core.sim_loop import SimulationLoop


@dataclass
class BenchmarkResult:
    timestamp: str
    config_path: str
    config_id: str
    providers: dict[str, str]
    ticks: int
    avg_tick_seconds: float
    transport: dict[str, Any]
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "timestamp": self.timestamp,
            "config_path": self.config_path,
            "config_id": self.config_id,
            "providers": dict(self.providers),
            "ticks": int(self.ticks),
            "avg_tick_seconds": float(self.avg_tick_seconds),
            "transport": dict(self.transport),
        }
        if self.notes:
            payload["notes"] = self.notes
        return payload


def _set_nested_attr(root: Any, path: str, value: Any) -> None:
    parts = [p for p in path.split(".") if p]
    if not parts:
        return
    target = root
    for name in parts[:-1]:
        target = getattr(target, name)
    setattr(target, parts[-1], value)


def run_benchmark(
    *,
    config_path: Path,
    ticks: int = 500,
    telemetry_provider: str | None = None,
    notes: str | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> BenchmarkResult:
    if ticks <= 0:
        raise ValueError("ticks must be positive")
    config = load_config(config_path)
    # Apply limited overrides for sweep tuning if provided
    if overrides:
        for key, val in overrides.items():
            try:
                _set_nested_attr(config, str(key), val)
            except Exception:
                # Best-effort; ignore invalid override keys
                pass
    loop = SimulationLoop(config, telemetry_provider=telemetry_provider or None)
    start = time.perf_counter()
    loop.run_for(ticks)
    elapsed = time.perf_counter() - start
    avg_tick = elapsed / ticks
    transport = loop.telemetry.latest_transport_status()
    ts = datetime.now(UTC).isoformat()
    providers = loop.provider_info
    result = BenchmarkResult(
        timestamp=ts,
        config_path=str(config_path),
        config_id=config.config_id,
        providers=providers,
        ticks=ticks,
        avg_tick_seconds=avg_tick,
        transport=dict(transport),
        notes=notes,
    )
    # Ensure clean shutdown of telemetry
    close = getattr(loop.telemetry, "close", None)
    if callable(close):
        try:
            close()
        except Exception:
            pass
    return result


def write_benchmark_result(result: BenchmarkResult, out_path: Path | None = None) -> Path:
    payload = result.to_dict()
    target = out_path
    if target is None:
        root = Path("tmp/wp-d/benchmarks").resolve()
        root.mkdir(parents=True, exist_ok=True)
        name = f"benchmark_{result.config_id}_{int(time.time())}.json"
        target = root / name
    else:
        target = Path(out_path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True))
    return target


def load_benchmark(path: Path) -> dict[str, Any]:
    resolved = Path(path).expanduser().resolve()
    return json.loads(resolved.read_text())


def compare_benchmarks(
    current: Mapping[str, Any], baseline: Mapping[str, Any]
) -> dict[str, Any]:
    def _get(mapping: Mapping[str, Any], key: str, default: float = 0.0) -> float:
        value = mapping.get(key, default)
        try:
            return float(value) if value is not None else float(default)
        except Exception:
            return float(default)

    curr_avg = _get(current, "avg_tick_seconds")
    base_avg = _get(baseline, "avg_tick_seconds")
    curr_tx = dict(current.get("transport", {}))
    base_tx = dict(baseline.get("transport", {}))
    fields = [
        "dropped_messages",
        "queue_length_peak",
        "worker_restart_count",
        "bytes_flushed_total",
        "payloads_flushed_total",
        "send_failures_total",
    ]
    deltas: dict[str, Any] = {
        "avg_tick_seconds_delta": curr_avg - base_avg,
        "avg_tick_seconds": curr_avg,
        "avg_tick_seconds_baseline": base_avg,
    }
    for name in fields:
        deltas[name] = curr_tx.get(name, 0)
        deltas[f"{name}_baseline"] = base_tx.get(name, 0)
        try:
            deltas[f"{name}_delta"] = float(curr_tx.get(name, 0)) - float(base_tx.get(name, 0))
        except Exception:
            deltas[f"{name}_delta"] = 0.0
    return deltas
