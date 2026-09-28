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

