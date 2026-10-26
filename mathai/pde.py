from .base import *
from .inverse import inverse
from .ode import diffsolve as ode_solve
from .integrate import integrate_formula
from .simplify import simplify
from .formula_applier import formula_applier
from .formula_compiler import formula_list_compiler

pde_character_s = """a*pdif(u,x)+b*pdif(u,y)+c=0 list(dif(x,y)=a/b,dif(u,x)=-c/a,dif(u,y)=-c/b,u) [[c,0],[a,1],[b,1]] [u,x,y] _ _ _"""
pde_character = lambda x: formula_applier(x, pde_character_s)

def solve_pde(eq):
    def conv(eq):
        lst = list(dict.fromkeys(vlist(eq)))
        lst = [item for item in lst if item not in ("v_0", "v_1")]
        lst2 = [f"v_{i}" for i in range(5) if f"v_{i}" not in vlist(eq)]
        dic = {}
        dic2 = {}
        for i, item in enumerate(lst):
            new = lst2[i]
            dic[item] = new
            dic2[new] = item
        def to_v(eq):
            for key, item in dic.items():
                eq = replace(eq, TreeNode(key), TreeNode(item))
            return eq
        def from_v(eq):
            for key, item in dic2.items():
                eq = replace(eq, TreeNode(key), TreeNode(item))
            return eq
        return to_v, from_v
    eq = pde_character(eq)
    u = eq.children.pop(-1)
    lst = []
    for child in eq.children:
        f, g = conv(child)
        tmp = f(child)
        tmp = simplify(integrate_formula(ode_solve(tmp)))
        tmp = g(tmp)
        lst.append(inverse(tmp.children[0], f"v_101"))
    lst = TreeNode("f_eq", [lst[1], lst[0].fx("f")])
    return u, inverse(simplify(lst).children[0], u.name)

