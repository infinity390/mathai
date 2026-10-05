from .base import *
from .simplify import simplify
from .parser import parse
from .formula_compiler import formula_list_compiler
import marshal
from pathlib import Path
formula_data = {}
# formula in
# formula out
# literal variable (formula/equation)
# non-constant variable (formula)
# constant variable (formula)
# constant variable (equation)
# integer constraint
# positive constraint
# negative constraint
# associative arity
formula = """
a*x^2+b*x+c true x [a,b] [a,b,c] _ [a,0] _ _ 1
a*x+b true x [a,b] [a,b] _ [a,0] _ _ 2
a false _ _ _ _ _ _ _ 1
// is_integrate_subs

d*a^(b+c) d*a^b*a^c _ d _ _ [d,0] _ _ 2
// power_rule

integrate(x^2*e^(a*x+b),x) ((x^2/a)-(2*x/(a^2))+(2/(a^3)))*e^(a*x+b) x [a,b] [a,b] _ [a,0] _ _ 2
integrate(x*e^(a*x+b),x) ((x/a)-(1/(a^2)))*e^(a*x+b) x [a,b] [a,b] _ [a,0] _ _ 2
integrate(e^(a*x+b),x) e^(a*x+b)/a x [a,b] [a,b] _ [a,0] _ _ 2
integrate(1/(a*x+b),x) log(abs(a*x+b))/a x [a,b] [a,b] _ [a,0] _ _ 2
integrate((a*x+b)^c,x) (a*x+b)^(c+1)/(a*(c+1)) x [a,b] [a,b,c] _ [[a,0],[c,-1]] _ _ 2
integrate(1/cos(a*x+b)^2,x) tan(a*x+b)/a x [a,b] [a,b] _ [a,0] _ _ 2
integrate(1/sin(a*x+b)^2,x) -cot(a*x+b)/a x [a,b] [a,b] _ [a,0] _ _ 2
integrate(1/cos(a*x+b),x) log(abs((1+sin(a*x+b))/cos(a*x+b)))/a x [a,b] [a,b] _ [a,0] _ _ 2
integrate(1/sin(a*x+b),x) log(abs(tan((a*x+b)/2)))/a x [a,b] [a,b] _ [a,0] _ _ 2
integrate(sin(a*x+b)^2/cos(a*x+b)^2,x) tan(a*x+b)/a-x x [a,b] [a,b] _ [a,0] _ _ 1
integrate(sin(a*x+b)/(cos(a*x+b)^2),x) 1/(a*cos(a*x+b)) x [a,b] [a,b] _ [a,0] _ _ 1
integrate(sin(a*x+b),x) -cos(a*x+b)/a x [a,b] [a,b] _ [a,0] _ _ 2
integrate(cos(a*x+b),x) sin(a*x+b)/a x [a,b] [a,b] _ [a,0] _ _ 2
c+integrate(a+b,x) c+integrate(a,x)+integrate(b,x) x c _ _ [[a,0],[b,0],[c,1]] _ _ 2
integrate(x,x) x^2/2 x _ _ _ _ _ _ 2
integrate(a,x) a*x x _ a _ _ _ _ 2
c*integrate(a*b,x) c*a*integrate(b,x) x c a _ [[c,0],[a,1]] _ _ 2
// integration

integrate(cos(a*x+b)/sin(a*x+b),x) log(abs(sin(a*x+b)))/a x [a,b] [a,b] _ [a,0] _ _ 1
integrate(sin(a*x+b)/cos(a*x+b),x) -(log(abs(cos(a*x+b)))/a) x [a,b] [a,b] _ [a,0] _ _ 1
integrate(sin(x)^a*cos(x)^b,x) -(sin(x)^(a+1)*cos(x)^(b+1)/(b+1))+(a+b+2)/(b+1)*integrate(sin(x)^a*cos(x)^(b+2),x) x [a,b] [a,b] _ [b,-1] _ b 2
integrate((sin(x)/cos(x))^a,x) tan(x)^(a-1)/(a-1)-integrate((sin(x)/cos(x))^(a-2),x) x a a _ [[a,1],[a,0]] a _ 2
integrate((cos(x)/sin(x))^a,x) -(cot(x)^(a-1)/(a-1))-integrate((cos(x)/sin(x))^(a-2),x) x a a _ [[a,1],[a,0]] a _ 2
integrate(sin(x)^a/cos(x),x) -(sin(x)^(a-1)/(a-1))+integrate(sin(x)^(a-2)/cos(x),x) x a a _ [[a,1],[a,0]] a _ 2
integrate(cos(x)^a/sin(x),x) cos(x)^(a-1)/(a-1)+integrate(cos(x)^(a-2)/sin(x),x) x a a _ [[a,1],[a,0]] a _ 2
integrate(sin(x)^a*cos(x)^b,x) sin(x)^(a+1)*cos(x)^(b+1)/(a+1)+(a+b+2)/(a+1)*integrate(sin(x)^(a+2)*cos(x)^b,x) x [a,b] [a,b] _ [a,-1] _ a 2
integrate(sin(x)^a,x) sin(x)^(a+1)*cos(x)/(a+1)+(a+2)/(a+1)*integrate(sin(x)^(a+2),x) x _ a _ [[a,-1],[a,0]] _ a 2
integrate(cos(x)^a,x) -(sin(x)*cos(x)^(a+1)/(a+1))+(a+2)/(a+1)*integrate(cos(x)^(a+2),x) x _ a _ [[a,-1],[a,0]] _ a 2
// integration_trig

pdif(a^b,x) b*(a^(b-1))*pdif(a,x)+(a^b)*log(a)*pdif(b,x) x _ k _ _ _ _ 2
pdif(sin(a),x) cos(a)*pdif(a,x) x _ k _ [[c,1],[d,1],[f,0],[g,0]] _ _ 2
pdif(cos(a),x) -sin(a)*pdif(a,x) x _ k _ [[c,1],[d,1],[f,0],[g,0]] _ _ 2
pdif(arcsin(a),x) (1/sqrt(1-a^2))*pdif(a,x) x _ k _ [[c,1],[d,1],[f,0],[g,0]] _ _ 2
pdif(arccos(a),x) (-1/sqrt(1-a^2))*pdif(a,x) x _ k _ [[c,1],[d,1],[f,0],[g,0]] _ _ 2
pdif(arctan(a),x) (1/(1+a^2))*pdif(a,x) x _ k _ [[c,1],[d,1],[f,0],[g,0]] _ _ 2
pdif(k,x) 0 x _ k _ _ _ _ 2
pdif(x,x) 1 x _ k _ _ _ _ 2
pdif(a*b,x) pdif(a,x)*b+a*pdif(b,x) x _ k _ [[a,1],[b,1],[a,0],[b,0]] _ _ 2
c+pdif(a+b,x) c+pdif(a,x)+pdif(b,x) x c k _ [[c,1],[b,1],[a,0],[b,0]] _ _ 2
pdif(k*a,x) k*pdif(a,x) x _ k _ [[a,1],[k,1],[a,0],[k,0]] _ _ 2
// differentiation

I lambda(x,x) [x,y,f,t,I] _ _ _ _ _ _ 1
true lambda(t,lambda(f,t)) [x,y,f,t,I] _ _ _ _ _ _ 1
false lambda(t,lambda(f,f)) [x,y,f,t,I] _ _ _ _ _ _ 1
0 lambda(f,lambda(x,x)) [x,y,f,t,I] _ _ _ _ _ _ 1
// lambda_expand

apply(lambda(a,a),b) b _ _ _ _ _ _ _ 1
apply(lambda(a,apply(c,a)),b) apply(c,b) [a,b,c] _ _ _ _ _ _ 1
// lambda_reduce

lambda(x,x) I [x,y,f,t,I] _ _ _ _ _ _ 1
lambda(t,lambda(f,t)) true [x,y,f,t,I] _ _ _ _ _ _ 1
lambda(t,lambda(f,f)) false [x,y,f,t,I] _ _ _ _ _ _ 1
lambda(f,lambda(x,x)) 0 [x,y,f,t,I] _ _ _ _ _ _ 1
// lambda_compress

limitpinf(a*b,x) a*limitpinf(b,x) x _ a _ [a,1] _ _ 2
limitpinf(x^c,x) 0 x _ _ _ _ _ c 2
limitpinf(x^c*e^(d*x),x) 0 x _ _ _ _ _ d 2
limitpinf(x*e^(d*x),x) 0 x _ _ _ _ _ d 2
limitpinf(e^(d*x),x) 0 x _ _ _ _ _ d 2
limitpinf(a+b,x) limitpinf(a,x)+limitpinf(b,x) x _ _ _ _ _ _ 2
limitpinf(a,x) a x _ a _ _ _ _ 1
// limit_infinity

1/(1+sin(x)) (1-sin(x))/cos(x)^2 x _ _ _ _ _ _ 2
1/(1+cos(x)) (1-cos(x))/sin(x)^2 x _ _ _ [x,0] _ _ 2
// trigonometry_misc

wmul(identity(a),b) b x _ k m _ _ _ 6
wmul(b,identity(a)) b x _ k m _ _ _ 6
pdif(k,vec(x)) 0 x _ k m _ _ _ 6
pdif(hadamard(k,a),vec(x)) hadamard(k,pdif(a,vec(x))) x _ k m _ _ _ 6
pdif(wadd(a,b),vec(x)) wadd(pdif(a,vec(x)),pdif(b,vec(x))) x _ k m _ _ _ 6
pdif(vec(wadd(a,b)),vec(x)) wadd(pdif(vec(a),vec(x)),pdif(vec(b),vec(x))) x _ k m _ _ _ 6
transpose(transpose(a)) a x _ k m _ _ _ 6
vec(vec(a)) vec(a) x _ k m _ _ _ 6
pdif(vec(flatten(a)),vec(x)) pdif(vec(a),vec(x)) x _ k m _ _ _ 6
pdif(vec(x),vec(x)) identity(len(x)*len(index(x,0))) x _ k m _ _ _ 6
pdif(vec(transpose(a)),vec(x)) wmul(commutation(len(a),len(index(a,0))),pdif(vec(a),vec(x))) x _ k m _ _ _ 6
pdif(vec(hadamard(a,b)),vec(x)) wadd(wmul(diag(b),pdif(vec(a),vec(x))),wmul(diag(a),pdif(vec(b),vec(x)))) x _ k m _ _ _ 6
pdif(vec(broadcast(a,r)),vec(x)) wmul(kronecker(identity(len(vec(a))),wadd(1,zeros(r,1))),pdif(vec(a),vec(x))) x _ k m _ _ _ 6
pdif(vec(sigmoid(a)),vec(x)) wmul(diag(vec(hadamard(sigmoid(a),wadd(1,hadamard(-1,sigmoid(a)))))),pdif(vec(a),vec(x))) x _ k m _ _ _ 6
pdif(vec(wmul(a,b)),vec(x)) wadd(wmul(kronecker(transpose(b),identity(len(a))),pdif(vec(a),vec(x))),wmul(kronecker(identity(len(index(b,0))),a),pdif(vec(b),vec(x)))) x _ k m _ _ _ 6
pdif(wmul(transpose(y),y),vec(x)) wmul(transpose(pdif(y,vec(x))),hadamard(2,y)) x _ k m _ _ _ 6
pdif(vec(conv(a,b)),vec(x)) wadd(wmul(im2col(a,b),pdif(vec(b),vec(x))),wmul(col2im(b,a),pdif(vec(a),vec(x)))) x _ k m _ _ _ 6
// matrix_vectorization_calculus

expect(a+b) expect(a)+expect(b) _ _ _ _ [[a,0],[a,1],[b,0],[b,1]] _ _ 2
expect(1) 1 _ _ _ _ _ _ _ 2
expect(0) 0 _ _ _ _ _ _ _ 2
variance(x) expect(x^2)+expect(x)^2 _ _ _ _ _ _ _ 2
covariance(x,y) expect(x*y)-expect(x)*expect(y) _ _ _ _ _ _ _ 2
expect(k) k _ [A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z] k _ _ _ _ 2
// statistics_1

expect(x*y)-expect(x)*expect(y)+a covariance(x,y)+a _ _ _ _ [[x,1],[x,0],[y,0],[y,1],[b,1],[a,1]] _ _ 1
-expect(x*y)+expect(x)*expect(y)+a -covariance(x,y)+a _ _ _ _ [[x,1],[x,0],[y,0],[y,1],[b,1],[a,1]] _ _ 1
// statistics_2

a*x^2+b*x+c a*(x-(-b+sqrt(b^2-4*a*c))/(2*a))*(x-(-b-sqrt(b^2-4*a*c))/(2*a)) x [a,b,c] [a,b,c] _ [[a,0],[c,1]] b^2-4*a*c _ 2
// quadratic

a*pdif(u,x)+b*pdif(u,y)+c=0 list(dif(x,y)=a/b,dif(u,x)=-c/a,dif(u,y)=-c/b) [u,x,y] [a,b,c] _ _ [[a,0],[b,0],[c,0]] _ _ 1
a*pdif(u,x)+b*pdif(u,y)=0 list(dif(x,y)=a/b,dif(u,x)=0) [u,x,y] [a,b] _ _ [[a,0],[b,0]] _ _ 2
// pde_character
"""

def load_formula(label):
    global formula_data 
    return formula_data[label]
def convert_lst(eq):
    if eq.name == "f_list":
        return [int(child.name[2:]) if child.name.startswith("d_") else convert_lst(child) for child in eq.children]
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
def compile_formula(s, save_to_file=None):
    lst = []
    for item in s.split("\n"):
        item = item.split(" ")
        lst.append([simplify(parse(item[0])), simplify(parse(item[1]))] + [convert_string(item2) for item2 in item[2:-1]] + [int(item[-1])])
    fx = formula_list_compiler(lst, save_to_file)
    if fx is None:
        return None
    return lambda y: dowhile(fx(simplify(y)), lambda x: transform_dfs(x, wrap_h, [fx]))
def make_formula(fx):
    return lambda y: dowhile(fx(simplify(y)),lambda x: transform_dfs(x, wrap_h, [fx]))
def de_w_addmul_h(eq):
    if eq.name in ["f_addw", "f_mulw", "f_waddw", "f_hadamardw"]:
        return TreeNode(eq.name[:-1], eq.children)
    return eq

def de_w_addmul(eq):
    return transform_dfs(eq, de_w_addmul_h)
def load_formula_from_file():
    global formula_data
    print("loading formulas from file...")
    formula_dir = Path(__file__).parent / "formula"
    for file in formula_dir.glob("*.marshal"):
        with file.open("rb") as f:
            code = marshal.load(f)
        namespace = {
            "tree_form": tree_form,
            "TreeNode": TreeNode,
            "contain": contain,
            "str_form": str_form,
            "copy": copy,
            "simplify": simplify,
            "frac": frac,
            "de_w_addmul": de_w_addmul
        }
        exec(code, namespace)
        formula_data[file.stem] = make_formula(namespace["transform"])
    print("done\n")
def init_formula(label_list="all", save_to_file=False):
    global formula_data
    global formula
    print("initialising formula compilation...")
    for item in formula.strip().split("\n\n"):
        item = item.split("\n")
        item[-1] = item[-1][3:]
        if label_list == "all" or item[-1] in label_list or (label_list == "god" and item[-1] in "is_integrate_subs integration_trig differentiation integration quadratic trigonometry_misc".split(" ")):
            formula_data[item[-1]] = compile_formula("\n".join(item[:-1]), item[-1] if save_to_file else None)
            print(f"{item[-1]} formula set compiled")
    print()
    return None
