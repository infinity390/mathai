import math
from .inverse import inverse, inverse2
from .integrate import integrate_full, def_integrate_formula
from .ode import diffsolve as ode_solve
from .parser import parse
from .simplify import simplify, log0
from .base import *
from .diff import diff, diff2
from .trig import trig0, trig1, zu_simplify
from .univariate_inequality import simple_wavycurvy, wavycurvy, prepare, absolute, handle_sqrt, eq2range, domain, Range
from .fraction import fraction
from .expand import expand
from .logic import logic0, set_sub, truth_gen, solve_logically
from .factor import factor2, factor1, factor0
from .limit import limit1, limit5
from .linear import linear_solve
from .matrix import matrix_solve, matrix_formula

def vlist_2(eq):
    out = []
    if eq.name[2:] in "det adj dim".split(" ") and eq.children[0].name[:2] == "v_":
        return [eq]
    if eq.name[:2] == "v_":
        return [eq]
    for child in eq.children:
        out += vlist_2(child)
    return list(set(out))
def convert_single_solution(eq):
    if eq.name == "f_range":
        out = eq2range(eq)
        if out.r == [False] and len(out.p) == 1:
            return TreeNode("f_eq", [out.variable - out.p[0], TreeNode("d_0")])
    return eq
def solve_subs(q):
    solution = {}
    orig = copy.deepcopy(q)
    if q.name != "f_and":
        q = TreeNode("f_and", [q])
    lst = q.children
    if not all(item.name == "f_eq" for item in lst):
        return orig
    q = simplify(q)
    done = True
    while done:
        done = False
        for i in range(len(q.children)):
            item = q.children[i]
            for key, item2 in solution.items():
                item = replace(item, tree_form(key), item2)
            item = fraction(expand(trig0(simplify(item))))
            q.children[i] = item
            vars_in_item = vlist_2(item)
            if len(vars_in_item) == 1:
                target_var = vars_in_item[0]
                tmp = inverse(item.children[0], str_form(target_var))
                if tmp is not None:
                    solution[str_form(target_var)] = tmp
                    done = True
                    break
    if len(solution.keys()) == 0:
        return orig
    return operation("f_and", [item for item in lst if all(not contain(item, tree_form(key)) for key in solution.keys())] + [TreeNode("f_eq", [tree_form(key), item]) for key, item in solution.items()])

def god(string, debug=True):
    if debug:
        print(f"? {string}")
        print("thinking...")
    eq = None
    eq = parse(string)
    log = [eq]
    if "f_pdif" in str_form(eq):
        eq = diff2(eq)
    if "f_limit" in str_form(eq):
        eq = limit1(limit5(eq))
    if any(contain2(eq, "f_"+item) for item in "adj det list transpose".split(" ")):
           eq = matrix_formula(eq)
           if debug:
               print(eq)
           eq = matrix_solve(eq)
           if debug:
               print(eq)
           eq = solve_subs(eq)
           if debug:
               print(f"=> {eq}")
               print()
           return eq
    elif all(not contain2(eq, "f_"+item) for item in "dif add mul abs pow dif integrate arcsin sin cos log limit eq lt le ge gt".split(" ")) and\
       any(contain2(eq, "f_"+item) for item in "and or not imply equiv".split(" ")):
        eq = solve_logically(truth_gen(simplify(set_sub(eq))))
        if debug:
            print(f"=> {eq}")
            print()
        return eq
    elif not (eq.name == "f_and" and len(vlist(eq)) > 1) and any(contain2(eq, "f_"+item) for item in "eq lt le ge gt".split(" ")) and all(not contain2(eq, "f_"+item) for item in "limit dif integrate".split(" ")):
        lst = [simplify, log0, simplify, lambda x: dowhile(x, absolute), lambda x: dowhile(x, lambda y: simplify(expand(y))), lambda x: dowhile(x, lambda y: simplify(fraction(y))), logic0, simple_wavycurvy, simple_wavycurvy]
        fx2 = lambda x: dowhile(x, lambda y: simplify(fraction(y)))
        fx3 = lambda x: dowhile(x, trig1)
        lst2 = [simplify, trig0, lambda x: dowhile(x, lambda y: fx2(fx3(y))), solve_subs, logic0]
        sel = lst.copy()
        if any(contain2(eq, "f_"+item) for item in "sin cos tan cosec sec cot".split(" ")) or\
           len(vlist(eq)) > 1:
            sel = lst2
        for item in sel:
            eq = item(eq)
            if eq not in log:
                log.append(eq)
                if debug:
                    print(eq)
        if debug:
            print(f"=> {eq}")
            print()
        return eq
    elif "f_dif" in str_form(eq) or "f_integrate" in str_form(eq):
        if "f_dif" in str_form(eq) and "f_integrate" not in str_form(eq):
            eq = simplify(ode_solve(simplify(eq)))
            log.append(eq)
        if "f_integrate" in str_form(eq):
            eq = def_integrate_formula(eq)
            eq = integrate_full(eq, debug)
            eq = limit5(eq)
            eq = limit1(eq)
        eq = simplify(expand(simplify(eq)))
        if contain2(eq, "f_integrate"):
            return None
        if debug:
            print(f"=> {eq}")
            print()
        return eq
    if any("f_"+item in str_form(eq) for item in "eq lt le ge gt".split(" ")):
        eq = simple_wavycurvy(eq)
        eq = transform_dfs(eq, convert_single_solution)
        out = linear_solve(eq)
        if out is not None:
            eq = out
        if debug:
            print(eq)
        eq = solve_subs(eq)
        out = linear_solve(eq)
        if out is not None:
            eq = out
        eq = simple_wavycurvy(eq)
    eq = simplify(expand(simplify(fraction(simplify(eq)))))
    if debug:
        print(f"=> {eq}")
        print()
    return eq
