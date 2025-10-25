"""Tests ensuring the FSM serializes movements."""

from __future__ import annotations

import asyncio
import pytest

from fsm import arm_fsm
from fsm.arm_fsm import ArmFSM


def test_fsm_prevents_concurrent_moves(monkeypatch: pytest.MonkeyPatch) -> None:
    async def scenario() -> None:
        fsm = ArmFSM()
        order: list[str] = []
        running: set[str] = set()

        original_execute = arm_fsm.execute_move

        async def wrapped_execute(*args, **kwargs):
            plan = args[0]
            order.append(plan.name)
            running.add(plan.name)
            assert len(running) == 1
            try:
                return await original_execute(*args, **kwargs)
            finally:
                running.remove(plan.name)

        monkeypatch.setattr(arm_fsm, "execute_move", wrapped_execute)

        first = asyncio.create_task(fsm.request_move((0.5,), name="first"))
        await asyncio.sleep(0.02)
        second = asyncio.create_task(fsm.request_move((0.5,), name="second"))

        await asyncio.sleep(0.06)
        assert order == ["first"]
        assert not second.done()

        first_result = await first
        second_result = await second

        assert first_result.plan_name == "first"
        assert second_result.plan_name == "second"
        assert order == ["first", "second"]

    asyncio.run(scenario())
