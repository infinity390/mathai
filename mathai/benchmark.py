import copy
from pathlib import Path

from .simplify import simplify
from .expand import expand
from .parser import parse
from .fraction import fraction
from .apart import apart
from .integrate import (
    integrate_formula,
    integrate_trig_formula,
    integrate_fraction,
    integrate_subs_main as integrate_subs,
    solve_integrate as integrate_clean,
)
from .factor import factor2
from .trig import trig0, trig1, trig4, trig6
from .univariate_inequality import simple_wavycurvy, absolute
from .limit import limit1
from .logic import logic0
from .base import *


fx_list = [
    lambda x: dowhile(x, absolute),
    logic0,
    limit1,
    simple_wavycurvy,
    simplify,
    expand,
    fraction,
    integrate_formula,
    integrate_subs,
    integrate_trig_formula,
    integrate_clean,
    apart,
    trig0,
    trig1,
    trig4,
    integrate_fraction,
    factor2,
    trig6,
]

name_list = """
absolute logic0 limit1 simple_wavycurvy simplify expand fraction
integrate_formula integrate_subs integrate_trig_formula
integrate_clean apart trig0 trig1 trig4 integrate_fraction factor2 trig6
""".split()

# O(1) name -> function lookup
FUNCS = dict(zip(name_list, fx_list))


# ---------------------------------------------------------------------------
# Benchmark
# ---------------------------------------------------------------------------


def benchmark(s="ncert_data"):
    data_path = Path(__file__).parent / f"{s}.txt"
    output_path = Path(__file__).parent / f"{s}_optimized.txt"

    optimized_lines = []

    with open(data_path, "r", encoding="utf-8") as file:
        for count, line in enumerate(file, 1):
            parts = line.split()

            if not parts:
                continue

            expr_str, *function_names = parts
            eq = simplify(parse(expr_str))
            effective_steps = [expr_str]

            for func_name in function_names:
                func = FUNCS[func_name]
                prev_eq = copy.deepcopy(eq)
                eq = func(eq)

                if eq != prev_eq:
                    effective_steps.append(func_name)

            print(f"{count}. {expr_str} => {eq}")
            optimized_lines.append(" ".join(effective_steps))

    with open(output_path, "w", encoding="utf-8") as file:
        file.write("\n".join(optimized_lines) + "\n")

    print(f"\nOptimized dataset successfully written to: {output_path}")


# ---------------------------------------------------------------------------
# Strategy tree
# ---------------------------------------------------------------------------


class Node:
    def __init__(self, value):
        self.value = value
        self.children = {}  # Dictionary for O(1) child lookup

    def add_child(self, value):
        if value not in self.children:
            self.children[value] = Node(value)
        return self.children[value]

    def execute(self, equation, sequence=None, terminal_condition=None):
        if sequence is None:
            sequence = []

        if self.value != "ROOT":
            func = FUNCS[self.value]

            # Track previous state to detect and prune no-ops
            prev_eq = copy.deepcopy(equation)
            equation = func(equation)

            # PRUNING: if the function didn't change the equation, halt this branch
            if equation == prev_eq:
                return []

            sequence = sequence + [self.value]

            # Check terminal condition after applying the function
            if terminal_condition is not None and terminal_condition(equation):
                return [(equation, sequence)]

        if not self.children:
            return [(equation, sequence)]

        results = []
        for child in self.children.values():
            results.extend(
                child.execute(copy.deepcopy(equation), sequence, terminal_condition)
            )

        return results


def strategy_tree(sequences):
    root = Node("ROOT")

    for sequence in sequences:
        node = root

        for function_name in sequence:
            node = node.add_child(function_name)

    return root


def load_sequences(s="ncert_data"):
    data_path = Path(__file__).parent / f"{s}.txt"
    sequences = []

    with open(data_path, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.split()

            if parts:
                sequences.append(parts[1:])

    return sequences


def print_tree(node, depth=0):
    print("  " * depth + str(node.value))

    for child in node.children.values():
        print_tree(child, depth + 1)


# ---------------------------------------------------------------------------
# Serial Execution Entry Point
# ---------------------------------------------------------------------------


def execute_serial(tree, equation, terminal_condition=None):
    """
    Executes the strategy tree serially and returns at most one 
    matching path as a list of tuples: [(equation, sequence)].
    """
    for child in tree.children.values():
        try:
            results = child.execute(copy.deepcopy(equation), [], terminal_condition)
        except Exception:
            continue

        for eq, seq in results:
            if terminal_condition is None or terminal_condition(eq):
                return [(eq, seq)]

    return []
