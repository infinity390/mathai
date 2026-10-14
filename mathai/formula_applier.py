import math
import copy
import itertools
from .base import *
from .parser import parse
from .expand import expand
from fractions import Fraction
from .simplify import simplify

_W_NAMES = {"f_add": "f_addw", "f_mul": "f_mulw", "f_hadamard": "f_hadamardw", "f_wadd": "f_waddw"}
_COMMUTATIVE = ("f_addw", "f_mulw")
_LABEL_PREFIXES = ("f_", "s_", "d_")

def en_w_addmul_h(eq):
    new_name = _W_NAMES.get(eq.name)
    if new_name is not None:
        return TreeNode(new_name, eq.children)
    return eq

def en_w_addmul(eq):
    return transform_dfs(eq, en_w_addmul_h)

def get_name(item):
    if hasattr(item, "name"):
        return item.name
    return str(item)

def _collect_labels(node, acc):
    if node.name in ("f_sum"):
        acc.add("f_addw")
    if node.name in ("f_product"):
        acc.add("f_mulw")
    if node.name in ("f_poly"):
        acc.add("f_mulw")
        acc.add("f_addw")
    name = _W_NAMES.get(node.name, node.name)
    if name[:2] in _LABEL_PREFIXES:
        acc.add(name)
    for child in node.children:
        _collect_labels(child, acc)
    return acc

def _node_count(node):
    if not node.children:
        return 1
    return 1 + sum(_node_count(c) for c in node.children)

def _leaf_count(node):
    if not node.children:
        return 1
    return sum(_leaf_count(c) for c in node.children)

def _extract_f_sum_vars(node, v_set):
    if node.name in ("f_add", "f_wadd", "f_wmul", "f_mul", "f_product", "f_sum", "f_poly"):
        for child in node.children:
            if child.name.startswith("v_") and not child.children:
                v_set.add(child.name)
            else:
                _extract_f_sum_vars(child, v_set)
    for child in node.children:
        _extract_f_sum_vars(child, v_set)

def _variable_candidates(eq, out):
    if eq.name in ("f_addw", "f_mulw"):
        base = eq.name[:-1]
        for i in range(1, len(eq.children)):
            for item in itertools.combinations(eq.children, i):
                out.append(operation(base, list(item)))
    else:
        out.extend(eq.children)
    for child in eq.children:
        _variable_candidates(child, out)
    return list(set(out))

def _as_exprs(x):
    if x is None:
        return []
    if isinstance(x, list):
        out = []
        for item in x:
            out += _as_exprs(item)
        return out
    return [x]

def _subst(node, mapping):
    if not node.children and node.name in mapping:
        return copy.deepcopy(mapping[node.name])
    return TreeNode(node.name, [_subst(c, mapping) for c in node.children])

def _value_of(expr, mapping):
    sub = _subst(expr, mapping)
    v = simplify(sub)
    if v is not None:
        v = frac(sub)
    return v

def count_same_nodes(node, cmp):
    count = 1 if node == cmp else 0
    for child in node.children:
        count += count_same_nodes(child, cmp)
    return count

def count_v_nodes(node):
    if node.name in "f_addw f_add f_mulw f_mul f_product f_sum f_poly".split(" "):
        count = 0
        for child in node.children:
            if child.name.startswith("v_"):
                continue
            count += count_v_nodes(child)
        return count
    count = 1 if node.name.startswith("v_") else 0
    for child in node.children:
        count += count_v_nodes(child)
    return count

def _is_plain_variable(node):
    return node.name.startswith("v_") and not node.children

def _match_struct_bind_core(eq, f, binding, const_1_vars, ignore_set, resolved_ignore):
    if f.name == "f_poly":
        for item in vlist(eq):
            out = extract_polynomial_coefficients(de_w_addmul(eq), item, len(f.children)-1)
            if out is not None:
                out = out[::-1][1:]
                if out[0] != 0:
                    local_binding = binding.copy()
                    for i in range(1, len(f.children)):
                        local_binding[f.children[i].name] = out[i-1]
                    local_binding[f.children[0].name] = TreeNode(item)
                    binding.update(local_binding)
                    return True
        return False

    if f.name in ("f_sum", "f_product") and len(f.children) >= 2:
        op_name = "f_addw" if f.name == "f_sum" else "f_mulw"
        if eq.name == op_name and len(eq.children) >= len(f.children):
            local_binding = binding.copy()
            if len(f.children) == 2:
                if (f.children[0].name in const_1_vars and f.children[1].name in const_1_vars) or \
                   (f.children[0].name not in const_1_vars and f.children[1].name not in const_1_vars):
                    local_binding[f.children[0].name] = eq.children[0]
                    local_binding[f.children[1].name] = operation(op_name, eq.children[1:])
                    binding.update(local_binding)
                    return True
                else:
                    const_term = []
                    non_const_term = []
                    
                    for child in eq.children:
                        if vlist(child) == []:
                            const_term.append(child)
                        elif not set(vlist(child)) < resolved_ignore:
                            non_const_term.append(child)
                        else:
                            const_term.append(child)
                    if not const_term:
                        return False
                    if not non_const_term:
                        local_binding[f.children[0].name] = const_term[0]
                        local_binding[f.children[1].name] = operation(op_name, const_term[1:])
                        binding.update(local_binding)
                        return True
                    else:
                        index = 0
                        if f.children[1].name in const_1_vars:
                            index = 1
                        local_binding[f.children[index].name] = operation(op_name, const_term)
                        local_binding[f.children[1-index].name] = operation(op_name, non_const_term)
                        binding.update(local_binding)
                        return True

    if f.name.startswith("v_") and not f.children:
        f_str = str_form(f)
        if f_str in binding:
            return str_form(eq) == str_form(binding[f_str])
        else:
            binding[f_str] = eq
            return True

    if eq.name != f.name:
        return False

    fc = f.children
    ec = eq.children
    n = len(fc)
    if len(ec) != n:
        return False

    if f.name in _COMMUTATIVE and n > 1:
        for p in itertools.permutations(range(n)):
            sub_binding = binding.copy()
            if all(_match_struct_bind_core(ec[p[i]], fc[i], sub_binding, const_1_vars, ignore_set, resolved_ignore) for i in range(n)):
                binding.update(sub_binding)
                return True
        return False

    sub_binding = binding.copy()
    for i in range(n):
        if not _match_struct_bind_core(ec[i], fc[i], sub_binding, const_1_vars, ignore_set, resolved_ignore):
            return False
    binding.update(sub_binding)
    return True

def _match_struct_bind(eq, f, binding, const_1_vars=None, ignore_set=None, assigned_mapping=None):
    if assigned_mapping is None:
        assigned_mapping = {}
    if const_1_vars is None:
        const_1_vars = set()
    if ignore_set is None:
        ignore_set = set()
        
    pass1_binding = binding.copy()
    _match_struct_bind_core(eq, f, pass1_binding, const_1_vars, ignore_set, set())
    
    resolved_ignore = set()
    for ign in ignore_set:
        if ign in pass1_binding:
            resolved_ignore.add(str_form(pass1_binding[ign]))
        if ign in assigned_mapping:
            resolved_ignore.add(str_form(assigned_mapping[ign]))

    return _match_struct_bind_core(eq, f, binding, const_1_vars, ignore_set, resolved_ignore)

class _Matcher:
    def __init__(self, formula, formula_out, positive=None, negative=None, ignore_list=None, const_1=None):
        self.orig_formula = formula
        self.formula_out = formula_out
        self.formula_w = en_w_addmul(copy.deepcopy(formula))
        self.root_name = self.formula_w.name
        self.labels = _collect_labels(self.formula_w, set())
        
        vl_set = set(vlist(self.formula_w))
        f_sum_vars = set()
        _extract_f_sum_vars(self.formula_w, f_sum_vars)
        vl_set = vl_set - f_sum_vars
        self.vl = list(vl_set)
        
        self.positive = _as_exprs(positive)
        self.negative = _as_exprs(negative)
        
        ignore = {get_name(item) for item in _as_exprs(ignore_list)}
        self.ignore_list_exprs = _as_exprs(ignore_list)
        self.ignore_set = ignore
        self.must_be_var = {name: (name in ignore and name not in f_sum_vars) for name in self.vl}
        self.ignore_given = bool(ignore)
        
        const = {get_name(item) for item in _as_exprs(const_1)}
        self.must_be_const = {name: (name in const) for name in self.vl}
        self.const_1_vars = const

    def conditions_hold(self, mapping):
        for exprs, sign in ((self.positive, 1), (self.negative, -1)):
            for expr in exprs:
                v = _value_of(expr, mapping)
                if v is None or sign * v < 0:
                    return False
        return True

    def __call__(self, equation):
        equation = simplify(equation)
        orig = equation
        eq_w = en_w_addmul(copy.deepcopy(orig))

        vc = [eq_w] + _variable_candidates(eq_w, [])
        seen = set()
        unique_vc = []
        for item in vc:
            de_item = de_w_addmul(item)
            s = str_form(de_item)
            if s not in seen:
                seen.add(s)
                unique_vc.append(de_item)
        vc = unique_vc
        result = self._assign(copy.deepcopy(orig), vc)
        return orig if result is None else result
    
    def _assign(self, orig, vc):
        variables = list(self.vl)
        n = len(variables)
        def check(assigned_mapping):
            if len(assigned_mapping) == n:
                equation = copy.deepcopy(self.orig_formula)
                for var_name, cand in assigned_mapping.items():
                    equation = replace(equation, TreeNode(var_name), cand)
                equation = flatten_tree(equation)
                eq_w = en_w_addmul(copy.deepcopy(orig))
                eq_cand_w = en_w_addmul(copy.deepcopy(equation))
                binding = {}
                if not _match_struct_bind(eq_w, eq_cand_w, binding, self.const_1_vars, set([item.name for item in self.ignore_list_exprs]), assigned_mapping):
                    return None
                binding = {key: de_w_addmul(item) for key, item in binding.items()}
                assigned_mapping.update(binding)
                
                if self.positive != [] or self.negative != []:
                    if not self.conditions_hold(assigned_mapping):
                        return None
                result = copy.deepcopy(self.formula_out)
                for var_name, cand in assigned_mapping.items():
                    result = replace(result, TreeNode(var_name), cand)
                return result
            return None
        if n == 0:
            return check({})
        
        if not vc:
            return None
        
        is_var = [_is_plain_variable(candidate) for candidate in vc]
        is_const = [("v_" not in str_form(x)) for x in vc]
        same_count = [count_same_nodes(self.orig_formula, TreeNode(x)) for x in variables]
        domains = {}
        for var in variables:
            valid = []
            for i, cand in enumerate(vc):
                if self.must_be_var[var] and not is_var[i]:
                    continue
                if self.must_be_const[var] and not is_const[i]:
                    continue
                valid.append(i)
            domains[var] = valid

        target = _leaf_count(orig)
        
        def dfs(domains, mapping, count=0, i=0):
            if i == n:
                return check(mapping)
            if count >= target:
                return None
            var_name = variables[i]
            sc = same_count[i]
            for item in domains[var_name]:
                cand = vc[item]
                mapping[var_name] = cand
                out = dfs(domains, mapping, count + _leaf_count(cand) * sc, i + 1)
                if out is not None:
                    return out
                del mapping[var_name]
            return None

        return dfs(domains, {})

def structure(equation, formula, formula_out, ignore_list=None, const_1=None, positive=None, negative=None):
    return _Matcher(formula, formula_out, positive, negative, ignore_list, const_1)(equation)

def convert_lst(eq):
    if eq.name == "f_list":
        return [convert_lst(child) for child in eq.children]
    return TreeNode(eq.name, [convert_lst(child) for child in eq.children])

def convert_string(s):
    if s == "_":
        return None
    return convert_lst(parse(s))

def wrap_h(eq, fx):
    out = fx(simplify(eq))
    if out is not None:
        return out
    return eq

def _replace_in(x, key, value):
    if x is None:
        return None
    if isinstance(x, list):
        return [_replace_in(item, key, value) for item in x]
    return replace(x, key, value)

def formula_applier(eq, s):
    item = s.split(" ")
    a, b = (simplify(parse(x)) for x in item[:2])
    subs = {}
    for key, value in convert_string(item[2]):
        subs.setdefault(key, [None]).append(value)
    lst = [convert_string(x) for x in item[3:]]
    lst += [None] * (4 - len(lst))
    ignore_list, const_1, positive, negative = lst[:4]
    subs_x = list(subs)
    subs_y = list(subs.values())
    for combination in itertools.product(*subs_y):
        x, y, pos, neg = a, b, positive, negative
        for key, value in zip(subs_x, combination):
            if value is not None:
                x = replace(x, key, value)
                y = replace(y, key, value)
                pos = _replace_in(pos, key, value)
                neg = _replace_in(neg, key, value)
        x, y = simplify(x), simplify(y)
        matcher = _Matcher(x, y, pos, neg, ignore_list, const_1)
        eq = dowhile(eq, lambda u: transform_dfs(u, matcher))
    return eq

def extract_polynomial_coefficients(eq, var, degree):
    current_eq = copy.deepcopy(eq)
    zero_node = TreeNode("d_0")
    var_node = TreeNode(var)
    coefficients = []
    for i in range(degree + 1):
        subbed_zero = replace(copy.deepcopy(current_eq), var_node, zero_node)
        c_val = simplify(subbed_zero)
        if c_val is None:
            return None
        coefficients.append(c_val)
        num = operation("f_sub", [current_eq, c_val])
        simplified_num = simplify(num)
        if simplified_num == 0:
            while len(coefficients) <= degree:
                coefficients.append(TreeNode("d_0"))
            return coefficients
        div_node = operation("f_div", [simplified_num, var_node])
        current_eq = simplify(expand(simplify(div_node)))
        if current_eq is None:
            return None
    final_sub = replace(copy.deepcopy(current_eq), var_node, zero_node)
    final_check = simplify(final_sub)
    if final_check != 0:
        return None
    return coefficients

def formula_list_applier_h(eq, s):
    for item in s.strip().split("\n"):
        if not item.strip():
            continue
        eq = formula_applier(eq, item)
    return eq

def formula_list_applier(eq, s):
    return dowhile(eq, lambda x: formula_list_applier_h(x, s))

def de_w_addmul_h(eq):
    if eq.name in ("f_addw", "f_mulw", "f_waddw", "f_hadamardw"):
        return TreeNode(eq.name[:-1], eq.children)
    return eq

def de_w_addmul(eq):
    return transform_dfs(eq, de_w_addmul_h)
