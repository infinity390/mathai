from .linear import linear_solve
from .expand import expand
from .simplify import simplify
from .diff import diff
from .inverse import inverse
from .base import *
import math
from .factor import factor2
from .tool import poly, enclose_const, longdiv
def _apart(eq, v=None):
    if v is None:
        if len(vlist(eq)) == 0:
            return eq
        v = vlist(eq)[0]
    origv = vlist(eq)
    if eq.name != "f_mul":
        return eq
    if any(contain2(eq, "f_"+item) for item in "arctan sin cos tan log".split(" ")):
        return eq
    def exclude(eq):
        if eq.name == "f_pow" and frac(eq.children[1]) is not None and frac(eq.children[1]).denominator != 1:
            return False
        if any(not exclude(child) for child in eq.children):
            return False
        return True
    if not exclude(eq):
        return eq
    def countfac(lst, eq):
        count=0
        for item in lst:
            if simplify(expand(simplify(eq - item))) == tree_form("d_0"):
                count += 1
        return tree_form("d_"+str(count))
    alloclst = []
    for i in range(0,26):
        if "v_"+str(i) not in vlist(eq):
            alloclst.append(tree_form("v_"+str(i)))
    nn, d = num_dem(eq)
    s = []
    facd = [simplify(x) for x in factor_generation(simplify(d))]
    facd2 = remove_duplicates_custom(facd, lambda m, n: simplify(expand(simplify(m-n))) == tree_form("d_0"))
    if len(facd2) == 1:
        return eq
    x = tree_form(v)
    num = []
    dem = []
    for item in facd2:
        g = countfac(facd, item)
        for n in range(int(g.name[2:])):
            n = n+1
            if n > 3:
                return eq
            n = tree_form("d_"+str(n))
            l = len(poly(item, v))
            if l == 3:
                a = alloclst.pop(0)
                b = alloclst.pop(0)
                if n == tree_form("d_1"):
                    num.append(a*x+ b)
                    dem.append(item)
                    s.append((a*x+ b)/item)
                else:
                    num.append(a*x+ b)
                    dem.append(item**n)
                    s.append((a*x+ b)/item**n)
            elif l == 2:
                a = alloclst.pop(0)
                if n == tree_form("d_1"):
                    num.append(a)
                    dem.append(item)
                    s.append(a/item)
                else:
                    num.append(a)
                    dem.append(item**n)
                    s.append(a/item**n)
            else:
                return eq
    final3 = summation(s)
    eq2 = simplify(nn*product(dem)/d)
    final2 = []
    for i in range(len(num)):
        final2.append(product([dem[k] for k in range(len(dem)) if i != k])*num[i])
    final = summation(final2)
    s = simplify(TreeNode("f_eq", [final-eq2, tree_form("d_0")]))
    lst = poly(s.children[0], v)
    lst = [simplify(TreeNode("f_eq", [item, tree_form("d_0")])) for item in lst if "v_" in str_form(item)]
    lst2 = []
    for item in lst:
        lst2+=vlist(item)
    origv = list(set(lst2)-set(origv))
    out = linear_solve(simplify(TreeNode("f_and", lst)))
    vr = set(origv)-set(vlist(out))
    for item in out.children:
        vr2 = tree_form(list(set(vlist(item))-vr)[0])
        final3 = replace(final3, vr2, simplify(replace(item.children[0], vr2, tree_form("d_0"))))
    final4 = simplify(final3)
    return final4
def apart2(eq):
    if eq.name == "f_mul":
        a, b = num_dem(eq)
        tmp = longdiv(a, b, 2, 1)
        if tmp is not None:
            return simplify(tmp[0]+tmp[1]/b)
    return TreeNode(eq.name, [apart2(child) for child in eq.children])
def apart(eq):
    eq = factor2(simplify(eq))
    eq, fx = enclose_const(eq)
    def helper(eq):
        eq2 = _apart(eq)
        if eq != eq2:
            return eq2
        return TreeNode(eq.name, [helper(child) for child in eq.children])
    eq = helper(eq)
    eq = fx(eq)
    return eq
