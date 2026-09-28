"""Minimax search strategies for the Tic-Tac-Toe players."""

from math import inf
from typing import Optional

from tictactoe import PLAYER_X, PLAYERS, GameState, Move


# these scores show if max wins loses or ties
WIN_SCORE = 1
DRAW_SCORE = 0
LOSS_SCORE = -1


# this makes sure the search settings are valid
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


# this gives a finished board its score from the max side
def evaluate_state(
    state: GameState,
    maximizing_player: str = PLAYER_X,
) -> int:
    if maximizing_player not in PLAYERS:
        raise ValueError("maximizing_player must be X or O")

    winner = state.winner
    if winner == maximizing_player:
        return WIN_SCORE
    if winner is not None:
        return LOSS_SCORE
    return DRAW_SCORE


# regular minimax checks every possible branch so it can be slower
def minimax(
    state: GameState,
    depth: int,
    is_maximizing: bool,
    maximizing_player: str = PLAYER_X,
) -> float:
    """Return the best score after searching every reachable branch."""

    _validate_search_inputs(depth, is_maximizing, maximizing_player)

    # this stops at the depth limit or when the game is over
    if depth == 0 or state.is_terminal:
        return evaluate_state(state, maximizing_player)

    # max checks every move and keeps the highest score
    if is_maximizing:
        best_score = -inf
        for move in state.legal_moves():
            new_state = state.apply_move(move)
            score = minimax(new_state, depth - 1, False, maximizing_player)
            best_score = max(score, best_score)
        return best_score

    # min checks every move and keeps the lowest score for max
    best_score = inf
    for move in state.legal_moves():
        new_state = state.apply_move(move)
        score = minimax(new_state, depth - 1, True, maximizing_player)
        best_score = min(score, best_score)
    return best_score


# alpha beta finds the same best move while skipping work that cannot help
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

    # this stops at the depth limit or when the game is over
    if depth == 0 or state.is_terminal:
        return evaluate_state(state, maximizing_player)

    # max checks moves and keeps the highest score
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

            # alpha remembers the best score max can guarantee so far
            alpha = max(alpha, best_score)

            # alpha reached beta so the rest cannot change the final choice
            if alpha >= beta:
                break
        return best_score

    # min checks moves and keeps the lowest score for max
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

        # beta remembers the best score min can guarantee so far
        beta = min(beta, best_score)

        # alpha reached beta so the rest cannot change the final choice
        if alpha >= beta:
            break
    return best_score


# this gives max the faster alpha beta search
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

    # this searches every move left so the ai can reach the end
    depth = len(state.legal_moves())
    best_score = -inf
    best_move: Optional[Move] = None

    # alpha starts low and beta starts high before any moves are checked
    alpha = -inf
    beta = inf

    # max checks each move that has not been pruned and keeps the best one
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

        # alpha remembers the best score max can guarantee so far
        alpha = max(alpha, best_score)

    if best_move is None:
        raise RuntimeError("the ai could not find a legal move")
    return best_move


# this gives min regular minimax so it checks every branch
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

    # this searches every move left so the opponent can reach the end
    depth = len(state.legal_moves())
    best_score = inf
    best_move: Optional[Move] = None

    # min checks every move and keeps the one that hurts max the most
    for move in state.legal_moves():
        new_state = state.apply_move(move)
        score = minimax(new_state, depth - 1, True, ai_player)
        if score < best_score:
            best_score = score
            best_move = move

    if best_move is None:
        raise RuntimeError("the opponent could not find a legal move")
    return best_move


# this lets any player use plain minimax as its own agent
def choose_minimax_move(
    state: GameState,
    agent_player: str = PLAYER_X,
) -> Move:
    """Choose an optimal move with standard minimax and no pruning."""

    if agent_player not in PLAYERS:
        raise ValueError("agent_player must be X or O")
    if state.is_terminal:
        raise ValueError("minimax cannot move after the game is over")
    if state.current_player != agent_player:
        raise ValueError("minimax can only move on its own turn")

    # this searches every move left and keeps the best one for the agent
    depth = len(state.legal_moves())
    best_score = -inf
    best_move: Optional[Move] = None

    for move in state.legal_moves():
        new_state = state.apply_move(move)
        score = minimax(new_state, depth - 1, False, agent_player)
        if score > best_score:
            best_score = score
            best_move = move

    if best_move is None:
        raise RuntimeError("minimax could not find a legal move")
    return best_move
