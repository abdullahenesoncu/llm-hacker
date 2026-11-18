# Chess Checkmate Placement

Implement a standalone program in `/workspace/solution/solve.py`. It reads
one inventory string per line from standard input until EOF and writes one
FEN string per input line to standard output.

Each input is exactly ten decimal digits in this order:

```text
wPawns wRooks wKnights wBishops wQueens bPawns bRooks bKnights bBishops bQueens
```

For example, `1210030201` means White has 1 pawn, 2 rooks, 1 knight, no
bishops or queens; Black has 3 pawns, no rooks, 2 knights, no bishops, and
1 queen. Each color also has exactly one king; kings are not included in the
input string.

## Input guarantees

- Each line contains exactly ten digits, with no spaces or separators.
- Each side has at most 16 pieces including its king.
- Per side, pawn counts are 0-8, rook/knight/bishop counts are 0-2, and queen
  counts are 0-1.
- Every provided inventory has at least one valid solution.
- Piece order is not relevant; only the counts matter.

## Required output

For each input line, output one FEN string that `chess.Board(fen)` can parse
and for which:

- Black is the side to move and is in checkmate.
- `board.is_valid()` is true.
- The board contains exactly the requested number of each piece for each
  color, plus one king per color.
- No pawn is on the first or eighth rank.
- There are no castling rights or en-passant target square.

Any FEN satisfying these requirements is accepted. Do not print labels,
debugging output, or blank lines. The program must process multiple test
strings in one run. You may use Python's standard library and `python-chess`,
but no external chess engines, network services, or additional packages.

A position may be checkmate even when White has only a king and a knight:
Black's own pieces can block all of its king's escape squares. The tests
include such a crowded position, which is intentionally difficult for random
placement and evolutionary search.

## Runtime limit

The program must process the complete input stream in no more than 10 seconds.

## Example

```bash
printf '0000100000\n' | python3 /workspace/solution/solve.py
```
