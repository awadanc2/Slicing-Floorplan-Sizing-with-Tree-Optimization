# Slicing Floorplan Sizing Project

This project implements a slicing floorplan sizing workflow for the data structure course poster.
The current version also uses a simulated annealing style search to improve the slicing structure.

## Topic

Use stacks and binary trees to solve an EDA floorplan sizing problem:

- `Stack`: parse postfix slicing expressions
- `Binary tree`: represent the slicing structure
- `Sorting`: rank candidate solutions and summarize experiments

## Scales

The experiments follow the course project requirement:

- Small: 20 modules
- Medium: 50 modules
- Large: 100 modules

## Files

- `src/floorplan.py`: core data structures, shape-curve sizing, and slicing-tree optimization
- `src/visualize.py`: plots and layout rendering
- `run_experiments.py`: generate data, run experiments, save images and metrics
- `outputs/`: generated figures and JSON metrics

## Run

```powershell
python run_experiments.py
```

## Outputs

The script generates:

- floorplan layout images for small / medium / large cases
- shape-curve plots for each case
- a summary chart of runtime / area / aspect ratio
- `metrics.json` for poster writing

## Algorithm

1. Randomly generate rectangular modules with rotatable width and height.
2. Randomly build a slicing binary tree and convert it to a postfix expression.
3. Parse the postfix expression with a stack to rebuild the tree.
4. Compute shape curves bottom-up.
5. Prune dominated `(width, height)` pairs.
6. Use simulated annealing style local moves on the slicing tree to improve area and aspect ratio.
7. Choose the best solution, then reconstruct coordinates for all modules.

## Borrowed Ideas from the EDA Reference Project

The local reference project is a general placement project rather than a slicing floorplan project.
This project borrows only the ideas that fit the course topic:

- search-based optimization instead of a single random construction
- explicit cost design
- convergence visualization

The slicing representation, postfix parsing, and exact shape-curve evaluation remain the core of this project.

## Coordinate Convention

- `H`: horizontal cut, one child on top of the other
- `V`: vertical cut, one child placed to the right of the other
