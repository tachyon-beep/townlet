from __future__ import annotations

from pathlib import Path

from townlet.benchmark.utils import compare_benchmarks, run_benchmark, write_benchmark_result


def test_run_and_write_benchmark(tmp_path: Path) -> None:
    result = run_benchmark(config_path=Path("configs/examples/poc_hybrid.yaml"), ticks=5, telemetry_provider="stdout", notes="test")
    assert result.avg_tick_seconds > 0
    assert result.ticks == 5
    assert "queue_length" in result.transport
    out = write_benchmark_result(result, tmp_path / "bench.json")
    assert out.exists()


def test_compare_benchmarks_zero_delta(tmp_path: Path) -> None:
    # Use a tiny run to generate a current + baseline pair
    result = run_benchmark(config_path=Path("configs/examples/poc_hybrid.yaml"), ticks=5, telemetry_provider="stdout")
    current = result.to_dict()
    baseline = result.to_dict()
    deltas = compare_benchmarks(current, baseline)
    assert deltas["avg_tick_seconds_delta"] == 0.0
    assert deltas["dropped_messages_delta"] == 0.0

