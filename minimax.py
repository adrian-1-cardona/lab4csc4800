"""Minimax search strategies for the Tic-Tac-Toe players."""

from math import inf
from typing import Optional

from tictactoe import PLAYER_X, PLAYERS, GameState, Move


# these scores are always measured from the ai side
WIN_SCORE = 1
DRAW_SCORE = 0
LOSS_SCORE = -1


# this checks the shared values before a search starts
def _validate_search_inputs(
    depth: int,
    is_maximizing: bool,
    maximizing_player: str,
) -> None:
    if not isinstance(depth, int) or isinstance(depth, bool) or depth < 0:
        raise ValueError("depth must be a nonnegative integer")
    if not isinstance(is_maximizing, bool):
        raise ValueError("is_maximizing must be True or False")
    if maximizing_player not in PLAYERS:
        raise ValueError("maximizing_player must be X or O")


# this gives each finished board its value for max
def evaluate_state(
    state: GameState,
    maximizing_player: str = PLAYER_X,
) -> int:
    if maximizing_player not in PLAYERS:
        raise ValueError("maximizing_player must be X or O")

    if state.winner == maximizing_player:
        return WIN_SCORE
    if state.winner is not None:
        return LOSS_SCORE
    return DRAW_SCORE


# this checks every branch without cutting any of them off
def minimax(
    state: GameState,
    depth: int,
    is_maximizing: bool,
    maximizing_player: str = PLAYER_X,
) -> float:
    """Return the best score after searching every reachable branch."""

    _validate_search_inputs(depth, is_maximizing, maximizing_player)
    if depth == 0 or state.is_terminal:
        return evaluate_state(state, maximizing_player)

    if is_maximizing:
        best_score = -inf
        for move in state.legal_moves():
            new_state = state.apply_move(move)
            score = minimax(new_state, depth - 1, False, maximizing_player)
            best_score = max(score, best_score)
        return best_score

    best_score = inf
    for move in state.legal_moves():
        new_state = state.apply_move(move)
        score = minimax(new_state, depth - 1, True, maximizing_player)
        best_score = min(score, best_score)
    return best_score


# this searches the same tree and skips branches that cannot help
def minimax_alpha_beta(
    state: GameState,
    depth: int,
    alpha: float,
    beta: float,
    is_maximizing: bool,
    maximizing_player: str = PLAYER_X,
) -> float:
    """Return the minimax score while pruning irrelevant branches."""

    _validate_search_inputs(depth, is_maximizing, maximizing_player)
    if depth == 0 or state.is_terminal:
        return evaluate_state(state, maximizing_player)

    if is_maximizing:
        best_score = -inf
        for move in state.legal_moves():
            new_state = state.apply_move(move)
            score = minimax_alpha_beta(
                new_state,
                depth - 1,
                alpha,
                beta,
                False,
                maximizing_player,
            )
            best_score = max(score, best_score)
            alpha = max(alpha, best_score)

            # this is the beta cutoff for a max branch
            if beta <= alpha:
                break
        return best_score

    best_score = inf
    for move in state.legal_moves():
        new_state = state.apply_move(move)
        score = minimax_alpha_beta(
            new_state,
            depth - 1,
            alpha,
            beta,
            True,
            maximizing_player,
        )
        best_score = min(score, best_score)
        beta = min(beta, best_score)

        # this is the alpha cutoff for a min branch
        if beta <= alpha:
            break
    return best_score


# this lets max choose its move with alpha beta pruning
def choose_ai_move(
    state: GameState,
    ai_player: str = PLAYER_X,
) -> Move:
    """Choose MAX's optimal move with alpha-beta pruning."""

    if ai_player not in PLAYERS:
        raise ValueError("ai_player must be X or O")
    if state.is_terminal:
        raise ValueError("the ai cannot move after the game is over")
    if state.current_player != ai_player:
        raise ValueError("the ai can only move on its own turn")

    depth = len(state.legal_moves())
    best_score = -inf
    best_move: Optional[Move] = None
    alpha = -inf
    beta = inf

    for move in state.legal_moves():
        new_state = state.apply_move(move)
        score = minimax_alpha_beta(
            new_state,
            depth - 1,
            alpha,
            beta,
            False,
            ai_player,
        )
        if score > best_score:
            best_score = score
            best_move = move
        alpha = max(alpha, best_score)

    if best_move is None:
        raise RuntimeError("the ai could not find a legal move")
    return best_move


# this lets min answer with regular minimax and no pruning
def choose_opponent_move(
    state: GameState,
    ai_player: str = PLAYER_X,
) -> Move:
    """Choose MIN's optimal move with standard minimax."""

    if ai_player not in PLAYERS:
        raise ValueError("ai_player must be X or O")
    if state.is_terminal:
        raise ValueError("the opponent cannot move after the game is over")
    if state.current_player == ai_player:
        raise ValueError("the opponent can only move on its own turn")

    depth = len(state.legal_moves())
    best_score = inf
    best_move: Optional[Move] = None

    for move in state.legal_moves():
        new_state = state.apply_move(move)
        score = minimax(new_state, depth - 1, True, ai_player)
        if score < best_score:
            best_score = score
            best_move = move

    if best_move is None:
        raise RuntimeError("the opponent could not find a legal move")
    return best_move
