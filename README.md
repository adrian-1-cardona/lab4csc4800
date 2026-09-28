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

Every score is measured from MAX's perspective:
- `+1` means the AI wins.
- `0` means the game is a draw or the depth limit was reached before either player won.
- `-1` means the opponent wins.

### Minimax Without Alpha-Beta Pruning
`minimax(state, depth, is_maximizing, maximizing_player)` searches every legal branch down to the depth limit or the end of the game. MAX keeps the highest child score, while MIN keeps the lowest child score.

### Minimax With Alpha-Beta Pruning
`minimax_alpha_beta(state, depth, alpha, beta, is_maximizing, maximizing_player)` returns the same optimal score while avoiding branches that cannot affect the result. Alpha stores MAX's best guaranteed score, and beta stores MIN's best guaranteed score. A branch is pruned when `beta <= alpha`.

### Player Roles
- **MAX (the AI):** `choose_ai_move()` uses alpha-beta pruning and selects the move with the highest guaranteed score.
- **MIN (the opponent):** `choose_opponent_move()` uses standard minimax without pruning and selects the move with the lowest score for the AI.

Both players are treated as rational. The recursive search alternates between maximizing and minimizing levels until it reaches a terminal board, then backs up those utility values to select an optimal move.

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