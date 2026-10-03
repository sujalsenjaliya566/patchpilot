# PatchPilot — Memory & State Log

This file records the evolution of the project: decisions made, problems encountered, resolutions
applied, and the current state of the system. Updated at the end of every significant work session.

---

## Entry 0001 — Bootstrap

**Date:** initial  
**Phase:** 0 — Bootstrap  
**Status:** in-progress

### What was done
- Wrote 6 specification files to workspace root:
  - `PRD.md` — product requirements, goals, functional/non-functional requirements, success metrics.
  - `ARCHITECTURE.md` — component diagram, data models, config schema, directory layout.
  - `RULES.md` — 12 non-negotiable engineering rules (TDD, static analysis, patch safety, etc.).
  - `TASKS.md` — phased task tracker (Phase 0–10).
  - `MEMORY.md` — this file.
  - `DESIGN.md` — UX/interaction design, prompt templates, FSM state diagram.

### Decisions made
| Decision | Rationale |
|---|---|
| Python 3.11+ | `tomllib` in stdlib, improved typing (PEP 654, PEP 673). |
| Typer for CLI | Clean, type-annotated, minimal boilerplate. |
| Ruff over flake8+isort | Single tool, faster, modern. |
| Dataclasses (not Pydantic) | Zero extra runtime dependency for data containers. |
| Temp Git worktree | Safest way to test patches without touching the user's work. |
| Ollama + vLLM adapters | Both are standard local inference runtimes for open-weight models. |

### Open questions
- Should `Reproducer` synthesise a test when none is provided, or require `--test-file`?
  → Decision deferred to Phase 3 implementation. Synthesise is preferred for UX.
- Coverage threshold: 80 % is the floor. Can likely reach 85 %+ with mocked subprocess tests.

### Next actions
1. Scaffold project directory structure.
2. Write `pyproject.toml`.
3. Begin Phase 1 (models + config).

---

## Entry 0002 — Full Implementation

**Date:** bootstrap → complete
**Phase:** 1–10
**Status:** complete

### What was done
- `src/patchpilot/models.py` — frozen dataclasses: `BugReport`, `ReproductionResult`, `Patch`, `ValidationResult`, `ContextWindow`, `AgentReport`, `TurnRecord`.
- `src/patchpilot/config.py` — `Settings` (TOML + env overlay), `ModelSettings`, `AgentSettings`, `OutputSettings`.
- `src/patchpilot/llm/base.py` — `BaseLLMAdapter` ABC.
- `src/patchpilot/llm/ollama.py` — `OllamaAdapter` (POST `/api/generate`).
- `src/patchpilot/llm/vllm.py` — `VLLMAdapter` (POST `/v1/chat/completions`).
- `src/patchpilot/llm/factory.py` — `make_adapter` factory.
- `src/patchpilot/reproducer.py` — `Reproducer` (subprocess with timeout).
- `src/patchpilot/generator.py` — `PatchGenerator` + `extract_diff` + `_changed_files`.
- `src/patchpilot/validator.py` — `Validator` (temp git worktree, apply diff, run tests, parse output).
- `src/patchpilot/agent/orchestrator.py` — `OrchestratorAgent` FSM (`INIT → REPRODUCE → GENERATE → VALIDATE → DONE|ABORT`).
- `src/patchpilot/cli.py` — Typer CLI entry point.
- 62 tests across 6 test modules; 60 passed, 2 skipped (git not on PATH in this env).
- All of: `ruff check` ✅ · `ruff format --check` ✅ · `mypy --strict` ✅ · `pytest --cov 86.62%` ✅

### Decisions made
| Decision | Rationale |
|---|---|
| `default=str` in `json.dumps` | Avoids recursive `asdict` in serialiser; `Path` and other non-JSON-native types render as strings. |
| `shutil.which("git")` in conftest | Makes tests portable on Windows where `git` may not be in PATH. |
| Annotated + module-level type aliases for Typer args | Avoids B008 (function call in default) while keeping type safety. |
| ANN401 satisfied by using `object` instead of `Any` | Strict ruff ANN rule; `json.dumps(default=str)` made the `Any` annotation unnecessary. |

### Final state
- 14 source files, 0 mypy errors, 0 ruff warnings.
- 86.62% line coverage (floor: 80%).
- Low-coverage modules: `validator.py` (52% — subprocess I/O), `generator.py` (77% — source-reading path).

---

## Entry template (copy for future entries)

```
## Entry NNNN — <Title>

**Date:** <date>
**Phase:** <phase>
**Status:** <in-progress | complete | blocked>

### What was done

### Decisions made

### Problems encountered & resolutions

### Next actions
```
