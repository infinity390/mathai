import itertools
from .parser import parse, remove_extra_brackets
from .simplify import simplify, addition_node_mat

from .base import *
import random
import copy
import math
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

diff_matrix_matrix = lambda x: load_formula("matrix_vectorization_calculus")(x)

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
class NeuralNetwork:
    def __init__(self, struct):
        self.struct = struct
        self.var_list = [tree_form(f"v_-{i}") for i in range(1,26+1-4)]
        self.o = None
        self.lst_w = None
        self.gradient = None
        self.learn = None
        self.learn_var = None
        self.loss = None
        self.model_type = None
        self.init_mat = lambda *args: gpu_var(*args)
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
        for j in range(len(lst_w)):
            item = lst_w[j]
            tmp = TreeNode("f_pdif", [L, item.fx("vec")])
            tmp = diff_matrix_matrix(tmp)
            d = []
            k = self.learn[j]
            while isinstance(k, list):
                d.append(len(k))
                k = k[0]
            tmp = TreeNode("f_reshape", [tmp]+[tree_form(f"d_{item}") for item in d])
            eq = TreeNode("f_hadamard",[tree_form("d_-1"), parse("n"), tmp])
            eq = TreeNode("f_wadd", [item, eq])
            gradient.append(eq)
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
                "exp":math.exp,
                "sigmoid": lambda x: 1.0 / (1.0 + math.exp(-x))
            }
            A_list = []
            for item in self.learn:
                A_list = A_list + flatten_list(item)
            exec(s, env2)
            return env2["fx"](A_list,flatten_list(given_x))
    def train(self, train_x, train_y, learning_rate, epoch, batch_size=1):
        global hadamard, zeros, transpose, matadd, sigmoid, identity, power, vec, diag, flatten,\
               matmul, reshape, kronecker, commutation, broadcast, im2col, conv, col2im
        print("gradients calculated")
        def make_batches(data, batch_size):
            n = len(data)//batch_size
            assert n*batch_size == len(data)
            output = []
            for i in range(n):
                out = []
                for j in range(batch_size):
                    out.append(data[i*batch_size+j])
                output.append(flatten_list(out))
            return output
        data_x_batch = None
        data_y_batch = None
        if self.model_type == "image":
            data_x_batch = make_batches(copy.deepcopy(train_x), batch_size)
            data_y_batch = make_batches(copy.deepcopy(train_y), batch_size)
        data_x = gpu_var_x(*shape(train_x[:batch_size]))
        data_y = gpu_var_y(*shape(train_y[:batch_size]))
        env = {
            "identity":identity,
            "n": learning_rate,
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
            "w":self.learn,
            "X":data_x,
            "Y":data_y  
        }
        env2 = {
            "exp":math.exp,
            "sigmoid": lambda x: 1.0 / (1.0 + math.exp(-x))
        }
        self.learn_var = []
        exec("fx = lambda A,X,Y: "+\
             str(eval("["+",".join([gen2(self.gradient[j], self.lst_w)\
                                    for j in range(len(self.lst_w))])+"]", {}, env)), env2)
        def count_elements(lst):
            count = 0
            for x in lst:
                if isinstance(x, list):
                    count += count_elements(x)
                else:
                    count += 1
            return count
        count = count_elements(self.learn)
        buffer = [[random.random() for j in range(count)] for i in range(2)]
        count = len(data_x_batch)
        print("calculated the equation of every weight in the network")
        for i in range(epoch):
            if i%(epoch//10) == 0:
                print(f"epoch {i}/{epoch}")
            buffer[i%2] = env2["fx"](flatten_list(buffer[(i+1)%2]) if i in [0,1] else flatten_list2(buffer[(i+1)%2]),\
                                     data_x_batch[i%count],data_y_batch[i%count])
        self.learn = buffer[(epoch+1)%2]
        print()
