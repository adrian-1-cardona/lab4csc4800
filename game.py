"""Command-line Tic-Tac-Toe games and agent comparisons."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from time import perf_counter
from typing import NamedTuple, Optional, Sequence, Tuple

from iddfs import choose_iddfs_move
from minimax import SearchStats, choose_alpha_beta_move, choose_minimax_move
from tictactoe import PLAYER_O, PLAYER_X, GameState, Move


ALGORITHMS = ("minimax", "alphabeta", "iddfs", "human")
ALGORITHM_LABELS = {
    "minimax": "Plain Minimax",
    "alphabeta": "Alpha-Beta",
    "iddfs": "IDDFS",
    "human": "Human",
}

DRAW = 0
PLAYER_ONE_WIN = 1
PLAYER_TWO_WIN = 2


# every pair plays once as x and once as o for a fair comparison
COMPARISON_MATCHUPS = (
    ("minimax", "alphabeta"),
    ("alphabeta", "minimax"),
    ("minimax", "iddfs"),
    ("iddfs", "minimax"),
    ("alphabeta", "iddfs"),
    ("iddfs", "alphabeta"),
)


# named fields keep the original tuple return easy to understand
class GameMetrics(NamedTuple):
    winner: int
    player1_seconds: float
    player1_nodes: int
    player2_seconds: float
    player2_nodes: int


class ComparisonResult(NamedTuple):
    player1_algorithm: str
    player2_algorithm: str
    winner: int
    player1_seconds: float
    player1_nodes: int
    player2_seconds: float
    player2_nodes: int


# this stores one player's time and node count
@dataclass
class PlayerMetrics:
    seconds: float = 0.0
    search: SearchStats = field(default_factory=SearchStats)


# this keeps asking until the human enters a legal move
def _choose_human_move(state: GameState) -> Move:
    while True:
        answer = input("enter row and column from 0 to 2: ").replace(",", " ")
        values = answer.split()
        if len(values) != 2:
            print("enter two numbers like 1 2")
            continue

        try:
            move = (int(values[0]), int(values[1]))
        except ValueError:
            print("row and column must be numbers")
            continue

        if move not in state.legal_moves():
            print("that move is not open")
            continue
        return move


# this sends the board to the selected player algorithm
def _choose_move(
    algorithm: str,
    state: GameState,
    player: str,
    stats: SearchStats,
) -> Move:
    if algorithm == "human":
        return _choose_human_move(state)
    if algorithm == "minimax":
        return choose_minimax_move(state, player, stats)
    if algorithm == "alphabeta":
        return choose_alpha_beta_move(state, player, stats)
    if algorithm == "iddfs":
        return choose_iddfs_move(state, player, stats=stats)
    raise ValueError(f"unknown algorithm: {algorithm}")


# this turns the winner number into an easy result message
def outcome_name(winner: int) -> str:
    outcomes = {
        DRAW: "Draw",
        PLAYER_ONE_WIN: "P1 Win",
        PLAYER_TWO_WIN: "P2 Win",
    }
    if isinstance(winner, bool) or winner not in outcomes:
        raise ValueError("winner must be 0, 1, or 2")
    return outcomes[winner]


# this runs one complete game and returns the five lab metrics
def run_game(
    player1_algo: str,
    player2_algo: str,
    verbose: bool = False,
) -> GameMetrics:
    """Play one game and return winner, times, and node counts."""

    if player1_algo not in ALGORITHMS:
        raise ValueError(f"unknown player 1 algorithm: {player1_algo}")
    if player2_algo not in ALGORITHMS:
        raise ValueError(f"unknown player 2 algorithm: {player2_algo}")

    state = GameState.new_game()
    player1 = PlayerMetrics()
    player2 = PlayerMetrics()

    if verbose:
        print(f"player 1 is {PLAYER_X} using {player1_algo}")
        print(f"player 2 is {PLAYER_O} using {player2_algo}")
        print()
        print(state)

    while not state.is_terminal:
        is_player1 = state.current_player == PLAYER_X
        algorithm = player1_algo if is_player1 else player2_algo
        metrics = player1 if is_player1 else player2
        player_number = 1 if is_player1 else 2

        started_at = perf_counter()
        move = _choose_move(
            algorithm,
            state,
            state.current_player,
            metrics.search,
        )
        metrics.seconds += perf_counter() - started_at

        if move not in state.legal_moves():
            raise RuntimeError(f"{algorithm} returned an illegal move")

        state = state.apply_move(move)

        if verbose:
            print()
            print(f"player {player_number} {algorithm} chose {move}")
            print(state)

    if state.winner == PLAYER_X:
        winner = PLAYER_ONE_WIN
    elif state.winner == PLAYER_O:
        winner = PLAYER_TWO_WIN
    else:
        winner = DRAW

    if verbose:
        print()
        print(f"outcome: {outcome_name(winner)}")
        print(
            f"player 1 time: {player1.seconds:.4f}s  "
            f"nodes: {player1.search.nodes_evaluated}"
        )
        print(
            f"player 2 time: {player2.seconds:.4f}s  "
            f"nodes: {player2.search.nodes_evaluated}"
        )

    return GameMetrics(
        winner,
        player1.seconds,
        player1.search.nodes_evaluated,
        player2.seconds,
        player2.search.nodes_evaluated,
    )


# this runs the same comparison suite used by the report
def run_comparison_suite() -> Tuple[ComparisonResult, ...]:
    """Run every role-balanced AI matchup and print its metrics."""

    print("=== Running Adversarial Search Evaluation Suite ===")
    print(
        f"{'Matchup':<27} | {'Outcome':<10} | {'P1 Nodes':<10} | "
        f"{'P2 Nodes':<10} | {'P1 Time (s)':<12} | {'P2 Time (s)':<12}"
    )
    print("-" * 102)

    results = []
    for player1_algo, player2_algo in COMPARISON_MATCHUPS:
        game = run_game(player1_algo, player2_algo)
        matchup = f"{player1_algo} vs {player2_algo}"
        print(
            f"{matchup:<27} | {outcome_name(game.winner):<10} | "
            f"{game.player1_nodes:<10} | {game.player2_nodes:<10} | "
            f"{game.player1_seconds:<12.4f} | {game.player2_seconds:<12.4f}"
        )
        results.append(
            ComparisonResult(
                player1_algo,
                player2_algo,
                game.winner,
                game.player1_seconds,
                game.player1_nodes,
                game.player2_seconds,
                game.player2_nodes,
            )
        )

    return tuple(results)


# this builds the command line options shown in the readme
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Adversarial Search Tic-Tac-Toe Lab"
    )
    parser.add_argument(
        "--algo1",
        choices=ALGORITHMS,
        default="alphabeta",
        help="algorithm for player 1 as X",
    )
    parser.add_argument(
        "--algo2",
        choices=ALGORITHMS,
        default="minimax",
        help="algorithm for player 2 as O",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="run the automated comparison suite",
    )
    return parser


# this chooses between one visible game and the full comparison
def main(argv: Optional[Sequence[str]] = None) -> None:
    args = build_parser().parse_args(argv)
    if args.compare:
        run_comparison_suite()
    else:
        run_game(args.algo1, args.algo2, verbose=True)


if __name__ == "__main__":
    main()
