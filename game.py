"""Command-line Tic-Tac-Toe games and agent comparisons."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from time import perf_counter
from typing import Optional, Sequence, Tuple

from iddfs import choose_iddfs_move
from minimax import SearchStats, choose_ai_move, choose_minimax_move
from tictactoe import GameState, Move


ALGORITHMS = ("minimax", "alphabeta", "iddfs", "human")


# these matchups compare every ai algorithm from the lab
COMPARISON_MATCHUPS = (
    ("minimax", "alphabeta"),
    ("alphabeta", "minimax"),
    ("iddfs", "minimax"),
    ("iddfs", "alphabeta"),
)

GameMetrics = Tuple[int, float, int, float, int]
ComparisonResult = Tuple[str, str, int, float, int, float, int]


# this stores one players time and node count
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
        return choose_ai_move(state, player, stats)
    if algorithm == "iddfs":
        return choose_iddfs_move(state, player, stats=stats)
    raise ValueError(f"unknown algorithm: {algorithm}")


# this turns the winner number into an easy result message
def _outcome_name(winner: int) -> str:
    if winner == 1:
        return "P1 Win"
    if winner == 2:
        return "P2 Win"
    return "Draw"


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
        print(f"player 1 is X using {player1_algo}")
        print(f"player 2 is O using {player2_algo}")
        print()
        print(state)

    while not state.is_terminal:
        is_player1 = state.current_player == "X"
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

    if state.winner == "X":
        winner = 1
    elif state.winner == "O":
        winner = 2
    else:
        winner = 0

    if verbose:
        print()
        print(f"outcome: {_outcome_name(winner)}")
        print(
            f"player 1 time: {player1.seconds:.4f}s  "
            f"nodes: {player1.search.nodes_evaluated}"
        )
        print(
            f"player 2 time: {player2.seconds:.4f}s  "
            f"nodes: {player2.search.nodes_evaluated}"
        )

    return (
        winner,
        player1.seconds,
        player1.search.nodes_evaluated,
        player2.seconds,
        player2.search.nodes_evaluated,
    )


# this runs every ai matchup and prints one comparison table
def run_comparison_suite() -> Tuple[ComparisonResult, ...]:
    print("=== Running Adversarial Search Evaluation Suite ===")
    print(
        f"{'Matchup':<27} | {'Outcome':<10} | {'P1 Nodes':<10} | "
        f"{'P2 Nodes':<10} | {'P1 Time (s)':<12} | {'P2 Time (s)':<12}"
    )
    print("-" * 102)

    results = []
    for player1_algo, player2_algo in COMPARISON_MATCHUPS:
        winner, p1_time, p1_nodes, p2_time, p2_nodes = run_game(
            player1_algo,
            player2_algo,
        )
        matchup = f"{player1_algo} vs {player2_algo}"
        outcome = _outcome_name(winner)
        print(
            f"{matchup:<27} | {outcome:<10} | {p1_nodes:<10} | "
            f"{p2_nodes:<10} | {p1_time:<12.4f} | {p2_time:<12.4f}"
        )
        results.append(
            (
                player1_algo,
                player2_algo,
                winner,
                p1_time,
                p1_nodes,
                p2_time,
                p2_nodes,
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
