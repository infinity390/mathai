from .factor import factor2
from .factor import factorconst as factor0
from .factor import factor as factor1
from .parser import parse
import itertools
from .diff import diff
from .fraction import fraction
from .simplify import simplify
from .expand import expand
from .base import *
from .structure import transform_formula
from .inverse import inverse
from .tool import poly
from fractions import Fraction
from .trig import trig0, trig2, trig3, trig4, trig1, trig5, trig6
from .apart import apart, apart2
from .univariate_inequality import wavycurvy, eq2range, range2eq2, Range
from .printeq import *
def integrate_summation(equation):
    if equation.name == "f_ref":
        return equation
    eq2 = equation
    if eq2.name == "f_integrate":
        equation = eq2.children[0]
        wrt = eq2.children[1]
        if equation.name == "f_add":
            return summation([TreeNode("f_integrate", [child, wrt]) for child in equation.children])
        equation = eq2
    return TreeNode(equation.name, [integrate_summation(child) for child in equation.children])
def subs_heuristic(eq, var):
    output = []
    last = []
    def collect2(eq):
        if eq.name == "f_pow" and frac(eq.children[1]) is not None and frac(eq.children[1]) == Fraction(1,2):
            if eq.children[0] == var:
                output.append(str_form(eq))
        if eq.name in ["f_pow"] and var.name in str_form(eq):
            if eq.children[1].name[:2] != "v_":
                output.append(str_form(eq))
        if eq.name in ["f_pow", "f_sin", "f_cos", "f_arcsin"] and var.name in str_form(eq.children[0]):
            if eq.children[0].name[:2] != "v_":
                output.append(str_form(eq.children[0]))
            if eq.name in ["f_sin", "f_cos"]:
                output.append(str_form(eq))
                last.append(eq.children[0].fx("tan"))
                if eq.children[0].name[:2] != "v_":
                    output.append(str_form(eq.children[0]))
        if eq.name == "f_pow" and eq.children[0].name == "s_e" and "v_" in str_form(eq):
            if eq.children[1].name[:2] != "v_":
                output.append(str_form(eq.children[1]))
            output.append(str_form(eq))
        for child in eq.children:
            collect2(child)
    def collect3(eq):
        if eq.name in ["f_sin", "f_cos"]:
            output.append(str_form(eq.children[0].fx("cos")))
        for child in eq.children:
            collect3(child)  
    collect2(eq)
    
    if output == []:
        collect3(eq)
    tmp = list(set([simplify(tree_form(x)) for x in output]))
    tmp = sorted(tmp, key=lambda x: len(str_form(x)))
    poly_term = None
    term_degree = 20
    output = []
    
    for item in tmp:
        n = poly(simplify(item), var.name)
        if n is None:
            output.append(item)
        else:
            if term_degree > len(n):
                poly_term = item
                term_degree = len(n)
    p = None
    if poly_term is None:
        p = tmp
    else:
        p = [poly_term]+output
    last = list(set(last))
    if len(p)>3:
        p = p[:3]
    elif len(p)<3:
        p = (p+last)[:3]
    return p
try_index = []
try_lst = []
def ref(eq):
    if eq.name  == "f_integrate":
        return TreeNode("f_try", [eq.fx("ref"), eq])
    return TreeNode(eq.name, [ref(child) for child in eq.children])
def place_try(eq):
    global try_index
    if eq.name == "f_try":
        try_index.append(list(range(len(eq.children))))
    return TreeNode(eq.name, [place_try(child) for child in eq.children])
def place_try2(eq):
    global try_lst
    if eq.name == "f_try":
        return eq.children[try_lst.pop(0)]
    return TreeNode(eq.name, [place_try2(child) for child in eq.children]) 
def _solve_integrate(eq):
    if eq is None:
        return None
    if eq.name == "f_subs":
        if all(not contain2(eq.children[0], item) for item in ["f_integrate", "f_subs", "f_try"]):
            return replace(copy.deepcopy(eq.children[0]), eq.children[1], eq.children[2])
    if eq.name == "f_try":
        for child in eq.children:
            if not contain2(child, "f_integrate"):
                return child
    return eq
def handle_try(eq):
    global try_lst, try_index
    if eq.name == "f_try":
        try_lst = []
        try_index = []
        for child in eq.children:
            place_try(child)
        output = []
        for item in itertools.product(*try_index):
            try_lst = list(item)
            output += [place_try2(child) for child in eq.children]
        return TreeNode("f_try", output)
    else:
        return TreeNode(eq.name, [handle_try(child) for child in eq.children])
def inteq(eq):
    if eq.name == "f_try":
        eq2 = None
        output = []
        for child in eq.children:
            if child.name == "f_ref":
                eq2 = child.children[0]
                break
        if eq2 is None:
            return eq
        for child in eq.children:
            if child.name == "f_ref":
                output.append(child)
            else:
                eq3 = simplify(expand(simplify(eq2 - child)))
                if contain(eq3, eq2):
                    out = inverse(eq3, str_form(eq2))
                    if out is None:
                        output.append(child)
                    else:
                        output.append(out)
                else:
                    output.append(child)
        return TreeNode("f_try", output)
    else:
        return TreeNode(eq.name, [inteq(child) for child in eq.children])
def rm(eq):
    if eq is None:
        return None
    if eq.name == "f_try":
        eq = TreeNode(eq.name, list(set(eq.children)))
    return TreeNode(eq.name, [rm(child) for child in eq.children if child is not None])
def solve_integrate(eq):
    fx = lambda x: transform_dfs(x, _solve_integrate, [])
    eq2 = dowhile(eq, fx)
    eq2 = rm(eq2)
    if eq2 is None:
        return None
    if eq2.name == "f_try":
        eq2.children = list(set(eq2.children))
    return eq2
def integrate_subs(equation, term, v1, v2):
    output = []
    orig = equation.copy_tree()
    none = TreeNode("f_integrate",[orig, tree_form(v1)])
    origv2 = copy.deepcopy(v2)
    equation = simplify(equation)
    eq = equation
    termeq = term
    t = inverse(copy.deepcopy(termeq), v1)
    g = inverse(termeq, v2)
    if g is None:
        return none
    if t is None:
        return none
    else:
        t = expand(t)
        eq = replace(eq, tree_form(v1), t)
        eq2 = replace(diff(g, v1), tree_form(v1), t)
        equation = eq/eq2
        equation = simplify(equation)
    if v1 in str_form(equation):
        return none
    return dowhile(TreeNode("f_subs", [TreeNode("f_integrate", [simplify(equation), tree_form(origv2)]),tree_form(origv2) ,g]), lambda x: simplify(trig4(trig0(x))))
def integrate_subs_main_helper(equation):
    eq2 = equation
    if eq2.name == "f_integrate":
        output = []
        wrt = eq2.children[1]
        eq = equation.children[0]
        v2 = "v_"+str(int(wrt.name[2:])+1)
        for item in subs_heuristic(eq, wrt):
            x = tree_form(v2)-item
            output.append(integrate_subs(eq, x, wrt.name, v2))
        output = list(set(output)-{eq2})
        if len(output) == 1:
            return output[0]
        if len(output) == 0:
            return equation
        return TreeNode("f_try", [item.copy_tree() for item in output])
    return equation
def integrate_subs_main(equation):
    return transform_dfs(equation, integrate_subs_main_helper)
def _sqint(equation):
    def sgn(eq):
        if compute(eq) <0:
            return tree_form("d_-1"), tree_form("d_-1")*eq
        return tree_form("d_1"), eq
    eq2 = equation
    if eq2.name == "f_integrate":
        equation = eq2.children[0]
        var = eq2.children[1]
        one = tree_form("d_1")
        two = tree_form("d_2")
        four = tree_form("d_4")
        three = tree_form("d_3")
        root = tree_form("d_2")**-1
        zero = tree_form("d_0")
        n, d = num_dem(equation)
        n, d = simplify(n), simplify(d)
        term = [simplify(x) for x in factor_generation(d)]
        const = product([item for item in term if "v_" not in str_form(item)])
        term = [item for item in term if "v_" in str_form(item)]
        mode = False
        if all(item.name == "f_pow" and simplify(item.children[1]-root) == zero for item in term):
            d = simplify(expand(const**two*product([item.children[0] for item in term])))
        else:
            mode = True
            if any(item.name == "f_pow" and simplify(item.children[1]-root) == zero for item in term):
                return None
        if vlist(equation) == []:
            return None
        v = vlist(equation)[0]
        x = tree_form(v)
        np = poly(n, v)
        dp = poly(d, v)
        if np is None or dp is None:
            return None
        if len(np) == 1 and len(dp) == 3:
            k, a, b, c = np+dp
            if a == zero:
                return None
            s1, s2 = sgn(a)
            const = (four*a*c - b**two)/(four*a)
            t1, t2 = sgn(const)
            la = s2**root
            lb = b*s2**root/(two*a)
            if mode:
                if s1 == one:
                    if t1 == one:
                        if simplify(t2**root) == tree_form("d_0"):
                            return None
                        return k*((la*x+lb)/t2**root).fx("arctan")/(la * t2**root)
                    else:
                        return None
                else:
                    if t1 == one:
                        return None
                    else:
                        _, t2 = sgn(-const)
                        return -k*((la*x+lb)/t2**root).fx("arctan")/(la * t2**root)
            if s1 == one:
                if t1 == one:
                    return simplify(k*(la*x + lb + ((la*x + lb)**two + t2)**root).fx("abs").fx("log")/la)
                else:
                    return simplify(k*(la*x + lb + ((la*x + lb)**two - t2)**root).fx("abs").fx("log")/la)
            else:
                if t1 == one:
                    return k*((la*x + lb)/t2**root).fx("arcsin")/la
                else:
                    return None
        if len(np) == 2 and len(dp) == 3:
            p, q, a, b, c = np+dp
            if a == zero:
                return None
            A = p/(two*a)
            B = q - A*b
            t = a*x**two + b*x + c
            if not mode:
                tmp = _sqint(TreeNode("f_integrate", [simplify(one/t**root), var]))
                if tmp is None:
                    tmp = TreeNode("f_integrate", [simplify(one/t**root), var])
                return A*two*t**root + tmp*B
            else:
                tmp = _sqint(TreeNode("f_integrate", [simplify(one/t), var]))
                if tmp is None:
                    tmp = TreeNode("f_integrate", [simplify(one/t), var])
                return A*t.fx("abs").fx("log") + tmp*B
        equation = eq2
    coll = TreeNode(equation.name, [])
    for child in equation.children:
        out = _sqint(child)
        if out is None:
            coll.children.append(child)
        else:
            coll.children.append(out)
    return coll
def sqint(eq):
    eq = _sqint(eq)
    out = simplify(eq)
    if out is None:
        return eq
    return out
def byparts(eq):
    if eq.name == "f_ref":
        return eq
    eq2 = eq
    if eq2.name == "f_integrate":
        output = []
        eq = eq2.children[0]
        wrt = eq2.children[1]
        lst = factor_generation(eq)
        if len(lst) == 3 and len(list(set(lst))) == 1:
            lst = [(lst[0]**2).copy_tree(), lst[0].copy_tree()]
        if len(lst) == 3 and len(list(set(lst))) == 2:
            lst2 = list(set(lst))
            a, b = lst2
            a = a**lst.count(a)
            b = b**lst.count(b)
            lst = [a.copy_tree(), b.copy_tree()]
        if len(lst) == 1:
            lst += [tree_form("d_1")]
        if len(lst) == 2:
            for i in range(2):
                f, g = [lst[i], lst[1-i]]
                if contain(f, tree_form("s_e")):
                    continue
                out1 = TreeNode("f_integrate", [g.copy_tree(), wrt])
                out2 = TreeNode("f_integrate", [simplify(diff(f.copy_tree(), wrt.name)*out1), wrt])
                output.append(simplify(f.copy_tree() * out1 - out2))
        if len(output) == 0:
            pass
        elif len(output) == 1:
            return output[0]
        else:
            return TreeNode("f_try", output)
        eq = eq2
    return TreeNode(eq.name, [byparts(child) for child in eq.children])
def integration_formula_init():
    var = "x"
    formula_list = [
        (f"(A*{var}+B)^C", f"(A*{var}+B)^(C+1)/(A*(C+1))"),
        (f"sin(A*{var}+B)", f"-cos(A*{var}+B)/A"),
        (f"cos(A*{var}+B)", f"sin(A*{var}+B)/A"),
        (f"1/(A*{var}+B)", f"log(abs(A*{var}+B))/A"),
        (f"e^(A*{var}+B)", f"e^(A*{var}+B)/A"),
        (f"1/cos(A*{var}+B)", f"log(abs((1+sin(A*{var}+B))/cos(A*{var}+B)))/A"),
        (f"1/cos(A*{var}+B)^2", f"tan(A*{var}+B)/A"),
        (f"1/sin(A*{var}+B)^2", f"-cot(A*{var}+B)/A"),
        (f"1/sin(A*{var}+B)", f"log(abs(tan((A*{var}+B)/2)))/A"),
        (f"C^(A*{var}+B)", f"C^(A*{var}+B)/(A*log(C))"),
    ]
    formula_list = [[simplify(parse(y)) for y in x] for x in formula_list]
    expr = [[parse("A"), parse("1")], [parse("B"), parse("0")]]
    return [formula_list, var, expr]

formula_gen = integration_formula_init()
def rm_const(equation):
    if equation is None:
        return None
    eq2 = equation
    if eq2.name == "f_integrate" and contain(eq2.children[0], eq2.children[1]):
        equation = eq2.children[0]
        wrt = eq2.children[1]
        lst = factor_generation(equation)
        lst_const = [item for item in lst if not contain(item, wrt)]
        if lst_const != []:
            equation = product([item for item in lst if contain(item, wrt)]).copy_tree()
            const = product(lst_const)
            const = simplify(const)
            if not contain(const, tree_form("s_i")):
                return rm_const(TreeNode("f_integrate",[equation, wrt])) *const
        equation = eq2
    return TreeNode(equation.name, [rm_const(child)  for child in equation.children])
def shorten(eq):
    if eq.name.startswith("d_"):
        return tree_form("d_0")
    return TreeNode(eq.name, [shorten(child) for child in eq.children])
def integrate_formula(equation):
    global formula_gen
    if equation is None:
        return None
    eq2 = equation.copy_tree()
    if eq2.name == "f_integrate":
        integrand = eq2.children[0]
        wrt = eq2.children[1]
        if integrand == wrt:
            return wrt**2/2
        if not contain(integrand, wrt):
            return integrand*wrt
        out = transform_formula(simplify(integrand), wrt.name, formula_gen[0], formula_gen[1], formula_gen[2])
        if out is not None:
            return out
    return TreeNode(eq2.name, [integrate_formula(child) for child in eq2.children])
def has_nested_trig(node, seen_trig=False):
    if not isinstance(node, TreeNode):
        return False
    trig = {
        "f_sin", "f_cos", "f_tan",
        "f_sec", "f_cosec", "f_cot"
    }
    is_trig = node.name in trig
    if is_trig and seen_trig:
        return True
    seen_trig = seen_trig or is_trig
    children = getattr(node, "args", None) or getattr(node, "children", None) or []
    for c in children:
        if has_nested_trig(c, seen_trig):
            return True
    return False
def has_nested_trig(node, seen_trig=False):
    if not isinstance(node, TreeNode):
        return False
    trig = {
        "f_sin", "f_cos", "f_tan",
        "f_sec", "f_cosec", "f_cot"
    }
    is_trig = node.name in trig
    if is_trig and seen_trig:
        return True
    seen_trig = seen_trig or is_trig
    children = getattr(node, "args", None) or getattr(node, "children", None) or []
    for c in children:
        if has_nested_trig(c, seen_trig):
            return True
    return False
def sin_range(eq, n, wrt):
    a = tree_form(f"d_{n}")*parse("pi/2")
    b = tree_form(f"d_{n+1}")*parse("pi/2")
    return eq2range(wavycurvy(simplify(TreeNode("f_lt", [a,eq]) & TreeNode("f_lt", [eq,b])), wrt)), tree_form("d_1") if (n // 2)%2 ==0 else tree_form("d_-1")
def def_int(eq, start, end, wrt):
    if eq.name == "f_abs" and eq.children[0].name == "f_sin":
        lst = []
        f = Range()
        f.r = [False, start, True, end, False]
        a = math.floor(compute(start)/compute(parse("pi/2")))
        b = math.floor(compute(end)/compute(parse("pi/2")))+1
        for i in range(a,b+1):
            inq, sgn = sin_range(eq.children[0].children[0], i, wrt)
            inq = eq2range(wavycurvy(range2eq2(f&inq))).fix()
            if len(inq.r) != 5:
                continue
            eqn = TreeNode("f_integrate", [eq.children[0]*sgn, wrt])
            eqn2 = TreeNode("f_subs", [eqn, wrt, inq.r[3]]) - TreeNode("f_subs", [eqn, wrt, inq.r[1]])
            lst.append(eqn2)
        return simplify(summation(lst))
    elif eq.name == "f_abs":
        lst = []
        f = TreeNode("f_gt", [eq.children[0], tree_form("d_0")])
        f = simplify(f)
        g = TreeNode("f_lt", [eq.children[0], tree_form("d_0")])
        g = simplify(g)
        h = Range()
        h.r = [False, start, True, end, False]
        f = eq2range(wavycurvy(f, wrt))
        f = (f & h).fix()
        g = eq2range(wavycurvy(g, wrt))
        g = (g & h).fix()
        for i in range(2):
            for j in range(len([f,g][i].r)):
                if [f,g][i].r[j] == True:
                    eqn = TreeNode("f_integrate", [eq.children[0]*[tree_form("d_1"), tree_form("d_-1")][i], wrt])
                    eqn2 = TreeNode("f_subs", [eqn, wrt, [f,g][i].r[j+1]]) - TreeNode("f_subs", [eqn, wrt, [f,g][i].r[j-1]])
                    lst.append(eqn2)
        return simplify(summation(lst))
    return None
def integrate_definite(eq):
    if eq.name == "f_integrate" and len(eq.children) == 4:
        out = def_int(eq.children[0], eq.children[2], eq.children[3], eq.children[1])
        if out is not None:
            return out
    return TreeNode(eq.name, [integrate_definite(child) for child in eq.children])
def integrate_full(root):
    root = integrate_definite(trig0(root))
    def normalize(x, f=True):
        x = simplify(x)
        x = factor2(x)
        x = trig4(x)
        if f:
            x = dowhile(x, lambda y: fraction(simplify(integrate_formula(rm_const(integrate_summation(y))))))
            x = factor0(x)
        else:
            x = dowhile(x, lambda y: simplify(integrate_formula(rm_const(integrate_summation(y)))))
        out = sqint(x)
        if out is not None:
            x = out
        return x
    def is_solved(x):
        x = solve_integrate(x)
        return "f_integrate" not in str_form(x)
    result = None
    root = normalize(root)
    normalize2 = lambda x: normalize(x, False)
    log = []
    orig = copy.deepcopy(root)
    eq = root
    for item in [[lambda x: x], [factor2, apart, normalize2, apart2, normalize], [trig1, normalize2],\
                 [factor1, normalize, trig6, normalize, expand, normalize, integrate_subs_main, normalize, factor2, apart, normalize2],\
                 [normalize, integrate_subs_main, normalize2, expand, normalize, byparts, normalize]]:
        for item2 in item:
            eq = item2(eq)
            if eq not in log:
                print(eq)
                log.append(eq)
            if is_solved(eq):
                result = eq
                break
        if result is not None:
            break
        eq = copy.deepcopy(orig)
    result = solve_integrate(result)
    if result is None:
        result = root
    result = dowhile(result, lambda x: trig0(simplify(fraction(x))))
    return result
