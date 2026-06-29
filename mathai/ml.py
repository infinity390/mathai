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
def hadamard_h(A, B):
    assert len(A)==len(B)
    assert len(A[0])==len(B[0])
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
def hadamard(*lst_prod):
    result = lst_prod[0]
    for x in lst_prod[1:]:
        if isinstance(x, list) and isinstance(result, list):
            result = hadamard_h(result, x)
        elif isinstance(x, list):
            result = apply(x, lambda y: y*result)
        elif isinstance(result, list):
            result = apply(result, lambda y: y*x)
        else:
            result = result * x
    return result
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
    assert len(A[0])==len(B)
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
    result = lst_prod[0]
    for x in lst_prod[1:]:
        result = matmul_h(result, x)
    return result
def matadd(*lst_prod):
    result = lst_prod[0]
    for x in lst_prod[1:]:
        if isinstance(x, list) and isinstance(result, list):
            result = matadd_h(result, x)
        elif isinstance(x, list):
            result = apply(x, lambda y: y+result)
        elif isinstance(result, list):
            result = apply(result, lambda y: y+x)
        else:
            result = result + x
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
def apply(arr, fx):
    if isinstance(arr, list):
        return [apply(item, fx) for item in arr]
    return fx(arr)
def exp(arg):
    return apply(arg, lambda x: math.exp(x))
def inv(arg):
    return apply(arg, lambda x: 1.0/x)
def tanh(arg):
    return apply(arg, lambda x: math.tanh(x))
def sigmoid(arg):
    return apply(arg, lambda x: 1.0/(1.0 + math.exp(-x) ))
def gen2(eq, w, active):
    def from_treenode(eq):
        nonlocal w, active
        
        alter = {"f_wadd":"matadd", "f_transpose":"transpose", "f_wmul":"matmul", "f_hadamard":"hadamard", "f_cap":"cap", "f_sigmoid":"sigmoid"}
        if eq.name in alter.keys():
            return alter[eq.name]+"("+",".join([from_treenode(child) for child in eq.children])+")"

        alter2 = {"f_add":"+", "f_pow":"**", "f_mul":"+"}
        if eq.name in alter2.keys():
            return alter2[eq.name].join([from_treenode(child) for child in eq.children])
        
        if eq.name == "f_index":
            return from_treenode(eq.children[0])+"["+from_treenode(eq.children[1])+"]"

        if eq in w:
            return f"w[{w.index(eq)}]"
        
        if eq.name in ["f_F", "f_G"]:
            child = None
            active2 = copy.deepcopy(active)
            active2 = active2[eq.name[2:]]
            
            if len(eq.children) == 2:
                for _ in range(int(eq.children[0].name[2:])):
                    active2 = diff2(TreeNode("f_dif", [active2, parse("Z")]))
                child = eq.children[1]
            else:
                child = eq.children[0]
                
            return from_treenode(matrix_solve(replace(active2, parse("Z"), child)))
        
        if eq.name == "f_len":
            return "len("+from_treenode(eq.children[0])+")"
        
        return str(eq)
    return from_treenode(eq)
def cap(a, b, x, y, val):
    arr = zeros(a,b)
    arr[x][y] = val
    return arr

class NeuralNetwork:
    def __init__(self, struct, rand_range=None, active=None):
        self.struct = struct
        self.update_fx = {}
        self.var_list = [tree_form(f"v_-{i}") for i in range(1,26+1-4) if tree_form(f"v_-{i}") not in [parse("G"), parse("F")]]
        if active is None:
            self.active = {"F":parse("sigmoid(Z)"), "G":parse("sigmoid(Z)")}
        else:
            self.active = active
        self.o = None
        self.lst_w = None
        self.gradient = None
        self.learn = None
        self.model_type = None
        if rand_range is None:
            self.init_mat = lambda x,y: zeros(x, y)
        else:
            self.init_mat = lambda x,y: randos(rand_range[0], rand_range[1], x, y)
    def model(self, t="dense"):
        self.model_type = t
        if t == "dense":
            return self.model_dense()
        else:
            return self.model_rnn_vanilla()
    def model_dense(self):
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
            eq = TreeNode("f_wmul", [lst_z[-1], lst_w[-1]])
            eq = TreeNode("f_wadd", [eq, lst_b[-1]])
            lst_z.append(eq)
            lst_z[-1] = matrix_solve(lst_z[-1].fx("F"))
        self.lst_w = lst_w + lst_b
        self.o = lst_z[-1]
        eq = TreeNode("f_hadamard", [tree_form("d_-1"), y])
        eq = TreeNode("f_wadd", [self.o, eq])
        eq = copy.deepcopy(eq)
        L = TreeNode("f_wmul", [eq,eq.fx("transpose")])
        L = TreeNode("f_hadamard", [L, tree_form("d_2")**tree_form("d_-1")])
        L = matrix_solve(L)
        gradient = []
        for i in range(2):
            for j in range(len(self.struct)-1):
                item = [lst_w, lst_b][i][j]
                if i == 0:
                    item = TreeNode("f_index", [TreeNode("f_index", [item, tree_form("v_11")]), parse("j")])
                else:
                    item = TreeNode("f_index", [TreeNode("f_index", [item, tree_form("d_0")]), parse("j")])
                tmp = diff2(TreeNode("f_pdif", [L, item]))
                eq = TreeNode("f_hadamard", [tree_form("d_-1").fx("list").fx("list"), parse("n").fx("list").fx("list"),tmp])
                eq = TreeNode("f_wadd", [parse("z").fx("list").fx("list"), eq])
                eq = matrix_solve(eq)
                gradient.append(eq)
        self.gradient = gradient
        lst_1 = []
        lst_2 = []
        for i in range(1,len(self.struct)):
            lst_1.append(self.init_mat(1, self.struct[i]))
            lst_2.append(self.init_mat(self.struct[i-1], self.struct[i]))
        self.learn = lst_2 + lst_1
        return self
    def model_rnn_vanilla(self):
        Hht0 = self.var_list.pop(0)
        lst_Hht = [Hht0]
        Wxh = self.var_list.pop(0)
        Whh = self.var_list.pop(0)
        Why = self.var_list.pop(0)
        Bh = self.var_list.pop(0)
        By = self.var_list.pop(0)
        var_i = tree_form("v_11")
        var_j = parse("j")
        x = parse("X")
        y = parse("Y")
        lst_o = []
        for i in range(self.struct[3]):
            eq = TreeNode("f_wadd", [TreeNode("f_wmul", [TreeNode("f_index",[x,tree_form(f"d_{i}")]) , Wxh]) , TreeNode("f_wmul", [lst_Hht[i], Whh]) , Bh])
            lst_Hht.append(eq.fx("F"))
            eq = TreeNode("f_wadd", [TreeNode("f_wmul", [lst_Hht[-1], Why]) , By])
            lst_o.append(eq.fx("G"))
        self.lst_w = [Wxh, Whh, Why, By, Bh, Hht0]
        self.o = lst_o
        L_lst = []
        for i, item in enumerate(self.o):
            eq = TreeNode("f_index", [y, tree_form(f"d_{i}")])
            eq = TreeNode("f_hadamard", [eq, tree_form("d_-1")])
            eq = TreeNode("f_wadd", [eq, item])
            eq = TreeNode("f_wmul", [eq, eq.fx("transpose")])
            eq = TreeNode("f_hadamard", [eq, tree_form("d_2") ** tree_form("d_-1")])
            L_lst.append(eq)
        L = operation("f_wadd", L_lst)
        L = matrix_solve(L)
        gradient = []
        # x, y, h, t
        for i in range(2):
            for j in range(3):
                item = [[Wxh, Whh, Why], [By, Bh, Hht0]][i][j]
                if i == 0:
                    item = TreeNode("f_index", [TreeNode("f_index", [item, tree_form("v_11")]), parse("j")])
                else:
                    item = TreeNode("f_index", [TreeNode("f_index", [item, tree_form("d_0")]), parse("j")])
                tmp = diff2(TreeNode("f_pdif", [L, item]))
                eq = TreeNode("f_hadamard", [tree_form("d_-1").fx("list").fx("list"), parse("n").fx("list").fx("list"),tmp])
                eq = TreeNode("f_wadd", [parse("z").fx("list").fx("list"), eq])
                eq = matrix_solve(eq)
                gradient.append(eq)
        self.gradient = gradient
        lst_1 = []
        for item in [[self.struct[0], self.struct[2]], [self.struct[2], self.struct[2]], [self.struct[2], self.struct[1]],\
                     [1, self.struct[1]], [1, self.struct[2]], [1,self.struct[2]]]:
            lst_1.append(self.init_mat(*item))
        self.learn = lst_1
        return self
    def predict(self, given_x):
        global shape, exp, hadamard, zeros, matmul, transpose, matadd, tanh, sigmoid, inv
        env = {
            "w": self.learn,
            "cap": cap,
            "X": [given_x] if self.model_type == "dense" else transpose([transpose(given_x)]),
            "transpose":transpose,
            "matmul":matmul,
            "zeros":zeros,
            "hadamard": hadamard,
            "exp":exp,
            "tanh":tanh,
            "sigmoid":sigmoid,
            "matadd": matadd,
            "inv":inv
        }
        if self.model_type == "dense":
            return eval(gen2(self.o, self.lst_w, self.active), {}, env)[0]
        else:
            return transpose([eval(gen2(item, self.lst_w, self.active), {}, env)[0] for item in self.o])
    def train(self, train_x, train_y, learning_rate, epoch):
        global shape, exp, hadamard, zeros, matmul, transpose, matadd, tanh, sigmoid, inv
        if self.model_type != "dense":
            train_x = [transpose(item) for item in train_x]
            train_y = [transpose(item) for item in train_y]
        env = {
            "cap": cap,
            "n": learning_rate,
            "sigmoid":sigmoid,
            "matadd": matadd,
            "transpose":transpose,
            "matmul":matmul,
            "zeros":zeros,
            "hadamard": hadamard,
            "exp":exp,
            "tanh":tanh,
            "inv":inv
        }
        for j in range(len(self.lst_w)):
            tmp = f"fx_{j} = lambda z,X,Y,i,j,w: "+gen2(self.gradient[j], self.lst_w, self.active)
            exec(tmp, env)
        for k in range(epoch):            
            for data_index in range(len(train_x)):
                learn_new = copy.deepcopy(self.learn)
                data_x = None
                data_y = None
                if self.model_type == "dense":
                    data_x = [train_x[data_index]]
                    data_y = [train_y[data_index]]
                else:
                    data_x = transpose([train_x[data_index]])
                    data_y = transpose([train_y[data_index]])
                for j in range(len(self.lst_w)):
                    s = shape(self.learn[j])
                    for x in range(s[0]):
                        for y in range(s[1]):
                            z = self.learn[j][x][y]
                            out = env[f"fx_{j}"](z, data_x, data_y, x, y, self.learn)
                            learn_new[j][x][y] = out[0][0]
                self.learn = copy.deepcopy(learn_new)
            if k % round(epoch/10.0) == 0:
                print(f"epoches done {k+1}/{epoch}")
        print("training done.")
        print()
