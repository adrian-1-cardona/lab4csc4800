"""Compare the speed and game outcomes of all three AI agents."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Callable, Dict, Optional, Tuple

from iddfs import choose_iddfs_move
from minimax import choose_ai_move, choose_minimax_move
from tictactoe import GameState, Move


AgentSelector = Callable[[GameState, str], Move]


# this gives every algorithm the same agent shape
@dataclass(frozen=True)
class Agent:
    name: str
    choose_move: AgentSelector


# this stores the time and move from one decision
@dataclass(frozen=True)
class DecisionResult:
    position: str
    agent: str
    move: Move
    seconds: float

    @property
    def milliseconds(self) -> float:
        return self.seconds * 1000


# this stores the outcome from one full game
@dataclass(frozen=True)
class GameResult:
    x_agent: str
    o_agent: str
    winner: Optional[str]
    moves: int


# this adds up one agents time and game results
@dataclass
class AgentMetrics:
    decisions: int = 0
    total_seconds: float = 0.0
    games: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0

    # this records how long one move took
    def record_decision(self, seconds: float) -> None:
        self.decisions += 1
        self.total_seconds += seconds

    # this records if the agent won drew or lost
    def record_outcome(self, outcome: str) -> None:
        self.games += 1
        if outcome == "win":
            self.wins += 1
        elif outcome == "draw":
            self.draws += 1
        else:
            self.losses += 1

    @property
    def average_milliseconds(self) -> float:
        if self.decisions == 0:
            return 0.0
        return self.total_seconds * 1000 / self.decisions

    @property
    def quality_score(self) -> float:
        if self.games == 0:
            return 0.0
        return (self.wins + 0.5 * self.draws) / self.games


# these are the three agents being compared
PLAIN_MINIMAX = Agent("Plain Minimax", choose_minimax_move)
ALPHA_BETA = Agent("Alpha-Beta", choose_ai_move)
IDDFS = Agent("IDDFS", choose_iddfs_move)
AGENTS = (PLAIN_MINIMAX, ALPHA_BETA, IDDFS)


# these are the three matchups from the lab
MATCHUPS = (
    (ALPHA_BETA, PLAIN_MINIMAX),
    (IDDFS, PLAIN_MINIMAX),
    (IDDFS, ALPHA_BETA),
)


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
    started_at = perf_counter()
    move = agent.choose_move(state, state.current_player)
    elapsed = perf_counter() - started_at

    if move not in state.legal_moves():
        raise RuntimeError(f"{agent.name} returned an illegal move")

    return DecisionResult(position, agent.name, move, elapsed)


# this times every agent on the same three boards
def benchmark_decisions() -> Tuple[DecisionResult, ...]:
    results = []
    for position, state in benchmark_positions():
        for agent in AGENTS:
            results.append(_time_decision(agent, state, position))
    return tuple(results)


# this plays one game and records every decision time
def play_game(
    x_agent: Agent,
    o_agent: Agent,
    metrics: Dict[str, AgentMetrics],
) -> GameResult:
    state = GameState.new_game()
    moves = 0

    while not state.is_terminal:
        agent = x_agent if state.current_player == "X" else o_agent
        decision = _time_decision(agent, state, "game")
        metrics[agent.name].record_decision(decision.seconds)
        state = state.apply_move(decision.move)
        moves += 1

    winner = None
    if state.winner == "X":
        winner = x_agent.name
    elif state.winner == "O":
        winner = o_agent.name

    # both agents get a result from the same finished game
    for agent in (x_agent, o_agent):
        if winner is None:
            outcome = "draw"
        elif winner == agent.name:
            outcome = "win"
        else:
            outcome = "loss"
        metrics[agent.name].record_outcome(outcome)

    return GameResult(x_agent.name, o_agent.name, winner, moves)


# this runs each requested matchup one time
def run_matchups() -> Tuple[Tuple[GameResult, ...], Dict[str, AgentMetrics]]:
    metrics = {agent.name: AgentMetrics() for agent in AGENTS}
    games = tuple(
        play_game(x_agent, o_agent, metrics)
        for x_agent, o_agent in MATCHUPS
    )
    return games, metrics


# this turns the measurements into tables for the lab report
def format_report(
    decisions: Tuple[DecisionResult, ...],
    games: Tuple[GameResult, ...],
    metrics: Dict[str, AgentMetrics],
) -> str:
    lines = [
        "# Step 4 Evaluation and Comparison",
        "",
        "## Same-Position Decision Times",
        "",
        "| Position | Agent | Move | Time (ms) |",
        "| --- | --- | --- | ---: |",
    ]

    for decision in decisions:
        lines.append(
            f"| {decision.position} | {decision.agent} | "
            f"{decision.move} | {decision.milliseconds:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Matchup Results",
            "",
            "| X Agent | O Agent | Outcome | Moves |",
            "| --- | --- | --- | ---: |",
        ]
    )

    for game in games:
        outcome = game.winner if game.winner is not None else "Draw"
        lines.append(
            f"| {game.x_agent} | {game.o_agent} | {outcome} | {game.moves} |"
        )

    lines.extend(
        [
            "",
            "## Matchup Summary",
            "",
            "| Agent | Games | Wins | Draws | Losses | Decisions | "
            "Total Time (ms) | Average Time (ms) | Quality |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )

    for agent in AGENTS:
        result = metrics[agent.name]
        lines.append(
            f"| {agent.name} | {result.games} | {result.wins} | "
            f"{result.draws} | {result.losses} | {result.decisions} | "
            f"{result.total_seconds * 1000:.3f} | "
            f"{result.average_milliseconds:.3f} | "
            f"{result.quality_score:.3f} |"
        )

    opening_times = {
        result.agent: result.milliseconds
        for result in decisions
        if result.position == "opening"
    }
    speedup = opening_times[PLAIN_MINIMAX.name] / opening_times[ALPHA_BETA.name]

    lines.extend(
        [
            "",
            "## Comparison",
            "",
            f"- Alpha-Beta was {speedup:.2f} times faster than Plain Minimax "
            "on the opening decision.",
            "- Plain Minimax and Alpha-Beta made the same optimal decisions, "
            "but Alpha-Beta skipped branches that could not help.",
            "- IDDFS reached the same full-depth decision after repeating "
            "the search at each smaller depth.",
            "- A win scores 1, a draw scores 0.5, and a loss scores 0 in "
            "the quality column.",
        ]
    )

    return "\n".join(lines)


# this runs the complete step four comparison
def main() -> None:
    decisions = benchmark_decisions()
    games, metrics = run_matchups()
    print(format_report(decisions, games, metrics))


if __name__ == "__main__":
    main()
