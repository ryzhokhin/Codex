"""Trajectory planning stubs used by the FSM and simulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from control.hw_interface import MovementPlan, MovementStep


@dataclass(slots=True)
class PlanningConfig:
    """Configuration for the very small demo planner."""

    default_speed: float = 1.0
    default_torque: float = 1.0
    default_jerk: float = 3.0
    step_duration: float = 0.05


class SimplePlanner:
    """Generate a straight-line plan in normalized joint space."""

    def __init__(self, config: PlanningConfig | None = None) -> None:
        self.config = config or PlanningConfig()

    def plan(self, target_pose: Sequence[float], *, name: str = "user-plan") -> MovementPlan:
        """Produce a :class:`MovementPlan` for ``target_pose``.

        The implementation creates three interpolation steps between the origin
        and the requested pose.  The values are deterministic to keep unit tests
        reproducible.
        """

        pose = tuple(float(value) for value in target_pose)
        steps = tuple(self._generate_steps(pose))
        return MovementPlan(name=name, steps=steps)

    def _generate_steps(self, pose: tuple[float, ...]) -> Iterable[MovementStep]:
        fraction = (1 / 3, 2 / 3, 1.0)
        for part in fraction:
            position = tuple(component * part for component in pose)
            yield MovementStep(
                position=position,
                torque=self.config.default_torque,
                speed=self.config.default_speed,
                jerk=self.config.default_jerk,
                duration=self.config.step_duration,
            )
