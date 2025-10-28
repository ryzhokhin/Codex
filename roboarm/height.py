"""Height adjustment subsystem."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Tuple

from .hardware import Direction, Motor


@dataclass
class HeightAdjuster:
    """Controls the vertical position of the robotic arm."""

    lift_motor: Motor
    position_range: Tuple[float, float]
    current_height: float = 0.0
    ramp_threshold: float = 8.0
    min_effective_speed: float = 0.25
    target_height: float = field(init=False)

    def __post_init__(self) -> None:
        min_height, max_height = self.position_range
        clamped_height = max(min(self.current_height, max_height), min_height)
        if clamped_height != self.current_height:
            print(
                "[HeightAdjuster] Initial height clamped",
                f"from {self.current_height:.2f} to {clamped_height:.2f}"
            )
            self.current_height = clamped_height
        self.target_height = self.current_height

    def move_to(self, height: float, *, max_speed: float | None = None) -> None:
        """Move the arm to an absolute height using a motion profile."""

        plan = self._plan_motion(height, max_speed=max_speed)
        self._execute_motion_plan(plan)

    def move_by(self, delta: float, *, max_speed: float | None = None) -> None:
        """Move the arm by a relative amount."""

        desired_height = self.target_height + delta
        self.move_to(desired_height, max_speed=max_speed)

    def nudge(self, delta: float, *, max_speed: float | None = None) -> None:
        """Convenience helper for small relative adjustments.

        Parameters
        ----------
        delta:
            The relative distance to travel. Positive values raise the arm while
            negative values lower it.
        max_speed:
            Optional override that lets callers cap the motor speed used for the
            adjustment. When omitted the adjuster will select a gentle default
            derived from ``min_effective_speed`` so nudges stay smooth.
        """

        if delta == 0:
            print("[HeightAdjuster] Nudge of zero requested; no action taken")
            return

        if max_speed is None:
            # Apply a soft cap that keeps nudges from running at full speed while
            # still respecting the minimum effective speed so the motor moves.
            default_speed = max(self.min_effective_speed * 1.5, self.min_effective_speed)
            max_speed = min(default_speed, self.lift_motor.max_speed)

        self.move_by(delta, max_speed=max_speed)

    def calibrate(self, reference_height: float, new_range: Tuple[float, float]) -> None:
        """Recalibrate the current height and soft limits."""

        min_height, max_height = new_range
        if min_height > max_height:
            raise ValueError("Minimum height cannot exceed maximum height")

        clamped_reference = max(min(reference_height, max_height), min_height)
        print(
            "[HeightAdjuster] Calibrated",
            f"reference set to {clamped_reference:.2f} within range {new_range}"
        )
        self.position_range = new_range
        self.current_height = clamped_reference
        self.target_height = clamped_reference
        self.hold_position()

    def hold_position(self) -> None:
        """Stop the motor and hold the current target height."""

        self.lift_motor.stop()
        self.target_height = self.current_height

    def stop(self) -> None:
        """Alias for hold_position to match controller expectations."""

        self.hold_position()

    def emergency_stop(self) -> None:
        """Immediately stop any motion and reset the target."""

        print("[HeightAdjuster] Emergency stop triggered")
        self.lift_motor.stop()
        self.target_height = self.current_height

    def get_status(self) -> dict:
        """Return a snapshot of the adjuster's current state."""

        return {
            "current_height": self.current_height,
            "target_height": self.target_height,
            "position_range": self.position_range,
            "motor_speed": self.lift_motor.speed,
            "motor_direction": self.lift_motor.direction,
        }

    def _plan_motion(self, height: float, *, max_speed: float | None = None) -> List[Tuple[str, Direction, float]]:
        """Create a list of motion segments to reach the requested height."""

        min_height, max_height = self.position_range
        clamped_height = max(min(height, max_height), min_height)
        distance = clamped_height - self.current_height
        if distance == 0:
            print("[HeightAdjuster] Already at target height")
            return []

        allowed_speed = self.lift_motor.max_speed if max_speed is None else min(max_speed, self.lift_motor.max_speed)
        travel_distance = abs(distance)
        direction = Direction.CLOCKWISE if distance > 0 else Direction.COUNTER_CLOCKWISE
        ramp_distance = min(self.ramp_threshold, travel_distance / 2)
        cruise_distance = max(travel_distance - (2 * ramp_distance), 0.0)

        ramp_speed = max(allowed_speed * 0.6, self.min_effective_speed)
        cruise_speed = max(allowed_speed, self.min_effective_speed)

        plan: List[Tuple[str, Direction, float]] = []
        if ramp_distance > 0:
            plan.append(("accelerate", direction, ramp_speed))
        if cruise_distance > 0:
            plan.append(("cruise", direction, cruise_speed))
        if ramp_distance > 0:
            plan.append(("decelerate", direction, self.min_effective_speed))

        print(
            "[HeightAdjuster] Planned motion",
            f"from {self.current_height:.2f} to {clamped_height:.2f}"
        )
        self.target_height = clamped_height
        return plan

    def _execute_motion_plan(self, plan: Iterable[Tuple[str, Direction, float]]) -> None:
        """Execute the motion plan and ensure the lift holds position on completion."""

        if not plan:
            return

        for phase, direction, speed in plan:
            print(
                f"[HeightAdjuster] Phase: {phase}",
                f"speed {speed:.2f} in {direction}"
            )
            self.lift_motor.set_speed(speed, direction)

        self.current_height = self.target_height
        self.hold_position()

