import schemdraw
import schemdraw.elements as elm
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
def draw_circuit(graph):
    size = 80
    margin = 35
    spacing = 6
    positions = []
    n = graph.node_count
    side_counts = [n // 4] * 4
    for i in range(n % 4):
        side_counts[i] += 1
    top, right, bottom, left = side_counts
    for i in range(top):
        positions.append((margin, margin + i * spacing))
    for i in range(right):
        positions.append(
            (margin + i * spacing, size - margin - 1)
        )
    for i in range(bottom):
        positions.append(
            (size - margin - 1, size - margin - 1 - i * spacing)
        )
    for i in range(left):
        positions.append(
            (size - margin - 1 - i * spacing, margin)
        )
    if len(positions) != n:
        print("No circuit layout found.")
        return
    edges = []
    for edge in graph.edge_list:
        if not edge.edge:
            continue
        u, v = edge.edge
        if u == v:
            continue
        edges.append((u, v))
    def orientation(a, b, c):
        value = (
            (b[1] - a[1]) * (c[0] - b[0])
            - (b[0] - a[0]) * (c[1] - b[1])
        )
        if value == 0:
            return 0
        return 1 if value > 0 else 2
    def on_segment(a, b, c):
        return (
            min(a[0], c[0]) <= b[0] <= max(a[0], c[0])
            and
            min(a[1], c[1]) <= b[1] <= max(a[1], c[1])
        )
    def intersects(a, b, c, d):
        o1 = orientation(a, b, c)
        o2 = orientation(a, b, d)
        o3 = orientation(c, d, a)
        o4 = orientation(c, d, b)
        if o1 != o2 and o3 != o4:
            return True
        if o1 == 0 and on_segment(a, c, b):
            return True
        if o2 == 0 and on_segment(a, d, b):
            return True
        if o3 == 0 and on_segment(c, a, d):
            return True
        if o4 == 0 and on_segment(c, b, d):
            return True
        return False
    def edge_intersects_node(a, b, node):
        if node == a or node == b:
            return False
        x1, y1 = a
        x2, y2 = b
        x, y = node
        cross = (
            (x - x1) * (y2 - y1)
            - (y - y1) * (x2 - x1)
        )
        if cross != 0:
            return False
        return (
            min(x1, x2) <= x <= max(x1, x2)
            and
            min(y1, y2) <= y <= max(y1, y2)
        )
    def valid_edge(a, b, drawn_edges, node_positions):
        for node in node_positions.values():
            if edge_intersects_node(a, b, node):
                return False
        for c, d in drawn_edges:
            if (
                a == c or
                a == d or
                b == c or
                b == d
            ):
                continue
            if intersects(a, b, c, d):
                return False
        return True
    node_order = list(range(n))
    def try_permutation(order):
        node_positions = {
            node: positions[i]
            for i, node in enumerate(order)
        }
        drawn_edges = []
        ordered_edges = sorted(
            edges,
            key=lambda edge: (
                abs(
                    node_positions[edge[0]][0]
                    - node_positions[edge[1]][0]
                )
                +
                abs(
                    node_positions[edge[0]][1]
                    - node_positions[edge[1]][1]
                )
            ),
            reverse=True
        )
        for u, v in ordered_edges:
            a = node_positions[u]
            b = node_positions[v]
            if not valid_edge(
                a,
                b,
                drawn_edges,
                node_positions
            ):
                return None
            drawn_edges.append((a, b))
        return node_positions, drawn_edges
    def permutations(items):
        if len(items) <= 1:
            yield items
            return
        for i in range(len(items)):
            first = items[i]
            rest = items[:i] + items[i + 1:]
            for result in permutations(rest):
                yield [first] + result
    result = None
    for order in permutations(node_order):
        result = try_permutation(order)
        if result is not None:
            break
    if result is None:
        print("No circuit layout found.")
        return
    node_positions, drawn_edges = result
    d = schemdraw.Drawing()
    for edge in graph.edge_list:
        if not edge.edge:
            continue
        u, v = edge.edge
        if u == v:
            continue
        start = node_positions[u]
        end = node_positions[v]
        if edge.edge_type == "resistor":
            element = (
                elm.Resistor()
                .at(start)
                .to(end)
            )
            if edge.value is not None:
                element.label(str(edge.value))
        elif edge.edge_type == "cell":
            element = (
                elm.Cell()
                .at(start)
                .to(end)
            )
        else:
            element = (
                elm.Line()
                .at(start)
                .to(end)
            )
        d.add(element)
    for node, position in node_positions.items():
        d.add(
            elm.Dot()
            .at(position)
            .label(chr(ord("A") + node))
        )
    d.draw()
    return node_positions
