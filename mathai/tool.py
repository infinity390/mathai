from .diff import diff
from .expand import expand
from .simplify import simplify
from .base import *
import math
def poly_div(dividend_coeffs, divisor_coeffs):
    dividend = [item.copy_tree() for item in dividend_coeffs]
    divisor = [item.copy_tree() for item in divisor_coeffs]
    while len(dividend) > 1 and simplify(dividend[0]) == 0:
        dividend.pop(0)
    while len(divisor) > 1 and simplify(divisor[0]) == 0:
        divisor.pop(0)
    if len(divisor) == 0 or simplify(divisor[0]) == 0:
        raise ValueError("Invalid divisor")
    if len(dividend) < len(divisor):
        return [tree_form("d_0")], [item.copy_tree() for item in dividend]
    deg_p = len(dividend) - 1
    deg_q = len(divisor) - 1
    deg_quot = deg_p - deg_q
    quotient = [tree_form("d_0")] * (deg_quot + 1)
    working_dividend = [item.copy_tree() for item in dividend]
    for k in range(deg_quot, -1, -1):
        while len(working_dividend) > 1 and simplify(working_dividend[0]) == 0:
            working_dividend.pop(0)
        if len(working_dividend) == 0 or simplify(working_dividend[0]) == 0:
            continue
        leading_ratio = simplify(working_dividend[0] / divisor[0])
        quotient[k] = leading_ratio
        new_dividend = []
        for i in range(max(len(working_dividend), len(divisor))):
            dividend_term = working_dividend[i] if i < len(working_dividend) else tree_form("d_0")
            divisor_term = simplify(leading_ratio * divisor[i]) if i < len(divisor) else tree_form("d_0")
            result = simplify(dividend_term - divisor_term)
            new_dividend.append(result)
        working_dividend = new_dividend
    remainder = working_dividend[-(deg_q):] if len(working_dividend) > deg_q else working_dividend
    while len(remainder) > 1 and simplify(remainder[0]) == 0:
        remainder.pop(0)
    if not remainder:
        remainder = [tree_form("d_0")]
    while len(quotient) > 1 and simplify(quotient[-1]) == 0:
        quotient.pop()
    return quotient, remainder
def unpoly(eq, var):
    eq = eq[::-1]
    eq = [simplify(item) for item in eq]
    eq2 = copy.deepcopy([eq[i]*tree_form(var)**tree_form("d_"+str(i)) if i != 0 else eq[i] for i in range(len(eq))])
    return summation(eq2)
def longdiv(p, q, p_min=0, q_min=0):
    p, q = simplify(p), simplify(q)
    var = set(vlist(p)) & set(vlist(q))
    if len(var) > 0:
        var = list(var)[0]
        p = poly(p, var)
        q = poly(q, var)
        if p is not None and q is not None and len(p)-1>=p_min and len(q)-1>=q_min and len(p)>=len(q):
            a, b = poly_div(p, q)
            return unpoly(a, var), unpoly(b, var)
    return None
def poly_simplify(eq):
    a, b = num_dem(eq)
    b = simplify(b)
    if b != 1:
        return simplify(poly_simplify(a)/poly_simplify(b))
    for var in vlist(eq):
        n = poly(eq, var, 20)
        if n is not None:
            return simplify(unpoly(n, var))
    return TreeNode(eq.name, [poly_simplify(child) for child in eq.children])
def enclose_const(eq):
    def req(eq, dic):
        for key in dic.keys():
            eq  = replace(eq, dic[key], key)
        return eq
    alloclst = []
    for i in range(0,26):
        if "v_"+str(i) not in vlist(eq):
            alloclst.append(tree_form("v_"+str(i)))
    dic = {}
    def helper(eq):
        nonlocal alloclst, dic
        if frac(eq) is not None:
            return eq
        if "v_" not in str_form(eq):
            if eq not in dic.keys():
                n = alloclst.pop(0)
                dic[eq] = n
            return dic[eq]
        else:
            if eq.name == "f_pow":
                return TreeNode(eq.name, [helper(eq.children[0]), eq.children[1]])
            return TreeNode(eq.name, [helper(child) for child in eq.children])
    eq= helper(eq)
    return eq, lambda x: req(x, dic)
def poly(eq, to_compute, m=10):
    def substitute_val(eq, val, var="v_0"):
        eq = replace(eq, tree_form(var), tree_form("d_"+str(val)))
        return eq
    def inv(eq):
        if eq.name[:2] == "f_" and eq.name[2:] in "arccos arcsin ref try integrate subs mod".split(" "):
            return False
        if eq.name[2:] in ["sin", "cos", "log"] and contain(eq.children[0], tree_form(to_compute)):
            return False
        if eq.name == "f_pow" and contain(eq, tree_form(to_compute)) and\
           (frac(eq.children[1]) is None or frac(eq.children[1]) < 0 or frac(eq.children[1]).denominator != 1):
            return False
        if eq.name == "f_abs":
            return False
        if any(not inv(child) for child in eq.children):
            return False
        return True
    if not inv(eq):
        return None
    out = []
    eq2 = eq
    for i in range(m):
        out.append(expand(simplify(eq2)))
        eq2 = diff(out[-1], to_compute)
    for i in range(len(out)-1,-1,-1):
        if out[i] == tree_form("d_0"):
            out.pop(i)
        else:
            break
    final = []
    for index, item in enumerate(out):
        final.append(substitute_val(item, 0, to_compute)/tree_form("d_"+str(math.factorial(index))))
    return [expand(simplify(item)) for item in final][::-1]
