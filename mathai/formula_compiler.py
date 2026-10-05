import copy
import more_itertools
import itertools
from .base import *
from .parser import parse
from fractions import Fraction
from .simplify import simplify
import marshal
import os


def en_w_addmul_h(eq):
    """Wraps operators into 'w' variants to prevent implicit auto-sorting by TreeNode."""
    if eq.name == "f_add":
        return TreeNode("f_addw", eq.children)
    if eq.name == "f_mul":
        return TreeNode("f_mulw", eq.children)
    if eq.name == "f_hadamard":
        return TreeNode("f_hadamardw", eq.children)
    if eq.name == "f_wadd":
        return TreeNode("f_waddw", eq.children)
    return eq

def en_w_addmul(eq):
    return transform_dfs(eq, en_w_addmul_h)

def simplify0_h(eq):
    # Updated to process 'w' variants and bypass operation() to avoid external auto-sort triggers
    if eq.name in ["f_add", "f_addw"]:
        lst = [item for item in eq.children if item.name != "d_0"]
        if len(lst) == 1: return lst[0]
        if len(lst) == 0: return tree_form("d_0")
        return TreeNode(eq.name, lst)
        
    if eq.name in ["f_mul", "f_mulw"]:
        if any(item.name == "d_0" for item in eq.children):
            return tree_form("d_0")
        lst = [item for item in eq.children if item.name != "d_1"]
        if len(lst) == 1: return lst[0]
        if len(lst) == 0: return tree_form("d_1")
        return TreeNode(eq.name, lst)
        
    return eq

def simplify0(eq):
    return dowhile(eq, lambda x: transform_dfs(x, simplify0_h))

def get_name(item):
    if hasattr(item, "name"):
        return item.name
    return str(item)

def make_treenode_string(name, children):
    return f"TreeNode('{name}',[{','.join(children)}])"

def structure(
    formula,
    formula_out,
    ignore_list=None,
    var_name=None,
    const_1=None,
    const_var=None,
    forbidden_value=None,
    positive=None,
    negative=None,
    arity=6,
):
    # PRE-PROCESSING: Wrap f_add/f_mul into f_addw/f_mulw to prevent auto-sorting during AST traversal
    formula = en_w_addmul(copy.deepcopy(formula))
    formula_out = en_w_addmul(copy.deepcopy(formula_out))

    if ignore_list is None: ignore_list = []
    if not isinstance(ignore_list, list): ignore_list = [ignore_list]

    if var_name is None: var_name = []
    if not isinstance(var_name, list): var_name = [var_name]

    if const_1 is None: const_1 = []
    if not isinstance(const_1, list): const_1 = [const_1]

    if const_var is None: const_var = []
    if not isinstance(const_var, list): const_var = [const_var]

    if forbidden_value is None: forbidden_value = []
    if len(forbidden_value) > 0 and not isinstance(forbidden_value[0], (list, tuple)):
        forbidden_value = [forbidden_value]

    if positive is None: positive = []
    if not isinstance(positive, list): positive = [positive]

    if negative is None: negative = []
    if not isinstance(negative, list): negative = [negative]

    positive = [en_w_addmul(copy.deepcopy(p)) if hasattr(p, 'name') else p for p in positive]
    negative = [en_w_addmul(copy.deepcopy(n)) if hasattr(n, 'name') else n for n in negative]

    var_name = [get_name(item) for item in var_name]
    const_var = [get_name(item) for item in const_var]
    const_1 = [get_name(item) for item in const_1]
    ignore_list = [get_name(item) for item in ignore_list]
    positive_names = [get_name(item) for item in positive]
    negative_names = [get_name(item) for item in negative]

    def helper_gen(eq_path, formula, associativity, varlist, ignore, ignore_list):
        if formula.name.startswith("v_") and formula.name in ignore_list:
            cond_1 = TreeNode("f_condition", [])
            cond_2 = TreeNode(
                "f_if",
                [
                    TreeNode(f"not {eq_path}.name.startswith('v_')"),
                    TreeNode("False"),
                ],
            )
            if formula.name in varlist:
                cond_3 = TreeNode(f"{varlist[formula.name]} == {eq_path}")
                cond_1.children += [cond_2, cond_3.fx("else")]
                yield cond_1, varlist, ignore
            else:
                new_varlist = varlist.copy()
                new_varlist[formula.name] = eq_path
                new_ignore = ignore.copy()
                if eq_path not in new_ignore:
                    new_ignore.append(eq_path)
                cond_3 = TreeNode("True")
                cond_1.children += [cond_2, cond_3.fx("else")]
                yield cond_1, new_varlist, new_ignore
            return
            
        elif formula.name.startswith("v_"):
            if formula.name in varlist:
                yield TreeNode(f"{varlist[formula.name]} == {eq_path}"), varlist, ignore
            else:
                new_varlist = varlist.copy()
                new_varlist[formula.name] = eq_path
                yield TreeNode("True"), new_varlist, ignore
            return
            
        else:
            s = sum(associativity.get(key.name, 1) for key in formula.children)
            cond_type_len = TreeNode("f_condition", [])
            ls = [
                TreeNode(f"{eq_path}.name != '{formula.name}'"),
                TreeNode(f"len({eq_path}.children) != {s}"),
            ]
            cond_2 = TreeNode("f_if", [operation("f_wor", ls), TreeNode("False")])
            eq_children_paths = [f"{eq_path}.children[{i}]" for i in range(s)]

            # Permutation support natively extended to 'w' variants
            if formula.name in ["f_add", "f_mul", "f_addw", "f_mulw"]:
                target_lengths = [associativity.get(k.name, 1) for k in formula.children]
                for p in itertools.permutations(eq_children_paths):
                    groups = list(more_itertools.split_into(p, target_lengths))
                    new_children_paths = [
                        item[0] if len(item) == 1 else make_treenode_string(formula.name, item)
                        for item in groups
                    ]
                    yield from helper_gen_children(
                        new_children_paths, formula.children, associativity, varlist, ignore, ignore_list, cond_type_len, cond_2
                    )
            else:
                new_children_paths = []
                curr_paths = list(eq_children_paths)
                for key in formula.children:
                    n = associativity.get(key.name, 1)
                    if n == 1:
                        new_children_paths.append(curr_paths.pop(0))
                    else:
                        new_children_paths.append(make_treenode_string(formula.name, curr_paths[:n]))
                        curr_paths = curr_paths[n:]
                        
                yield from helper_gen_children(
                    new_children_paths, formula.children, associativity, varlist, ignore, ignore_list, cond_type_len, cond_2
                )

    def helper_gen_children(paths, pattern_children, associativity, varlist, ignore, ignore_list, cond_type_len, cond_2):
        def thread_children(idx, current_varlist, current_ignore):
            if idx == len(pattern_children):
                yield [], current_varlist, current_ignore
                return
            for child_cond, next_varlist, next_ignore in helper_gen(
                paths[idx], pattern_children[idx], associativity, current_varlist, current_ignore, ignore_list
            ):
                for rest_conds, final_varlist, final_ignore in thread_children(idx + 1, next_varlist, next_ignore):
                    yield [child_cond] + rest_conds, final_varlist, final_ignore

        for child_conds, final_varlist, final_ignore in thread_children(0, varlist, ignore):
            if len(child_conds) == 0:
                cond_3 = TreeNode("True")
            elif len(child_conds) == 1:
                cond_3 = child_conds[0]
            else:
                cond_3 = TreeNode("f_wand", child_conds)
                
            final_cond = copy.deepcopy(cond_type_len)
            final_cond.children += [copy.deepcopy(cond_2), cond_3.fx("else")]
            yield final_cond, final_varlist, final_ignore

    def gen_ac(eq, ignore_list, arity):
        lst = []
        def merge_unique(dicts):
            merged = {}
            for d in dicts:
                for key, value in d.items():
                    if key in merged and merged[key] != value:
                        return None
                    merged[key] = value
            return merged

        def make_eq(f, arity):
            # Whitelisted 'w' variants
            valid_ops = {"f_add", "f_mul", "f_hadamard", "f_wadd", "f_wmul", "f_addw", "f_mulw"}
            if f.name in valid_ops:
                lst2 = []
                label = [c.name for c in f.children if c.name.startswith("v_")]
                lst3 = [[1] if c.name in ignore_list else list(range(1, arity + 1)) 
                        for c in f.children if c.name.startswith("v_")]
                
                for item in itertools.product(*lst3):
                    dic = {label[i]: item2 for i, item2 in enumerate(item)}
                    lst2.append(dic)
                
                if lst2:
                    lst.append(lst2)
            for child in f.children:
                make_eq(child, arity)

        make_eq(eq, arity)
        if not lst:
            return [{}]
        
        output = []
        for item in itertools.product(*lst):
            out = merge_unique(item)
            if out is not None:
                output.append(out)
        return output

    formula_lst = []
    ll = []
    sorted_vars = list(sorted(set(get_name(v) for v in vlist(formula))))

    fv = {}
    for key, item in forbidden_value:
        k_str = get_name(key)
        if k_str not in fv:
            fv[k_str] = []
        fv[k_str].append(item)

    for item in sorted_vars:
        if item in ignore_list:
            ll.append([-100])
            continue
        output = [0, 1] if item in var_name else []
        output = [
            x for x in output
            if (item not in fv or x not in fv[item]) and (item not in negative_names or x != 1)
        ]
        if output:
            ll.append([-100] + list(set(output)))
        else:
            ll.append([-100])

    for item in itertools.product(*ll):
        eq_try = copy.deepcopy(formula)
        eq_var = {}
        for index, item2 in enumerate(item):
            if item2 == -100:
                continue
            var_key = sorted_vars[index]
            eq_var[var_key] = f"d_{item2}"
            eq_try = simplify0(replace(eq_try, tree_form(var_key), tree_form(f"d_{item2}")))
        formula_lst.append((eq_try, eq_var))

    final_output = ""
    for item, upd in formula_lst:
        hh = gen_ac(item, ignore_list, arity)
        for associativity in hh:
            varlist_base = {k: v for k, v in upd.items()}
            
            for out, varlist, ignore in helper_gen("eq", item, associativity, varlist_base, [], ignore_list):
                d = []
                for key, item2_code in varlist.items():
                    if key in const_1:
                        ignore_str = ", ".join(ignore)
                        if not item2_code.startswith("d_"):
                            d.append(TreeNode(f"all(not contain({item2_code}, item) for item in [{ignore_str}])"))

                for key, item2_code in varlist.items():
                    forbidden_vals = fv.get(key, [])
                    for val in forbidden_vals:
                        if item2_code.startswith("d_"):
                            d.append(TreeNode(f"tree_form('{item2_code}') != {val}"))
                        elif item2_code[:2] in ["f_", "v_", "s_"]:
                            pass
                        else:
                            d.append(TreeNode(f"{item2_code} != {val}"))

                for item2 in positive:
                    local_pos = copy.deepcopy(item2)
                    if isinstance(local_pos, TreeNode):
                        for key, item3_code in varlist.items():
                            local_pos = replace(local_pos, tree_form(key), TreeNode(item3_code, []))
                        s = print_code2(local_pos)
                        d.append(TreeNode(f"frac({s}) is not None and frac({s})>=0"))

                for item2 in negative:
                    local_neg = copy.deepcopy(item2)
                    if isinstance(local_neg, TreeNode):
                        for key, item3_code in varlist.items():
                            local_neg = replace(local_neg, tree_form(key), TreeNode(item3_code, []))
                        s = print_code2(local_neg)
                        d.append(TreeNode(f"frac({s}) is not None and frac({s})<=0"))

                if len(d) == 0:
                    pass
                elif len(d) == 1:
                    out = TreeNode("f_condition", [TreeNode("f_if", [out, d[0]]), tree_form("s_false").fx("else")])
                else:
                    out = TreeNode("f_condition", [TreeNode("f_if", [out, TreeNode("f_wand", d)]), tree_form("s_false").fx("else")])
                
                local_formula_out = copy.deepcopy(formula_out)
                for key, item2_code in varlist.items():
                    local_formula_out = replace(local_formula_out, tree_form(key), TreeNode(item2_code, []))

                # Generating the output python string
                s = "\tif " + print_code(out) + ":\n"
                t = "\t\treturn " + print_code2(local_formula_out) + "\n"
                final_output += s + t

    return final_output

def print_condition(eq):
    assert eq.name == "f_condition"
    def emit(i):
        branch = eq.children[i]
        if branch.name == "f_else": return print_code_h(branch.children[0])
        cond = print_code_h(branch.children[0])
        value = print_code_h(branch.children[1])
        rest = emit(i + 1)
        return f"({value} if {cond} else {rest})"
    return emit(0)

def print_code_h(eq):
    if eq.name == "s_true": return "True"
    if eq.name == "s_false": return "False"
    if eq.name == "f_not": return f"(not {print_code_h(eq.children[0])})"
    
    binary = {"f_==": "==", "f_!=": "!=", "f_wor": "or", "f_wand": "and", "f_>": ">", "f_>=": ">="}
    if eq.name in binary:
        return "(" + f" {binary[eq.name]} ".join(print_code_h(c) for c in eq.children) + ")"
        
    if eq.name == "f_index": return f"{print_code_h(eq.children[0])}[{eq.children[1]}]"
    if eq.name == "f_any": return f"any({print_code_h(eq.children[0])} {print_code_h(eq.children[1])})"
    if eq.name == "f_list": return "[" + ", ".join(print_code_h(c) for c in eq.children) + "]"
    if eq.name == "f_condition": return print_condition(eq)
    if not eq.children: return eq.name
    
    return f"{eq.name}(" + ", ".join(print_code_h(c) for c in eq.children) + ")"

def print_code2(eq):
    if eq.name.startswith("d_") or eq.name.startswith("v_") or eq.name.startswith("s_"):
        return f"tree_form('{eq.name}')"
        
    if eq.name == "s_true": return "True"
    if eq.name == "s_false": return "False"
    
    if eq.name == "f_sqrt": return f"{print_code2(eq.children[0])}.fx('sqrt')"
    if eq.name == "f_not": return f"~{print_code2(eq.children[0])}"
    
    # Extended to seamlessly unwrap returned 'w' operations via '+' and '*' overload translations 
    binary = {
        "f_==": "==", "f_!=": "!=", "f_>": ">", "f_>=": ">=", "f_wor": "or", 
        "f_pow": "**", "f_wand": "and", "f_mul": "*", "f_add": "+", 
        "f_addw": "+", "f_mulw": "*"
    }
    
    if eq.name in binary:
        return "(" + f" {binary[eq.name]} ".join(print_code2(c) for c in eq.children) + ")"
        
    if eq.name == "f_condition": return print_condition(eq)
    if not eq.children: return eq.name
    
    # Safely strip W fallback for non-overloaded string prints
    name = eq.name
    if name in ["f_addw", "f_mulw", "f_waddw", "f_hadamardw"]:
        name = name[:-1]
        
    return f"TreeNode('{name}',[" + ", ".join(print_code2(c) for c in eq.children) + "])"

def de_w_addmul_h(eq):
    if eq.name in ["f_addw", "f_mulw", "f_waddw", "f_hadamardw"]:
        return TreeNode(eq.name[:-1], eq.children)
    return eq

def de_w_addmul(eq):
    return transform_dfs(eq, de_w_addmul_h)

def print_code(eq):
    # This automatically unwraps the generated conditional match strings (eq.name != 'f_addw' -> eq.name != 'f_add')
    out = print_code_h(de_w_addmul(eq))
    for item in ["f_addw", "f_mulw", "f_waddw", "f_hadamardw"]:
        out = out.replace(item, item[:-1])
    return out

def formula_compiler(lst_formula, save_to_file=None):
    s = "def transform(eq_orig):\n\teq = copy.deepcopy(eq_orig)\n"
    s += lst_formula
    s += "\treturn de_w_addmul(eq_orig)"

    env = {
        "tree_form": tree_form,
        "TreeNode": TreeNode,
        "contain": contain,
        "str_form": str_form,
        "copy": copy,
        "simplify": simplify,
        "frac": frac,
        "de_w_addmul": de_w_addmul,
    }

    if save_to_file is not None:
        code = compile(s, "<string>", "exec")
        folder = os.path.join(os.path.dirname(__file__), "formula")
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, f"{save_to_file}.marshal"), "wb") as f:
            marshal.dump(code, f)
        return None

    exec(s, env)
    return env["transform"]

def formula_list_compiler(lst, save_to_file=None):
    dic = ""
    for index, item in enumerate(lst):
        print(f"{index+1}/{len(lst)}")
        dic += structure(*item)
    return formula_compiler(dic, save_to_file)
