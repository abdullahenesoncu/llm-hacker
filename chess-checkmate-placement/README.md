# aeo/chess-checkmate-placement

A Python-only Harbor task: read ten-digit piece-count strings from stdin and
write legal FENs in which Black is checkmated. The agent gets `python-chess`;
the solution may not rely on the unrelated C++ chess-library source in this
repository.

## Layout

```text
chess-checkmate-placement/
├── instruction.md       # task shown to the agent
├── task.toml            # Harbor configuration
├── environment/         # agent image: starter solve.py and python-chess only
├── solution/            # oracle implementation
└── tests/               # verifier-only image, hard inputs, and Harbor runner
```

Each test string has one implicit king per side, with the other pieces
specified by count. The verifier parses every emitted FEN with python-chess
and checks legality, checkmate, exact piece counts, pawn placement, output
shape, and a runtime limit. A key hard case has only a white king and knight
against a full black inventory; the black pieces themselves constrain the
king's escapes.

The verifier reads all cases from `tests/tests.txt`, runs the candidate once
with the complete input, and enforces a 10-second global time limit. The
current reference batch completes in about 6.7 seconds in the verifier image.

The agent and verifier use separate containers. The agent Dockerfile does not
copy the test directory; `tests/Dockerfile` builds the verifier image with the
test files and dependencies.

## Local checks

```bash
python3 -m pip install python-chess pytest
cd chess-checkmate-placement/solution
CHESS_TESTS_FILE=../tests/tests.txt python3 -m pytest ../tests/test_outputs.py -q
```
