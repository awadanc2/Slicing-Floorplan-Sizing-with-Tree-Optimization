from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import random
import copy
import math


Shape = Tuple[int, int]


@dataclass
class Module:
    name: str
    width: int
    height: int


@dataclass
class ShapeOption:
    width: int
    height: int
    left_index: Optional[int] = None
    right_index: Optional[int] = None
    rotated: bool = False

    @property
    def area(self) -> int:
        return self.width * self.height

    @property
    def aspect_ratio(self) -> float:
        longer = max(self.width, self.height)
        shorter = min(self.width, self.height)
        return longer / shorter


@dataclass
class Node:
    label: str
    left: Optional["Node"] = None
    right: Optional["Node"] = None
    module: Optional[Module] = None
    shape_curve: List[ShapeOption] = field(default_factory=list)

    @property
    def is_leaf(self) -> bool:
        return self.module is not None and self.left is None and self.right is None


def generate_modules(num_modules: int, rng: random.Random) -> List[Module]:
    modules: List[Module] = []
    for idx in range(num_modules):
        width = rng.randint(2, 12)
        height = rng.randint(2, 12)
        modules.append(Module(name=f"M{idx + 1}", width=width, height=height))
    return modules


def build_random_slicing_tree(modules: List[Module], rng: random.Random) -> Node:
    forest = [Node(label=module.name, module=module) for module in modules]
    operators = ["H", "V"]
    while len(forest) > 1:
        i = rng.randrange(len(forest))
        left = forest.pop(i)
        j = rng.randrange(len(forest))
        right = forest.pop(j)
        op = rng.choice(operators)
        forest.append(Node(label=op, left=left, right=right))
    return forest[0]


def postorder_tokens(node: Node) -> List[str]:
    if node.is_leaf:
        return [node.label]
    return postorder_tokens(node.left) + postorder_tokens(node.right) + [node.label]


def parse_postfix_expression(tokens: List[str], modules: Dict[str, Module]) -> Node:
    stack: List[Node] = []
    for token in tokens:
        if token in {"H", "V"}:
            right = stack.pop()
            left = stack.pop()
            stack.append(Node(label=token, left=left, right=right))
        else:
            stack.append(Node(label=token, module=modules[token]))
    if len(stack) != 1:
        raise ValueError("Invalid postfix slicing expression.")
    return stack[0]


def prune_shape_curve(options: List[ShapeOption]) -> List[ShapeOption]:
    best_by_width: Dict[int, ShapeOption] = {}
    for option in options:
        current = best_by_width.get(option.width)
        if current is None or option.height < current.height:
            best_by_width[option.width] = option

    width_sorted = sorted(best_by_width.values(), key=lambda item: (item.width, item.height))
    pruned: List[ShapeOption] = []
    min_height_so_far = float("inf")
    for option in width_sorted:
        if option.height < min_height_so_far:
            pruned.append(option)
            min_height_so_far = option.height
    return pruned


def limit_shape_curve(options: List[ShapeOption], max_options: int = 36) -> List[ShapeOption]:
    if len(options) <= max_options:
        return options

    ranked = sorted(
        enumerate(options),
        key=lambda item: (item[1].area, item[1].aspect_ratio, item[1].width),
    )
    selected = []
    seen = set()
    sample_positions = [round(i * (len(ranked) - 1) / (max_options - 1)) for i in range(max_options)]
    for pos in sample_positions:
        idx, option = ranked[pos]
        key = (option.width, option.height, option.left_index, option.right_index, option.rotated)
        if key not in seen:
            selected.append(option)
            seen.add(key)

    if len(selected) < max_options:
        for _, option in ranked:
            key = (option.width, option.height, option.left_index, option.right_index, option.rotated)
            if key not in seen:
                selected.append(option)
                seen.add(key)
            if len(selected) >= max_options:
                break

    selected.sort(key=lambda item: (item.width, item.height))
    return selected


def compute_shape_curve(node: Node) -> List[ShapeOption]:
    if node.is_leaf:
        width = node.module.width
        height = node.module.height
        options = [ShapeOption(width=width, height=height, rotated=False)]
        if width != height:
            options.append(ShapeOption(width=height, height=width, rotated=True))
        node.shape_curve = limit_shape_curve(prune_shape_curve(options))
        return node.shape_curve

    left_curve = compute_shape_curve(node.left)
    right_curve = compute_shape_curve(node.right)
    combined: List[ShapeOption] = []

    for left_index, left_option in enumerate(left_curve):
        for right_index, right_option in enumerate(right_curve):
            if node.label == "H":
                width = max(left_option.width, right_option.width)
                height = left_option.height + right_option.height
            elif node.label == "V":
                width = left_option.width + right_option.width
                height = max(left_option.height, right_option.height)
            else:
                raise ValueError(f"Unknown operator: {node.label}")
            combined.append(
                ShapeOption(
                    width=width,
                    height=height,
                    left_index=left_index,
                    right_index=right_index,
                )
            )

    node.shape_curve = limit_shape_curve(prune_shape_curve(combined))
    return node.shape_curve


def select_best_shape(shape_curve: List[ShapeOption]) -> int:
    scored = list(enumerate(shape_curve))
    scored.sort(key=lambda item: (item[1].area, item[1].aspect_ratio, item[1].width))
    return scored[0][0]


def assign_coordinates(
    node: Node,
    option_index: int,
    origin_x: int = 0,
    origin_y: int = 0,
    placements: Optional[List[Dict[str, int]]] = None,
) -> List[Dict[str, int]]:
    if placements is None:
        placements = []

    option = node.shape_curve[option_index]
    if node.is_leaf:
        width = node.module.height if option.rotated else node.module.width
        height = node.module.width if option.rotated else node.module.height
        placements.append(
            {
                "name": node.module.name,
                "x": origin_x,
                "y": origin_y,
                "width": width,
                "height": height,
                "rotated": int(option.rotated),
            }
        )
        return placements

    left_option = option.left_index
    right_option = option.right_index

    if node.label == "H":
        assign_coordinates(node.left, left_option, origin_x, origin_y + node.right.shape_curve[right_option].height, placements)
        assign_coordinates(node.right, right_option, origin_x, origin_y, placements)
    else:
        assign_coordinates(node.left, left_option, origin_x, origin_y, placements)
        assign_coordinates(node.right, right_option, origin_x + node.left.shape_curve[left_option].width, origin_y, placements)
    return placements


def evaluate_floorplan(root: Node) -> Dict[str, object]:
    shape_curve = compute_shape_curve(root)
    best_index = select_best_shape(shape_curve)
    best_shape = shape_curve[best_index]
    placements = assign_coordinates(root, best_index)
    placements.sort(key=lambda item: item["name"])
    return {
        "shape_curve": shape_curve,
        "best_index": best_index,
        "best_shape": best_shape,
        "placements": placements,
    }


def generate_case(num_modules: int, seed: int) -> Dict[str, object]:
    rng = random.Random(seed)
    modules = generate_modules(num_modules, rng)
    original_tree = build_random_slicing_tree(modules, rng)
    tokens = postorder_tokens(original_tree)
    parsed_tree = parse_postfix_expression(tokens, {module.name: module for module in modules})
    return {
        "modules": modules,
        "tokens": tokens,
        "root": parsed_tree,
    }


def clone_tree(node: Node) -> Node:
    return copy.deepcopy(node)


def collect_internal_paths(node: Node, path: str = "") -> List[str]:
    if node.is_leaf:
        return []
    paths = [path]
    paths.extend(collect_internal_paths(node.left, path + "L"))
    paths.extend(collect_internal_paths(node.right, path + "R"))
    return paths


def collect_leaf_paths(node: Node, path: str = "") -> List[str]:
    if node.is_leaf:
        return [path]
    paths: List[str] = []
    paths.extend(collect_leaf_paths(node.left, path + "L"))
    paths.extend(collect_leaf_paths(node.right, path + "R"))
    return paths


def get_node_by_path(node: Node, path: str) -> Node:
    current = node
    for step in path:
        current = current.left if step == "L" else current.right
    return current


def get_subtree_modules(node: Node) -> List[Module]:
    if node.is_leaf:
        return [node.module]
    return get_subtree_modules(node.left) + get_subtree_modules(node.right)


def build_balanced_tree(modules: List[Module], rng: random.Random) -> Node:
    if len(modules) == 1:
        module = modules[0]
        return Node(label=module.name, module=module)

    split = len(modules) // 2
    left_modules = modules[:split]
    right_modules = modules[split:]
    cut = "V" if rng.random() < 0.5 else "H"
    return Node(
        label=cut,
        left=build_balanced_tree(left_modules, rng),
        right=build_balanced_tree(right_modules, rng),
    )


def score_shape(width: int, height: int, aspect_tolerance: float = 1.25) -> float:
    area = width * height
    aspect_ratio = max(width, height) / min(width, height)
    return area + max(0.0, aspect_ratio - aspect_tolerance) * area * 0.35


def best_pair_merge(left: Node, right: Node) -> Tuple[str, float, ShapeOption]:
    left_curve = compute_shape_curve(left)
    right_curve = compute_shape_curve(right)
    best_cut = "H"
    best_score = float("inf")
    best_shape = ShapeOption(width=0, height=0)

    for left_index, left_option in enumerate(left_curve):
        for right_index, right_option in enumerate(right_curve):
            candidates = [
                (
                    "H",
                    max(left_option.width, right_option.width),
                    left_option.height + right_option.height,
                ),
                (
                    "V",
                    left_option.width + right_option.width,
                    max(left_option.height, right_option.height),
                ),
            ]
            for cut, width, height in candidates:
                score = score_shape(width, height)
                if score < best_score:
                    best_cut = cut
                    best_score = score
                    best_shape = ShapeOption(
                        width=width,
                        height=height,
                        left_index=left_index,
                        right_index=right_index,
                    )

    return best_cut, best_score, best_shape


def combine_modules_greedily(nodes: List[Node], rng: random.Random) -> Node:
    pool = nodes[:]
    while len(pool) > 1:
        best_i = 0
        best_j = 1
        best_cut = "H"
        best_score = float("inf")

        for i in range(len(pool)):
            module_i = pool[i].module
            for j in range(i + 1, len(pool)):
                module_j = pool[j].module
                h_width = max(module_i.width, module_j.width)
                h_height = module_i.height + module_j.height
                h_score = score_shape(h_width, h_height)

                v_width = module_i.width + module_j.width
                v_height = max(module_i.height, module_j.height)
                v_score = score_shape(v_width, v_height)

                score = min(h_score, v_score)
                if score < best_score:
                    best_score = score
                    best_i = i
                    best_j = j
                    best_cut = "H" if h_score <= v_score else "V"

        right = pool.pop(best_j)
        left = pool.pop(best_i)
        if rng.random() < 0.5:
            left, right = right, left
        merged_module = Module(
            name=f"TMP_{len(pool)}",
            width=max(left.module.width, right.module.width) if best_cut == "H" else left.module.width + right.module.width,
            height=left.module.height + right.module.height if best_cut == "H" else max(left.module.height, right.module.height),
        )
        pool.append(Node(label=best_cut, left=left, right=right, module=merged_module))

    root = pool[0]
    strip_internal_module_markers(root)
    return root


def combine_modules_shape_greedily(nodes: List[Node], rng: random.Random) -> Node:
    pool = nodes[:]
    while len(pool) > 1:
        best_i = 0
        best_j = 1
        best_cut = "H"
        best_score = float("inf")

        for i in range(len(pool)):
            for j in range(i + 1, len(pool)):
                cut, score, _ = best_pair_merge(pool[i], pool[j])
                if score < best_score:
                    best_score = score
                    best_i = i
                    best_j = j
                    best_cut = cut

        right = pool.pop(best_j)
        left = pool.pop(best_i)
        if rng.random() < 0.5:
            left, right = right, left
        pool.append(Node(label=best_cut, left=left, right=right))

    return pool[0]


def strip_internal_module_markers(node: Node) -> None:
    if node is None:
        return
    if not node.is_leaf:
        node.module = None
        strip_internal_module_markers(node.left)
        strip_internal_module_markers(node.right)


def build_greedy_tree(modules: List[Module], rng: random.Random) -> Node:
    leaves = [Node(label=module.name, module=module) for module in modules]
    return combine_modules_greedily(leaves, rng)


def build_shape_greedy_tree(modules: List[Module], rng: random.Random) -> Node:
    leaves = [Node(label=module.name, module=module) for module in modules]
    return combine_modules_shape_greedily(leaves, rng)


def build_chain_tree(nodes: List[Node], cut: str) -> Node:
    if len(nodes) == 1:
        return nodes[0]
    root = Node(label=cut, left=nodes[0], right=nodes[1])
    for node in nodes[2:]:
        root = Node(label=cut, left=root, right=node)
    return root


def build_shelf_tree(modules: List[Module], rng: random.Random, target_width: int) -> Node:
    ordered = sorted(
        modules,
        key=lambda module: (max(module.width, module.height), module.width * module.height),
        reverse=True,
    )
    if rng.random() < 0.5:
        ordered = ordered[: len(ordered) // 2] + list(reversed(ordered[len(ordered) // 2 :]))

    rows: List[List[Node]] = []
    current_row: List[Node] = []
    current_width = 0

    for module in ordered:
        preferred_width = min(module.width, module.height)
        if current_row and current_width + preferred_width > target_width:
            rows.append(current_row)
            current_row = []
            current_width = 0
        current_row.append(Node(label=module.name, module=module))
        current_width += preferred_width

    if current_row:
        rows.append(current_row)

    row_trees = [build_chain_tree(row, "V") for row in rows]
    return build_chain_tree(row_trees, "H")


def build_best_shelf_tree(modules: List[Module], rng: random.Random) -> Node:
    total_area = sum(module.width * module.height for module in modules)
    base_width = max(1, round(math.sqrt(total_area)))
    factors = [0.85, 0.95, 1.05, 1.15, 1.3, 1.45]
    best_root: Optional[Node] = None
    best_eval: Optional[Dict[str, object]] = None

    for factor in factors:
        root = build_shelf_tree(modules, rng, max(1, round(base_width * factor)))
        result = evaluate_cost(root, aspect_tolerance=1.25, penalty_weight=0.35)
        if best_eval is None or result["cost"] < best_eval["cost"]:
            best_root = root
            best_eval = result

    return best_root


def evaluate_cost(root: Node, aspect_tolerance: float = 1.3, penalty_weight: float = 0.8) -> Dict[str, object]:
    result = evaluate_floorplan(root)
    best_shape: ShapeOption = result["best_shape"]
    area = best_shape.area
    aspect_ratio = best_shape.aspect_ratio
    total_module_area = sum(item["width"] * item["height"] for item in result["placements"])
    dead_space = area - total_module_area
    utilization = total_module_area / area if area > 0 else 0.0
    aspect_penalty = max(0.0, aspect_ratio - aspect_tolerance) * area * penalty_weight
    cost = area + aspect_penalty
    return {
        "cost": cost,
        "area": area,
        "aspect_ratio": aspect_ratio,
        "aspect_penalty": aspect_penalty,
        "dead_space": dead_space,
        "utilization": utilization,
        **result,
    }


def perturb_tree(root: Node, rng: random.Random) -> Tuple[Node, str]:
    candidate = clone_tree(root)
    move_type = rng.choice(["flip_cut", "swap_children", "swap_modules", "rebuild_subtree", "rebuild_small_cluster"])

    if move_type == "flip_cut":
        internal_paths = collect_internal_paths(candidate)
        if not internal_paths:
            return candidate, move_type
        path = rng.choice(internal_paths)
        node = get_node_by_path(candidate, path)
        node.label = "H" if node.label == "V" else "V"
        return candidate, move_type

    if move_type == "swap_children":
        internal_paths = collect_internal_paths(candidate)
        if not internal_paths:
            return candidate, move_type
        path = rng.choice(internal_paths)
        node = get_node_by_path(candidate, path)
        node.left, node.right = node.right, node.left
        return candidate, move_type

    if move_type == "swap_modules":
        leaf_paths = collect_leaf_paths(candidate)
        if len(leaf_paths) < 2:
            return candidate, move_type
        path_a, path_b = rng.sample(leaf_paths, 2)
        leaf_a = get_node_by_path(candidate, path_a)
        leaf_b = get_node_by_path(candidate, path_b)
        leaf_a.module, leaf_b.module = leaf_b.module, leaf_a.module
        leaf_a.label, leaf_b.label = leaf_a.module.name, leaf_b.module.name
        return candidate, move_type

    internal_paths = [path for path in collect_internal_paths(candidate) if path]
    if not internal_paths:
        return candidate, move_type
    path = rng.choice(internal_paths)
    subtree = get_node_by_path(candidate, path)
    modules = get_subtree_modules(subtree)
    if move_type == "rebuild_small_cluster":
        modules.sort(key=lambda module: (module.width * module.height, abs(module.width - module.height)))
    else:
        modules.sort(key=lambda module: module.width * module.height, reverse=True)
    if rng.random() < 0.5:
        modules = list(reversed(modules))
    roll = rng.random()
    if roll < 0.5:
        rebuilt = build_greedy_tree(modules, rng)
    elif roll < 0.75 and len(modules) <= 24:
        rebuilt = build_shape_greedy_tree(modules, rng)
    else:
        rebuilt = build_balanced_tree(modules, rng)

    parent = get_node_by_path(candidate, path[:-1])
    if path[-1] == "L":
        parent.left = rebuilt
    else:
        parent.right = rebuilt
    return candidate, move_type


def optimize_floorplan(
    modules: List[Module],
    seed: int,
    num_iterations: int = 1500,
    aspect_tolerance: float = 1.3,
    penalty_weight: float = 0.8,
    num_restarts: int = 6,
) -> Dict[str, object]:
    global_best_eval: Optional[Dict[str, object]] = None
    global_best_tokens: List[str] = []
    best_history: List[Dict[str, float]] = []
    best_restart_index = 0

    for restart in range(num_restarts):
        rng = random.Random(seed + restart * 97)
        shuffled = modules[:]
        rng.shuffle(shuffled)

        if restart % 4 == 0:
            current_root = build_balanced_tree(shuffled, rng)
        elif restart % 4 == 1:
            current_root = build_random_slicing_tree(shuffled, rng)
        elif restart % 4 == 2:
            current_root = build_greedy_tree(shuffled, rng)
        else:
            current_root = build_best_shelf_tree(shuffled, rng)

        current_eval = evaluate_cost(current_root, aspect_tolerance, penalty_weight)
        best_root = clone_tree(current_root)
        best_eval = current_eval

        initial_temp = max(600.0, current_eval["cost"] * 0.2)
        final_temp = 1e-2
        history: List[Dict[str, float]] = []
        accepted_moves = 0

        for iteration in range(num_iterations):
            if num_iterations == 1:
                temperature = final_temp
            else:
                ratio = iteration / (num_iterations - 1)
                temperature = initial_temp * ((final_temp / initial_temp) ** ratio)

            candidate_root, move_type = perturb_tree(current_root, rng)
            candidate_eval = evaluate_cost(candidate_root, aspect_tolerance, penalty_weight)
            delta = candidate_eval["cost"] - current_eval["cost"]

            accept = delta <= 0 or rng.random() < math.exp(-delta / max(temperature, 1e-9))
            if accept:
                current_root = candidate_root
                current_eval = candidate_eval
                accepted_moves += 1
                if current_eval["cost"] < best_eval["cost"]:
                    best_root = clone_tree(current_root)
                    best_eval = current_eval

            history.append(
                {
                    "iteration": iteration + 1,
                    "temperature": temperature,
                    "cost": current_eval["cost"],
                    "area": current_eval["area"],
                    "aspect_ratio": current_eval["aspect_ratio"],
                    "aspect_penalty": current_eval["aspect_penalty"],
                    "utilization": current_eval["utilization"],
                    "dead_space": current_eval["dead_space"],
                    "accepted_moves": accepted_moves,
                    "move_type": move_type,
                    "restart": restart + 1,
                }
            )

        best_tokens = postorder_tokens(best_root)
        reparsed_best = parse_postfix_expression(best_tokens, {module.name: module for module in modules})
        final_eval = evaluate_cost(reparsed_best, aspect_tolerance, penalty_weight)
        final_eval["history"] = history
        final_eval["tokens"] = best_tokens
        final_eval["accept_rate"] = accepted_moves / num_iterations if num_iterations > 0 else 0.0
        final_eval["restart"] = restart + 1

        if global_best_eval is None or final_eval["cost"] < global_best_eval["cost"]:
            global_best_eval = final_eval
            global_best_tokens = best_tokens
            best_history = history
            best_restart_index = restart + 1

    global_best_eval["history"] = best_history
    global_best_eval["tokens"] = global_best_tokens
    global_best_eval["best_restart"] = best_restart_index
    return global_best_eval
