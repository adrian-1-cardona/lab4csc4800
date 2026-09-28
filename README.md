# Lab 4 - Adversarial Search and Games

**Student:** Adrian Cardona

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

## Example

```python
from tictactoe import GameState, build_game_tree

state = GameState.new_game()
state = state.apply_move((1, 1))

print(state)
print(state.legal_moves())

tree = build_game_tree(state)
print(len(tree.children))
```

The implementation only uses the Python standard library and can be imported directly with Python 3.