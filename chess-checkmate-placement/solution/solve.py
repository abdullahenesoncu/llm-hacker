import random
import sys

import chess


_PIECE_TYPES = (
    chess.PAWN,
    chess.ROOK,
    chess.KNIGHT,
    chess.BISHOP,
    chess.QUEEN,
)
_MAX_COUNTS = (8, 2, 2, 2, 1)


def _parse_inventory(line):
    if len(line) != 10 or not line.isascii() or not line.isdigit():
        raise ValueError(f"Expected exactly ten digits, got {line!r}")

    counts = [int(digit) for digit in line]
    for color_counts in (counts[:5], counts[5:]):
        if any(count > limit for count, limit in zip(color_counts, _MAX_COUNTS)):
            raise ValueError("Piece count exceeds the standard chess inventory")
        if sum(color_counts) + 1 > 16:
            raise ValueError("A side cannot have more than 16 pieces")

    white = [chess.KING] + [
        piece_type
        for piece_type, count in zip(_PIECE_TYPES, counts[:5])
        for _ in range(count)
    ]
    black = [chess.KING] + [
        piece_type
        for piece_type, count in zip(_PIECE_TYPES, counts[5:])
        for _ in range(count)
    ]
    return white, black


def _remove_piece(composition, piece_type):
    remaining = list(composition)
    remaining.remove(piece_type)
    return remaining


def _template_board(white, black):
    board = chess.Board(None)
    white_remaining = _remove_piece(white, chess.KING)
    black_remaining = _remove_piece(black, chess.KING)

    if chess.QUEEN in white_remaining:
        white_remaining.remove(chess.QUEEN)
        board.set_piece_at(chess.A8, chess.Piece(chess.KING, chess.BLACK))
        board.set_piece_at(chess.B7, chess.Piece(chess.QUEEN, chess.WHITE))
        board.set_piece_at(chess.C6, chess.Piece(chess.KING, chess.WHITE))
    elif (
        chess.KNIGHT in white_remaining
        and black_remaining.count(chess.ROOK) >= 2
        and black_remaining.count(chess.BISHOP) >= 2
        and chess.KNIGHT in black_remaining
    ):
        white_remaining.remove(chess.KNIGHT)
        for piece_type, square in (
            (chess.BISHOP, chess.D8),
            (chess.ROOK, chess.D7),
            (chess.ROOK, chess.E7),
            (chess.BISHOP, chess.F8),
            (chess.KNIGHT, chess.F7),
        ):
            board.set_piece_at(square, chess.Piece(piece_type, chess.BLACK))
            black_remaining.remove(piece_type)
        board.set_piece_at(chess.E8, chess.Piece(chess.KING, chess.BLACK))
        board.set_piece_at(chess.F6, chess.Piece(chess.KNIGHT, chess.WHITE))
        board.set_piece_at(chess.C6, chess.Piece(chess.KING, chess.WHITE))
    else:
        return None

    board.turn = chess.BLACK
    remaining = [(chess.WHITE, piece_type) for piece_type in white_remaining]
    remaining.extend((chess.BLACK, piece_type) for piece_type in black_remaining)
    remaining.sort(key=lambda item: (item[1] == chess.PAWN, -item[1]))
    if not board.is_valid() or not board.is_checkmate():
        return None
    return board, remaining


def _place_remaining(board, remaining, seed):
    rng = random.Random(seed)
    for color, piece_type in remaining:
        squares = list(chess.SQUARES)
        rng.shuffle(squares)
        for square in squares:
            if board.piece_at(square):
                continue
            if piece_type == chess.PAWN and chess.square_rank(square) in (0, 7):
                continue

            board.set_piece_at(square, chess.Piece(piece_type, color))
            if board.is_valid() and board.is_checkmate():
                break
            board.remove_piece_at(square)
        else:
            return None
    return board


def _random_construction(white, black, seed, attempts=20000):
    pieces = (
        [(chess.WHITE, piece_type) for piece_type in white]
        + [(chess.BLACK, piece_type) for piece_type in black]
    )
    rng = random.Random(seed)
    for _ in range(attempts):
        board = chess.Board(None)
        board.turn = chess.BLACK
        squares = list(chess.SQUARES)
        rng.shuffle(squares)
        rng.shuffle(pieces)
        for color, piece_type in pieces:
            for index, square in enumerate(squares):
                if piece_type != chess.PAWN or chess.square_rank(square) not in (0, 7):
                    board.set_piece_at(square, chess.Piece(piece_type, color))
                    squares.pop(index)
                    break
        if board.is_valid() and board.is_checkmate():
            return board
    return None


def _construct_fen(white, black):
    template = _template_board(white, black)
    if template is not None:
        base_board, remaining = template
        for seed in range(32):
            board = _place_remaining(base_board.copy(), remaining, seed)
            if board is not None:
                return board.fen(en_passant="fen")

    for seed in range(8):
        board = _random_construction(white, black, seed)
        if board is not None:
            return board.fen(en_passant="fen")
    raise RuntimeError("Could not construct a checkmate for the supplied inventory")


def main():
    output = []
    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        white, black = _parse_inventory(line)
        output.append(_construct_fen(white, black))
    if output:
        sys.stdout.write("\n".join(output) + "\n")


if __name__ == "__main__":
    main()
