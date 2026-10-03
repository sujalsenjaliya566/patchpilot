# PatchPilot — Engineering Rules

These rules are non-negotiable and apply to every change in this repository.
Violations block merge.

---

## R01 — Test-Driven Development

- Write tests **before or alongside** production code. Never ship a feature without a test.
- Every new public function/class must have at least one positive-path and one negative-path test.
- Use `pytest` exclusively. No `unittest.TestCase` unless inheriting from a framework that requires it.

## R02 — Static Analysis Must Stay Green

Run the following suite before every commit and on every CI push:

```bash
ruff check src tests
ruff format --check src tests
mypy --strict src
pytest --tb=short -q
```

All four commands must exit `0`. A red check blocks the branch.

## R03 — No `# type: ignore` Without Justification

If `mypy` cannot be satisfied without a `# type: ignore`, add an inline comment explaining why:

```python
result = external_lib.call()  # type: ignore[no-any-return]  # third-party stub incomplete
```

Blanket `# type: ignore` with no reason is a merge-blocking violation.

## R04 — No Hardcoded Secrets or Paths

- Model URLs, API base addresses, file paths: config file or environment variable only.
- Use `patchpilot.config.Settings` as the single source of truth.
- `grep`-ing for `localhost` in source (outside tests/config) triggers a review flag.

## R05 — Patch Safety

- The `Validator` **must** apply patches to a temporary Git worktree, never to the user's working tree.
- The worktree must be cleaned up in a `finally` block or context manager, even on exception.
- The original branch HEAD must be identical before and after a PatchPilot run.

## R06 — Subprocess Timeout

- Every `subprocess.run` / `subprocess.Popen` call must specify `timeout=`.
- Default timeout for test runs: `Settings.agent.test_timeout` (default 120 s).
- Catch `subprocess.TimeoutExpired` and surface it as a structured error, not a crash.

## R07 — LLM Response Validation

- Never `eval()` or `exec()` LLM output.
- Diff extraction must use a dedicated regex/parser; raw output must not touch the filesystem.
- If no valid diff is found in the LLM response, log a warning and count the turn as failed.

## R08 — Logging Over Print

- Use `logging.getLogger(__name__)` in all modules.
- `print()` is allowed **only** in `cli.py` for user-facing output.
- Log level is driven by `Settings.output.verbose` (DEBUG when true, WARNING otherwise).

## R09 — Immutable Data Models

- `BugReport`, `ReproductionResult`, `Patch`, `ValidationResult`, `ContextWindow` are frozen
  dataclasses (`@dataclass(frozen=True)` where feasible).
- Mutable state lives only in `AgentState` inside `OrchestratorAgent`.

## R10 — Commit Discipline

- Every commit must pass R02 in full.
- Commit messages: `<type>(<scope>): <subject>` — e.g. `feat(generator): extract diff parser`.
- Types: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`.
- No WIP commits on `main`.

## R11 — Coverage Floor

- Line coverage on `src/patchpilot` must not drop below **80 %**.
- Measure with `pytest --cov=src/patchpilot --cov-fail-under=80`.
- I/O-heavy modules (`cli.py`, `reproducer.py`, `validator.py`) may use `# pragma: no cover`
  on specific subprocess-invoke lines with a comment justification.

## R12 — Dependency Hygiene

- Add dependencies to `pyproject.toml` only; no bare `pip install` in scripts.
- Pin minimum versions, not exact versions, to allow security patches.
- Dev dependencies go in `[project.optional-dependencies] dev = [...]`.
- Review `pip-audit` output before any release.
