from .simplify import simplify
from .base import *
from .parser import parse
from .formula_applier import formula_list_applier

diff2_s = """pdif(e^a,x) e^a*pdif(a,x) [] x _ _ _
pdif(a^b,x) b*(a^(b-1))*pdif(a,x)+(a^b)*log(a)*pdif(b,x) [] x _ _ _
pdif(sin(a),x) cos(a)*pdif(a,x) [] x _ _ _
pdif(cos(a),x) -sin(a)*pdif(a,x) [] x _ _ _
pdif(arcsin(a),x) (1/sqrt(1-a^2))*pdif(a,x) [] x _ _ _
pdif(arccos(a),x) (-1/sqrt(1-a^2))*pdif(a,x) [] x _ _ _
pdif(arctan(a),x) (1/(1+a^2))*pdif(a,x) [] x _ _ _
pdif(k,x) 0 [] x k _ _
pdif(x,x) 1 [] x _ _ _
pdif(product(a,b),x) pdif(a,x)*b+a*pdif(b,x) [] x _ _ _
pdif(sum(a,b),x) pdif(a,x)+pdif(b,x) [] x _ _ _
pdif(product(k,a),x) k*pdif(a,x) [] x k _ _"""

diff2 = lambda x: formula_list_applier(x, diff2_s)

def diff(equation, var=None):
    var = var if var else "v_0"
    out = diff2(simplify(TreeNode("f_pdif", [equation, tree_form(var)])))
    return out
