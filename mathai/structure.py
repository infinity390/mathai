import itertools
from .diff import diff, diff2
from .simplify import simplify
from .base import *
def structure(equation, formula, formula_out=None, only_const=[], wrt=None):
    varlist = {}
    def helper(equation, formula):
        nonlocal varlist
        if formula.name[:2] == "v_" and int(formula.name[2:])< 0:
            if formula.name in varlist.keys():
                return varlist[formula.name] == equation
            else:
                varlist[formula.name] = equation
                return True
        if equation.name != formula.name:
            return False
        if len(equation.children) != len(formula.children):
            return False
        return all(helper(equation.children[i], formula.children[i]) for i in range(len(equation.children)))
    def lst(formula):
        out = set()
        formula = conversion(formula)
        def helper(node):
            if not node.children:
                return [node]
            child_groups = [tuple(node.children)]
            if node.name in ["f_addw", "f_mulw"]:
                child_groups = list(itertools.permutations(node.children))
            results = []
            for children in child_groups:
                child_perms = [helper(child) for child in children]
                for combo in itertools.product(*child_perms):
                    results.append(TreeNode(node.name, list(combo)))
            return results
        def conversionrev(node):
            if node.name == "f_addw":
                node.name = "f_add"
            elif node.name == "f_mulw":
                node.name = "f_mul"
            return TreeNode(node.name, [conversionrev(child) for child in node.children])
        for tree in helper(formula):
            out.add(tree)
        return list(out)
    def conversion(node):
        if node.name == "f_add":
            node.name = "f_addw"
        elif node.name == "f_mul":
            node.name = "f_mulw"
        return TreeNode(node.name, [conversion(child) for child in node.children])
    def conversionrev(node):
        if node.name == "f_addw":
            node.name = "f_add"
        elif node.name == "f_mulw":
            node.name = "f_mul"
        return TreeNode(node.name, [conversionrev(child) for child in node.children])
    equation = conversion(equation)
    if formula_out is not None:
        formula_out = conversion(formula_out)
    for item in lst(formula):
        varlist = {}
        if helper(equation, item):
            if not all(tree_form(key) not in only_const or\
                       (not contain(diff(conversionrev(varlist[key]), wrt), tree_form(wrt)) and contain(varlist[key], tree_form(wrt))) for key in varlist.keys()):
                continue
            if formula_out is None:
                return varlist
            for key in varlist.keys():
                formula_out = replace(formula_out, tree_form(key), varlist[key])
            return simplify(conversionrev(formula_out))
    return None
def transform_formula(equation, wrt, formula_list, var, expr):
    var2 = str(tree_form(wrt))
    if var != var2:
        formula_list =  [[replace(y, tree_form("v_0"), tree_form(wrt)) for y in x] for x in formula_list]
        expr = [replace(item, tree_form("v_0"), tree_form(wrt)) for item in expr]
    for item in formula_list:
        out = structure(equation.copy_tree(), copy.deepcopy(item[0]), copy.deepcopy(item[1]), expr, wrt)
        if out is not None:
            return simplify(diff2(out))
    return None
