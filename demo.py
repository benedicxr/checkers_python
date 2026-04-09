from __future__ import annotations

from checkers_logic import (
    WHITE_PLAYER,
    Coords,
    create_initial_board,
    get_valid_moves_for_piece,
    get_winner_by_board,
)

def main() -> None:
    board, next_id = create_initial_board()
    print("next_id:", next_id)

    found = None
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p is not None and p.color == WHITE_PLAYER:
                found = Coords(r, c)
                break
        if found is not None:
            break

    if found is None:
        print("no white pieces found")
        return

    moves = get_valid_moves_for_piece(board, WHITE_PLAYER, found)
    print("piece at:", found)
    print("moves:", moves)

    winner = get_winner_by_board(board, WHITE_PLAYER)
    print("winner:", winner)

if __name__ == "__main__":
    main()