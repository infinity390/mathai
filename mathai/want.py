from .univariate_inequality import eq2range, simple_wavycurvy
from .base import *
from .logic import distribute, logic0
def only_var(eq, var):
    if not contain(eq, var):
        return False
    for item in vlist(eq):
        item = tree_form(item)
        if item == var:
            continue
        if contain(eq, item):
            return False
    return True
def extract_true_var(eq, var):
    if only_var(eq, var):
        return eq
    if eq.name == "f_and":
        lst = []
        for child in eq.children:
            if only_var(child, var):
                lst.append(child)
        if len(lst) == 0:
            return None
        if len(lst) == 1:
            return lst[0]
        return TreeNode("f_and", lst)
    if eq.name == "f_or":
        lst = []
        for child in eq.children:
            out = extract_true_var(child, var)
            if out is None:
                return None
            lst.append(out)
        if len(lst) == 1:
            return lst[0]
        return TreeNode("f_or", lst)
    return None
def solve_want_h(eq):
    if eq.name == "f_want" and len(eq.children) == 2:
        var = eq.children[0]
        if eq.children[0].name[:2] != "v_":
            for i in range(26):
                if "v_"+str(i) not in vlist(eq):
                    var = tree_form("v_"+str(i))
                    break
        out = extract_true_var(eq.children[1], var)
        if out is not None:
            eq = TreeNode(eq.name, [eq.children[0], out])
        if eq.children[0].name[:2] == "v_":
            if eq.children[1].name == "f_and":
                for child in eq.children[1].children:
                    if child.name == "f_range":
                        child = eq2range(child)
                        if child.variable == eq.children[0] and child.r == [False] and child.z == []:
                            if len(child.p) == 1:
                                return child.p[0]
            elif eq.children[1].name == "f_range":
                child = eq2range(eq.children[1])
                if child.variable == eq.children[0] and child.r == [False] and child.z == [] and len(child.p) == 1:
                    return child.p[0]
        else:
            return TreeNode("f_want", [var, TreeNode("f_eq", [eq.children[0]-var, tree_form("d_0")])&eq.children[1]])
    return eq
def solve_want(eq):
    var = None
    for i in range(26):
        if "v_"+str(i) not in vlist(eq):
            var = tree_form("v_"+str(i))
            break
    out = dowhile(eq, lambda y: simple_wavycurvy(transform_dfs(y, solve_want_h, [])))
    return out
