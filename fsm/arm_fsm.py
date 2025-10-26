"""Async finite-state machine coordinating movement requests."""

from __future__ import annotations

import asyncio
from typing import Sequence

from control.executor import ExecutionResult, execute_move
from control.hw_interface import MovementPlan
from planner.planning import SimplePlanner
from session.session_queue import SessionQueue, SessionRequest


class ArmFSM:
    """Cooperative FSM that serializes arm movements via an ``asyncio.Lock``."""

    def __init__(self, planner: SimplePlanner | None = None) -> None:
        self._planner = planner or SimplePlanner()
        self._queue = SessionQueue()
        self._lock = asyncio.Lock()
        self._state = "idle"
        self._worker_task: asyncio.Task[None] | None = None
        self._current_request: SessionRequest | None = None

    def get_state(self) -> str:
        """Return the current FSM state."""

        return self._state

    async def request_move(
        self,
        target_pose: Sequence[float],
        *,
        category: str = "user",
        dry_run: bool = True,
        name: str = "user-request",
        timeout: float = 5.0,
    ) -> ExecutionResult:
        """Queue a movement request and wait for its completion."""

        pose = tuple(float(value) for value in target_pose)
        request = self._queue.add_request(
            category=category,
            target_pose=pose,
            dry_run=dry_run,
            name=name,
        )
        await self._ensure_worker()
        return await asyncio.wait_for(request.future, timeout=timeout)

    async def tick(self) -> None:
        """Advance the internal worker coroutine.

        ``request_move`` automatically schedules the worker, but tests can call
        ``tick`` to cooperatively advance the event loop and observe state
        changes.
        """

        await asyncio.sleep(0)

    async def _ensure_worker(self) -> None:
        if self._worker_task is not None and self._worker_task.done():
            self._worker_task = None
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._worker())
        await asyncio.sleep(0)

    async def _worker(self) -> None:
        while True:
            if self._current_request is None:
                request = self._queue.pop_next()
                if request is None:
                    self._state = "idle"
                    break
                self._current_request = request

            request = self._current_request
            try:
                async with self._lock:
                    self._state = "plan"
                    plan = self._planner.plan(request.target_pose, name=request.name)
                    self._state = "move"
                    result = await execute_move(plan, dry_run=request.dry_run)
                    self._state = "verify"
                    await self._verify(plan)
                    self._state = "log"
                    await self._log(plan, result)
                request.set_result(result)
            except Exception as exc:  # pragma: no cover - defensive
                request.set_exception(exc)
            finally:
                self._current_request = None
        self._worker_task = None

    async def _verify(self, _plan: MovementPlan) -> None:
        """Placeholder verification step that yields control."""

        await asyncio.sleep(0)

    async def _log(self, _plan: MovementPlan, _result: ExecutionResult) -> None:
        """Placeholder logging step for the FSM."""

        await asyncio.sleep(0)
