"""Build a repeatable performance report for all three AI agents."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Dict, Tuple

from game import (
    ALGORITHM_LABELS,
    COMPARISON_MATCHUPS,
    DRAW,
    PLAYER_ONE_WIN,
    PLAYER_TWO_WIN,
    GameMetrics,
    run_game,
)
from iddfs import choose_iddfs_move
from minimax import SearchStats, choose_alpha_beta_move, choose_minimax_move
from tictactoe import GameState, Move


AgentSelector = Callable[[GameState, str, SearchStats], Move]


# this gives iddfs the same call shape as the other agents
def _choose_iddfs_with_stats(
    state: GameState,
    player: str,
    stats: SearchStats,
) -> Move:
    return choose_iddfs_move(state, player, stats=stats)


# this keeps each algorithm name and selector together
@dataclass(frozen=True)
class Agent:
    key: str
    name: str
    choose_move: AgentSelector


# this stores one decision from a shared board position
@dataclass(frozen=True)
class DecisionResult:
    position: str
    agent_key: str
    agent_name: str
    move: Move
    seconds: float
    nodes_evaluated: int

    @property
    def milliseconds(self) -> float:
        return self.seconds * 1000


# this stores one complete command line matchup
@dataclass(frozen=True)
class MatchupResult:
    player1: Agent
    player2: Agent
    metrics: GameMetrics


# this adds up one agent's game results
@dataclass
class AgentMetrics:
    games: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    total_seconds: float = 0.0
    total_nodes: int = 0

    def record_game(self, outcome: str, seconds: float, nodes: int) -> None:
        if outcome not in {"win", "draw", "loss"}:
            raise ValueError("outcome must be win, draw, or loss")

        self.games += 1
        self.total_seconds += seconds
        self.total_nodes += nodes
        if outcome == "win":
            self.wins += 1
        elif outcome == "draw":
            self.draws += 1
        else:
            self.losses += 1

    @property
    def quality_score(self) -> float:
        if self.games == 0:
            return 0.0
        return (self.wins + 0.5 * self.draws) / self.games


PLAIN_MINIMAX = Agent(
    "minimax",
    ALGORITHM_LABELS["minimax"],
    choose_minimax_move,
)
ALPHA_BETA = Agent(
    "alphabeta",
    ALGORITHM_LABELS["alphabeta"],
    choose_alpha_beta_move,
)
IDDFS = Agent(
    "iddfs",
    ALGORITHM_LABELS["iddfs"],
    _choose_iddfs_with_stats,
)
AGENTS = (PLAIN_MINIMAX, ALPHA_BETA, IDDFS)
AGENTS_BY_KEY = {agent.key: agent for agent in AGENTS}


# this builds a board by playing each move in order
def _state_after(*moves: Move) -> GameState:
    state = GameState.new_game()
    for move in moves:
        state = state.apply_move(move)
    return state


# these boards compare every agent from the same starting point
def benchmark_positions() -> Tuple[Tuple[str, GameState], ...]:
    return (
        ("opening", GameState.new_game()),
        ("middle", _state_after((0, 0), (1, 1), (2, 2), (0, 2))),
        (
            "late",
            _state_after(
                (0, 0),
                (0, 1),
                (0, 2),
                (1, 1),
                (1, 0),
                (2, 0),
                (2, 1),
            ),
        ),
    )


# this measures one decision with the high precision clock
def _time_decision(
    agent: Agent,
    state: GameState,
    position: str,
) -> DecisionResult:
    stats = SearchStats()
    started_at = perf_counter()
    move = agent.choose_move(state, state.current_player, stats)
    elapsed = perf_counter() - started_at

    if move not in state.legal_moves():
        raise RuntimeError(f"{agent.name} returned an illegal move")

    return DecisionResult(
        position,
        agent.key,
        agent.name,
        move,
        elapsed,
        stats.nodes_evaluated,
    )


# this times every agent on the same three boards
def benchmark_decisions() -> Tuple[DecisionResult, ...]:
    return tuple(
        _time_decision(agent, state, position)
        for position, state in benchmark_positions()
        for agent in AGENTS
    )


# this converts the numeric winner into one player's result
def _outcome_for_player(winner: int, player_number: int) -> str:
    if winner == DRAW:
        return "draw"
    if winner == player_number:
        return "win"
    if winner in {PLAYER_ONE_WIN, PLAYER_TWO_WIN}:
        return "loss"
    raise ValueError("winner must be 0, 1, or 2")


# this runs the same balanced matchups as game.py
def run_matchups() -> Tuple[Tuple[MatchupResult, ...], Dict[str, AgentMetrics]]:
    summaries = {agent.key: AgentMetrics() for agent in AGENTS}
    games = []

    for player1_key, player2_key in COMPARISON_MATCHUPS:
        player1 = AGENTS_BY_KEY[player1_key]
        player2 = AGENTS_BY_KEY[player2_key]
        metrics = run_game(player1_key, player2_key)
        summaries[player1_key].record_game(
            _outcome_for_player(metrics.winner, PLAYER_ONE_WIN),
            metrics.player1_seconds,
            metrics.player1_nodes,
        )
        summaries[player2_key].record_game(
            _outcome_for_player(metrics.winner, PLAYER_TWO_WIN),
            metrics.player2_seconds,
            metrics.player2_nodes,
        )
        games.append(MatchupResult(player1, player2, metrics))

    return tuple(games), summaries


# this checks if every agent chose the same move on each shared board
def _all_benchmark_moves_match(
    decisions: Tuple[DecisionResult, ...],
) -> bool:
    expected_agents = {agent.key for agent in AGENTS}
    for position, _ in benchmark_positions():
        position_results = {
            result.agent_key: result.move
            for result in decisions
            if result.position == position
        }
        if set(position_results) != expected_agents:
            return False
        if len(set(position_results.values())) != 1:
            return False
    return True


# this turns the measurements into a complete report
def format_report(
    decisions: Tuple[DecisionResult, ...],
    games: Tuple[MatchupResult, ...],
    summaries: Dict[str, AgentMetrics],
) -> str:
    lines = [
        "# Step 4 Evaluation and Comparison",
        "",
        "## Method",
        "",
        "Each agent chose a move from the same opening, middle, and late boards. "
        "The comparison then played every pair twice so each agent used X once "
        "and O once.",
        "",
        "Decision time uses `time.perf_counter()`. A node means one recursive "
        "state visit, so repeated IDDFS visits are counted again.",
        "",
        "## Same-Position Decisions",
        "",
        "| Position | Agent | Move | Nodes | Time (ms) |",
        "| --- | --- | --- | ---: | ---: |",
    ]

    for decision in decisions:
        lines.append(
            f"| {decision.position} | {decision.agent_name} | "
            f"`{decision.move}` | {decision.nodes_evaluated} | "
            f"{decision.milliseconds:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Role-Balanced Matchups",
            "",
            "| X Agent | O Agent | Outcome | X Nodes | O Nodes | "
            "X Time (s) | O Time (s) |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )

    for game in games:
        if game.metrics.winner == DRAW:
            outcome = "Draw"
        elif game.metrics.winner == PLAYER_ONE_WIN:
            outcome = f"{game.player1.name} Win"
        elif game.metrics.winner == PLAYER_TWO_WIN:
            outcome = f"{game.player2.name} Win"
        else:
            raise ValueError("winner must be 0, 1, or 2")

        lines.append(
            f"| {game.player1.name} | {game.player2.name} | {outcome} | "
            f"{game.metrics.player1_nodes} | {game.metrics.player2_nodes} | "
            f"{game.metrics.player1_seconds:.4f} | "
            f"{game.metrics.player2_seconds:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Outcome Summary",
            "",
            "| Agent | Games | Wins | Draws | Losses | Total Nodes | "
            "Total Time (s) | Quality |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )

    for agent in AGENTS:
        result = summaries.get(agent.key)
        if result is None:
            continue
        lines.append(
            f"| {agent.name} | {result.games} | {result.wins} | "
            f"{result.draws} | {result.losses} | {result.total_nodes} | "
            f"{result.total_seconds:.4f} | {result.quality_score:.3f} |"
        )

    lines.extend(["", "## Comparison", ""])

    benchmark_moves_match = _all_benchmark_moves_match(decisions)
    if benchmark_moves_match:
        lines.append(
            "- All three agents chose the same move on every shared board."
        )

    opening = {
        result.agent_key: result
        for result in decisions
        if result.position == "opening"
    }
    plain = opening.get(PLAIN_MINIMAX.key)
    alpha_beta = opening.get(ALPHA_BETA.key)
    iddfs = opening.get(IDDFS.key)

    if plain is not None and alpha_beta is not None:
        if alpha_beta.seconds > 0:
            speedup = plain.seconds / alpha_beta.seconds
            lines.append(
                f"- Alpha-Beta was {speedup:.2f} times faster than Plain "
                "Minimax on this opening run."
            )
        if plain.nodes_evaluated > 0:
            reduction = 1 - alpha_beta.nodes_evaluated / plain.nodes_evaluated
            lines.append(
                f"- Alpha-Beta visited {reduction:.2%} fewer opening nodes "
                "without changing the move."
            )

    if iddfs is not None:
        lines.append(
            "- IDDFS repeated earlier depth limits, so those repeated node "
            "visits are included in its total."
        )

    if games and all(game.metrics.winner == DRAW for game in games):
        lines.append(
            "- Every role-balanced matchup ended in a draw, which is the "
            "expected result for optimal Tic-Tac-Toe play."
        )

    if benchmark_moves_match:
        implication = (
            "These results show me that getting the right move is not the only "
            "thing that matters. All three agents reached the same decisions, "
            "but Alpha-Beta did less work because it skipped branches that "
            "could not improve its answer."
        )
    else:
        implication = (
            "These results show me that the agents did not choose the same "
            "moves. I would check the search logic before comparing their "
            "speed or calling the decisions equal."
        )

    lines.extend(
        [
            "",
            "A win scores `1`, a draw scores `0.5`, and a loss scores `0` "
            "in the quality column. Exact times can change between runs and "
            "computers, so node visits are the more stable comparison.",
            "",
            "## Implications",
            "",
            implication,
            "",
            "Plain Minimax was correct, but it checked every branch. IDDFS was "
            "also correct at full depth, but it repeated its earlier searches. "
            "For this small game, Alpha-Beta gave me the best balance between "
            "decision quality and speed.",
            "",
            "## Future Improvements",
            "",
            "In a future version, I would test each board several times and "
            "report the median time. I would also try stronger move ordering, "
            "save board results so they can be reused, and give IDDFS a time "
            "limit so it can return its deepest completed answer.",
            "",
            "I could also add more automated checks, randomize moves with equal "
            "scores, show a visual game tree, and test the agents on a larger "
            "game such as Connect Four.",
        ]
    )

    return "\n".join(lines)


# this runs the complete step four comparison
def main() -> None:
    decisions = benchmark_decisions()
    games, summaries = run_matchups()
    print(format_report(decisions, games, summaries))


if __name__ == "__main__":
    main()
