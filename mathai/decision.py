from .inverse import inverse2
from .integrate import integrate_full
from .ode import diffsolve as ode_solve
from .parser import parse
from .simplify import simplify, log0
from .base import *
from .diff import diff
from .trig import trig0, trig1, zu_simplify
from .univariate_inequality import simple_wavycurvy, wavycurvy, prepare, absolute, handle_sqrt, eq2range, domain
from .bivariate_inequality import solve_logically
from .fraction import fraction
from .expand import expand
from .logic import logic0, set_sub, truth_gen, distribute
from .factor import factor2, factor
from .limit import limit1, limit5
from .linear import linear_solve

def two_eq_handle(eq):

    eq = flatten_tree(eq)
    orig = eq

    if eq.name != "f_and":
        return orig

    vars_ = vlist(eq)

    if len(vars_) < 2 or len(eq.children) < 2:
        return orig

    eq = simplify(eq)

    # ============================================
    # PURE LINEAR SYSTEM
    # ============================================

    if (
        all(item.name == "f_eq" for item in eq.children)
        and
        all(
            all("v_" not in str_form(diff(item.children[0], v))
                for v in vars_)
            for item in eq.children
        )
    ):
        out = linear_solve(eq)
        if out is not None:
            return out

    # ============================================
    # GENERAL TWO-EQUATION ELIMINATION
    # ============================================

    n = len(eq.children)

    for i in range(n):

        for j in range(i + 1, n):

            a = copy.deepcopy(eq.children[i])
            b = copy.deepcopy(eq.children[j])

            if a.name != "f_eq" or b.name != "f_eq":
                continue

            a_expr = a.children[0]
            b_expr = b.children[0]

            # ------------------------------------
            # TRY EACH VARIABLE
            # ------------------------------------

            for v in vars_:

                inv = inverse2(copy.deepcopy(a), v)
                
                if inv is None:
                    continue

                branches = []

                # --------------------------------
                # NORMALIZE OR BRANCHES
                # --------------------------------

                if inv.name == "f_or":
                    branches = inv.children
                else:
                    branches = [inv]

                out = []

                # --------------------------------
                # PROCESS EACH BRANCH
                # --------------------------------

                for branch in branches:
                    if (
                        branch.name != "f_eq"
                        or branch.children[0] != tree_form(v)
                    ):
                        continue

                    replacement = branch.children[1]

                    reduced = replace(
                        copy.deepcopy(b_expr),
                        tree_form(v),
                        replacement
                    )

                    reduced = zu_simplify(reduced)

                    new_eq = TreeNode(
                        "f_eq",
                        [reduced, tree_form("d_0")]
                    )

                    pair = TreeNode(
                        "f_and",
                        [
                            branch,
                            new_eq
                        ]
                    )

                    out.append(pair)

                if out == []:
                    continue

                result = (
                    out[0]
                    if len(out) == 1
                    else TreeNode("f_or", out)
                )

                # --------------------------------
                # APPEND REMAINING EQUATIONS
                # --------------------------------

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
def god(string):
    print(f"? {string}")
    print("thinking...")
    eq = None
    eq = parse(string)
    log = [eq]
    if "f_limit" in str_form(eq):
        eq = limit1(limit5(eq))
    elif all(not contain2(eq, "f_"+item) for item in "dif add mul abs pow dif integrate arcsin sin cos log limit eq lt le ge gt".split(" ")) and\
       any(contain2(eq, "f_"+item) for item in "and or not".split(" ")):
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
        print(f"=> {eq}")
        print()
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
