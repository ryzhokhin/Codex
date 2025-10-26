"""Entry point for running robotic arm simulations."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Sequence

from control.executor import MAX_JERK, MAX_SPEED, MAX_TORQUE, ExecutionResult, execute_move
from planner.planning import PlanningConfig, SimplePlanner
from simulation import log_utils

_CASES: dict[str, tuple[float, ...]] = {
    "basic_path": (0.4, 0.1, 0.0),
    "safety_edge": (1.0, 0.0, 0.2),
}


async def _execute_case(case: str, *, dry_run: bool) -> tuple[ExecutionResult | None, str, Exception | None, str]:
    config = PlanningConfig()
    if case == "safety_edge":
        config = PlanningConfig(default_torque=2.5)
    planner = SimplePlanner(config)
    target = _CASES.get(case)
    if target is None:
        raise ValueError(f"Unknown simulation case: {case}")

    plan = planner.plan(target, name=f"plan-{case}")
    outcome = "success"
    error: Exception | None = None
    result: ExecutionResult | None = None
    try:
        result = await execute_move(plan, dry_run=dry_run)
    except RuntimeError as exc:
        outcome = "failure"
        error = exc
    return result, outcome, error, plan.name


def _build_trace(result: ExecutionResult | None, *, outcome: str, error: Exception | None, case: str) -> dict[str, object]:
    data: dict[str, object] = {
        "case": case,
        "outcome": outcome,
        "limits": {"max_torque": MAX_TORQUE, "max_speed": MAX_SPEED, "max_jerk": MAX_JERK},
    }
    if result:
        data.update(
            {
                "plan": result.plan_name,
                "steps": result.steps_executed,
                "duration": result.duration_s,
                "dry_run": result.dry_run,
            }
        )
    if error:
        data["error"] = str(error)
    return data


def _write_artifacts(directory: Path, trace: dict[str, object], outcome: str) -> None:
    log_utils.write_trace(directory, trace)
    log_utils.write_summary(
        directory,
        limits={"MAX_TORQUE": MAX_TORQUE, "MAX_SPEED": MAX_SPEED, "MAX_JERK": MAX_JERK},
        outcome=outcome,
    )
    log_utils.write_plot_placeholder(directory)


async def _async_main(case: str, *, dry_run: bool) -> int:
    result, outcome, error, plan_name = await _execute_case(case, dry_run=dry_run)
    directory = log_utils.create_run_directory(case)
    trace = _build_trace(result, outcome=outcome, error=error, case=case)
    trace["plan_name"] = plan_name
    _write_artifacts(directory, trace, outcome)
    if error:
        raise error
    return 0


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a simulated robotic arm movement.")
    parser.add_argument("--case", default="basic_path", help="Scenario to execute.")
    parser.add_argument("--dry-run", action="store_true", help="Skip hardware calls (default).")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        return asyncio.run(_async_main(args.case, dry_run=args.dry_run))
    except RuntimeError as exc:
        print(exc)
        return 1
    except Exception as exc:  # pragma: no cover - CLI guardrail
        print(f"Unexpected failure: {exc}")
        return 2


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
