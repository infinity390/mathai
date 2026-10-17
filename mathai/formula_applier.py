import copy
import itertools
from functools import lru_cache
from .base import *
from .parser import parse
from .expand import expand
from .simplify import simplify

_W_NAMES = {
    "f_add": "f_addw",
    "f_mul": "f_mulw",
    "f_hadamard": "f_hadamardw",
    "f_wadd": "f_waddw",
    "f_wmul": "f_wmulw",
}
_COMMUTATIVE = frozenset(("f_addw", "f_mulw", "f_hadamardw"))
_ORDERED_ASSOC = frozenset(("f_wmulw",))
_LABEL_PREFIXES = frozenset(("f_", "s_", "d_"))
_SPECIAL_PATTERN = frozenset(("f_poly", "f_sum", "f_product", "f_hprod"))
_PATTERN_OPS = {"f_sum": "f_addw", "f_product": "f_mulw", "f_hprod": "f_hadamardw"}
_AGG_NAMES = frozenset((
    "f_addw", "f_add", "f_mulw", "f_mul", "f_hadamardw", "f_hadamard",
    "f_product", "f_sum", "f_hprod", "f_poly",
))
_EXTRACT_NAMES = frozenset((
    "f_add", "f_wadd", "f_waddw", "f_wmul", "f_wmulw",
    "f_mul", "f_product", "f_sum", "f_hprod", "f_poly",
))
_DE_W_NAMES = frozenset(("f_addw", "f_mulw", "f_waddw", "f_hadamardw", "f_wmulw"))


def transform_dfs(node, fn, stable=None):
    if node is None:
        return None
    if stable is not None and node in stable:
        return node
    children = node.children
    if children is None:
        return fn(node)
    new_children = [transform_dfs(c, fn, stable) for c in children]
    if any(c is None for c in new_children):
        return None
    unchanged = True
    for a, b in zip(new_children, children):
        if a is not b:
            unchanged = False
            break
    cur = node if unchanged else TreeNode(node.name, new_children)
    out = fn(cur)
    if out is not None and out is not cur and out == cur:
        out = cur
    if stable is not None and unchanged and out is cur:
        stable[cur] = cur
    return out


def dowhile(x, fn):
    while True:
        y = fn(x)
        if y is x or y == x or y is None:
            return x if y is None else y
        x = y


def _fixpoint(eq, fn):
    if eq is None:
        return None
    stable = {}
    while True:
        new = transform_dfs(eq, fn, stable)
        if new is eq or new == eq or new is None:
            return eq if new is None else new
        eq = new


def en_w_addmul_h(eq):
    if eq is None:
        return None
    new_name = _W_NAMES.get(eq.name)
    if new_name is not None:
        return TreeNode(new_name, eq.children)
    return eq


def en_w_addmul(eq):
    return transform_dfs(eq, en_w_addmul_h)


def de_w_addmul_h(eq):
    if eq is None:
        return None
    if eq.name in _DE_W_NAMES:
        return TreeNode(eq.name[:-1], eq.children)
    return eq


def de_w_addmul(eq):
    return transform_dfs(eq, de_w_addmul_h)


def get_name(item):
    return item.name if hasattr(item, "name") else str(item)


def _collect_labels(node, acc):
    if node is None:
        return acc
    if node.name == "f_sum":
        acc.add("f_addw")
    elif node.name == "f_product":
        acc.add("f_mulw")
    elif node.name == "f_hprod":
        acc.add("f_hadamardw")
    elif node.name == "f_poly":
        acc.add("f_mulw")
        acc.add("f_addw")
    name = _W_NAMES.get(node.name, node.name)
    if name[:2] in _LABEL_PREFIXES:
        acc.add(name)
    for child in node.children:
        _collect_labels(child, acc)
    return acc


def _node_names(node, acc):
    if node is None:
        return acc
    acc.add(node.name)
    for c in node.children:
        _node_names(c, acc)
    return acc


def _leaf_count(node):
    if node is None:
        return 0
    if not node.children:
        return 1
    return sum(_leaf_count(c) for c in node.children)


def _extract_f_sum_vars(node, v_set):
    if node is None:
        return
    is_agg = node.name in _EXTRACT_NAMES
    for child in node.children:
        if is_agg and child.name.startswith("v_") and not child.children:
            v_set.add(child.name)
        else:
            _extract_f_sum_vars(child, v_set)


def _collect_candidates(eq, out):
    if eq is None:
        return
    if eq.name in _COMMUTATIVE:
        base = eq.name[:-1]
        ch = eq.children
        for i in range(1, len(ch)):
            for item in itertools.combinations(ch, i):
                out.append(operation(base, list(item)))
    elif eq.name in _ORDERED_ASSOC:
        base = eq.name[:-1]
        ch = eq.children
        n = len(ch)
        for length in range(1, n):
            for s in range(n - length + 1):
                out.append(operation(base, list(ch[s:s + length])))
    else:
        out.extend(eq.children)
    for child in eq.children:
        _collect_candidates(child, out)


def _variable_candidates(eq, out):
    if eq is None:
        return []
    _collect_candidates(eq, out)
    return list(dict.fromkeys(out))


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
    if node is None:
        return None
    if not node.children and node.name in mapping:
        val = mapping[node.name]
        if val is None:
            return None
        return copy.deepcopy(val)
    new_children = []
    for c in node.children:
        res = _subst(c, mapping)
        if res is None:
            return None
        new_children.append(res)
    return TreeNode(node.name, new_children)


def _value_of(expr, mapping):
    if expr is None:
        return None
    sub = _subst(expr, mapping)
    if sub is None:
        return None
    v = simplify(sub)
    if v is not None:
        v = frac(sub)
    return v


def count_same_nodes(node, cmp):
    if node is None:
        return 0
    count = 1 if node == cmp else 0
    for child in node.children:
        count += count_same_nodes(child, cmp)
    return count


def count_v_nodes(node):
    if node is None:
        return 0
    if node.name in _AGG_NAMES:
        return sum(count_v_nodes(c) for c in node.children if not c.name.startswith("v_"))
    count = 1 if node.name.startswith("v_") else 0
    for child in node.children:
        count += count_v_nodes(child)
    return count


def _is_plain_variable(node):
    return node is not None and node.name.startswith("v_") and not node.children


def _match_struct_bind_core(eq, f, binding, const_1_vars, ignore_set, resolved_ignore, free_vars):
    if eq is None or f is None:
        return False
    fname = f.name
    if fname == "f_poly":
        eq_plain = de_w_addmul(eq)
        degree = len(f.children) - 1
        for item in vlist(eq):
            out = extract_polynomial_coefficients(eq_plain, item, degree)
            if out is not None:
                out = out[::-1][1:]
                if out[0] != 0:
                    local_binding = binding.copy()
                    for i in range(1, len(f.children)):
                        local_binding[f.children[i].name] = out[i - 1]
                    local_binding[f.children[0].name] = TreeNode(item)
                    binding.update(local_binding)
                    return True
        return False
    if fname in _PATTERN_OPS and len(f.children) >= 2:
        op_name = _PATTERN_OPS[fname]
        if eq.name == op_name and len(eq.children) >= len(f.children):
            if len(f.children) == 2:
                local_binding = binding.copy()
                c0, c1 = f.children[0].name, f.children[1].name
                if (c0 in const_1_vars) == (c1 in const_1_vars):
                    local_binding[c0] = eq.children[0]
                    local_binding[c1] = operation(op_name, eq.children[1:])
                    binding.update(local_binding)
                    return True
                const_term, non_const_term = [], []
                for child in eq.children:
                    vl = vlist(child)
                    if vl and not set(vl) < resolved_ignore:
                        non_const_term.append(child)
                    else:
                        const_term.append(child)
                if not const_term:
                    return False
                if not non_const_term:
                    local_binding[c0] = const_term[0]
                    local_binding[c1] = operation(op_name, const_term[1:])
                else:
                    index = 1 if c1 in const_1_vars else 0
                    local_binding[f.children[index].name] = operation(op_name, const_term)
                    local_binding[f.children[1 - index].name] = operation(op_name, non_const_term)
                binding.update(local_binding)
                return True
    if fname.startswith("v_") and not f.children and fname in free_vars:
        f_str = str_form(f)
        if f_str in binding:
            return str_form(eq) == str_form(binding[f_str])
        binding[f_str] = eq
        return True
    if eq.name != fname:
        return False
    fc, ec = f.children, eq.children
    n = len(fc)

    if fname in _ORDERED_ASSOC:
        m = len(ec)
        if m < n:
            return False

        def search_ordered(i, j, b):
            if i == n:
                return b if j == m else None
            pat = fc[i]
            free = (not pat.children) and pat.name in free_vars
            remaining_pats = n - i - 1
            max_len = (m - j - remaining_pats) if free else 1
            for L in range(1, max_len + 1):
                seg = ec[j] if L == 1 else TreeNode(fname, list(ec[j:j + L]))
                sb = b.copy()
                if _match_struct_bind_core(seg, pat, sb, const_1_vars,
                                           ignore_set, resolved_ignore, free_vars):
                    r = search_ordered(i + 1, j + L, sb)
                    if r is not None:
                        return r
            return None

        result = search_ordered(0, 0, binding)
        if result is None:
            return False
        binding.update(result)
        return True

    if len(ec) != n:
        return False
    if fname in _COMMUTATIVE and n > 1:
        compat = [
            [
                (fc[i].name in free_vars and not fc[i].children)
                or fc[i].name in _SPECIAL_PATTERN
                or fc[i].name == ec[j].name
                for j in range(n)
            ]
            for i in range(n)
        ]

        def search(i, used, b):
            if i == n:
                return b
            for j in range(n):
                if j in used or not compat[i][j]:
                    continue
                sb = b.copy()
                if _match_struct_bind_core(ec[j], fc[i], sb, const_1_vars,
                                           ignore_set, resolved_ignore, free_vars):
                    r = search(i + 1, used | {j}, sb)
                    if r is not None:
                        return r
            return None

        result = search(0, frozenset(), binding)
        if result is None:
            return False
        binding.update(result)
        return True
    sub_binding = binding.copy()
    for i in range(n):
        if not _match_struct_bind_core(ec[i], fc[i], sub_binding, const_1_vars,
                                       ignore_set, resolved_ignore, free_vars):
            return False
    binding.update(sub_binding)
    return True


def _match_struct_bind(eq, f, binding, const_1_vars=None, ignore_set=None,
                       assigned_mapping=None, free_vars=frozenset()):
    assigned_mapping = assigned_mapping or {}
    const_1_vars = const_1_vars or set()
    ignore_set = ignore_set or set()
    resolved_ignore = set()
    if ignore_set:
        pass1_binding = binding.copy()
        _match_struct_bind_core(eq, f, pass1_binding, const_1_vars, ignore_set, resolved_ignore, free_vars)
        for ign in ignore_set:
            if ign in pass1_binding:
                resolved_ignore.add(str_form(pass1_binding[ign]))
            if ign in assigned_mapping:
                resolved_ignore.add(str_form(assigned_mapping[ign]))
    return _match_struct_bind_core(eq, f, binding, const_1_vars, ignore_set, resolved_ignore, free_vars)


class _Matcher:
    def __init__(self, formula, formula_out, positive=None, negative=None, ignore_list=None, const_1=None, forbidden_list=None):
        self.orig_formula = formula
        self.formula_out = formula_out
        self.formula_w = en_w_addmul(formula)
        self.root_name = self.formula_w.name if self.formula_w else ""
        f_sum_vars = set()
        _extract_f_sum_vars(self.formula_w, f_sum_vars)
        self.free_vars = frozenset(f_sum_vars)
        self.positive = _as_exprs(positive)
        self.negative = _as_exprs(negative)
        self.ignore_list_exprs = _as_exprs(ignore_list)
        self.ignore_set = {get_name(item) for item in self.ignore_list_exprs}
        self.ignore_names = {item.name for item in self.ignore_list_exprs}
        self.forbidden_list_exprs = _as_exprs(forbidden_list)
        
        names = set(vlist(self.formula_w)) - f_sum_vars if self.formula_w else set()
        self.vl = sorted(names, key=lambda n: (0 if n in self.ignore_set else 1, n))
        self.must_be_var = {n: (n in self.ignore_set and n not in f_sum_vars) for n in self.vl}
        self.const_1_vars = {get_name(item) for item in _as_exprs(const_1)}
        self.must_be_const = {n: (n in self.const_1_vars) for n in self.vl}
        self.root_is_free = (
            not self.formula_w
            or (self.root_name.startswith("v_") and not self.formula_w.children)
            or self.root_name in _SPECIAL_PATTERN
        )
        self.required = {
            n for n in _node_names(self.formula_w, set())
            if n[:2] in _LABEL_PREFIXES and n not in _SPECIAL_PATTERN
        }
        self._same_count = [count_same_nodes(self.orig_formula, TreeNode(x)) for x in self.vl]

    def _is_forbidden(self, mapping):
        if not self.forbidden_list_exprs:
            return False
        for forb_pair in self.forbidden_list_exprs:
            if isinstance(forb_pair, list) and len(forb_pair) == 2:
                expr_part, forb_val = forb_pair[0], forb_pair[1]
                subbed_expr = _subst(expr_part, mapping)
                subbed_val = _subst(forb_val, mapping)
                if subbed_expr is None or subbed_val is None:
                    return True
                simp_expr = simplify(subbed_expr)
                simp_val = simplify(subbed_val)
                if simp_expr is None or simp_val is None or simp_expr == simp_val:
                    return True
        return False

    def conditions_hold(self, mapping):
        for exprs, sign in ((self.positive, 1), (self.negative, -1)):
            for expr in exprs:
                v = _value_of(expr, mapping)
                if v is None or sign * v < 0:
                    return False
        return True

    def __call__(self, equation):
        if equation is None:
            return None
        orig = simplify(equation)
        if orig is None:
            return equation
        eq_w = en_w_addmul(orig)
        if eq_w is None:
            return orig
        if not self.root_is_free and eq_w.name != self.root_name:
            return orig
        if self.required and not self.required <= _node_names(eq_w, set()):
            return orig
        seen, vc = set(), []
        for item in [eq_w] + _variable_candidates(eq_w, []):
            de_item = de_w_addmul(item)
            if de_item is not None:
                s = str_form(de_item)
                if s not in seen:
                    seen.add(s)
                    vc.append(de_item)
        result = self._assign(orig, eq_w, vc)
        return orig if result is None else result

    def _assign(self, orig, eq_w, vc):
        variables = self.vl
        n = len(variables)

        def check(assigned_mapping):
            if len(assigned_mapping) != n:
                return None
            if self._is_forbidden(assigned_mapping):
                return None
            equation = copy.deepcopy(self.orig_formula)
            for var_name, cand in assigned_mapping.items():
                equation = replace(equation, TreeNode(var_name), cand)
            equation = flatten_tree(equation)
            eq_cand_w = en_w_addmul(equation)
            binding = {}
            if not _match_struct_bind(eq_w, eq_cand_w, binding, self.const_1_vars,
                                       self.ignore_names, assigned_mapping, self.free_vars):
                return None
            full_mapping = dict(assigned_mapping)
            full_mapping.update({k: de_w_addmul(v) for k, v in binding.items()})
            
            if self._is_forbidden(full_mapping):
                return None

            banned = set()
            for ign in self.ignore_names:
                if ign in full_mapping:
                    banned.update(vlist(full_mapping[ign]))
            if banned:
                for cname in self.const_1_vars:
                    if cname in full_mapping and banned.intersection(vlist(full_mapping[cname])):
                        return None
            if (self.positive or self.negative) and not self.conditions_hold(full_mapping):
                return None
            result = copy.deepcopy(self.formula_out)
            for var_name, cand in full_mapping.items():
                result = replace(result, TreeNode(var_name), cand)
            return simplify(result)

        if n == 0:
            return check({})
        if not vc:
            return None
        is_var = [_is_plain_variable(c) for c in vc]
        cand_vars = [frozenset(vlist(c)) for c in vc]
        leaves = [_leaf_count(c) for c in vc]
        same_count = self._same_count
        rng = range(len(vc))
        domains = [
            [i for i in rng if not (self.must_be_var[v] and not is_var[i])]
            for v in variables
        ]
        target = _leaf_count(orig)

        def dfs(mapping, count, i, banned):
            if i == n:
                return check(mapping)
            if count >= target:
                return None
            var_name, sc = variables[i], same_count[i]
            must_const = self.must_be_const[var_name]
            must_var = self.must_be_var[var_name]
            for idx in domains[i]:
                if must_const and banned and not banned.isdisjoint(cand_vars[idx]):
                    continue
                mapping[var_name] = vc[idx]
                if self._is_forbidden(mapping):
                    del mapping[var_name]
                    continue
                nb = (banned | cand_vars[idx]) if must_var else banned
                out = dfs(mapping, count + leaves[idx] * sc, i + 1, nb)
                if out is not None:
                    return out
                del mapping[var_name]
            return None

        return dfs({}, 0, 0, frozenset())


def structure(equation, formula, formula_out, ignore_list=None, const_1=None, positive=None, negative=None, forbidden_list=None):
    return _Matcher(formula, formula_out, positive, negative, ignore_list, const_1, forbidden_list)(equation)


def convert_lst(eq):
    if eq is None:
        return None
    if eq.name == "f_list":
        return [convert_lst(child) for child in eq.children]
    return TreeNode(eq.name, [convert_lst(child) for child in eq.children])


def convert_string(s):
    if s == "_":
        return None
    parsed = parse(s)
    if parsed is None:
        return None
    return convert_lst(parsed)


def wrap_h(eq, fx):
    if eq is None:
        return None
    out = fx(simplify(eq))
    return eq if out is None else out


def _replace_in(x, key, value):
    if x is None:
        return None
    if isinstance(x, list):
        return [_replace_in(item, key, value) for item in x]
    return replace(x, key, value)


@lru_cache(maxsize=None)
def _compile_rule(s):
    item = s.split(" ")
    a, b = (simplify(parse(x)) for x in item[:2])
    subs = {}
    parsed_subs = convert_string(item[2])
    if parsed_subs:
        for key, value in parsed_subs:
            subs.setdefault(key, [None]).append(value)
    
    lst = [convert_string(x) for x in item[3:]]
    lst += [None] * (5 - len(lst))
    ignore_list, const_1, positive, negative, forbidden_list = lst[:5]
    
    keys = tuple(subs)
    matchers = []
    for combination in itertools.product(*subs.values()):
        x, y, pos, neg, forb = a, b, positive, negative, forbidden_list
        valid_comb = True
        for key, value in zip(keys, combination):
            if value is not None:
                x = replace(x, key, value)
                y = replace(y, key, value)
                pos = _replace_in(pos, key, value)
                neg = _replace_in(neg, key, value)
                forb = _replace_in(forb, key, value)
        
        if forbidden_list is not None:
            comb_map = {k: v for k, v in zip(keys, combination) if v is not None}
            for forb_pair in _as_exprs(forbidden_list):
                if isinstance(forb_pair, list) and len(forb_pair) == 2:
                    sub_expr = _subst(forb_pair[0], comb_map)
                    sub_val = _subst(forb_pair[1], comb_map)
                    if sub_expr is None or sub_val is None:
                        valid_comb = False
                        break
                    simp_expr = simplify(sub_expr)
                    simp_val = simplify(sub_val)
                    if simp_expr is None or simp_val is None or simp_expr == simp_val:
                        valid_comb = False
                        break
        
        if valid_comb:
            simp_x = simplify(x)
            simp_y = simplify(y)
            if simp_x is not None and simp_y is not None:
                matchers.append(_Matcher(simp_x, simp_y, pos, neg, ignore_list, const_1, forb))
    return tuple(matchers)


def formula_applier(eq, s):
    if eq is None:
        return None
    for matcher in _compile_rule(s):
        eq = _fixpoint(eq, matcher)
    return eq


@lru_cache(maxsize=None)
def _split_rules(s):
    return tuple(line for line in s.strip().split("\n") if line.strip())


def formula_list_applier_h(eq, s):
    if eq is None:
        return None
    for item in _split_rules(s):
        eq = formula_applier(eq, item)
    return eq


def formula_list_applier(eq, s):
    if eq is None:
        return None
    return dowhile(eq, lambda x: formula_list_applier_h(x, s))


def extract_polynomial_coefficients(eq, var, degree):
    if eq is None:
        return None
    current_eq = copy.deepcopy(eq)
    zero_node = TreeNode("d_0")
    var_node = TreeNode(var)
    coefficients = []
    for _ in range(degree + 1):
        c_val = simplify(replace(copy.deepcopy(current_eq), var_node, zero_node))
        if c_val is None:
            return None
        coefficients.append(c_val)
        simplified_num = simplify(operation("f_sub", [current_eq, c_val]))
        if simplified_num == 0:
            coefficients.extend(TreeNode("d_0") for _ in range(degree + 1 - len(coefficients)))
            return coefficients
        current_eq = simplify(expand(simplify(operation("f_div", [simplified_num, var_node]))))
        if current_eq is None:
            return None
    final_check = simplify(replace(copy.deepcopy(current_eq), var_node, zero_node))
    return coefficients if final_check == 0 else None
