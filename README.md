# RoboArm Demo Project

This repository contains a small Python project that simulates the control logic for a robotic arm. The goal is to showcase how different subsystems—motor control, arm movement, and height adjustment—can be composed into a cohesive application.

## Project Structure

```
.
├── main.py              # Entry point for running the scripted demo
└── roboarm
    ├── __init__.py      # Convenience exports for the package
    ├── controller.py    # High level orchestration logic
    ├── hardware.py      # Hardware abstraction of motors and servos
    ├── height.py        # Height adjustment subsystem
    └── movement.py      # Arm movement and joint coordination
```

## Getting Started

1. Ensure you have Python 3.10 or later installed.
2. Install any dependencies (none are required beyond the standard library).
3. Run the demo script:

```bash
python main.py
```

The script prints a sequence of actions that represent a pick-and-place routine for the robotic arm. This project is designed for testing and demonstration purposes only; no actual hardware is controlled.
