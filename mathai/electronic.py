import math
from .base import *
from .simplify import simplify
from .fraction import fraction
from .linear import linear_solve
from .inverse import inverse
from .expand import expand

class Node:
    def __init__(self, node_type="wire", value=None, cell_direction=None):
        self.node_type = node_type
        self.value = value
        self.cell_direction = cell_direction
class CircuitGraph:
    def __init__(self, node_list=None, connection=None):
        self.node_list = node_list if node_list else []
        self.connection = connection if connection else {}
        self.variable_list = [TreeNode(f"v_{i}") for i in range(26)]
    def complete_connection(self):
        lst = list(self.connection.items())
        for node, edge in lst:
            for item in edge:
                if item not in self.connection.keys():
                    self.connection[item] = [node]
                elif node not in self.connection[item]:
                    self.connection[item].append(node)
    def loop_rule(self, cycle):
        _, edge_cycle = cycle
        loop_sum = None
        for u, v in edge_cycle:
            node_u = self.node_list[u]
            current = self.current_map.get((u, v))
            if node_u.node_type == "resistor" and node_u.value is not None:
                term = current * node_u.value
                loop_sum = term if loop_sum is None else loop_sum + term
            if node_u.node_type == "cell" and node_u.value is not None:
                if node_u.cell_direction == (u, v):
                    term = -node_u.value
                else:
                    term = node_u.value
                loop_sum = term if loop_sum is None else loop_sum + term
        return loop_sum
    def all_simple_cycle(self):
        cycles = []
        canonical_cycles = set()
        def find_cycles(start_node, curr_node, parent_node, path):
            for neighbor in self.connection.get(curr_node, []):
                if neighbor == parent_node:
                    continue
                if neighbor == start_node and len(path) >= 3:
                    cycle_nodes = path[:]
                    min_idx = cycle_nodes.index(min(cycle_nodes))
                    rotated = cycle_nodes[min_idx:] + cycle_nodes[:min_idx]
                    reversed_rotated = rotated[:1] + list(reversed(rotated[1:]))
                    canonical = tuple(min(rotated, reversed_rotated))
                    if canonical not in canonical_cycles:
                        canonical_cycles.add(canonical)
                        cycle_edges = [
                            (cycle_nodes[i], cycle_nodes[(i + 1) % len(cycle_nodes)])
                            for i in range(len(cycle_nodes))
                        ]
                        cycles.append((cycle_nodes, cycle_edges))
                elif neighbor not in path and neighbor > start_node:
                    find_cycles(start_node, neighbor, curr_node, path + [neighbor])
        num_nodes = len(self.node_list) if self.node_list else len(self.connection)
        for node in range(num_nodes):
            find_cycles(node, node, None, [node])
        return cycles
    def current_direction_map(self):
        direction_map = {}
        start_node = 0
        first_neighbor = self.connection[start_node][0]
        v0 = self.variable_list.pop(0)
        direction_map[(start_node, first_neighbor)] = v0
        direction_map[(first_neighbor, start_node)] = -v0
        while True:
            progress = False
            for node in range(len(self.node_list)):
                neighbors = self.connection[node]
                unassigned = [nbr for nbr in neighbors if (node, nbr) not in direction_map]
                if len(unassigned) == 1:
                    last_nbr = unassigned[0]
                    total_in = None
                    for nbr in neighbors:
                        if (nbr, node) in direction_map:
                            inc = direction_map[(nbr, node)]
                            total_in = inc if total_in is None else total_in + inc

                    direction_map[(node, last_nbr)] = total_in
                    direction_map[(last_nbr, node)] = -total_in
                    progress = True
            if progress:
                continue
            for node in range(len(self.node_list)):
                neighbors = self.connection[node]
                unassigned = [nbr for nbr in neighbors if (node, nbr) not in direction_map]
                has_known_in = any((nbr, node) in direction_map for nbr in neighbors)
                if len(unassigned) > 1 and has_known_in:
                    var = self.variable_list.pop(0)
                    target = unassigned[0]
                    direction_map[(node, target)] = var
                    direction_map[(target, node)] = -var
                    progress = True
                    break
            if not progress:
                break
        return direction_map
def find_resistance(circuit, start, end):
    if start not in circuit.connection.keys():
        circuit.connection[start] = []
    circuit.connection[start].append(end)
    circuit.node_list.append(Node("cell", TreeNode("d_1"), (start, end)))
    circuit.complete_connection()
    circuit.current_map = circuit.current_direction_map()
    cycles = circuit.all_simple_cycle()
    eq_list = []
    for cycle in cycles:
        eq = circuit.loop_rule(cycle)
        eq_list.append(expand(eq))
    eq_list = operation("f_and", [TreeNode("f_eq", [item, TreeNode("d_0")]) for item in eq_list])
    eq_list = simplify(fraction(simplify(eq_list)))
    eq_list = linear_solve(eq_list)
    var = vlist(circuit.current_map[(start, end)])[0]
    result = None
    if eq_list.name == "f_and":
        for child in eq_list.children:
            if [var] == vlist(child):
                result = inverse(child.children[0], var)
    else:
        if [var] == vlist(child):
            result = inverse(eq_list.children[0], var)
    if result is None:
        return None
    return TreeNode("d_1")/replace(circuit.current_map[(start, end)], tree_form(var), result)
