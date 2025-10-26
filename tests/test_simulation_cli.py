"""Tests covering the CLI simulation runner."""

from __future__ import annotations

import json
from pathlib import Path

from simulation import run_case


def _collect_single_run(base: Path) -> Path:
    runs = sorted(base.iterdir())
    assert runs, "No run directories were created"
    return runs[-1]


def test_cli_generates_artifacts(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("ROBOT_RUN_BASE", str(tmp_path))
    exit_code = run_case.main(["--case", "basic_path", "--dry-run"])
    assert exit_code == 0

    run_dir = _collect_single_run(tmp_path)
    trace = run_dir / "trace.json"
    summary = run_dir / "summary.txt"
    plot = run_dir / "plot.txt"

    assert trace.exists()
    assert summary.exists()
    assert plot.exists()

    data = json.loads(trace.read_text(encoding="utf-8"))
    assert data["case"] == "basic_path"
    assert data.get("dry_run", True) is True


def test_cli_reports_safety_violation(monkeypatch, tmp_path, capsys) -> None:
    monkeypatch.setenv("ROBOT_RUN_BASE", str(tmp_path))
    exit_code = run_case.main(["--case", "safety_edge", "--dry-run"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert "Safety limit exceeded" in captured.out

    run_dir = _collect_single_run(tmp_path)
    trace = json.loads((run_dir / "trace.json").read_text(encoding="utf-8"))
    assert trace["outcome"] == "failure"
    assert "error" in trace
    summary_text = (run_dir / "summary.txt").read_text(encoding="utf-8")
    assert "Outcome: failure" in summary_text
