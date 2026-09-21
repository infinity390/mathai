from .base import *
from .fraction import fraction
from .simplify import simplify
from .trig import trig0
import itertools
from .inverse import inverse
def solve_graphics(Ax, Ay, Az, Bx, By, Bz, BAx, BAy, BAz, phi, theta, fvl, length):
    eq1 = TreeNode("f_eq", [TreeNode("v_6"), TreeNode("v_3")-TreeNode("v_0")])
    eq2 = TreeNode("f_eq", [TreeNode("v_7"), TreeNode("v_4")-TreeNode("v_1")])
    eq3 = TreeNode("f_eq", [TreeNode("v_8"), TreeNode("v_5")-TreeNode("v_2")])
    eq4 = TreeNode("f_eq", [TreeNode("v_6"), TreeNode("v_9").fx("sin")*TreeNode("v_12")])
    eq5 = TreeNode("f_eq", [TreeNode("v_7"), TreeNode("v_10").fx("sin")*TreeNode("v_12")])
    eq6 = TreeNode("f_eq", [TreeNode("v_8"), (TreeNode("d_1") - TreeNode("v_9").fx("sin")**2 - TreeNode("v_10").fx("sin")**2).fx("sqrt")*TreeNode("v_12")])
    eq7 = TreeNode("f_eq", [TreeNode("v_7"), (TreeNode("v_12")**2 - TreeNode("v_11")**2).fx("sqrt")])
    q = operation("f_and", [eq1, eq2, eq3, eq4, eq5, eq6, eq7])
    lst = [Ax, Ay, Az, Bx, By, Bz, BAx, BAy, BAz, phi, theta, fvl, length]
    lst_map = {}
    for index, item in enumerate(lst):
        lst_map[index] = item
    solution = {}
    for i in range(len(lst_map.keys())):
        if lst_map[i] is not None:
            solution[f"v_{i}"] = lst_map[i]
    done = True
    q = simplify(q)
    while done:
        done = False
        for i in range(len(q.children)):
            item = q.children[i]
            for key, item2 in solution.items():
                item = replace(item, TreeNode(key), item2)
            item = fraction(trig0(simplify(item)))
            q.children[i] = item
            if len(vlist(item)) == 1:
                solution[vlist(item)[0]] = inverse(
                    item.children[0], vlist(item)[0]
                )
                done = True
                break
        if done:
            continue
    return solution
