# Step 4 Evaluation and Comparison

## Method

Each agent chose a move from the same opening, middle, and late boards. The comparison then played every pair twice so each agent used X once and O once.

Decision time uses `time.perf_counter()`. A node means one recursive state visit, so repeated IDDFS visits are counted again.

## Same-Position Decisions

| Position | Agent | Move | Nodes | Time (ms) |
| --- | --- | --- | ---: | ---: |
| opening | Plain Minimax | `(0, 0)` | 549946 | 3416.480 |
| opening | Alpha-Beta | `(0, 0)` | 18297 | 120.606 |
| opening | IDDFS | `(0, 0)` | 1290114 | 7783.629 |
| middle | Plain Minimax | `(2, 0)` | 178 | 1.138 |
| middle | Alpha-Beta | `(2, 0)` | 83 | 0.559 |
| middle | IDDFS | `(2, 0)` | 430 | 2.631 |
| late | Plain Minimax | `(1, 2)` | 5 | 0.031 |
| late | Alpha-Beta | `(1, 2)` | 5 | 0.031 |
| late | IDDFS | `(1, 2)` | 8 | 0.045 |

## Role-Balanced Matchups

| X Agent | O Agent | Outcome | X Nodes | O Nodes | X Time (s) | O Time (s) |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| Plain Minimax | Alpha-Beta | Draw | 557492 | 2435 | 3.4627 | 0.0164 |
| Alpha-Beta | Plain Minimax | Draw | 19217 | 60692 | 0.1261 | 0.3813 |
| Plain Minimax | IDDFS | Draw | 557492 | 142882 | 3.4445 | 0.8700 |
| IDDFS | Plain Minimax | Draw | 1307988 | 60692 | 7.7973 | 0.3813 |
| Alpha-Beta | IDDFS | Draw | 19217 | 142882 | 0.1259 | 0.8666 |
| IDDFS | Alpha-Beta | Draw | 1307988 | 2435 | 7.7915 | 0.0163 |

## Outcome Summary

| Agent | Games | Wins | Draws | Losses | Total Nodes | Total Time (s) | Quality |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Plain Minimax | 4 | 0 | 4 | 0 | 1236368 | 7.6699 | 0.500 |
| Alpha-Beta | 4 | 0 | 4 | 0 | 43304 | 0.2846 | 0.500 |
| IDDFS | 4 | 0 | 4 | 0 | 2901740 | 17.3255 | 0.500 |

## Comparison

- All three agents chose the same move on every shared board.
- Alpha-Beta was 28.33 times faster than Plain Minimax on this opening run.
- Alpha-Beta visited 96.67% fewer opening nodes without changing the move.
- IDDFS repeated earlier depth limits, so those repeated node visits are included in its total.
- Every role-balanced matchup ended in a draw, which is the expected result for optimal Tic-Tac-Toe play.

A win scores `1`, a draw scores `0.5`, and a loss scores `0` in the quality column. Exact times can change between runs and computers, so node visits are the more stable comparison.

## Implications

These results show me that getting the right move is not the only thing that matters. All three agents reached the same decisions, but Alpha-Beta did less work because it skipped branches that could not improve its answer.

Plain Minimax was correct, but it checked every branch. IDDFS was also correct at full depth, but it repeated its earlier searches. For this small game, Alpha-Beta gave me the best balance between decision quality and speed.

## Future Improvements

In a future version, I would test each board several times and report the median time. I would also try stronger move ordering, save board results so they can be reused, and give IDDFS a time limit so it can return its deepest completed answer.

I could also add more automated checks, randomize moves with equal scores, show a visual game tree, and test the agents on a larger game such as Connect Four.
