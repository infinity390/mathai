from .structure import structure
from .base import *
from .parser import parse
from .simplify import simplify
from .expand import expand
from .diff import diff
from .trig import trig0
from .fraction import fraction
from .tool import poly
from .printeq import print_raw
def substitute_val(eq, val, var="v_0"):
    eq = replace(eq, tree_form(var), tree_form("d_"+str(val)))
    return eq
def subslimit(equation, var):
    equation2 = trig0(replace(equation, var, tree_form("d_0")))
    try:
        tmp = simplify(equation2)
        return simplify(expand(tmp))
    except:
        return None
def check(num, den, var, name):
    n, d = None, None
    if name == "f_limit":
        n, d = (dowhile(replace(e, tree_form(var), tree_form("d_0")), lambda x: trig0(simplify(x))) for e in (num, den))
    else:
        n, d = limit3(TreeNode("f_limitpinf", [num, tree_form(var)]), True), limit3(TreeNode("f_limitpinf", [den, tree_form(var)]), True)
    if n is None or d is None:
        return False
    
    if name == "f_limit" and n == 0 and d == 0: return True
    elif name == "f_limitpinf":
        if n == tree_form("s_inf") and d == tree_form("s_inf"):
            return True
        else:
            n, d = num, den
    if d != 0:
        return simplify(n/d)
    return False
def lhospital(num, den, steps,var, name):
    out = check(num, den, var, name)
    if isinstance(out, TreeNode):
        return out
    for _ in range(steps):
        num2, den2 = map(lambda e: simplify(diff(e, var)), (num, den))
        out = check(num2, den2, var, name)
        if out is True:
            num, den = num2, den2
            continue
        if out is False:
            eq2 = simplify(fraction(simplify(num/den)))
            return eq2
        return out
def lhospital2(eq, var, name):
    eq=  simplify(eq)
    if eq is None:
        return None
    if not contain(eq, tree_form(var)):
        return eq
    num, dem = [simplify(item) for item in num_dem(eq)]
    if num is None or dem is None:
        return eq
    return lhospital(num, dem, 10,var, name)
def limit0(equation):
    equation = copy.deepcopy(equation)
    limit_tags = ["f_limit", "f_limitpinf", "f_limitninf"]
    if equation.name not in limit_tags:
        return TreeNode(
            equation.name,
            [limit0(child) for child in equation.children]
        )
    expr = equation.children[0]
    wrt = equation.children[1]
    factors = factor_generation(expr)
    const_factors = []
    var_factors = []
    for f in factors:
        if contain(f, wrt):
            var_factors.append(f)
        else:
            const_factors.append(f)
    if const_factors == []:
        new_expr = expr
        const_part = tree_form("d_1")
    else:
        const_part = simplify(product(const_factors))
        new_expr = product(var_factors)
    inner_limit = TreeNode(
        equation.name,
        [
            limit0(new_expr),
            wrt
        ]
    )
    if const_factors == []:
        return inner_limit
    return simplify(const_part) * inner_limit
def limit2(eq):
    g = ["f_limit", "f_limitpinf", "f_limitninf"]
    if eq.name in g and eq.children[0].name == "f_add":
        eq = summation([TreeNode(eq.name, [child, eq.children[1]]) for child in eq.children[0].children])
    return TreeNode(eq.name, [limit2(child) for child in eq.children])
def limit1(eq):
    if eq.name in ["f_limitpinf", "f_limit"]:
        a, b = limit(eq.children[0], eq.children[1].name, eq.name)
        if b:
            return a
        else:
            return TreeNode(eq.name, [a, eq.children[1]])
    return TreeNode(eq.name, [limit1(child) for child in eq.children])
def replace_abs_var_h(eq, pos, wrt):
    if eq in pos:
        return tree_form("d_-1")
    
    if eq.name.startswith("v_") and (wrt is None or eq!=wrt):
        return tree_form("d_1")
    return eq
def replace_abs_var(eq, pos, wrt=None):
    return transform_dfs(eq, replace_abs_var_h, [pos, wrt])
def fxinf2(eq):
    if eq is None:
        return None
    orig = eq
    if not contain(eq, tree_form("s_inf")):
        eq = simplify(eq)
    if eq.name == "f_add":
        if tree_form("s_inf") in eq.children and -tree_form("s_inf") in eq.children:
            return None
        if tree_form("s_inf") in eq.children:
            return tree_form("s_inf")
        if -tree_form("s_inf") in eq.children:
            return -tree_form("s_inf")
    if eq.name == "f_pow":
        pass
        '''
        if "v_" not in str_form(eq.children[0]) and not contain(eq.children[0],tree_form("s_inf")) and simplify(eq.children[0]) != 1 and compute(eq.children[0]) > 1:
            if eq.children[1] == -tree_form("s_inf"):
                return tree_form("d_0")
        '''
    
    return eq
def fxinf3(eq, pos=[]):
    if eq is None:
        return None
    orig = eq
    n, d = num_dem(eq)
    nlst = [item for item in factor_generation(n) if item != 1]
    dlst = [item for item in factor_generation(d) if item != 1]
    enter = True
    a = contain(n, tree_form("s_inf"))
    b = contain(d, tree_form("s_inf"))
    if a:
        if all(item == tree_form("s_inf") or not contain(item,tree_form("s_inf")) for item in nlst):
            pass
        else:
            enter = False
    if b:
        if all(item == tree_form("s_inf") or not contain(item,tree_form("s_inf")) for item in dlst):
            pass
        else:
            enter = False
    if enter:
        if d == 0:
            return None
        if n == 0:
            return tree_form("d_0")
        if not a and not b:
            return eq
        if not a and b:
            return tree_form("d_0")
        if not b and a:
            if compute(d) > 0:
                return n
            else:
                return -n
        if a and b:
            return None
    return eq
def fxinf(eq, pos=[]):
    if eq is None:
        return None
    lst = [item for item in factor_generation(eq) if item != 1]
    sign = 1
    inf = (tree_form("s_inf") in lst)
    inf_inv = (tree_form("s_inf")**-1 in lst)
    for i in range(len(lst)-1,-1,-1):
        if not contain(lst[i], tree_form("s_inf")):
            lst[i] = simplify(lst[i])
        if lst[i] == 0:
            return tree_form("d_0")
        if not contain(lst[i], tree_form("s_inf")) and (inf or inf_inv):
            if lst[i] == 0:
                return tree_form("d_0")
            if compute(lst[i])<0:
                sign *= -1
            lst.pop(i)
        elif lst[i] == tree_form("s_inf"):
            inf = True
            lst.pop(i)
        elif lst[i] == tree_form("s_inf")**-1:
            inf_inv = True
            lst.pop(i)
        elif lst[i] == 1:
            lst.pop(i)
    if sign == -1:
        lst.append(tree_form("d_-1"))
    if inf:
        lst.append(tree_form("s_inf"))
    if inf_inv:
        lst.append(tree_form("s_inf")**-1)
    lst = [item for item in lst if item != 1]
    out = product(lst)
    return out
def sep_const_h(eq, wrt):
    if eq.name == "f_pow":
        eq.children[1] = expand(eq.children[1])
        if eq.children[1].name == "f_add" and contain(eq.children[1], wrt):
            return product([eq.children[0]**item for item in eq.children[1].children])
    return eq
def sep_const(eq, wrt):
    return transform_dfs(eq, sep_const_h, [wrt])
def fxinf4_h(node, parent=None):
    if node is None:
        return None
    temp = node
    einf = simplify(tree_form("s_e")**(tree_form("d_-1")*tree_form("s_inf")))
    if parent == "f_mul":
        temp = flatten_tree(temp)
        lst = set(map(simplify, factor_generation(temp)))
        if lst == set(map(simplify, [tree_form("s_inf"), einf])):
            return tree_form("d_0")
        if einf in lst:
            lst = lst - set([einf])
            if len(lst) == 0 or not contain(product(list(lst)), tree_form("s_inf")):
                return tree_form("d_0")
    return temp
def fxinf6_h(node, parent=None):
    if node is None:
        return None
    temp = node
    einf = simplify(tree_form("s_e")**(tree_form("d_-1")*tree_form("s_inf")))
    if simplify(node) == einf:
        return tree_form("d_0")
    return temp
def fxinf5_h(node, parent=None):
    if node is None:
        return None
    temp = node
    temp = flatten_tree(temp)
    temp = fxinf(temp)
    temp = flatten_tree(temp)
    temp = fxinf2(temp)
    if parent != "f_mul":
        temp = flatten_tree(temp)
        temp = fxinf3(temp)
    return temp
def fxinf5(node, parent=None):
    return transform_dfs_parent(node, fxinf5_h, parent, [])
def fxinf4(node, parent=None):
    return transform_dfs_parent(node, fxinf4_h, parent, [])
def fxinf6(node, parent=None):
    return transform_dfs_parent(node, fxinf6_h, parent, [])
def limit4(equation):
    if equation.name == "f_limitpinf":
        if not contain(equation, equation.children[1]):
            return equation.children[0]
        eq = equation.children[0]
        n, d = num_dem(eq)
        n, d = simplify(n), simplify(d)
        v2 = tree_form(vlist(eq)[0])
        p1 = poly(n, v2.name)
        p2 = poly(d, v2.name)
        if p1 is not None and p2 is not None and len(p1)<=len(p2) and len(p1)>1 and len(p2)>1:
            v = simplify(v2**(len(p2)-1))
            return TreeNode("f_limitpinf", [simplify(expand(n/v)/expand(d/v)), equation.children[1]])
    return equation
def limit5(eq):
    if eq.name == "f_limit" and len(eq.children) == 3:
        return TreeNode("f_limit", [replace(eq.children[0], eq.children[1], eq.children[1]+eq.children[2]), eq.children[1]])
    return TreeNode(eq.name, [limit5(child) for child in eq.children])
def limit3(eq, allowinf=False, pos=[]):
    if eq.name == "f_limitpinf":
        if not contain(eq, eq.children[1]):
            return eq.children[0]
        eq.children[0] = sep_const(simplify(eq.children[0]), eq.children[1])
        eq2 = replace(eq.children[0], eq.children[1], tree_form("s_inf"))
        eq2 = replace_abs_var(eq2, pos)
        eq2 = dowhile(eq2, lambda x: fxinf5(x, x.name))
        eq2 = dowhile(eq2, lambda x: fxinf4(x, x.name))
        eq2 = dowhile(eq2, lambda x: fxinf6(x, x.name))
        if (allowinf or not contain(eq2, tree_form("s_inf"))) and not contain(eq2, eq.children[1]):
            return simplify(eq2)
    return TreeNode(eq.name, [limit3(child) for child in eq.children])
def limit(equation, var="v_0", name = "f_limit"):
    eq2 = dowhile(replace(equation, tree_form(var), tree_form("d_0")), lambda x: trig0(simplify(x)))
    if eq2 is not None and not contain(equation, tree_form(var)):
        return eq2, True
    equation =  lhospital2(equation, var, name)
    equation = simplify(expand(simplify(equation)))
    if not contain(equation, tree_form(var)):
        return equation, True
    return equation, False
