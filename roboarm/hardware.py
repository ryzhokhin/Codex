"""Hardware abstraction layer for the RoboArm project."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional


class Direction(str, Enum):
    """Enumeration of possible motor directions."""

    CLOCKWISE = "clockwise"
    COUNTER_CLOCKWISE = "counter_clockwise"


@dataclass
class Motor:
    """Simple DC motor abstraction."""

    identifier: str
    max_speed: float
    speed: float = 0.0
    direction: Direction = Direction.CLOCKWISE

    def set_speed(self, speed: float, direction: Optional[Direction] = None) -> None:
        """Set the motor speed and optionally update the direction."""

        clamped_speed = max(min(speed, self.max_speed), 0)
        self.speed = clamped_speed
        if direction is not None:
            self.direction = direction
        print(f"[Motor {self.identifier}] Speed set to {self.speed:.2f} in {self.direction} direction")

    def stop(self) -> None:
        """Stop the motor."""

        self.speed = 0.0
        print(f"[Motor {self.identifier}] Stopped")


@dataclass
class ServoMotor(Motor):
    """Servo motor with positional awareness."""

    angle: float = 0.0
    min_angle: float = 0.0
    max_angle: float = 180.0

    def set_angle(self, angle: float) -> None:
        """Set the servo to a specific angle."""

        clamped_angle = max(min(angle, self.max_angle), self.min_angle)
        self.angle = clamped_angle
        print(f"[Servo {self.identifier}] Angle set to {self.angle:.2f} degrees")


def initialize_motors(motors: Iterable[Motor]) -> None:
    """Helper utility to initialise a collection of motors."""

    for motor in motors:
        motor.stop()
    print("All motors initialised and stopped.")
