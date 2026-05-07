from .base import *
import itertools
def expand_nc(expr, labels=("f_add", "f_mul")):
    a, b = labels
    if expr.name not in {a, b, "f_pow"}:
        return expr
    expr = flatten_tree(expr)
    if expr.name == "f_pow":
        base, exp = expr.children
        n = frac(exp)
        if n and n.denominator == 1 and n.numerator > 1:
            factors = [base] * n.numerator
            return TreeNode(b, factors)
    if expr.name == b:
        factors = []
        for c in expr.children:
            if c.name == b:
                factors.extend(c.children)
            else:
                factors.append(c)
        for i, f in enumerate(factors):
            if f.name == a:
                left = factors[:i]
                right = factors[i+1:]
                return TreeNode(
                    a,
                    [
                        TreeNode(b, left + [t] + right)
                        for t in f.children
                    ]
                )
        return TreeNode(b, factors)
    return expr
def expand2(eq, labels):
    a, b = labels
    return expand_nc(eq, (a, b))
def expand(eq, a="f_add", b="f_mul"):
    return dowhile(eq, lambda x: transform_dfs(x, expand2, [(a, b)]))
