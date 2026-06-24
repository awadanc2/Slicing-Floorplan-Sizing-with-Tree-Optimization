# Optimization Operations and Effects

## Preserved Baseline

- Previous figures were backed up in `outputs_baseline_stage1` and were not overwritten.

## Effective Operations

- Multi-start search: run simulated annealing from multiple initial slicing trees and keep the best result.
- Mixed initial trees: use balanced, random, greedy, and shelf-style slicing trees to avoid being trapped by a single tree style.
- Shelf-style initialization: group modules by a target row width, build each row with `V` cuts, and stack rows with `H` cuts.
- Stronger subtree rebuild: rebuild local subtrees during search to reduce large empty regions.
- Larger search budget: increase iteration counts for all three scales.
- Limited shape-curve retention: keep more candidate shapes instead of pruning too aggressively.

## Observed Effects

| Case | Stage 1 Area | Stage 2 Area | Area Gain (%) | Stage 1 AR | Stage 2 AR | Utilization | Best Restart |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| small | 1295 | 1254 | 3.17 | 1.0571 | 1.1515 | 0.9306 | 8 |
| medium | 3074 | 2736 | 11.0 | 1.0943 | 1.1875 | 0.9324 | 4 |
| large | 6408 | 5727 | 10.63 | 1.2361 | 1.2029 | 0.9068 | 4 |

## Interpretation

- The biggest improvement came from better initial slicing topologies rather than from a single longer annealing run.
- Shelf-style trees gave the optimizer compact row-based starting points while preserving the binary-tree representation.
- Greedy or rebuilt subtrees helped reduce visible empty corridors inside the slicing layout.
- Stage 2 still solves a slicing floorplan problem, so some structural blank regions can remain if the chosen cut topology is restrictive.