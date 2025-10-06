# WP-D Phase 7 – Benchmark Runbook

This guide shows how to record and compare benchmarking results for the telemetry pipeline.

## Record a Benchmark

Writes JSON to `tmp/wp-d/benchmarks/` by default (prints the path):

```
python scripts/wp_d_benchmark.py \
  --config configs/examples/poc_hybrid.yaml \
  --ticks 500 \
  --telemetry-provider stdout \
  --notes "phase7"
```

## Compare to a Baseline

Reads two JSON files and prints/writes a text summary of deltas:

```
python scripts/wp_d_benchmark_compare.py \
  --current tmp/wp-d/benchmarks/benchmark_<id>.json \
  --baseline tmp/wp-d/benchmarks/benchmark_baseline.json \
  --out tmp/wp-d/benchmarks/compare.txt
```

## Parameter Sweep (Optional)

Generates a CSV grid to help tune queue/batch behavior. Defaults are conservative.

```
python scripts/wp_d_benchmark.py \
  --config configs/examples/poc_hybrid.yaml \
  --ticks 200 \
  --telemetry-provider stdout \
  --sweep --sweep-batch 16,32,64 --sweep-flush 1,2,4 --sweep-poll 0.25,0.5,1.0 \
  --sweep-out tmp/wp-d/benchmarks/sweep.csv
```

## Metrics Captured

- `avg_tick_seconds`
- Transport counters: `dropped_messages`, `queue_length_peak`, `worker_restart_count`,
  `bytes_flushed_total`, `payloads_flushed_total`, `send_failures_total`, `last_flush_duration_ms`.

