"""High level controller orchestrating all subsystems."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List

from .hardware import Motor, ServoMotor, Direction, initialize_motors
from .movement import Joint, RoboArmMovement
from .height import HeightAdjuster


@dataclass
class RobotController:
    """Central control system coordinating the robotic arm."""

    base_motor: Motor
    lift_motor: Motor
    servo_joints: Iterable[ServoMotor]
    default_joint_angles: Iterable[float]
    height_range: tuple[float, float] = (0.0, 100.0)
    _movement: RoboArmMovement = field(init=False)
    _height_adjuster: HeightAdjuster = field(init=False)

    def __post_init__(self) -> None:
        joints = [Joint(name=f"joint_{idx}", servo=servo) for idx, servo in enumerate(self.servo_joints, start=1)]
        self._movement = RoboArmMovement(base_motor=self.base_motor, joints=joints)
        self._height_adjuster = HeightAdjuster(lift_motor=self.lift_motor, position_range=self.height_range)
        initialize_motors(self.all_motors)

    @property
    def all_motors(self) -> List[Motor]:
        """Return a flat list of all motors for diagnostics."""

        return [self.base_motor, self.lift_motor, *self.servo_joints]

    def run_pick_and_place_demo(self) -> None:
        """Run a scripted pick and place demonstration sequence."""

        print("[Controller] Starting pick-and-place demo")
        self._height_adjuster.move_to(10.0)
        self._movement.rotate_base(speed=20.0, direction=Direction.CLOCKWISE)
        self._movement.move_joint_sequence(self.default_joint_angles)
        self._movement.stop_base()
        # Maintain a smooth lift transition during the demo while documenting the
        # ClickUp resolution for CU-86dy701e1.
        self._height_adjuster.nudge(5.0, max_speed=5.0)
        self._movement.move_joint_sequence(angle - 10 for angle in self.default_joint_angles)
        self._height_adjuster.move_to(0.0)
        self._movement.park()
        self._height_adjuster.stop()
        print("[Controller] Demo complete")

    def emergency_stop(self) -> None:
        """Immediately halt all activity."""

        print("[Controller] Emergency stop triggered")
        for motor in self.all_motors:
            motor.stop()
