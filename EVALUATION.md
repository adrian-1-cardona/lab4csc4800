# Step 4 Evaluation and Comparison

## Method

Each agent made one decision from the same opening, middle, and late boards. Decision time was measured with `time.perf_counter()`. The three matchups were then played from an empty board while every move time and final outcome were recorded.

These values came from one run on the local computer. Timing can change between computers and runs, but each agent still receives the same board positions and uses the same scoring rules.

## Same-Position Decision Times

| Position | Agent | Move | Time (ms) |
| --- | --- | --- | ---: |
| opening | Plain Minimax | `(0, 0)` | 3298.995 |
| opening | Alpha-Beta | `(0, 0)` | 116.187 |
| opening | IDDFS | `(0, 0)` | 7159.853 |
| middle | Plain Minimax | `(2, 0)` | 1.100 |
| middle | Alpha-Beta | `(2, 0)` | 0.538 |
| middle | IDDFS | `(2, 0)` | 2.463 |
| late | Plain Minimax | `(1, 2)` | 0.030 |
| late | Alpha-Beta | `(1, 2)` | 0.033 |
| late | IDDFS | `(1, 2)` | 0.041 |

## Matchup Results

| X Agent | O Agent | Outcome | Moves |
| --- | --- | --- | ---: |
| Alpha-Beta | Plain Minimax | Draw | 9 |
| IDDFS | Plain Minimax | Draw | 9 |
| IDDFS | Alpha-Beta | Draw | 9 |

## Matchup Summary

| Agent | Games | Wins | Draws | Losses | Decisions | Total Time (ms) | Average Time (ms) | Quality |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Plain Minimax | 2 | 0 | 2 | 0 | 8 | 735.384 | 91.923 | 0.500 |
| Alpha-Beta | 2 | 0 | 2 | 0 | 9 | 136.742 | 15.194 | 0.500 |
| IDDFS | 2 | 0 | 2 | 0 | 10 | 14486.476 | 1448.648 | 0.500 |

## Comparison

- All three agents chose the same moves on the shared benchmark boards.
- Alpha-Beta was 28.39 times faster than Plain Minimax on the opening move.
- Alpha-Beta saved time by skipping branches that could not change the final decision.
- IDDFS took the most time because it repeated depth-limited search from depth 1 through the full remaining depth.
- Every matchup ended in a draw after nine moves, which is the expected result when both Tic-Tac-Toe agents play optimally.
- Every agent earned a quality score of `0.500`. A win scores `1`, a draw scores `0.5`, and a loss scores `0`.

Alpha-Beta gave the best performance in this run because it produced the same optimal decisions as Plain Minimax and IDDFS in less time.
