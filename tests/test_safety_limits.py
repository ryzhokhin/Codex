"""Safety validation tests for the executor."""

from __future__ import annotations

import asyncio
import pytest

from control.executor import MAX_TORQUE, execute_move
from control.hw_interface import MovementPlan, MovementStep


def test_execute_move_raises_on_torque_violation() -> None:
    plan = MovementPlan(
        name="unsafe",
        steps=(
            MovementStep(position=(0.0,), torque=MAX_TORQUE + 0.5, speed=1.0, jerk=1.0, duration=0.01),
        ),
    )

    async def scenario() -> None:
        with pytest.raises(RuntimeError, match="Safety limit exceeded: torque"):
            await execute_move(plan, dry_run=True)

    asyncio.run(scenario())
