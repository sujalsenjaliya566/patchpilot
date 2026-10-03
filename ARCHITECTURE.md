# PatchPilot — Architecture

## 1. High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI Entry Point                          │
│                   patchpilot.cli  (Typer)                       │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                 ┌──────────▼──────────┐
                 │   OrchestratorAgent  │
                 │  (closed-loop FSM)   │
                 └──┬──────┬──────┬────┘
                    │      │      │
          ┌─────────▼─┐  ┌─▼──────▼──────┐  ┌──────────────┐
          │  Reproducer│  │ PatchGenerator │  │  Validator   │
          │  (harness) │  │  (LLM + diff) │  │ (test runner)│
          └─────────┬──┘  └───────┬───────┘  └──────┬───────┘
                    │             │                  │
                    └─────────────▼──────────────────┘
                              Shared Context
                         (ContextWindow dataclass)
                                    │
                    ┌───────────────▼──────────────┐
                    │       LLM Adapter Layer       │
                    │  OllamaAdapter | vLLMAdapter  │
                    └───────────────────────────────┘
```

---

## 2. Component Responsibilities

### 2.1 CLI (`patchpilot.cli`)
- Parse user arguments with **Typer**.
- Load config (TOML → env vars → CLI flags, in ascending priority).
- Instantiate and run `OrchestratorAgent`.
- Pretty-print the final report.

### 2.2 OrchestratorAgent (`patchpilot.agent.orchestrator`)
- Implements a finite-state machine (FSM):
  ```
  INIT → REPRODUCE → GENERATE → VALIDATE → [DONE | ITERATE → GENERATE]
  ```
- Holds the mutable `AgentState` (turn count, context window, patch history).
- Enforces `max_turns` limit; raises `MaxTurnsExceeded` on overflow.
- Writes `patchpilot_report.json` on exit (success or failure).

### 2.3 Reproducer (`patchpilot.reproducer`)
- Identifies the failing test(s) from the bug description or explicit `--test-file`.
- Runs the test suite in a **subprocess** with a clean environment.
- Returns a `ReproductionResult` (stdout, stderr, exit_code, confirmed_failure: bool).

### 2.4 PatchGenerator (`patchpilot.generator`)
- Constructs a structured prompt from `ContextWindow`.
- Calls the LLM adapter with streaming.
- Extracts a unified diff via regex from the raw response.
- Returns a `Patch` (raw_diff, hunks, files_changed).

### 2.5 Validator (`patchpilot.validator`)
- Applies the `Patch` to a **temporary Git worktree** (never the working tree).
- Runs the test suite against the patched worktree.
- Returns `ValidationResult` (passed, failed, errors, regressions).
- Cleans up the temporary worktree on exit.

### 2.6 LLM Adapter Layer (`patchpilot.llm`)
- Abstract base: `BaseLLMAdapter` with `generate(prompt, config) → str`.
- `OllamaAdapter`: calls Ollama REST API (`/api/generate`).
- `vLLMAdapter`: calls vLLM OpenAI-compatible API (`/v1/chat/completions`).
- Model identifier format: `<runtime>:<model-tag>` — e.g. `ollama:gemma2:9b`.

---

## 3. Data Models (`patchpilot.models`)

```python
@dataclass
class BugReport:
    description: str
    test_file: Path | None
    repo_path: Path

@dataclass
class ReproductionResult:
    stdout: str
    stderr: str
    exit_code: int
    confirmed_failure: bool

@dataclass
class Patch:
    raw_diff: str
    files_changed: list[str]
    turn: int

@dataclass
class ValidationResult:
    passed: int
    failed: int
    errors: int
    regressions: list[str]
    success: bool

@dataclass
class ContextWindow:
    bug_report: BugReport
    reproduction: ReproductionResult | None
    patches: list[Patch]
    validations: list[ValidationResult]

@dataclass
class AgentReport:
    success: bool
    turns: int
    final_patch: Patch | None
    validation: ValidationResult | None
    context: ContextWindow
```

---

## 4. Configuration (`patchpilot.config`)

Priority order (highest wins): CLI flags > Environment variables > `patchpilot.toml` > defaults.

```toml
[model]
provider = "ollama"          # "ollama" | "vllm"
name     = "gemma2:9b"
base_url = "http://localhost:11434"
timeout  = 120               # seconds

[agent]
max_turns      = 5
sandbox        = true        # use temp git worktree for patching
test_command   = "pytest"
test_args      = ["-x", "--tb=short"]

[output]
report_path = "patchpilot_report.json"
verbose     = false
```

---

## 5. Directory Layout

```
patchpilot/
├── pyproject.toml
├── patchpilot.toml.example
├── PRD.md
├── ARCHITECTURE.md
├── RULES.md
├── TASKS.md
├── MEMORY.md
├── DESIGN.md
├── src/
│   └── patchpilot/
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       ├── models.py
│       ├── agent/
│       │   ├── __init__.py
│       │   └── orchestrator.py
│       ├── llm/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── ollama.py
│       │   └── vllm.py
│       ├── reproducer.py
│       ├── generator.py
│       └── validator.py
└── tests/
    ├── conftest.py
    ├── test_models.py
    ├── test_config.py
    ├── test_reproducer.py
    ├── test_generator.py
    ├── test_validator.py
    ├── test_orchestrator.py
    └── test_llm_adapters.py
```

---

## 6. Key Design Decisions

| Decision | Rationale |
|---|---|
| Temp Git worktree for patching | Prevents corruption of user's working tree; trivially reversible. |
| FSM for orchestration | Explicit states make turn-counting, logging, and testing straightforward. |
| Adapter pattern for LLMs | Swappable backends without touching agent logic. |
| `dataclass` over Pydantic | Zero extra dependency for pure data containers; Pydantic added only if validation overhead is justified. |
| Typer for CLI | Minimal, type-annotated, good auto-help generation. |
| ruff + mypy --strict | Enforces correctness at every commit; no `# type: ignore` allowed without justification. |
