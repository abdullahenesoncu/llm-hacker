"""Outline of the behaviors checked by the verifier; not a runnable test."""


def test_stdin_lines_produce_fens():
    """Each ten-digit inventory line read from stdin produces exactly one FEN line."""
    raise NotImplementedError


def test_piece_counts_and_legal_mate():
    """Every FEN is valid checkmate and matches the inventory on its input line."""
    raise NotImplementedError


def test_dense_inventory_finishes_quickly():
    """A white king and knight can mate a full black inventory within the runtime limit."""
    raise NotImplementedError
