import copy
import itertools
import textwrap
import warnings
from .base import *
from .simplify import simplify
from .parser import parse
from .formula_applier import (
    extract_polynomial_coefficients, convert_string, _as_pairs, _replace_in,
    _as_exprs, get_name, en_w_addmul, formula_applier,
)

try:
    from .formula_applier import _split_rules
except ImportError:
    def _split_rules(s):
        return tuple(line for line in s.strip().split("\n") if line.strip())


# --- CONSTANTS & CONFIGURATION ---

_W_NAMES = {
    "f_add": "f_addw",
    "f_mul": "f_mulw",
    "f_hadamard": "f_hadamardw",
    "f_wadd": "f_waddw",
    "f_wmul": "f_wmulw",
}
_COMMUTATIVE = frozenset(("f_addw", "f_mulw", "f_hadamardw", "f_waddw"))
_ORDERED_ASSOC = frozenset(("f_wmulw",))
_LABEL_PREFIXES = frozenset(("f_", "s_", "d_"))
_SPECIAL_PATTERN = frozenset(("f_poly", "f_sum", "f_wsum", "f_product", "f_hprod", "f_mprod"))
_PATTERN_OPS = {
    "f_sum": "f_addw",
    "f_product": "f_mulw",
    "f_hprod": "f_hadamardw",
    "f_wsum": "f_waddw",
}
_ORDERED_PATTERN_OPS = {"f_mprod": "f_wmulw"}
_AGG_NAMES = frozenset((
    "f_addw", "f_add", "f_mulw", "f_mul", "f_hadamardw", "f_hadamard",
    "f_product", "f_sum", "f_wsum", "f_hprod", "f_mprod", "f_poly", "f_wmulw", "f_wmul",
))
_EXTRACT_NAMES = frozenset((
    "f_add", "f_wadd", "f_waddw", "f_wmul", "f_wmulw",
    "f_mul", "f_product", "f_sum", "f_wsum", "f_hprod", "f_mprod", "f_poly",
))
_DE_W_NAMES = frozenset(("f_addw", "f_mulw", "f_waddw", "f_hadamardw", "f_wmulw"))


# --- TREE NODE CLASS ---

if "TreeNode" not in globals():
    class TreeNode:
        def __init__(self, name, children=None):
            if children is None:
                children = []
            self.name = name
            self.children = copy.deepcopy(children)

        def __repr__(self):
            if not self.children:
                return repr(self.name)
            return f"TreeNode({self.name!r}, {self.children!r})"

        def __eq__(self, other):
            if not (hasattr(other, "name") and hasattr(other, "children")):
                return NotImplemented
            return self.name == other.name and list(self.children) == list(other.children)

        def __hash__(self):
            return hash((self.name, tuple(self.children)))

        def fx(self, op):
            if not op.startswith(tuple(_LABEL_PREFIXES)):
                op = "f_" + op
            return TreeNode(op, [self])

        def __add__(self, o): return TreeNode("f_add", [self, o])
        def __radd__(self, o): return TreeNode("f_add", [o, self])
        def __mul__(self, o): return TreeNode("f_mul", [self, o])
        def __rmul__(self, o): return TreeNode("f_mul", [o, self])
        def __pow__(self, o): return TreeNode("f_pow", [self, o])
        def __invert__(self): return TreeNode("f_not", [self])


# --- PERMUTATION GENERATOR ---

def generate_tree_permutations(node):
    """All valid permutations of a tree, respecting commutative / ordered ops."""
    if not node.children:
        yield TreeNode(node.name)
        return

    child_perms_list = [list(generate_tree_permutations(c)) for c in node.children]

    for combined_children in itertools.product(*child_perms_list):
        if node.name in _COMMUTATIVE:
            seen = set()
            for perm in itertools.permutations(combined_children):
                sig = tuple(repr(c) for c in perm)
                if sig not in seen:
                    seen.add(sig)
                    yield TreeNode(node.name, list(perm))
        else:
            yield TreeNode(node.name, list(combined_children))


# --- CODE PRINTING & DE-W HELPERS ---

def de_w_addmul_h(eq):
    if eq.name in _DE_W_NAMES:
        return TreeNode(eq.name[:-1], eq.children)
    return eq


def de_w_addmul(eq):
    return transform_dfs(eq, de_w_addmul_h)


def print_condition(eq, printer=None):
    printer = printer or print_code_h
    assert eq.name == "f_condition"

    def emit(i):
        if i >= len(eq.children):
            return "None"
        branch = eq.children[i]
        if branch.name in ("f_else", "else"):
            return printer(branch.children[0])
        cond = printer(branch.children[0])
        value = printer(branch.children[1])
        return f"({value} if {cond} else {emit(i + 1)})"
    return emit(0)


def print_code_h(eq):
    if eq.name == "s_true":
        return "True"
    if eq.name == "s_false":
        return "False"
    if eq.name == "f_not":
        return f"(not {print_code_h(eq.children[0])})"
    binary = {
        "f_==": "==",
        "f_!=": "!=",
        "f_wor": "or",
        "f_wand": "and",
        "f_>": ">",
        "f_>=": ">=",
    }
    if eq.name in binary:
        op = f" {binary[eq.name]} "
        return "(" + op.join(print_code_h(c) for c in eq.children) + ")"
    if eq.name == "f_index":
        return f"{print_code_h(eq.children[0])}[{eq.children[1]}]"
    if eq.name == "f_any":
        return f"any({print_code_h(eq.children[0])} {print_code_h(eq.children[1])})"
    if eq.name == "f_list":
        return "[" + ", ".join(print_code_h(c) for c in eq.children) + "]"
    if eq.name == "f_condition":
        return print_condition(eq)
    if not eq.children:
        return eq.name
    return f"{eq.name}(" + ", ".join(print_code_h(c) for c in eq.children) + ")"


def print_code2_with_varlist(eq, varlist):
    if eq is None:
        return "None"
    if not eq.children and eq.name in varlist:
        return varlist[eq.name]
    if eq.name.startswith(("d_", "v_", "s_")):
        return f"tree_form('{eq.name}')"

    def rec(c):
        return print_code2_with_varlist(c, varlist)

    if eq.name == "f_sqrt":
        return f"{rec(eq.children[0])}.fx('sqrt')"
    if eq.name == "f_not":
        return f"~{rec(eq.children[0])}"
    binary = {
        "f_==": "==", "f_!=": "!=", "f_>": ">", "f_>=": ">=",
        "f_wor": "or", "f_pow": "**", "f_wand": "and",
        "f_mul": "*", "f_add": "+",
    }
    if eq.name in binary:
        op = f" {binary[eq.name]} "
        return "(" + op.join(rec(c) for c in eq.children) + ")"
    if eq.name == "f_condition":
        return print_condition(eq, rec)
    if not eq.children:
        return eq.name
    return f"TreeNode('{eq.name}',[" + ", ".join(rec(c) for c in eq.children) + "])"


def print_code(eq):
    return print_code_h(de_w_addmul(eq))


# --- SPECIAL PATTERN MATCHERS ---

def _split_const(children, resolved_ignore):
    const_t, non_t = [], []
    for ch in children:
        (non_t if set(vlist(ch)) & resolved_ignore else const_t).append(ch)
    return const_t, non_t


def _op(op_name, items):
    return items[0] if len(items) == 1 else operation(op_name, items)


def _is_zero(node):
    return node is not None and (getattr(node, "name", None) == "d_0" or node == 0)


def special_pattern_poly(eq, f, binding):
    n_coeffs = len(f.children) - 1
    if n_coeffs < 1:
        return False
    var_name = f.children[0].name

    if var_name in binding:
        bound = binding[var_name]
        if getattr(bound, "children", None) or not str(getattr(bound, "name", "")).startswith("v_"):
            return False
        candidates = [bound.name]
    else:
        candidates = vlist(eq)

    eq_plain = de_w_addmul(eq)
    for item in candidates:
        out = extract_polynomial_coefficients(eq_plain, item, n_coeffs - 1)
        if out is None or len(out) != n_coeffs or _is_zero(out[-1]):
            continue
        out = out[::-1]
        local_binding = binding.copy()
        consistent = True
        for c, val in zip(f.children[1:], out):
            if c.name in binding and binding[c.name] != val:
                consistent = False
                break
            local_binding[c.name] = val
        if not consistent:
            continue
        local_binding[var_name] = TreeNode(item)
        binding.update(local_binding)
        return True
    return False


def special_pattern(eq, f, binding, const_1_vars, resolved_ignore):
    if eq is None or f is None:
        return False
    if f.name == "f_poly":
        return special_pattern_poly(eq, f, binding)

    op_name = _PATTERN_OPS.get(f.name)
    if (op_name is None or len(f.children) != 2
            or eq.name != op_name or len(eq.children) < 2):
        return False

    c0, c1 = f.children[0].name, f.children[1].name
    kids = eq.children

    if (c0 in const_1_vars) == (c1 in const_1_vars):
        binding[c0] = kids[0]
        binding[c1] = _op(op_name, kids[1:])
        return True

    const_name, other_name = (c0, c1) if c0 in const_1_vars else (c1, c0)
    const_t, non_t = _split_const(kids, resolved_ignore)
    if not const_t:
        return False
    if not non_t:
        binding[const_name] = const_t[0]
        binding[other_name] = _op(op_name, const_t[1:])
    else:
        binding[const_name] = _op(op_name, const_t)
        binding[other_name] = _op(op_name, non_t)
    return True


def special_pattern_ordered(eq, f, binding, const_1_vars, resolved_ignore):
    if eq is None or f is None:
        return False
    if f.name == "f_poly":
        return special_pattern_poly(eq, f, binding)

    op_name = _ORDERED_PATTERN_OPS.get(f.name)
    if (op_name is None or len(f.children) != 2
            or eq.name != op_name or len(eq.children) < 2):
        return False

    c0, c1 = f.children[0].name, f.children[1].name
    kids = eq.children
    if c1 in const_1_vars:
        binding[c0] = _op(op_name, kids[:-1])
        binding[c1] = kids[-1]
    else:
        binding[c0] = kids[0]
        binding[c1] = _op(op_name, kids[1:])
    return True


def special_pattern_router(fname, eq, f=None, binding=None, const_1_vars=None, resolved_ignore=None):
    if binding is None:
        binding = {}
    if const_1_vars is None:
        const_1_vars = set()
    if resolved_ignore is None:
        resolved_ignore = set()

    if fname == "f_poly":
        return special_pattern_poly(eq, f, binding) if f else False
    if fname in _ORDERED_PATTERN_OPS:
        return special_pattern_ordered(eq, f, binding, const_1_vars, resolved_ignore) if f else False
    if fname in _PATTERN_OPS:
        return special_pattern(eq, f, binding, const_1_vars, resolved_ignore) if f else False
    if fname in _SPECIAL_PATTERN:
        raise ValueError(
            f"special pattern {fname!r} is not registered in _PATTERN_OPS / _ORDERED_PATTERN_OPS"
        )
    return True


# --- TWO-STEP COMPILER ---

def _consumed(form_node):
    return len(form_node.children)


def _node_src(node):
    return f"TreeNode({node.name!r}, [{', '.join(_node_src(c) for c in node.children)}])"


def compile_permutation_matcher_two_step(
    tree_node,
    formula_out=None,
    ignore_list=None,
    const_1=None,
    positive=None,
    negative=None,
    forbidden_list=None,
):
    ignore_list = ignore_list or []
    const_1 = const_1 or []
    positive = positive or []
    negative = negative or []
    forbidden_list = forbidden_list or []

    ignore_set = {get_name(i) for i in ignore_list}
    const_1_set = {get_name(i) for i in const_1}

    varlist = {}
    specials = []
    late_eq = []
    struct_expr = {}

    def helper(expr, form_node):
        name = form_node.name

        if name in _SPECIAL_PATTERN:
            specials.append((expr, form_node))
            for c in form_node.children:
                if c.name in varlist:
                    late_eq.append(f"{varlist[c.name]} == _b[{c.name!r}]")
                else:
                    varlist[c.name] = f"_b[{c.name!r}]"
            return "True"

        if name.startswith("v_"):
            if name in varlist:
                if varlist[name].startswith("_b["):
                    late_eq.append(f"{varlist[name]} == {expr}")
                    struct_expr.setdefault(name, expr)
                    return "True"
                return f"{varlist[name]} == {expr}"
            varlist[name] = expr
            struct_expr[name] = expr
            return "True"

        n = _consumed(form_node)
        checks = [f"{expr}.name == {name!r}", f"len({expr}.children) == {n}"]
        for i, child in enumerate(form_node.children):
            sub = helper(f"{expr}.children[{i}]", child)
            if sub != "True":
                checks.append(sub)
        return "(" + " and ".join(checks) + ")"

    match = helper("eq", tree_node)

    special_bound = {c.name for _, f in specials for c in f.children}
    ignore_exprs = [e for k, e in varlist.items() if k in ignore_set]
    struct_ignore = [e for k, e in varlist.items() if k in ignore_set and k not in special_bound]

    conds = [match]

    for e in struct_ignore:
        conds.append(f"({e}.name.startswith('v_') and not {e}.children)")

    c1_src = "set([" + ", ".join(repr(k) for k in sorted(const_1_set)) + "])"
    ig_src = "set([" + ", ".join(f"{e}.name" for e in struct_ignore) + "])"
    for expr, fnode in specials:
        seed = {c.name: struct_expr[c.name] for c in fnode.children if c.name in struct_expr}
        if seed:
            items = ", ".join(f"{k!r}: {v}" for k, v in seed.items())
            conds.append(f"(_b.update({{{items}}}) or True)")
        conds.append(
            f"special_pattern_router({fnode.name!r}, {expr}, {_node_src(fnode)}, _b, {c1_src}, {ig_src})"
        )

    conds.extend(late_eq)

    for k, e in varlist.items():
        if k in ignore_set and k in special_bound:
            conds.append(f"({e}.name.startswith('v_') and not {e}.children)")

    ig_list = "[" + ", ".join(ignore_exprs) + "]"
    for k in sorted(const_1_set):
        if k in varlist:
            conds.append(f"all(not contain({varlist[k]}, item) for item in {ig_list})")

    for lhs, val in forbidden_list:
        if lhs.name in varlist:
            conds.append(f"{varlist[lhs.name]} != {print_code2_with_varlist(val, varlist)}")

    for p in positive:
        s = print_code2_with_varlist(p, varlist)
        conds.append(f"(frac({s}) is not None and frac({s}) >= 0)")
    for p in negative:
        s = print_code2_with_varlist(p, varlist)
        conds.append(f"(frac({s}) is not None and frac({s}) <= 0)")

    if formula_out is not None:
        ret = f"simplify({print_code2_with_varlist(formula_out, varlist)})"
    else:
        ret = "eq"

    return (
        "_b = {}\n"
        f"if {' and '.join(conds)}:\n"
        f"    return {ret}\n"
        "return None\n"
    )


def indent_block(code_str, spaces=4):
    return textwrap.indent(code_str, " " * spaces)


# --- CONTAINER MATCH BLOCKS ---

def _commutative_block(op, k, fn):
    plain = op[:-1]
    return (
        f"if eq.name == {op!r} and len(eq.children) >= {k}:\n"
        f"    for comb in itertools.combinations(range(len(eq.children)), {k}):\n"
        f"        res = {fn}(TreeNode({op!r}, [eq.children[i] for i in comb]))\n"
        f"        if res is not None:\n"
        f"            kids = [eq.children[i] for i in range(len(eq.children)) if i not in comb]\n"
        f"            if res.name in ({op!r}, {plain!r}):\n"
        f"                kids.extend(res.children)\n"
        f"            else:\n"
        f"                kids.append(res)\n"
        f"            node = kids[0] if len(kids) == 1 else TreeNode({op!r}, kids)\n"
        f"            return simplify(de_w_addmul(node))\n"
    )


def _ordered_block(op, k, fn):
    plain = op[:-1]
    return (
        f"if eq.name == {op!r} and len(eq.children) >= {k}:\n"
        f"    n_ch = len(eq.children)\n"
        f"    for start in range(n_ch - {k} + 1):\n"
        f"        res = {fn}(TreeNode({op!r}, eq.children[start:start + {k}]))\n"
        f"        if res is not None:\n"
        f"            ins = list(res.children) if res.name in ({op!r}, {plain!r}) else [res]\n"
        f"            kids = eq.children[:start] + ins + eq.children[start + {k}:]\n"
        f"            node = kids[0] if len(kids) == 1 else TreeNode({op!r}, kids)\n"
        f"            return simplify(de_w_addmul(node))\n"
    )


def formula_compiler(s):
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
    fn_defs, blocks = [], []

    for combination in itertools.product(*subs.values()):
        x, y, pos, neg, forb = a, b, positive, negative, forbidden_list
        for key, value in zip(keys, combination):
            if value is not None:
                x = replace(x, key, value)
                y = replace(y, key, value)
                pos = _replace_in(pos, key, value)
                neg = _replace_in(neg, key, value)
                forb = _replace_in(forb, key, value)

        valid_comb = True
        for expr_part, forb_val in _as_pairs(forb):
            se, sv = simplify(expr_part), simplify(forb_val)
            if se is None or sv is None or se == sv:
                valid_comb = False
                break
        if not valid_comb:
            continue

        simp_x, simp_y = simplify(x), simplify(y)
        if simp_x is None or simp_y is None:
            continue
        formula_w = en_w_addmul(simp_x)
        if formula_w is None:
            continue

        op = formula_w.name
        k = _consumed(formula_w)

        for perm_tree in generate_tree_permutations(formula_w):
            body = compile_permutation_matcher_two_step(
                tree_node=perm_tree,
                formula_out=simp_y,
                ignore_list=_as_exprs(ignore_list),
                const_1=_as_exprs(const_1),
                positive=_as_exprs(pos),
                negative=_as_exprs(neg),
                forbidden_list=_as_pairs(forb),
            )
            fn = f"_m{len(fn_defs)}"
            fn_defs.append(f"def {fn}(eq):\n" + indent_block(body, 4))

            if op in _COMMUTATIVE:
                blocks.append(_commutative_block(op, k, fn))
            elif op in _ORDERED_ASSOC:
                blocks.append(_ordered_block(op, k, fn))
            else:
                blocks.append(f"r = {fn}(eq)\nif r is not None:\n    return r\n")

    if not fn_defs:
        warnings.warn(f"rule produced no matchers (simplify returned None?): {s!r}")

    src = "\n\n".join(fn_defs) + "\n\n"
    src += "def transform(eq_orig):\n    eq = copy.deepcopy(eq_orig)\n"
    for blk in blocks:
        src += indent_block(blk, 4) + "\n"
    src += "    return eq_orig\n"

    env = {
        "tree_form": tree_form,
        "TreeNode": TreeNode,
        "contain": contain,
        "str_form": str_form,
        "copy": copy,
        "simplify": simplify,
        "frac": frac,
        "replace": replace,
        "operation": operation,
        "special_pattern_router": special_pattern_router,
        "special_pattern": special_pattern,
        "special_pattern_ordered": special_pattern_ordered,
        "special_pattern_poly": special_pattern_poly,
        "extract_polynomial_coefficients": extract_polynomial_coefficients,
        "de_w_addmul": de_w_addmul,
        "vlist": vlist,
        "itertools": itertools,
    }
    exec(src, env)

    def apply(x):
        w = en_w_addmul(x)
        out = env["transform"](w)
        if out is w:
            return x
        return None if out is None else de_w_addmul(out)

    apply.source = src
    return apply


formula_compiler_from_rule_string = formula_compiler


# --- RULE LISTS ---

def transform_dfs_changed(root, func, arg=None, key=None):
    if root is None:
        return None
    arg = () if arg is None else arg
    key = key or str_form
    stable = {}
    in_progress = set()
    values = []
    stack = [("visit", root, None)]

    def finish(sig, cur, out):
        stable[sig] = out
        stable[key(cur)] = out
        stable[key(out)] = out
        in_progress.discard(sig)
        values.append(out)

    while stack:
        kind, node, sig = stack.pop()
        if kind == "visit":
            sig = key(node)
            if sig in stable:
                values.append(stable[sig])
                continue
            if sig in in_progress:
                values.append(node)
                continue
            in_progress.add(sig)
            stack.append(("combine", node, sig))
            for child in reversed(node.children):
                stack.append(("visit", child, None))
        elif kind == "combine":
            n = len(node.children)
            kids = values[len(values) - n:]
            del values[len(values) - n:]
            if all(a is b for a, b in zip(kids, node.children)):
                cur = node
            else:
                cur = TreeNode(node.name, kids)
            res = func(cur, *arg)
            if res is None or res is cur or key(res) == key(cur):
                finish(sig, cur, cur)
            else:
                stack.append(("record", cur, sig))
                stack.append(("visit", res, None))
        else:
            finish(sig, node, values.pop())
    return values[-1]


def formula_list_compiler(s, mode="fixpoint"):
    rules = []
    for line in _split_rules(s):
        line = line.strip()
        if line.startswith("@"):
            line = line[1:].strip()
            rules.append(lambda x, line=line: formula_applier(x, line))
        else:
            rules.append(formula_compiler(line))

    def node_fn(node):
        for rule in rules:
            r = rule(node)
            if r is not None:
                node = r
        return node

    if mode == "dowhile":
        def apply(eq):
            if eq is None:
                return None
            return dowhile(eq, lambda x: transform_dfs(x, node_fn))
    elif mode == "fixpoint":
        def apply(eq):
            return None if eq is None else transform_dfs_changed(eq, node_fn)
    else:
        raise ValueError("mode must be 'fixpoint' or 'dowhile'")

    apply.rules = rules
    apply.node_fn = node_fn
    apply.sources = [getattr(r, "source", None) for r in rules]
    return apply
