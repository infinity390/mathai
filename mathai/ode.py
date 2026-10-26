from collections import Counter

from .base import *  # tree_form, TreeNode, contain, replace, str_form, factor_generation, product, summation ...
from .factor import factor1, factor2   # factor1 = formula-list compiler (takes ONE expression, not a list)
from .fraction import fraction
from .simplify import simplify
from .inverse import inverse
from .parser import parse

# --------------------------------------------------------------------------- #
# Constants (built once)
# --------------------------------------------------------------------------- #
ZERO = tree_form("d_0")
ONE = tree_form("d_1")
TWO = tree_form("d_2")
NEG_ONE = tree_form("d_-1")
E = tree_form("s_e")
I = tree_form("s_i")
V0 = tree_form("v_0")
V1 = tree_form("v_1")
V2 = tree_form("v_2")
V = (V0, V1)
DIF0 = V0.fx("dif")
DIF1 = V1.fx("dif")
INV_DIF0 = DIF0 ** -1
INV_DIF1 = DIF1 ** -1

_MAX_DEPTH = 8     # bound on the shift/factor rewriting loop in inversediff


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def _has_name(node, name):
    return node.name == name or any(_has_name(c, name) for c in node.children)


def _terms(eq):
    return list(eq.children) if eq.name == "f_add" else [eq]


def _expr(eq):
    """The 'expression = 0' side of an equation (or the expression itself)."""
    if eq.name == "f_eq":
        lhs, rhs = eq.children
        return lhs if rhs == ZERO else lhs - rhs
    return eq


def allocvar():
    return tree_form("v_101")


def clist(x):
    return list(x.elements())


def e0(eq):
    return TreeNode("f_eq", [eq, ZERO])


def e1(eq):
    return eq.children[0] if eq.name == "f_eq" else eq


# --------------------------------------------------------------------------- #
# Separation of variables
# --------------------------------------------------------------------------- #
def rev(eq):
    factors = factor_generation(eq)
    if INV_DIF0 in factors or INV_DIF1 in factors:
        return False
    return all(rev(child) for child in eq.children)


def check(eq):
    """False if some single factor mixes x and y."""
    return not any(contain(f, V0) and contain(f, V1) for f in factor_generation(eq))


def shift(lhs, rhs):
    """Rearrange  lhs + rhs = 0  into  A(x) = B(y)-style sides; returns [new_lhs, new_rhs]."""
    if isinstance(lhs, list):
        lhs = simplify(summation(lhs))
    if isinstance(rhs, list):
        rhs = simplify(summation(rhs))
    rhs = simplify(-rhs)
    sides = [factor_generation(lhs), factor_generation(rhs)]
    moved = [[], []]          # moved[k] = factors that must be divided out of side k
    for i in (0, 1):
        stay = []
        for f in sides[i]:
            if contain(f, V[1 - i]) and not contain(f, V[i]):
                moved[1 - i].append(f)
            else:
                stay.append(f)
        sides[i] = stay
    output = [simplify(product(sides[i]) * product(moved[i]) ** NEG_ONE) for i in (0, 1)]
    if any(_has_name(item, "f_dif") for item in output) and DIF0 not in factor_generation(output[0]):
        output = [ONE / item for item in output]
    return output


def inversediff(lhs, rhs, old=None):
    if lhs is None or rhs is None:
        return None
    old = [] if old is None else old
    if len(old) > _MAX_DEPTH:
        return None

    eq = factor1(simplify(lhs - rhs))
    if eq in old:                       # already seen -> rewriting is looping
        return None

    const, xonly, yonly, mixed = [], [], [], []
    for item in _terms(eq):
        cx, cy = contain(item, V0), contain(item, V1)
        if cx and cy:
            mixed.append(item)
        elif cx:
            xonly.append(item)
        elif cy:
            yonly.append(item)
        else:
            const.append(item)
    (yonly if yonly else xonly).extend(const)

    if not mixed:
        return simplify(lhs - rhs)      # already separated (unfactored form, so terms stay iterable)

    m = factor1(summation(mixed))       # factor1 takes an expression, not a list
    mixed = _terms(m)
    nxt = old + [eq]

    if xonly and yonly:
        out = inversediff(*shift(mixed + xonly, yonly), nxt)
        if out is None:
            out = inversediff(*shift(xonly, factor1(summation(mixed + yonly))), nxt)
        return out
    if yonly:
        if m.name == "f_add":
            return None
        return inversediff(*shift(m, yonly), nxt)
    if xonly:
        if m.name == "f_add":
            return None
        return inversediff(*shift(xonly, m), nxt)
    if len(mixed) == 2:
        return inversediff(*shift(*mixed), nxt)
    return None


def epowersplit(eq):
    if not eq.children:
        return eq
    if eq.name == "f_pow" and eq.children[1].name == "f_add":
        return product([eq.children[0] ** child for child in eq.children[1].children])
    return TreeNode(eq.name, [epowersplit(child) for child in eq.children])


def esolve(s):
    if not s.children:
        return s
    if s.name == "f_add" and _has_name(s, "f_log"):
        return product([E ** child for child in s.children]) - ONE
    return TreeNode(s.name, [esolve(child) for child in s.children])


def groupe(eq):
    eq = simplify(esolve(eq))
    eq = simplify(fraction(eq))
    return epowersplit(eq)


def diffsolve_sep(eq):
    expr = e1(epowersplit(eq))
    return inversediff(ZERO, expr.copy_tree())


def diffsolve_sep2(eq):
    """Integrate a separated form  f(x)dx + g(y)dy  term by term."""
    if eq is None:
        return None
    parts = [allocvar()]
    for item in _terms(eq):
        factors = factor_generation(simplify(item))
        rest = product([k for k in factors if k.name != "f_dif"])
        if DIF0 in factors:
            parts.append(TreeNode("f_integrate", [rest, V0]))
        elif DIF1 in factors:
            parts.append(TreeNode("f_integrate", [rest, V1]))
        else:
            return None        # a term with no differential cannot be integrated (was silently dropped)
    return TreeNode("f_eq", [summation(parts), ZERO])


# --------------------------------------------------------------------------- #
# Derivative bookkeeping
# --------------------------------------------------------------------------- #
def order(eq, m=0):
    if eq.name in ("f_pdif", "f_dif"):
        return order(eq.children[0], m + 1)
    return max([m] + [order(child, m) for child in eq.children])


def subs2(eq, orde):
    if not eq.children:
        return eq
    if eq.name in ("f_dif", "f_pdif") and len(eq.children) == 2:
        if orde == 1:
            return eq.children[0].fx("dif") / eq.children[1].fx("dif")
        return eq
    return TreeNode(eq.name, [subs2(child, orde) for child in eq.children])


def subs3(eq):
    """Push dif through sums and products (sum / product rule)."""
    if not eq.children:
        return eq
    if eq.name == "f_dif":
        inner = eq.children[0]
        if inner.name == "f_add":
            return summation([subs3(c.fx("dif")) for c in inner.children])
        if inner.name == "f_mul":
            kids = inner.children
            return summation([
                product([subs3(c.fx("dif")) if i == j else c for j, c in enumerate(kids)])
                for i in range(len(kids))
            ])
    return TreeNode(eq.name, [subs3(child) for child in eq.children])


# --------------------------------------------------------------------------- #
# Coefficient collection
# --------------------------------------------------------------------------- #
def collect_term(eq, term_lst):
    """Split eq into  sum(coef[t] * t for t in term_lst) + other.  Returns [coef_dict, other]."""
    ordered = sorted(term_lst, key=lambda x: -len(factor_generation(x)))   # most specific first
    counters = [(t, Counter(factor_generation(t))) for t in ordered]       # built once, not per term
    parts = {t: [] for t, _ in counters}
    other = []
    for term in _terms(eq):
        tc = Counter(factor_generation(term))
        for t, c in counters:
            if (tc & c) == c:
                parts[t].append(product(clist(tc - c)))
                break
        else:
            other.append(term)
    coef = {t: (simplify(summation(p)) if p else ZERO) for t, p in parts.items()}
    return [coef, simplify(summation(other)) if other else ZERO]

def linear_dif(eq, a, b):
    """db + p*b*da - q*da = 0  ->  integrating-factor solution."""
    eq = simplify(eq)
    db, da = b.fx("dif"), a.fx("dif")
    bda = b * da
    coef, other = collect_term(_expr(eq), [db, bda, da])
    if other != ZERO:
        return None
    lead = coef[db]
    if lead == ZERO:
        return None
    p = simplify(coef[bda] / lead)
    q = simplify(-(coef[da] / lead))
    if contain(p, b) or contain(q, b):
        return None
    f = E ** TreeNode("f_integrate", [p, a])
    return simplify(TreeNode("f_eq", [b * f, TreeNode("f_integrate", [q * f, a]) + allocvar()]))


def diffsolve(eq):
    orig = eq.copy_tree()
    eq = subs2(eq, order(eq))
    eq = fraction(simplify(fraction(eq)))
    n = order(eq)

    if n != 1:                       # only first order are handled
        return orig

    # 1) directly separable
    sol = diffsolve_sep2(diffsolve_sep(eq))
    if sol is not None:
        return sol

    # 2) homogeneous: substitute b = b*a, separate, substitute back
    first = subs2(orig, 1)           # same for both loop iterations
    for i in (0, 1):
        a, b = V[i], V[1 - i]
        eq2 = subs3(replace(first, b, b * a))
        eq2 = simplify(fraction(simplify(eq2)))
        eq2 = diffsolve_sep2(diffsolve_sep(eq2))
        if eq2 is not None:
            return e0(TreeNode("f_subs", [replace(eq2.children[0], b, V2), V2, b / a]).fx("try"))

    # 3) linear first order
    eq = fraction(subs2(simplify(orig), 1))
    for i in (0, 1):
        out = linear_dif(eq, V[i], V[1 - i])
        if out is not None:
            return out
    return orig
