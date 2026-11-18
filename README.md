# llm-hacker

Custom [Harbor](https://github.com/laude-institute/harbor) tasks for evaluating coding agents.

| Task | Summary |
|---|---|
| [chess-checkmate-placement](chess-checkmate-placement/) | Build legal checkmate FENs from piece-count strings with python-chess. |
| [openscad-box-designer](openscad-box-designer/) | Write an OpenSCAD script for a storage box with a captured two-station hinge. |
| [python-data-manipulation](python-data-manipulation/) | Implement a persistent segment tree with a numba merge callback (C++/pybind11). |

Each task directory contains `instruction.md`, `task.toml`, `environment/`, `solution/` and `tests/`.

## Setup

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# put model API keys in .env
```

## Running

```bash
harbor run -p <task-dir> --agent oracle   # reference solution, expected reward 1
harbor run -p <task-dir> --agent nop      # no-op agent, expected reward 0
harbor run -p <task-dir> --agent <agent> --model <model>
```

Run results are written to `jobs/` (git-ignored).
