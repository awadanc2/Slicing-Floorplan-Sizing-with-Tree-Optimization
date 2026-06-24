from __future__ import annotations

from pathlib import Path
import json
import time

from src.floorplan import generate_case, evaluate_floorplan, optimize_floorplan
from src.visualize import (
    save_convergence_plot,
    save_layout_plot,
    save_summary_plot,
)


PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "outputs_optimized_stage2"
BASELINE_DIR = PROJECT_DIR / "outputs_baseline_stage1"


CASE_CONFIGS = [
    {"case_name": "small", "num_modules": 20, "seed": 20260528, "iterations": 1600, "restarts": 8},
    {"case_name": "medium", "num_modules": 50, "seed": 20260529, "iterations": 2200, "restarts": 8},
    {"case_name": "large", "num_modules": 100, "seed": 20260530, "iterations": 3000, "restarts": 10},
]


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics = []
    stage1_metrics = {}

    baseline_metrics_path = BASELINE_DIR / "metrics.json"
    if baseline_metrics_path.exists():
        with baseline_metrics_path.open("r", encoding="utf-8") as fp:
            baseline_metrics = json.load(fp)
        stage1_metrics = {item["case_name"]: item for item in baseline_metrics}

    for config in CASE_CONFIGS:
        case = generate_case(config["num_modules"], config["seed"])
        baseline = evaluate_floorplan(case["root"])
        start = time.perf_counter()
        result = optimize_floorplan(
            case["modules"],
            seed=config["seed"] + 99,
            num_iterations=config["iterations"],
            num_restarts=config["restarts"],
        )
        runtime_ms = (time.perf_counter() - start) * 1000.0

        best_shape = result["best_shape"]
        placements = result["placements"]
        baseline_shape = baseline["best_shape"]
        previous_stage = stage1_metrics.get(config["case_name"], {})

        save_layout_plot(
            placements,
            title=f"Improved Floorplan ({config['case_name']}, n={config['num_modules']})",
            output_path=OUTPUT_DIR / f"{config['case_name']}_layout.png",
        )
        save_convergence_plot(
            result["history"],
            title=f"Annealing Search ({config['case_name']}, n={config['num_modules']})",
            output_path=OUTPUT_DIR / f"{config['case_name']}_convergence.png",
        )

        metrics.append(
            {
                "case_name": config["case_name"],
                "num_modules": config["num_modules"],
                "seed": config["seed"],
                "iterations": config["iterations"],
                "restarts": config["restarts"],
                "runtime_ms": round(runtime_ms, 3),
                "shape_curve_size": len(result["shape_curve"]),
                "baseline_width": baseline_shape.width,
                "baseline_height": baseline_shape.height,
                "baseline_area": baseline_shape.area,
                "baseline_aspect_ratio": round(baseline_shape.aspect_ratio, 4),
                "best_width": best_shape.width,
                "best_height": best_shape.height,
                "best_area": best_shape.area,
                "best_aspect_ratio": round(best_shape.aspect_ratio, 4),
                "dead_space": result["dead_space"],
                "utilization": round(result["utilization"], 4),
                "improvement_area_pct": round((baseline_shape.area - best_shape.area) / baseline_shape.area * 100.0, 2),
                "improvement_aspect_pct": round((baseline_shape.aspect_ratio - best_shape.aspect_ratio) / baseline_shape.aspect_ratio * 100.0, 2),
                "improvement_vs_stage1_area_pct": round(
                    ((previous_stage.get("best_area", best_shape.area) - best_shape.area) / previous_stage.get("best_area", best_shape.area) * 100.0)
                    if previous_stage.get("best_area")
                    else 0.0,
                    2,
                ),
                "stage1_best_area": previous_stage.get("best_area"),
                "stage1_best_aspect_ratio": previous_stage.get("best_aspect_ratio"),
                "accept_rate": round(result["accept_rate"], 4),
                "best_restart": result["best_restart"],
                "postfix_expression_length": len(case["tokens"]),
                "postfix_expression_preview": " ".join(result["tokens"][:20]) + (" ..." if len(result["tokens"]) > 20 else ""),
            }
        )

    save_summary_plot(metrics, OUTPUT_DIR / "summary_metrics.png")

    with (OUTPUT_DIR / "metrics.json").open("w", encoding="utf-8") as fp:
        json.dump(metrics, fp, indent=2, ensure_ascii=False)

    summary_lines = [
        "# Experiment Summary",
        "",
        "## Problem",
        "",
        "Implement slicing floorplan sizing with stack-based postfix parsing and binary-tree-based shape-curve merging.",
        "",
        "## Results",
        "",
        "| Case | Modules | Restarts | Runtime (ms) | Best Width | Best Height | Best Area | Aspect Ratio | Utilization |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in metrics:
        summary_lines.append(
            f"| {item['case_name']} | {item['num_modules']} | {item['restarts']} | {item['runtime_ms']} | "
            f"{item['best_width']} | {item['best_height']} | {item['best_area']} | "
            f"{item['best_aspect_ratio']} | {item['utilization']} |"
        )
    summary_lines.extend(
        [
            "",
            "## Improvement over Random Baseline",
            "",
            "| Case | Baseline Area | Optimized Area | Area Improvement (%) | Baseline AR | Optimized AR | AR Improvement (%) |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in metrics:
        summary_lines.append(
            f"| {item['case_name']} | {item['baseline_area']} | {item['best_area']} | "
            f"{item['improvement_area_pct']} | {item['baseline_aspect_ratio']} | "
            f"{item['best_aspect_ratio']} | {item['improvement_aspect_pct']} |"
        )
    summary_lines.extend(
        [
            "",
            "## Improvement over Stage 1 Search Baseline",
            "",
            "| Case | Stage 1 Area | Stage 2 Area | Area Improvement (%) | Stage 1 AR | Stage 2 AR |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for item in metrics:
        summary_lines.append(
            f"| {item['case_name']} | {item['stage1_best_area']} | {item['best_area']} | "
            f"{item['improvement_vs_stage1_area_pct']} | {item['stage1_best_aspect_ratio']} | {item['best_aspect_ratio']} |"
        )
    summary_lines.extend(
        [
            "",
            "## Data Structure Mapping",
            "",
            "- Stack: parse postfix slicing expressions and reconstruct the tree.",
            "- Binary tree: represent recursive floorplan composition and support subtree perturbation and subtree rebuilding.",
            "- Sorting: select candidate shapes and rank restart results.",
            "- Simulated annealing: optimize the slicing structure through local moves.",
            "",
            "## Generated Figures",
            "",
            "- `small_layout.png`, `medium_layout.png`, `large_layout.png`",
            "- `small_convergence.png`, `medium_convergence.png`, `large_convergence.png`",
            "- `summary_metrics.png`",
        ]
    )
    with (OUTPUT_DIR / "experiment_summary.md").open("w", encoding="utf-8") as fp:
        fp.write("\n".join(summary_lines))

    improvement_lines = [
        "# Optimization Operations and Effects",
        "",
        "## Preserved Baseline",
        "",
        f"- Previous figures were backed up in `{BASELINE_DIR.name}` and were not overwritten.",
        "",
        "## Effective Operations",
        "",
        "- Multi-start search: run simulated annealing from multiple initial slicing trees and keep the best result.",
        "- Mixed initial trees: use balanced, random, greedy, and shelf-style slicing trees to avoid being trapped by a single tree style.",
        "- Shelf-style initialization: group modules by a target row width, build each row with `V` cuts, and stack rows with `H` cuts.",
        "- Stronger subtree rebuild: rebuild local subtrees during search to reduce large empty regions.",
        "- Larger search budget: increase iteration counts for all three scales.",
        "- Limited shape-curve retention: keep more candidate shapes instead of pruning too aggressively.",
        "",
        "## Observed Effects",
        "",
        "| Case | Stage 1 Area | Stage 2 Area | Area Gain (%) | Stage 1 AR | Stage 2 AR | Utilization | Best Restart |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for item in metrics:
        improvement_lines.append(
            f"| {item['case_name']} | {item['stage1_best_area']} | {item['best_area']} | "
            f"{item['improvement_vs_stage1_area_pct']} | {item['stage1_best_aspect_ratio']} | "
            f"{item['best_aspect_ratio']} | {item['utilization']} | {item['best_restart']} |"
        )
    improvement_lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The biggest improvement came from better initial slicing topologies rather than from a single longer annealing run.",
            "- Shelf-style trees gave the optimizer compact row-based starting points while preserving the binary-tree representation.",
            "- Greedy or rebuilt subtrees helped reduce visible empty corridors inside the slicing layout.",
            "- Stage 2 still solves a slicing floorplan problem, so some structural blank regions can remain if the chosen cut topology is restrictive.",
        ]
    )
    with (OUTPUT_DIR / "optimization_effects.md").open("w", encoding="utf-8") as fp:
        fp.write("\n".join(improvement_lines))

    print("Experiment completed. Outputs saved to:", OUTPUT_DIR)
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
