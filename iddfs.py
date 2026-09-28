"""Iterative deepening search for the third Tic-Tac-Toe agent."""

from math import inf
from typing import Optional

from minimax import DRAW_SCORE, SearchStats, evaluate_state
from tictactoe import PLAYER_X, PLAYERS, GameState, Move


# this makes sure the depth and player values are valid
def _validate_search_inputs(
    max_depth: int,
    is_maximizing: Optional[bool],
    maximizing_player: str,
) -> None:
    if not isinstance(max_depth, int) or isinstance(max_depth, bool):
        raise ValueError("max_depth must be a nonnegative integer")
    if max_depth < 0:
        raise ValueError("max_depth must be a nonnegative integer")
    if is_maximizing is not None and not isinstance(is_maximizing, bool):
        raise ValueError("is_maximizing must be True, False, or None")
    if maximizing_player not in PLAYERS:
        raise ValueError("maximizing_player must be X or O")


# this runs one minimax search with a set depth limit
def dls(
    state: GameState,
    max_depth: int,
    is_maximizing: Optional[bool] = None,
    maximizing_player: str = PLAYER_X,
    stats: Optional[SearchStats] = None,
) -> float:
    """Return the best terminal score found within one depth limit."""

    _validate_search_inputs(max_depth, is_maximizing, maximizing_player)
    expected_role = state.current_player == maximizing_player
    if is_maximizing is None:
        is_maximizing = expected_role
    elif is_maximizing != expected_role:
        raise ValueError("is_maximizing does not match the current player")

    if stats is not None:
        stats.visit()

    # finished boards use their win draw or loss score
    if state.is_terminal:
        return evaluate_state(state, maximizing_player)

    # unfinished cutoff boards are neutral because there is no heuristic
    if max_depth == 0:
        return DRAW_SCORE

    # max checks every move and keeps the highest score
    if is_maximizing:
        best_score = -inf
        for move in state.legal_moves():
            new_state = state.apply_move(move)
            score = dls(
                new_state,
                max_depth - 1,
                False,
                maximizing_player,
                stats,
            )
            best_score = max(score, best_score)
        return best_score

    # min checks every move and keeps the lowest score for max
    best_score = inf
    for move in state.legal_moves():
        new_state = state.apply_move(move)
        score = dls(
            new_state,
            max_depth - 1,
            True,
            maximizing_player,
            stats,
        )
        best_score = min(score, best_score)
    return best_score


# this finds the best move during one iddfs depth
def _best_move_at_depth(
    state: GameState,
    depth_limit: int,
    agent_player: str,
    stats: Optional[SearchStats] = None,
) -> Move:
    if stats is not None:
        stats.visit()

    best_score = -inf
    best_move: Optional[Move] = None

    # the agent is max so it keeps the highest score at this depth
    for move in state.legal_moves():
        new_state = state.apply_move(move)
        score = dls(
            new_state,
            depth_limit - 1,
            False,
            agent_player,
            stats,
        )
        if score > best_score:
            best_score = score
            best_move = move

    if best_move is None:
        raise RuntimeError("iddfs could not find a legal move")
    return best_move


# this starts shallow and goes one level deeper after every search
def iddfs(
    state: GameState,
    agent_player: str = PLAYER_X,
    max_depth: Optional[int] = None,
    stats: Optional[SearchStats] = None,
) -> Move:
    """Choose the best move from the deepest completed DLS pass."""

    if agent_player not in PLAYERS:
        raise ValueError("agent_player must be X or O")
    if state.is_terminal:
        raise ValueError("iddfs cannot move after the game is over")
    if state.current_player != agent_player:
        raise ValueError("iddfs can only move on its own turn")

    remaining_moves = len(state.legal_moves())
    if max_depth is None:
        search_limit = remaining_moves
    else:
        if not isinstance(max_depth, int) or isinstance(max_depth, bool):
            raise ValueError("max_depth must be a positive integer")
        if max_depth <= 0:
            raise ValueError("max_depth must be a positive integer")
        search_limit = min(max_depth, remaining_moves)

    best_move: Optional[Move] = None

    # repeated boards count again because each pass does the work again
    for depth_limit in range(1, search_limit + 1):
        best_move = _best_move_at_depth(
            state,
            depth_limit,
            agent_player,
            stats,
        )

    if best_move is None:
        raise RuntimeError("iddfs did not complete a search")
    return best_move


# this gives the third agent a clear name for the matchups
def choose_iddfs_move(
    state: GameState,
    agent_player: str = PLAYER_X,
    max_depth: Optional[int] = None,
    stats: Optional[SearchStats] = None,
) -> Move:
    """Choose the third agent's move with iterative deepening."""

    return iddfs(state, agent_player, max_depth, stats)
