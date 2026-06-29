from .simplify import simplify
from .base import *
def helper(eq):
    name = eq.name
    mat = False
    if name in ["f_dif", "f_pdif"]:
        if "v_" not in str_form(eq.children[0]):
            return tree_form("d_0")
    if name in ["f_dif", "f_pdif"] and contain2(eq.children[1],"f_index"):
        mat = True
        v = eq.children[1].children[0]
        d = 1
        if eq.children[1].children[0].name == "f_index":
            d = 2
            v = eq.children[1].children[0].children[0]
        if not contain(eq.children[0], v) and name == "f_pdif":
            return tree_form("d_0")
        if eq.children[1].children[0] == eq.children[0]:
            return TreeNode("f_cap", [tree_form("d_1"), eq.children[0].fx("len"), tree_form("d_0"), eq.children[1].children[1], tree_form("d_1")])
        if d ==2 and eq.children[1].children[0].children[0] == eq.children[0]:
            return TreeNode("f_cap", [eq.children[0].fx("len"),\
                                      TreeNode("f_index", [eq.children[0], tree_form("d_0")]).fx("len"),\
                                      eq.children[1].children[0].children[1], eq.children[1].children[1], tree_form("d_1")])
    if name in ["f_dif", "f_pdif"]:
        if eq.children[0].name == "f_list":
            return TreeNode("f_list", [TreeNode(name, [child, eq.children[1]]) for child in eq.children[0].children])
        
        if eq.children[0].name == "f_transpose":
            return TreeNode(name, [eq.children[0].children[0], eq.children[1]]).fx("transpose")
        
        if eq.children[0].name in ["f_add", "f_wadd"]:
            return operation(eq.children[0].name, [TreeNode(name, [child, eq.children[1]]) for child in eq.children[0].children])
        if eq.children[0].name in ["f_mul", "f_wmul", "f_hadamard"]:
            op = eq.children[0].name
            op2 = "f_wadd"
            if op == "f_mul":
                op2 = "f_add"
            tmp = operation(op2, [
                operation(
                    op,
                    [
                        TreeNode(name, [child, eq.children[1]])
                        if index == index2
                        else child
                        for index2, child in enumerate(eq.children[0].children)
                    ]
                )
                for index in range(len(eq.children[0].children))
            ])
            return tmp
        if eq.children[0].name == "f_pow" and "v_" not in str_form(eq.children[0].children[1]):
            base, power = eq.children[0].children
            dbase = TreeNode(name, [base, eq.children[1]])
            b1 = power - tree_form("d_1")
            bab1 = TreeNode("f_pow", [base, b1])
            return power * bab1 * dbase
        if eq.children[0].name == "f_pow":
            a, b = eq.children
            return a**b * ((b/a) * TreeNode(name, [a, eq.children[1]]) + a.fx("log") * TreeNode(name, [b, eq.children[1]]))

        if eq.children[0] == eq.children[1]:
            return tree_form("d_1")
        if name == "f_pdif" and not contain(eq.children[0], eq.children[1]) and not mat:
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
        if eq.children[0].name in ["f_F", "f_G", "f_sigmoid"]:
            op = "f_hadamard"               
            if len(eq.children[0].children) == 1:
                a = TreeNode(eq.children[0].name, [tree_form("d_1"), eq.children[0].children[0]])
                b = TreeNode(name, [eq.children[0].children[0], eq.children[1]])
                return TreeNode(op, [a,b])
            else:
                a = TreeNode(eq.children[0].name, [tree_form("d_1")+eq.children[0].children[0], eq.children[0].children[1]])
                b = TreeNode(name, [eq.children[0].children[1], eq.children[1]])
                return TreeNode(op, [a,b])
    return eq
def diff2(eq):
    if eq is None:
        return None
    return dowhile(eq, lambda x: transform_dfs(x, helper))
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
