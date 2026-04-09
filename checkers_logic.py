from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional


Player = Literal[1, 2]
Color = Player

ROWS: int = 8
COLS: int = 8
WHITE_PLAYER: Player = 1
BLACK_PLAYER: Player = 2

INITIAL_PIECE_ROWS: int = 3
MOVE_STEP: int = 1
JUMP_STEP: int = 2

WHITE_DIRECTION: int = -1
BLACK_DIRECTION: int = 1
SIDES: tuple[int, int] = (-1, 1)

MEN_CAN_CAPTURE_BACKWARDS: bool = True
FLYING_KINGS: bool = True


@dataclass(frozen=True, slots=True)
class Coords:
    r: int
    c: int


@dataclass(frozen=True, slots=True)
class Piece:
    id: int
    color: Color
    is_king: bool = False


@dataclass(frozen=True, slots=True)
class Move:
    type: Literal["simple", "capture"]
    from_: Coords
    to: Coords
    captured: Optional[Coords] = None


Board = list[list[Optional[Piece]]]


def is_inside(r: int, c: int) -> bool:
    return 0 <= r < ROWS and 0 <= c < COLS


def get_piece(board: Board, r: int, c: int) -> Optional[Piece]:
    if not is_inside(r, c):
        return None
    return board[r][c]


def create_initial_board() -> tuple[Board, int]:
    board: Board = [[None for _ in range(COLS)] for _ in range(ROWS)]
    next_id = 1

    for r in range(ROWS):
        for c in range(COLS):
            if (r + c) % 2 != 1:
                continue

            if r < INITIAL_PIECE_ROWS:
                board[r][c] = Piece(id=next_id, color=BLACK_PLAYER, is_king=False)
                next_id += 1
            elif r >= ROWS - INITIAL_PIECE_ROWS:
                board[r][c] = Piece(id=next_id, color=WHITE_PLAYER, is_king=False)
                next_id += 1

    return board, next_id


def get_quiet_moves_for_piece(board: Board, turn: Color, from_: Coords) -> list[Move]:
    piece = get_piece(board, from_.r, from_.c)
    if piece is None or piece.color != turn:
        return []

    moves: list[Move] = []

    if piece.is_king and FLYING_KINGS:
        diagonals = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        for dr, dc in diagonals:
            r = from_.r + dr
            c = from_.c + dc
            while is_inside(r, c) and get_piece(board, r, c) is None:
                moves.append(Move(type="simple", from_=from_, to=Coords(r, c)))
                r += dr
                c += dc
        return moves

    if piece.is_king:
        directions = (WHITE_DIRECTION, BLACK_DIRECTION)
    else:
        directions = (WHITE_DIRECTION,) if piece.color == WHITE_PLAYER else (BLACK_DIRECTION,)

    for dir_ in directions:
        for side in SIDES:
            to = Coords(from_.r + dir_ * MOVE_STEP, from_.c + side)
            if is_inside(to.r, to.c) and get_piece(board, to.r, to.c) is None:
                moves.append(Move(type="simple", from_=from_, to=to))

    return moves


def get_captures_for_piece(board: Board, turn: Color, from_: Coords) -> list[Move]:
    piece = get_piece(board, from_.r, from_.c)
    if piece is None or piece.color != turn:
        return []

    captures: list[Move] = []

    if piece.is_king and FLYING_KINGS:
        diagonals = ((-1, -1), (-1, 1), (1, -1), (1, 1))

        for dr, dc in diagonals:
            r = from_.r + dr
            c = from_.c + dc

            while is_inside(r, c) and get_piece(board, r, c) is None:
                r += dr
                c += dc

            if not is_inside(r, c):
                continue

            target = get_piece(board, r, c)
            if target is None or target.color == piece.color:
                continue

            land_r = r + dr
            land_c = c + dc
            while is_inside(land_r, land_c) and get_piece(board, land_r, land_c) is None:
                captures.append(
                    Move(
                        type="capture",
                        from_=from_,
                        to=Coords(land_r, land_c),
                        captured=Coords(r, c),
                    )
                )
                land_r += dr
                land_c += dc

        return captures

    if piece.is_king:
        directions = (WHITE_DIRECTION, BLACK_DIRECTION)
    elif MEN_CAN_CAPTURE_BACKWARDS:
        directions = (WHITE_DIRECTION, BLACK_DIRECTION)
    else:
        directions = (WHITE_DIRECTION,) if piece.color == WHITE_PLAYER else (BLACK_DIRECTION,)

    for dir_ in directions:
        for side in SIDES:
            mid = Coords(from_.r + dir_ * MOVE_STEP, from_.c + side)
            to = Coords(from_.r + dir_ * JUMP_STEP, from_.c + side * JUMP_STEP)

            if not is_inside(to.r, to.c):
                continue
            if get_piece(board, to.r, to.c) is not None:
                continue

            middle_piece = get_piece(board, mid.r, mid.c)
            if middle_piece is not None and middle_piece.color != piece.color:
                captures.append(Move(type="capture", from_=from_, to=to, captured=mid))

    return captures


def get_valid_moves_for_piece(board: Board, turn: Color, from_: Coords, *, captures_only: bool = False) -> list[Move]:
    piece = get_piece(board, from_.r, from_.c)
    if piece is None or piece.color != turn:
        return []

    captures = get_captures_for_piece(board, turn, from_)
    if captures_only:
        return captures

    quiet = get_quiet_moves_for_piece(board, turn, from_)
    return [*captures, *quiet]


def apply_move(board: Board, move: Move) -> Board:
    next_b = [row[:] for row in board]

    piece = get_piece(next_b, move.from_.r, move.from_.c)
    if piece is None:
        return next_b

    next_b[move.from_.r][move.from_.c] = None
    next_b[move.to.r][move.to.c] = piece

    if move.type == "capture" and move.captured is not None:
        next_b[move.captured.r][move.captured.c] = None

    placed = next_b[move.to.r][move.to.c]
    if placed is not None and not placed.is_king:
        if placed.color == WHITE_PLAYER and move.to.r == 0:
            next_b[move.to.r][move.to.c] = Piece(id=placed.id, color=placed.color, is_king=True)
        elif placed.color == BLACK_PLAYER and move.to.r == ROWS - 1:
            next_b[move.to.r][move.to.c] = Piece(id=placed.id, color=placed.color, is_king=True)

    return next_b


def get_winner_by_board(board: Board, turn: Color) -> Optional[Color]:
    white_count = 0
    black_count = 0

    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if p is None:
                continue
            if p.color == WHITE_PLAYER:
                white_count += 1
            else:
                black_count += 1

    if white_count == 0 and black_count == 0:
        return None
    if white_count == 0:
        return BLACK_PLAYER
    if black_count == 0:
        return WHITE_PLAYER

    for r in range(ROWS):
        for c in range(COLS):
            p = board[r][c]
            if p is None or p.color != turn:
                continue
            from_ = Coords(r, c)
            if get_captures_for_piece(board, turn, from_) or get_quiet_moves_for_piece(board, turn, from_):
                return None

    return BLACK_PLAYER if turn == WHITE_PLAYER else WHITE_PLAYER


def format_board(board: Board) -> str:
    header = "   " + " ".join(chr(ord("a") + c) for c in range(COLS))
    lines = [header]

    for r in range(ROWS):
        symbols: list[str] = []
        for c in range(COLS):
            piece = board[r][c]
            if piece is None:
                symbols.append(".")
                continue

            symbol = "K" if piece.is_king else "W" if piece.color == WHITE_PLAYER else "B"
            symbols.append(symbol)

        lines.append(f"{r + 1:>2}  " + " ".join(symbols))

    return "\n".join(lines)


def print_board(board: Board) -> None:
    print(format_board(board))
