from .simplify import simplify
from .base import *
from .parser import parse
from .formula_applier import formula_list_applier

diff2_s = """pdif(e^a,x) e^a*pdif(a,x) [] x _ _ _
pdif(a^b,x) b*(a^(b-1))*pdif(a,x)+(a^b)*log(a)*pdif(b,x) [] x _ _ _
pdif(sin(a),x) cos(a)*pdif(a,x) [] x _ _ _
pdif(cos(a),x) -sin(a)*pdif(a,x) [] x _ _ _
pdif(arcsin(a),x) (1/sqrt(1-a^2))*pdif(a,x) [] x _ _ _
pdif(arccos(a),x) (-1/sqrt(1-a^2))*pdif(a,x) [] x _ _ _
pdif(arctan(a),x) (1/(1+a^2))*pdif(a,x) [] x _ _ _
pdif(k,x) 0 [] x k _ _
pdif(x,x) 1 [] x _ _ _
pdif(product(a,b),x) pdif(a,x)*b+a*pdif(b,x) [] x _ _ _
pdif(sum(a,b),x) pdif(a,x)+pdif(b,x) [] x _ _ _
pdif(product(k,a),x) k*pdif(a,x) [] x k _ _"""

diff2 = lambda x: formula_list_applier(x, diff2_s)
'''
def diff(equation, var=None):
    var = var if var else "v_0"
    out = diff2(simplify(TreeNode("f_pdif", [equation, tree_form(var)])))
    return out
'''
def diff(equation, var="v_0"):
    def diffeq_iterative(root_eq):
        stack = [(root_eq, False)]
        results = {}
        while stack:
            eq, processed = stack.pop()
            if eq in results:
                continue
            if not processed:
                eq_simplified = simplify(eq)
                if "v_" not in str_form(eq_simplified):
                    results[eq] = tree_form("d_0")
                    continue
                stack.append((eq, True))
                if eq.name in ("f_add", "f_mul"):
                    for child in eq.children:
                        if child not in results:
                            stack.append((child, False))
                elif eq.name in ("f_abs", "f_tan", "f_log", "f_arcsin", "f_arccos", "f_arctan", "f_sin", "f_cos"):
                    child = eq.children[0]
                    if child not in results:
                        stack.append((child, False))
                elif eq.name == "f_pow":
                    for child in eq.children:
                        if child not in results:
                            stack.append((child, False))
            else:
                if "v_" not in str_form(eq):
                    results[eq] = tree_form("d_0")
                    continue
                if eq.name == "f_add":
                    add_res = tree_form("d_0")
                    for child in eq.children:
                        add_res = add_res + results.get(child, tree_form("d_0"))
                    results[eq] = add_res
                elif eq.name == "f_abs":
                    u = eq.children[0]
                    du = results.get(u, tree_form("d_0"))
                    results[eq] = du * u / eq
                elif eq.name == "f_pow" and eq.children[0].name == "s_e":
                    u = eq.children[1]
                    du = results.get(u, tree_form("d_0"))
                    results[eq] = du * eq
                elif eq.name == "f_tan":
                    u = eq.children[0]
                    du = results.get(u, tree_form("d_0"))
                    cos_u = u.fx("cos")
                    results[eq] = du / (cos_u * cos_u)
                elif eq.name == "f_log":
                    u = eq.children[0]
                    du = results.get(u, tree_form("d_0"))
                    results[eq] = du * (tree_form("d_1") / u)
                elif eq.name == "f_arcsin":
                    u = eq.children[0]
                    du = results.get(u, tree_form("d_0"))
                    one = tree_form("d_1")
                    half = tree_form("d_2") ** tree_form("d_-1")
                    results[eq] = du / ((one - u * u) ** half)
                elif eq.name == "f_arccos":
                    u = eq.children[0]
                    du = results.get(u, tree_form("d_0"))
                    one = tree_form("d_1")
                    half = tree_form("d_2") ** tree_form("d_-1")
                    results[eq] = tree_form("d_-1") * du / ((one - u * u) ** half)
                elif eq.name == "f_arctan":
                    u = eq.children[0]
                    du = results.get(u, tree_form("d_0"))
                    results[eq] = du / (tree_form("d_1") + u * u)
                elif eq.name == "f_pow" and "v_" in str_form(eq.children[1]):
                    u, v = eq.children
                    du = results.get(u, tree_form("d_0"))
                    dv = results.get(v, tree_form("d_0"))
                    term1 = (v / u) * du
                    term2 = u.fx("log") * dv
                    results[eq] = (u ** v) * (term1 + term2)
                elif eq.name == "f_mul":
                    add_res = tree_form("d_0")
                    n_children = len(eq.children)
                    for i in range(n_children):
                        target_child = eq.children[i]
                        d_target = results.get(target_child, tree_form("d_0"))
                        other_terms = [eq.children[j] for j in range(n_children) if j != i]
                        if len(other_terms) == 1:
                            other_prod = other_terms[0]
                        else:
                            other_prod = TreeNode("f_mul", other_terms)
                        add_res = add_res + (d_target * other_prod)
                    results[eq] = add_res
                elif eq.name == "f_sin":
                    u = eq.children[0]
                    du = results.get(u, tree_form("d_0"))
                    results[eq] = du * u.fx("cos")
                elif eq.name == "f_cos":
                    u = eq.children[0]
                    du = results.get(u, tree_form("d_0"))
                    results[eq] = tree_form("d_-1") * du * u.fx("sin")
                elif eq.name[:2] == "v_":
                    results[eq] = TreeNode("f_dif", [eq])
                elif eq.name == "f_pow" and "v_" not in str_form(eq.children[1]):
                    base, power = eq.children
                    dbase = results.get(base, tree_form("d_0"))
                    power_minus_1 = power - tree_form("d_1")
                    results[eq] = power * (base ** power_minus_1) * dbase
                else:
                    results[eq] = TreeNode("f_dif", [eq, tree_form(var)])
        return results.get(root_eq, tree_form("d_0"))
    def helper2_iterative(root_eq, target_var):
        stack = [(root_eq, False)]
        results = {}
        while stack:
            eq, processed = stack.pop()
            if eq in results:
                continue
            if not processed:
                stack.append((eq, True))
                for child in eq.children:
                    if child not in results:
                        stack.append((child, False))
            else:
                if eq.name == "f_dif":
                    if eq.children[0].name == target_var:
                        results[eq] = tree_form("d_1")
                    elif not contain(eq.children[0], target_var):
                        results[eq] = tree_form("d_0")
                    else:
                        results[eq] = eq
                else:
                    new_children = [results.get(child, child) for child in eq.children]
                    results[eq] = TreeNode(eq.name, new_children)
        return results.get(root_eq, root_eq)
    def calc_iterative(root_eq):
        stack = [(root_eq, False)]
        results = {}
        while stack:
            eq, processed = stack.pop()
            if eq in results:
                continue
            if not processed:
                stack.append((eq, True))
                for child in eq.children:
                    if child not in results:
                        stack.append((child, False))
            else:
                if eq.name == "f_dif":
                    results[eq] = diffeq_iterative(eq.children[0])
                else:
                    new_children = [results.get(child, child) for child in eq.children]
                    results[eq] = TreeNode(eq.name, new_children)
        return results.get(root_eq, root_eq)
    if var is None:
        return simplify(calc_iterative(equation))
    equation = diffeq_iterative(equation)
    equation = helper2_iterative(equation, var)
    return simplify(equation)
