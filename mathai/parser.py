import re
from .base import *
TOKEN_REGEX = [
    ("NUMBER",   r'\d+(\.\d+)?'),
    ("IDENT",    r'[A-Za-z_][A-Za-z0-9_]*'),
    ("OP",       r'<=|>=|!=|->|<->|[+\-*/^=<>|&(),~]'),
    ("SPACE",    r'\s+'),
]
MASTER = re.compile(
    '|'.join(f'(?P<{name}>{regex})'
             for name, regex in TOKEN_REGEX)
)
def tokenize(text):
    tokens = []
    for match in MASTER.finditer(text):
        kind = match.lastgroup
        value = match.group()
        if kind == "SPACE":
            continue
        tokens.append((kind, value))
    tokens.append(("EOF", "EOF"))
    return tokens
class Parser:
    PRECEDENCE = {
        "|": 10,
        "&": 20,
        "<->": 25,
        "=": 30,
        "<": 30,
        ">": 30,
        "<=": 30,
        ">=": 30,
        "+": 40,
        "-": 40,
        "*": 50,
        "/": 50,
        "^": 60,
    }
    RIGHT_ASSOC = {"^"}
    OP_MAP = {
        "+": "f_add",
        "-": "f_sub",
        "*": "f_mul",
        "/": "f_div",
        "^": "f_pow",
        "=": "f_eq",
        "<": "f_lt",
        ">": "f_gt",
        "<=": "f_le",
        ">=": "f_ge",
        "&": "f_and",
        "|": "f_or",
        "<->": "f_equiv",
    }
    FUNCTIONS = {
        "expect": "f_expect",
        "zu": "f_zu",
        "covariance": "f_covariance",
        "variance": "f_variance",
        "subs": "f_subs",
        "try": "f_try",
        "limit": "f_limit",
        "forall": "f_forall",
        "limitninf": "f_limitninf",
        "limitpinf": "f_limitpinf",
        "imply": "f_imply",
        "exist": "f_exist",
        "pdif": "f_pdif",
        "sin": "f_sin",
        "cos": "f_cos",
        "tan": "f_tan",
        "log": "f_log",
        "sqrt": "f_sqrt",
        "integrate": "f_integrate",
        "dif": "f_dif",
        "abs": "f_abs",
        "cosec": "f_cosec",
        "sec": "f_sec",
        "cot": "f_cot",
        "arctan": "f_arctan",
        "arcsin": "f_arcsin",
        "arccot": "f_arccot",
        "arccos": "f_arccos",
        "max": "f_max"
    }
    CONSTANTS = {
        "pi": "s_pi",
        "e": "s_e",
        "true": "s_true",
        "false": "s_false",
        "inf": "s_inf",
        "i": "s_i"
    }
    def __init__(self, text):
        self.tokens = tokenize(text)
        self.pos = 0
    def peek(self):
        return self.tokens[self.pos]
    def advance(self):
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok
    def expect(self, value):
        tok = self.advance()
        if tok[1] != value:
            raise SyntaxError(f"Expected {value}, got {tok}")
    def parse(self):
        expr = self.expression()
        if self.peek()[0] != "EOF":
            raise SyntaxError("Unexpected token")
        return expr
    def expression(self, rbp=0):
        t = self.advance()
        left = self.nud(t)
        while rbp < self.lbp(self.peek()):
            t = self.advance()
            left = self.led(t, left)
        return left
    def lbp(self, token):
        if token[0] != "OP":
            return 0
        return self.PRECEDENCE.get(token[1], 0)
    def nud(self, token):
        kind, value = token
        if kind == "NUMBER":
            return TreeNode("d_" + value)
        if kind == "IDENT":
            if value in self.CONSTANTS:
                return TreeNode(self.CONSTANTS[value])
            if self.peek()[1] == "(":
                self.expect("(")
                args = []
                if self.peek()[1] != ")":
                    while True:
                        args.append(self.expression())
                        if self.peek()[1] == ",":
                            self.advance()
                            continue
                        break
                self.expect(")")
                fname = self.FUNCTIONS.get(
                    value,
                    "f_" + value
                )
                return TreeNode(fname, args)
            return TreeNode("v_" + value)
        if value == "-":
            expr = self.expression(100)
            return TreeNode(
                "f_neg",
                [expr]
            )
        if value == "~":
            expr = self.expression(100)
            return TreeNode(
                "f_not",
                [expr]
            )
        if value == "(":
            expr = self.expression()
            self.expect(")")
            return expr
        raise SyntaxError(f"Unexpected token {token}")
    def led(self, token, left):
        op = token[1]
        bp = self.PRECEDENCE[op]
        if op in self.RIGHT_ASSOC:
            right = self.expression(bp - 1)
        else:
            right = self.expression(bp)
        return TreeNode(
            self.OP_MAP[op],
            [left, right]
        )
def normalize_variables(text):
    lower_map = {}
    lower_order = ['x', 'y', 'z']
    lower_order += [chr(c) for c in range(ord('a'), ord('w') + 1)]
    for i, ch in enumerate(lower_order):
        lower_map[ch] = i
    upper_map = {}
    for i, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        upper_map[ch] = -(i + 1)
    def repl(match):
        var = match.group(1)
        if var in lower_map:
            return f"v_{lower_map[var]}"
        if var in upper_map:
            return f"v_{upper_map[var]}"
        return match.group(0)
    return re.sub(r'v_([a-zA-Z])', repl, text)
def replace_var_convention_h(eq):
    if eq.name.startswith("v_"):
        return tree_form(normalize_variables(eq.name))
    return eq
def replace_var_convention(eq):
    return transform_dfs(eq, replace_var_convention_h, [])
def parse(text):
    return replace_var_convention(Parser(text).parse())
