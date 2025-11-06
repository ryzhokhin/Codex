"""Entry point for running the RoboArm demonstration."""
# Task CU-86dyaq7ha: Added documentation and verified functionality
# Task CU-86dyb4rjd: Testing automatic things with the automated prompt
from __future__ import annotations

from roboarm import Motor, ServoMotor, RobotController


def create_controller() -> RobotController:
    """Factory helper to build a demo RobotController instance."""

    base_motor = Motor(identifier="base", max_speed=50.0)
    lift_motor = Motor(identifier="lift", max_speed=30.0)
    servo_joints = [
        ServoMotor(identifier="shoulder", max_speed=120.0, max_angle=180.0),
        ServoMotor(identifier="elbow", max_speed=120.0, max_angle=160.0),
        ServoMotor(identifier="wrist", max_speed=120.0, max_angle=140.0),
    ]
    default_angles = [45.0, 90.0, 30.0]
    return RobotController(
        base_motor=base_motor,
        lift_motor=lift_motor,
        servo_joints=servo_joints,
        default_joint_angles=default_angles,
        height_range=(0.0, 50.0),
    )


def main() -> None:
    controller = create_controller()
    controller.run_pick_and_place_demo()


if __name__ == "__main__":
    main()
