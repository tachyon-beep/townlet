import importlib.util
import sys
from pathlib import Path

import pytest

from townlet.policy.models import torch_available

spec = importlib.util.spec_from_file_location(
    "run_anneal_rehearsal",
    Path(__file__).resolve().parent.parent / "scripts" / "run_anneal_rehearsal.py",
)
assert spec and spec.loader
run_anneal_rehearsal = importlib.util.module_from_spec(spec)
sys.modules["run_anneal_rehearsal"] = run_anneal_rehearsal
spec.loader.exec_module(run_anneal_rehearsal)  # type: ignore[arg-type]

evaluate_summary = run_anneal_rehearsal.evaluate_summary
run_rehearsal = run_anneal_rehearsal.run_rehearsal


@pytest.mark.skipif(not torch_available(), reason="Torch not installed")
def test_run_anneal_rehearsal_pass(tmp_path: Path) -> None:
    config = Path("artifacts/m5/acceptance/config_idle_v1.yaml")
    manifest = Path("data/bc_datasets/manifests/idle_v1.json")
    log_dir = tmp_path / "logs"
    summary = run_rehearsal(config, manifest, log_dir)
    final = evaluate_summary(summary)
    assert final["status"] == "PASS"
    assert final["bc_passed"]
    assert not final["loss_flag"]
    assert not final["queue_flag"]
    assert not final["intensity_flag"]
