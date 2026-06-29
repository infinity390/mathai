import copy
from .base import *
from .simplify import simplify
from .expand import expand
ZERO = tree_form("d_0")
ONE = tree_form("d_1")
def tree_to_py(root):
    if not isinstance(root, TreeNode):
        return copy.deepcopy(root)
    stack = [(root, False)]
    result = {}
    while stack:
        node, visited = stack.pop()
        if not visited:
            stack.append((node, True))
            for child in node.children:
                stack.append((child, False))
        else:
            if node.name == "f_list":
                result[node] = [
                    copy.deepcopy(result[child])
                    for child in node.children
                ]
            else:
                result[node] = TreeNode(
                    node.name,
                    [
                        copy.deepcopy(result[child])
                        for child in node.children
                    ]
                )
    return result[root]
def py_to_tree(root):
    if not isinstance(root, list):
        return copy.deepcopy(root)
    stack = [(root, False)]
    result = {}
    while stack:
        obj, visited = stack.pop()
        if not visited:
            stack.append((obj, True))
            if isinstance(obj, list):
                for item in obj:
                    if isinstance(item, list):
                        stack.append((item, False))
        else:
            children = []
            for item in obj:
                if isinstance(item, list):
                    children.append(result[id(item)])
                else:
                    children.append(copy.deepcopy(item))
            result[id(obj)] = TreeNode(
                "f_list",
                children
            )
    return result[id(root)]
def promote(obj):
    return tree_to_py(obj)
def is_scalar(obj):
    return isinstance(obj, TreeNode)
def is_vector(obj):
    return (
        isinstance(obj, list)
        and all(isinstance(x, TreeNode) for x in obj)
    )
def is_matrix(obj):
    if not isinstance(obj, list):
        return False
    if len(obj) == 0:
        return False
    if not all(is_vector(row) for row in obj):
        return False
    cols = len(obj[0])
    return all(len(row) == cols for row in obj)
def dot(u, v):
    if len(u) != len(v):
        raise ValueError("Vector dimension mismatch")
    out = ZERO
    for a, b in zip(u, v):
        out = out + a * b
    return simplify(out)
def vec_add(A, B):
    if len(A) != len(B):
        raise ValueError("Vector dimension mismatch")
    return [
        simplify(A[i] + B[i])
        for i in range(len(A))
    ]
def scalar_vector(a, v):
    return [
        simplify(a * x)
        for x in v
    ]
def mat_add(A, B):
    if len(A) != len(B):
        raise ValueError("Matrix dimension mismatch")
    if len(A[0]) != len(B[0]):
        raise ValueError("Matrix dimension mismatch")
    rows = len(A)
    cols = len(A[0])
    return [
        [
            simplify(A[i][j] + B[i][j])
            for j in range(cols)
        ]
        for i in range(rows)
    ]
def mat_hadamard(A, B):
    if len(A) != len(B):
        raise ValueError("Matrix dimension mismatch")
    if len(A[0]) != len(B[0]):
        raise ValueError("Matrix dimension mismatch")
    rows = len(A)
    cols = len(A[0])
    return [
        [
            simplify(A[i][j] * B[i][j])
            for j in range(cols)
        ]
        for i in range(rows)
    ]
def scalar_matrix(a, M):
    return [
        [
            simplify(a * x)
            for x in row
        ]
        for row in M
    ]
def identity_matrix(n):
    return [
        [
            ONE if i == j else ZERO
            for j in range(n)
        ]
        for i in range(n)
    ]
def mat_mul(A, B):
    rows = len(A)
    inner = len(A[0])
    if inner != len(B):
        raise ValueError("Matrix dimension mismatch")
    cols = len(B[0])
    C = []
    for i in range(rows):
        row = []
        for j in range(cols):
            expr = 0
            for k in range(inner):
                left = copy.deepcopy(A[i][k])
                right = copy.deepcopy(B[k][j])
                if isinstance(left, TreeNode) and isinstance(right, TreeNode):
                    expr = frac_to_tree(expr)
                expr = expr + (left * right)
            row.append(
                simplify(expr)
            )
        C.append(row)
    return C
def matrix_power(A, n):
    if n < 0:
        raise ValueError(
            "Negative matrix powers not implemented"
        )
    rows = len(A)
    if n == 0:
        return [
            [
                ONE if i == j else ZERO
                for j in range(rows)
            ]
            for i in range(rows)
        ]
    result = copy.deepcopy(A)
    for _ in range(1, n):
        result = mat_mul(
            result,
            copy.deepcopy(A)
        )
    return result
def multiply(left, right):
    A = promote(left)
    B = promote(right)
    if is_vector(A) and is_vector(B):
        return dot(A, B)
    if is_matrix(A) and is_matrix(B):
        return py_to_tree(
            mat_mul(A, B)
        )
    if is_scalar(A) and is_vector(B):
        return py_to_tree(
            scalar_vector(A, B)
        )
    if is_scalar(B) and is_vector(A):
        return py_to_tree(
            scalar_vector(B, A)
        )
    if is_scalar(A) and is_matrix(B):
        return py_to_tree(
            scalar_matrix(A, B)
        )
    if is_scalar(B) and is_matrix(A):
        return py_to_tree(
            scalar_matrix(B, A)
        )
    return None
def addition(left, right):
    A = promote(left)
    B = promote(right)
    if is_vector(A) and is_vector(B):
        return py_to_tree(
            vec_add(A, B)
        )
    if is_matrix(A) and is_matrix(B):
        return py_to_tree(
            mat_add(A, B)
        )
    return None
def transpose_matrix(A):
    rows = len(A)
    cols = len(A[0])
    return [
        [
            A[i][j]
            for i in range(rows)
        ]
        for j in range(cols)
    ]
def determinant(M):
    n = len(M)
    if n == 1:
        return M[0][0]
    if n == 2:
        return simplify(
            M[0][0]*M[1][1] - M[0][1]*M[1][0]
        )
    det = tree_form("d_0")
    for j in range(n):
        minor = [
            [
                M[i][k]
                for k in range(n)
                if k != j
            ]
            for i in range(1, n)
        ]
        cofactor = ((-1) ** j) * M[0][j]
        det = det + cofactor * determinant(minor)
    return simplify(det)
def fold_wmul(root):
    stack = [(root, False)]
    result = {}
    while stack:
        node, visited = stack.pop()
        if not visited:
            stack.append(
                (node, True)
            )
            for child in node.children:
                stack.append(
                    (child, False)
                )
            continue
        children = [
            result[c]
            for c in node.children
        ]
        eq = TreeNode(
            node.name,
            children
        )
        if eq.name == "f_transpose":
            A = promote(eq.children[0])
            if is_matrix(A):
                eq = py_to_tree(
                    transpose_matrix(A)
                )
        elif eq.name == "f_det":
            A = promote(eq.children[0])
            if is_matrix(A):
                eq = determinant(A)
        elif eq.name in ["f_mul", "f_wmul"]:
            changed = True
            while (
                changed
                and
                len(eq.children) > 1
            ):
                changed = False
                for i in range(
                    len(eq.children) - 1
                ):
                    out = multiply(
                        eq.children[i],
                        eq.children[i + 1]
                    )
                    if out is not None:
                        eq.children = (
                            eq.children[:i]
                            +
                            [out]
                            +
                            eq.children[i + 2:]
                        )
                        changed = True
                        break
            if len(eq.children) == 1:
                eq = eq.children[0]
        elif eq.name == "f_add":
            changed = True
            while (
                changed
                and
                len(eq.children) > 1
            ):
                changed = False
                for i in range(
                    len(eq.children) - 1
                ):
                    out = addition(
                        eq.children[i],
                        eq.children[i + 1]
                    )
                    if out is not None:
                        eq.children = (
                            eq.children[:i]
                            +
                            [out]
                            +
                            eq.children[i + 2:]
                        )
                        changed = True
                        break
            if len(eq.children) == 1:
                eq = eq.children[0]
        elif eq.name == "f_pow":
            base = promote(eq.children[0])
            exponent = frac(eq.children[1])
            if (
                is_matrix(base)
                and exponent is not None
                and exponent.denominator == 1
                and exponent >= 0
            ):
                eq = py_to_tree(
                    matrix_power(
                        copy.deepcopy(base),
                        exponent.numerator
                    )
                )
        result[node] = eq
    return result[root]

def helper_matrix(eq):
    if eq.name == "f_sigmoid" and len(eq.children) == 2 and eq.children[0].name == "d_1":
        eq2 = eq.children[1].fx("sigmoid")
        eq3 = TreeNode("f_wadd", [tree_form("d_1") , TreeNode("f_hadamard", [tree_form("d_-1"), eq2])])
        return TreeNode("f_hadamard", [eq2, eq3])
    if eq.name == "f_transpose" and eq.children[0].name == "f_cap":
        eq2 = eq.children[0]
        return TreeNode("f_cap", [eq2.children[1], eq2.children[0], eq2.children[3], eq2.children[2], eq2.children[4]])
    if eq.name in ["f_hadamard", "f_wmul"]:
        if tree_form("d_0") in eq.children:
            return tree_form("d_0")
        if tree_form("d_1") in eq.children and eq.name == "f_hadamard":
            out = [child for child in eq.children if child != tree_form("d_1")]
            if out == []:
                return tree_form("d_1")
            if len(out) == 1:
                return out[0]
            return TreeNode(eq.name, out)
    if eq.name in ["f_wadd"]:
        if tree_form("d_0") in eq.children:
            out = [child for child in eq.children if child != tree_form("d_0")]
            if out == []:
                return tree_form("d_0")
            if len(out) == 1:
                return out[0]
            return TreeNode(eq.name, out)
    if eq.name == "f_wmul" and tree_form("d_0") in eq.children:
        return tree_form("d_0")
    return eq
def _matrix_solve2(eq):
    prev = None
    while prev != eq:
        prev = eq
        eq = flatten_tree(eq)
        eq = fold_wmul(eq)
        eq = simplify(eq)
        eq = transform_dfs(eq, helper_matrix)
    return eq
def matrix_solve2(eq):
    return _matrix_solve2(eq)
def matrix_solve(eq):
    fx = lambda x: transform_dfs(simplify(x), helper_matrix)
    return dowhile(eq, fx)
