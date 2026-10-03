# PatchPilot — Product Requirements Document

## 1. Problem Statement

Software teams spend significant engineering cycles manually reproducing bugs reported in issues,
crafting minimal reproductions, iterating on fixes, and verifying they hold. This cycle is slow,
error-prone, and does not scale. PatchPilot automates the entire loop: given a bug report (issue
text, stack trace, or failing test), it autonomously reproduces the failure, generates a patch,
validates the patch, and iterates until the test suite is green — all locally, using open-weight
models, with no external API calls required.

---

## 2. Goals

| ID  | Goal                                                                                    |
|-----|-----------------------------------------------------------------------------------------|
| G1  | Reproduce a reported bug reliably from a natural-language description or stack trace.   |
| G2  | Generate candidate patches using a local LLM (Gemma 2, Llama 3 via Ollama or vLLM).    |
| G3  | Validate patches by executing the project's own test suite in an isolated environment.  |
| G4  | Iterate autonomously (up to a configurable max-turns limit) until tests pass.           |
| G5  | Emit a structured report: reproduction steps, root cause, final diff, validation log.   |
| G6  | Run entirely offline — zero cloud dependencies at runtime.                              |
| G7  | Keep latency acceptable on consumer-grade hardware (≥ 8 GB VRAM or CPU-only fallback). |

---

## 3. Non-Goals

- Replacing human code review for safety-critical systems.
- Automated deployment or merging of generated patches.
- Support for closed-source or remote LLM APIs (OpenAI, Anthropic, etc.) in the initial release.
- IDE plugin / GUI — CLI-first for v1.

---

## 4. Users & Personas

| Persona           | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| **Developer**     | Wants a one-command fix for a reproducible bug in their local repo.         |
| **CI Bot**        | Integrates PatchPilot into a CI pipeline to auto-triage flaky/failing PRs.  |
| **Researcher**    | Benchmarks open-weight models on real-world bug-fixing tasks (SWE-bench).   |

---

## 5. Functional Requirements

### 5.1 Input
- FR-01 Accept a bug description as free text (CLI flag `--bug`).
- FR-02 Accept a path to a failing test file (`--test-file`).
- FR-03 Accept a Git repo path (`--repo`, defaults to CWD).
- FR-04 Accept a model identifier (`--model`, e.g. `ollama:gemma2:9b`).

### 5.2 Reproduction
- FR-05 Parse the bug input to identify relevant files, symbols, and failure conditions.
- FR-06 Execute the failing test (or synthesise one) inside a sandboxed subprocess.
- FR-07 Capture stdout/stderr and exit code; confirm failure before proceeding.

### 5.3 Patch Generation
- FR-08 Build a structured prompt: bug context + relevant source snippets + task instructions.
- FR-09 Stream the LLM response and extract a unified diff from the output.
- FR-10 Apply the diff to a temporary working tree (never modifying the original branch).

### 5.4 Validation
- FR-11 Run the full test suite (or targeted tests) against the patched working tree.
- FR-12 Capture pass/fail/error counts; treat any new failure as a regression.

### 5.5 Self-Healing Loop
- FR-13 If validation fails, feed the error output back to the LLM as additional context.
- FR-14 Retry up to `max_turns` (default: 5) before declaring failure.
- FR-15 On success, emit a final unified diff relative to the original HEAD.

### 5.6 Reporting
- FR-16 Write a structured JSON report to `patchpilot_report.json`.
- FR-17 Print a human-readable summary to stdout.

---

## 6. Non-Functional Requirements

| ID    | Requirement                                                               |
|-------|---------------------------------------------------------------------------|
| NFR-01| All secrets / model paths configured via environment variables or a TOML  |
|       | config file; no hardcoded values.                                         |
| NFR-02| Type-annotated Python 3.11+; passes `mypy --strict`.                      |
| NFR-03| Linted and formatted with `ruff`; zero warnings.                          |
| NFR-04| ≥ 80 % unit-test line coverage on non-I/O modules.                        |
| NFR-05| Graceful handling of LLM timeout, malformed diff, and subprocess failure.  |
| NFR-06| Reproducible builds; pinned dependencies via `pyproject.toml`.             |

---

## 7. Success Metrics (v1)

- Resolves ≥ 40 % of SWE-bench Lite instances in ≤ 5 turns on Llama 3 8B.
- End-to-end latency < 3 min per bug on a 16 GB RAM laptop (CPU inference).
- Zero silent data-corruption failures (patch never applied to original branch).

---

## 8. Out-of-Scope for v1

- Multi-repo / monorepo spanning changes.
- Windows sandboxing (Linux/macOS only for subprocess isolation).
- Fine-tuning or LoRA adaptation of base models.
