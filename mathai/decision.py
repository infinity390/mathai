import math
from .inverse import inverse, inverse2
from .integrate import integrate_full
from .ode import diffsolve as ode_solve
from .parser import parse
from .simplify import simplify, log0
from .base import *
from .diff import diff
from .trig import trig0, trig1, zu_simplify
from .univariate_inequality import simple_wavycurvy, wavycurvy, prepare, absolute, handle_sqrt, eq2range, domain, Range
from .fraction import fraction
from .expand import expand
from .logic import logic0, set_sub, truth_gen, solve_logically
from .factor import factor2, factor
from .limit import limit1, limit5
from .linear import linear_solve
def two_eq_handle2(eq):
    eq = flatten_tree(eq)
    orig = eq
    if eq.name != "f_and":
        return orig
    vars_ = vlist(eq)
    if len(vars_) < 2 or len(eq.children) < 2:
        return orig
    eq = simplify(eq)
    n = len(eq.children)
    for i in range(n):
        for j in range(i + 1, n):
            a = copy.deepcopy(eq.children[i])
            b = copy.deepcopy(eq.children[j])
            if a.name != "f_eq" or b.name != "f_eq":
                continue
            for v in vars_:
                inv = inverse2(
                    copy.deepcopy(a),
                    v
                )
                if inv is None:
                    continue
                branches = (
                    inv.children
                    if inv.name == "f_or"
                    else [inv]
                )
                out_branches = []
                for branch in branches:
                    substitutions = []
                    def collect(node):
                        if node.name == "f_eq":
                            lhs = node.children[0]
                            rhs = node.children[1]
                            if lhs == tree_form(v):
                                substitutions.append((lhs, rhs))
                            elif rhs == tree_form(v):
                                substitutions.append((rhs, lhs))
                        elif node.name == "f_and":
                            for child in node.children:
                                collect(child)
                    collect(branch)
                    if substitutions == []:
                        continue
                    reduced = copy.deepcopy(b.children[0])
                    for lhs, rhs in substitutions:
                        reduced = replace(
                            reduced,
                            lhs,
                            rhs
                        )
                    reduced = simplify(
                        zu_simplify(reduced)
                    )
                    new_eq = TreeNode(
                        "f_eq",
                        [
                            reduced,
                            tree_form("d_0")
                        ]
                    )
                    if branch.name == "f_and":
                        pair = TreeNode(
                            "f_and",
                            branch.children + [new_eq]
                        )
                    else:
                        pair = TreeNode(
                            "f_and",
                            [
                                branch,
                                new_eq
                            ]
                        )
                    out_branches.append(pair)
                if out_branches == []:
                    continue
                result = (
                    out_branches[0]
                    if len(out_branches) == 1
                    else TreeNode(
                        "f_or",
                        out_branches
                    )
                )
                remaining = (
                    eq.children[:i]
                    + eq.children[i+1:j]
                    + eq.children[j+1:]
                )
                if remaining:
                    result = TreeNode(
                        "f_and",
                        [result] + remaining
                    )
                return flatten_tree(
                    expand(result, "f_or", "f_and")
                )
    return orig
def extract(eq):
    out = []
    if eq.name in ["f_sin", "f_cos"]:
        out.append(eq)
    for child in eq.children:
        out += extract(child)
    return list(set(out))
def trig_inv_h(eq):
    if eq.name == "f_eq" and eq.children[0].name == "f_add":
        a = extract(eq)
        if a != []:
            b = inverse(copy.deepcopy(eq.children[0]), str_form(a[0]))
            if len(a) == 1:
                a = a[0]
                if a.name in ["f_sin", "f_cos"] and "v_" not in str_form(b):
                    v = tree_form(vlist(a.children[0])[0])
                    return TreeNode("f_zu", [-a.children[0]+b.fx(f"arc{a.name[2:]}") + parse("2*pi*k"), v, parse("k")]) |\
                           TreeNode("f_zu", [parse("pi")-a.children[0]-b.fx(f"arc{a.name[2:]}") + parse("2*pi*k"), v, parse("k")])
            elif len(a) == 2:
                a = a[0]
                if a.name in ["f_sin", "f_cos"] and b.name in ["f_sin", "f_cos"]:
                    if a.name == b.name:
                        if a.name == "f_sin":
                            v = tree_form(vlist(a.children[0])[0])
                            return TreeNode("f_zu", [-a.children[0] + b.children[0] + parse("2*pi*k"), v, parse("k")]) |\
                                   TreeNode("f_zu", [-a.children[0] + parse("pi") - b.children[0] + parse("2*pi*k"), v, parse("k")])
    if eq.name == "f_and" and len(eq.children) == 2 and contain2(eq, "f_zu"):
        a,b = eq.children
        if b.name == "f_range":
            a, b = b, a
        if a.name == "f_range":
            a = eq2range(a)
            if a.variable == b.children[0]:
                pass
            elif vlist(b) == [a.variable.name]:
                v = a.variable
                a = a.equation()
                a = simplify(replace(a, v, b.children[1]))
                a = simple_wavycurvy(a)
                a = eq2range(a)
            if not isinstance(a, Range) or a.r[0] or a.r[-1]:
                return eq
            lst = []
            for i in range(2,len(a.r)-1,2):
                if isinstance(a.r[i], bool) and a.r[i]:
                    v = trig0(b.children[0])
                    L, U = a.r[i-1], a.r[i+1]
                    out_a, out_b = None, None
                    if b.name == "f_zu":
                        x = str_form(b.children[2])
                        f = inverse(copy.deepcopy(v),x)
                        f = simplify(f)
                        inc = diff(copy.deepcopy(f),b.children[1].name)
                        out_a = replace(f, b.children[1], L).fx("floor") + tree_form("d_1")
                        out_b = replace(f, b.children[1], U).fx("ceil") - tree_form("d_1")
                        if frac(inc) is not None:
                            if frac(inc) < 0:
                                out_a, out_b = out_b, out_a                                
                    else:
                        return eq
                    out_a = simplify(out_a)
                    out_b = simplify(out_b)
                    if out_a.name.startswith("d_"):
                        out_a = int(out_a.name[2:])
                    else:
                        return eq
                    if out_b.name.startswith("d_"):
                        out_b  = int(out_b.name[2:])
                    else:
                        return eq
                    lst += list(range(out_a, out_b+1))
                    lst = list(set(lst))
            for i in range(2):
                for item in [a.p, a.z][i]:
                    v = trig0(b.children[0])
                    L = item
                    out_a = None
                    if b.name == "f_zu":
                        f = inverse(copy.deepcopy(v),str_form(b.children[2]))
                        out_a = replace(f, b.children[1], L)
                    else:
                        return eq
                    out_a = simplify(fraction(out_a))
                    if out_a.name.startswith("d_"):
                        out_a = int(out_a.name[2:])
                    elif frac(out_a) is not None:
                        continue
                    else:
                        return eq
                    if i == 0:
                        if out_a not in lst:
                            lst.append(out_a)
                    else:
                        if out_a in lst:
                            lst.remove(out_a)
            lst2 = TreeNode("f_or", [])
            for item in lst:
                if b.name == "f_zu":
                    out = inverse(copy.deepcopy(b.children[0]),str_form(b.children[1]))
                    out = replace(out, b.children[2], tree_form(f"d_{item}"))
                    out = TreeNode("f_eq", [a.variable-out, tree_form("d_0")])
                    lst2.children.append(out)
                else:
                    return eq
            if lst2.children == []:
                return tree_form("s_false")
            if len(lst2.children) == 1:
                return lst2.children[0]
            return lst2
    return eq
def trig_inv(eq):
    return transform_dfs(eq, trig_inv_h)
def trig7(equation):
    eq = copy.deepcopy(equation)
    if contain2(eq, "f_sin") or contain2(eq, "f_cos"):
        eq = simplify(eq)
        eq = trig_inv(eq)
        eq = simple_wavycurvy(eq)
        eq = trig0(eq)
        eq = simplify(eq)
        eq = expand(eq, "f_or", "f_and")
        eq = simplify(eq)
        eq = trig_inv(eq)
        eq = simplify(eq)
        if not contain2(eq, "f_zu"):
            eq = simple_wavycurvy(eq)
            if eq.name == "f_range":
                return eq
        else:
            return equation
    return eq
def two_eq_handle(eq):
    eq2 = trig0(eq)
    eq = flatten_tree(eq)
    orig = eq
    if eq.name == "f_and":
        out = vlist(eq)
        eq = simplify(eq)
        if out == []:
            pass
        elif all(item.name == "f_eq" for item in eq.children) and all(all("v_" not in str_form(diff(item.children[0],v)) for v in out) for item in eq.children):
            eq = linear_solve(eq)
            return eq
        elif len(eq.children) >= 2 and len(out) >= 2:
            for i in range(len(eq.children)):
                for j in range(len(eq.children)):
                    if i >= j:
                        continue
                    a, b = copy.deepcopy((eq.children[i], eq.children[j]))
                    if a.name != "f_eq" or b.name != "f_eq":
                        continue
                    a_expr = a.children[0]
                    b_expr = b.children[0]
                    result = tree_form("s_false")
                    for v1, v2 in [(out[0], out[1]), (out[1], out[0])]:
                        inv = inverse(copy.deepcopy(a_expr), v1)
                        if inv is None:
                            continue
                        reduced = replace(copy.deepcopy(b_expr), tree_form(v1), inv)
                        reduced = simplify(reduced)
                        pair = (
                            TreeNode("f_eq", [tree_form(v1), inv]) &
                            TreeNode("f_eq", [reduced, tree_form("d_0")])
                        )
                        if result.name == "s_false":
                            result = pair
                        else:
                            result = result | pair
                    tmp = TreeNode(eq.name, eq.children[:i]+eq.children[i+1:j]+eq.children[j+1:])
                    if len(tmp.children) == 1:
                        tmp = tmp.children[0]
                    if len(tmp.children) == 0:
                        return flatten_tree(expand(result, "f_or", "f_and"))
                    return flatten_tree(expand(result, "f_or", "f_and")&tmp)
    return orig
def god(string):
    print(f"? {string}")
    print("thinking...")
    eq = None
    eq = parse(string)
    log = [eq]
    if "f_limit" in str_form(eq):
        eq = limit1(limit5(eq))
    elif all(not contain2(eq, "f_"+item) for item in "dif add mul abs pow dif integrate arcsin sin cos log limit eq lt le ge gt".split(" ")) and\
       any(contain2(eq, "f_"+item) for item in "and or not imply equiv".split(" ")):
        eq = solve_logically(truth_gen(simplify(set_sub(eq))))
        print(f"=> {eq}")
        print()
        return eq
    elif not (eq.name == "f_and" and len(vlist(eq)) > 1) and any(contain2(eq, "f_"+item) for item in "eq lt le ge gt".split(" ")) and all(not contain2(eq, "f_"+item) for item in "limit dif integrate".split(" ")):
        lst = [simplify, log0, simplify, lambda x: dowhile(x, absolute), lambda x: dowhile(x, lambda y: simplify(expand(y))), lambda x: dowhile(x, lambda y: simplify(fraction(y))), logic0, simple_wavycurvy, simple_wavycurvy]
        fx2 = lambda x: dowhile(x, lambda y: simplify(fraction(y)))
        fx3 = lambda x: dowhile(x, trig1)
        lst2 = [simplify, trig0, lambda x: dowhile(x, lambda y: fx2(fx3(y))), logic0]
        sel = lst.copy()
        if any(contain2(eq, "f_"+item) for item in "sin cos tan cosec sec cot".split(" ")) or\
           len(vlist(eq)) > 1:
            sel = lst2
        for item in sel:
            eq = item(eq)
            if eq not in log:
                log.append(eq)
                print(eq)
        # eq = trig7(eq)
        print(f"=> {eq}")
        return eq
    elif "f_dif" in str_form(eq) or "f_integrate" in str_form(eq):
        if "f_dif" in str_form(eq) and "f_integrate" not in str_form(eq):
            eq = simplify(ode_solve(simplify(eq)))
            log.append(eq)
        if "f_integrate" in str_form(eq):
            eq = integrate_full(eq)
        eq = simplify(expand(simplify(eq)))
        print(f"=> {eq}")
        print()
        return eq
    if any("f_"+item in str_form(eq) for item in "eq lt le ge gt".split(" ")):
        def fun(eq):
            print(eq)
            eq = simple_wavycurvy(eq, True)
            eq = zu_simplify(eq)
            eq = transform_dfs(eq, two_eq_handle)
            fx = lambda x: logic0(simplify(factor2(dowhile(x, lambda y: simplify(fraction(y)))), True, True))
            eq = fx(eq)
            eq = flatten_tree(eq)
            eq = expand(eq, "f_or", "f_and")
            return eq
        eq = dowhile(eq, fun)
        if eq.name in ["f_and", "f_or"]:
            eq = TreeNode(eq.name, list(set(eq.children)))
            if len(eq.children) == 1:
                eq = eq.children[0]
    eq = simplify(expand(simplify(fraction(simplify(eq)))))
    print(f"=> {eq}")
    print()
    return eq
