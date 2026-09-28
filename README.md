# Lab 4 - Adversarial Search and Games Adrian Cardona

## Game Selection

This project uses Tic-Tac-Toe because it is a two-player, zero-sum game with a small state space. Each player tries to create a winning line while stopping the other player, which makes the game useful for comparing adversarial search algorithms.

The project only uses the Python 3 standard library.

## How to Run

```bash
# watch alpha beta play against plain minimax
python3 game.py --algo1 alphabeta --algo2 minimax

# play as a human against alpha beta
python3 game.py --algo1 human --algo2 alphabeta

# watch iddfs play against alpha beta
python3 game.py --algo1 iddfs --algo2 alphabeta
```

Player 1 uses X and Player 2 uses O. Human moves use zero-based `row column` values, so `1 1` is the center square.

Each player can use `minimax`, `alphabeta`, `iddfs`, or `human`. Run `python3 game.py --help` to see every option.

### Automated Performance Evaluation

```bash
python3 game.py --compare
```

The comparison runs every pair of AI agents twice so each one plays as X and O. The table records the outcome, decision time, and recursive node visits for both players.

Run the full report generator with:

```bash
python3 evaluation.py
```

The measured report is in [`EVALUATION.md`](EVALUATION.md). To replace it with a new run, use `python3 evaluation.py > EVALUATION.md`.

## Project Files

- `tictactoe.py` stores the immutable board, validates moves, finds wins and draws, and can build a complete game tree.
- `minimax.py` contains Plain Minimax, Alpha-Beta, shared scoring, and node counting.
- `iddfs.py` contains depth-limited search and the IDDFS agent.
- `game.py` runs visible games and the shared role-balanced comparison suite.
- `evaluation.py` benchmarks shared boards and builds the detailed report.
- `EVALUATION.md` records the measured results and discussion.

## How the Agents Decide

### Plain Minimax

Plain Minimax checks every possible branch. MAX keeps the highest score, while MIN keeps the lowest score for MAX. A win is `+1`, a draw is `0`, and a loss is `-1`.

### Alpha-Beta

Alpha-Beta returns the same Minimax decision while skipping branches that cannot help. Alpha is the best score MAX can guarantee so far, and beta is the best score MIN can guarantee so far. The search cuts off a branch when `alpha >= beta`.

### IDDFS

IDDFS runs depth-limited adversarial search at depth 1, then depth 2, and keeps going through the remaining moves. It counts repeated boards again because each deeper pass performs that work again. A nonterminal board at a limited-depth cutoff receives a neutral score because this project does not use a heuristic.

All agents check legal moves in row-first order. When moves have the same score, they keep the first one. This makes repeated runs choose the same moves.

## Code Quality Notes

- Game states are immutable, so one search branch cannot change another branch.
- Public move selectors validate the player, turn, and terminal state.
- Search counters measure recursive node visits rather than unique board positions.
- Named result fields keep game metrics readable while still allowing tuple unpacking.
- The original assignment function names remain available for compatibility.

## Implications and Future Improvements

From my results, all three agents were able to play without losing. They reached the same decisions, but they did not do the same amount of work. Plain Minimax checked every branch. Alpha-Beta skipped work that could not change its choice. IDDFS repeated earlier searches before reaching the full depth.

The main thing I learned is that getting the right answer is not the only thing that matters. Alpha-Beta was the best fit for this project because it kept the same decision quality while checking fewer nodes.

In the future, I could test each board several times and use the median time. I could also check stronger moves first, save board results for reuse, add a real cutoff heuristic, give IDDFS a time limit, randomize equal moves, show a visual game tree, and try a larger game such as Connect Four.
