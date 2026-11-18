import collections
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest

import chess


TEST_FILE = Path(
    os.environ.get("CHESS_TESTS_FILE", Path(__file__).with_name("tests.txt"))
)
SOLVER = Path(__file__).resolve().parent / "solve.py"
if not SOLVER.exists():
    SOLVER = Path(__file__).resolve().parents[1] / "solution" / "solve.py"
PIECE_TYPES = (
    chess.PAWN,
    chess.ROOK,
    chess.KNIGHT,
    chess.BISHOP,
    chess.QUEEN,
)
TIME_LIMIT_SECONDS = 10.0


def _composition(counts):
    return [
        piece_type
        for piece_type, count in zip(PIECE_TYPES, counts)
        for _ in range(count)
    ]


def _check_fen(test_case, inventory, fen):
    test_case.assertRegex(inventory, r"^[0-9]{10}$")
    counts = [int(digit) for digit in inventory]
    white = _composition(counts[:5])
    black = _composition(counts[5:])

    board = chess.Board(fen)
    test_case.assertTrue(board.is_valid(), f"Invalid position: {fen}")
    test_case.assertEqual(board.turn, chess.BLACK)
    test_case.assertTrue(board.is_checkmate(), f"Not checkmate: {fen}")
    test_case.assertEqual(board.castling_rights, 0)
    test_case.assertIsNone(board.ep_square)

    for color, expected in ((chess.WHITE, white), (chess.BLACK, black)):
        expected_counts = collections.Counter(expected)
        expected_counts[chess.KING] += 1
        actual_counts = collections.Counter(
            piece.piece_type
            for piece in board.piece_map().values()
            if piece.color == color
        )
        test_case.assertEqual(actual_counts, expected_counts)

    for square, piece in board.piece_map().items():
        if piece.piece_type == chess.PAWN:
            test_case.assertNotIn(chess.square_rank(square), (0, 7))


class TestCheckmatePlacement(unittest.TestCase):
    def test_test_strings_are_valid_and_solvable(self):
        inputs = [
            line.strip()
            for line in TEST_FILE.read_text(encoding="ascii").splitlines()
            if line.strip()
        ]
        self.assertGreaterEqual(len(inputs), 4)
        self.assertIn("0010082221", inputs)

        start = time.monotonic()
        result = subprocess.run(
            [sys.executable, str(SOLVER)],
            input="\n".join(inputs) + "\n",
            text=True,
            capture_output=True,
            timeout=TIME_LIMIT_SECONDS,
            check=False,
        )
        elapsed = time.monotonic() - start

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertLess(elapsed, TIME_LIMIT_SECONDS)
        fens = result.stdout.splitlines()
        self.assertEqual(len(fens), len(inputs), result.stdout)
        for inventory, fen in zip(inputs, fens):
            with self.subTest(inventory=inventory):
                _check_fen(self, inventory, fen)


if __name__ == "__main__":
    unittest.main()
