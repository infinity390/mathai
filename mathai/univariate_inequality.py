import itertools
from .base import *
from .inverse import inverse
from collections import Counter
from .simplify import simplify
from .expand import expand
from .fraction import fraction
import copy
from .diff import diff
from .logic import logic0
from .tool import poly, poly_simplify
def intersection2(domain, lst):
    domain = copy.deepcopy(domain)
    if domain == [True]:
        return lst
    elif domain == [True]:
        return []
    lst = [item for item in lst if item not in domain]
    out = []
    for item2 in lst:
        for index in range(len(domain)):
            if isinstance(domain[index], bool) and domain[index]:
                if index == 0 and compute(item2) < compute(domain[index+1]):
                    out.append(item2)
                    break
                elif index == len(domain)-1 and compute(domain[index-1]) < compute(item2):
                    out.append(item2)
                    break
                elif index != 0 and index != len(domain)-1 and compute(domain[index-1]) < compute(item2) and compute(item2) < compute(domain[index+1]):
                    out.append(item2)
                    break
    return list(set(out))
def flip_less_than(inter):
    inter = copy.deepcopy(inter)
    return [not item if isinstance(item, bool) else item for item in inter]
def intersection(domain_1, domain_2):
    domain_1, domain_2 = copy.deepcopy(domain_1), copy.deepcopy(domain_2)
    if domain_1 == [True]:
        return domain_2
    if domain_2 == [True]:
        return domain_1
    if domain_1 == [False] or domain_2 == [False]:
        return [False]
    def simplify_ranges(ranges):
        simplified_ranges = []
        i = 0
        while i < len(ranges):
            if i + 2 < len(ranges) and ranges[i] is True and ranges[i + 2] is True:
                simplified_ranges.append(True)
                i += 3
            elif i + 2 < len(ranges) and ranges[i] is False and ranges[i + 2] is False:
                simplified_ranges.append(False)
                i += 3
            else:
                simplified_ranges.append(ranges[i])
                i += 1
        return simplified_ranges
    result = domain_1 + domain_2
    result = [item for item in result if not isinstance(item, bool)]
    result = list(set(result))
    result = sorted(result, key=lambda x: compute(x))
    i = len(result)
    while i>=0:
        result.insert(i, True)
        i = i - 1
    result[0] = domain_1[0] and domain_2[0]
    result[-1] = domain_1[-1] and domain_2[-1]
    def find_fraction_in_list(fraction_list, target_fraction):
        for i in range(1, len(fraction_list)-1, 2):
            if fraction_list[i] == target_fraction:
                return i
        return -1
    for i in range(2, len(result)-1, 2):
        if result[i+1] in domain_1:
            result[i] = result[i] and domain_1[find_fraction_in_list(domain_1, result[i+1])-1]
        if result[i+1] in domain_2:
            result[i] = result[i] and domain_2[find_fraction_in_list(domain_2, result[i+1])-1]
        if result[i-1] in domain_1:
            result[i] = result[i] and domain_1[find_fraction_in_list(domain_1, result[i-1])+1]
        if result[i-1] in domain_2:
            result[i] = result[i] and domain_2[find_fraction_in_list(domain_2, result[i-1])+1]
    result = simplify_ranges(result)
    return result
class Range:
    def __init__(self, r=[True], p=[], z=[], variable=None):
        self.r = r
        self.p = p
        self.z = z
        self.do = True
        if variable is None:
            self.variable = tree_form("d_0")
        else:
            self.variable = variable
    def truth(self):
        if self.r == [True]:
            return 1
        if self.r == [False] and self.p == [] and self.z == []:
            return -1
        return 0
    def unfix(self):
        self.do = False
        return self
    def fix(self):
        if not self.do:
            return
        def simplify_ranges(ranges):
            simplified_ranges = []
            i = 0
            while i < len(ranges):
                if i + 2 < len(ranges) and ranges[i] is True and ranges[i + 2] is True:
                    simplified_ranges.append(True)
                    i += 3
                elif i + 2 < len(ranges) and ranges[i] is False and ranges[i + 2] is False:
                    simplified_ranges.append(False)
                    i += 3
                else:
                    simplified_ranges.append(ranges[i])
                    i += 1
            return simplified_ranges
        self.r = simplify_ranges(self.r)
        common = set(self.p) & set(self.z)
        self.z = list(set(self.z) - common)
        self.p = list(set(self.p) - common)
        self.p = list(set(self.p) - set(intersection2(self.r, self.p)))
        self.z = list(set(intersection2(self.r, self.z)))
        return self
    def __or__(self, other):
        tmp = (self.unfix().__invert__().unfix() & other.unfix().__invert__().unfix()).unfix().__invert__().fix()
        tmp.variable = self.variable
        return tmp
    def __invert__(self):
        tmp =  Range(flip_less_than(self.r), self.z, list(set(self.p)-set(self.z)))
        tmp.variable = self.variable
        return tmp
    def __and__(self, other):
        a = intersection(self.r, other.r)
        b = intersection2(self.r, other.p)
        c = intersection2(other.r, self.p)
        tmp = Range(a, list(set(b)|set(c)|(set(self.p)&set(other.p))), list(set(self.z)|set(other.z)))
        tmp.variable = self.variable
        return tmp
    def __str__(self):
        if self.r == [False] and self.p == [] and self.z == []:
            return str(self.variable)+"∈"+"{}"
        out = []
        out2 = ""
        if self.r != [False]:
            for i in range(0, len(self.r), 2):
                string = ""
                if self.r[i]:
                    if i == 0:
                        string += "(-inf,"
                        if len(self.r)==1:
                            string += "+inf)"
                        else:
                            string += str(self.r[i+1])+")"
                    elif i == len(self.r)-1 and len(self.r)!=1:
                        string += "("+str(self.r[i-1])+",+inf)"
                    else:
                        string += "("+str(self.r[i-1])+","+str(self.r[i+1])+")"
                    out.append(string)
        if self.p != []:
            out.append("{"+",".join([str(item) for item in self.p])+"}")
        if self.z != []:
            out2 = "{"+",".join([str(item) for item in self.z])+"}"
        if out2 == "":
            return str(self.variable)+"∈"+"U".join(out)
        else:
            return str(self.variable)+"∈"+"U".join(out)+"-"+out2
def prepare(eq):
    if eq.name[2:] in "and not or".split(" "):
        output = TreeNode(eq.name, [])
        for child in eq.children:
            out = prepare(child)
            if out is None:
                return child
            output.children.append(out)
        output = TreeNode(output.name, output.children)
        return output
    elif eq.name[2:] in "gt lt eq ge le".split(" "):
        eq = simplify(eq)
        if "f_mod" not in str_form(eq):
            out = prepare(eq.children[0])
        else:
            out = eq.children[0]
        if out is None:
            return eq.children[0]
        output = TreeNode(eq.name, [out, tree_form("d_0")])
        output = logic0(output)
        return output
    else:
        eq = logic0(eq)
        if eq.name in ["s_true", "s_false"]:
            return eq
        if len(vlist(eq)) != 1:
            return eq
        out = poly(eq, vlist(eq)[0])
        if out is None or len(out) > 3:
            output = []
            for item in factor_generation(eq):
                if item.name == "f_pow" and item.children[1].name == "d_-1":
                    out2 = poly(item.children[0], vlist(eq)[0])
                    if out2 is not None and len(out2) <= 3:
                        output.append(poly_simplify(item.children[0])**-1)
                    else:
                        output.append(item)
                else:
                    out2 = poly(item, vlist(eq)[0])
                    if out2 is not None and len(out2) <= 3:
                        output.append(poly_simplify(item))
                    else:
                        output.append(item)
            return simplify(product(output))
        else:
            return poly_simplify(eq)
dic_table = {}
def helper(eq, var="v_0"):
    global dic_table
    eq2 = copy.deepcopy(eq)
    if eq2 in dic_table.keys():
        return dic_table[eq2]
    if eq.children[0].name == "f_add":
        eq.children[0] = simplify(expand(eq.children[0]))
    equ = False
    sign= True
    if eq.name in ["f_gt", "f_ge"]:
        sign = True
    elif eq.name in ["f_lt", "f_le"]:
        sign = False
    if eq.name in ["f_ge", "f_le"]:
        equ = True
    if eq.name == "f_eq":
        equ= True
    critical = []
    equal = []
    more = []
    _, d = num_dem(eq.children[0])
    d = simplify(d)
    for item in factor_generation(d):
        item = simplify(expand(item))
        if len(vlist(item)) != 0:
            v = vlist(item)[0]
            if diff(diff(item, v), v) != tree_form("d_0"):
                continue
            out = inverse(item, vlist(item)[0])
            more.append(simplify(out))
    for item in factor_generation(eq.children[0]):
        item = simplify(expand(item))
        if len(vlist(item)) == 0:
            if compute(item) <0:
                sign = not sign
            continue
        v = vlist(item)[0]
        if item.name == "f_pow" and item.children[1].name== "d_-1":
            item = item.children[0]
            if diff(diff(item, v), v) != tree_form("d_0"):
                a = replace(diff(diff(item, v), v), tree_form(v), tree_form("d_0"))/tree_form("d_2")
                if "v_" in str_form(a):
                    return None
                if compute(a) < 0:
                    sign = not sign
                continue
            else:
                tmp2 = diff(copy.deepcopy(item))
                if compute(tmp2)<0:
                    sign = not sign
                    item = simplify(item * tree_form("d_-1"))
                out = inverse(item, vlist(item)[0])
                critical.append(out)
        else:
            if diff(diff(item, v), v) != tree_form("d_0"):
                a = replace(diff(diff(item, v), v), tree_form(v), tree_form("d_0"))/tree_form("d_2")
                if "v_" in str_form(a):
                    return None
                if compute(a) < 0:
                    sign = not sign
                continue
            else:
                tmp2 = diff(copy.deepcopy(item))
                if compute(tmp2)<0:
                    sign = not sign
                    item = simplify(item * tree_form("d_-1"))
                out = inverse(item, vlist(item)[0])
                critical.append(out)
                if equ:
                    equal.append(out)
    equal = list(set([simplify(item) for item in equal]))
    more = list(set([simplify(item) for item in more]))
    critical = [simplify(item) for item in critical]
    critical = Counter(critical)
    critical = sorted(critical.items(), key=lambda x: compute(x[0]))
    i = len(critical)
    element = sign
    while i>=0:
        critical.insert(i, element)
        if i>0 and critical[i-1][1] % 2 != 0:
            element = not element
        i = i - 1
    for i in range(1, len(critical), 2):
        critical[i] = critical[i][0]
    if eq.name == "f_eq":
        final = Range([False], equal, more)
        dic_table[eq2] = final
        return final
    final = Range(critical, equal, more)
    dic_table[eq2] = final
    return final   
def wavycurvy_helper(eq, var=None):
    if var is None and len(vlist(eq)) == 1:
        var = tree_form(vlist(eq)[0])
    if eq.name == "s_true":
        out = Range([True])
        out.variable = var
        return range2eq2(out)
    if eq.name == "s_false":
        out = Range([False])
        out.variable = var
        return range2eq2(out)
    if eq.name == "f_range":
        return eq
    if eq.name in ["f_le", "f_ge", "f_lt", "f_gt", "f_eq"]:
        out = None
        if "f_mod" not in str_form(eq) and len(vlist(eq)) < 2:
            tmp = poly(eq.children[0], vlist(eq)[0])
            if tmp is not None and len(tmp) <= 3:                
                out = helper(eq)
                out.variable = var
                out = range2eq2(out)
            else:
                out = eq
        else:
            out = eq
        return out
    elif eq.name in ["f_and", "f_or", "f_not"]:
        orig = copy.deepcopy(eq)
        lst2 = eq.children
        lst = [item for item in lst2 if isinstance(item, Range)]+[eq2range(item) for item in lst2 if isinstance(item, TreeNode) and item.name == "f_range"]
        lst3 = [item for item in lst2 if isinstance(item, TreeNode) and item.name != "f_range"]
        if lst == []:
            return eq
        if eq.name == "f_not":
            if lst[0].truth() != 0:
                return range2eq2(~lst[0])
        if eq.name == "f_and":
            for item in lst:
                if item.truth() == -1:
                    return range2eq2(item)
            lst = [item for item in lst if item.truth() != 1]
        if eq.name == "f_or":
            for item in lst:
                if item.truth() == 1:
                    return range2eq2(item)
            lst = [item for item in lst if item.truth() != -1]
        lst5 = {}
        for item in list(set([x.variable.name for x in lst])):
            lst5[tree_form(item)] = [item2 for item2 in lst if item == item2.variable.name]
        eq3 = TreeNode(eq.name, [])
        ra = None
        for key in lst5.keys():
            lst = lst5[key]
            ra = lst[0]
            if eq.name == "f_and":
                for child in lst[1:]:
                    ra = ra & child
            elif eq.name == "f_or":
                for child in lst[1:]:
                    ra = ra | child
            elif eq.name == "f_not":
                ra = ~ra
            ra = ra.fix()
            eq3.children.append(range2eq2(ra))
        if len(eq3.children) == 1:
            eq = eq3.children[0]
            ra = eq2range(eq)
        else:
            eq = eq3
        for index, ra in enumerate(eq3.children):
            ra = eq2range(ra)
            for index2, eq2 in enumerate(lst3):
                lst4 = tree_form("s_false")
                if orig.name == "f_and" and ra is not None and ra.r == [False] and len(ra.z) == 0 and len(ra.p) > 0 and\
                   ra.variable.name in vlist(eq2):
                    for item in ra.p:
                        lst4 = lst4 | (TreeNode("f_eq", [ra.variable - item, tree_form("d_0")]) & replace(eq2, ra.variable, item))
                    fx = lambda x: dowhile(x, lambda y: logic0(simplify(y, True, True)))
                    lst4 = fx(lst4)
                    tmp2 = eq3.children[:index]+eq3.children[index+1:]+lst3[:index2]+lst3[index2+1:]
                    if len(tmp2) == 1:
                        tmp2 = tmp2[0]
                        output = flatten_tree(lst4 & tmp2)
                        return output
                    elif len(tmp2) > 1:
                        tmp2 = TreeNode("f_and", tmp2)
                        output = flatten_tree(lst4 & tmp2)
                        return output
                    else:
                        return lst4
        if orig.name == eq.name:
            lst3 = eq.children+lst3
        else:
            lst3 = [eq]+lst3
        if len(lst3) == 1:
            return lst3[0]
        else:
            return TreeNode(orig.name, lst3)
    if isinstance(eq, Range):
        return range2eq2(eq)
    return eq
def range2eq2(c):
    r = TreeNode("f_r", [])
    for item in c.r:
        if isinstance(item, bool):
            if item:
                r.children.append(tree_form("s_wtrue"))
            else:
                r.children.append(tree_form("s_wfalse"))
        else:
            r.children.append(item)
    out = TreeNode("f_range", [r, TreeNode("f_p", c.p), TreeNode("f_z", c.z), c.variable])
    return out
def eq2range(eq):
    if eq.name == "f_range":
        r = []
        for item in eq.children[0].children:
            if item == tree_form("s_wtrue"):
                r.append(True)
            elif item == tree_form("s_wfalse"):
                r.append(False)
            else:
                r.append(item)
        c = Range(r, eq.children[1].children, eq.children[2].children)
        c.variable = eq.children[3]
        return c
    return None
def wavycurvy(eq, var=None):
    if var is None:
        if len(vlist(eq)) == 1:
            var = tree_form(vlist(eq)[0])
    eq = flatten_tree(eq)
    if len(vlist(eq)) == 0:
        return eq
    else:
        eq = transform_dfs(eq, wavycurvy_helper, [var])
    if isinstance(eq, Range):
        return range2eq2(eq.fix())
    return eq
def range2eq(c):
    if c.r == [True]:
        return tree_form("s_true")
    if c.r == [False]:
        if c.p == []:
            return tree_form("s_false")
        else:
            out = TreeNode("f_or", [TreeNode("f_eq", [c.variable-item, tree_form("d_0")]) for item in c.p])
            if len(out.children) == 1:
                return out.children[0]
            return out
    return c
def absolute(equation):
    def mul_abs(eq):
        if eq.name == "f_abs" and eq.children[0].name == "f_mul":
            return simplify(product([item.fx("abs") for item in factor_generation(eq.children[0])]))
        return TreeNode(eq.name, [mul_abs(child) for child in eq.children])
    equation = mul_abs(equation)
    def collectabs(eq):
        out = []
        if eq.name == "f_abs":
            out.append(eq)
            return out
        for child in eq.children:
            out += collectabs(child)
            if out != []:
                return out
        return out
    def abc(eq, arr):
        def trans(eq):
            nonlocal arr
            out = {}
            if eq.name == "f_abs":
                x = arr.pop(0)
                if x == 0 or x==2:
                    return eq.children[0]
                else:
                    return -eq.children[0]
            else:  
                return TreeNode(eq.name, [trans(child) for child in eq.children])
        return trans(eq)
    out = list(set(collectabs(equation)))
    if out == []:
        return logic0(equation)
    else:
        a = TreeNode("f_ge", [out[0].children[0], tree_form("d_0")]) & replace(equation, out[0], out[0].children[0])
        b = TreeNode("f_lt", [out[0].children[0], tree_form("d_0")]) & replace(equation, out[0], -out[0].children[0])
        return a | b
def handle_sqrt(eq):
    d= []
    def helper2(eq):
        nonlocal d
        if eq.name in ["f_lt", "f_gt", "f_le", "f_ge","f_eq"]:
            out = []
            def helper(eq):
                nonlocal out
                if eq.name == "f_pow" and frac(eq.children[1]) == Fraction(1,2):
                    out.append(simplify(eq))
                x = [helper(child) for child in eq.children]
            helper(eq)
            for item in out:
                n = tree_form("d_1")
                if eq.name == "f_eq":
                    eq2 = inverse(simplify(eq.children[0]), str_form(item))
                else:
                    eq2, sgn = inverse(simplify(eq.children[0]), str_form(item), True)
                    if sgn == False:
                        n = tree_form("d_-1")
                d.append(TreeNode("f_ge", [eq2,tree_form("d_0")]))
                eq3 = simplify(expand(simplify(eq2**2)))
                f = TreeNode("f_and", d)
                if len(f.children) == 1:
                    f = f.children[0]
                d = []
                return simplify(TreeNode(eq.name, [simplify(n*item.children[0]-eq3*n), tree_form("d_0")])) & f
        return TreeNode(eq.name, [helper2(child) for child in eq.children])
    return helper2(eq)
def domain(eq):
    eq = simplify(eq)
    out = []
    def helper2(eq):
        nonlocal out
        if eq.name == "f_pow" and frac(eq.children[1]) is not None and frac(eq.children[1]).denominator == 2:
            if "v_" in str_form(eq.children[0]):
                out.append(TreeNode("f_ge", [eq.children[0], tree_form("d_0")]))
                out.append(TreeNode("f_ge", [eq, tree_form("d_0")]))
        if eq.name == "f_pow" and frac(eq.children[1]) is not None and frac(eq.children[1]) <0:
            tmp = TreeNode("f_eq", [eq.children[0], tree_form("d_0")]).fx("not")
            if "v_" in str_form(tmp):
                out.append(tmp)
        x = [helper2(child) for child in eq.children]
    helper2(eq)
    out = list(set([simplify(item) for item in out]))
    if out == []:
        return eq
    if len(out)==1:
        out = out[0]
    else:
        out = TreeNode("f_and", list(out))
    if eq.name in ["f_lt", "f_gt", "f_le", "f_ge", "f_eq"]:
        return eq & out
    return out
