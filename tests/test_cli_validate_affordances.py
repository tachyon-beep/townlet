from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = Path("scripts/validate_affordances.py").resolve()


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(SCRIPT), *args]
    return subprocess.run(cmd, text=True, capture_output=True)


def test_validate_affordances_cli_success(tmp_path: Path) -> None:
    manifest = tmp_path / "simple.yaml"
    manifest.write_text(
        """
- type: object
  id: stove_1
  object_type: stove
- id: cook_breakfast
  object_type: stove
  duration: 12
  effects:
    hunger: 0.2
"""
    )
    result = _run(str(manifest))
    assert result.returncode == 0
    assert "[ok]" in result.stdout
    assert manifest.name in result.stdout


def test_validate_affordances_cli_failure(tmp_path: Path) -> None:
    manifest = tmp_path / "invalid.yaml"
    manifest.write_text(
        """
- id: bad_affordance
  object_type: bench
  effects:
    energy: 0.1
"""
    )
    result = _run(str(manifest))
    assert result.returncode != 0
    assert "invalid" in result.stderr.lower()


def test_validate_affordances_cli_bad_precondition(tmp_path: Path) -> None:
    manifest = tmp_path / "bad_precond.yaml"
    manifest.write_text(
        """
- id: tricky
  object_type: bench
  duration: 3
  effects:
    energy: 0.1
  preconds:
    - "do_something()"
"""
    )
    result = _run(str(manifest))
    assert result.returncode != 0
    assert "precondition" in result.stderr.lower()


def test_validate_affordances_cli_directory(tmp_path: Path) -> None:
    good = tmp_path / "good.yaml"
    good.write_text(
        """
- type: object
  id: seat_1
  object_type: seat
- id: sit
  object_type: seat
  duration: 3
  effects:
    energy: 0.05
"""
    )
    subdir = tmp_path / "sub"
    subdir.mkdir()
    bad = subdir / "bad.yml"
    bad.write_text(
        """
- id: missing_effects
  object_type: seat
  duration: 3
"""
    )

    result = _run(str(tmp_path))
    assert result.returncode != 0
    assert "missing_effects" in result.stderr
