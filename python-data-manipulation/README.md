# aeo/python-data-manipulation

Harbor task: implement a persistent (version-keeping) segment tree behind a fixed Python interface, with a user-supplied numba merge function.

## Overview

The agent receives a package in `/workspace/solution` containing a stub `solver_class.py`, a minimal `setup.py` and an outline of the tests. Items are NumPy arrays (primitive or structured/record dtype) and the merge function is a numba `cfunc` `merge(left, right, out)` on item pointers. It must implement `Solver` (`update`, `query`, `version_count`, `size`) so that any version can be updated or queried online, and so that the performance limits in `instruction.md` are met.

## Structure

```text
python-data-manipulation/
├── instruction.md        # task description shown to the agent
├── task.toml             # task config and metadata
├── environment/
│   ├── Dockerfile        # python:3.11-slim + g++, numpy, numba, pybind11, pytest
│   ├── __init__.py       # exports Solver
│   ├── solver_class.py   # stub to implement
│   ├── setup.py          # minimal package setup
│   └── test_example.py   # outline of what the tests check (not runnable)
├── solution/             # oracle only, never copied into the environment
│   ├── solve.sh
│   ├── solver_class.py
│   ├── setup.py, pyproject.toml
│   └── cpp/              # C++17 persistent segment tree + pybind11 bindings
└── tests/
    ├── test.sh           # builds the solution and runs the tests, writes the reward
    └── test_outputs.py   # verifier tests
```

## Difficulty

The algorithm is standard, but the merge function is a numba `cfunc` operating on pointers to raw items (primitives or records). The agent must handle 500k operations on 200k items in 3 s and support the callback ABI in a package that installs with `pip install -e .`.

## Oracle solution

`solution/solve.sh` copies a C++17 persistent segment tree (`cpp/`, exposed as `_solver` through pybind11) and a thin NumPy-based Python `Solver` wrapper into `/workspace/solution`. The merge function is called through its cfunc address.

## Verification

`tests/test.sh` copies `tests/test_outputs.py` into `/workspace/solution`, runs `pip install -e .` and then pytest. The reward is 1 if everything passes and 0 otherwise. The tests cover:

- **Versioning:** initial state, new version ids, old versions unchanged.
- **Correctness:** all ranges on small sizes, random online updates and queries against brute force, sum/max/keep-left merges, a non-commutative polynomial-hash record merge, float min, return types, error types and input copying.
- **Performance:** N=200,000 with 500,000 operations: build + operations (interleaved updates and queries, or queries only) in under 3 s, and peak memory under 1 GB.

## Running

```bash
harbor run -p python-data-manipulation --agent oracle   # expected reward 1
harbor run -p python-data-manipulation --agent nop      # expected reward 0
```

## TODO before submission

Fill `author_name`, `author_email`, `author_organization` and `relevant_experience` in `task.toml`.
