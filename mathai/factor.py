
import math

from .base import *  # tree_form, TreeNode, str_form, factor_generation, product, summation, partitions ...
from .simplify import simplify
from .expand import expand  # noqa: F401
from .formula_compiler import formula_list_compiler

# Kept so that `from .factor import *` in other modules keeps working.
from .parser import parse  # noqa: F401
from .simplify import convert_to_basic  # noqa: F401
from .tool import poly  # noqa: F401
from .fraction import fraction


factor2 = formula_list_compiler("poly(x,a,b,c) a*(x-(-b+sqrt(b^2-4*a*c))/(2*a))*(x-(-b-sqrt(b^2-4*a*c))/(2*a)) [] _ _ b^2-4*a*c _")
factor1_s = """x^2-y^2 (x+y)*(x-y) [] _ _ _ _
x^3-y^3 (x-y)*(x^2+x*y+y^2) [] _ _ _ _
x^3+y^3 (x+y)*(x^2-x*y+y^2) [] _ _ _ _
x*y+a*y+x+a (x+a)*(y+1) [[a,1]] _ _ _ _
a*b+a*c a*(b+c) [[b,1]] _ _ _ _
a*b*c+a*b*d a*b*(c+d) [] _ _ _ _
a*x+b*x (a+b)*x [] _ _ _ _
a*x+a*y a*(x+y) [] _ _ _ _
a*c+a*d+b*c+b*d (a+b)*(c+d) [] _ _ _ _
x^2+2*a*x+a^2 (x+a)^2 [] _ _ _ _
x^2-2*a*x+a^2 (x-a)^2 [] _ _ _ _
a*b*c+a*d a*(b*c+d) [] _ _ _ _"""
factor1 = formula_list_compiler(factor1_s)

def _coeff(term):
    """Integer coefficient of a term (1 if none)."""
    for item in factor_generation(term):
        if item.name.startswith("d_"):
            try:
                return int(item.name[2:])
            except ValueError:
                return 1
    return 1


def _hcf(numbers):
    """gcd of the coefficients; negative only if every coefficient is negative."""
    g = 0
    for x in numbers:
        g = math.gcd(g, x)
    if g == 0:
        return 1
    if numbers and all(x < 0 for x in numbers):
        return -g
    return g


def _factorconst(eq):
    if not eq.children:
        return eq
    if eq.name == "f_add":
        n = _hcf([_coeff(child) for child in eq.children])
        if n != 1:
            const = tree_form("d_" + str(n))
            return const * TreeNode(eq.name, [child / const for child in eq.children])
    return TreeNode(eq.name, [_factorconst(child) for child in eq.children])


def factor0(eq):
    return simplify(_factorconst(eq))
