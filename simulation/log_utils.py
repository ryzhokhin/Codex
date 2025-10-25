"""Utility helpers for producing simulation artifacts."""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

RUN_BASE_ENV = "ROBOT_RUN_BASE"


def _base_runs_dir() -> Path:
    root = os.getenv(RUN_BASE_ENV)
    if root:
        return Path(root)
    return Path.cwd() / "runs"


def create_run_directory(case_name: str) -> Path:
    """Return the directory that should contain run artifacts."""

    timestamp = datetime.now(tz=None).strftime("%Y%m%d-%H%M%S")
    directory = _base_runs_dir() / f"{timestamp}-{case_name}"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def write_summary(directory: Path, *, limits: dict[str, float], outcome: str) -> Path:
    """Write a human-readable summary and return the path."""

    summary = directory / "summary.txt"
    lines = ["Simulation Summary", "===================", f"Outcome: {outcome}", "", "Limits:"]
    for key, value in limits.items():
        lines.append(f"- {key}: {value}")
    summary.write_text("\n".join(lines), encoding="utf-8")
    return summary


def write_trace(directory: Path, trace: dict[str, Any]) -> Path:
    """Write the structured trace to ``trace.json``."""

    path = directory / "trace.json"
    path.write_text(json.dumps(trace, indent=2), encoding="utf-8")
    return path


def write_plot_placeholder(directory: Path) -> Path:
    """Create a placeholder artifact representing a generated plot."""

    path = directory / "plot.txt"
    path.write_text("Plot placeholder - attach real visualization here.", encoding="utf-8")
    return path
