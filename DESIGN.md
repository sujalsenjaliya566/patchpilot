# PatchPilot — Design Document

## 1. User Experience Flow

```
$ patchpilot --repo ./myproject --bug "IndexError on empty list in process_items()" --model ollama:gemma2:9b

[PatchPilot] Analysing bug report...
[PatchPilot] Identifying failing tests...
[PatchPilot] Confirming reproduction (turn 1)...
  ✗  tests/test_processor.py::test_process_empty  FAILED
[PatchPilot] Generating patch (turn 1)...
[PatchPilot] Applying patch to temporary worktree...
[PatchPilot] Validating patch (turn 1)...
  ✓  21 passed, 0 failed
[PatchPilot] ✅ Bug resolved in 1 turn.

Patch summary:
  Modified: src/myproject/processor.py (+3 / -1)

Report written to: patchpilot_report.json
```

---

## 2. CLI Interface

```
Usage: patchpilot [OPTIONS]

Options:
  --repo        PATH    Path to the Git repository (default: .)
  --bug         TEXT    Natural-language bug description
  --test-file   PATH    Path to a failing test file (optional)
  --model       TEXT    Model identifier, e.g. ollama:gemma2:9b
  --max-turns   INT     Maximum self-healing iterations (default: 5)
  --verbose     FLAG    Enable DEBUG logging
  --config      PATH    Path to patchpilot.toml (default: ./patchpilot.toml)
  --help                Show this message and exit.
```

---

## 3. Orchestrator FSM

```
         ┌─────────────────────────────────────────────────────┐
         │                   OrchestratorAgent                  │
         │                                                       │
         │   ┌──────┐  reproduce   ┌────────────┐               │
         │   │ INIT ├─────────────►│ REPRODUCE  │               │
         │   └──────┘              └─────┬──────┘               │
         │                               │                       │
         │                    confirmed  │  not confirmed        │
         │                    failure    │  → ABORT              │
         │                               ▼                       │
         │                        ┌──────────────┐              │
         │              ┌────────►│   GENERATE   │              │
         │              │  retry  └──────┬───────┘              │
         │              │                │ patch                 │
         │              │                ▼                       │
         │              │         ┌─────────────┐               │
         │              │         │   VALIDATE  │               │
         │              │         └──────┬──────┘               │
         │              │                │                       │
         │         fail │   turn<max     │ pass                  │
         │              └────────────────┤                       │
         │                               │                       │
         │                               ▼                       │
         │                          ┌────────┐                   │
         │                          │  DONE  │                   │
         │                          └────────┘                   │
         └─────────────────────────────────────────────────────-─┘
```

States: `INIT`, `REPRODUCE`, `GENERATE`, `VALIDATE`, `DONE`, `ABORT`

Transitions:
| From       | Event                        | To         |
|------------|------------------------------|------------|
| INIT       | start()                      | REPRODUCE  |
| REPRODUCE  | failure confirmed            | GENERATE   |
| REPRODUCE  | failure not confirmed        | ABORT      |
| GENERATE   | patch extracted              | VALIDATE   |
| GENERATE   | no diff in response          | GENERATE (retry, count turn) |
| VALIDATE   | all tests pass               | DONE       |
| VALIDATE   | tests fail AND turn < max    | GENERATE   |
| VALIDATE   | tests fail AND turn == max   | ABORT      |

---

## 4. Prompt Templates

### 4.1 Initial Patch Prompt

```
You are an expert software engineer. Your task is to fix a bug in a Python codebase.

## Bug Description
{bug_description}

## Failing Test Output
```
{test_output}
```

## Relevant Source Files
{source_snippets}

## Instructions
1. Analyse the root cause.
2. Write the minimal fix as a unified diff (--- a/... +++ b/... format).
3. Output ONLY the diff block. Do not explain. Do not add prose.

## Diff
```diff
```

### 4.2 Retry Prompt (turn > 1)

```
Your previous patch did not fix the bug. The test suite still fails.

## Previous Patch
```diff
{previous_patch}
```

## New Failure Output
```
{new_test_output}
```

## Instructions
Analyse the new failure, revise your approach, and output a new unified diff.
Output ONLY the diff block.

## Diff
```diff
```

---

## 5. Diff Extraction Regex

```python
DIFF_PATTERN = re.compile(
    r"```diff\s*\n(.*?)```",
    re.DOTALL,
)
```

Fallback (no fence): match lines starting with `---` through the last `+` line.

---

## 6. Report Schema (`patchpilot_report.json`)

```json
{
  "success": true,
  "turns": 1,
  "model": "ollama:gemma2:9b",
  "bug_description": "...",
  "final_patch": "--- a/src/...\n+++ b/src/...\n...",
  "files_changed": ["src/myproject/processor.py"],
  "validation": {
    "passed": 21,
    "failed": 0,
    "errors": 0,
    "regressions": []
  },
  "turn_history": [
    {
      "turn": 1,
      "patch_applied": true,
      "validation_passed": true
    }
  ]
}
```

---

## 7. Error Taxonomy

| Code                  | Meaning                                           | Handling                            |
|-----------------------|---------------------------------------------------|-------------------------------------|
| `E_NO_REPRODUCTION`   | Bug could not be confirmed to fail                | ABORT, explain in report            |
| `E_NO_DIFF`           | LLM response contained no parseable diff          | Count turn, retry with clearer hint |
| `E_PATCH_APPLY`       | `git apply` failed on the generated diff          | Count turn, include error in retry  |
| `E_TEST_TIMEOUT`      | Test suite exceeded `test_timeout` seconds        | Count turn, truncate output         |
| `E_MAX_TURNS`         | Reached `max_turns` without passing tests         | ABORT, emit partial report          |
| `E_LLM_TIMEOUT`       | LLM adapter request exceeded `model.timeout`      | ABORT with error                    |
| `E_WORKTREE_CLEANUP`  | Temp worktree could not be removed                | Log warning, continue               |
