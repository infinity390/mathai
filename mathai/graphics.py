from .base import *
from .fraction import fraction
from .simplify import simplify
from .trig import trig0
import itertools
from .inverse import inverse
from .expand import expand
from .parser import parse
def solve_graphics(Ax, Ay, Az, Bx, By, Bz, BAx, BAy, BAz, phi, theta, fvl, tvl, length):
    eq1 = TreeNode("f_eq", [TreeNode("v_6"), TreeNode("v_3") - TreeNode("v_0")])
    eq2 = TreeNode("f_eq", [TreeNode("v_7"), TreeNode("v_4") - TreeNode("v_1")])
    eq3 = TreeNode("f_eq", [TreeNode("v_8"), TreeNode("v_5") - TreeNode("v_2")])
    eq4 = TreeNode("f_eq", [TreeNode("v_6"), TreeNode("v_9").fx("sin") * TreeNode("v_13")])
    eq5 = TreeNode("f_eq", [TreeNode("v_7"), TreeNode("v_10").fx("sin") * TreeNode("v_13")])
    eq6 = TreeNode("f_eq", [TreeNode("v_8"), (TreeNode("d_1") - TreeNode("v_9").fx("sin")**2 - TreeNode("v_10").fx("sin")**2).fx("sqrt") * TreeNode("v_13")])
    eq7 = TreeNode("f_eq", [TreeNode("v_12")**2, (TreeNode("v_3") - TreeNode("v_0"))**2 + (TreeNode("v_5") - TreeNode("v_2"))**2])
    eq8 = TreeNode("f_eq", [TreeNode("v_11")**2, (TreeNode("v_4") - TreeNode("v_1"))**2 + (TreeNode("v_5") - TreeNode("v_2"))**2])
    q = operation("f_and", [eq1, eq2, eq3, eq4, eq5, eq6, eq7, eq8])
    lst = [Ax, Ay, Az, Bx, By, Bz, BAx, BAy, BAz, phi, theta, fvl, tvl, length]
    name = "Ax Ay Az Bx By Bz Bx-Ax By-Ay Bz-Az inclination_with_VP inclination_with_HP front_view_length top_view_length line_length".split(" ")
    solution = {}
    for index, item in enumerate(lst):
        if item is not None:
            solution[f"v_{index}"] = item
    q = simplify(q)
    done = True
    while done:
        done = False
        for i in range(len(q.children)):
            item = q.children[i]
            for key, item2 in solution.items():
                item = replace(item, TreeNode(key), item2)
            item = fraction(expand(trig0(simplify(item))))
            q.children[i] = item
            vars_in_item = vlist(item)
            if len(vars_in_item) == 1:
                target_var = vars_in_item[0]
                solution[target_var] = inverse(item.children[0], target_var)
                done = True
                break
    final_solution = {}
    for i, param_name in enumerate(name):
        var_key = f"v_{i}"
        if var_key in solution:
            final_solution[param_name] = simplify(expand(solution[var_key]))
    return final_solution
def solve_graphics_string(s):
    s_parsed = [None if item == "None" else parse(item) for item in s.split()]
    for key, item in solve_graphics(*s_parsed).items():
        print(f"{key} : {item}")
