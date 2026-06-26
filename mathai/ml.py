from .parser import parse, remove_extra_brackets
from .simplify import simplify
from .diff import diff2, diff
from .matrix import matrix_solve
from .base import *
import random
import copy
import math
def zeros(a, b):
    arr = []
    for i in range(a):
        arr.append([])
        for j in range(b):
            arr[-1].append(0)
    return arr
def randos(low,high,a, b):
    arr = []
    for i in range(a):
        arr.append([])
        for j in range(b):
            tmp = random.uniform(low,high)
            arr[-1].append(tmp)
    return arr
def hadamard(A, B):
    rows = len(A)
    cols = len(A[0])
    tmp = [
        [
            A[i][j] * B[i][j]
            for j in range(cols)
        ]
        for i in range(rows)
    ]
    return tmp
def matadd_h(A, B):
    rows = len(A)
    cols = len(A[0])
    return [
        [
            A[i][j] + B[i][j]
            for j in range(cols)
        ]
        for i in range(rows)
    ]
def matmul_h(A, B):
    rows = len(A)
    inner = len(A[0])
    cols = len(B[0])
    C = []
    for i in range(rows):
        row = []
        for j in range(cols):
            expr = 0
            for k in range(inner):
                left = A[i][k]
                right = B[k][j]
                expr = expr + (left * right)
            row.append(expr)
        C.append(row)
    return C
def matmul(*lst_prod):
    lst_prod = list(lst_prod)
    result = lst_prod[0]
    for x in lst_prod[1:]:
        result = matmul_h(result, x)
    return result
def matadd(*lst_prod):
    lst_prod = list(lst_prod)
    result = lst_prod[0]
    for x in lst_prod[1:]:
        result = matadd_h(result, x)
    return result
def transpose(A):
    rows = len(A)
    cols = len(A[0])
    return [
        [
            A[i][j]
            for i in range(rows)
        ]
        for j in range(cols)
    ]
def shape(s):
    if not isinstance(s[0], list):
        return [len(s)]
    return [len(s), len(s[0])]
def multiply(*lst_prod):
    lst_prod = list(lst_prod)
    result = lst_prod[0]
    for x in lst_prod[1:]:
        if isinstance(result, list) and isinstance(x, list):
            result = hadamard(result, x)
        elif isinstance(result, list):
            result = apply(result, lambda y: y*x)
        elif isinstance(x, list):
            result = apply(x, lambda y: y*result)
        else:
            result = result * x
    return result
def apply(arr, fx):
    if isinstance(arr, list):
        return [apply(item, fx) for item in arr]
    return fx(arr)
def exp(arg):
    return apply(arg, lambda x: math.exp(x))
def power(a, b):
    return apply(a, lambda x: math.pow(x,b))
def index_func(eq, s):
    if eq.name.startswith("d_"):
        return str(int(eq.name[2:])-1)
    return s+"-1"
def gen(eq, w, b, active):
    if eq == parse("X"):
        return "X"
    if eq == parse("Y"):
        return "Y"
    if eq == parse("W"):
        return "[[W]]"
    if eq == parse("n"):
        return "[[n]]"
    if eq.name == "f_transpose":
        return f"transpose({gen(eq.children[0], w, b, active)})"
    if eq.name == "f_index":
        if eq.children[0].name == "f_index":
            d = gen(eq.children[0].children[0], w, b, active)
            return f"[[{d}[{index_func(eq.children[0].children[1], 'i')}][{index_func(eq.children[1], 'j')}]]]"
        else:
            print("error")
    if eq.name == "f_cap":
        dim = eq.children[0].children[0]
        d = gen(dim, w, b, active)
        return f"cap(shape({d})[0],shape({d})[1],{index_func(eq.children[2], 'i')},{index_func(eq.children[3], 'j')})"
    if eq.name == "f_add":
        return "matadd("+",".join([gen(child, w, b, active) for child in eq.children])+")"
    if eq.name == "f_wmul":
        return "matmul("+",".join([gen(child, w, b, active) for child in eq.children])+")"
    if eq.name in ["f_mul"]:
        return "multiply("+",".join([gen(child, w, b, active) for child in eq.children])+")"
    if eq.name in ["f_hadamard"]:
        return "hadamard("+",".join([gen(child, w, b, active) for child in eq.children])+")"
    if eq.name == "f_pow" and eq.children[0] == tree_form("s_e"):
        return f"exp({gen(eq.children[1], w, b, active)})"
    if eq.name == "f_pow" and eq.children[1].name.startswith("d_"):
        n = int(eq.children[1].name[2:])
        return f"power({gen(eq.children[0], w, b, active)},{n})"
    if eq.name.startswith("v_") and eq in w:
        return f"w[{w.index(eq)}]"
    if eq.name.startswith("v_") and eq in b:
        return f"b[{b.index(eq)}]"
    if eq.name == "f_F":
        child = None
        orig = copy.deepcopy(active)
        if len(eq.children) == 2:
            for _ in range(int(eq.children[0].name[2:])):
                active = diff(active, parse("Z").name)
            child = eq.children[1]
        else:
            child = eq.children[0]
        return gen(simplify(replace(active, parse("Z"), child)), w, b, orig)
    if eq.name.startswith("d_"):
        return f"[[{eq.name[2:]}]]"
def gen2(eq, w, b, active):
    tmp = gen(eq, w, b, active)
    tmp = remove_extra_brackets(tmp)
    return tmp
def cap(a, b, x, y):
    arr = zeros(a,b)
    arr[x][y] = 1
    return arr
class NeuralNetwork:
    def __init__(self, struct, rand_range=None, active=None):
        self.struct = struct
        self.update_fx = {}
        self.var_list = [tree_form(f"v_-{i}") for i in range(1,26+1-4) if tree_form(f"v_-{i}") != parse("F")]
        if active is None:
            self.active = simplify(parse("1/(e^(-Z)+1)"))
        else:
            self.active = simplify(active)
        self.o = None
        self.lst_w = None
        self.lst_b = None
        self.gradient = None
        self.learn = None
        if rand_range is None:
            self.init_mat = lambda x,y: zeros(x, y)
        else:
            self.init_mat = lambda x,y: randos(rand_range[0], rand_range[1], x, y)
    def model(self):
        lst_z = []
        lst_w = []
        lst_b = []
        x = parse("X")
        y = parse("Y")
        var_i = tree_form("v_11")
        var_j = parse("j")
        lst_z.append(x)
        for i in range(len(self.struct)-1):
            lst_w.append(self.var_list.pop(0))
            lst_b.append(self.var_list.pop(0))
            lst_z.append((TreeNode("f_wmul", [lst_z[-1], lst_w[-1]])+lst_b[-1]))
            lst_z[-1] = matrix_solve(lst_z[-1].fx("F"))
        self.lst_b = lst_b
        self.lst_w = lst_w
        self.o = lst_z[-1]
        L = TreeNode("f_wmul", [self.o-y,(self.o-y).fx("transpose")])/tree_form("d_2")
        L = matrix_solve(L)
        gradient = [[], []]
        for i in range(2):
            for j in range(len(self.struct)-1):
                item = [lst_w, lst_b][i][j]
                if i == 0:
                    item = TreeNode("f_index", [TreeNode("f_index", [item, tree_form("v_11")]), parse("j")])
                else:
                    item = TreeNode("f_index", [TreeNode("f_index", [item, tree_form("d_1")]), parse("j")])
                tmp = diff2(TreeNode("f_pdif", [L, item]))
                eq = parse("W") - TreeNode("f_wmul", [parse("n"),tmp])
                eq = matrix_solve(eq)
                gradient[i].append(eq)
        self.gradient = gradient
        lst_1 = []
        lst_2 = []
        for i in range(1,len(self.struct)):
            lst_1.append(self.init_mat(1, self.struct[i]))
            lst_2.append(self.init_mat(self.struct[i-1], self.struct[i]))
        self.learn = [lst_2, lst_1]
        return self
    def predict(self, given_x):
        global shape, exp, power, hadamard, zeros, matmul, multiply, transpose, matadd
        env = {
            "w": self.learn[0],
            "b": self.learn[1],
            "cap": cap,
            "X": [given_x],
            "transpose":transpose,
            "multiply":multiply,
            "shape":shape,
            "matmul":matmul,
            "zeros":zeros,
            "hadamard": hadamard,
            "exp":exp,
            "power":power,
            "matadd": matadd
        }
        return eval(gen2(self.o, self.lst_w, self.lst_b, self.active), {}, env)
    def train(self, train_x, train_y, learning_rate, epoch):
        global shape, exp, power, hadamard, zeros, matmul, multiply, transpose, matadd
        env = {
            "cap": cap,
            "n": learning_rate,
            "matadd": matadd,
            "transpose":transpose,
            "multiply":multiply,
            "shape":shape,
            "matmul":matmul,
            "zeros":zeros,
            "hadamard": hadamard,
            "exp":exp,
            "power":power
        }
        for i in range(2):
            for j in range(len(self.struct)-1):
                tmp = f"fx_{i}_{j} = lambda W,X,Y,i,j,w,b: "+gen2(self.gradient[i][j], self.lst_w, self.lst_b, self.active)
                exec(tmp, env)
        for k in range(epoch):            
            for data_index in range(len(train_x)):
                learn_new = copy.deepcopy(self.learn)
                data_x = [train_x[data_index]]
                data_y = [train_y[data_index]]
                for i in range(2):
                    for j in range(len(self.struct)-1):
                        s = shape(self.learn[i][j])
                        for x in range(s[0]):
                            for y in range(s[1]):
                                W = self.learn[i][j][x][y]
                                learn_new[i][j][x][y] = env[f"fx_{i}_{j}"](W, data_x, data_y, x+1, y+1, self.learn[0], self.learn[1])[0][0]
                self.learn = copy.deepcopy(learn_new)
            print(f"epoches done {k+1}/{epoch}")
