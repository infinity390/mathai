import random
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
    current = simplify(TreeNode("d_1")/current)
    return current
import random
import schemdraw
import schemdraw.elements as elm


def on_segment(p, a, b):
    """Returns True if point p lies exactly on the line segment a-b."""
    # Collinearity check (cross product == 0)
    cross = (p[0] - a[0]) * (b[1] - a[1]) - (p[1] - a[1]) * (b[0] - a[0])
    if abs(cross) > 1e-6:
        return False
    # Bounding box check
    if min(a[0], b[0]) <= p[0] <= max(a[0], b[0]) and \
       min(a[1], b[1]) <= p[1] <= max(a[1], b[1]):
        return True
    return False


def segments_conflict_exact(a, b, c, d):
    """
    Checks if segment ab conflicts with cd (intersects or overlaps), 
    ignoring shared endpoints unless they perfectly overlap.
    """
    def ccw(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])

    c1, c2 = ccw(a, b, c), ccw(a, b, d)
    c3, c4 = ccw(c, d, a), ccw(c, d, b)

    # 1. True geometric intersection (lines cross)
    if ((c1 > 0 and c2 < 0) or (c1 < 0 and c2 > 0)) and \
       ((c3 > 0 and c4 < 0) or (c3 < 0 and c4 > 0)):
        return True

    # 2. Collinear overlap (one point lies strictly inside the other segment)
    if on_segment(c, a, b) and c != a and c != b: return True
    if on_segment(d, a, b) and d != a and d != b: return True
    if on_segment(a, c, d) and a != c and a != d: return True
    if on_segment(b, c, d) and b != c and b != d: return True

    # 3. Identical overlapping segments
    if (a == c and b == d) or (a == d and b == c):
        return True

    return False


def get_all_candidate_routes(p1, p2):
    """Generates all valid orthogonal straight line and 1-bend L-routes."""
    x1, y1 = p1
    x2, y2 = p2

    # Collinear (Straight line along single axis)
    if x1 == x2 or y1 == y2:
        return [[p1, p2]]

    # Standard L-shapes (Horizontal-first or Vertical-first)
    return [
        [p1, (x1, y2), p2],
        [p1, (x2, y1), p2]
    ]


def route_to_segments(route):
    return [(route[i], route[i + 1]) for i in range(len(route) - 1)]


def check_route_conflict(route, placed_routes, node_positions, u, v):
    """Validates that a new route does not cross placed routes or run over unrelated nodes."""
    segs = route_to_segments(route)
    
    # 1. Check against already placed routes
    for placed_route in placed_routes:
        placed_segs = route_to_segments(placed_route)
        for a, b in segs:
            for c, d in placed_segs:
                if segments_conflict_exact(a, b, c, d):
                    return True
                    
    # 2. Check against nodes (prevent line from running through an unrelated node)
    for node, pos in node_positions.items():
        if node == u or node == v:
            continue  # Permitted to touch its own endpoints
        for a, b in segs:
            if on_segment(pos, a, b):
                return True
                
    return False


def solve_routing(edges, node_positions):
    """DFS Backtracking to find a 100% collision-free route mapping for a given node layout."""
    placed_routes = []
    
    def backtrack(edge_idx):
        if edge_idx == len(edges):
            return True
        
        edge = edges[edge_idx]
        u, v = edge.edge
        p1, p2 = node_positions[u], node_positions[v]
        
        candidate_routes = get_all_candidate_routes(p1, p2)
        random.shuffle(candidate_routes) 
        
        for route in candidate_routes:
            if not check_route_conflict(route, placed_routes, node_positions, u, v):
                placed_routes.append(route)
                if backtrack(edge_idx + 1):
                    return True
                placed_routes.pop()
        return False
        
    if backtrack(0):
        return placed_routes
    return None


def draw_circuit(graph, start=None, end=None, scale=3.0, grid_size=12, max_attempts=10000):
    """
    Renders a circuit using randomized grid placement and exact geometric backtracking.
    Guarantees strict L/straight paths without line intersections or bugs.
    """
    edges = graph.edge_list
    all_nodes = set()
    for edge in edges:
        all_nodes.add(edge.edge[0])
        all_nodes.add(edge.edge[1])
        
    nodes_list = sorted(list(all_nodes))

    best_positions = None
    best_routes = None

    # Search for a node configuration that allows a perfect non-intersecting layout
    for _ in range(max_attempts):
        # Generate random available grid locations
        available_cells = [
            (col * scale, -row * scale)
            for row in range(grid_size)
            for col in range(grid_size)
        ]
        random.shuffle(available_cells)

        current_positions = {node: available_cells[i] for i, node in enumerate(nodes_list)}

        # Attempt to perfectly route all edges
        routes = solve_routing(edges, current_positions)
        
        if routes is not None:
            best_positions = current_positions
            best_routes = routes
            break  # Perfect layout found!

    if best_routes is None:
        raise RuntimeError("Failed to find a non-intersecting layout. Try increasing grid_size or max_attempts.")

    # Render Circuit Diagram with Schemdraw
    d = schemdraw.Drawing()

    for idx, edge in enumerate(edges):
        route = best_routes[idx]
        segs = route_to_segments(route)
        resistor = getattr(edge, "edge_type", "") == "resistor"
        value = getattr(edge, "value", "")

        for i, (p1, p2) in enumerate(segs):
            # Place resistor component on the last segment of the route
            if resistor and i == len(segs) - 1:
                lbl = f"{value} Ω" if value else ""
                d.add(
                    elm.Resistor()
                    .at(p1)
                    .to(p2)
                    .label(lbl)
                )
            else:
                d.add(elm.Line().at(p1).to(p2))

    # Draw Nodes
    for node, pos in best_positions.items():
        d.add(elm.Dot().at(pos))

    # Add Terminal Labels
    if start is not None and start in best_positions:
        d.add(elm.Label().at(best_positions[start]).label("Start", loc="left"))

    if end is not None and end in best_positions:
        d.add(elm.Label().at(best_positions[end]).label("End", loc="right"))

    d.draw()
    return d
