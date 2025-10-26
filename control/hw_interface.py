"""Hardware abstraction layer for robotic arm control."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class MovementStep:
    """A single movement step produced by the planner.

    The executor uses the metadata in each step to validate safety limits before
    attempting to run it.  Values are expressed in normalized units so the
    module stays hardware agnostic.
    """

    position: tuple[float, ...]
    torque: float
    speed: float
    jerk: float
    duration: float = 0.1


@dataclass(frozen=True)
class MovementPlan:
    """Container for a complete motion plan."""

    name: str
    steps: tuple[MovementStep, ...]

    def __iter__(self) -> Iterator[MovementStep]:
        return iter(self.steps)


class HardwareInterface(ABC):
    """Abstract interface that isolates real hardware access.

    Implementations should translate normalized movement steps into concrete
    device commands.  Tests and CI use a lightweight stub implementation.
    """

    @abstractmethod
    async def move_to(self, step: MovementStep) -> None:
        """Apply a single movement step.

        Implementations must raise ``RuntimeError`` if the motion cannot be
        carried out safely.  The coroutine should be cooperative and avoid
        blocking the event loop for extended periods of time.
        """


class SimulatedHardware(HardwareInterface):
    """Default simulation-friendly hardware stub used in CI.

    The implementation simply records the last requested pose.  Real hardware
    drivers can subclass :class:`HardwareInterface` in a different project
    without modifying the executor.
    """

    def __init__(self) -> None:
        self.last_pose: tuple[float, ...] | None = None

    async def move_to(self, step: MovementStep) -> None:  # pragma: no cover -
        """Record the pose for debugging purposes."""

        self.last_pose = step.position
