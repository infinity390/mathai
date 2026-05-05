from .base import *
import itertools
def expand_nc(expr, label="f_mul"):
    if expr.name not in {"f_add", label, "f_pow"}:
        return expr
    expr.children = [expand_nc(c, label) for c in expr.children]
    if expr.name == "f_pow":
        base, exp = expr.children
        n = frac(exp)
        if n and n.denominator == 1 and n.numerator > 1:
            factors = [base] * n.numerator
            return expand_nc(TreeNode(label, factors), label)
        return expr
    if expr.name == "f_add":
        out = []
        for c in expr.children:
            if c.name == "f_add":
                out.extend(c.children)
            else:
                out.append(c)
        return TreeNode("f_add", out)
    if expr.name == label:
        factors = []
        for c in expr.children:
            if c.name == label:
                factors.extend(c.children)
            else:
                factors.append(c)
        for i, f in enumerate(factors):
            if f.name == "f_add":
                left  = factors[:i]
                right = factors[i+1:]
                terms = []
                for term in f.children:
                    new_factors = left + [term] + right
                    terms.append(
                        expand_nc(TreeNode(label, new_factors), label)
                    )
                return TreeNode("f_add", terms)
        return TreeNode(label, factors)
    return expr
def expand2(eq, over="*"):
    over = {"@": "f_wmul", ".":"f_dot", "*":"f_mul"}[over]
    return expand_nc(eq, over)
def expand(eq, over="*"):
    return transform_dfs(eq, expand2, [over])
