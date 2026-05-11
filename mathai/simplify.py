import math
from .base import *
from fractions import Fraction
from collections import Counter
def convert_to_basic(node):
    if not node.name.startswith("f_"):
        return node
    node.children = [convert_to_basic(c) for c in node.children]
    if node.name == "f_sub":
        node = node.children[0]-node.children[1]
    if node.name == "f_div":
        node = node.children[0]/node.children[1]
    if node.name == "f_sqrt":
        node = node.children[0]**(tree_form("d_2")**tree_form("d_-1"))
    return node
def clear_div(eq, denom):
    if eq is None:
        return None
    lst = factor_generation(eq)
    if tree_form("d_0") in lst:
        return tree_form("d_0"), True
    lst3 = []
    for item in lst:
        if "v_" not in str_form(item) and compute(item) < 0:
            lst3.append(item)
    sign = denom
    if len(lst3) % 2 == 1:
        sign = False
    if denom:
        eq2 = []
        eq3 = []
        for item in lst:
            if frac(item) is not None:
                eq2.append(item)
            else:
                eq3.append(item)
        if eq3 == []:
            return product(eq2), True
        return product(eq3), sign
    lst4 = []
    for item in lst:
        if item.name == "f_pow":
            tmp = frac(item.children[1])
            if tmp is None or tmp != -1:
                lst4.append(item)
        else:
            lst4.append(item)
    lst2 = []
    for item in lst4:
        if frac(item) is None:
            lst2.append(item)
    if lst2 == []:
        return product(lst4), sign
    return product(lst2), sign
def multiply_node(equation):
    if equation is None:
        return None
    stack = [(equation, 0, [])]
    while stack:
        node, child_index, processed_children = stack.pop()
        if child_index >= len(node.children):
            node.children = processed_children
            if node.name == "f_mul":
                con = 1
                new_children = []
                for child in reversed(node.children):
                    val = frac(child)
                    if val is not None:
                        con *= val
                    else:
                        new_children.append(child)
                if con == 0:
                    node = tree_form("d_0")
                    if stack:
                        parent, idx, parent_children = stack.pop()
                        parent_children.append(node)
                        stack.append((parent, idx + 1, parent_children))
                        continue
                    else:
                        return node
                node.children = new_children
                base_powers = []
                for child in node.children:
                    if child.name == "f_pow":
                        base, power = child.children
                    else:
                        base = child
                        power = tree_form("d_1")
                    found = False
                    for i, (b, p) in enumerate(base_powers):
                        if flatten_tree(b) == flatten_tree(base):
                            base_powers[i] = (b, p + power)
                            found = True
                            break
                    if not found:
                        base_powers.append((base, power))
                new_mul = TreeNode("f_mul", [])
                for base, power in base_powers:
                    if power == tree_form("d_1"):
                        new_mul.children.append(base)
                    elif power == tree_form("d_0"):
                        continue
                    else:
                        new_mul.children.append(TreeNode("f_pow", [base, power]))
                con_tree = frac_to_tree(con)
                if con_tree != tree_form("d_1"):
                    new_mul.children.append(con_tree)
                if not new_mul.children:
                    node = tree_form("d_1")
                elif len(new_mul.children) == 1:
                    node = new_mul.children[0]
                else:
                    node = new_mul
            if stack:
                parent, idx, parent_children = stack.pop()
                parent_children.append(node)
                stack.append((parent, idx + 1, parent_children))
            else:
                return node  
        else:
            stack.append((node, child_index, processed_children))
            child = node.children[child_index]
            stack.append((child, 0, []))

    return TreeNode("f_add", terms)
def addition_node(equation):
    if equation is None:
        return None
    stack = [(equation, 0, [])]
    while stack:
        node, child_index, processed_children = stack.pop()
        if child_index >= len(node.children):
            node.children = processed_children
            if node.name == "f_add":
                con = 0
                new_children = []
                for child in reversed(node.children):
                    val = frac(child)
                    if val is not None:
                        con += val
                    else:
                        new_children.append(child)
                node.children = new_children
                base_terms = []
                for child in node.children:
                    if child.name == "f_mul":
                        coeff_parts = []
                        base_parts = []
                        for c in child.children:
                            val = frac(c)
                            if val is not None:
                                coeff_parts.append(c)
                            else:
                                base_parts.append(c)
                        if not coeff_parts:
                            coeff = tree_form("d_1")
                        elif len(coeff_parts) == 1:
                            coeff = coeff_parts[0]
                        else:
                            coeff = TreeNode("f_mul", coeff_parts)
                        if not base_parts:
                            base = tree_form("d_1")
                        elif len(base_parts) == 1:
                            base = base_parts[0]
                        else:
                            base = TreeNode("f_mul", base_parts)
                    else:
                        base = child
                        coeff = tree_form("d_1")
                    found = False
                    for i, (b, cff) in enumerate(base_terms):
                        if flatten_tree(b) == flatten_tree(base):
                            base_terms[i] = (b, cff + coeff)
                            found = True
                            break
                    if not found:
                        base_terms.append((base, coeff))
                new_add = TreeNode("f_add", [])
                for base, coeff in base_terms:
                    if coeff == tree_form("d_0"):
                        continue
                    elif coeff == tree_form("d_1"):
                        new_add.children.append(base)
                    else:
                        new_add.children.append(TreeNode("f_mul", [coeff, base]))
                con_tree = frac_to_tree(con)
                if con_tree != tree_form("d_0"):
                    new_add.children.append(con_tree)
                if not new_add.children:
                    node = tree_form("d_0")
                elif len(new_add.children) == 1:
                    node = new_add.children[0]
                else:
                    node = new_add
            if stack:
                parent, idx, parent_children = stack.pop()
                parent_children.append(node)
                stack.append((parent, idx + 1, parent_children))
            else:
                return node
        else:
            stack.append((node, child_index, processed_children))
            child = node.children[child_index]
            stack.append((child, 0, []))
    return tree_form("d_0")
def complex_to_tree(z):
    if z is None:
        return None
    real, imag = z
    parts = []
    if real != 0:
        parts.append(frac_to_tree(real))
    if imag != 0:
        if imag == 1:
            imag_part = tree_form("s_i")
        elif imag == -1:
            imag_part = -tree_form("s_i")
        else:
            imag_part = frac_to_tree(imag) * tree_form("s_i")
        parts.append(imag_part)
    if not parts:
        return tree_form("d_0")
    if len(parts) == 1:
        return parts[0]
    return sum(parts)
def tree_to_complex_strict(root):
    if root is None:
        return None
    stack = [(root, False)]
    values = {}
    while stack:
        node, visited = stack.pop()
        if node is None:
            return None
        if not visited:
            stack.append((node, True))
            if hasattr(node, "children"):
                for child in node.children:
                    stack.append((child, False))
        else:
            name = node.name
            if name.startswith("d_"):
                try:
                    val = Fraction(name[2:])
                except:
                    return None
                values[node] = (val, Fraction(0))
                continue
            if name == "s_i":
                values[node] = (Fraction(0), Fraction(1))
                continue
            if name == "f_neg":
                child = values.get(node.children[0])
                if child is None:
                    return None
                values[node] = (-child[0], -child[1])
                continue
            if name == "f_add":
                real = Fraction(0)
                imag = Fraction(0)
                for c in node.children:
                    val = values.get(c)
                    if val is None:
                        return None
                    real += val[0]
                    imag += val[1]
                values[node] = (real, imag)
                continue
            if name == "f_mul":
                real = Fraction(1)
                imag = Fraction(0)
                for c in node.children:
                    val = values.get(c)
                    if val is None:
                        return None
                    a, b = real, imag
                    c_real, c_imag = val
                    new_real = a*c_real - b*c_imag
                    new_imag = a*c_imag + b*c_real

                    real, imag = new_real, new_imag

                values[node] = (real, imag)
                continue
            if name == "f_pow":
                base = values.get(node.children[0])
                expo = values.get(node.children[1])
                if base is None or expo is None:
                    return None
                if expo[1] != 0:
                    return None
                n = expo[0]
                if n.denominator != 1:
                    return None
                n = n.numerator
                real, imag = base
                result_real = Fraction(1)
                result_imag = Fraction(0)
                if n < 0:
                    n = -n
                    invert = True
                else:
                    invert = False
                for _ in range(n):
                    a, b = result_real, result_imag
                    c, d = real, imag
                    result_real = a*c - b*d
                    result_imag = a*d + b*c
                if invert:
                    denom = result_real**2 + result_imag**2
                    if denom == 0:
                        return None
                    result_real, result_imag = (
                        result_real/denom,
                        -result_imag/denom
                    )
                values[node] = (result_real, result_imag)
                continue
            return None
    return values.get(root)
def other_node(root):
    if root is None:
        return None
    stack = [(root, False)]
    result_map = {}
    while stack:
        eq, visited = stack.pop()
        if eq is None:
            result_map[eq] = None
            continue
        if visited:
            if eq.name == "f_log":
                if len(eq.children) == 1:
                    if eq.children[0].name == "d_1":
                        result_map[eq] = tree_form("d_0")
                        continue
                    if eq.children[0].name == "s_e":
                        result_map[eq] = tree_form("d_1")
                        continue
            if eq.name == "f_mul":
                out = factor_generation(eq)
                index = None
                for i in range(len(out)):
                    for j in range(len(out)):
                        if i == j:
                            continue
                        if out[i].name == "f_sgn" and out[j].name == "f_abs" and out[i].children[0] == out[j].children[0]:
                            index = (i,j,out[i].children[0])
                            break
                    if index is not None:
                        break
                if index is not None:
                    out = list(set([out for i,item in enumerate(out) if i!=index[0] and j!=index[1]]+[index[2]]))
                con = 1
                addition_index = None
                best = -1
                for i in range(len(out)-1,-1,-1):
                    temp = frac(out[i])
                    if temp is not None:
                        con *= temp
                        out.pop(i)
                for i in range(len(out)-1,-1,-1):
                    if out[i].name == "f_add" and con < 0:
                        count = 0
                        for item in out[i].children:
                            if tree_form("d_-1") in factor_generation(item):
                                count += 1
                        if len(out[i].children) == count:
                            addition_index = i
                            best = -2
                        elif best != -2 and count > best:
                            addition_index = i
                            best = count
                        elif addition_index is None:
                            addition_index = i
                if addition_index is not None:
                    temp = out.pop(addition_index)
                    temp = temp.copy_tree()
                    temp.children = [c*tree_form("d_-1") for c in temp.children]
                    result_map[eq] = flatten_tree(frac_to_tree(-con)*product(out)*temp)
                    continue
                if tree_form("d_1") in eq.children:
                    result_map[eq] = product([
                        child
                        for child in eq.children
                        if child != tree_form("d_1")
                    ])
                    continue
            if eq.name == "f_mod" and eq.children[0].name[:2] == "d_" and eq.children[1].name[:2] == "d_":
                a, b = int(eq.children[0].name[2:]), int(eq.children[1].name[2:])
                result_map[eq] = tree_form("d_"+str(a%b))
                continue
            if eq.name == "f_pow" and len(eq.children) == 2:
                a, b = frac(eq.children[0]), frac(eq.children[1])
                b2 = eq.children[1]
                a2 = eq.children[0]
                if a is not None and b is None and b2.name == "f_mul":
                    done = False
                    for i in range(2):
                        if b2.children[i].name == "f_pow" and frac(b2.children[i].children[1]) == -1 and b2.children[i].children[0] == a2.fx("log") and\
                           b2.children[1-i].name == "f_log":
                            result_map[eq] = b2.children[1-i].children[0]
                            done = True
                            break
                    if done:
                        continue
                if a is not None and b is not None and a == 0 and b < 0:
                    result_map[eq] = None
                    continue
                if eq.children[1].name == "d_0":
                    result_map[eq] = tree_form("d_1")
                    continue
                if eq.children[1].name == "d_1":
                    result_map[eq] = eq.children[0]
                    continue
                if eq.children[0].name == "d_1":
                    result_map[eq] = tree_form("d_1")
                    continue
                if (eq.children[0].name == "f_abs"
                        and eq.children[1].name.startswith("d_")
                        and int(eq.children[1].name[2:]) % 2 == 0):
                    result_map[eq] = eq.children[0].children[0] ** eq.children[1]
                    continue
                if eq.children[0].name == "f_mul":
                    n = frac(eq.children[1])
                    if n is not None and n in [Fraction(1,2), Fraction(-1,2)]:
                        lst = [child for child in eq.children[0].children if frac(child) is not None and frac(child)>=0]
                        lst2 = [child for child in eq.children[0].children if not(frac(child) is not None and frac(child)>=0)]
                        n2 = frac_to_tree(n)
                        result_map[eq] = product([
                            child ** n2 for child in lst
                        ])*product(lst2)**n2
                        continue
                    elif n is not None and n < 0 and n.numerator % 2 == 1 and n.denominator == 1:
                        n2 = frac_to_tree(-n)
                        if n2 == tree_form("d_1"):
                            result_map[eq] = product([
                                child ** -1 for child in eq.children[0].children
                            ])
                        else:
                            result_map[eq] = product([
                                child ** -1 for child in eq.children[0].children
                            ]) ** n2
                        continue
                if frac(eq.children[1]) == Fraction(1, 2):
                    d = frac(eq.children[0])
                    if d is not None and d < 0:
                        result_map[eq] = tree_form("s_i") * (
                            frac_to_tree(-d) ** eq.children[1]
                        )
                        continue
                if eq.children[0].name == "f_pow":
                    b = eq.children[0].children[1]
                    c = eq.children[1]
                    out = frac(b * c)
                    if out is not None:
                        out2 = frac(b)
                        if out.numerator % 2 == 0 or (
                            out2 is not None and out2.numerator % 2 != 0
                        ):
                            result_map[eq] = eq.children[0].children[0] ** (b * c)
                        else:
                            result_map[eq] = eq.children[0].children[0].fx("abs") ** (b * c)
                        continue
                    else:
                        tmp = compute(eq.children[0].children[0])
                        if ((tmp is not None and tmp > 0)
                                or eq.children[0].children[0].name == "f_abs"):
                            result_map[eq] = eq.children[0].children[0] ** (b * c)
                            continue
            c = frac(eq)
            if c is not None:
                c = frac_to_tree(c)
                if c != eq:
                    result_map[eq] = c
                    continue
            if eq.name == "f_pow" and eq.children[0].name == "s_e":
                if eq.children[1].name == "f_log":
                    result_map[eq] = eq.children[1].children[0]
                    continue
                if eq.children[1].name == "f_mul":
                    lst = factor_generation(eq.children[1])
                    log = None
                    for i in range(len(lst) - 1, -1, -1):
                        if lst[i].name == "f_log":
                            log = lst[i]
                            lst.pop(i)
                            break
                    if log is not None:
                        result_map[eq] = log.children[0] ** product(lst)
                        continue
            for index, child in enumerate(eq.children):
                out = result_map.get(child)
                if out is None:
                    result_map[eq] = None
                    break
                eq.children[index] = out
            else:
                result_map[eq] = TreeNode(eq.name, eq.children)
        else:
            stack.append((eq, True))
            for child in reversed(eq.children):
                stack.append((child, False))
    return result_map[root]
def com(eq):
    d = tree_to_complex_strict(eq)
    if d is not None:
        tmp = complex_to_tree(d)
        if tmp != eq:
            return tmp
    return eq
def solve3(eq):
    a = lambda x: multiply_node(flatten_tree(x))
    b = lambda x: addition_node(flatten_tree(x))
    c = lambda x: other_node(flatten_tree(x))
    return dowhile(eq, lambda x: a(c(b(x))))
def break_f(eq):
    if eq.name[2:] in "gt ge lt le eq".split(" "):
        if eq.name == "f_eq" and eq.children[0].name == "f_mul" and eq.children[1].name == "d_0":
            lst = list(set([TreeNode("f_eq", [item, tree_form("d_0")]) for item in factor_generation(eq.children[0]) if "v_" in str_form(item)]))
            if lst != []:
                if len(lst) == 1:
                    return lst[0]
                return TreeNode("f_or", lst)
    return eq
def simplify_h(eq):
    if eq is None:
        return None
    stack = [(eq, False)]
    result = {}
    while stack:
        node, visited = stack.pop()
        if node is None:
            continue
        if visited:
            if node.name in ("f_and", "f_or", "f_not"):
                new_children = [result[c] for c in node.children]
                result[node] = TreeNode(node.name, new_children)
                continue
            if node.name[2:] in ("gt", "ge", "lt", "le", "eq"):
                denom = node.name != "f_eq"
                tmp2 = solve3(node.children[0] - node.children[1])
                if tmp2 is None:
                    return None
                tmp, denom = clear_div(tmp2, denom)
                tmp = solve3(tmp)
                if tmp is None:
                    return None
                value2 = node.name[2:]
                if denom is False:
                    value2 = {"ge":"le", "le":"ge", "gt":"lt", "lt":"gt", "eq":"eq"}[value2]
                value2 = "f_" + value2
                result[node] = TreeNode(value2, [tmp, tree_form("d_0")])
                continue
            out = solve3(node)
            if out is None:
                return None
            result[node] = out
            continue
        if node.name in ("f_and", "f_or", "f_not"):
            stack.append((node, True))
            for c in node.children[::-1]:
                stack.append((c, False))
            continue
        stack.append((node, True))
    return result[eq]
def simplify(eq, basic=True, break_factors=False):
    if eq is None:
        return None
    eq = flatten_tree(eq)
    if basic:
        eq = convert_to_basic(eq)
    eq = transform_dfs(eq, com)
    eq = flatten_tree(simplify_h(eq))
    if break_factors:
        eq = transform_dfs(eq, break_f)
    return eq
def log0_helper(eq):
    if eq.name == "f_eq":
        eq2 = simplify(eq.children[0]+tree_form("d_1"))
        if eq2.name == "f_pow" and "v_" in str_form(eq2.children[0]) and "v_" in str_form(eq2.children[1]):
            return (TreeNode("f_eq", [eq2.children[1], tree_form("d_0")])&TreeNode("f_eq", [eq2.children[0], tree_form("d_0")]).fx("not")) | \
                   TreeNode("f_eq", [eq2.children[0], tree_form("d_1")]) | \
                   (TreeNode("f_eq", [eq2.children[0], tree_form("d_-1")])& \
                    TreeNode("f_eq", [TreeNode("f_mod", [eq2.children[1], tree_form("d_2")]), tree_form("d_0")]))
    return eq
def log0(eq):
    return transform_dfs(eq, log0_helper)
