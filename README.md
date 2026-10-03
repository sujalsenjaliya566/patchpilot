# PatchPilot

Autonomous closed-loop bug reproduction and self-healing agent using local open-weight LLMs.

## Quick Start

```bash
pip install -e ".[dev]"
patchpilot --repo ./myproject --bug "IndexError on empty list" --model ollama:gemma2:9b
```

## Configuration

Copy `patchpilot.toml.example` to `patchpilot.toml` and adjust settings.

## Requirements

- Python 3.11+
- [Ollama](https://ollama.com/) or [vLLM](https://github.com/vllm-project/vllm) running locally
- Git
