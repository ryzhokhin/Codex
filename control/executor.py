"""Safety aware execution utilities for robotic arm plans."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Iterable

from .hw_interface import HardwareInterface, MovementPlan, MovementStep, SimulatedHardware

MAX_TORQUE = 2.0
MAX_SPEED = 1.5
MAX_JERK = 5.0


@dataclass(slots=True)
class ExecutionResult:
    """Summary produced after running a plan."""

    plan_name: str
    steps_executed: int
    duration_s: float
    dry_run: bool


def _validate_step(step: MovementStep) -> None:
    """Validate a single movement step against the configured limits."""

    if step.torque > MAX_TORQUE:
        raise RuntimeError(f"Safety limit exceeded: torque={step.torque:.2f} > {MAX_TORQUE:.2f}")
    if step.speed > MAX_SPEED:
        raise RuntimeError(f"Safety limit exceeded: speed={step.speed:.2f} > {MAX_SPEED:.2f}")
    if step.jerk > MAX_JERK:
        raise RuntimeError(f"Safety limit exceeded: jerk={step.jerk:.2f} > {MAX_JERK:.2f}")
    if step.duration <= 0:
        raise RuntimeError("Safety limit exceeded: duration must be positive")


async def _run_steps(
    steps: Iterable[MovementStep],
    hardware: HardwareInterface,
    dry_run: bool,
) -> int:
    """Execute all steps and return the count of executed items."""

    count = 0
    for step in steps:
        _validate_step(step)
        if dry_run:
            await asyncio.sleep(step.duration)
        else:  # pragma: no cover - real hardware usage is opt-in
            await hardware.move_to(step)
        count += 1
    return count


async def execute_move(
    plan: MovementPlan,
    *,
    dry_run: bool = True,
    hardware: HardwareInterface | None = None,
) -> ExecutionResult:
    """Run ``plan`` against ``hardware`` after validating safety limits.

    Parameters
    ----------
    plan:
        Movement plan to execute.
    dry_run:
        When ``True`` (default) the hardware is not contacted.  Instead the
        coroutine simply sleeps for the requested step duration which keeps
        tests deterministic.
    hardware:
        Optional :class:`HardwareInterface` implementation.  A
        :class:`SimulatedHardware` instance is created lazily if not provided.
    """

    if hardware is None:
        hardware = SimulatedHardware()

    start = time.perf_counter()
    executed = await _run_steps(plan, hardware, dry_run)
    duration = time.perf_counter() - start
    return ExecutionResult(
        plan_name=plan.name,
        steps_executed=executed,
        duration_s=duration,
        dry_run=dry_run,
    )
