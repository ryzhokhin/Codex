# Robot Test Project

![Tests](https://github.com/your-org/robot-test/actions/workflows/tests.yml/badge.svg)
![Manual Simulation](https://github.com/your-org/robot-test/actions/workflows/manual_sim.yml/badge.svg)

A Python 3.13 playground for validating robotic arm motion logic.  Everything
runs in simulation so GitHub Actions can exercise the code without talking to
real hardware.

## Quickstart

1. Create a Python 3.13 virtual environment.
2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Run the quality gate locally:
   ```bash
   ruff check .
   mypy .
   pytest -q
   ```
4. Execute a simulated move:
   ```bash
   python -m simulation.run_case --case basic_path --dry-run
   ```

## Workflows

- **tests.yml** – Runs ruff, mypy, and pytest on pushes to `main` and `dev` as
  well as every pull request.
- **manual_sim.yml** – Exposes a "Run Simulation" button under the Actions tab.
  Select a `test_case` (defaults to `basic_path`) and toggle `dry_run` if you
  ever hook in real hardware.  Concurrency is enforced via
  `group: robot-session`, so manual sessions never overlap.
- **safety_gate.yml** – Runs automatically on pull requests.  It executes the
  `safety_edge` scenario which intentionally violates torque limits.  Any
  regression that weakens safety checks leaves the workflow red and blocks the
  merge.
- **release.yml** – Optional helper to bundle the most recent `runs/` artifacts
  into a GitHub Release.  Trigger it via workflow dispatch once you are happy
  with the results.

All simulation workflows upload the generated `runs/<timestamp>-<case>` folder
as an artifact (named `robot-run-<case>`).  Download it from the job summary to
inspect `trace.json`, `summary.txt`, and the plot placeholder.

> ℹ️ Screenshot placeholder: capture the Actions run summary and paste the image
> here after the first successful pipeline execution to help future teammates
> find the artifacts quickly.

## Architecture Overview

```
control/
  hw_interface.py   # abstract, simulation-friendly hardware layer
  executor.py       # enforces safety limits before executing a plan
planner/
  planning.py       # straight-line trajectory stub
fsm/
  arm_fsm.py        # asyncio FSM with session locking and priority queue
session/
  session_queue.py  # safety > user > background queueing rules
simulation/
  run_case.py       # CLI entry point used by workflows
  log_utils.py      # helpers for run artifacts under ./runs/
docs/
  state_diagram.md  # Mermaid diagram of the state machine
```

The finite-state machine acquires an `asyncio.Lock` for each move to guarantee
exclusive control of the simulated arm.  Safety limits live in
`control/executor.py` and raise `RuntimeError` when violated.  The CLI returns a
non-zero exit code in that case which propagates to GitHub Actions as a failed
check.

## Collaboration Guidelines

- Pull requests must pass `tests.yml` and `safety_gate.yml`.  Configure them as
  required checks in the repository settings.
- Use the provided issue templates when reporting bugs or requesting features.
- Secrets such as `MY_ROBOT_TOKEN` should only be added via the repository
  settings.  Never commit real credentials; locally you can export the variable
  before invoking workflows.
- Reviewers listed in `CODEOWNERS` must approve changes touching the critical
  control and FSM modules.

## How to Reproduce

1. Clone the repository.
2. Follow the Quickstart steps above.
3. Trigger `manual_sim.yml` from the GitHub Actions tab to produce downloadable
   run artifacts.
4. Inspect `runs/` locally or in the downloaded artifact bundle to verify the
   summary and JSON trace.

## Further Reading

- [`docs/state_diagram.md`](docs/state_diagram.md) explains the idle → plan →
  move → verify → log loop with a Mermaid diagram.
- Tests under `tests/` showcase the locking behaviour, safety gates, and
  artifact generation end-to-end.
