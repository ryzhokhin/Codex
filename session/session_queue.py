"""Priority-based movement request queue."""

from __future__ import annotations

import asyncio
import itertools
from dataclasses import dataclass
from typing import Any

_PRIORITY = {"safety": 0, "user": 1, "background": 2}


@dataclass(slots=True)
class SessionRequest:
    """Container for queued movement requests."""

    category: str
    target_pose: tuple[float, ...]
    dry_run: bool
    name: str
    future: asyncio.Future[Any]

    def set_result(self, result: Any) -> None:
        if not self.future.done():
            self.future.set_result(result)

    def set_exception(self, exc: BaseException) -> None:
        if not self.future.done():
            self.future.set_exception(exc)


class SessionQueue:
    """Simple priority queue with deterministic ordering."""

    def __init__(self) -> None:
        self._items: list[tuple[int, int, SessionRequest]] = []
        self._counter = itertools.count()

    def add_request(
        self,
        *,
        category: str,
        target_pose: tuple[float, ...],
        dry_run: bool,
        name: str,
    ) -> SessionRequest:
        if category not in _PRIORITY:
            raise ValueError(f"Unknown session category: {category}")
        loop = asyncio.get_running_loop()
        request = SessionRequest(
            category=category,
            target_pose=target_pose,
            dry_run=dry_run,
            name=name,
            future=loop.create_future(),
        )
        item = (_PRIORITY[category], next(self._counter), request)
        self._items.append(item)
        self._items.sort(key=lambda entry: (entry[0], entry[1]))
        return request

    def pop_next(self) -> SessionRequest | None:
        if not self._items:
            return None
        _, _, request = self._items.pop(0)
        return request

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._items)

    def __bool__(self) -> bool:  # pragma: no cover - trivial
        return bool(self._items)
