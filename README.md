# Lab 4 - Adversarial Search and Games Adrian Cardona

## Game Selection
This project uses Tic-Tac-Toe because it is a two-player, zero-sum game with a small state space. Each player tries to create a winning line while preventing the other player from doing the same, which makes it suitable for adversarial search.

## Game Environment Setup

The game board is stored as an immutable tuple with nine cells. Each cell contains `"X"`, `"O"`, or a blank space. A move is a zero-based `(row, column)` tuple, so `(0, 0)` is the top-left square and `(2, 2)` is the bottom-right square.

`GameState` provides the main game behavior:
- `new_game()` creates an empty board with X moving first.
- `legal_moves()` returns every open square on a nonterminal board.
- `apply_move(move)` validates a move and returns a new state without changing the original state.
- `winner`, `is_draw`, and `is_terminal` describe the result of the game.
- `successors()` returns every legal move and its resulting child state.

Invalid boards and illegal moves raise `ValueError` with a clear explanation.

## Game Tree Construction

`build_game_tree(state)` recursively builds every possible branch from the supplied state until each branch reaches a win or draw. The root node has no move. Every child node stores the move used to reach it, its resulting `GameState`, and all states that can follow it.

Use `successors()` when only the next set of possible moves is needed. Use `build_game_tree()` when the complete recursive tree is needed.

## Step 2: Minimax Algorithm Implementation

Every score is measured from MAX's side:
- `+1` means the AI wins.
- `0` means the game is a draw or the search reached its depth limit.
- `-1` means the opponent wins.

### Standard Minimax
`minimax(state, depth, is_maximizing, maximizing_player)` checks every possible branch. MAX keeps the highest score, and MIN keeps the lowest score for MAX. This finds the optimal move, but checking every branch can be slow.

### Build the Faster AI With Alpha-Beta Pruning
`minimax_alpha_beta(state, depth, alpha, beta, is_maximizing, maximizing_player)` finds the same optimal move while skipping branches that cannot change the answer.

- **Alpha:** The best score MAX can guarantee so far.
- **Beta:** The best score MIN can guarantee so far.
- **Cutoff rule:** When `alpha >= beta`, the rest of that branch cannot improve the final choice, so the search stops checking it.

Skipping that extra work makes the AI faster without changing its final move.

### Player Roles
- **MAX (the AI):** `choose_ai_move()` uses the faster alpha-beta search and keeps the highest guaranteed score.
- **MIN (the opponent):** `choose_opponent_move()` uses regular minimax with no pruning and picks the lowest score for the AI.

Both players still play rationally. The search keeps switching between MAX and MIN until it reaches the end of the game, then it brings those scores back up the tree to choose the best move.

## Step 3: Iterative Deepening Depth-First Search

Regular IDDFS looks for a goal by running depth-limited search again and again. In Tic-Tac-Toe, Agent 3 uses the same idea with adversarial MAX and MIN levels:

1. Search to depth 1.
2. Start over and search to depth 2.
3. Keep increasing the limit until it reaches the requested depth or every remaining move.
4. Keep the best move from the deepest completed search.

`dls(state, max_depth)` runs one depth-limited adversarial search. `iddfs(state)` repeats DLS through every remaining level. `choose_iddfs_move()` exposes that search as the third AI agent.

A Tic-Tac-Toe game has at most nine moves. Once IDDFS reaches the full remaining depth, it sees every possible ending and selects the same optimal move as the alpha-beta agent.

### Three Agent Options

1. **Plain Minimax Agent:** Searches every branch with no pruning.
2. **Alpha-Beta Agent:** Skips branches that cannot change the final move.
3. **IDDFS Agent:** Repeats depth-limited minimax at deeper limits.

### Matchups for Later Comparisons

- **Matchup 1:** Alpha-Beta Agent vs. Plain Minimax Agent
- **Matchup 2:** IDDFS Agent vs. Plain Minimax Agent
- **Matchup 3:** IDDFS Agent vs. Alpha-Beta Agent

## Step 4: Evaluation and Comparison

The project now has two evaluation commands:

- `python3 evaluation.py` measures all three agents on the same opening, middle, and late boards and prints the report format used in `EVALUATION.md`.
- `python3 game.py --compare` plays automated matchups and prints game outcomes, execution time, and nodes evaluated for each player.

A node is counted every time an algorithm evaluates a game state. IDDFS counts states again when it revisits them at a deeper limit because those repeated searches are part of its computational work.

Decision quality is measured with the final game outcome. A win scores `1`, a draw scores `0.5`, and a loss scores `0`. Timing values depend on the computer running the evaluation, while the moves and outcomes stay deterministic.

## Running the Game and Evaluation

### Interactive Gameplay

Player 1 uses X and Player 2 uses O. Human moves use zero-based `row column` coordinates such as `1 2`.

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

## How This Maps to Chapter 5

### Decision Quality and Optimal Play

Minimax chooses the best move while assuming the opponent also chooses its best move. Tic-Tac-Toe is a two-player zero-sum game with perfect information, so two optimal agents always force a draw.

### Minimax and Alpha-Beta Efficiency

Plain Minimax explores the full game tree and has worst-case time complexity `O(b^m)`, where `b` is the branching factor and `m` is the maximum depth.

Alpha-Beta keeps alpha as MAX's best guaranteed score and beta as MIN's best guaranteed score. It stops a branch when `alpha >= beta`. This pruning returns the same optimal move as Minimax while evaluating fewer nodes. With ideal move ordering, its best-case search can approach `O(b^(m/2))`.

### Iterative Deepening

IDDFS repeats depth-limited adversarial search at depths `1, 2, ...` until it reaches the full remaining game depth. Earlier passes can provide a best move when a search has a time limit. This implementation finishes every depth, so its final move matches the other optimal agents while its node count includes the repeated work.

The measured comparison from this project is saved in `EVALUATION.md`.

## Example
```python
from minimax import choose_ai_move, choose_opponent_move
from tictactoe import PLAYER_X, GameState

state = GameState.new_game()
ai_player = PLAYER_X

while not state.is_terminal:
    if state.current_player == ai_player:
        move = choose_ai_move(state, ai_player)
    else:
        move = choose_opponent_move(state, ai_player)

    state = state.apply_move(move)
    print(state)
    print()

print("winner:", state.winner or "draw")
```

The AI searches with alpha-beta pruning, while its opponent searches the complete minimax tree without pruning. Since both players choose optimal moves, the example ends in a draw.

The implementation only uses the Python standard library and can be imported directly with Python 3.