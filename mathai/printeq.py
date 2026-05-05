from .base import *
from .factor import merge_sqrt
from .simplify import simplify
import copy
from fractions import Fraction
from .univariate_inequality import eq2range
def abstractexpr(eq):
    if eq.name == "f_range":
        return tree_form("v_"+str(eq2range(eq)))
    if eq.name == "f_pow":
        power = frac(eq.children[1])
        if power is not None:
            if power == Fraction(1, 2):
                return eq.children[0].fx("sqrt")
            if power == Fraction(-1, 2):
                return eq.children[0].fx("sqrt") ** -1
    if eq.name == "f_mul":
        num, deno = num_dem(eq)
        num = simplify(num, False)
        deno = simplify(deno, False)
        if deno != tree_form("d_1"):
            return TreeNode("f_div", [num, deno])
    return eq
def abstractexpr2(eq):
    eq = simplify(eq, False)
    if eq.name == "f_pow":
        n = frac(eq.children[1])
        if n is not None and n < Fraction(0):
            if n == Fraction(-1):
                return TreeNode("f_div", [tree_form("d_1"), eq.children[0]])
            else:
                return TreeNode("f_div", [tree_form("d_1"), eq.children[0]**frac_to_tree(-n)])
    return eq
def abstractexpr3(eq):
    if eq.name in ["f_mul", "f_pow"]:
        lst = factor_generation(eq)
        if eq.name == "f_mul" and any(
            frac(item) is not None and frac(item) < 0 for item in lst
        ):
            return simplify(-eq, False).fx("neg")
    return eq
def printeq_str(eq):
    if eq is None:
        return None
    eq = simplify(eq, False)
    fx = lambda x: transform_dfs(x, abstractexpr)
    fx2 = lambda y: dowhile(y, lambda x: transform_dfs(x, abstractexpr2))
    fx3 = lambda y: dowhile(y, lambda x: transform_dfs(x, abstractexpr3))
    return string_equation(str_form(fx3(fx2(fx(eq)))))
def printeq_obj(self):
    return printeq_str(self)
TreeNode.__repr__ = printeq_obj
