# Experiment Summary

## Problem

Implement slicing floorplan sizing with stack-based postfix parsing and binary-tree-based shape-curve merging.

## Results

| Case | Modules | Restarts | Runtime (ms) | Best Width | Best Height | Best Area | Aspect Ratio | Utilization |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| small | 20 | 8 | 24124.825 | 33 | 38 | 1254 | 1.1515 | 0.9306 |
| medium | 50 | 8 | 88802.767 | 57 | 48 | 2736 | 1.1875 | 0.9324 |
| large | 100 | 10 | 361322.835 | 83 | 69 | 5727 | 1.2029 | 0.9068 |

## Improvement over Random Baseline

| Case | Baseline Area | Optimized Area | Area Improvement (%) | Baseline AR | Optimized AR | AR Improvement (%) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| small | 2304 | 1254 | 45.57 | 1.7778 | 1.1515 | 35.23 |
| medium | 6882 | 2736 | 60.24 | 1.2568 | 1.1875 | 5.51 |
| large | 25200 | 5727 | 77.27 | 1.5873 | 1.2029 | 24.22 |

## Improvement over Stage 1 Search Baseline

| Case | Stage 1 Area | Stage 2 Area | Area Improvement (%) | Stage 1 AR | Stage 2 AR |
| --- | ---: | ---: | ---: | ---: | ---: |
| small | 1295 | 1254 | 3.17 | 1.0571 | 1.1515 |
| medium | 3074 | 2736 | 11.0 | 1.0943 | 1.1875 |
| large | 6408 | 5727 | 10.63 | 1.2361 | 1.2029 |

## Data Structure Mapping

- Stack: parse postfix slicing expressions and reconstruct the tree.
- Binary tree: represent recursive floorplan composition and support subtree perturbation and subtree rebuilding.
- Sorting: select candidate shapes and rank restart results.
- Simulated annealing: optimize the slicing structure through local moves.

## Generated Figures

- `small_layout.png`, `medium_layout.png`, `large_layout.png`
- `small_convergence.png`, `medium_convergence.png`, `large_convergence.png`
- `summary_metrics.png`