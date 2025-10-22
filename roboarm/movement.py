"""Movement algorithms for the RoboArm."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .hardware import Motor, ServoMotor, Direction


@dataclass
class Joint:
    """A single joint composed of a servo motor."""

    name: str
    servo: ServoMotor

    def move_to(self, angle: float) -> None:
        """Move the joint to the target angle."""

        print(f"[Joint {self.name}] Moving to {angle} degrees")
        self.servo.set_angle(angle)


@dataclass
class RoboArmMovement:
    """High level movement control for the robotic arm."""

    base_motor: Motor
    joints: Iterable[Joint]

    def rotate_base(self, speed: float, direction: Direction) -> None:
        """Rotate the base of the arm."""

        print(f"[RoboArm] Rotating base {direction} at speed {speed}")
        self.base_motor.set_speed(speed, direction)

    def stop_base(self) -> None:
        """Stop the base rotation."""

        self.base_motor.stop()

    def move_joint_sequence(self, angles: Iterable[float]) -> None:
        """Move all joints through a sequence of angles."""

        for joint, angle in zip(self.joints, angles):
            joint.move_to(angle)

    def park(self) -> None:
        """Park the arm by resetting joints and stopping base motor."""

        print("[RoboArm] Parking arm")
        for joint in self.joints:
            joint.move_to(0.0)
        self.stop_base()
