import copy
from lark import Lark, Tree
from .base import *
import re
grammar = """
?start: expr

?expr: logic_equiv

?logic_equiv: logic_imply
            | logic_equiv "<->" logic_imply  -> equiv

?logic_imply: logic_or
            | logic_or "->" logic_imply      -> imply

?logic_or: logic_and
         | logic_or "|" logic_and            -> or
         | logic_or "||" logic_and           -> or

?logic_and: logic_not
          | logic_and "&" logic_not          -> and
          | logic_and "&&" logic_not         -> and

?logic_not: comparison
          | "!" logic_not                    -> not
          | "~" logic_not                    -> not

?comparison: arithmetic
           | comparison "=" arithmetic  -> eq
           | comparison "<" arithmetic  -> lt
           | comparison ">" arithmetic  -> gt
           | comparison "<=" arithmetic -> le
           | comparison ">=" arithmetic -> ge

?arithmetic: arithmetic "+" term   -> add
           | arithmetic "-" term   -> sub
           | term

?term: term "*" power  -> mul
     | term "@" power  -> wmul
     | term "/" power  -> div
     | term "." power  -> dot
     | power

?power: power "^" factor   -> pow
      | power "**" factor  -> pow
      | factor

?factor: "-" factor        -> neg
       | "+" factor        -> pass_through
       | atom

?atom: NUMBER               -> number
     | VARIABLE             -> variable
     | FUNC_NAME "(" [expr ("," expr)*] ")" -> func
     | "[" [expr ("," expr)*] "]"           -> list
     | "(" expr ")"        -> paren
     | CNUMBER             -> cnumber
     | ESCAPED_STRING      -> string
     | CAPITAL_ID          -> matrix

FUNC_NAME: "midpoint" | "ref" | "expect" | "U" | "zu" | "P" | "Q" | "covariance" | "variance" | "subs" | "try" | "limit" | "forall" | "limitninf" | "limitpinf" | "imply" | "exist" | "len" | "sum" | "angle" | "line" | "sum2" | "charge" | "electricfield" | "perm" | "point" | "equationrhs" | "transpose" | "equationlhs" | "equation" | "error" | "covariance" | "variance" | "expect" | "mag" | "rad" | "laplace" | "diverge" | "pdif" | "gradient" | "curl" | "point1" | "point2" | "dot" | "point3" | "line1" | "line2" | "line3" | "sin" | "circumcenter" | "eqtri" | "linesegment" | "cos" | "tan" | "log" | "sqrt" | "zu" | "integrate" | "dif" | "abs" | "cosec" | "sec" | "cot" | "arctan" | "arcsin" | "arccot" | "arccos" | "log10"

VARIABLE: /[a-z]/ | "nabla" | "pi" | "kc" | "hbar" | "em" | "ec" | "anot" | "false" | "true"

CAPITAL_ID: /[A-Z]/

CNUMBER: /c[0-9]+/

%import common.NUMBER
%import common.ESCAPED_STRING
%import common.WS_INLINE
%ignore WS_INLINE
"""
def parse(equation, funclist=None):
    equation = copy.copy(equation.replace(" ", ""))
    grammar2 = copy.deepcopy(grammar)
    if funclist is not None:
        output = grammar2.split("\n")
        for i in range(len(output)):
            if "FUNC_NAME:" in output[i]:
                output[i] = output[i].replace("FUNC_NAME: ", "FUNC_NAME: " + " | ".join(['"' + x + '"' for x in funclist]) + " | ")
        grammar2 = "\n".join(output)
    parser_main = Lark(grammar2, start='start', parser='lalr')
    parse_tree = parser_main.parse(equation)
    def convert_to_treenode(parse_tree):
        if isinstance(parse_tree, Tree):
            node = TreeNode(parse_tree.data)
            node.children = [convert_to_treenode(child) for child in parse_tree.children]
            return node
        else:
            return TreeNode(str(parse_tree))
    def remove_past(equation):
        if equation.name in {"number", "paren", "func", "variable", "pass_through", "cnumber", "string", "matrix"}:
            if len(equation.children) == 1:
                return remove_past(equation.children[0])
            else:
                equation.children = [remove_past(child) for child in equation.children]
                return TreeNode(equation.children[0].name, equation.children[1:])
        equation.children = [remove_past(child) for child in equation.children]
        return equation
    def prefixindex(equation):
        if equation.name == "base" and len(equation.children) > 1:
            return TreeNode("index", [equation.children[0]] + equation.children[1].children)
        return TreeNode(equation.name, [prefixindex(child) for child in equation.children])
    tree_node = convert_to_treenode(parse_tree)
    tree_node = remove_past(tree_node)
    tree_node = prefixindex(tree_node)
    def fxchange(tree_node):
        tmp3 = funclist if funclist is not None else []
        if tree_node.name == "neg":
            child = fxchange(tree_node.children[0])
            if child.name.startswith("d_") and re.match(r"d_\d+(\.\d+)?$", child.name):
                return TreeNode("d_" + str(-int(child.name[2:])))
            else:
                return TreeNode("f_sub", [tree_form("d_0"), child])
        if tree_node.name == "pass_through":
            return fxchange(tree_node.children[0])
        return TreeNode(
            "f_" + tree_node.name if tree_node.name in tmp3 + ["P", "Q", "U", "limitninf", "limitpinf", "limit", "try", "ref", "sqrt","imply","forall","exist","exclude","union","intersection","len","index","angle","charge","sum2","electricfield","line","point","sum","transpose","equationrhs","equationlhs","equation","covariance","variance","expect","error","laplace","dot","curl","pdif","diverge","gradient","rad","ge","le","gt","lt","eqtri","linesegment","midpoint","mag","point1","point2","point3","line1","line2","line3","log10","arccot","arcsin","arccos","arctan","list","cosec","sec","cot","equiv","or","not","and","circumcenter","eq","sub","add","sin","cos","tan","mul", "cross", "wmul","zu","integrate","dif","pow","div","log","abs"] else "d_" + tree_node.name,
            [fxchange(child) for child in tree_node.children]
        )
    tree_node = fxchange(tree_node)
    for const in ["e","pi","kc","em","ec","anot","hbar","false","true","i","nabla"]:
        tree_node = replace(tree_node, tree_form("d_"+const), tree_form("s_"+const))
    for i, c in enumerate(["x","y","z"] + [chr(x+ord("a")) for x in range(0,23)]):
        tree_node = replace(tree_node, tree_form("d_"+c), tree_form("v_"+str(i)))
    for i, c in enumerate([chr(x+ord("A")) for x in range(0,26)]):
        tree_node = replace(tree_node, tree_form("d_"+c), tree_form("v_-"+str(i+1)))
        tree_node = replace(tree_node, tree_form("f_"+c), tree_form("v_-"+str(i+1)))
    def rfx(tree_node):
        if tree_node.name[:3] == "d_c":
            return tree_form("v_" + str(int(tree_node.name[3:])+100))
        tree_node.children = [rfx(child) for child in tree_node.children]
        return tree_node
    tree_node = rfx(tree_node)
    return tree_node
