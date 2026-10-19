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
from .formula_applier import formula_list_applier, formula_applier
from .inverse import inverse
from .tool import poly
from fractions import Fraction
from .trig import trig0, trig2, trig3, trig4, trig1, trig5, trig6
from .apart import apart, apart2
from .univariate_inequality import wavycurvy, eq2range, range2eq2, Range
from .printeq import *
def all_branch(eq):
    if eq.children == []:
        return []
    out = [eq.name]
    for child in eq.children:
        out += all_branch(child)
    return list(set(out))
is_integrate_subs_s = """poly(x,a,b,c) true [] x [a,b,c] _ _
a*x+b true [] x [a,b] _ _
a false [] x a _ _"""

is_integrate_subs = lambda x: formula_list_applier(x, is_integrate_subs_s)

def subs_heuristic(eq, var):
    output = []
    last = []
    def collect2(eq):
        if eq.name == "f_pow" and frac(eq.children[1]) is not None and frac(eq.children[1]) == Fraction(1,2):
            if eq.children[0] == var:
                output.append(str_form(eq))
        if eq.name == "f_log":
            output.append(str_form(eq))
        if eq.name in ["f_pow"] and var.name in str_form(eq):
            if eq.children[1].name[:2] != "v_":
                output.append(str_form(eq))
        if eq.name in ["f_arctan"] and var.name in str_form(eq.children[0]):
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
    poly_size = -1
    fx = is_integrate_subs
    output = []
    if set(all_branch(eq)) <= set("f_add f_mul f_pow".split(" ")):
        for item in tmp:
            if fx(item).name == "s_true":
                if len(item) > poly_size:
                    poly_term = item
                    poly_size = len(item)
            else:
                output.append(item)
    p = None
    if poly_term is None:
        p = tmp
    else:
        p = [poly_term]+output
    last = list(set(last))
    if len(p)>2:
        p = p[:2]
    elif len(p)<2:
        p = (p+last)[:2]
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
def integrate_subs(equation, term, v1, v2, extra):
    output = []
    orig = equation.copy_tree()
    none = TreeNode("f_integrate",[orig, tree_form(v1)])
    origv2 = copy.deepcopy(v2)
    equation = simplify(equation)
    eq = equation
    termeq = term
    t = inverse(termeq, v1)
    g = inverse(termeq, v2)
    if g is None:
        return none
    if t is None:
        equation = simplify(factor2(factor0(simplify(replace(eq, g, tree_form(v2))/diff(g, v1)))))
        if v1 in str_form(equation):        
            return none
    else:
        t = expand(t)
        eq3 = diff(g, v1)
        eq2 = replace(eq, g, tree_form(v2))
        eq4 = simplify(eq2/eq3)
        if not contain(eq4, tree_form(v1)):
            equation = eq4
        else:
            eq = replace(eq, tree_form(v1), t)
            equation = eq/eq3
            equation = simplify(equation)
            if v1 in str_form(equation):
                equation = replace(equation, tree_form(v1), t)
                equation = formula_applier(equation, "abs(x) x [] _ _ _ _")
    if v1 in str_form(equation):
        return none
    return dowhile(TreeNode("f_subs", [TreeNode("f_integrate", [simplify(equation), tree_form(origv2)]),tree_form(origv2) ,g]+extra), lambda x: simplify(trig4(trig0(x))))
def integrate_subs_main_helper(equation):
    eq2 = equation
    if eq2.name == "f_integrate":
        output = []
        wrt = eq2.children[1]
        eq = equation.children[0]
        v2 = "v_"+str(int(wrt.name[2:])+1)
        if str(tree_form(v2)) == "i":
            v2 = "v_"+str(int(v2[2:])+1)
        for item in subs_heuristic(eq, wrt):
            x = tree_form(v2)-item
            output.append(integrate_subs(eq, x, wrt.name, v2, eq2.children[2:]))
        output = list(set(output)-{eq2})
        if len(output) == 1:
            return output[0]
        if len(output) == 0:
            return equation
        return TreeNode("f_try", [item.copy_tree() for item in output])
    return equation
def integrate_subs_main(equation):
    return transform_dfs(equation, integrate_subs_main_helper)

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
                out1 = TreeNode("f_integrate", [g.copy_tree(), wrt]+eq2.children[2:])
                out2 = TreeNode("f_integrate", [simplify(diff(f.copy_tree(), wrt.name)*out1), wrt]+eq2.children[2:])
                output.append(simplify(f.copy_tree() * out1 - out2))
        if len(output) == 0:
            pass
        elif len(output) == 1:
            return output[0]
        else:
            return TreeNode("f_try", output)
        eq = eq2
    return TreeNode(eq.name, [byparts(child) for child in eq.children])

integrate_fraction_s = """integrate(1/sqrt(poly(x,a,b,c)),x) 1/sqrt(a)*log(abs(sqrt(a)*x+b/(2*sqrt(a))+sqrt((sqrt(a)*x+b/(2*sqrt(a)))^2+(4*a*c-b^2)/(4*a)))) [] x [a,b,c] [a,4*a*c-b^2] _ [[a,0],[b^2-4*a*c,0]]
integrate(1/sqrt(poly(x,a,b,c)),x) 1/sqrt(a)*log(abs(sqrt(a)*x+b/(2*sqrt(a))+sqrt((sqrt(a)*x+b/(2*sqrt(a)))^2-(b^2-4*a*c)/(4*a)))) [] x [a,b,c] [a,b^2-4*a*c] _ [[a,0],[4*a*c-b^2,0]]
integrate(1/sqrt(poly(x,a,b,c)),x) 1/sqrt(-a)*arcsin((sqrt(-a)*x-b/(2*sqrt(-a)))/sqrt((4*a*c-b^2)/(4*a))) [] x [a,b,c] [4*a*c-b^2] a [[a,0],[b^2-4*a*c,0]]
integrate(1/poly(x,a,b,c),x) 1/(sqrt(a)*sqrt((4*a*c-b^2)/(4*a)))*arctan((sqrt(a)*x+b/(2*sqrt(a)))/sqrt((4*a*c-b^2)/(4*a))) [] x [a,b,c] [a,4*a*c-b^2] _ [[a,0],[b^2-4*a*c,0]]
integrate(1/poly(x,a,b,c),x) -1/(sqrt(-a)*sqrt((b^2-4*a*c)/(-4*a)))*arctan((sqrt(-a)*x-b/(2*sqrt(-a)))/sqrt((b^2-4*a*c)/(-4*a))) [] x [a,b,c] _ [a,b^2-4*a*c] [[a,0],[4*a*c-b^2,0]]
integrate(poly(x,p,q)/sqrt(poly(x,a,b,c)),x) (p/a)*sqrt(a*x^2+b*x+c)+(q-p*b/(2*a))*integrate(1/sqrt(a*x^2+b*x+c),x) [] x [p,q,a,b,c] _ _ _ [[a,0]]
integrate(poly(x,p,q)/poly(x,a,b,c),x) (p/(2*a))*log(abs(a*x^2+b*x+c))+(q-p*b/(2*a))*integrate(1/(a*x^2+b*x+c),x) [] x [p,q,a,b,c] _ _ _ [[a,0]]"""
integrate_fraction = lambda x: formula_list_applier(x, integrate_fraction_s)

def_integrate_formula_s = """integrate(abs(poly(x,a,b)),x,m,n) ((a*n+b)*abs(a*n+b)-(a*m+b)*abs(a*m+b))/(2*a) [] x [a,b] _ _
integrate(abs(sin(x)),x) 2*floor(x/pi)+1-cos(x-pi*floor(x/pi)) [] x _ _ _
integrate(u,x,a,inf) limitpinf(integrate(u,x),x)-limit(integrate(u,x),x,a) [] x a _ _ _
integrate(u,x,a,b) limit(integrate(u,x),x,b)-limit(integrate(u,x),x,a) [] x [a,b] _ _ _"""
def_integrate_formula = lambda x: formula_list_applier(x, def_integrate_formula_s)

integrate_formula_s = """
integrate(x^2*e^(poly(x,a,b)),x) ((x^2/a)-(2*x/(a^2))+(2/(a^3)))*e^(a*x+b) [] x [a,b] _ _
integrate(x*e^(poly(x,a,b)),x) ((x/a)-(1/(a^2)))*e^(a*x+b) [] x [a,b] _ _
integrate(e^(poly(x,a,b)),x) e^(a*x+b)/a [] x [a,b] _ _
integrate(1/(poly(x,a,b)),x) log(abs(a*x+b))/a [] x [a,b] _ _
integrate((poly(x,a,b))^c,x) (a*x+b)^(c+1)/(a*(c+1)) [] x [a,b,c] _ _
integrate(1/cos(poly(x,a,b))^2,x) tan(a*x+b)/a [] x [a,b] _ _
integrate(1/sin(poly(x,a,b))^2,x) -cot(a*x+b)/a [] x [a,b] _ _
integrate(1/cos(poly(x,a,b)),x) log(abs((1+sin(a*x+b))/cos(a*x+b)))/a [] x [a,b] _ _
integrate(1/sin(poly(x,a,b)),x) log(abs(tan((a*x+b)/2)))/a [] x [a,b] _ _
integrate(sin(poly(x,a,b))^2/cos(a*x+b)^2,x) tan(a*x+b)/a-x [] x [a,b] _ _
integrate(sin(poly(x,a,b))/(cos(a*x+b)^2),x) 1/(a*cos(a*x+b)) [] x [a,b] _ _
integrate(sin(poly(x,a,b)),x) -cos(a*x+b)/a [] x [a,b] _ _
integrate(cos(poly(x,a,b)),x) sin(a*x+b)/a [] x [a,b] _ _
integrate(sum(a,b),x) integrate(a,x)+integrate(b,x) [] x _ _ _
integrate(x,x) x^2/2 [] x _ _ _
integrate(a,x) a*x [] x a _ _
integrate(product(a,b),x) a*integrate(b,x) [] x a _ _
"""
integrate_formula = lambda x: formula_list_applier(x, integrate_formula_s)

integrate_trig_s = """integrate(cos(poly(x,a,b))/sin(poly(x,a,b)),x) log(abs(sin(a*x+b)))/a [] x [a,b] _ _
integrate(sin(poly(x,a,b))/cos(poly(x,a,b)),x) -(log(abs(cos(a*x+b)))/a) [] x [a,b] _ _
integrate((sin(x)/cos(x))^a,x) tan(x)^(a-1)/(a-1)-integrate((sin(x)/cos(x))^(a-2),x) [] x a a _ [[a,1]]
integrate((cos(x)/sin(x))^a,x) -(cot(x)^(a-1)/(a-1))-integrate((cos(x)/sin(x))^(a-2),x) [] x a a _ [[a,1]]
integrate(cos(x)^a/sin(x),x) cos(x)^(a-1)/(a-1)+integrate(cos(x)^(a-2)/sin(x),x) [] x a a _ [[a,1]]
integrate(sin(x)^a/cos(x),x) -(sin(x)^(a-1)/(a-1))+integrate(sin(x)^(a-2)/cos(x),x) [] x a a _ [[a,1]]
integrate(sin(x)^a*cos(x)^b,x) -(sin(x)^(a+1)*cos(x)^(b+1)/(b+1))+(a+b+2)/(b+1)*integrate(sin(x)^a*cos(x)^(b+2),x) [] x [a,b] _ b [[b,-1]]
integrate(sin(x)^a*cos(x)^b,x) sin(x)^(a+1)*cos(x)^(b+1)/(a+1)+(a+b+2)/(a+1)*integrate(sin(x)^(a+2)*cos(x)^b,x) [] x [a,b] _ a [[a,-1]]
integrate(sin(x)^a,x) sin(x)^(a+1)*cos(x)/(a+1)+(a+2)/(a+1)*integrate(sin(x)^(a+2),x) [] x a _ a [[a,-1]]
integrate(cos(x)^a,x) -(sin(x)*cos(x)^(a+1)/(a+1))+(a+2)/(a+1)*integrate(cos(x)^(a+2),x) [] x a _ a [[a,-1]]"""
integrate_trig_formula = lambda x: formula_list_applier(x, integrate_trig_s)

def normalize(x, f=True):
    x = simplify(x)
    x = factor2(x)
    if f:
        x = dowhile(x, lambda y: fraction(simplify(integrate_formula(y))))
    else:
        x = integrate_formula(x)
    out = integrate_fraction(x)
    if out is not None:
        x = out
    return x

def integrate_full(root, debug=True):
    root = trig0(root)
    def is_solved(x):
        x = solve_integrate(x)
        return "f_integrate" not in str_form(x)
    result = None
    root = normalize(root)
    root = formula_applier(root, "(a^b)^c a^(b*c) [] b c _ _")
    normalize2 = lambda x: normalize(x, False)
    log = []
    orig = copy.deepcopy(root)
    eq = root
    for item in [[lambda x: x, simplify, expand, normalize], [factor2, apart, normalize2, normalize], [trig1, normalize2],\
                 [factor1, normalize, trig6, normalize, expand, normalize, integrate_subs_main, normalize, factor2, simplify, integrate_trig_formula, trig1, apart, normalize2],\
                 [normalize2, integrate_subs_main, expand, normalize, factor2, simplify, apart, normalize, expand, byparts, normalize],\
                 [simplify, integrate_trig_formula, trig1, integrate_formula]]:
        for item2 in item:
            eq = item2(eq)
            if eq not in log:
                if debug:
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
