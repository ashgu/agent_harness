# agent-harness

A small agent harness for chatting with an Ollama model and calling local tools.

## Quick start

```bash
# 1. Create/sync the environment (creates .venv, installs any dependencies)
uv sync

# 2. Run from the project root
uv run main.py --task "Reply with exactly: PONG"
```

> **Note:** Always run with `uv run` (or `python3 main.py`) **from the project root**.
> `harness/` and `examples/` are local packages that live in this repo — they are
> *not* installed, and Python finds them because they sit next to `main.py`.
> Running the script from another directory will raise `ModuleNotFoundError`.
> There are no third-party dependencies, so nothing appears in `uv.lock` beyond
> the Python interpreter itself.

## Project layout

```
main.py            # CLI entry point (Stage 2 tool loop; --task / --model)
harness/           # core harness: config, Ollama client, tool registry
examples/          # sample tools (weather, time, temp compare)
step0_check_env.sh # environment sanity check
```

## Configuration

`harness.config.Config` reads settings from environment variables (see
`Config.from_env`). You can override the model on the CLI with `--model`.

> The active entry point is `main()` (Stage 2, the tool loop), which accepts
> `--task` and `--model`. The `--say` flag lives in the unused `step1()` helper.

## Using uv

| Task | Command |
|------|---------|
| Create/sync env | `uv sync` |
| Run the app | `uv run main.py --task "..."` |
| Add a dependency | `uv add <package>` |
| Remove a dependency | `uv remove <package>` |
| Pin Python version | `uv python pin 3.12` |
