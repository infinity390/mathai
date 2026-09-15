import copy
from .base import *
from .simplify import simplify
from .fraction import fraction
from .linear import linear_solve
from .inverse import inverse
from .expand import expand
class Edge:
    def __init__(self, edge=None, edge_type="wire", value=None):
        self.edge_type = edge_type
        self.value = value
        self.edge = tuple(edge) if edge else None
        self.current = None
class CircuitGraph:
    def __init__(self, node_count=0, edge_list=None, connection=None):
        self.node_count = node_count
        self.edge_list = []
        if edge_list:
            for edge in edge_list:
                if isinstance(edge, Edge):
                    self.edge_list.append(edge)
                else:
                    self.edge_list.append(Edge(edge))
        for edge in self.edge_list:
            if edge.edge:
                self.node_count = max(self.node_count, max(edge.edge) + 1)
        self.connection = copy.deepcopy(connection) if connection else {}
        self.variable_list = [TreeNode(f"v_{i}") for i in range(26)]
        self.complete_connection()
    def complete_connection(self):
        for i in range(self.node_count):
            self.connection.setdefault(i, [])
        for edge in self.edge_list:
            if not edge.edge:
                continue
            u, v = edge.edge
            self.connection.setdefault(u, [])
            self.connection.setdefault(v, [])
            if v not in self.connection[u]:
                self.connection[u].append(v)
            if u not in self.connection[v]:
                self.connection[v].append(u)
    def loop_rule(self, cycle):
        _, edge_cycle = cycle
        loop_sum = None
        for u, v in edge_cycle:
            edge = None
            for item in self.edge_list:
                if not item.edge:
                    continue
                a, b = item.edge
                if (a, b) == (u, v) or (a, b) == (v, u):
                    edge = item
                    break
            if edge is None:
                continue
            if (u, v) == edge.edge:
                current = edge.current
            else:
                current = -edge.current
            if current is None:
                continue
            if edge.edge_type == "resistor":
                if edge.value is None:
                    continue
                term = current * edge.value
            elif edge.edge_type == "cell":
                if edge.value is None:
                    continue
                term = -edge.value if (u, v) == edge.edge else edge.value
            else:
                continue
            loop_sum = term if loop_sum is None else loop_sum + term
        return loop_sum
    def all_simple_cycle(self):
        cycles = []
        seen = set()
        def canonical(path):
            n = len(path)
            rotations = []
            reverse = list(reversed(path))
            for i in range(n):
                rotations.append(tuple(path[i:] + path[:i]))
                rotations.append(tuple(reverse[i:] + reverse[:i]))
            return min(rotations)
        def dfs(start, node, path):
            for neighbor in self.connection.get(node, []):
                if neighbor == start and len(path) >= 3:
                    key = canonical(path)
                    if key in seen:
                        continue
                    seen.add(key)
                    edges = [(path[i], path[(i + 1) % len(path)]) for i in range(len(path))]
                    cycles.append((path[:], edges))
                    continue
                if neighbor in path:
                    continue
                if neighbor < start:
                    continue
                dfs(start, neighbor, path + [neighbor])
        for start in range(self.node_count):
            dfs(start, start, [start])
        return cycles
    def assign_currents(self, start_edge_idx=None):
        if not self.edge_list:
            return
        for edge in self.edge_list:
            edge.current = None
        adj = {i: [] for i in range(self.node_count)}
        for idx, edge in enumerate(self.edge_list):
            if not edge.edge:
                continue
            u, v = edge.edge
            adj.setdefault(u, []).append((v, idx, 1))
            adj.setdefault(v, []).append((u, idx, -1))
        tree_edges = set()
        visited = set()
        def add_tree(start):
            stack = [start]
            visited.add(start)
            while stack:
                node = stack.pop()
                for neighbor, idx, _ in adj.get(node, []):
                    if idx == start_edge_idx:
                        continue
                    if neighbor in visited:
                        continue
                    visited.add(neighbor)
                    tree_edges.add(idx)
                    stack.append(neighbor)
        for node in range(self.node_count):
            if node not in visited:
                add_tree(node)
        independent = [idx for idx in range(len(self.edge_list)) if idx not in tree_edges]
        if start_edge_idx in independent:
            independent.remove(start_edge_idx)
            independent.insert(0, start_edge_idx)
        if len(independent) > len(self.variable_list):
            raise ValueError("Too many independent currents.")
        for i, idx in enumerate(independent):
            self.edge_list[idx].current = self.variable_list[i]
        while True:
            progress = False
            for node in range(self.node_count):
                unknown = []
                for neighbor, idx, sign in adj.get(node, []):
                    if idx not in tree_edges:
                        continue
                    if self.edge_list[idx].current is None:
                        unknown.append((idx, sign))
                if len(unknown) != 1:
                    continue
                target_idx, target_sign = unknown[0]
                total = TreeNode("d_0")
                for _, idx, sign in adj.get(node, []):
                    if idx == target_idx:
                        continue
                    current = self.edge_list[idx].current
                    if current is None:
                        continue
                    if sign == 1:
                        total = total + current
                    else:
                        total = total - current
                if target_sign == 1:
                    current = -total
                else:
                    current = total
                self.edge_list[target_idx].current = simplify(current)
                progress = True
            if not progress:
                break
        missing = [i for i, edge in enumerate(self.edge_list) if edge.current is None]
        if missing:
            raise ValueError(f"Could not determine currents: {missing}")
def find_resistance(circuit, start, end):
    circuit = copy.deepcopy(circuit)
    if start == end:
        return TreeNode("d_0")
    new_node = circuit.node_count
    circuit.node_count += 1
    cell = Edge((end, new_node), "cell", TreeNode("d_1"))
    wire = Edge((new_node, start), "wire")
    circuit.edge_list.append(cell)
    cell_idx = len(circuit.edge_list) - 1
    circuit.edge_list.append(wire)
    circuit.complete_connection()
    circuit.assign_currents(cell_idx)
    cycles = circuit.all_simple_cycle()
    equations = []
    for cycle in cycles:
        equation = circuit.loop_rule(cycle)
        if equation is not None:
            equations.append(expand(equation))
    if not equations:
        return None
    equations = operation(
        "f_and",
        [TreeNode("f_eq", [equation, TreeNode("d_0")]) for equation in equations]
    )
    equations = simplify(fraction(simplify(equations)))
    equations = linear_solve(equations)
    solutions = {}
    equation_list = equations.children if equations.name == "f_and" else [equations]
    for equation in equation_list:
        variables = vlist(equation)
        if len(variables) != 1:
            continue
        variable = variables[0]
        solutions[variable] = inverse(equation.children[0], variable)
    current = circuit.edge_list[cell_idx].current
    for variable, value in solutions.items():
        if variable in vlist(current):
            current = replace(current, tree_form(variable), value)
    current = simplify(current)
    if vlist(current):
        return None
    if current == TreeNode("d_0"):
        return None
    return simplify(TreeNode("d_1") / current)
