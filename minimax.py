"""Minimax search strategies for the Tic-Tac-Toe players."""

from dataclasses import dataclass
from math import inf
from typing import Optional

from tictactoe import PLAYER_O, PLAYER_X, PLAYERS, GameState, Move


# these scores show if max wins loses or ties
WIN_SCORE = 1
DRAW_SCORE = 0
LOSS_SCORE = -1


# this counts recursive node visits including repeated boards
@dataclass
class SearchStats:
    """Track the amount of search work completed by one agent."""

    nodes_evaluated: int = 0

    def visit(self) -> None:
        self.nodes_evaluated += 1


# this makes sure a player marker is valid
def _validate_player(player: str, parameter_name: str) -> None:
    if player not in PLAYERS:
        raise ValueError(f"{parameter_name} must be X or O")


# this makes sure each search level matches the player on the board
def _validate_search_inputs(
    state: GameState,
    depth: int,
    is_maximizing: bool,
    maximizing_player: str,
) -> None:
    if not isinstance(depth, int) or isinstance(depth, bool) or depth < 0:
        raise ValueError("depth must be a nonnegative integer")
    if not isinstance(is_maximizing, bool):
        raise ValueError("is_maximizing must be True or False")

    _validate_player(maximizing_player, "maximizing_player")
    expected_role = state.current_player == maximizing_player
    if is_maximizing != expected_role:
        raise ValueError("is_maximizing does not match the current player")


# this rejects move requests made for the wrong player or board
def _validate_agent_turn(
    state: GameState,
    agent_player: str,
    algorithm_name: str,
) -> None:
    _validate_player(agent_player, "agent_player")
    if state.is_terminal:
        raise ValueError(f"{algorithm_name} cannot move after the game is over")
    if state.current_player != agent_player:
        raise ValueError(f"{algorithm_name} can only move on its own turn")


# this gives a finished board its score from the max side
def evaluate_state(
    state: GameState,
    maximizing_player: str = PLAYER_X,
) -> int:
    _validate_player(maximizing_player, "maximizing_player")

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
    stats: Optional[SearchStats] = None,
) -> float:
    """Return the best score after searching every reachable branch."""

    _validate_search_inputs(state, depth, is_maximizing, maximizing_player)
    if stats is not None:
        stats.visit()

    # this stops at the depth limit or when the game is over
    if depth == 0 or state.is_terminal:
        return evaluate_state(state, maximizing_player)

    # max checks every move and keeps the highest score
    if is_maximizing:
        best_score = -inf
        for move in state.legal_moves():
            new_state = state.apply_move(move)
            score = minimax(
                new_state,
                depth - 1,
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
        score = minimax(
            new_state,
            depth - 1,
            True,
            maximizing_player,
            stats,
        )
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
    stats: Optional[SearchStats] = None,
) -> float:
    """Return the minimax score while pruning irrelevant branches."""

    _validate_search_inputs(state, depth, is_maximizing, maximizing_player)
    if stats is not None:
        stats.visit()

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
                stats,
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
            stats,
        )
        best_score = min(score, best_score)

        # beta remembers the best score min can guarantee so far
        beta = min(beta, best_score)

        # alpha reached beta so the rest cannot change the final choice
        if alpha >= beta:
            break
    return best_score


# this gives any player the plain minimax search
def choose_minimax_move(
    state: GameState,
    agent_player: str = PLAYER_X,
    stats: Optional[SearchStats] = None,
) -> Move:
    """Choose an optimal move with standard minimax and no pruning."""

    _validate_agent_turn(state, agent_player, "minimax")
    if stats is not None:
        stats.visit()

    depth = len(state.legal_moves())
    best_score = -inf
    best_move: Optional[Move] = None

    # the agent is max so it keeps the highest move score
    for move in state.legal_moves():
        new_state = state.apply_move(move)
        score = minimax(
            new_state,
            depth - 1,
            False,
            agent_player,
            stats,
        )
        if score > best_score:
            best_score = score
            best_move = move

    if best_move is None:
        raise RuntimeError("minimax could not find a legal move")
    return best_move


# this gives any player the faster alpha beta search
def choose_alpha_beta_move(
    state: GameState,
    agent_player: str = PLAYER_X,
    stats: Optional[SearchStats] = None,
) -> Move:
    """Choose an optimal move with alpha-beta pruning."""

    _validate_agent_turn(state, agent_player, "alpha-beta")
    if stats is not None:
        stats.visit()

    depth = len(state.legal_moves())
    best_score = -inf
    best_move: Optional[Move] = None
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
            agent_player,
            stats,
        )
        if score > best_score:
            best_score = score
            best_move = move

        # reuse alpha across root moves to prune more work
        alpha = max(alpha, best_score)

    if best_move is None:
        raise RuntimeError("alpha-beta could not find a legal move")
    return best_move


# this keeps the original assignment name working
def choose_ai_move(
    state: GameState,
    ai_player: str = PLAYER_X,
    stats: Optional[SearchStats] = None,
) -> Move:
    """Choose a move with alpha-beta pruning."""

    return choose_alpha_beta_move(state, ai_player, stats)


# this keeps the original minimizing opponent option working
def choose_opponent_move(
    state: GameState,
    ai_player: str = PLAYER_X,
    stats: Optional[SearchStats] = None,
) -> Move:
    """Choose the opposing player's move with plain minimax."""

    _validate_player(ai_player, "ai_player")
    opponent_player = PLAYER_O if ai_player == PLAYER_X else PLAYER_X
    _validate_agent_turn(state, opponent_player, "the opponent")
    return choose_minimax_move(state, opponent_player, stats)
