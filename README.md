# Lab 4 - Adversarial Search and Games Adrian Cardona

## Game Selection
This project uses Tic-Tac-Toe because it is a two-player, zero-sum game with a small state space. Each player tries to create a winning line while preventing the other player from doing the same, which makes it suitable for adversarial search.

## How to Run: 
```bash
# watch alpha beta play against plain minimax
python3 game.py --algo1 alphabeta --algo2 minimax

# play as a human against alpha beta
python3 game.py --algo1 human --algo2 alphabeta

# watch iddfs play against alpha beta
python3 game.py --algo1 iddfs --algo2 alphabeta
```
Each player can use `minimax`, `alphabeta`, `iddfs`, or `human`. Run `python3 game.py --help` to see every option.
### Automated Performance Evaluation
```bash
python3 game.py --compare
```
The comparison table shows:
- The algorithms in each matchup.
- The winner or draw outcome.
- Nodes evaluated by each player.
- Total decision time for each player.