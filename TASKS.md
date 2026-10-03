# PatchPilot — Task Tracker

Legend: `[ ]` pending · `[-]` in-progress · `[x]` complete

---

## Phase 0 — Bootstrap

- [x] Write specification files (PRD.md, ARCHITECTURE.md, RULES.md, TASKS.md, MEMORY.md, DESIGN.md)
- [x] Scaffold project directory structure
- [x] Write `pyproject.toml` with ruff, mypy, pytest config
- [x] Create `patchpilot.toml.example`

## Phase 1 — Data Models & Config

- [x] Implement `patchpilot.models` (frozen dataclasses)
- [x] Implement `patchpilot.config` (TOML + env var loading, Settings object)
- [x] Write `tests/test_models.py`
- [x] Write `tests/test_config.py`

## Phase 2 — LLM Adapter Layer

- [x] Implement `patchpilot.llm.base.BaseLLMAdapter`
- [x] Implement `patchpilot.llm.ollama.OllamaAdapter`
- [x] Implement `patchpilot.llm.vllm.VLLMAdapter`
- [x] Implement `patchpilot.llm.factory.make_adapter`
- [x] Write `tests/test_llm_adapters.py` (mock HTTP with respx)

## Phase 3 — Reproducer

- [x] Implement `patchpilot.reproducer.Reproducer`
- [x] Write `tests/test_reproducer.py`

## Phase 4 — Patch Generator

- [x] Implement `patchpilot.generator.PatchGenerator`
- [x] Implement diff extraction regex/parser (`extract_diff`, `_changed_files`)
- [x] Write `tests/test_generator.py`

## Phase 5 — Validator

- [x] Implement `patchpilot.validator.Validator` (temp worktree, apply diff, run tests)
- [x] Write `tests/test_validator.py`

## Phase 6 — Orchestrator Agent

- [x] Implement `patchpilot.agent.orchestrator.OrchestratorAgent` (FSM)
- [x] Implement `AgentState`, `MaxTurnsExceeded`, `ReproductionFailed`
- [x] Write `tests/test_orchestrator.py`

## Phase 7 — CLI

- [x] Implement `patchpilot.cli` (Typer, argument parsing, config wiring)
- [x] Smoke-test: `patchpilot --help`

## Phase 8 — Reporting

- [x] Implement JSON report writer (`AgentReport → patchpilot_report.json`)
- [x] Implement human-readable stdout summary

## Phase 9 — Validation & QA ✅

- [x] Run `ruff check` — 0 warnings
- [x] Run `ruff format --check` — 0 diff
- [x] Run `mypy --strict` — 0 errors
- [x] Run `pytest --cov=src/patchpilot --cov-fail-under=80` — 86.62% coverage, 60 passed

## Phase 10 — Documentation

- [x] Write `README.md` with quick-start
- [x] Update `MEMORY.md` with final state

---

_Last updated: implementation complete_
