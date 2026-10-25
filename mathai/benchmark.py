import copy
from pathlib import Path
import concurrent.futures

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

def _no_integrate_left(eq):
    return eq.name == "f_range" or eq.name == "s_true" or all(not contain2(eq, "f_"+item) for item in "eq integrate subs limit limitpinf limitninf".split(" "))

# Top-level helper function for picklability in multiprocessing
def run_absolute(x):
    return dowhile(x, absolute)


fx_list = [
    run_absolute,
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
# Serial & Parallel Execution Entry Points
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


def _execute_child_worker(args):
    """Worker helper function for parallel execution across cores."""
    child, equation, terminal_condition = args
    try:
        return child.execute(copy.deepcopy(equation), [], terminal_condition)
    except Exception:
        return []


def execute_parallel(tree, equation, terminal_condition=None):
    """
    Splits the strategy tree root node's children and distributes 
    them across multiple CPU cores using ProcessPoolExecutor.
    """
    children = list(tree.children.values())
    if not children:
        return []

    tasks = [(child, equation, terminal_condition) for child in children]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(_execute_child_worker, task) for task in tasks]
        
        for future in concurrent.futures.as_completed(futures):
            try:
                results = future.result()
                for eq, seq in results:
                    if terminal_condition is None or terminal_condition(eq):
                        return [(eq, seq)]
            except Exception:
                continue

    return []


def god2(string, parallel=False):
    tree = strategy_tree(load_sequences("ncert_data"))
    if parallel:
        out = execute_parallel(tree, simplify(parse(string)), _no_integrate_left)
    else:
        out = execute_serial(tree, simplify(parse(string)), _no_integrate_left)
    if len(out) >= 1:
        print(string)
        print("=>", out[0][0])
        print(["parse", "simplify"] + out[0][1])
    return out


# ---------------------------------------------------------------------------
# Benchmark Test (Pure Execution, No Writing, No Strategy Trees)
# ---------------------------------------------------------------------------


def benchmark_test(s="ncert_data"):
    data_path = Path(__file__).parent / f"{s}.txt"

    with open(data_path, "r", encoding="utf-8") as file:
        for count, line in enumerate(file, 1):
            parts = line.split()

            if not parts:
                continue

            expr_str, *function_names = parts
            eq = simplify(parse(expr_str))

            for func_name in function_names:
                func = FUNCS[func_name]
                prev_eq = copy.deepcopy(eq)
                eq = func(eq)

            print(f"{count}. {expr_str} => {eq}")

    print(f"\nBenchmark test execution completed for: {s}.txt")


# ---------------------------------------------------------------------------
# Benchmark
# ---------------------------------------------------------------------------


def benchmark(s="ncert_data"):
    data_path = Path(__file__).parent / f"{s}.txt"
    output_path = Path(__file__).parent / f"{s}_optimized.txt"

    optimized_lines = []
    
    # Initialize an empty strategy tree
    tree = Node("ROOT")

    with open(data_path, "r", encoding="utf-8") as file:
        for count, line in enumerate(file, 1):
            parts = line.split()

            if not parts:
                continue

            expr_str, *function_names = parts
            eq_parsed = simplify(parse(expr_str))

            # Try solving with the strategy tree built so far
            out = execute_serial(tree, eq_parsed, _no_integrate_left)

            if len(out) >= 1:
                # Solved successfully by the strategy tree: DO NOT update tree, exclude from optimized file
                print(f"{count}.", expr_str, "=>", out[0][0])
                continue

            # Strategy tree failed: fall back to manual function sequence
            eq = eq_parsed
            effective_steps = [expr_str]

            for func_name in function_names:
                func = FUNCS[func_name]
                prev_eq = copy.deepcopy(eq)
                eq = func(eq)
                if eq != prev_eq:
                    effective_steps.append(func_name)

            # Update the strategy tree ONLY because it failed
            current_node = tree
            for func_name in effective_steps[1:]:
                current_node = current_node.add_child(func_name)

            print(f"{count}. {expr_str} => {eq} **")
            optimized_lines.append(" ".join(effective_steps))

    with open(output_path, "w", encoding="utf-8") as file:
        file.write("\n".join(optimized_lines) + "\n")

    print(f"\nOptimized dataset successfully written to: {output_path}")
