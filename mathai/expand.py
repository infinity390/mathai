from .base import *
def expand(eq, a="f_add", b="f_mul"):
    stack = [eq]
    while stack:
        expr = stack.pop()
        if not hasattr(expr, "children"):
            continue
        for c in expr.children:
            stack.append(c)
        if expr.name == "f_pow":
            base, exp = expr.children
            n = frac(exp)
            if n and n.denominator == 1 and n.numerator > 1:
                expr.name = b
                expr.children = [base] * n.numerator
                stack.append(expr)
                continue
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
                    expr.name = a
                    expr.children = [
                        TreeNode(b, left + [t] + right)
                        for t in f.children
                    ]
                    stack.append(expr)
                    break
            else:
                expr.children = factors
    return eq
