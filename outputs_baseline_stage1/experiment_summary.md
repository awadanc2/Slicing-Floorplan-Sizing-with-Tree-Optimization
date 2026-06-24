# Experiment Summary

## Problem

Implement slicing floorplan sizing with stack-based postfix parsing and binary-tree-based shape-curve merging.

## Results

| Case | Modules | Runtime (ms) | Curve Size | Best Width | Best Height | Best Area | Aspect Ratio |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| small | 20 | 1736.481 | 4 | 35 | 37 | 1295 | 1.0571 |
| medium | 50 | 8143.158 | 6 | 58 | 53 | 3074 | 1.0943 |
| large | 100 | 21434.057 | 7 | 72 | 89 | 6408 | 1.2361 |

## Improvement over Random Baseline

| Case | Baseline Area | Optimized Area | Area Improvement (%) | Baseline AR | Optimized AR | AR Improvement (%) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| small | 2304 | 1295 | 43.79 | 1.7778 | 1.0571 | 40.54 |
| medium | 6882 | 3074 | 55.33 | 1.2568 | 1.0943 | 12.92 |
| large | 25200 | 6408 | 74.57 | 1.5873 | 1.2361 | 22.12 |

## Data Structure Mapping

- Stack: parse postfix slicing expressions and reconstruct the tree.
- Binary tree: represent recursive floorplan composition and support subtree perturbation.
- Sorting: select the best candidate by area and aspect ratio.
- Simulated annealing: optimize the slicing structure through local moves.

## Generated Figures

- `small_layout.png`, `medium_layout.png`, `large_layout.png`
- `small_comparison.png`, `medium_comparison.png`, `large_comparison.png`
- `small_convergence.png`, `medium_convergence.png`, `large_convergence.png`
- `small_shape_curve.png`, `medium_shape_curve.png`, `large_shape_curve.png`
- `summary_metrics.png`