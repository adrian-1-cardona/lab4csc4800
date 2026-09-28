"""Tic-Tac-Toe game state and game tree construction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


# these values keep the board easy to read
BOARD_SIZE = 3
EMPTY = " "
PLAYER_X = "X"
PLAYER_O = "O"
PLAYERS = (PLAYER_X, PLAYER_O)

Move = Tuple[int, int]
Board = Tuple[str, ...]


# these are all the ways a player can win
WINNING_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


@dataclass(frozen=True)
class GameState:
    """An immutable Tic-Tac-Toe board and the player whose turn is next."""

    board: Board = (EMPTY,) * (BOARD_SIZE * BOARD_SIZE)
    current_player: str = PLAYER_X

    # this makes sure every state follows the game rules
    def __post_init__(self) -> None:
        board = tuple(self.board)
        object.__setattr__(self, "board", board)

        if len(board) != BOARD_SIZE * BOARD_SIZE:
            raise ValueError("the board must contain exactly 9 cells")

        invalid_cells = set(board) - {EMPTY, PLAYER_X, PLAYER_O}
        if invalid_cells:
            raise ValueError("board cells must be X, O, or empty")

        if self.current_player not in PLAYERS:
            raise ValueError("current_player must be X or O")

        x_count = board.count(PLAYER_X)
        o_count = board.count(PLAYER_O)
        if x_count not in (o_count, o_count + 1):
            raise ValueError("the number of X and O moves is not valid")

        expected_player = PLAYER_X if x_count == o_count else PLAYER_O
        if self.current_player != expected_player:
            raise ValueError("current_player does not match the moves on the board")

        winners = self._winning_players()
        if len(winners) > 1:
            raise ValueError("both players cannot win in the same game")
        if PLAYER_X in winners and x_count != o_count + 1:
            raise ValueError("an X win must happen immediately after an X move")
        if PLAYER_O in winners and x_count != o_count:
            raise ValueError("an O win must happen immediately after an O move")

    # this starts a new game with an empty board
    @classmethod
    def new_game(cls) -> "GameState":
        return cls()

    # this finds every player with a winning line
    def _winning_players(self) -> set[str]:
        return {
            self.board[first]
            for first, second, third in WINNING_LINES
            if self.board[first] != EMPTY
            and self.board[first] == self.board[second] == self.board[third]
        }

    # this returns the winner when the game has one
    @property
    def winner(self) -> Optional[str]:
        winners = self._winning_players()
        return next(iter(winners), None)

    # this checks if every square has been played
    @property
    def is_full(self) -> bool:
        return EMPTY not in self.board

    # this checks if no more moves should be made
    @property
    def is_terminal(self) -> bool:
        return self.winner is not None or self.is_full

    # this checks if the board ended without a winner
    @property
    def is_draw(self) -> bool:
        return self.is_full and self.winner is None

    # this lists every move the current player can make
    def legal_moves(self) -> Tuple[Move, ...]:
        if self.is_terminal:
            return ()

        return tuple(
            divmod(index, BOARD_SIZE)
            for index, cell in enumerate(self.board)
            if cell == EMPTY
        )

    # this creates a new state so the old board stays unchanged
    def apply_move(self, move: Move) -> "GameState":
        if self.is_terminal:
            raise ValueError("a move cannot be made after the game is over")

        try:
            row, column = move
        except (TypeError, ValueError) as error:
            raise ValueError("a move must contain a row and column") from error

        if (
            not isinstance(row, int)
            or isinstance(row, bool)
            or not isinstance(column, int)
            or isinstance(column, bool)
        ):
            raise ValueError("the row and column must be integers")
        if not (0 <= row < BOARD_SIZE and 0 <= column < BOARD_SIZE):
            raise ValueError("the row and column must be between 0 and 2")

        index = row * BOARD_SIZE + column
        if self.board[index] != EMPTY:
            raise ValueError("that square is already occupied")

        updated_board = list(self.board)
        updated_board[index] = self.current_player
        next_player = PLAYER_O if self.current_player == PLAYER_X else PLAYER_X

        return GameState(tuple(updated_board), next_player)

    # this gives one child state for every legal move
    def successors(self) -> Tuple[Tuple[Move, "GameState"], ...]:
        return tuple((move, self.apply_move(move)) for move in self.legal_moves())

    # this displays the board in a familiar layout
    def __str__(self) -> str:
        rows = []
        for row in range(BOARD_SIZE):
            start = row * BOARD_SIZE
            rows.append(" | ".join(self.board[start : start + BOARD_SIZE]))
        return "\n---------\n".join(rows)


@dataclass(frozen=True)
class GameTreeNode:
    """One state in the game tree and every state reachable in one move."""

    state: GameState
    move: Optional[Move] = None
    children: Tuple["GameTreeNode", ...] = ()

    # this checks if the node is at the end of its branch
    @property
    def is_leaf(self) -> bool:
        return not self.children


# this keeps building every branch until each game is over
def build_game_tree(state: GameState) -> GameTreeNode:
    """Build the complete game tree that begins at state."""

    def build_node(current_state: GameState, move: Optional[Move]) -> GameTreeNode:
        children = tuple(
            build_node(next_state, next_move)
            for next_move, next_state in current_state.successors()
        )
        return GameTreeNode(current_state, move, children)

    return build_node(state, None)
