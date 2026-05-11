import itertools
from .parser import parse
from .structure import transform_formula
from .base import *
from .simplify import simplify, convert_to_basic
from .expand import expand
import math
from .tool import poly
from .fraction import fraction
from collections import Counter
def multiset_intersection(*lists):
    counters = list(map(Counter, lists))
    common = counters[0]
    for c in counters[1:]:
        common = common & c
    return list(common.elements())
def subtract_sublist(full_list, sublist):
    c_full = Counter(full_list)
    c_sub = Counter(sublist)
    result = c_full - c_sub
    tmp = list(result.elements())
    if tmp == []:
        return [tree_form("d_1")]
    return tmp
def term_common2(lst, take_neg_common=False):
    s = []
    arr = [factor_generation(child,True) for child in lst]
    if take_neg_common and not all(tree_form("d_-1") not in item for item in arr):
        arr = [item+[tree_form("d_-1"), tree_form("d_-1")] if tree_form("d_-1") not in item else item for item in arr]
    s = multiset_intersection(*arr)
    if s == []:
        return simplify(summation(lst))
    arr = [subtract_sublist(item, s) for item in arr]
    return simplify(product(s)*summation([product(item) for item in arr]))
def take_common(eq):
    score = []
    output = []
    def helper(eq, depth=0):
        nonlocal score
        nonlocal output
        key = tuple(sorted(eq,key=lambda x: str_form(x)))
        if key in output:
            return
        else:
            score.append(depth)
            output.append(key)
        for item3 in partitions(eq):
            for option in [False, True]:
                item = [term_common2(item2, option) for item2 in item3]  
                helper(item, depth+1)
    if eq.name == "f_add":
        helper(eq.children)
    else:
        return [eq]
    sc = {}
    for i in range(len(output)):
        output[i] = simplify(summation(list(output[i])))
        sc[output[i]] = score[i]
    output = list(set(output))
    return list(sorted(output, key=lambda x: -sc[x]))
def _factorconst(eq):
    def hcf_list(numbers):
        if not numbers:
            return None
        n = 1
        if math.prod(numbers) < 0:
            n = -1
        hcf = numbers[0]
        for num in numbers[1:]:
            hcf = math.gcd(hcf, abs(num))
        return hcf*n
    def extractnum(eq):
        lst = factor_generation(eq)
        for item in lst:
            if item.name[:2] == "d_":
                return int(item.name[2:])
        return 1
    n = 1
    if eq.name == "f_add":
        n = hcf_list([extractnum(child) for child in eq.children])
        eq = TreeNode(eq.name, [child/tree_form("d_"+str(n)) for child in eq.children])
    if n != 1:
        return tree_form("d_"+str(n))*eq
    return TreeNode(eq.name, [factorconst(child) for child in eq.children])
def _merge_sqrt(eq):
    lst= []
    eq2 = []
    for child in factor_generation(eq):
        if frac(child) is not None and frac(child).denominator==1:
            if frac(child)>0:
                eq2.append(child**2)
            elif frac(child)!=-1:
                eq2.append((-child)**2)
                lst.append(tree_form("d_-1"))
            else:
                lst.append(tree_form("d_-1"))
        elif child.name == "f_pow" and frac(child.children[1]) == Fraction(1,2):
            eq2.append(child.children[0])
        else:
            lst.append(child)
    if len(eq2)>1:
        if lst == []:
            lst= [tree_form("d_1")]
        return simplify(product(eq2)**(tree_form("d_2")**-1)*product(lst))
    return TreeNode(eq.name, [_merge_sqrt(child) for child in eq.children])
def sqrt_to_a_sqrt_b(n):
    if n == 0:
        return 0, 0
    sign = 1
    if n < 0:
        sign = -1
        m = -n
    else:
        m = n
    a = 1
    b = 1
    p = 2
    while p * p <= m:
        exp = 0
        while m % p == 0:
            m //= p
            exp += 1
        if exp:
            a *= p ** (exp // 2)
            if exp % 2 == 1:
                b *= p
        p += 1 if p == 2 else 2
    if m > 1:
        b *= m
    return sign * a, b
def merge_sqrt(eq):
    def helper(eq):
        if eq.name == "f_pow" and frac(eq.children[1]) == Fraction(1,2):
            if eq.children[0].name[:2] == "d_":
                n = int(eq.children[0].name[2:])
                a, b =sqrt_to_a_sqrt_b(n)
                return tree_form("d_"+str(b))**(tree_form("d_2")**-1)*tree_form("d_"+str(a))
        if eq.name == "f_pow" and frac(eq.children[1]) == Fraction(-1,2):
            if frac(eq.children[0]) is not None:
                out = frac(eq.children[0])
                b, a = [tree_form("d_"+str(x)) for x in [out.numerator, out.denominator]]
                return a**(tree_form("d_2")**-1)/b**(tree_form("d_2")**-1)
        return TreeNode(eq.name, [helper(child) for child in eq.children])
    return helper(_merge_sqrt(eq))
def rationalize_sqrt(eq):
    if eq.name== "f_pow" and frac(eq.children[1]) == Fraction(-1,2):
        eq = eq.children[0]**(tree_form("d_2")**-1)/eq.children[0]
    def term(eq):
        if eq.name == "f_add":
            output = []
            for child in eq.children:
                if any(child2.name == "f_pow" and frac(child2.children[1]) == Fraction(1,2) for child2 in factor_generation(child)):
                    output.append(simplify(-child))
                else:
                    output.append(child)
            return summation(output)
        return None
    n, d=num_dem(eq)
    n,d=simplify(n), simplify(d)
    if d != 1:
        t = term(d)
        if t is not None and t!=1:
            n,d=simplify(expand(simplify(n*t))),simplify(expand(simplify(d*t)))
            tmp= simplify(n/d)
            tmp = _merge_sqrt(tmp)
            return tmp
    return TreeNode(eq.name, [rationalize_sqrt(child) for child in eq.children])
def factorconst(eq):
    return simplify(_factorconst(eq))
def factor_helper(equation, complexnum):
    if any(contain2(equation, "f_"+item) for item in "eq lt le ge gt".split(" ")):
        return equation
    for r in vlist(equation):
        lst = poly(equation, r)
        if lst is not None and len(lst)==3:
            a, b, c = lst
            x1 = (-b+(b**2 - 4*a*c)**(tree_form("d_2")**-1))/(2*a)
            x2 = (-b-(b**2 - 4*a*c)**(tree_form("d_2")**-1))/(2*a)
            x1 = simplify(fraction(simplify(x1)))
            x2 = simplify(fraction(simplify(x2)))
            eq2 = a*(tree_form(r)-x1)*(tree_form(r)-x2)
            eq2 = simplify(eq2)
            if complexnum or (not complexnum and not contain(eq2, tree_form("s_i"))):
                return eq2
    return equation
def factor2(eq, complexnum=False):
    out = transform_dfs(simplify(eq), factor_helper, [complexnum])
    out = dowhile(out, lambda x: simplify(fraction(x)))
    return out
def max_depth(node):
    if node is None:
        return 0
    if not node.children:
        return 1
    return 1 + max(max_depth(child) for child in node.children)
def factor(equation):
    if equation.name == "f_add": 
        lst = take_common(equation)
        lst3 = lst
        mx = min([len(item.children) for item in lst3])
        lst3 = [item for item in lst3 if len(item.children)==mx]
        tmp = max(lst3, key=lambda x: -max_depth(x))
        if equation != tmp:
            return tmp
    return TreeNode(equation.name, [factor(child) for child in equation.children])
