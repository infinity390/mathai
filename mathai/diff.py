from .simplify import simplify
from .base import *
def helper(eq):
    name = eq.name
    if name in ["f_dif", "f_pdif"]:
        if eq.children[0].name == "f_add":
            return summation([TreeNode(name, [child, eq.children[1]]) for child in eq.children[0].children])
        if eq.children[0].name == "f_mul":
            return summation([product([TreeNode(name, [child, eq.children[1]]) if index==index2 else child for index2, child in enumerate(eq.children[0].children)])\
                              for index in range(len(eq.children[0].children))])
        if eq.children[0].name == "f_pow" and "v_" not in str_form(eq.children[0].children[1]):
            base, power = eq.children[0].children
            dbase = TreeNode(name, [base, eq.children[1]])
            b1 = power - tree_form("d_1")
            bab1 = TreeNode("f_pow", [base, b1])
            return power * bab1 * dbase
        if eq.children[0].name == "f_pow":
            a, b = eq.children
            return a**b * ((b/a) * TreeNode(name, [a, eq.children[1]]) + a.fx("log") * TreeNode(name, [b, eq.children[1]]))
        if "v_" not in str_form(eq.children[0]):
            return tree_form("d_0")
        if eq.children[0] == eq.children[1]:
            return tree_form("d_1")
        if name == "f_pdif" and not contain(eq.children[0], eq.children[1]):
            return tree_form("d_0")
        if eq.children[0].name == "f_sin":
            eq.children[0].name = "f_cos"
            d =  TreeNode(name, [eq.children[0].children[0], eq.children[1]])
            return d*eq.children[0]
        if eq.children[0].name == "f_cos":
            eq.children[0].name = "f_sin"
            d =  TreeNode(name, [eq.children[0].children[0], eq.children[1]])
            return tree_form("d_-1")*d*eq.children[0]
        if eq.children[0].name == "f_tan":
            d =  TreeNode(name, [eq.children[0].children[0], eq.children[1]])
            return d/(eq.children[0].children[0].fx("cos")*eq.children[0].children[0].fx("cos"))
        if eq.children[0].name == "f_log":
            d =  TreeNode(name, [eq.children[0].children[0], eq.children[1]])
            return d*(tree_form("d_1")/eq.children[0].children[0])
        if eq.children[0].name == "f_arcsin":
            d =  TreeNode(name, [eq.children[0].children[0], eq.children[1]])
            return d/(tree_form("d_1")-eq.children[0].children[0]*eq.children[0].children[0])**(tree_form("d_2")**-1)
        if eq.children[0].name == "f_arccos":
            d =  TreeNode(name, [eq.children[0].children[0], eq.children[1]])
            return tree_form("d_-1")*d/(tree_form("d_1")-eq.children[0].children[0]*eq.children[0].children[0])**(tree_form("d_2")**-1)
        if eq.children[0].name == "f_arctan":
            d =  TreeNode(name, [eq.children[0].children[0], eq.children[1]])
            return d/(tree_form("d_1")+eq.children[0].children[0]*eq.children[0].children[0])
    return eq
def diff3(eq):
    if eq is None:
        return None
    eq = simplify(eq)
    if eq is None:
        return None
    stack = [(eq, False)]
    out = {}
    while stack:
        node, visited = stack.pop()
        if not visited:
            stack.append((node, True))
            for c in node.children:
                stack.append((c, False))
            continue
        new_children = [out[c] for c in node.children]
        rebuilt = TreeNode(node.name, new_children)
        rebuilt = helper(rebuilt)
        rebuilt = simplify(rebuilt)
        out[node] = rebuilt
    return out[eq]
def diff2(eq):
    if eq is None:
        return None
    return dowhile(eq, diff3)
def diff(equation, var="v_0"):
    def diffeq(eq):
        eq = simplify(eq)
        if "v_" not in str_form(eq):
            return tree_form("d_0")
        if eq.name == "f_add":
            add = tree_form("d_0")
            for child in eq.children:
                add += diffeq(child)
            return add
        elif eq.name == "f_abs":
            return diffeq(eq.children[0])*eq.children[0]/eq
        elif eq.name == "f_pow" and eq.children[0].name == "s_e":
            return diffeq(eq.children[1])*eq
        elif eq.name == "f_tan":
            return diffeq(eq.children[0])/(eq.children[0].fx("cos")*eq.children[0].fx("cos"))
        elif eq.name == "f_log":
            return diffeq(eq.children[0])*(tree_form("d_1")/eq.children[0])
        elif eq.name == "f_arcsin":
            return diffeq(eq.children[0])/(tree_form("d_1")-eq.children[0]*eq.children[0])**(tree_form("d_2")**-1)
        elif eq.name == "f_arccos":
            return tree_form("d_-1")*diffeq(eq.children[0])/(tree_form("d_1")-eq.children[0]*eq.children[0])**(tree_form("d_2")**-1)
        elif eq.name == "f_arctan":
            return diffeq(eq.children[0])/(tree_form("d_1")+eq.children[0]*eq.children[0])
        elif eq.name == "f_pow" and "v_" in str_form(eq.children[1]):
            a, b = eq.children
            return a**b * ((b/a) * diffeq(a) + a.fx("log") * diffeq(b))
        elif eq.name == "f_mul":
            add = tree_form("d_0")
            for i in range(len(eq.children)):
                tmp = eq.children.pop(i)
                if len(eq.children)==1:
                    eq2 = eq.children[0]
                else:
                    eq2 = eq
                add += diffeq(tmp)*eq2
                eq.children.insert(i, tmp)
            return add
        elif eq.name == "f_sin":
            eq.name = "f_cos"
            return diffeq(eq.children[0])*eq
        elif eq.name == "f_cos":
            eq.name = "f_sin"
            return tree_form("d_-1")*diffeq(eq.children[0])*eq
        elif eq.name[:2] == "v_":
            return TreeNode("f_dif", [eq])
        elif eq.name == "f_pow" and "v_" not in str_form(eq.children[1]):
            base, power = eq.children
            dbase = diffeq(base)
            b1 = power - tree_form("d_1")
            bab1 = TreeNode("f_pow", [base, b1])
            return power * bab1 * dbase
        return TreeNode("f_dif", [eq, tree_form(var)])
    def helper2(equation, var="v_0"):
        if equation.name == "f_dif":
            if equation.children[0].name == var:
                return tree_form("d_1")
            if not contain(equation.children[0], var):
                return tree_form("d_0")
            else:
                return equation
        return TreeNode(equation.name, [helper2(child, var) for child in equation.children])
    def calc(eq):
        if eq.name == "f_dif":
            return diffeq(eq.children[0])
        return TreeNode(eq.name, [calc(child) for child in eq.children])
    if var is None:
        return simplify(calc(equation))
    equation = diffeq(equation)
    equation = helper2(equation, var)
    return simplify(equation)
