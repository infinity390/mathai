from .formula_compiler import formula_list_compiler
import itertools
from .parser import parse, remove_extra_brackets
from .simplify import simplify, addition_node_mat
from .ml import diff_matrix_matrix
from .base import *
import random
import copy
import math
import numpy as np
class TreeNode2:
    count = 0
    count_x = 0
    count_y = 0
    def __new__(cls, name=None, children=None):
        if name is None:
            return super().__new__(cls)
        if children and len(children) == 2:
            c1, c2 = children[0], children[1]
            if hasattr(c1, 'name') and c1.name.startswith("d_") and \
               hasattr(c2, 'name') and c2.name.startswith("d_"):
                try:
                    val1 = int(c1.name[2:])
                    val2 = int(c2.name[2:])
                    res = None
                    if name == "f_add":
                        res = val1 + val2
                    elif name == "f_sub":
                        res = val1 - val2
                    elif name == "f_mul":
                        res = val1 * val2
                    elif name == "f_pow":
                        if val2 >= 0:
                            res = val1 ** val2
                        else:
                            if val1 == 1:
                                res = 1
                            elif val1 == -1:
                                res = 1 if val2 % 2 == 0 else -1
                    if res is not None:
                        obj = super().__new__(cls)
                        obj.name = f"d_{res}"
                        obj.children = []
                        return obj
                except ValueError:
                    pass
        if name == "f_mul" and children and any(hasattr(child, 'name') and child.name == "d_0" for child in children):
            obj = super().__new__(cls)
            obj.name = "d_0"
            obj.children = []
            return obj
        if name == "f_mul" and children and len(children) == 2:
            if hasattr(children[0], 'name') and children[0].name == "d_1":
                return children[1]
            if hasattr(children[1], 'name') and children[1].name == "d_1":
                return children[0]
        if name == "f_add" and children and len(children) == 2:
            if hasattr(children[0], 'name') and children[0].name == "d_0":
                return children[1]
            if hasattr(children[1], 'name') and children[1].name == "d_0":
                return children[0]
        return super().__new__(cls)
    def __init__(self, name=None, children=None):
        if hasattr(self, 'name'):
            return
        if name is None:
            return
        self.name = name
        self.children = children
        self.compare = None
    def normal(self):
        commutative={"f_add","f_mul"}
        stack=[(self,False)]
        while stack:
            node,visited=stack.pop()
            if visited:
                if node.children:
                    if node.name in commutative:
                        node.children.sort(key=lambda c:c.compare)
                    node.compare=(node.name,*(c.compare for c in node.children))
                else:
                    node.compare=(node.name,)
            else:
                stack.append((node,True))
                stack.extend((c,False) for c in node.children)
    def __repr__(self):
        action_stack = [(self, False)]
        value_stack = []
        while action_stack:
            node, children_processed = action_stack.pop()
            if node.name.startswith("v_"):
                var_idx = node.name.split("_")[1]
                value_stack.append(f"A[{var_idx}]")
                continue
            if node.name.startswith("x_"):
                var_idx = node.name.split("_")[1]
                value_stack.append(f"X[{var_idx}]")
                continue
            if node.name.startswith("y_"):
                var_idx = node.name.split("_")[1]
                value_stack.append(f"Y[{var_idx}]")
                continue
            if node.name.startswith("w_"):
                value_stack.append(node.name.split("_")[1])
                continue
            if node.name.startswith("d_"):
                value_stack.append(node.name.split("_")[1])
                continue
            if not children_processed:
                action_stack.append((node, True))
                for child in reversed(node.children):
                    action_stack.append((child, False))
                continue
            num_children = len(node.children)
            child_strs = []
            for _ in range(num_children):
                child_strs.append(value_stack.pop())
            child_strs.reverse()
            if node.name == "f_add":
                value_stack.append(f"({'+'.join(child_strs)})")
            elif node.name == "f_mul":
                value_stack.append(f"({'*'.join(child_strs)})")
            elif node.name == "f_pow":
                value_stack.append(f"({'**'.join(child_strs)})")
            elif node.name == "f_div":
                value_stack.append(f"({'/'.join(child_strs)})")
            elif node.name == "f_exp":
                value_stack.append(f"exp({child_strs[0]})")
            elif node.name == "f_neg":
                value_stack.append(f"(-{child_strs[0]})")
            elif node.name == "f_sigmoid":
                value_stack.append(f"sigmoid({child_strs[0]})")
            else:
                value_stack.append(f"{node.name}({','.join(child_strs)})")
        return value_stack[0]
def zeros(*shape):
    if len(shape) == 0:
        return TreeNode2("d_0",[])
    return [zeros(*shape[1:]) for _ in range(shape[0])]
def flatten(A):
    B = len(A)
    H = len(A[0])
    W = len(A[0][0])
    C = len(A[0][0][0])
    out = []
    for b in range(B):
        row = []
        for i in range(H):
            for j in range(W):
                for c in range(C):
                    row.append(A[b][i][j][c])
        out.append(row)
    return out
def conv(X, K):
    B = len(X)
    H = len(X[0])
    W = len(X[0][0])
    C = len(X[0][0][0])
    P = len(K[0])
    OH = H - P + 1
    OW = W - P + 1
    out = []
    for b in range(B):
        batch = []
        for i in range(OH):
            row = []
            for j in range(OW):
                s = TreeNode2("d_0",[])
                for u in range(P):
                    for v in range(P):
                        for c in range(C):
                            s = TreeNode2("f_add", [s, TreeNode2("f_mul",[X[b][i + u][j + v][c] , K[0][u][v][c]])])
                row.append([s])
            batch.append(row)
        out.append(batch)
    return out
def im2col(image, kernel):
    B = len(image)
    H = len(image[0])
    W = len(image[0][0])
    C = len(image[0][0][0])
    Kh = len(kernel[0])
    Kw = len(kernel[0][0])
    out_h = H - Kh + 1
    out_w = W - Kw + 1
    P = Kh * Kw * C
    cols = []
    for b in range(B):
        for i in range(out_h):
            for j in range(out_w):
                row = [TreeNode2("d_0",[]) for _ in range(B * P)]
                idx = b * P
                for r in range(Kh):
                    for c in range(Kw):
                        for ch in range(C):
                            row[idx] = image[b][i+r][j+c][ch]
                            idx += 1
                cols.append(row)
    return cols
def col2im(kernel, image):
    B = len(image)
    H = len(image[0])
    W = len(image[0][0])
    C = len(image[0][0][0])
    K = len(kernel)
    Kh = len(kernel[0])
    Kw = len(kernel[0][0])
    assert K == 1 or K == B
    OH = H - Kh + 1
    OW = W - Kw + 1
    rows = B * OH * OW
    cols = B * H * W * C
    J = [[TreeNode2("d_0",[]) for _ in range(cols)] for _ in range(rows)]
    row = 0
    for b in range(B):
        kb = 0 if K == 1 else b
        for i in range(OH):
            for j in range(OW):
                for u in range(Kh):
                    for v in range(Kw):
                        for ch in range(C):
                            col = (
                                (((b * H + (i + u)) * W + (j + v)) * C)
                                + ch
                            )
                            J[row][col] = kernel[kb][u][v][ch]
                row += 1
    return J
def commutation(m, n):
    size = m * n
    K = [[TreeNode2("d_0", []) for _ in range(size)] for _ in range(size)]
    for i in range(m):
        for j in range(n):
            src_idx = j * m + i
            dest_idx = i * n + j
            K[dest_idx][src_idx] = TreeNode2("d_1",[])
    return K
def hadamard_h(A, B):
    if isinstance(A, list) and isinstance(B, list):
        assert len(A) == len(B)
        return [hadamard_h(a, b) for a, b in zip(A, B)]
    return TreeNode2("f_mul",[A,B])
def hadamard(*lst_prod):
    result = lst_prod[0]
    for x in lst_prod[1:]:
        if isinstance(result, list) and isinstance(x, list):
            result = hadamard_h(result, x)
        elif isinstance(result, list):
            result = apply(result, lambda y: TreeNode2("f_mul",[y,x]))
        elif isinstance(x, list):
            result = apply(x, lambda y: TreeNode2("f_mul",[result,y]))
        else:
            result = TreeNode2("f_mul",[result,x])
    return result
def matadd_h(A, B):
    if isinstance(A, list) and isinstance(B, list):
        assert len(A) == len(B)
        return [matadd_h(a, b) for a, b in zip(A, B)]
    return TreeNode2("f_add",[A,B])
def matadd(*lst_prod):
    result = lst_prod[0]
    for x in lst_prod[1:]:
        if isinstance(result, list) and isinstance(x, list):
            result = matadd_h(result, x)
        elif isinstance(result, list):
            result = apply(result, lambda y: TreeNode2("f_add",[y,x]))
        elif isinstance(x, list):
            result = apply(x, lambda y: TreeNode2("f_add",[result,y]))
        else:
            result = TreeNode2("f_add",[result,x])
    return result
def matmul_h(A, B):
    assert len(A[0])==len(B)
    rows = len(A)
    inner = len(A[0])
    cols = len(B[0])
    C = []
    for i in range(rows):
        row = []
        for j in range(cols):
            expr = TreeNode2("d_0",[])
            for k in range(inner):
                left = A[i][k]
                right = B[k][j]
                expr = TreeNode2("f_add",[expr,TreeNode2("f_mul",[left,right])])
            row.append(expr)
        C.append(row)
    return C
def depth(x):
    d = 0
    while isinstance(x, list):
        d += 1
        x = x[0]
    return d
def matmul(*lst_prod):
    result = lst_prod[0]
    for index, x in enumerate(lst_prod[1:]):
        if not isinstance(result, list) or not isinstance(x, list):
            if isinstance(result, list):
                result = apply(result, lambda y: TreeNode2("f_mul",[y,x]))
            elif isinstance(x, list):
                result = apply(x, lambda y: TreeNode2("f_mul",[result,y]))
            else:
                result = TreeNode2("f_mul",[result,x])
            continue
        r1 = depth(result)
        r2 = depth(x)
        if r1 == 2 and r2 == 2:
            result = matmul_h(result, x)
        elif r1 == 3 and r2 == 2:
            result = [matmul_h(A, x) for A in result]
        elif r1 == 2 and r2 == 3:
            result = [matmul_h(result, B) for B in x]
        elif r1 == 3 and r2 == 3:
            if len(result) == 1:
                result = [matmul_h(result[0], B) for B in x]
            elif len(x) == 1:
                result = [matmul_h(A, x[0]) for A in result]
            else:
                assert len(result) == len(x)
                result = [
                    matmul_h(A, B)
                    for A, B in zip(result, x)
                ]
        else:
            raise ValueError(
                f"Unsupported matmul ranks ({r1}, {r2})"
            )
    return result
def kronecker_h(A, B):
    m = len(A)
    n = len(A[0])
    p = len(B)
    q = len(B[0])
    result = [[TreeNode2("d_0", []) for _ in range(n * q)] for _ in range(m * p)]
    for j in range(n):
        for c in range(q):
            col_target = (j*q)+c
            for i in range(m):
                for r in range(p):
                    row_target = (i*p)+r
                    result[row_target][col_target] = TreeNode2("f_mul",[A[i][j],B[r][c]])
    return result
def kronecker(*lst_prod):
    result = lst_prod[0]
    for x in lst_prod[1:]:
        result = kronecker_h(result, x)
    return result
def transpose(A):
    rows = len(A)
    cols = len(A[0])
    return [[A[i][j] for i in range(rows)] for j in range(cols)]
def apply(arr, fx):
    if isinstance(arr, list):
        return [apply(item, fx) for item in arr]
    return fx(arr)
def sigmoid(arg):
    def fx_apply(x):
        return TreeNode2("f_sigmoid",[x])
    return apply(arg, fx_apply)
def identity(size):
    arr = zeros(size,size)
    for i in range(size):
        for j in range(size):
            if i == j:
                arr[i][j] = TreeNode2("d_1",[])
    return arr
def vec(A):
    out = []
    def visit(x):
        if isinstance(x, list):
            for y in x:
                visit(y)
        else:
            out.append([x])
    visit(A)
    return out
def diag(v):
    if len(v) > 0 and isinstance(v[0], list):
        if len(v[0]) != 1:
            raise ValueError("diag expects a column vector.")
        v = [x[0] for x in v]
    for x in v:
        if isinstance(x, list):
            raise ValueError("diag received a tensor instead of a vector.")
    n = len(v)
    result = [[TreeNode2("d_0", []) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        result[i][i] = v[i]
    return result
def broadcast(M, rows):
    if not isinstance(M, list):
        raise ValueError("Cannot broadcast a scalar.")
    r = len(M)
    if r == rows:
        return M
    if r != 1:
        raise ValueError(f"Cannot broadcast first dimension {r} to {rows}")
    return [copy.deepcopy(M[0]) for _ in range(rows)]
def reshape(data, *shape):
    def get_shape(x):
        if not isinstance(x, list):
            return []
        return [len(x)] + get_shape(x[0])
    in_shape = get_shape(data)
    def get_element(x, indices):
        for idx in indices:
            x = x[idx]
        return x
    flat = []
    if in_shape:
        num_elements = 1
        for s in in_shape:
            num_elements *= s
        for i in range(num_elements):
            indices = [0] * len(in_shape)
            rem = i
            for d in reversed(range(len(in_shape))):
                indices[d] = rem % in_shape[d]
                rem //= in_shape[d]
            flat.append(get_element(data, indices))
    else:
        flat = [data]
    total = 1
    for s in shape:
        total *= s
    if len(flat) != total:
        raise ValueError(f"Cannot reshape: incompatible dimensions. Total size {len(flat)} vs {total}")
    def make_empty(shp):
        if len(shp) == 1:
            return [None] * shp[0]
        return [make_empty(shp[1:]) for _ in range(shp[0])]
    out_structure = make_empty(shape)
    def set_element(x, indices, val):
        for idx in indices[:-1]:
            x = x[idx]
        x[indices[-1]] = val
    for i in range(total):
        indices = [0] * len(shape)
        rem = i
        for d in reversed(range(len(shape))):
            indices[d] = rem % shape[d]
            rem //= shape[d]
        set_element(out_structure, indices, flat[i])
    return out_structure
def gen2(eq, w):
    def from_treenode(eq,keep_integer=False):
        nonlocal w
        alter = {"f_wadd":"matadd", "f_transpose":"transpose", "f_diag":"diag", "f_identity":"identity","f_wmul":"matmul",\
                 "f_hadamard":"hadamard","f_commutation":"commutation","f_kronecker":"kronecker",\
                 "f_conv":"conv", "f_im2col":"im2col","f_col2im":"col2im", "f_flatten":"flatten",\
                 "f_sigmoid":"sigmoid", "f_vec":"vec"\
                 }
        if eq.name in alter.keys():
            return alter[eq.name]+"("+",".join([from_treenode(child,keep_integer) for child in eq.children])+")"
        if eq.name in ["f_reshape", "f_broadcast"]:
            return eq.name[2:]+"("+",".join([from_treenode(eq.children[0])]+\
                                            [from_treenode(child,True) for child in eq.children[1:]])+")"
        if eq.name in ["f_zeros","f_len"]:
            return eq.name[2:]+"("+",".join([from_treenode(child,True) for child in eq.children])+")"
        alter2 = ["f_add", "f_pow", "f_mul"]
        if eq.name in alter2:
            return f"TreeNode2('{eq.name}',["+",".join([from_treenode(child,keep_integer) for child in eq.children])+"])"
        if not keep_integer and eq.name in [parse("m").name, parse("n").name]:
            return "TreeNode2(f'd_{m}',[])"
        if eq.name == "f_index":
            return from_treenode(eq.children[0],keep_integer)+"["+str(eq.children[1])+"]"
        if eq in w:
            return f"w[{w.index(eq)}]"
        if not keep_integer and eq.name.startswith("d_"):
            return f"TreeNode2('d_{eq.name[2:]}',[])"
        return str(eq)
    return from_treenode(eq)
def gpu_var(*shape):
    if len(shape) == 0:
        TreeNode2.count += 1
        return TreeNode2(f"v_{TreeNode2.count-1}", [])
    return [gpu_var(*shape[1:]) for _ in range(shape[0])]
def gpu_var_x(*shape):
    if len(shape) == 0:
        TreeNode2.count_x += 1
        return TreeNode2(f"x_{TreeNode2.count_x-1}", [])
    return [gpu_var_x(*shape[1:]) for _ in range(shape[0])]
def gpu_var_y(*shape):
    if len(shape) == 0:
        TreeNode2.count_y += 1
        return TreeNode2(f"y_{TreeNode2.count_y-1}", [])
    return [gpu_var_y(*shape[1:]) for _ in range(shape[0])]
def gpu_var_write(content,*shape):
    def gpu_var_helper(*shape):
        if len(shape) == 0:
            return content.pop(0)
        return [gpu_var_helper(*shape[1:]) for _ in range(shape[0])]
    return gpu_var_helper(*shape)
def flatten_list(nested_list):
    flat = []
    def _traverse(items):
        for item in items:
            if isinstance(item, list):
                _traverse(item)
            else:
                flat.append(item)
    _traverse(nested_list)
    return flat
def shape(nested_list):
    if not isinstance(nested_list, list):
        return []
    return [len(nested_list)] + shape(nested_list[0])
def flatten_list2(nested_list):
    flat = []
    def _traverse(items):
        for item in items:
            if isinstance(item, list):
                _traverse(item)
            else:
                flat.append(item)
    output = []
    for item in nested_list:
        flat = []
        _traverse(item)
        output += flat
    return output

def _t_const(k):
    return TreeNode2(f"d_{k}", [])
def _t_add(terms):
    terms = [t for t in terms if t.name != "d_0"]
    if not terms:
        return _t_const(0)
    r = terms[0]
    for t in terms[1:]:
        r = TreeNode2("f_add", [r, t])
    return r
def _t_mul(factors):
    r = factors[0]
    for f in factors[1:]:
        r = TreeNode2("f_mul", [r, f])
    return r
def _diff_rule(node, dch, var):
    name = node.name
    ch = node.children or []
    if not ch:
        return _t_const(1) if name == var else _t_const(0)
    if name == "f_add":
        return _t_add(dch)
    if name == "f_mul":
        terms = []
        for i in range(len(ch)):
            if dch[i].name == "d_0":
                continue
            terms.append(_t_mul([dch[i]] + ch[:i] + ch[i+1:]))
        return _t_add(terms)
    if name == "f_pow":
        base, expo = ch
        if not expo.name.startswith("d_"):
            raise NotImplementedError("derivative of a pow with a non-constant exponent is not supported")
        k = int(expo.name[2:])
        if k == 0 or dch[0].name == "d_0":
            return _t_const(0)
        if k == 1:
            return dch[0]
        return _t_mul([_t_const(k), TreeNode2("f_pow", [base, _t_const(k-1)]), dch[0]])
    if name == "f_sigmoid":
        if dch[0].name == "d_0":
            return _t_const(0)
        one_minus = TreeNode2("f_add", [_t_const(1), TreeNode2("f_mul", [_t_const(-1), node])])
        return _t_mul([node, one_minus, dch[0]])
    if name == "f_exp":
        if dch[0].name == "d_0":
            return _t_const(0)
        return _t_mul([node, dch[0]])
    if name == "f_neg":
        return _t_mul([_t_const(-1), dch[0]])
    if name == "f_div":
        a, b = ch
        t1 = _t_mul([dch[0], TreeNode2("f_pow", [b, _t_const(-1)])])
        t2 = _t_mul([_t_const(-1), a, dch[1], TreeNode2("f_pow", [b, _t_const(-2)])])
        return _t_add([t1, t2])
    raise NotImplementedError(f"no derivative rule for {name}")
def diff_node(root, var, memo):
    stack = [root]
    while stack:
        node = stack[-1]
        if id(node) in memo:
            stack.pop()
            continue
        kids = node.children or []
        pending = [c for c in kids if id(c) not in memo]
        if pending:
            stack.extend(pending)
            continue
        stack.pop()
        memo[id(node)] = _diff_rule(node, [memo[id(c)] for c in kids], var)
    return memo[id(root)]

_DAG_OPS = {"f_add":"add", "f_mul":"mul", "f_pow":"pow", "f_div":"div",
            "f_exp":"exp", "f_neg":"neg", "f_sigmoid":"sigmoid"}
def compile_dag(roots):
    index = {}
    prog = []
    for root in roots:
        stack = [root]
        while stack:
            node = stack[-1]
            if id(node) in index:
                stack.pop()
                continue
            kids = node.children or []
            pending = [c for c in kids if id(c) not in index]
            if pending:
                stack.extend(pending)
                continue
            stack.pop()
            name = node.name
            if not kids:
                if name.startswith("d_"):
                    entry = ("const", float(name[2:]))
                elif name.startswith("v_"):
                    entry = ("A", int(name[2:]))
                elif name.startswith("x_"):
                    entry = ("X", int(name[2:]))
                elif name.startswith("y_"):
                    entry = ("Y", int(name[2:]))
                else:
                    raise ValueError(f"cannot evaluate leaf {name}")
            else:
                if name not in _DAG_OPS:
                    raise ValueError(f"cannot evaluate node {name}")
                entry = (_DAG_OPS[name], tuple(index[id(c)] for c in kids))
            index[id(node)] = len(prog)
            prog.append(entry)
    return prog, [index[id(r)] for r in roots]
def sigmoid_num(x):
    return 0.5 * (1.0 + np.tanh(0.5 * x))
def run_dag(prog, outs, A, X, Y):
    vals = [0.0] * len(prog)
    with np.errstate(all="ignore"):
        for i, (op, arg) in enumerate(prog):
            if op == "const":
                vals[i] = arg
            elif op == "A":
                vals[i] = A[arg]
            elif op == "X":
                vals[i] = X[arg]
            elif op == "Y":
                vals[i] = Y[arg]
            elif op == "add":
                s = 0.0
                for k in arg:
                    s += vals[k]
                vals[i] = s
            elif op == "mul":
                p = 1.0
                for k in arg:
                    p *= vals[k]
                vals[i] = p
            elif op == "pow":
                vals[i] = np.power(vals[arg[0]], vals[arg[1]])
            elif op == "div":
                vals[i] = np.divide(vals[arg[0]], vals[arg[1]])
            elif op == "exp":
                vals[i] = np.exp(vals[arg[0]])
            elif op == "neg":
                vals[i] = -vals[arg[0]]
            elif op == "sigmoid":
                vals[i] = sigmoid_num(vals[arg[0]])
    return [float(vals[k]) for k in outs]

class NeuralNetworkDirect:
    def __init__(self, struct):
        self.struct = struct
        self.var_list = [tree_form(f"v_-{i}") for i in range(1,26+1-4)]
        self.o = None
        self.lst_w = None
        self.gradient = None
        self.weight_equation = None
        self.hessian_equation = None
        self.critical_points = None
        self.critical_point_info = None
        self.learn = None
        self.learn_sym = None
        self.learn_var = None
        self.loss = None
        self.model_type = None
        self.init_mat = lambda *args: gpu_var(*args)
        self._eq_key = None
        self._flat_grad = None
        self._grad_prog = None
        self._grad_outs = None
        self._hess_prog = None
        self._hess_outs = None
        self.loss_equation = None
        self._loss_prog = None
        self._loss_outs = None
        self.minima = None
        self.num_gradients = 0
        self.diff_matrix_count = 0
        self.weight_equation_count = 0
        TreeNode2.count = 0
        TreeNode2.count_x = 0
        TreeNode2.count_y = 0
    def model(self, t="image"):
        self.model_type = t
        if t == "image":
            return self.model_image()
    def model_image(self):
        lst_z = []
        lst_w = []
        x = parse("X")
        y = parse("Y")
        lst_z.append(x)
        flattening_needed = False
        for i in range(1,len(self.struct)):
            if self.struct[i]["type"] == "convolution":
                flattening_needed = True
                lst_w.append(self.var_list.pop(0))
                eq = TreeNode("f_broadcast", [lst_w[-1], parse("m")])
                tmp = TreeNode("f_conv", [lst_z[-1], eq])
                tmp = replace(self.struct[i]["activation"], parse("Z"), tmp)
                lst_z[-1] = tmp
            elif self.struct[i]["type"] == "dense":
                lst_w.append(self.var_list.pop(0))
                lst_w.append(self.var_list.pop(0))
                if flattening_needed:
                    flattening_needed = False
                    lst_z[-1] = lst_z[-1].fx("flatten")
                eq = TreeNode("f_wmul", [lst_z[-1], lst_w[-2]])
                eq = TreeNode("f_wadd", [eq, TreeNode("f_broadcast", [lst_w[-1], parse("m")])])
                lst_z.append(eq)
                tmp = replace(self.struct[i]["activation"], parse("Z"), lst_z[-1])
                lst_z[-1] = tmp
        self.lst_w = lst_w
        self.o = lst_z[-1]
        eq = TreeNode("f_hadamard", [tree_form("d_-1"), y])
        eq = TreeNode("f_wadd", [self.o, eq])
        eq = eq.fx("vec")
        eq = TreeNode("f_wmul", [eq.fx("transpose"), eq])
        L = TreeNode("f_hadamard", [eq, (parse("m") * tree_form("d_2")) ** tree_form("d_-1")])
        self.loss = L
        gradient = []
        index = 0
        self.learn = []
        for i in range(1,len(self.struct)):
            if self.struct[i]["type"] == "dense":
                prev = None
                if self.struct[i-1]["type"] == "convolution":
                    a,b,c = self.struct[0]["dim"]
                    for j in range(1,i):
                        d,e,_ = self.struct[j]["dim"]
                        a,b = a-d + 1, b-e + 1
                    prev = a*b
                else:
                    prev = self.struct[i-1]["dim"][0]
                curr = self.struct[i]["dim"][0]
                self.learn.append(self.init_mat(prev, curr))
                self.learn.append(self.init_mat(1, curr))
            elif self.struct[i]["type"] == "convolution":
                self.learn.append(self.init_mat(*([1]+self.struct[i]["dim"])))
        self.learn_sym = self.learn
        self.num_gradients = len(lst_w)
        self.diff_matrix_count = 0
        print(f"gradients to calculate: {self.num_gradients}")
        for j in range(len(lst_w)):
            item = lst_w[j]
            tmp = TreeNode("f_pdif", [L, item.fx("vec")])
            tmp = diff_matrix_matrix(tmp)
            self.diff_matrix_count += 1
            print(f"diff_matrix_matrix {self.diff_matrix_count}/{self.num_gradients} done")
            d = []
            k = self.learn[j]
            while isinstance(k, list):
                d.append(len(k))
                k = k[0]
            tmp = TreeNode("f_reshape", [tmp]+[tree_form(f"d_{item}") for item in d])
            gradient.append(tmp)
        self.gradient = gradient
        return self
    def predict(self, given_x):
        global hadamard, zeros, transpose, matadd, sigmoid, identity, vec, diag, flatten,\
               matmul, reshape, kronecker, commutation, broadcast, im2col, conv, col2im, extract_values, shape
        TreeNode2.count = 0
        TreeNode2.count_x = 0
        TreeNode2.count_y = 0
        learn2 = []
        for item in self.learn:
            learn2.append(gpu_var(*shape(item)))
        given_x = [given_x]
        given2 = gpu_var_x(*shape(given_x))
        env = {
            "w": learn2,
            "m": 1,
            "identity":identity,
            "X": given2,
            "zeros":zeros,
            "hadamard": hadamard,
            "sigmoid":sigmoid,
            "matadd": matadd,
            "diag":diag,
            "vec":vec,
            "matmul":matmul,
            "reshape":reshape,
            "kronecker":kronecker,
            "commutation":commutation,
            "transpose":transpose,
            "broadcast":broadcast,
            "conv":conv,
            "im2col":im2col,
            "col2im": col2im,
            "flatten":flatten
        }
        if self.model_type == "image":
            tmp = gen2(self.o, self.lst_w)
            eq = eval(tmp, {}, env)[0]
            s = "fx = lambda A,X: "+str(eq)
            env2 = {
                "exp": np.exp,
                "sigmoid": sigmoid_num
            }
            A_list = []
            for item in self.learn:
                A_list = A_list + flatten_list(item)
            exec(s, env2)
            return env2["fx"](A_list,flatten_list(given_x))
    def build_equations(self, train_x, train_y, batch_size):
        key = (batch_size, tuple(shape(train_x[:batch_size])), tuple(shape(train_y[:batch_size])))
        if self._eq_key == key and self.weight_equation is not None:
            return
        TreeNode2.count_x = 0
        TreeNode2.count_y = 0
        data_x = gpu_var_x(*shape(train_x[:batch_size]))
        data_y = gpu_var_y(*shape(train_y[:batch_size]))
        env = {
            "identity":identity,
            "sigmoid":sigmoid,
            "matadd": matadd,
            "zeros":zeros,
            "hadamard": hadamard,
            "diag":diag,
            "vec":vec,
            "matmul":matmul,
            "reshape":reshape,
            "kronecker":kronecker,
            "commutation":commutation,
            "transpose":transpose,
            "broadcast":broadcast,
            "conv":conv,
            "im2col":im2col,
            "col2im":col2im,
            "flatten":flatten,
            "TreeNode2":TreeNode2,
            "m":batch_size,
            "w":self.learn_sym,
            "X":data_x,
            "Y":data_y
        }
        self.weight_equation_count = 0
        print(f"gradients: {self.num_gradients}, diff_matrix_matrix done: {self.diff_matrix_count}/{self.num_gradients}")
        weight_equation = []
        for g in self.gradient:
            weight_equation.append(eval(gen2(g, self.lst_w), {}, env))
            self.weight_equation_count += 1
            print(f"weight equation {self.weight_equation_count}/{self.num_gradients} done")
        self.weight_equation = weight_equation
        self._flat_grad = flatten_list(self.weight_equation)
        n_weights = len(flatten_list(self.learn_sym))
        assert len(self._flat_grad) == n_weights, "gradient size does not match number of weights"
        self._grad_prog, self._grad_outs = compile_dag(self._flat_grad)
        loss_flat = flatten_list(eval(gen2(self.loss, self.lst_w), {}, env))
        assert len(loss_flat) == 1, "loss must be a scalar"
        self.loss_equation = loss_flat[0]
        self._loss_prog, self._loss_outs = compile_dag([self.loss_equation])
        self.hessian_equation = None
        self._hess_prog = None
        self._hess_outs = None
        self.critical_points = None
        self.critical_point_info = None
        self._eq_key = key
    def _eval_gradient(self, A, X, Y):
        return run_dag(self._grad_prog, self._grad_outs, A, X, Y)
    def loss_at(self, A, X, Y):
        return run_dag(self._loss_prog, self._loss_outs, A, X, Y)[0]
    def _unflatten(self, flat):
        it = iter(flat)
        def build(shp):
            if not shp:
                return next(it)
            return [build(shp[1:]) for _ in range(shp[0])]
        return [build(shape(item)) for item in self.learn_sym]
    def build_hessian(self):
        if self._flat_grad is None:
            raise RuntimeError("call build_equations / find_critical_points / train first")
        flat = self._flat_grad
        N = len(flat)
        H = [[None] * N for _ in range(N)]
        step = max(1, N // 10)
        print(f"building hessian: {N} x {N}")
        for j in range(N):
            if j % step == 0:
                print(f"hessian column {j}/{N}")
            memo = {}
            var = f"v_{j}"
            for i in range(j + 1):
                H[i][j] = diff_node(flat[i], var, memo)
                H[j][i] = H[i][j]
        self.hessian_equation = H
        roots = [H[i][j] for j in range(N) for i in range(j + 1)]
        self._hess_prog, self._hess_outs = compile_dag(roots)
        return H
    def hessian_at(self, A, X, Y):
        if self._hess_prog is None:
            raise RuntimeError("call build_hessian() first")
        vals = run_dag(self._hess_prog, self._hess_outs, A, X, Y)
        N = len(self._flat_grad)
        Hn = np.empty((N, N))
        k = 0
        for j in range(N):
            for i in range(j + 1):
                Hn[i, j] = Hn[j, i] = vals[k]
                k += 1
        return Hn
    def _newton(self, x, X, Y, grad_tol, max_iter):
        g = np.array(self._eval_gradient(x.tolist(), X, Y))
        for it in range(max_iter):
            if not np.all(np.isfinite(g)):
                return x, it, False
            gnorm = np.linalg.norm(g, np.inf)
            if gnorm < grad_tol:
                return x, it, True
            Hn = self.hessian_at(x.tolist(), X, Y)
            if not np.all(np.isfinite(Hn)):
                return x, it, False
            try:
                dx = np.linalg.solve(Hn, -g)
            except np.linalg.LinAlgError:
                dx = np.linalg.lstsq(Hn, -g, rcond=None)[0]
            t = 1.0
            while True:
                x_new = x + t * dx
                g_new = np.array(self._eval_gradient(x_new.tolist(), X, Y))
                if np.all(np.isfinite(g_new)) and np.linalg.norm(g_new, np.inf) < gnorm:
                    break
                t *= 0.5
                if t < 1e-10:
                    return x, it, False
            x, g = x_new, g_new
        return x, max_iter, bool(np.linalg.norm(g, np.inf) < grad_tol)
    def find_critical_points(self, train_x, train_y, n_starts=50, init_scale=1.0, seed=None,
                             grad_tol=1e-8, dedup_tol=1e-5, max_iter=100):
        batch_size = len(train_x)
        self.build_equations(train_x, train_y, batch_size)
        if self._hess_prog is None:
            self.build_hessian()
        X = flatten_list(train_x)
        Y = flatten_list(train_y)
        N = len(self._flat_grad)
        rng = np.random.default_rng(seed)
        found = []
        for s in range(n_starts):
            x0 = rng.normal(0.0, init_scale, N)
            x, iters, ok = self._newton(x0, X, Y, grad_tol, max_iter)
            print(f"newton start {s+1}/{n_starts}: {'converged' if ok else 'failed'} after {iters} iterations")
            if not ok:
                continue
            if any(np.linalg.norm(x - p) <= dedup_tol * (1.0 + np.linalg.norm(p)) for p in found):
                continue
            found.append(x)
        self.critical_points = found
        return found
    def classify_critical_points(self, train_x, train_y, points=None, eig_tol=1e-6):
        batch_size = len(train_x)
        self.build_equations(train_x, train_y, batch_size)
        if self._hess_prog is None:
            self.build_hessian()
        if points is None:
            points = self.critical_points
        X = flatten_list(train_x)
        Y = flatten_list(train_y)
        results = []
        for p in points:
            Hn = self.hessian_at(np.asarray(p).tolist(), X, Y)
            eig = np.linalg.eigvalsh(Hn)
            thr = eig_tol * max(1.0, float(np.max(np.abs(eig))))
            if eig.min() > thr:
                kind = "local minimum"
            elif eig.max() < -thr:
                kind = "local maximum"
            elif eig.min() < -thr and eig.max() > thr:
                kind = "saddle point"
            else:
                kind = "inconclusive (singular Hessian)"
            grad_norm = float(np.linalg.norm(self._eval_gradient(np.asarray(p).tolist(), X, Y), np.inf))
            results.append({"point": np.asarray(p), "type": kind, "eigenvalues": eig,
                            "grad_norm": grad_norm,
                            "loss": self.loss_at(np.asarray(p).tolist(), X, Y)})
        self.critical_point_info = results
        return results
    def analyze_critical_points(self, train_x, train_y, **find_kwargs):
        points = self.find_critical_points(train_x, train_y, **find_kwargs)
        return self.classify_critical_points(train_x, train_y, points)
    def train(self, train_x, train_y, check_hessian=False, **find_kwargs):
        points = self.find_critical_points(train_x, train_y, **find_kwargs)
        if not points:
            raise RuntimeError("no critical point found; try a larger n_starts or a different init_scale")
        if check_hessian:
            results = [r for r in self.classify_critical_points(train_x, train_y, points)
                       if r["type"] == "local minimum"]
        else:
            X = flatten_list(train_x)
            Y = flatten_list(train_y)
            results = [{"point": p, "loss": self.loss_at(p.tolist(), X, Y)} for p in points]
        results.sort(key=lambda r: r["loss"])
        print(f"{len(points)} critical points found, {len(results)} kept")
        if not results:
            raise RuntimeError("no local minimum passed the Hessian test")
        self.minima = results
        self.learn = self._unflatten(results[0]["point"].tolist())
        return results
