"""Exact arithmetic with (nested) square roots.

G  : an exact value  const + sum(coef * sqrt(key))  where coef is a Fraction
     and key is a Fraction or, for nested radicals, another G.
F  : a number that is either an exact Fraction or a symbolic TreeNode.
"""
import itertools
import math
from fractions import Fraction

from .base import *
from .simplify import simplify

MAX_INT_POWER = 64          # largest |integer exponent| expanded exactly
MAX_CONJUGATE_RADICALS = 8  # rationalising uses 2**n conjugates; cap n


class NotRadical(Exception):
    """The tree is not  const + sum(rational * sqrt(...))."""


# --------------------------------------------------------------------------
# small number helpers
# --------------------------------------------------------------------------
def frac_to_tree_2(eq):
    if isinstance(eq, int):
        eq = Fraction(eq)
    if eq.numerator == 0:
        return tree_form("d_0")
    if eq.denominator == 1:
        return tree_form(f"d_{eq.numerator}")
    return TreeNode("f_div", [tree_form(f"d_{eq.numerator}"),
                              tree_form(f"d_{eq.denominator}")])


def perfect_sqrt(n):
    """Exact rational square root of n, or None."""
    n = Fraction(n)
    if n < 0:
        return None
    p, q = math.isqrt(n.numerator), math.isqrt(n.denominator)
    if p * p == n.numerator and q * q == n.denominator:
        return Fraction(p, q)
    return None


def simplify_sqrt(a):
    """sqrt(a) = b * sqrt(c) with c squarefree (integer-valued Fraction)."""
    a = Fraction(a)
    if a <= 0:
        return Fraction(1), a
    p, q = a.numerator, a.denominator
    c, b = p * q, 1            # sqrt(p/q) = sqrt(p*q) / q
    while c % 4 == 0:
        c //= 4
        b *= 2
    i = 3
    while i * i <= c:
        while c % (i * i) == 0:
            c //= i * i
            b *= i
        i += 2
    return Fraction(b, q), Fraction(c)


def coeff(eq):
    """Split eq into (rational k, rest) with eq = k * rest; rest is None if eq is rational."""
    out = frac(eq)
    if out is not None:
        return out, None
    k, rest = Fraction(1), []
    for factor in factor_generation(eq):
        v = frac(factor)
        if v is None:
            rest.append(factor)
        else:
            k *= v
    return k, product(rest)


def _coerce(x):
    if isinstance(x, G):
        return x
    if isinstance(x, (int, Fraction)) and not isinstance(x, bool):
        return G({}, Fraction(x))
    raise TypeError(f"cannot use {type(x).__name__} as a G")


# --------------------------------------------------------------------------
# tree rewriting helpers
# --------------------------------------------------------------------------
def helper_2_h(eq):
    if eq.name == "f_sqrt":
        return eq.children[0] ** (tree_form("d_2") ** tree_form("d_-1"))
    if eq.name == "f_div":
        return eq.children[0] * eq.children[1] ** tree_form("d_-1")
    return eq


def helper_3_h(eq):
    if eq.name == "f_sub":
        return eq.children[0] - eq.children[1]
    if eq.name == "f_neg":
        return -eq.children[0]
    return eq


def helper_2(eq):
    return transform_dfs(eq, helper_2_h)


def helper_3(eq):
    return transform_dfs(eq, helper_3_h)


def _tree_eq(self):
    return TreeNode(self.name, [child.eq() for child in self.children])


TreeNode.eq = _tree_eq


# --------------------------------------------------------------------------
# G : const + sum(coef * sqrt(key))
# --------------------------------------------------------------------------
class G:
    def __init__(self, dic=None, const=Fraction(0)):
        self.const = Fraction(const)
        self.dic = {}
        if dic is None:
            return
        if isinstance(dic, TreeNode):
            self._from_tree(dic)
            return
        for key, item in dic.items():
            if isinstance(key, int):
                key = Fraction(key)
            self.dic[key] = self.dic.get(key, Fraction(0)) + Fraction(item)

    def _from_tree(self, tree):
        value = frac(tree)
        if value is not None:
            self.const += value
            return
        terms = tree.children if tree.name == "f_add" else [tree]
        for term in terms:
            k, rest = coeff(helper_2(term))
            if rest is None:
                self.const += k
                continue
            if rest.name != "f_pow" or frac(rest.children[1]) != Fraction(1, 2):
                raise NotRadical(str(term))
            radicand = G(rest.children[0])
            if not radicand.dic and radicand.const < 0:
                raise NotRadical("negative radicand")
            key = radicand if radicand.dic else radicand.const
            self.dic[key] = self.dic.get(key, Fraction(0)) + k
        self.simplify()

    # ---- normal form -----------------------------------------------------
    def copy(self):
        return G(self.dic, self.const)

    def is_zero(self):
        return not self.dic and self.const == 0

    def simplify(self):
        """In place: pull squares out of radicands, merge equal radicals,
        drop zero terms, move sqrt(1) terms into the constant."""
        dic, const = {}, self.const
        for key, coef in self.dic.items():
            if isinstance(key, G):
                key = key.copy().simplify()
                if not key.dic:
                    key = key.const
            if isinstance(key, Fraction):
                b, key = simplify_sqrt(key)
                coef = coef * b
                if key == 1:
                    const += coef
                    continue
            dic[key] = dic.get(key, Fraction(0)) + coef
        self.dic = {k: v for k, v in dic.items()
                    if v != 0 and not (isinstance(k, Fraction) and k == 0)}
        self.const = const
        return self

    # ---- arithmetic ------------------------------------------------------
    def _terms(self):
        return list(self.dic.items()) + [(Fraction(1), self.const)]

    def __add__(self, other):
        try:
            other = _coerce(other)
        except TypeError:
            return NotImplemented
        out = dict(self.dic)
        for key, coef in other.dic.items():
            out[key] = out.get(key, Fraction(0)) + coef
        return G(out, self.const + other.const).simplify()

    __radd__ = __add__

    def __neg__(self):
        return G({k: -v for k, v in self.dic.items()}, -self.const)

    def __sub__(self, other):
        try:
            return self + (-_coerce(other))
        except TypeError:
            return NotImplemented

    def __rsub__(self, other):
        try:
            return _coerce(other) + (-self)
        except TypeError:
            return NotImplemented

    def __mul__(self, other):
        try:
            other = _coerce(other)
        except TypeError:
            return NotImplemented
        out = {}
        for a, ca in self._terms():
            for b, cb in other._terms():
                if isinstance(a, Fraction) and isinstance(b, Fraction):
                    c = a * b
                else:
                    ga = G({}, a) if isinstance(a, Fraction) else a
                    gb = G({}, b) if isinstance(b, Fraction) else b
                    c = (ga * gb).simplify()
                    if not c.dic:
                        c = c.const
                out[c] = out.get(c, Fraction(0)) + ca * cb
        return G(out).simplify()

    __rmul__ = __mul__

    def __pow__(self, n):
        """Integer powers; a negative power may return a TreeNode (see __truediv__)."""
        if not isinstance(n, int):
            return NotImplemented
        if n < 0:
            return G({}, 1) / (self ** -n)
        result, base = G({}, 1), self.copy()
        while n:
            if n & 1:
                result = result * base
            n >>= 1
            if n:
                base = base * base
        return result

    def __truediv__(self, other):
        """Returns a G, or a TreeNode when the quotient can't be rationalised."""
        try:
            other = _coerce(other)
        except TypeError:
            return NotImplemented
        num, den = nested_radical(self), nested_radical(other)
        if den.is_zero():
            raise ZeroDivisionError("division by zero in G")
        if num.is_zero():
            return num
        fallback = TreeNode("f_div", [num.eq(), den.eq()])
        if any(isinstance(k, G) for k in den.dic):
            return fallback
        keys = list(den.dic)
        if keys:
            if len(keys) > MAX_CONJUGATE_RADICALS:
                return fallback
            conj_prod = G({}, 1)
            for signs in itertools.product((1, -1), repeat=len(keys)):
                if all(s == 1 for s in signs):
                    continue          # that one is `den` itself
                conj = G({k: den.dic[k] * s for k, s in zip(keys, signs)}, den.const)
                conj_prod = conj_prod * conj
            norm = nested_radical(conj_prod * den)
            if norm.dic or norm.const == 0:   # radicals not independent -> give up
                return fallback
            ans = nested_radical(conj_prod * num)
        else:
            norm, ans = G({}, den.const), num
        return G({k: v / norm.const for k, v in ans.dic.items()},
                 ans.const / norm.const).simplify()

    def __rtruediv__(self, other):
        try:
            return _coerce(other) / self
        except TypeError:
            return NotImplemented

    # ---- comparison / display -------------------------------------------
    def __eq__(self, other):
        if isinstance(other, (int, Fraction)) and not isinstance(other, bool):
            return not self.dic and self.const == other
        if not isinstance(other, G):
            return NotImplemented
        return str_form(self.eq()) == str_form(other.eq())

    def __hash__(self):
        return hash(str_form(self.eq()))

    def __repr__(self):
        return str(self.eq())

    def eq(self):
        terms = []
        for key, coef in self.dic.items():
            if isinstance(key, Fraction):
                root = frac_to_tree_2(key).fx("sqrt")
            else:
                root = key.eq().fx("sqrt")
            if coef == 1:
                terms.append(root)
            elif coef != 0:
                terms.append(frac_to_tree_2(coef) * root)
        if self.const != 0:
            terms.append(frac_to_tree_2(self.const))
        return summation(terms)


# --------------------------------------------------------------------------
# denesting:  sqrt(a + b*sqrt(c)) = sqrt(x) +/- sqrt(y)
# --------------------------------------------------------------------------
def denest(g):
    """(sqrt(g) as a G, True) if g denests, otherwise (g normalised, False)."""
    g = nested_radical(g)
    if len(g.dic) != 1:
        return g, False
    (c, b), = g.dic.items()
    a = g.const
    if isinstance(c, G) or c <= 0 or a <= 0:
        return g, False
    d = perfect_sqrt(a * a - b * b * c)
    if d is None:
        return g, False
    x, y = (a + d) / 2, (a - d) / 2
    sign = Fraction(1) if b > 0 else Fraction(-1)
    return (G({x: Fraction(1)}) + G({y: sign})), True


def nested_radical(g):
    """Denest every nested radical of g that can be denested; returns a G."""
    out, extra = {}, []
    for key, coef in g.dic.items():
        if isinstance(key, G):
            val, ok = denest(key)
            if ok:
                extra.append(val * coef)
                continue
            key = val if val.dic else val.const
        out[key] = out.get(key, Fraction(0)) + coef
    result = G(out, g.const).simplify()
    for e in extra:
        result = result + e
    return result


# --------------------------------------------------------------------------
# tree -> G evaluation
# --------------------------------------------------------------------------
def valid(eq):
    if eq.name == "f_div" and contain2(eq.children[1], "f_sqrt"):
        return False
    if contain2(eq, "f_mul"):
        return False
    return all(valid(child) for child in eq.children)


def _to_tree(x):
    return x.eq() if isinstance(x, G) else x


def _sqrt_of(inner):
    if not isinstance(inner, G):
        return TreeNode("f_sqrt", [inner])
    inner = inner.copy().simplify()
    if not inner.dic and inner.const < 0:
        return TreeNode("f_sqrt", [inner.eq()])
    return G({inner: Fraction(1)}).simplify()


def _divide(a, b):
    if isinstance(a, G) and isinstance(b, G):
        if b.is_zero():
            return TreeNode("f_div", [a.eq(), b.eq()])
        return a / b
    return TreeNode("f_div", [_to_tree(a), _to_tree(b)])


def calc(eq):
    """Evaluate a tree to a G where possible; unknown parts stay TreeNodes.
    Never returns None."""
    if not isinstance(eq, TreeNode):
        return eq
    value = frac(eq)
    if value is not None:
        return G({}, value)
    if valid(eq):
        try:
            return G(eq)
        except NotRadical:
            pass
    if not eq.children:
        return eq

    name = eq.name
    parts = [calc(child) for child in eq.children]

    if name in ("f_add", "f_mul"):
        is_add = name == "f_add"
        acc = G({}, 0 if is_add else 1)
        rest = []
        for p in parts:
            if isinstance(p, G):
                acc = acc + p if is_add else acc * p
            else:
                rest.append(p)
        if not rest:
            return acc
        if is_add:
            return summation(rest + ([] if acc.is_zero() else [acc.eq()]))
        if acc.is_zero():
            return acc
        return product(rest + ([] if acc == 1 else [acc.eq()]))

    if name == "f_sqrt" and len(parts) == 1:
        return _sqrt_of(parts[0])

    if name == "f_div" and len(parts) == 2:
        return _divide(parts[0], parts[1])

    if name == "f_pow" and len(parts) == 2 and isinstance(parts[0], G):
        base, e = parts[0], frac(eq.children[1])
        if e == Fraction(1, 2):
            return _sqrt_of(base)
        if e is not None and e.denominator == 1 and abs(e) <= MAX_INT_POWER:
            n = int(e)
            if n > 0 or (n == 0 and not base.is_zero()):
                return base ** n
            if n < 0 and not base.is_zero():
                return _divide(G({}, 1), base ** -n)

    return TreeNode(name, [_to_tree(p) for p in parts])


def solve_sqrt_h(eq):
    x = calc(flatten_tree(helper_3(eq)))
    if isinstance(x, G):
        x = nested_radical(x).eq()
    return flatten_tree(x)


def solve_sqrt(eq):
    return dowhile(eq, lambda x: simplify(solve_sqrt_h(x), False))


def print_raw(eq):
    print(string_equation(str_form(eq)))


def frac_2(eq):
    return frac(helper_2(eq))


def simp(eq):
    if isinstance(eq, F):
        eq = eq.value
    if isinstance(eq, TreeNode):
        out = solve_sqrt(eq)
        if out is not None:
            eq = out
        value = frac_2(eq)
        return eq if value is None else value
    return eq


# --------------------------------------------------------------------------
# F : exact Fraction or symbolic TreeNode
# --------------------------------------------------------------------------
def get_value(x):
    if isinstance(x, F):
        return x.value
    if isinstance(x, int):
        return Fraction(x)
    return x


def promote_obj(x):
    if isinstance(x, F):
        x = x.value
    if isinstance(x, TreeNode):
        return x
    if isinstance(x, (int, Fraction)):
        return frac_to_tree_2(Fraction(x))
    raise TypeError(f"cannot promote {type(x).__name__}")


def _is_operand(x):
    return isinstance(x, (int, Fraction, TreeNode, F)) and not isinstance(x, bool)


def compare(a, b):
    """-1 / 0 / 1, or None when the two can't be compared numerically."""
    a, b = get_value(a), get_value(b)
    if isinstance(a, Fraction) and isinstance(b, Fraction):
        return (a > b) - (a < b)
    if isinstance(a, TreeNode) and isinstance(b, TreeNode) and str_form(a) == str_form(b):
        return 0
    vals = []
    for item in (a, b):
        if isinstance(item, TreeNode):
            try:
                item = compute(helper_2(item))
            except OverflowError:
                item = None
        vals.append(item)
    if any(v is None for v in vals):
        return None
    try:
        x, y = float(vals[0]), float(vals[1])
    except OverflowError:
        return None
    if math.isclose(x, y, rel_tol=1e-12, abs_tol=1e-12):
        return 0
    return 1 if x > y else -1


class F:
    def __init__(self, value=0):
        if isinstance(value, F):
            value = value.value
        elif isinstance(value, int):
            value = Fraction(value)
        self.value = value
        if isinstance(self.value, TreeNode):
            self.value = simp(self.value)

    def promote(self, other, op):
        return F(TreeNode(op, [promote_obj(self), promote_obj(other)]))

    def fx(self, name):
        return F(TreeNode("f_" + name, [promote_obj(self)]))

    def _binary(self, other, op, exact, reverse=False, force_symbolic=None):
        if not _is_operand(other):
            return NotImplemented
        a, b = (F(other), self) if reverse else (self, F(other))
        x, y = get_value(a), get_value(b)
        if (isinstance(x, TreeNode) or isinstance(y, TreeNode)
                or (force_symbolic is not None and force_symbolic(x, y))):
            return a.promote(b, op)
        return F(exact(x, y))

    def __add__(self, o):     return self._binary(o, "f_add", lambda x, y: x + y)
    def __radd__(self, o):    return self._binary(o, "f_add", lambda x, y: x + y, True)
    def __sub__(self, o):     return self._binary(o, "f_sub", lambda x, y: x - y)
    def __rsub__(self, o):    return self._binary(o, "f_sub", lambda x, y: x - y, True)
    def __mul__(self, o):     return self._binary(o, "f_mul", lambda x, y: x * y)
    def __rmul__(self, o):    return self._binary(o, "f_mul", lambda x, y: x * y, True)
    def __truediv__(self, o): return self._binary(o, "f_div", lambda x, y: x / y)
    def __rtruediv__(self, o): return self._binary(o, "f_div", lambda x, y: x / y, True)

    # a non-integer exponent stays symbolic so the result stays exact
    @staticmethod
    def _fractional_exp(x, y):
        return isinstance(y, Fraction) and y.denominator != 1

    def __pow__(self, o):
        return self._binary(o, "f_pow", lambda x, y: x ** y,
                            force_symbolic=F._fractional_exp)

    def __rpow__(self, o):
        return self._binary(o, "f_pow", lambda x, y: x ** y, True,
                            force_symbolic=F._fractional_exp)

    def __neg__(self):
        if isinstance(self.value, TreeNode):
            return F(TreeNode("f_neg", [promote_obj(self)]))
        return F(-self.value)

    def __hash__(self):
        v = get_value(self)
        if isinstance(v, Fraction):
            return hash(v)
        return hash(str_form(v))

    def __lt__(self, o):
        return _is_operand(o) and compare(self, o) == -1

    def __le__(self, o):
        return _is_operand(o) and compare(self, o) in (-1, 0)

    def __gt__(self, o):
        return _is_operand(o) and compare(self, o) == 1

    def __ge__(self, o):
        return _is_operand(o) and compare(self, o) in (1, 0)

    def __eq__(self, o):
        if not _is_operand(o):
            return NotImplemented
        return compare(self, o) == 0

    def __float__(self):
        value = get_value(self)
        if isinstance(value, TreeNode):
            out = compute(helper_2(value))
            if out is None:
                raise ValueError("expression has no numeric value")
            return float(out)
        return float(value)

    def __repr__(self):
        return str(self.value)
