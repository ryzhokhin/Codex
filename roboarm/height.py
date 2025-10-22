"""Height adjustment subsystem."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from .hardware import Motor, Direction


@dataclass
class HeightAdjuster:
    """Controls the vertical position of the robotic arm."""

    lift_motor: Motor
    position_range: Tuple[float, float]
    current_height: float = 0.0

    def move_to(self, height: float) -> None:
        """Move the arm to an absolute height."""

        min_height, max_height = self.position_range
        clamped_height = max(min(height, max_height), min_height)
        direction = Direction.CLOCKWISE if clamped_height >= self.current_height else Direction.COUNTER_CLOCKWISE
        speed = abs(clamped_height - self.current_height)
        print(
            "[HeightAdjuster] Moving from "
            f"{self.current_height:.2f} to {clamped_height:.2f}"
        )
        self.lift_motor.set_speed(speed, direction)
        self.current_height = clamped_height

    def nudge(self, delta: float) -> None:
        """Incrementally adjust the height."""

        target = self.current_height + delta
        self.move_to(target)

    def stop(self) -> None:
        """Stop the lift motor."""

        self.lift_motor.stop()
