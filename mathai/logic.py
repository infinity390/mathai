from .expand import expand
import itertools
from .base import *
from .fraction import fraction
from .simplify import simplify
from .expand import expand
from .factor import factorconst
def helper2(eq):
    if eq.name in ["f_forall", "f_exist"]:
        return False
    if eq.name in ["f_and", "f_not", "f_or", "f_equiv", "f_imply"]:
        return True
    return any(helper2(child) for child in eq.children)
def helper(eq):
    op_dic = {"le":"ge","ge":"le","gt":"lt","lt":"gt","eq":"eq"}
    out2 = []
    eq = simplify(eq)
    logic00 = lambda x: dowhile(x,logic0)
    simp = lambda y: simplify(factorconst(dowhile(y, fraction)))
    simp2 = simp
    def canon(eq):
        if eq.name[2:] in "eq ge gt le lt".split(" "):
            eq1 = simplify(TreeNode("f_"+op_dic[eq.name[2:]], [simp2(-eq.children[0]), tree_form("d_0")]))
            eq2 = simplify(TreeNode(eq.name, [simp2(eq.children[0]), tree_form("d_0")]))
            if eq1 == eq2:
                return eq1
            elif str_form(eq1.children[0]) < str_form(eq2.children[0]):
                return eq2
            else:
                return eq1
        return TreeNode(eq.name, [canon(child) for child in eq.children])
    def prepare2(eq):
        nonlocal out2
        if eq.name[2:] in "eq ge gt le lt".split(" "):
            if eq not in out2:
                out2.append(eq)
                return
        if not helper2(eq):
            out2.append(eq)
            return
        for child in eq.children:
            prepare2(child)
    eq = simp(eq)
    eq = canon(eq)
    eq = logic00(eq)
    prepare2(eq)
    dic = {}
    v = ["v_"+str(i) for i in range(26) if "v_"+str(i) not in vlist(eq)]
    for key in out2:
      if key not in dic.keys():
          dic[key] = tree_form(v.pop(0))
      eq = replace(eq,key,dic[key])
    eq = truth_gen(eq)
    if eq.name in ["s_true", "s_false"]:
        return eq
    eq = logic4(eq)
    for key in dic.keys():
      eq = replace(eq,dic[key],key)
    return eq
def solve_logically2(eq):
    if eq.name in ["f_forall", "f_exist"]:
        s = str_form(eq.children[1])
        if "f_forall" not in s and "f_exist" not in s :
            return TreeNode(eq.name, [eq.children[0], helper(eq.children[1])])
        else:
            return TreeNode(eq.name, [eq.children[0], solve_logically2(helper(eq.children[1]))])
    return TreeNode(eq.name, [solve_logically2(child) for child in eq.children])
def solve_logically(eq):
    eq2 = helper(eq)
    return solve_logically2(eq2)
def set_sub(eq):
  if eq.name == "f_sub":
    return eq.children[0] & eq.children[1].fx("not")
  return TreeNode(eq.name, [set_sub(child) for child in eq.children])
def compute_logic(eq):
     if eq is None:
          return None
     if eq.name == "s_true":
          return True
     if eq.name == "s_false":
          return False
     if eq.name == "f_and":
          return all(compute_logic(child) for child in eq.children)
     if eq.name == "f_or":
          return any(compute_logic(child) for child in eq.children)
     if eq.name == "f_not":
          return not compute_logic(eq.children[0])
     if eq.name == "f_equiv":
          return compute_logic(eq.children[0]) == compute_logic(eq.children[1])
     if eq.name == "f_imply":
          if compute_logic(eq.children[0]):
               return compute_logic(eq.children[1])
          return True
     return None
def logic3(eq):
    if eq.name == "f_forall" and eq.children[1] in [tree_form("s_true"), tree_form("s_false")]:
        return eq.children[1]
    if eq.name == "f_not" and eq.children[0].name == "f_exist":
        return TreeNode("f_forall", [eq.children[0].children[0], eq.children[0].children[1].fx("not")])
    if eq.name == "f_exist" and eq.children[1].name == "f_or":
        return TreeNode("f_or", [TreeNode("f_exist", [eq.children[0], child]) for child in eq.children[1].children])
    if eq.name == "f_forall" and eq.children[1].name == "f_and":
        return TreeNode("f_and", [TreeNode("f_forall", [eq.children[0], child]) for child in eq.children[1].children])
    if eq.name == "f_exist":
        return TreeNode("f_forall", [eq.children[0], eq.children[1].fx("not")]).fx("not")
    return TreeNode(eq.name, [logic3(child) for child in eq.children])
def truth_gen(eq):
     dic = {}
     count = 0
     lst = []
     false_count = 0
     truth_count = 0
     for item in vlist(eq):
          dic[count] = item
          count += 1
     for item in itertools.product([False,True], repeat=count):
          orig = copy.deepcopy(eq)
          for i in range(count):
               eq = replace(eq, tree_form(dic[i]), tree_form("s_true") if item[i] else tree_form("s_false"))
          if compute_logic(eq):
               lst.append(list(item))
               truth_count += 1
          else:
               false_count += 1
          eq = orig
     if false_count == 0:
          return tree_form("s_true")
     elif truth_count == 0:
          return tree_form("s_false")
     outeq = []
     for item in lst:
          outeq2 = []
          for i in range(count):
               if item[i]:
                    outeq2.append(tree_form(dic[i]))
               else:
                    outeq2.append(tree_form(dic[i]).fx("not"))
          if len(outeq2) == 1:
               outeq2 = outeq2[0]
          else:
               outeq2 = TreeNode("f_and", outeq2)
          outeq.append(outeq2)
     if len(outeq) == 1:
          outeq = outeq[0]
     else:
          outeq = TreeNode("f_or", outeq)
     return outeq
def logic0(eq):
    if eq.children is None or len(eq.children) == 0:
        return eq
    children = [logic0(child) for child in eq.children]
    eq = TreeNode(eq.name, children)
    if eq.name in ["f_eq", "f_lt", "f_gt", "f_ge", "f_le"]:
        a_node, b_node = eq.children
        if a_node.name.startswith("d_") and b_node.name.startswith("d_"):
            a = int(a_node.name[2:])
            b = int(b_node.name[2:])
            if eq.name == "f_eq":
                return tree_form("s_true") if a == b else tree_form("s_false")
            if eq.name == "f_ge":
                return tree_form("s_true") if a >= b else tree_form("s_false")
            if eq.name == "f_gt":
                return tree_form("s_true") if a > b else tree_form("s_false")
            if eq.name == "f_lt":
                return tree_form("s_true") if a < b else tree_form("s_false")
            if eq.name == "f_le":
                return tree_form("s_true") if a <= b else tree_form("s_false")
    if eq.name == "f_ge":
        return TreeNode("f_or", [
            TreeNode("f_gt", list(eq.children)),
            TreeNode("f_eq", list(eq.children))
        ])
    if eq.name == "f_le":
        return TreeNode("f_or", [
            TreeNode("f_lt", list(eq.children)),
            TreeNode("f_eq", list(eq.children))
        ])
    if eq.name == "f_gt":
        return TreeNode("f_le", list(eq.children)).fx("not")
    if eq.name == "f_or":
        out = [c for c in list(set(eq.children)) if c != tree_form("s_false")]
        if any(c == tree_form("s_true") for c in out):
            return tree_form("s_true")
        if len(out) == 0:
            return tree_form("s_false")
        if len(out) == 1:
            return out[0]
        return TreeNode("f_or", out)
    if eq.name == "f_and":        
        out = [c for c in list(set(eq.children)) if c != tree_form("s_true")]
        if any(c == tree_form("s_false") for c in out):
            return tree_form("s_false")
        if len(out) == 0:
            return tree_form("s_true")
        if len(out) == 1:
            return out[0]
        return TreeNode("f_and", out)
    return eq
class BDDNode:
    __slots__ = ("var", "low", "high")
    def __init__(self, var, low, high):
        self.var = var
        self.low = low
        self.high = high
    def __hash__(self):
        return hash((self.var, id(self.low), id(self.high)))
    def __eq__(self, other):
        return (
            isinstance(other, BDDNode)
            and self.var == other.var
            and self.low is other.low
            and self.high is other.high
        )
BDD_TRUE = object()
BDD_FALSE = object()
class BDDManager:
    def __init__(self, var_order):
        self.order = var_order
        self.unique = {}
    def mk(self, var, low, high):
        if low is high:
            return low
        key = (var, low, high)
        if key not in self.unique:
            self.unique[key] = BDDNode(var, low, high)
        return self.unique[key]
def restrict(expr: TreeNode, var: str, val: bool) -> TreeNode:
    if expr.name == "s_true" or expr.name == "s_false":
        return expr
    if expr.name.startswith("v_"):
        if expr.name == var:
            return TreeNode("s_true", []) if val else TreeNode("s_false", [])
        return expr
    if expr.name == "f_not":
        r = restrict(expr.children[0], var, val)
        if r.name == "s_true":
            return TreeNode("s_false", [])
        if r.name == "s_false":
            return TreeNode("s_true", [])
        return TreeNode("f_not", [r])
    if expr.name == "f_and":
        kids = [restrict(c, var, val) for c in expr.children]
        if any(c.name == "s_false" for c in kids):
            return TreeNode("s_false", [])
        kids = [c for c in kids if c.name != "s_true"]
        return TreeNode("s_true", []) if not kids else TreeNode("f_and", kids)
    if expr.name == "f_or":
        kids = [restrict(c, var, val) for c in expr.children]
        if any(c.name == "s_true" for c in kids):
            return TreeNode("s_true", [])
        kids = [c for c in kids if c.name != "s_false"]
        return TreeNode("s_false", []) if not kids else TreeNode("f_or", kids)
    return expr
def build_bdd(expr: TreeNode, mgr: BDDManager, vars_left: list):
    if expr.name == "s_true":
        return BDD_TRUE
    if expr.name == "s_false":
        return BDD_FALSE
    if not vars_left:
        raise RuntimeError("Non-constant expression at leaf")
    v = vars_left[0]
    low_expr = restrict(expr, v, False)
    high_expr = restrict(expr, v, True)
    low = build_bdd(low_expr, mgr, vars_left[1:])
    high = build_bdd(high_expr, mgr, vars_left[1:])
    return mgr.mk(v, low, high)
def bdd_to_tree(node) -> TreeNode:
    if node is BDD_TRUE:
        return TreeNode("s_true", [])
    if node is BDD_FALSE:
        return TreeNode("s_false", [])
    v = TreeNode(node.var, [])
    high = bdd_to_tree(node.high)
    low = bdd_to_tree(node.low)
    pos = TreeNode("f_and", [v, high])
    neg = TreeNode("f_and", [TreeNode("f_not", [v]), low])
    return TreeNode("f_or", [pos, neg])
def snapshot(eq):
  return eq
def simplify_tree(eq: TreeNode) -> TreeNode:
    if eq.name in ("s_true", "s_false") or eq.name.startswith("v_"):
        return eq
    if eq.name == "f_not":
        c = simplify_tree(eq.children[0])
        if c.name == "s_true":
            return TreeNode("s_false", [])
        if c.name == "s_false":
            return TreeNode("s_true", [])
        if c.name == "f_not":
            return c.children[0]
        return TreeNode("f_not", [c])
    if eq.name in ("f_and", "f_or"):
        kids = [simplify_tree(c) for c in eq.children]
        flat = []
        for k in kids:
            if k.name == eq.name:
                flat.extend(k.children)
            else:
                flat.append(k)
        if eq.name == "f_and":
            if any(k.name == "s_false" for k in flat):
                return TreeNode("s_false", [])
            flat = [k for k in flat if k.name != "s_true"]
        else:
            if any(k.name == "s_true" for k in flat):
                return TreeNode("s_true", [])
            flat = [k for k in flat if k.name != "s_false"]
        uniq = []
        seen = set()
        for k in flat:
            s = snapshot(k)
            if s not in seen:
                seen.add(s)
                uniq.append(k)
        if not uniq:
            return TreeNode("s_true" if eq.name == "f_and" else "s_false", [])
        if len(uniq) == 1:
            return uniq[0]
        return TreeNode(eq.name, uniq)
    return eq
def logic4(expr: TreeNode) -> TreeNode:
    if expr.name in ["s_true", "s_false"]:
        return expr
    var_order = vlist(expr)
    mgr = BDDManager(var_order)
    bdd = build_bdd(expr, mgr, var_order)
    tree = bdd_to_tree(bdd)
    tree = dowhile(tree, simplify_tree)
    return tree
