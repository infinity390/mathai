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
    solution = solve_graphics(*s_parsed)
    for key, item in solution.items():
        print(f"{key} : {item}")
    return solution
def draw_graphics_from_solution(solution):
    import matplotlib.pyplot as plt
    import numpy as np
    def get_val(key):
        if key in solution:
            val = solution[key]
            try:
                return float(compute(val))
            except Exception:
                try:
                    return float(str(val))
                except Exception:
                    return 0.0
        return 0.0
    Ax = get_val('Ax')
    Ay = get_val('Ay')
    Az = get_val('Az')
    Bx = get_val('Bx')
    By = get_val('By')
    Bz = get_val('Bz')
    fa_x, fa_y = Az, Ay
    fb_x, fb_y = Bz, By
    ta_x, ta_y = Az, -Ax
    tb_x, tb_y = Bz, -Bx
    fig, ax = plt.subplots(figsize=(9, 7))
    x_min = min(fa_x, fb_x, ta_x, tb_x) - 25
    x_max = max(fa_x, fb_x, ta_x, tb_x) + 25
    ax.axhline(0, color='black', linewidth=1.5, label='Reference Axis')
    ax.plot([fa_x, fb_x], [fa_y, fb_y], 'r-', linewidth=2, label="Front View (a' b')")
    ax.plot(fa_x, fa_y, 'ro', markersize=5)
    ax.plot(fb_x, fb_y, 'ro', markersize=5)
    ax.text(fa_x - 3, fa_y + 3, "a'", fontsize=11, color='red', fontweight='bold')
    ax.text(fb_x + 3, fb_y + 3, "b'", fontsize=11, color='red', fontweight='bold')
    ax.plot([ta_x, tb_x], [ta_y, tb_y], 'b-', linewidth=2, label="Top View (a b)")
    ax.plot(ta_x, ta_y, 'bo', markersize=5)
    ax.plot(tb_x, tb_y, 'bo', markersize=5)
    ax.text(ta_x - 3, ta_y - 8, "a", fontsize=11, color='blue', fontweight='bold')
    ax.text(tb_x + 3, tb_y - 8, "b", fontsize=11, color='blue', fontweight='bold')
    ax.plot([fa_x, ta_x], [fa_y, ta_y], 'k--', alpha=0.5)
    ax.plot([fb_x, tb_x], [fb_y, tb_y], 'k--', alpha=0.5)
    ax.set_aspect('equal', adjustable='datalim')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.set_xlabel('Coordinate Axis (Az / Bz)', fontsize=10)
    ax.set_ylabel('Height / Depth', fontsize=10)
    ax.set_title('Engineering Drawing: Projections of a Line', fontsize=13, fontweight='bold', pad=15)
    ax.legend(loc='upper right', framealpha=0.9)
    plt.tight_layout()
    plt.savefig('line_projections.png', dpi=300)
    plt.show()
