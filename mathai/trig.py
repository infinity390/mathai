from collections import Counter
import math
import itertools
from .logic import logic0
from .simplify import simplify
from .base import *
from .expand import expand
from .structure import transform_formula
from .parser import parse
from .fraction import fraction
from .factor import rationalize_sqrt
from .inverse import inverse
from .structure import structure
from .univariate_inequality import simple_wavycurvy, eq2range, Range, range2eq2
trig_sin_table = {
    (0,1): parse("0"),
    (1,6): parse("1/2"),
    (1,4): parse("1/sqrt(2)"),   
    (1,3): parse("sqrt(3)/2"),   
    (1,2): parse("1"),           
    (2,3): parse("sqrt(3)/2"),   
    (3,4): parse("1/sqrt(2)"),   
    (5,6): parse("1/2"),         
    (1,1): parse("0")            
}
trig_cos_table = {
    (0,1): parse("1"),
    (1,6): parse("sqrt(3)/2"),
    (1,4): parse("sqrt(2)/2"),
    (1,3): parse("1/2"),
    (1,2): parse("0"),
    (2,3): parse("-1/2"),
    (3,4): parse("-sqrt(2)/2"),
    (5,6): parse("-sqrt(3)/2"),
    (1,1): parse("-1")
}
trig_tan_table = {
    (0,1): parse("0"),           
    (1,6): parse("1/sqrt(3)"),   
    (1,4): parse("1"),   
    (1,3): parse("sqrt(3)")       
}
for key in trig_cos_table.keys():
    trig_cos_table[key] = simplify(trig_cos_table[key])
for key in trig_sin_table.keys():
    trig_sin_table[key] = simplify(trig_sin_table[key])
for key in trig_tan_table.keys():
    trig_tan_table[key] = simplify(trig_tan_table[key])
def trig0_helper(eq):
    if eq is None:
        return None
    def isneg(eq):
        return eq.name[:2] == "d_" and int(eq.name[2:]) < 0
    def single_pi(lst, quad=False):
        if tree_form("d_0") in lst:
            return (0, 1, None) if quad else (0, 1)
        count = sum(1 for item in lst if item == tree_form("s_pi"))
        if count != 1:
            return None
        eq = simplify(product(lst) / tree_form("s_pi"))
        out = frac(eq)
        if out is None or out < 0:
            return None
        a, b = out.numerator, out.denominator
        a %= 2 * b
        quadrant = None
        if quad:
            if a == 0 or a == b/2 or a == b or a == 3*b/2:
                quadrant = 0
            elif 0 < a < b/2:
                quadrant = 1
            elif b/2 < a < b:
                quadrant = 2
            elif b < a < 3*b/2:
                quadrant = 3
            else:
                quadrant = 4
        if a > b:
            a = 2*b - a
        return (a, b, quadrant) if quad else (a, b)
    cur = eq
    if cur.name == "f_arccosec":
        return (1/cur.children[0]).fx("arcsin")
    if cur.name == "f_arctan":
        if cur.children[0].name == "d_0":
            return tree_form("d_0")
        lst = factor_generation(cur.children[0])
        if any(isneg(item) for item in lst):
            return -(cur.children[0]*-1).fx("arctan")
    if cur.name == "f_arccot":
        return tree_form("s_pi")/tree_form("d_2") - cur.children[0].fx("arctan")
    if cur.name == "f_log":
        if cur.children[0].name == "d_1":
            return tree_form("d_0")
    if cur.name == "f_tan":
        if cur.children[0].name == "f_arctan":
            return cur.children[0].children[0]
        return cur.children[0].fx("sin") / cur.children[0].fx("cos")
    if cur.name == "f_sec":
        return cur.children[0].fx("cos")**-1
    if cur.name == "f_cosec":
        return cur.children[0].fx("sin")**-1
    if cur.name == "f_cot":
        return cur.children[0].fx("cos") / cur.children[0].fx("sin")
    if cur.name == "f_arcsin":
        if cur.children[0].name == "f_sin":
            out = single_pi(factor_generation(cur.children[0].children[0]), True)
            if out is not None:
                quad = out[-1]
                out = Fraction(1,2)-Fraction(*out[:2])
                if quad in [1,3]:
                    return frac_to_tree(out) * tree_form("s_pi")
        for item in trig_sin_table.keys():
            if Fraction(*item) < Fraction(1,2) and simplify(trig_sin_table[item] - cur.children[0]) == 0:
                return frac_to_tree(Fraction(*item)) * tree_form("s_pi")
        return cur
    if cur.name == "f_arccos":
        if cur.children[0].name == "f_cos":
            out = single_pi(factor_generation(cur.children[0].children[0]), True)
            if out is not None:
                quad = out[-1]
                out = Fraction(*out[:2])
                if quad in [2, 4]:
                    out = Fraction(1, 2) - out
                return frac_to_tree(out) * tree_form("s_pi")
        for item in trig_cos_table.keys():
            if simplify(trig_cos_table[item] - cur.children[0]) == 0:
                return frac_to_tree(Fraction(*item)) * tree_form("s_pi")
        return cur
    if cur.name == "f_arctan":
        for item in trig_tan_table:
            if simplify(trig_tan_table[item] - cur.children[0]) == 0:
                return frac_to_tree(Fraction(*item)) * tree_form("s_pi")
        return cur
    if cur.name == "f_sin":
        if cur.children[0].name == "f_arcsin":
            return cur.children[0].children[0]
        lst = factor_generation(cur.children[0])
        if any(isneg(item) for item in lst):
            return -(cur.children[0]*-1).fx("sin")
        out = single_pi(lst)
        if out is not None and tuple(out) in trig_sin_table:
            return trig_sin_table[tuple(out)]
    if cur.name == "f_cos":
        if cur.children[0].name == "f_arccos":
            return cur.children[0].children[0]
        lst = factor_generation(cur.children[0])
        if any(isneg(item) for item in lst):
            return (cur.children[0]*-1).fx("cos")
        out = single_pi(lst)
        if out is not None and tuple(out) in trig_cos_table:
            return trig_cos_table[tuple(out)]
    return cur
def trig0(eq):
    return transform_dfs(eq, trig0_helper)
def int_list_range(ra):
    ra = eq2range(ra)
    ra.variable = tree_form("v_13")
    mi = round(min(map(compute, [ra.r[1]] + ra.p))) - 1
    mx = round(max(map(compute, [ra.r[-2]] + ra.p))) + 1
    lst = []
    for i in range(mi, mx+1):
        out = eq2range(simple_wavycurvy(TreeNode("f_eq", [tree_form("v_13")-tree_form(f"d_{i}"), tree_form("d_0")])))
        if (out & ra).truth() != -1:
            lst.append(i)
    return lst
def zu_and_range_r_h(eq, a, b, var):
    out = logic0(simplify(TreeNode("f_lt", [a, eq]) & TreeNode("f_lt", [eq, b])))
    out = simple_wavycurvy(out)
    out = int_list_range(out)
    out = list(set(map(simplify, [replace(copy.deepcopy(eq), tree_form("v_13"), tree_form(f"d_{item}")) for item in out])))
    out = Range([False], out, [])
    out.variable = var
    return out
def zu_and_range_p_h(eq, val, var):
    out = inverse(eq-val, "v_13")
    out = simplify(out)
    if out.name.startswith("d_"):
        out = Range([False], [simplify(replace(copy.deepcopy(eq),tree_form("v_13"),out))], [])
    else:
        out = Range([False], [], [])
    out.variable = var
    return out
def zu_and_range_h(eq, ra, var):
    ra = eq2range(ra)
    ra2 = Range([False])
    if ra.r[0] or ra.r[-1]:
        return None
    for i in range(2,len(ra.r)-1,2):
        if ra.r[i] == True:
            ra2 = ra2 | zu_and_range_r_h(eq, ra.r[i-1], ra.r[i+1], var)
    for item in ra.p:
        ra2 = ra2 | zu_and_range_p_h(eq, item, var)
    for item in ra.z:
        ra2 = ra2 & ~zu_and_range_p_h(eq, item, var)
    return range2eq2(ra2)
def zu_simplify_h(eq):
    if eq.name in ["f_sin", "f_cos"] and eq.children[0].name == "f_zu":
        return eq.children[0].children[0].fx(eq.name[2:]).fx("zu")
    if eq.name == "f_zu" and not contain(eq.children[0], tree_form("v_13")):
        return eq.children[0]
    if eq.name == "f_sin":
        lst = factor_generation(eq.children[0], True)
        if tree_form("s_pi") in lst and tree_form("d_2") in lst:
            return tree_form("d_0")
    if eq.name == "f_cos":
        lst = factor_generation(eq.children[0], True)
        if tree_form("s_pi") in lst and tree_form("d_2") in lst:
            return tree_form("d_1")
    if eq.name == "f_and":
        lst = []
        for i in range(len(eq.children)):
            for j in range(len(eq.children)):
                if i == j:
                    continue
                if eq.children[i].name == "f_range" and eq.children[j].name == "f_eq" and contain2(eq.children[j], "f_zu") and\
                   len(vlist(eq.children[j]))==2:
                    var = list(set(vlist(eq.children[j]))-set(["v_13"]))[0]
                    tmp = inverse(copy.deepcopy(eq.children[j].children[0]), var)
                    if eq.children[i].children[-1] == tree_form(var):
                        out = zu_and_range_h(tmp.children[0], eq.children[i], tree_form(var))
                        if out is None:
                            continue
                        if i > j:
                            i, j= j, i
                        lst += [out]+eq.children[:i]+eq.children[i+1:j]+eq.children[j+1:]
                        if len(lst) == 1:
                            return lst[0]
                        return TreeNode("f_and", lst)
    return eq
def zu_simplify(eq):
    return dowhile(eq, lambda x: simplify(trig0(trig4(transform_dfs(x, zu_simplify_h, [])))))

def cog(expr):
    expr = TreeNode(expr.name, [product_to_sum(child) for child in expr.children])
    expr = trig0(simplify(expr))
    expr = expand(simplify(expr))
    return expr
def product_to_sum(expr):
    factors = factor_generation(expr)
    other = []
    lst = []
    for item in factors:
        if item.name in ["f_cos", "f_sin"]:
            lst.append(item)
        else:
            other.append(item)
    if len(lst) <= 1:
        return dowhile(expr, cog)
    if len(lst) == 2:
        a, b = lst
        out = None
        if a.name < b.name:
            a, b = b, a
        A, B = a.children[0], b.children[0]
        if a.name == "f_sin" and b.name == "f_sin":
            out =((A - B).fx("cos") - (A + B).fx("cos")) / tree_form("d_2")
        elif a.name == "f_cos" and b.name == "f_cos":
            out =((A - B).fx("cos") + (A + B).fx("cos")) / tree_form("d_2")
        elif a.name == "f_sin" and b.name == "f_cos":
            out =((A + B).fx("sin") + (A - B).fx("sin")) / tree_form("d_2")
        return out * product(other)
    rest = tree_form("d_1")
    if len(lst) % 2 == 1:
        rest = lst.pop(0)
    out = []
    for i in range(0, len(lst), 2):
        out.append(product_to_sum(product(lst[i:i+2])))
    expr = product(out)*rest*product(other)
    return dowhile(expr, cog)
def trig_formula_init():
    var = ""
    formula_list = [(f"A*sin(B)+C*sin(B)", f"(A^2+C^2)^(1/2)*sin(B+arctan(C/A))"),\
                    (f"sin(B+D)", f"sin(B)*cos(D)+cos(B)*sin(D)"),\
                    (f"cos(B+D)", f"cos(B)*cos(D)-sin(B)*sin(D)"),\
                    (f"cos(B)^2", f"1-sin(B)^2"),\
                    (f"1/cos(B)^2", f"1/(1-sin(B)^2)"),\
                    (f"cos(arcsin(B))", f"sqrt(1-B^2)"),\
                    (f"sin(arccos(B))", f"sqrt(1-B^2)"),\
                    (f"arccos(B)", f"pi/2-arcsin(B)"),\
                    (f"sin(arctan(B))", f"x/sqrt(1+x^2)"),\
                    (f"cos(arctan(B))", f"1/sqrt(1+x^2)")]
    formula_list = [[simplify(parse(y)) for y in x] for x in formula_list]
    expr = [[parse("A"), parse("1")], [parse("B")], [parse("C"), parse("1")], [parse("D")]]
    return [formula_list, var, expr]
def trig3(eq):
    def iseven(eq):
        if eq.name[:2] != "d_":
            return False
        if int(eq.name[2:]) < 2 or int(eq.name[2:]) % 2 != 0:
            return False
        return True
    if eq.name == "f_sin":
        lst = factor_generation(eq.children[0])
        if any(iseven(item) for item in lst):
            eq= 2*(eq.children[0]/2).fx("sin")*(eq.children[0]/2).fx("cos")
    if eq.name == "f_cos":
        lst = factor_generation(eq.children[0])
        if any(iseven(item) for item in lst):
            eq = (eq.children[0]/2).fx("cos")**2-(eq.children[0]/2).fx("sin")**2
    eq = expand(simplify(eq))
    return TreeNode(eq.name, [trig3(child) for child in eq.children])
def noneg_pow(eq):
    if eq.name == "f_pow" and frac(eq.children[1]) is not None and frac(eq.children[1])<0:
        return (eq.children[0]**(simplify(-eq.children[1])))**-1
    return TreeNode(eq.name, [noneg_pow(child) for child in eq.children])
def trig1(eq):
    eq = noneg_pow(eq)
    return product_to_sum(eq)
def trig4(eq):
    done = False
    def _trig4(eq, numer=True, chance="sin"):
        nonlocal done
        if eq.name == "f_sin":
            if eq.children[0].name == "f_add" and len(eq.children[0].children)>=2:
                r = len(eq.children[0].children)%2
                a, b = TreeNode("f_add", eq.children[0].children[:round((len(eq.children[0].children)-r)/2)]),\
                       TreeNode("f_add", eq.children[0].children[round((len(eq.children[0].children)-r)/2):])
                if len(a.children)==1:
                    a=a.children[0]
                if len(b.children)==1:
                    b=b.children[0]
                return a.fx("sin")*b.fx("cos") + a.fx("cos")*b.fx("sin")
            if eq.children[0].name == "f_arccos":
                a = eq.children[0].children[0]
                return (1-a**2)**(tree_form("d_2")**-1)
            if eq.children[0].name == "f_arctan":
                a = eq.children[0].children[0]
                return a/(1+a**2)**(tree_form("d_2")**-1)
        if eq.name == "f_pow" and numer:
            if eq.children[0].name == "f_cos" and chance == "cos":
                a = eq.children[0].children[0]
                if frac(eq.children[1]) == 2:
                    done = True
                    return 1 - a.fx("sin")**2
            if eq.children[0].name == "f_sin" and chance == "cos":
                a = eq.children[0].children[0]
                if frac(eq.children[1]) == 2:
                    done = True
                    return 1 - a.fx("cos")**2
        if eq.name == "f_cos":
            if eq.children[0].name == "f_add" and len(eq.children[0].children)>=2:
                r = len(eq.children[0].children)%2
                a, b = TreeNode("f_add", eq.children[0].children[:round((len(eq.children[0].children)-r)/2)]),\
                       TreeNode("f_add", eq.children[0].children[round((len(eq.children[0].children)-r)/2):])
                if len(a.children)==1:
                    a=a.children[0]
                if len(b.children)==1:
                    b=b.children[0]
                return a.fx("cos")*b.fx("cos") - a.fx("sin")*b.fx("sin")
            if eq.children[0].name == "f_arcsin":
                a = eq.children[0].children[0]
                return (1-a**2)**(tree_form("d_2")**-1)
            if eq.children[0].name == "f_arctan":
                a = eq.children[0].children[0]
                return tree_form("d_1")/(1+a**2)**(tree_form("d_2")**-1)
        return TreeNode(eq.name, [_trig4(child, False, chance) if eq.name != "f_add" and\
                                  (not numer or (eq.name == "f_pow" and frac(eq.children[1]) is not None and frac(eq.children[1]) < 0))\
                                   else _trig4(child, True, chance) for child in eq.children])
    eq= _trig4(eq)
    if not done:
        eq = _trig4(eq,"cos")
    return eq
def replace_cos2(eq, toggle=False):
    if toggle:
        if eq.name == "f_pow" and eq.children[1].name == "d_2" and eq.children[0].name == "f_cos":
            return parse("1")-eq.children[0].children[0].fx("sin")**2
    else:
        if eq.name == "f_pow" and eq.children[1].name == "d_2" and eq.children[0].name == "f_sin":
            return parse("1")-eq.children[0].children[0].fx("cos")**2
    return TreeNode(eq.name, [replace_cos2(child, toggle) for child in eq.children])
def trig6(eq):
    eq = trig3(simplify(eq))
    fx = lambda x: dowhile(x, lambda y: trig5(simplify(y)))
    eq = fx(eq)
    eq = simplify(expand(eq))
    eq = trig5(simplify(fraction(eq)))
    return eq
def trig5(eq):
    if eq.name == "f_arctan":
        x = eq.children[0]
        #return x.fx("sgn")*(parse("1")/(1+x**2).fx("sqrt")).fx("arccos")
        return (x/(1+x**2).fx("sqrt")).fx("arcsin")
    n, d = num_dem(eq)
    if simplify(d) == 1:
        return TreeNode(eq.name, [trig5(child) for child in eq.children])
    d1, d2 = simplify(replace_cos2(d)), simplify(replace_cos2(d, True))
    if len(str_form(d1)) > len(str_form(d2)):
        d = d2
    else:
        d = d1
    n1, n2 = simplify(replace_cos2(n)), simplify(replace_cos2(n, True))
    if len(str_form(n1)) > len(str_form(n2)):
        n = n2
    else:
        n = n1
    n = map(simplify, factor_generation(n))
    d = map(simplify, factor_generation(d))
    n = Counter(n)
    d = Counter(d)
    for item in d.keys():
        done = False
        if item.name == "f_sin":
            for item2 in d.keys():
                if item2.name == "f_cos" and item.children[0] == item2.children[0] and d[item]>=2 and d[item2]>=2:
                    tmp = item.children[0]
                    tmp1 = simplify(replace(trig0(simplify(parse("cosec(x)^2+sec(x)^2"))), parse("x"), tmp))
                    n[tmp1] += 1
                    d[tmp.fx("sin")] -=2
                    d[tmp.fx("cos")] -=2
                    done = True
                    break
        if done:
            break
    for item in d.keys():
        done = False
        if item.name == "f_sin":
            for item2 in d.keys():
                if item2.name == "f_cos" and item.children[0] == item2.children[0] and d[item]>=1 and d[item2]>=1:
                    tmp = item.children[0]
                    tmp1 = simplify(replace(trig0(simplify(parse("2*cosec(2*x)"))), parse("x"), tmp))
                    n[tmp1] += 1
                    d[tmp.fx("sin")] -=2
                    d[tmp.fx("cos")] -=2
                    done = True
                    break
        if done:
            break
    for item in d.keys():
        tmp = structure(copy.deepcopy(item),parse("1+sin(A)"), parse("A"), True, "")
        if tmp is None:
            continue
        tmp1 = parse("1")-tmp.fx("sin")
        tmp2 = tmp.fx("cos")**2
        n[simplify(tmp1)] += 1
        d[item] -= 1
        d[tmp2] += 1
        break
    for item in d.keys():
        tmp = structure(copy.deepcopy(item),parse("1+cos(A)"), parse("A"), True, "")
        if tmp is None:
            continue
        tmp1 = parse("1")-tmp.fx("cos")
        tmp2 = tmp.fx("sin")**2
        n[simplify(tmp1)] += 1
        d[item] -= 1
        d[tmp2] += 1
        break
    out = simplify(product(list(n.elements()))/product(list(d.elements())))
    if out != eq:
        return out
    return TreeNode(eq.name, [trig5(child) for child in eq.children])
def trig2(eq):
    if eq.name != "f_add":
        return TreeNode(eq.name, [trig2(child) for child in eq.children])
    for i, j in itertools.combinations(range(len(eq.children)), 2):
        c1, c2 = eq.children[i], eq.children[j]
        if c1.name in ["f_sin", "f_cos"] and c2.name in ["f_sin", "f_cos"]:
            A, B = c1.children[0], c2.children[0]
            rest = [eq.children[k] for k in range(len(eq.children)) if k not in (i, j)]
            rest_tree = summation(rest) if rest else tree_form("d_0")
            two = tree_form("d_2")
            if c1.name == "f_sin" and c2.name == "f_sin":
                combined = two * ((A + B) / two).fx("sin") * ((A - B) / two).fx("cos")
            elif c1.name == "f_cos" and c2.name == "f_cos":
                combined = two * ((A + B) / two).fx("cos") * ((A - B) / two).fx("cos")
            else:
                continue
            new_expr = rest_tree + combined
            return trig2(new_expr)
    return TreeNode(eq.name, [trig2(child) for child in eq.children])
