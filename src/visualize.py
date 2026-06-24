from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib

matplotlib.use("Agg")


def save_shape_curve_plot(shape_curve, title: str, output_path: Path) -> None:
    widths = [item.width for item in shape_curve]
    heights = [item.height for item in shape_curve]
    areas = [item.area for item in shape_curve]

    fig, ax = plt.subplots(figsize=(6, 4.5), dpi=160)
    scatter = ax.scatter(widths, heights, c=areas, cmap="viridis", s=48, edgecolors="black", linewidths=0.4)
    ax.set_title(title)
    ax.set_xlabel("Width")
    ax.set_ylabel("Height")
    ax.grid(alpha=0.25)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Area")
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def save_layout_plot(placements: List[Dict[str, int]], title: str, output_path: Path) -> None:
    max_x = max(item["x"] + item["width"] for item in placements)
    max_y = max(item["y"] + item["height"] for item in placements)

    fig, ax = plt.subplots(figsize=(8, 6), dpi=160)
    color_map = plt.cm.get_cmap("tab20", len(placements))
    for idx, item in enumerate(placements):
        rect = Rectangle((item["x"], item["y"]), item["width"], item["height"], facecolor=color_map(idx), edgecolor="black", linewidth=1.0, alpha=0.8)
        ax.add_patch(rect)
        if len(placements) <= 50:
            ax.text(
                item["x"] + item["width"] / 2,
                item["y"] + item["height"] / 2,
                item["name"],
                ha="center",
                va="center",
                fontsize=7 if len(placements) <= 30 else 5,
            )

    bbox = Rectangle((0, 0), max_x, max_y, facecolor="none", edgecolor="red", linewidth=1.6, linestyle="--", alpha=0.7)
    ax.add_patch(bbox)

    ax.set_xlim(0, max_x * 1.05)
    ax.set_ylim(0, max_y * 1.05)
    ax.set_aspect("equal")
    ax.set_title(title)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.grid(alpha=0.15)
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def save_layout_comparison_plot(
    initial_placements: List[Dict[str, int]],
    optimized_placements: List[Dict[str, int]],
    title: str,
    output_path: Path,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=160)
    panels = [
        ("Initial", initial_placements, axes[0]),
        ("Optimized", optimized_placements, axes[1]),
    ]

    for panel_title, placements, ax in panels:
        max_x = max(item["x"] + item["width"] for item in placements)
        max_y = max(item["y"] + item["height"] for item in placements)
        color_map = plt.cm.get_cmap("tab20", len(placements))
        for idx, item in enumerate(placements):
            rect = Rectangle((item["x"], item["y"]), item["width"], item["height"], facecolor=color_map(idx), edgecolor="black", linewidth=0.8, alpha=0.82)
            ax.add_patch(rect)
        bbox = Rectangle((0, 0), max_x, max_y, facecolor="none", edgecolor="red", linewidth=1.5, linestyle="--", alpha=0.7)
        ax.add_patch(bbox)
        ax.set_xlim(0, max_x * 1.05)
        ax.set_ylim(0, max_y * 1.05)
        ax.set_aspect("equal")
        ax.set_title(panel_title)
        ax.grid(alpha=0.15)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")

    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def save_convergence_plot(history: List[Dict[str, float]], title: str, output_path: Path) -> None:
    iterations = [item["iteration"] for item in history]
    costs = [item["cost"] for item in history]
    areas = [item["area"] for item in history]
    aspects = [item["aspect_ratio"] for item in history]
    temperatures = [item["temperature"] for item in history]

    fig, axes = plt.subplots(2, 2, figsize=(10, 6.5), dpi=160)
    axes[0, 0].plot(iterations, costs, color="#4C72B0", linewidth=1.1)
    axes[0, 0].set_title("Cost")
    axes[0, 0].grid(alpha=0.2)

    axes[0, 1].plot(iterations, areas, color="#55A868", linewidth=1.1)
    axes[0, 1].set_title("Area")
    axes[0, 1].grid(alpha=0.2)

    axes[1, 0].plot(iterations, aspects, color="#C44E52", linewidth=1.1)
    axes[1, 0].set_title("Aspect Ratio")
    axes[1, 0].grid(alpha=0.2)

    axes[1, 1].plot(iterations, temperatures, color="#8172B2", linewidth=1.1)
    axes[1, 1].set_title("Temperature")
    axes[1, 1].set_yscale("log")
    axes[1, 1].grid(alpha=0.2)

    for ax in axes.flat:
        ax.set_xlabel("Iteration")

    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def save_summary_plot(metrics: List[Dict[str, object]], output_path: Path) -> None:
    labels = [item["case_name"] for item in metrics]
    runtimes = [item["runtime_ms"] for item in metrics]
    areas = [item["best_area"] for item in metrics]
    aspects = [item["best_aspect_ratio"] for item in metrics]

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), dpi=160)
    axes[0].bar(labels, runtimes, color="#4C72B0")
    axes[0].set_title("Runtime (ms)")
    axes[0].grid(axis="y", alpha=0.25)

    axes[1].bar(labels, areas, color="#55A868")
    axes[1].set_title("Best Area")
    axes[1].grid(axis="y", alpha=0.25)

    axes[2].bar(labels, aspects, color="#C44E52")
    axes[2].set_title("Aspect Ratio")
    axes[2].grid(axis="y", alpha=0.25)

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)
