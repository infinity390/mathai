from .base import *
from .parser import parse
from .simplify import simplify
from .expand import expand
from .diff import diff
from .trig import trig0
from .fraction import fraction, fraction0
from .tool import poly
from .printeq import print_raw

def substitute_val(eq, val, var="v_0"):
    eq = replace(eq, tree_form(var), tree_form("d_"+str(val)))
    return eq
def subslimit(equation, var):
    equation2 = trig0(replace(equation, var, tree_form("d_0")))
    try:
        tmp = simplify(equation2)
        return simplify(expand(tmp))
    except:
        return None
def check(num, den, var, name):
    n, d = None, None
    if name == "f_limit":
        n, d = (dowhile(replace(e, tree_form(var), tree_form("d_0")), lambda x: trig0(simplify(x))) for e in (num, den))
    else:
        n, d = limit3(TreeNode("f_limitpinf", [num, tree_form(var)]), True), limit3(TreeNode("f_limitpinf", [den, tree_form(var)]), True)
    if n is None or d is None:
        return False
    if name == "f_limit" and n == 0 and d == 0: return True
    elif name == "f_limitpinf":
        if n == tree_form("s_inf") and d == tree_form("s_inf"):
            return True
        else:
            n, d = num, den
    if d != 0:
        return simplify(n/d)
    return False
def lhospital(num, den, steps,var, name):
    out = check(num, den, var, name)
    if isinstance(out, TreeNode):
        return out
    for _ in range(steps):
        num2, den2 = map(lambda e: simplify(diff(e, var)), (num, den))
        out = check(num2, den2, var, name)
        if out is True:
            num, den = num2, den2
            continue
        if out is False:
            eq2 = simplify(fraction(simplify(num/den)))
            return eq2
        return out
def lhospital2(eq, var, name):
    eq=  simplify(eq)
    if eq is None:
        return None
    if not contain(eq, tree_form(var)):
        return eq
    num, dem = [simplify(item) for item in num_dem(eq)]
    if num is None or dem is None:
        return eq
    return lhospital(num, dem, 10,var, name)
def limit0(equation):
    equation = copy.deepcopy(equation)
    limit_tags = ["f_limit", "f_limitpinf", "f_limitninf"]
    if equation.name not in limit_tags:
        return TreeNode(
            equation.name,
            [limit0(child) for child in equation.children]
        )
    expr = equation.children[0]
    wrt = equation.children[1]
    factors = factor_generation(expr)
    const_factors = []
    var_factors = []
    for f in factors:
        if contain(f, wrt):
            var_factors.append(f)
        else:
            const_factors.append(f)
    if const_factors == []:
        new_expr = expr
        const_part = tree_form("d_1")
    else:
        const_part = simplify(product(const_factors))
        new_expr = product(var_factors)
    inner_limit = TreeNode(
        equation.name,
        [
            limit0(new_expr),
            wrt
        ]
    )
    if const_factors == []:
        return inner_limit
    return simplify(const_part) * inner_limit
def limit2(eq):
    g = ["f_limit", "f_limitpinf", "f_limitninf"]
    if eq.name in g and eq.children[0].name == "f_add":
        eq = summation([TreeNode(eq.name, [child, eq.children[1]]) for child in eq.children[0].children])
    return TreeNode(eq.name, [limit2(child) for child in eq.children])
def limit1(eq):
    if eq.name in ["f_limitpinf", "f_limit"]:
        a, b = limit(eq.children[0], eq.children[1].name, eq.name)
        if b:
            return a
        else:
            return TreeNode(eq.name, [a, eq.children[1]])
    return TreeNode(eq.name, [limit1(child) for child in eq.children])
def replace_abs_var_h(eq, pos, wrt):
    if eq in pos:
        return tree_form("d_-1")
    if eq.name.startswith("v_") and (wrt is None or eq!=wrt):
        return tree_form("d_1")
    return eq
def replace_abs_var(eq, pos, wrt=None):
    return transform_dfs(eq, replace_abs_var_h, [pos, wrt])
def sep_const_h(eq, wrt):
    if eq.name == "f_pow":
        eq.children[1] = expand(eq.children[1])
        if eq.children[1].name == "f_add" and contain(eq.children[1], wrt):
            return product([eq.children[0]**item for item in eq.children[1].children])
    return eq
def sep_const(eq, wrt):
    return transform_dfs(eq, sep_const_h, [wrt])
def limit4(equation):
    if equation.name == "f_limitpinf":
        if not contain(equation, equation.children[1]):
            return equation.children[0]
        eq = equation.children[0]
        n, d = num_dem(eq)
        n, d = simplify(n), simplify(d)
        v2 = tree_form(vlist(eq)[0])
        p1 = poly(n, v2.name)
        p2 = poly(d, v2.name)
        if p1 is not None and p2 is not None and len(p1)<=len(p2) and len(p1)>1 and len(p2)>1:
            v = simplify(v2**(len(p2)-1))
            return TreeNode("f_limitpinf", [simplify(expand(n/v)/expand(d/v)), equation.children[1]])
    return equation
def limit5(eq):
    if eq.name == "f_limit" and len(eq.children) == 3:
        return TreeNode("f_limit", [replace(eq.children[0], eq.children[1], eq.children[1]+eq.children[2]), eq.children[1]])
    return TreeNode(eq.name, [limit5(child) for child in eq.children])

def is_positive(eq):
    if eq.name in ["s_pi", "s_e"]:
        return True
    out = frac(eq)
    if out is not None:
        if out >= 0:
            return True
    return False
def is_negative(eq):
    if eq.name in ["s_pi", "s_e"]:
        return False
    out = frac(eq)
    if out is not None:
        if out <= 0:
            return True
    return False
limit3 = lambda x: load_formula("limit_infinity")(x)
def solve_inf(eq):
    stack = [(eq, False)]
    result = {}
    while stack:
        node, done = stack.pop()
        if not done:
            stack.append((node, True))
            for child in reversed(node.children):
                stack.append((child, False))
            continue
        if node.name in ("s_inf", "s_-inf", "s_0/0", "s_inf/inf", "s_pi", "s_e"):
            result[node] = node
            continue
        if not node.children:
            result[node] = node
            continue
        ch = [result[c] for c in node.children]
        if any(c.name in ("s_0/0", "s_inf/inf") for c in ch):
            result[node] = tree_form("s_0/0") if any(c.name == "s_0/0" for c in ch) else tree_form("s_inf/inf")
            continue
        if node.name == "f_add":
            if any(c.name == "s_inf" for c in ch):
                if any(c.name == "s_-inf" for c in ch):
                    result[node] = tree_form("s_inf/inf")
                else:
                    result[node] = tree_form("s_inf")
                continue
            if any(c.name == "s_-inf" for c in ch):
                result[node] = tree_form("s_-inf")
                continue
            result[node] = TreeNode("f_add", ch)
            continue
        if node.name == "f_mul":
            sign = 1
            has_inf = False
            has_zero = False
            for c in ch:
                if c.name == "s_inf":
                    has_inf = True
                elif c.name == "s_-inf":
                    has_inf = True
                    sign *= -1
                elif c.name == "d_0":
                    has_zero = True
                elif c.name in ("s_pi", "s_e"):
                    pass
                elif is_negative(c):
                    sign *= -1
            if has_inf and has_zero:
                result[node] = tree_form("s_0/0")
                continue
            if has_inf:
                result[node] = tree_form("s_inf" if sign > 0 else "s_-inf")
                continue
            result[node] = TreeNode("f_mul", ch)
            continue
        if node.name == "f_div":
            a, b = ch
            if a.name in ("s_inf", "s_-inf") and b.name in ("s_inf", "s_-inf"):
                result[node] = tree_form("s_inf/inf")
                continue
            if b.name == "d_0":
                result[node] = tree_form("s_0/0") if a.name == "d_0" else tree_form("s_inf")
                continue
            if b.name in ("s_inf", "s_-inf"):
                result[node] = tree_form("d_0")
                continue
            if a.name in ("s_inf", "s_-inf"):
                result[node] = a
                continue
            result[node] = TreeNode("f_div", ch)
            continue
        if node.name == "f_pow":
            a, b = ch
            if a.name in ("s_inf", "s_-inf"):
                if b.name == "d_0":
                    result[node] = tree_form("s_inf/inf")
                    continue
                if is_positive(b):
                    result[node] = a
                    continue
                if is_negative(b):
                    result[node] = tree_form("d_0")
                    continue
            if a.name in ("s_pi", "s_e"):
                result[node] = TreeNode("f_pow", ch)
                continue
            result[node] = TreeNode("f_pow", ch)
            continue
        result[node] = TreeNode(node.name, ch)
    return result[eq]
def limit(equation, var="v_0", name = "f_limit"):
    eq2 = dowhile(replace(equation, tree_form(var), tree_form("d_0")), lambda x: trig0(simplify(x)))
    if eq2 is not None and not contain(equation, tree_form(var)):
        return eq2, True
    equation =  lhospital2(equation, var, name)
    equation = simplify(expand(simplify(equation)))
    if not contain(equation, tree_form(var)):
        return equation, True
    return equation, False
