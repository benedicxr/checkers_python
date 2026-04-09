from __future__ import annotations

from typing import Optional

from checkers import (
    BLACK_PLAYER,
    Board,
    COLS,
    Coords,
    WHITE_PLAYER,
    ROWS,
    apply_move,
    create_initial_board,
    get_captures_for_piece,
    get_piece,
    get_valid_moves_for_piece,
    get_winner_by_board,
    print_board,
)
from checkers.types import Move

PLAYER_LABELS = {
    WHITE_PLAYER: "White",
    BLACK_PLAYER: "Black",
}


def format_coords(coords: Coords) -> str:
    return f"{chr(ord('a') + coords.c)}{coords.r + 1}"


def parse_index(value: str) -> Optional[int]:
    value = value.strip().lower()
    if not value:
        return None

    if value.isdigit():
        index = int(value)
        if 1 <= index <= ROWS:
            return index - 1
        if 0 <= index < ROWS:
            return index
        return None

    if len(value) == 1 and "a" <= value <= "h":
        return ord(value) - ord("a")

    return None


def parse_coords(raw: str) -> Optional[Coords]:
    cleaned = raw.strip().lower().replace(",", " ").replace(";", " ")
    parts = cleaned.split()

    if len(parts) == 2:
        row = parse_index(parts[0])
        col = parse_index(parts[1])
        if row is not None and col is not None:
            return Coords(row, col)
        return None

    if len(parts) == 1 and len(parts[0]) >= 2:
        token = parts[0]
        if token[0].isalpha() and token[1:].isdigit():
            col = parse_index(token[0])
            row = parse_index(token[1:])
            if row is not None and col is not None:
                return Coords(row, col)

    return None


def get_all_capture_moves(board, turn: int) -> list[Move]:
    captures: list[Move] = []
    for r in range(ROWS):
        for c in range(COLS):
            piece = get_piece(board, r, c)
            if piece is None or piece.color != turn:
                continue
            captures.extend(get_valid_moves_for_piece(board, turn, Coords(r, c), captures_only=True))
    return captures


def prompt_piece_selection(board, turn: int, force_capture: bool = False) -> Coords:
    while True:
        raw = input(f"Player {PLAYER_LABELS[turn]}, select piece (row col or a1-h8): ")
        coords = parse_coords(raw)
        if coords is None:
            print("Invalid coordinate format. Use row and column numbers or a letter-number pair like a1.")
            continue

        piece = get_piece(board, coords.r, coords.c)
        if piece is None:
            print("No piece at that location.")
            continue
        if piece.color != turn:
            print("That is not your piece.")
            continue

        moves = get_valid_moves_for_piece(board, turn, coords, captures_only=force_capture)
        if not moves:
            if force_capture:
                print("A capture is available elsewhere. Select a piece that can capture.")
            else:
                print("Selected piece has no valid moves.")
            continue

        return coords


def prompt_move_selection(moves: list[Move]) -> int:
    while True:
        raw = input("Choose move number: ")
        if not raw.strip().isdigit():
            print("Enter the move number shown in the list.")
            continue

        index = int(raw.strip())
        if 0 <= index < len(moves):
            return index

        print("Move number is out of range.")


def format_move(move: Move) -> str:
    destination = format_coords(move.to)
    if move.type == "capture" and move.captured is not None:
        captured = format_coords(move.captured)
        return f"{move.type} to {destination} capturing {captured}"
    return f"{move.type} to {destination}"


def continue_capture_chain(board, turn: int, current: Coords) -> Board:
    while True:
        next_captures = get_captures_for_piece(board, turn, current)
        if not next_captures:
            return board

        print_board(board)
        print(f"Continue capturing with piece at {format_coords(current)}")
        for index, move in enumerate(next_captures):
            print(f"  {index}) {format_move(move)}")

        chosen_index = prompt_move_selection(next_captures)
        board = apply_move(board, next_captures[chosen_index])
        current = next_captures[chosen_index].to

    return board


def main() -> None:
    board, _ = create_initial_board()
    turn = WHITE_PLAYER

    while True:
        print_board(board)
        winner = get_winner_by_board(board, turn)
        if winner is not None:
            print(f"Game over. Winner: {PLAYER_LABELS[winner]}")
            break

        forced_capture = bool(get_all_capture_moves(board, turn))
        if forced_capture:
            print("Forced capture is active. You must choose a piece that can capture.")

        from_coords = prompt_piece_selection(board, turn, force_capture=forced_capture)
        valid_moves = get_valid_moves_for_piece(board, turn, from_coords, captures_only=forced_capture)

        print("Available moves:")
        for index, move in enumerate(valid_moves):
            print(f"  {index}) {format_move(move)}")

        chosen_index = prompt_move_selection(valid_moves)
        move = valid_moves[chosen_index]
        board = apply_move(board, move)

        if move.type == "capture":
            board = continue_capture_chain(board, turn, move.to)

        turn = BLACK_PLAYER if turn == WHITE_PLAYER else WHITE_PLAYER


if __name__ == "__main__":
    main()
