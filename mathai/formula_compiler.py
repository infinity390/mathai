import copy
import itertools
import textwrap
from .base import *
from .simplify import simplify
from .parser import parse
from .formula_applier import (
    extract_polynomial_coefficients, convert_string, _as_pairs, _replace_in,
    _as_exprs, get_name, en_w_addmul, formula_applier
)

# --- CONSTANTS & CONFIGURATION ---

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
_SPECIAL_PATTERN = frozenset(("f_poly", "f_sum", "f_wsum", "f_product", "f_hprod", "f_mprod"))
_PATTERN_OPS = {"f_sum": "f_addw", "f_product": "f_mulw",
                "f_hprod": "f_hadamardw", "f_wsum": "f_waddw"}
_ORDERED_PATTERN_OPS = {"f_mprod": "f_wmulw"}
_AGG_NAMES = frozenset((
    "f_addw", "f_add", "f_mulw", "f_mul", "f_hadamardw", "f_hadamard",
    "f_product", "f_sum", "f_hprod", "f_mprod", "f_poly", "f_wmulw", "f_wmul",
))
_EXTRACT_NAMES = frozenset((
    "f_add", "f_wadd", "f_waddw", "f_wmul", "f_wmulw",
    "f_mul", "f_product", "f_sum", "f_hprod", "f_mprod", "f_poly", "f_wsum", "f_wsumw"
))
_DE_W_NAMES = frozenset(("f_addw", "f_mulw", "f_waddw", "f_hadamardw", "f_wmulw", "f_wsumw"))


# --- TREE NODE CLASS ---
# FIX 1: `from .base import *` may already provide TreeNode (print_code2 emits
# `a * b`, `~a`, `.fx(...)`, which only work on that class).  Redefining it here
# shadowed it, giving two incompatible TreeNode classes with no __eq__/__hash__.
# Keep base's class if it exists; otherwise use this complete fallback.

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

        # structural equality (generated code relies on `==` / `!=`)
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

        # operators emitted by print_code2_with_varlist
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
                # FIX 2: dedupe on a structural signature (identity hashing never matched)
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
    # FIX 3: take the printer as a parameter (print_code2 used to fall into
    # print_code_h) and don't IndexError when there is no else-branch.
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
        # NOTE: `any(A B)` is not valid Python; left as-is because the intended
        # translation isn't clear from this file.
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
    # FIX 4: the unreachable s_true / s_false branches that followed this
    # (shadowed by this check) were removed: in a tree-building context they
    # must stay tree nodes, which is what this line produces.
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
    # FIX 5: dropped the blind str.replace loop (de_w_addmul already did the
    # renaming; the replace could corrupt longer identifiers).
    return print_code_h(de_w_addmul(eq))


# --- SPECIAL PATTERN MATCHERS ---

def _split_const(children, resolved_ignore):
    """Split into terms free of the 'variables of interest' and terms that use them."""
    const_t, non_t = [], []
    for ch in children:
        (non_t if set(vlist(ch)) & resolved_ignore else const_t).append(ch)
    return const_t, non_t


def _op(op_name, items):
    return items[0] if len(items) == 1 else operation(op_name, items)


def _is_zero(node):
    # TreeNode == 0 is False; zero is represented as the node "d_0"
    return node is not None and (getattr(node, "name", None) == "d_0" or node == 0)


def special_pattern_poly(eq, f, binding):
    # FIX 18: poly(x, a, b) = a*x + b has 2 coefficients -> degree 1.  Ask the
    # extractor for exactly that degree (it returns degree+1 ascending
    # coefficients, or None if eq has a higher degree) and require a nonzero
    # leading coefficient.  The old code asked for degree 2, then stripped leading
    # zeros with `out[0] == 0`, which is False for TreeNodes.
    n_coeffs = len(f.children) - 1
    if n_coeffs < 1:
        return False
    eq_plain = de_w_addmul(eq)
    for item in vlist(eq):
        out = extract_polynomial_coefficients(eq_plain, item, n_coeffs - 1)
        if out is None or len(out) != n_coeffs or _is_zero(out[-1]):
            continue
        out = out[::-1]                      # highest degree first
        local_binding = binding.copy()
        for i in range(1, len(f.children)):
            local_binding[f.children[i].name] = out[i - 1]
        local_binding[f.children[0].name] = TreeNode(item)
        binding.update(local_binding)
        return True
    return False


def special_pattern(eq, f, binding, const_1_vars, resolved_ignore):
    # FIX 6: the old code had two near-identical branches, accepted patterns with
    # >2 children but only bound two of them, and used a strict-subset test.
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
        binding[c0] = const_t[0]
        binding[c1] = _op(op_name, const_t[1:])
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
    return True


# --- TWO-STEP COMPILER ---

def _consumed(form_node):
    """How many children of the matched node this pattern node uses
    (an ordered-assoc child consumes two)."""
    return sum(2 if c.name in _ORDERED_ASSOC else 1 for c in form_node.children)


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
    """Returns the *body* of a function of `eq`: it returns the rewritten tree
    on a match and None otherwise.  Conditions are built as plain Python
    expression strings joined with short-circuiting `and`."""
    ignore_list = ignore_list or []
    const_1 = const_1 or []
    positive = positive or []
    negative = negative or []
    forbidden_list = forbidden_list or []

    ignore_set = {get_name(i) for i in ignore_list}
    # FIX 7: const_1 holds TreeNodes; the old `key in const_1` compared a str to
    # TreeNodes and was never true.
    const_1_set = {get_name(i) for i in const_1}

    varlist = {}      # pattern var name -> python expression that yields the bound subtree
    specials = []     # (expr, pattern_node), checked after the structure matches
    late_eq = []      # equalities involving special-bound vars; only valid after the router ran

    def helper(expr, form_node):
        name = form_node.name

        if name in _SPECIAL_PATTERN:
            # FIX 8: special patterns were emitted as router calls with no pattern,
            # no binding dict -> always False and never bound anything.
            specials.append((expr, form_node))
            for c in form_node.children:
                if c.name in varlist:
                    # FIX 16: var already bound structurally -> the router's binding must agree
                    late_eq.append(f"{varlist[c.name]} == _b[{c.name!r}]")
                else:
                    varlist[c.name] = f"_b[{c.name!r}]"
            return "True"

        if name.startswith("v_"):
            if name in varlist:
                if varlist[name].startswith("_b["):
                    # FIX 17: `_b[...]` doesn't exist until the router has run, so this
                    # comparison must come after it (it used to be inline -> KeyError)
                    late_eq.append(f"{varlist[name]} == {expr}")
                    return "True"
                return f"{varlist[name]} == {expr}"
            varlist[name] = expr
            return "True"

        n = _consumed(form_node)
        access = [f"{expr}.children[{i}]" for i in range(n)]
        child_exprs, pos = [], 0
        for child in form_node.children:
            if child.name in _ORDERED_ASSOC:
                # FIX 9: wrap with the *child's* name (was the parent's name)
                child_exprs.append(f"TreeNode({child.name!r}, [{access[pos]}, {access[pos + 1]}])")
                pos += 2
            else:
                child_exprs.append(access[pos])
                pos += 1

        # FIX 10: length check uses the number of children actually consumed
        checks = [f"{expr}.name == {name!r}", f"len({expr}.children) == {n}"]
        for child, ce in zip(form_node.children, child_exprs):
            sub = helper(ce, child)
            if sub != "True":
                checks.append(sub)
        return "(" + " and ".join(checks) + ")"

    # FIX 11: the old `form_node.count` permutation hack enumerated n! orderings per
    # node just to pick the last one.  Every pattern ordering is already produced by
    # generate_tree_permutations, so matching children positionally is enough.
    match = helper("eq", tree_node)

    special_bound = {c.name for _, f in specials for c in f.children}
    ignore_exprs = [e for k, e in varlist.items() if k in ignore_set]
    struct_ignore = [e for k, e in varlist.items() if k in ignore_set and k not in special_bound]

    conds = [match]

    # ignore-vars must be bare variables
    for e in struct_ignore:
        conds.append(f"({e}.name.startswith('v_') and not {e}.children)")

    # FIX 12: `ignore` used to collect *every* v_ variable (and mid-traversal); it is
    # now the ignore_list variables only, and special patterns get real variable names.
    c1_src = "set([" + ", ".join(repr(k) for k in sorted(const_1_set)) + "])"
    ig_src = "set([" + ", ".join(f"{e}.name" for e in struct_ignore) + "])"
    for expr, fnode in specials:
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

    # FIX 13: forbidden values were interpolated with repr() -> `x != 'd_0'`
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


# --- CONTAINER (sub-multiset / sub-sequence) MATCH BLOCKS ---

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
    """Compile a rule string into a transformation function."""
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
            # FIX 14: every matcher is its own top-level function with a parameter
            # named `eq` (the generated code refers to `eq`, but the old wrapper
            # called its parameter `sub_eq`), and indentation is done with
            # textwrap instead of multi-line f-string interpolation.
            fn = f"_m{len(fn_defs)}"
            fn_defs.append(f"def {fn}(eq):\n" + indent_block(body, 4))

            if op in _COMMUTATIVE:
                blocks.append(_commutative_block(op, k, fn))
            elif op in _ORDERED_ASSOC:
                blocks.append(_ordered_block(op, k, fn))
            else:
                blocks.append(f"r = {fn}(eq)\nif r is not None:\n    return r\n")

    src = "\n\n".join(fn_defs) + "\n\n"
    src += "def transform(eq_orig):\n    eq = copy.deepcopy(eq_orig)\n"
    for blk in blocks:
        # FIX 15: blocks used to be appended at column 0, i.e. outside the def
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
        if out is w:              # no rule matched: hand back the very same object
            return x
        return None if out is None else de_w_addmul(out)   # simplify() can return None

    apply.source = src   # handy for debugging
    return apply


# --- RULE LISTS ---

try:
    from .formula_applier import _split_rules
except ImportError:
    def _split_rules(s):
        return tuple(line for line in s.strip().split("\n") if line.strip())


def transform_dfs_changed(root, func, arg=None, key=None):
    """Iterative post-order transform that
      * only rebuilds a node if one of its children actually changed,
      * re-normalises a node's replacement when func changes it (so no outer
        dowhile is needed), and
      * never processes the same subtree twice: every subtree that has reached a
        fixed point is cached by structural key and reused.
    `func(node, *arg)` may return None or the same node to mean 'unchanged'."""
    if root is None:
        return None
    arg = () if arg is None else arg
    key = key or str_form
    stable = {}            # key(subtree) -> fully normalised subtree
    in_progress = set()    # keys being normalised (guards against rewrite cycles)
    values = []            # results of finished 'visit's, in visiting order
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
            if sig in in_progress:        # A -> B -> A: stop, keep as is
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
                cur = node                       # nothing below changed: reuse
            else:
                cur = TreeNode(node.name, kids)
            res = func(cur, *arg)
            if res is None or res is cur or key(res) == key(cur):
                finish(sig, cur, cur)            # unchanged
            else:
                stack.append(("record", cur, sig))
                stack.append(("visit", res, None))   # changed: normalise the new subtree
        else:  # record
            finish(sig, node, values.pop())
    return values[-1]
 
def formula_list_compiler(s, mode="fixpoint"):
    """Compile a multi-line rule string (one rule per line) into one function.
    mode="fixpoint": transform_dfs_changed (skips unchanged / already-stable nodes)
    mode="dowhile" : whole-tree dowhile(transform_dfs(...)) loop
    A line starting with "@" is always handled by formula_applier (the "@" is stripped);
    other lines go there only if _needs_applier() says so."""
 
    rules = []
    for line in _split_rules(s):
        line = line.strip()
        forced = line.startswith("@")          # "@rule ..." = always use formula_applier
        if forced:
            line = line[1:].strip()
        if forced:
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
