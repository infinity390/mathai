# Math AI Documentation
## Source
Github repository of the code
https://github.com/infinity390/mathai

PyPi Library
https://pypi.org/project/mathai

## Philosophy
I think it is a big realization in computer science and programming to realize that computers can solve mathematics.  
This understanding should be made mainstream. It can help transform education, mathematical research, and computation of mathematical equations for work.

## Societal Implications Of Such A Computer Program
I think mathematics is valued by society because of education. Schools and universities teach them.  
So this kind of software, if made mainstream, could revolutionarize society.

## The Summary Of How Computer "Solves" Math
Math equations are tree data structure (`TreeNode` class).  
We can manipulate the math equations using various algorithms (functions provided by the `mathai` library).  
The `god(expr)` function can be used to solve any mathematical equation, automatically with steps.

## The areas of mathematics my Mathematics Solving Software can Tackle
- Differentiation (partial and full derivaties both)
- Limits (approaching to infinity and to a constant value)
- Integration
- Trigonometry
- Algebra
- Inequality
- Absolute Value
- Boolean Algebra and Logic
- Linear Equations
- Ordinary Differential Equations
  
## The Library
Import the library by doing:

```python
from mathai import *
```

| Function | Description |
|---|---|
| `parse(string)` | Parses mathematical equations into Tree Data structure |
| `god(string)` | Can automatically solve any Math with steps |
| `simplify(expr)` | Simplifies and cleans up a given mathematical expression or equation. |
| `apart(expr)` | Partial Fraction Decomposition |
| `factor1(expr)` | Manual Factorization |
| `factor2(expr)` | Factorization of Quadratic Equations |
| `expand(expr)` | Distributive Property |
| `fraction(expr)` | Fraction Cross Multiplication |
| `diff(expr,wrt)` | Differentiation |
| `diff2(expr)` | Differentation Partial and Full |
| `limit0(expr)` | Remove constants to outside in a limit | 
| `limit1(expr)` | Limit to zero using Lhopital Rule |
| `limit2(expr)` | Limit across summations |
| `limit3(expr)` | Limit approaching to infinity |
| `limit4(expr)` | Limit approach to infinity given a fraction of polynomimals |
| `trig0(expr)` | Basic trigonometry formulas |
| `trig1(expr)` | Product to sum trigonometry |
| `ode_solve(expr)` | Solves ODEs but doesn't integrate automatically afterwards |
| `integrate_const(expr)` | Removes integration outside the integral |
| `integrate_formula(expr)` | Basic integration related formulas |
| `integrate_byparts(expr)` | Integration by parts |
| `integrate_subs(expr)` | Integration by substitution | 
| `integrate_summation(expr)` | Integration across summation |
| `integrate_fraction(expr)` | Integration of fractions |
| `integrate_clean(expr)` | Clean the expression to only keep the answer if integration was successful |
| `wavycurvy(expr)` | wavycurvy method to solve inequalities |
| `linear_solve(expr)` | linear equation solving |
| `absolute(expr)` | Handle absolute values by making cases |
| `solve_logically(expr)` | Boolean algebra by Binary Decision Diagrams and Truth tables |

### Incomplete Documentation, Will be updated and completed later on

### Demonstrations

#### Example Demonstration 1 (derivation of hydrogen atom's ground state energy in electron volts using the variational principle in quantum physics)
```python
from mathai import *
basic_int = lambda x: dowhile(x, lambda y: fraction(simplify(integrate_const(integrate_formula(integrate_summation(expand(y)))))))
algebra = lambda x: dowhile(x, lambda y: fraction(simplify(y)))
z =  simplify(parse("1"))
k =  simplify(parse("8987551787"))
m =  simplify(parse("9109383701 * 10^(-40)"))
e1=  simplify(parse("1602176634 * 10^(-28)"))
hbar=simplify(parse("1054571817 * 10^(-43)"))
pi = tree_form("s_pi")
euler = tree_form("s_e")
r = parse("r")
a0 = hbar**2 / (k*e1**2*m)
c2 = z/a0
c1 = (z**3 / (pi * a0**3)).fx("sqrt")
psi = c1 * euler**(-c2 * r)
psi2 = psi**2
laplace_psi = diff(r**2 * diff(psi, r.name), r.name)/r**2
psi2 = simplify(psi2)
integral_psi2 = TreeNode("f_integrate", [psi2 * parse("4")* pi * r**2, r])
integral_psi2 = simplify(integral_psi2)
integral_psi2 = integrate_subs(integral_psi2)
integral_psi2 = basic_int(integral_psi2)
integral_psi2 = integrate_byparts(integral_psi2)
integral_psi2 = basic_int(integral_psi2)
integral_psi2 = integrate_byparts(integral_psi2)
integral_psi2 = basic_int(integral_psi2)
integral_psi2 = integrate_clean(integral_psi2)
integral_psi2 = algebra(integral_psi2)
a = limit1(TreeNode("f_limit", [integral_psi2, r]))
b = limit3(TreeNode("f_limitpinf", [integral_psi2, r]))
integral_psi2 = simplify(b-a)
V = -(k * z * e1**2)/r
Hpsi = -hbar**2/(2*m) * laplace_psi + V*psi
psiHpsi = psi * Hpsi
integral_psiHpsi = TreeNode("f_integrate", [psiHpsi * parse("4")* pi * r**2, r])
integral_psiHpsi = simplify(integral_psiHpsi)
integral_psiHpsi = integrate_subs(integral_psiHpsi)
integral_psiHpsi = basic_int(integral_psiHpsi)
integral_psiHpsi = integrate_byparts(integral_psiHpsi)
integral_psiHpsi = basic_int(integral_psiHpsi)
integral_psiHpsi = integrate_byparts(integral_psiHpsi)
integral_psiHpsi = basic_int(integral_psiHpsi)
integral_psiHpsi = integrate_clean(integral_psiHpsi)
integral_psiHpsi = algebra(integral_psiHpsi)
a = limit1(TreeNode("f_limit", [integral_psiHpsi, r]))
b = limit3(limit2(expand(TreeNode("f_limitpinf", [integral_psiHpsi, r]))))
integral_psiHpsi = simplify(b-a)
result =  integral_psiHpsi / integral_psi2
print(compute(result /e1))
```
#### Output

```
-13.605693122882867
```

#### Example Demonstration 2 (derivation of helium atom's ground state energy in electron volts using the variational principle in quantum physics)
```python
from mathai import *
basic_int = lambda x: dowhile(x, lambda y: fraction(simplify(integrate_formula(integrate_const(integrate_summation(y))))))
algebra = lambda x: dowhile(x, lambda y: fraction(simplify(y)))
a0 = simplify(parse("529177210903 * 10^(-23)"))
e0 = simplify(parse("88541878128 * 10^(-22)"))
m = simplify(parse("9109383701 * 10^(-40)"))
e1 = simplify(parse("1602176634 * 10^(-28)"))
hbar = simplify(parse("1054571817 * 10^(-43)"))
pi = tree_form("s_pi")
euler = tree_form("s_e")
hydro = -(e1 ** 2)/(4*pi*e0) * (1/(2*a0))
k = -(e1 ** 2)/(4*pi*e0)
Z = parse("a")
r1 = parse("b")
r2 = parse("c")
phi1 = parse("d")
phi2 = parse("f")
theta1 = parse("g")
theta2 = parse("h")
def psi(r1, r2):
    global a0, pi, euler, Z
    two = tree_form("d_2")
    return (Z**3 / (pi * a0**3)) * euler**(-Z * (r1 + r2) / a0)
def r12(r1, r2, theta1, theta2, phi1, phi2):
    return TreeNode("f_max", [r1, r2])
f = psi(r1, r2)
def pdif(eq, wrt):
  return diff(eq, wrt.name)
def laplacian_r1(f):
    global r1, theta1, phi1
    term_r = (1/r1**2) * pdif(r1**2 * pdif(f, r1), r1)
    term_theta = (1/(r1**2 * theta1.fx("sin"))) * pdif(
        theta1.fx("sin") * pdif(f, theta1),
        theta1
    )
    term_phi = (1/(r1**2 * theta1.fx("sin")**2)) * pdif(
        pdif(f, phi1),
        phi1
    )
    return simplify(term_r + term_theta + term_phi)
def laplacian_r2(f):
    global r2, theta2, phi2
    term_r = (1/r2**2) * pdif(r2**2 * pdif(f, r2), r2)
    term_theta = (1/(r2**2 * theta2.fx("sin"))) * pdif(
        theta2.fx("sin") * pdif(f, theta2),
        theta2
    )
    term_phi = (1/(r2**2 * theta2.fx("sin")**2)) * pdif(
        pdif(f, phi2),
        phi2
    )
    return simplify(term_r + term_theta + term_phi)
def integrate_exec(eq, wrt, a, b):
  eq = simplify(eq)
  orig = eq
  eq = TreeNode("f_integrate", [eq, wrt])
  eq = integration_basic(eq)
  eq = simplify(expand(eq))
  eq = integration_basic(eq)
  eq = simplify(fraction(eq))
  eq_a = TreeNode("f_limit", [replace(eq, wrt, wrt+a), wrt])
  eq_a = limit1(eq_a)
  eq_b = None
  if b == tree_form("s_inf"):
      eq = algebra(eq)
      eq = simplify(expand(eq))
      eq_b = TreeNode("f_limitpinf", [eq, wrt])
      eq_b = dowhile(eq_b, lambda x: expand(limit0(limit2(limit3(simplify(x))))))
  else:
      eq_b = TreeNode("f_limit", [replace(copy.deepcopy(eq), wrt, wrt+b), wrt])
      eq_b = limit1(eq_b)
  out = algebra(eq_b - eq_a)
  return out
def integrate_function(func, r, theta, phi):
    phi_part = integrate_exec(
        func,
        phi,
        parse("0"),
        parse("2*pi")
    )
    theta_part = integrate_exec(
        phi_part * theta.fx("sin"),
        theta,
        parse("0"),
        parse("pi")
    )

    r_part = integrate_exec(
        theta_part * r**2,
        r,
        parse("0"),
        tree_form("s_inf")
    )
    return r_part
H1 = f * (-hbar**2 / (2*m) * laplacian_r1(f))
php1_1 = integrate_function(H1, r1, theta1, phi1)
php1 = integrate_function(php1_1, r2, theta2, phi2)
H2 = f * (-hbar**2 / (2*m) * laplacian_r2(f))
php2_1 = integrate_function(H2, r1, theta1, phi1)
php2 = integrate_function(php2_1, r2, theta2, phi2)
php3 = k * (Z/r1 + Z/r2) - k * ((Z-2)/r1 + (Z-2)/r2)
php4_1 = integrate_function(f**2 * php3, r1, theta1, phi1)
php4 = integrate_function(php4_1, r2, theta2, phi2)
H3 = algebra(php1 + php2 + php4)
php_int = TreeNode("f_integrate", [-k * psi(r1, r2)**2 * 1/r12(r1, r2, theta1, theta2, phi1, phi2) * theta2.fx("sin") * r2**2 * theta1.fx("sin") * r1**2, theta2])
php_int = algebra(php_int)
php_int = basic_int(php_int)
php_int = integrate_subs(php_int)
php_int = basic_int(php_int)
php_int = integrate_clean(php_int)
php_int_a = limit1(TreeNode("f_limit", [php_int, theta2]))
php_int_b = replace(php_int, theta2, theta2+parse("pi"))
php_int_b = limit1(TreeNode("f_limit", [php_int_b, theta2]))
php_int = algebra(php_int_b - php_int_a)
php_int = simplify(expand(php_int))
php_int = TreeNode("f_integrate", [php_int, r2, tree_form("d_0"), tree_form("s_inf")])
php_int = algebra(php_int)
php_int = basic_int(php_int)
php_int = factor2(php_int)
php_int = integrate_definite(php_int)
php_int = simplify(expand(php_int))
php_int = integration_basic(php_int)
php_int = dowhile(php_int, lambda x: limit3(simplify(limit2(limit0(limit1(x))))))
phpd = integrate_exec(php_int, theta1, parse("0"), parse("pi"))
phpd = algebra(phpd)
phpd = integrate_exec(phpd, r1, parse("0"), parse("inf")) * parse("2*pi*2*pi")
H = algebra(H3 + phpd)
dh = diff(H, Z.name)
hs = inverse(dh, Z.name)
H = replace(H, Z, hs)
print(compute(H/e1))
```
#### Output

```
-77.48867420464015
```

#### Example Demonstration 3 (boolean algebra)
```python
from mathai import *
eq = parse("(A-B)|(B-A)")
eq = set_sub(eq)
eq = solve_logically(eq)
print(eq)
eq = parse("(A|B)-(A&B)")
eq = set_sub(eq)
eq = solve_logically(eq)
print(eq)
```
#### Output

```
(~A&B)|(~B&A)
(~A&B)|(~B&A)
```

#### Example Demonstration 4 (limits approaching to a constant value)
```python
from mathai import *
limits = ["(e^(tan(x)) - 1 - tan(x)) / x^2", "sin(x)/x", "(1-cos(x))/x^2", "(sin(x)-x)/sin(x)^3"]
for q in limits:
    q = fraction(simplify(TreeNode("f_limit",[parse(q),parse("x")])))
    q = limit1(q)
    print(q)
```
#### Output

```
1/2
1
1/2
-(1/6)
```

#### Example Demonstration 5 (limits approaching to infinity)
```python
from mathai import *
eq= parse("limitpinf((3*x^2+x)/(2*x^2+5),x)")
eq = simplify(eq)
eq = limit4(eq)
eq = simplify(eq)
eq = limit3(eq)
eq = simplify(eq)
print(eq)
```
#### Output

```
3/2
```

#### Example Demonstration 6 (linear equations) (general solution of linear equations in two variables)
```python
from mathai import *
eq= parse("a*x+b*y+c = 0 & d*x+f*y+g = 0")
eq = simplify(eq)
eq = linear_solve(eq, [parse(item) for item in "a b c d f g".split(" ")])
eq = factor1(eq)
eq = simplify(eq)
for item in eq.children:
  print(item)
```
#### Output

```
((((c*f)-(b*g))/((a*f)-(b*d)))+x)=0
((((a*g)-(c*d))/((a*f)-(b*d)))+y)=0
```

#### Example Demonstration 7 (expectation algebra)
```python
from mathai import *
eq = simplify(parse("covariance(A+B,C+D)=covariance(B,C)+covariance(B,D)+covariance(A,D)+covariance(A,C)"))
eq = logic0(simplify(expect(simplify(expand(expect(eq))))))
print(eq)
```
#### Output

```
true
```

### Questions solved using god() function

#### Code

```python
from mathai import *
question_list = """integrate(tan(x)/(sec(x)+tan(x)),x)
integrate(sec(x)/(sec(x)+tan(x)),x)
integrate(e^arctan(x)/(1+x^2),x)
integrate(sin(x)^2/(1+cos(x)),x)
integrate(tan(x)^3,x)
integrate(cos(x)/(1+cos(x)),x)
integrate(1/(1+sin(x)),x)
integrate(cos(x)/(1+sin(x))^2,x)
(x-1)^2 = x^2 - 1
(sin(x)+cosec(x))^2+(cos(x)+sec(x))^2=7+tan(x)^2+cot(x)^2
2*x/(2*x^2+5*x+2)>1/(x+1)
(5*x-1)<(x+1)^2&(x+1)^2<7*x-3
abs(x+5)*x+2*abs(x+7)-2=0
x*abs(x)-5*abs(x+2)+6=0
abs(3*x-5)+abs(8-x)=abs(3+2*x)
abs(x^2+5*x+9)<abs(x^2+2*x+2)+abs(3*x+7)
(A-B)|(B-A) <-> (A|B)-(A&B)
(cosec(x)-cot(x))^2=(1-cos(x))/(1+cos(x))
x^2 = 4 & x+y^2 = 1
x + y*x = 5 & y + z=5 & z = 4
integrate(abs(x+1),x,-4,10)
integrate(abs(sin(x)),x,-pi,pi/6)
x^(2*x)=1
-i*(i+1)^5
sqrt(x) = x-2
integrate(sin(x+a)/sin(x),x)
integrate(sqrt(sin(2*x))*cos(2*x),x)
x = y & y = z & x+y+z=180
sec(x)^2*tan(y)+sec(y)^2*tan(x)*dif(y,x)=0
x + y = 10 & x*y = 24
(x+y)*dif(y,x)=1
abs(abs(x-2)-3)<=2
abs(x)>=0
dif(y,x)=arcsin(x)
integrate(sin(x)^6+cos(x)^6+3*sin(x)^2*cos(x)^2,x)
integrate((x^4+x^2+1)/(x^2-x+1),x)
integrate(1/(sin(x)^2*cos(x)^2),x)
integrate(x/sqrt(x+4),x)
integrate(sin(x)^4,x)
integrate(2*x/(1+x^2),x)
integrate(sin(2*x+5)^2,x)
integrate(sqrt(a*x+b),x)
integrate(x*sqrt(x),x)
integrate(x*sqrt(1+2*x^2),x)
integrate(e^(2*x+3),x)
integrate(x/e^(x^2),x)
integrate(sin(x)*sin(cos(x)),x)
integrate(sin(3*x)*cos(4*x),x)
integrate(cos(2*x)*cos(4*x)*cos(6*x),x)
integrate(sin(2*x+1)^3,x)
integrate(sin(x)^3*cos(x)^3,x)
integrate(sin(x)*sin(2*x)*sin(3*x),x)
integrate(sin(4*x)*sin(8*x),x)
integrate(cos(2*x)^4,x)
integrate(x/((x+1)*(x+2)),x)
integrate(1/(x^2-9),x)
integrate((3*x-1)/((x-1)*(x-2)*(x-3)),x)
integrate(x/((x-1)*(x-2)*(x-3)),x)
integrate(2*x/(x^2+3*x+2),x)
integrate((1-x^2)/(x*(1-2*x)),x)
integrate(x/((x-1)^2*(x+2)),x)
integrate((2*x-3)/((x^2-1)*(2*x+3)),x)
integrate(5*x/((x+1)*(x^2-4)),x)
(x+2)*(x+3)/((x-2)*(x-3))<=1
cos(x)/(1+sin(x))+(1+sin(x))/cos(x)=2*sec(x)
tan(x)/(1-cot(x))+cot(x)/(1-tan(x))=1+sec(x)*cosec(x)
(1+sec(x))/sec(x)=sin(x)^2/(1-cos(x))
(cos(x)-sin(x)+1)/(cos(x)+sin(x)-1)=cosec(x)+cot(x)
integrate(x/((x-1)*(x^2+1)),x)
(sin(x)-2*sin(x)^3)/(2*cos(x)^3-cos(x))=tan(x)
(cosec(x)-sin(x))*(sec(x)-cos(x))=1/(tan(x)+cot(x))
integrate(2/((1-x)*(1+x^2)),x)
x^2-abs(x+2)+x>0
limit(sin(x)/x,x)
limit((x^2 - 1)/(x-1),x,1)
dif(y,x)=sqrt(4-y^2)
dif(y,x)+y=1
x^5*dif(y,x)=-y^5
dif(y,x)=(1+x^2)*(1+y^2)
x*(x^2-1)*dif(y,x)=1
(x^2+x*y)*dif(y,x)=(x^2+y^2)
dif(y,x)=(x+y)/x
(x-y)*dif(y,x)-(x+y)=0
(x^2-y^2)+2*x*y*dif(y,x)=0
x*dif(y,x)-y+x*sin(y/x)=0
(a+b)^2 = a^2 + b^2 + 2*a*b
(x-1)*(x+1) = x^2 - 1
integrate((7^(7^(7^x)))*(7^(7^x))*(7^x),x)"""
for item in question_list.split("\n"):
  god(item)
```

#### Output

```
? integrate(tan(x)/(sec(x)+tan(x)),x)
thinking...
integrate(((cos(x)*sin(x))/(cos(x)+(cos(x)*sin(x)))),x)
integrate((sin((2*x))/(2*(cos(x)+(sin((2*x))/2)))),x)
integrate((sin((2*x))/(cos(x)+(sin((2*x))/2))),x)/2
integrate((sin(x)/(1+sin(x))),x)
integrate((sin(x)/(1+sin(x))),x)
integrate(((((-1+(cos(x)^2))*(cos(x)^2))+((cos(x)^2)*sin(x)))/(cos(x)^4)),x)
integrate((1+(-1/(cos(x)^2))+(sin(x)/(cos(x)^2))),x)
integrate((sin(x)/(cos(x)^2)),x)-tan(x)+x
-tan(x)+try(subs(integrate((y/(1/((1-(y^2))^(-3/2)))),y),y,sin(x)),subs(integrate((-1/(y^2)),y),y,cos(x)),subs(integrate((cos((y^(-1/2)))/2),y),y,(1/(cos(x)^2))))+x
-tan(x)+try(subs(integrate((y/(1/(((1-y)*(1+y))^(-3/2)))),y),y,sin(x)),subs((1/y),y,cos(x)),subs((integrate(cos((y^(-1/2))),y)/2),y,(1/(cos(x)^2))))+x
=> (1/cos(x))+(-sin(x)/cos(x))+x

? integrate(sec(x)/(sec(x)+tan(x)),x)
thinking...
integrate((cos(x)/(cos(x)+(cos(x)*sin(x)))),x)
integrate((cos(x)/(cos(x)+(sin((2*x))/2))),x)
integrate((1/(1+sin(x))),x)
integrate((1/(1+sin(x))),x)
integrate(((-((cos(x)^2)*sin(x))+(cos(x)^2))/(cos(x)^4)),x)
integrate(((1/(cos(x)^2))+(-sin(x)/(cos(x)^2))),x)
-integrate((sin(x)/(cos(x)^2)),x)+tan(x)
-try(subs(integrate((y/(1/((1-(y^2))^(-3/2)))),y),y,sin(x)),subs(integrate((-1/(y^2)),y),y,cos(x)),subs(integrate((cos((y^(-1/2)))/2),y),y,(1/(cos(x)^2))))+tan(x)
-try(subs(integrate((y/(1/(((1-y)*(1+y))^(-3/2)))),y),y,sin(x)),subs((1/y),y,cos(x)),subs((integrate(cos((y^(-1/2))),y)/2),y,(1/(cos(x)^2))))+tan(x)
=> (-1/cos(x))+(sin(x)/cos(x))

? integrate(e^arctan(x)/(1+x^2),x)
thinking...
integrate((1/((1+(x^2))*(e^-arctan(x)))),x)
integrate((1/((1+(x^2))*(e^-arctan(x)))),x)
integrate((1/((1+(x^2))*(e^-arcsin((x/(1/((1+(x^2))^(-1/2)))))))),x)
integrate((1/((1+(x^2))*(e^-arcsin((x/(1/((1+(x^2))^(-1/2)))))))),x)
try(subs(integrate((-1/(2*(1/((-1+(1/y))^(-1/2)))*(e^-arcsin((sqrt((-1+(1/y)))*sqrt(y))))*y)),y),y,(1/(1+(x^2)))),subs(integrate((1/(2*(1+y)*(1/(y^(-1/2)))*(e^-arcsin((sqrt(y)/(1/((1+y)^(-1/2)))))))),y),y,(x^2)),subs(integrate((-1/(abs(y)*(1/((-1+(1/(y^2)))^(-1/2)))*(e^-arcsin((abs(y)*sqrt((-1+(1/(y^2))))))))),y),y,((1+(x^2))^(-1/2))))
try(subs((-integrate((1/((1/((1-y)^(-1/2)))*(1/(y^(-1/2)))*(e^-arcsin(sqrt((1-y)))))),y)/2),y,(1/(1+(x^2)))),subs((integrate((1/((1+y)*(1/(y^(-1/2)))*(e^-arcsin((sqrt(y)/(1/((1+y)^(-1/2)))))))),y)/2),y,(x^2)),subs(-integrate((1/((1/((1-(y^2))^(-1/2)))*(e^-arcsin(sqrt((1-(y^2))))))),y),y,((1+(x^2))^(-1/2))))
try(subs((-integrate((1/((1/((1-y)^(-1/2)))*(1/(y^(-1/2)))*(e^-arcsin(sqrt((1-y)))))),y)/2),y,(1/(1+(x^2)))),subs((integrate((1/((1+y)*(1/(y^(-1/2)))*(e^-arcsin((sqrt(y)/(1/((1+y)^(-1/2)))))))),y)/2),y,(x^2)),subs(-integrate((1/((1/((1-y)^(-1/2)))*(1/((1+y)^(-1/2)))*(e^-arcsin((sqrt((1-y))*sqrt((1+y))))))),y),y,((1+(x^2))^(-1/2))))
try(subs((-integrate((1/((1/((1-y)^(-1/2)))*(1/(y^(-1/2)))*(e^-arcsin(sqrt((1-y)))))),y)/2),y,(1/(1+(x^2)))),subs((integrate((1/((1+y)*(1/(y^(-1/2)))*(e^-arcsin((sqrt(y)/(1/((1+y)^(-1/2)))))))),y)/2),y,(x^2)),subs(-integrate((1/((1/((1-y)^(-1/2)))*(1/((1+y)^(-1/2)))*(e^-arcsin((sqrt((1-y))*sqrt((1+y))))))),y),y,((1+(x^2))^(-1/2))))
try(subs(integrate(1,y),y,(e^arctan(x))),subs(integrate((1/(2*(1+y)*(1/(y^(-1/2)))*(e^-arctan(sqrt(y))))),y),y,(x^2)),subs(integrate((-1/(2*(1/((-1+(1/y))^(-1/2)))*(e^-arctan(sqrt((-1+(1/y)))))*y)),y),y,(1/(1+(x^2)))))
try(subs(y,y,(e^arctan(x))),subs((integrate((1/((1+y)*(1/(y^(-1/2)))*(e^-arctan(sqrt(y))))),y)/2),y,(x^2)),subs((-integrate((1/((1/((-1+(1/y))^(-1/2)))*(e^-arctan(sqrt((-1+(1/y)))))*y)),y)/2),y,(1/(1+(x^2)))))
=> e^arctan(x)

? integrate(sin(x)^2/(1+cos(x)),x)
thinking...
integrate(((sin(x)^2)/(1+cos(x))),x)
integrate(((1/(2*(1+cos(x))))+(-cos((2*x))/(2*(1+cos(x))))),x)
(integrate((1/(1+cos(x))),x)/2)+(-integrate((cos((2*x))/(1+cos(x))),x)/2)
integrate((1-cos(x)),x)
-sin(x)+x
=> -sin(x)+x

? integrate(tan(x)^3,x)
thinking...
integrate(((sin(x)/cos(x))^3),x)
integrate((((3*sin(x))/(4*(cos(x)^3)))+(-sin((3*x))/(4*(cos(x)^3)))),x)
((3*integrate((sin(x)/(cos(x)^3)),x))/4)+(-integrate((sin((3*x))/(cos(x)^3)),x)/4)
integrate(((sin(x)^3)/(cos(x)^3)),x)
integrate(((sin(x)^3)/(cos(x)^3)),x)
try(subs(integrate(((y^3)/((1-(y^2))^2)),y),y,sin(x)),subs(integrate(((-1+(y^2))/(y^3)),y),y,cos(x)),subs(integrate((sin((y^(1/3)))/(3*(cos((y^(1/3)))^4))),y),y,(sin(x)^3)))
try(subs(integrate(((y^3)/(((1-y)^2)*((1+y)^2))),y),y,sin(x)),subs(integrate((((-1+y)*(1+y))/(y^3)),y),y,cos(x)),subs((integrate((sin((y^(1/3)))/(cos((y^(1/3)))^4)),y)/3),y,(sin(x)^3)))
try(subs(integrate(((-1/(2*(1+y)))+(-1/(4*((1-y)^2)))+(1/(2*(1-y)))+(1/(4*((1+y)^2)))),y),y,sin(x)),subs(integrate((((-1+y)*(1+y))/(y^3)),y),y,cos(x)),subs((integrate((sin((y^(1/3)))/(cos((y^(1/3)))^4)),y)/3),y,(sin(x)^3)))
try(subs(((-1/(4*(1-y)))+(-1/(4*(1+y)))+(-log(abs((1-y)))/2)+(-log(abs((1+y)))/2)),y,sin(x)),subs(integrate((((-1+y)*(1+y))/(y^3)),y),y,cos(x)),subs((integrate((sin((y^(1/3)))/(cos((y^(1/3)))^4)),y)/3),y,(sin(x)^3)))
=> (-1/(2*(1-sin(x))*(1+sin(x))))+((log(abs((1-sin(x))))*(sin(x)^2))/(2*(1-sin(x))*(1+sin(x))))+((log(abs((1+sin(x))))*(sin(x)^2))/(2*(1-sin(x))*(1+sin(x))))+(-log(abs((1-sin(x))))/(2*(1-sin(x))*(1+sin(x))))+(-log(abs((1+sin(x))))/(2*(1-sin(x))*(1+sin(x))))

? integrate(cos(x)/(1+cos(x)),x)
thinking...
integrate((cos(x)/(1+cos(x))),x)
integrate(((((-1+(sin(x)^2))*(sin(x)^2))+(cos(x)*(sin(x)^2)))/(sin(x)^4)),x)
integrate((1+(-1/(sin(x)^2))+(cos(x)/(sin(x)^2))),x)
cot(x)+integrate((cos(x)/(sin(x)^2)),x)+x
cot(x)+try(subs(integrate((-sin((y^(-1/2)))/2),y),y,(1/(sin(x)^2))),subs(integrate((1/(y^2)),y),y,sin(x)),subs(integrate((-y/(1/((1-(y^2))^(-3/2)))),y),y,cos(x)))+x
cot(x)+try(subs((-integrate(sin((y^(-1/2))),y)/2),y,(1/(sin(x)^2))),subs((-1/y),y,sin(x)),subs(-integrate((y/(1/(((1-y)*(1+y))^(-3/2)))),y),y,cos(x)))+x
=> (-1/sin(x))+(cos(x)/sin(x))+x

? integrate(1/(1+sin(x)),x)
thinking...
integrate((1/(1+sin(x))),x)
integrate(((-((cos(x)^2)*sin(x))+(cos(x)^2))/(cos(x)^4)),x)
integrate(((1/(cos(x)^2))+(-sin(x)/(cos(x)^2))),x)
-integrate((sin(x)/(cos(x)^2)),x)+tan(x)
-try(subs(integrate((y/(1/((1-(y^2))^(-3/2)))),y),y,sin(x)),subs(integrate((-1/(y^2)),y),y,cos(x)),subs(integrate((cos((y^(-1/2)))/2),y),y,(1/(cos(x)^2))))+tan(x)
-try(subs(integrate((y/(1/(((1-y)*(1+y))^(-3/2)))),y),y,sin(x)),subs((1/y),y,cos(x)),subs((integrate(cos((y^(-1/2))),y)/2),y,(1/(cos(x)^2))))+tan(x)
=> (-1/cos(x))+(sin(x)/cos(x))

? integrate(cos(x)/(1+sin(x))^2,x)
thinking...
integrate((cos(x)/((1+sin(x))^2)),x)
integrate((cos(x)/((3/2)+(-cos((2*x))/2)+(2*sin(x)))),x)
integrate(((((cos(x)^6)*(sin(x)^2))-(2*(cos(x)^6)*sin(x))+(cos(x)^6))/(cos(x)^9)),x)
integrate(((1/(cos(x)^3))+(-(2*sin(x))/(cos(x)^3))+((sin(x)^2)/(cos(x)^3))),x)
integrate((1/(cos(x)^3)),x)+integrate(((sin(x)^2)/(cos(x)^3)),x)-(2*integrate((sin(x)/(cos(x)^3)),x))
-(2*try(subs(integrate((-1/(y^3)),y),y,cos(x)),subs(integrate((y/((1-(y^2))^2)),y),y,sin(x)),subs(integrate((cos((y^(-1/3)))/3),y),y,(1/(cos(x)^3)))))+try(subs(integrate((cos((y^(-1/3)))/(3*sin((y^(-1/3))))),y),y,(1/(cos(x)^3))),subs(integrate((-1/((1/((1-(y^2))^(-1/2)))*(y^3))),y),y,cos(x)),subs(integrate(sqrt((1+(y^2))),y),y,(sin(x)/cos(x))))+try(subs(integrate((-sqrt((1-(y^2)))/(y^3)),y),y,cos(x)),subs(integrate(((y^2)/((1-(y^2))^2)),y),y,sin(x)),subs(integrate((sin(sqrt(y))/(2*(cos(sqrt(y))^4))),y),y,(sin(x)^2)))
-(2*try(subs((1/(2*(y^2))),y,cos(x)),subs(integrate((y/(((1-y)^2)*((1+y)^2))),y),y,sin(x)),subs((integrate(cos((y^(-1/3))),y)/3),y,(1/(cos(x)^3)))))+try(subs((integrate((cos((y^(-1/3)))/sin((y^(-1/3)))),y)/3),y,(1/(cos(x)^3))),subs(-integrate((1/((1/((1-y)^(-1/2)))*(1/((1+y)^(-1/2)))*(y^3))),y),y,cos(x)),subs(integrate(sqrt((1+(y^2))),y),y,(sin(x)/cos(x))))+try(subs(-integrate(((sqrt((1-y))*sqrt((1+y)))/(y^3)),y),y,cos(x)),subs(integrate(((y^2)/(((1-y)^2)*((1+y)^2))),y),y,sin(x)),subs((integrate((sin(sqrt(y))/(cos(sqrt(y))^4)),y)/2),y,(sin(x)^2)))
-(2*try(subs((1/(2*(y^2))),y,cos(x)),subs(integrate(((-1/(4*((1-y)^2)))+(1/(4*((1+y)^2)))),y),y,sin(x)),subs((integrate(cos((y^(-1/3))),y)/3),y,(1/(cos(x)^3)))))+try(subs((integrate((cos((y^(-1/3)))/sin((y^(-1/3)))),y)/3),y,(1/(cos(x)^3))),subs(-integrate((1/((1/((1-y)^(-1/2)))*(1/((1+y)^(-1/2)))*(y^3))),y),y,cos(x)),subs(integrate(sqrt((1+(y^2))),y),y,(sin(x)/cos(x))))+try(subs(-integrate(((sqrt((1-y))*sqrt((1+y)))/(y^3)),y),y,cos(x)),subs(integrate(((-1/(4*((1-y)^2)))+(-1/(4*((1+y)^2)))+(1/(4*(1-y)))+(1/(4*(1+y)))),y),y,sin(x)),subs((integrate((sin(sqrt(y))/(cos(sqrt(y))^4)),y)/2),y,(sin(x)^2)))
-(2*try(subs((1/(2*(y^2))),y,cos(x)),subs(((-1/(4*(1-y)))+(-1/(4*(1+y)))),y,sin(x)),subs((integrate(cos((y^(-1/3))),y)/3),y,(1/(cos(x)^3)))))+try(subs((integrate((cos((y^(-1/3)))/sin((y^(-1/3)))),y)/3),y,(1/(cos(x)^3))),subs(-integrate((1/((1/((1-y)^(-1/2)))*(1/((1+y)^(-1/2)))*(y^3))),y),y,cos(x)),subs(integrate(sqrt((1+(y^2))),y),y,(sin(x)/cos(x))))+try(subs(-integrate(((sqrt((1-y))*sqrt((1+y)))/(y^3)),y),y,cos(x)),subs(((-1/(4*(1-y)))+(1/(4*(1+y)))+(log(abs((1+y)))/4)+(-log(abs((1-y)))/4)),y,sin(x)),subs((integrate((sin(sqrt(y))/(cos(sqrt(y))^4)),y)/2),y,(sin(x)^2)))
try(subs(integrate((1/(y^2)),y),y,(1+sin(x))),subs(integrate((1/((1+y)^2)),y),y,sin(x)),subs(integrate((-y/((1/((1-(y^2))^(-1/2)))*((1+sqrt((1-(y^2))))^2))),y),y,cos(x)))
try(subs((-1/y),y,(1+sin(x))),subs((-1/(1+y)),y,sin(x)),subs(-integrate((y/((1/((1-y)^(-1/2)))*(1/((1+y)^(-1/2)))*((1+(sqrt((1-y))*sqrt((1+y))))^2))),y),y,cos(x)))
=> -1/(1+sin(x))

? (x-1)^2 = x^2 - 1
thinking...
(1-(x^2)+((-1+x)^2))=0
(2-(2*x))=0
x∈{1}
=> x∈{1}

? (sin(x)+cosec(x))^2+(cos(x)+sec(x))^2=7+tan(x)^2+cot(x)^2
thinking...
(-7-(cot(x)^2)-(tan(x)^2)+((cos(x)+sec(x))^2)+((cosec(x)+sin(x))^2))=0
(-7-((cos(x)/sin(x))^2)-((sin(x)/cos(x))^2)+((cos(x)+(1/cos(x)))^2)+(((1/sin(x))+sin(x))^2))=0
0=0
true
=> true

? 2*x/(2*x^2+5*x+2)>1/(x+1)
thinking...
((-1/(1+x))+((2*x)/(2+(2*(x^2))+(5*x))))>0
~((((-1/(1+x))+((2*x)/(2+(2*(x^2))+(5*x))))=0)|(((-1/(1+x))+((2*x)/(2+(2*(x^2))+(5*x))))<0))
~(((-2-(3*x))=0)|(((-2-(3*x))/((1+x)*(2+(2*(x^2))+(5*x))))<0))
x∈(-2,-1)U(-2/3,-1/2)
=> x∈(-2,-1)U(-2/3,-1/2)

? (5*x-1)<(x+1)^2&(x+1)^2<7*x-3
thinking...
((-1+(5*x)+((-1-x)*(1+x)))<0)&((3-(7*x)+((1+x)^2))<0)
((-2+(3*x)-(x^2))<0)&((4-(5*x)+(x^2))<0)
x∈(2,4)
=> x∈(2,4)

? abs(x+5)*x+2*abs(x+7)-2=0
thinking...
(-2+(2*abs((7+x)))+(abs((5+x))*x))=0
(((5+x)<0)&((((-2+(2*(-7-x))+((-5-x)*x))=0)&((7+x)<0))|(((-2+(2*(7+x))+((-5-x)*x))=0)&(((7+x)=0)|~(((7+x)=0)|((7+x)<0))))))|(((((-2+(2*(-7-x))+((5+x)*x))=0)&((7+x)<0))|(((-2+(2*(7+x))+((5+x)*x))=0)&(((7+x)=0)|~(((7+x)=0)|((7+x)<0)))))&(((5+x)=0)|~(((5+x)=0)|((5+x)<0))))
(((5+x)<0)&((((-16-(7*x)-(x^2))=0)&((7+x)<0))|(((12-(3*x)-(x^2))=0)&(((7+x)=0)|~(((7+x)=0)|((7+x)<0))))))|(((((-16+(3*x)+(x^2))=0)&((7+x)<0))|(((12+(7*x)+(x^2))=0)&(((7+x)=0)|~(((7+x)=0)|((7+x)<0)))))&(((5+x)=0)|~(((5+x)=0)|((5+x)<0))))
x∈{-4,(-3/2)+(-sqrt(57)/2),-3}
x∈{-4,(-6-(2*sqrt(57)))/4,-3}
=> x∈{-4,(-6-(2*sqrt(57)))/4,-3}

? x*abs(x)-5*abs(x+2)+6=0
thinking...
(6+(abs(x)*x)-(5*abs((2+x))))=0
((x<0)&((((6+(5*(-2-x))-(x^2))=0)&(((2+x)=0)|~(((2+x)=0)|((2+x)<0))))|(((6+(5*(2+x))-(x^2))=0)&((2+x)<0))))|(((((6+(5*(-2-x))+(x^2))=0)&(((2+x)=0)|~(((2+x)=0)|((2+x)<0))))|(((6+(5*(2+x))+(x^2))=0)&((2+x)<0)))&((x=0)|~((x=0)|(x<0))))
((x<0)&((((-4-(5*x)-(x^2))=0)&(((2+x)=0)|~(((2+x)=0)|((2+x)<0))))|(((16+(5*x)-(x^2))=0)&((2+x)<0))))|(((((-4-(5*x)+(x^2))=0)&(((2+x)=0)|~(((2+x)=0)|((2+x)<0))))|(((16+(5*x)+(x^2))=0)&((2+x)<0)))&((x=0)|~((x=0)|(x<0))))
x∈{-1,(5/2)+(-sqrt(89)/2),(5/2)+(sqrt(41)/2)}
x∈{-1,(10-(2*sqrt(89)))/4,(10+(2*sqrt(41)))/4}
=> x∈{-1,(10-(2*sqrt(89)))/4,(10+(2*sqrt(41)))/4}

? abs(3*x-5)+abs(8-x)=abs(3+2*x)
thinking...
(abs((-5+(3*x)))+abs((8-x))-abs((3+(2*x))))=0
(((3+(2*x))<0)&((((8-x)<0)&(((0=0)&((-5+(3*x))<0))|(((-10+(6*x))=0)&(((-5+(3*x))=0)|~(((-5+(3*x))=0)|((-5+(3*x))<0))))))|(((((16-(2*x))=0)&((-5+(3*x))<0))|(((6+(4*x))=0)&(((-5+(3*x))=0)|~(((-5+(3*x))=0)|((-5+(3*x))<0)))))&(((8-x)=0)|~(((8-x)=0)|((8-x)<0))))))|(((((8-x)<0)&((((-16+(2*x))=0)&(((-5+(3*x))=0)|~(((-5+(3*x))=0)|((-5+(3*x))<0))))|(((-6-(4*x))=0)&((-5+(3*x))<0))))|((((0=0)&(((-5+(3*x))=0)|~(((-5+(3*x))=0)|((-5+(3*x))<0))))|(((10-(6*x))=0)&((-5+(3*x))<0)))&(((8-x)=0)|~(((8-x)=0)|((8-x)<0)))))&(((3+(2*x))=0)|~(((3+(2*x))=0)|((3+(2*x))<0))))
(((3+(2*x))<0)&((((8-x)<0)&(((0=0)&((-5+(3*x))<0))|(((-10+(6*x))=0)&(((-5+(3*x))=0)|~(((-5+(3*x))=0)|((-5+(3*x))<0))))))|(((((16-(2*x))=0)&((-5+(3*x))<0))|(((6+(4*x))=0)&(((-5+(3*x))=0)|~(((-5+(3*x))=0)|((-5+(3*x))<0)))))&(((8-x)=0)|~(((8-x)=0)|((8-x)<0))))))|(((((8-x)<0)&((((-16+(2*x))=0)&(((-5+(3*x))=0)|~(((-5+(3*x))=0)|((-5+(3*x))<0))))|(((-6-(4*x))=0)&((-5+(3*x))<0))))|((((0=0)&(((-5+(3*x))=0)|~(((-5+(3*x))=0)|((-5+(3*x))<0))))|(((10-(6*x))=0)&((-5+(3*x))<0)))&(((8-x)=0)|~(((8-x)=0)|((8-x)<0)))))&(((3+(2*x))=0)|~(((3+(2*x))=0)|((3+(2*x))<0))))
(((3+(2*x))<0)&((((8-x)<0)&((((-10+(6*x))=0)&(((-5+(3*x))=0)|~(((-5+(3*x))=0)|((-5+(3*x))<0))))|((-5+(3*x))<0)))|(((((16-(2*x))=0)&((-5+(3*x))<0))|(((6+(4*x))=0)&(((-5+(3*x))=0)|~(((-5+(3*x))=0)|((-5+(3*x))<0)))))&(((8-x)=0)|~(((8-x)=0)|((8-x)<0))))))|(((((8-x)<0)&((((-16+(2*x))=0)&(((-5+(3*x))=0)|~(((-5+(3*x))=0)|((-5+(3*x))<0))))|(((-6-(4*x))=0)&((-5+(3*x))<0))))|(((((10-(6*x))=0)&((-5+(3*x))<0))|((-5+(3*x))=0)|~(((-5+(3*x))=0)|((-5+(3*x))<0)))&(((8-x)=0)|~(((8-x)=0)|((8-x)<0)))))&(((3+(2*x))=0)|~(((3+(2*x))=0)|((3+(2*x))<0))))
x∈(5/3,8)U{8,5/3}
=> x∈(5/3,8)U{8,5/3}

? abs(x^2+5*x+9)<abs(x^2+2*x+2)+abs(3*x+7)
thinking...
(abs((9+(5*x)+(x^2)))-abs((2+(2*x)+(x^2)))-abs((7+(3*x))))<0
(((7+(3*x))<0)&((((2+(2*x)+(x^2))<0)&(((0<0)&((9+(5*x)+(x^2))<0))|(((18+(10*x)+(2*(x^2)))<0)&(((9+(5*x)+(x^2))=0)|~(((9+(5*x)+(x^2))=0)|((9+(5*x)+(x^2))<0))))))|(((((-4-(2*(x^2))-(4*x))<0)&((9+(5*x)+(x^2))<0))|(((14+(6*x))<0)&(((9+(5*x)+(x^2))=0)|~(((9+(5*x)+(x^2))=0)|((9+(5*x)+(x^2))<0)))))&(((2+(2*x)+(x^2))=0)|~(((2+(2*x)+(x^2))=0)|((2+(2*x)+(x^2))<0))))))|(((((2+(2*x)+(x^2))<0)&((((-14-(6*x))<0)&((9+(5*x)+(x^2))<0))|(((4+(2*(x^2))+(4*x))<0)&(((9+(5*x)+(x^2))=0)|~(((9+(5*x)+(x^2))=0)|((9+(5*x)+(x^2))<0))))))|((((0<0)&(((9+(5*x)+(x^2))=0)|~(((9+(5*x)+(x^2))=0)|((9+(5*x)+(x^2))<0))))|(((-18-(10*x)-(2*(x^2)))<0)&((9+(5*x)+(x^2))<0)))&(((2+(2*x)+(x^2))=0)|~(((2+(2*x)+(x^2))=0)|((2+(2*x)+(x^2))<0)))))&(((7+(3*x))=0)|~(((7+(3*x))=0)|((7+(3*x))<0))))
(((7+(3*x))<0)&((((2+(2*x)+(x^2))<0)&(((0<0)&((9+(5*x)+(x^2))<0))|(((18+(10*x)+(2*(x^2)))<0)&(((9+(5*x)+(x^2))=0)|~(((9+(5*x)+(x^2))=0)|((9+(5*x)+(x^2))<0))))))|(((((-4-(2*(x^2))-(4*x))<0)&((9+(5*x)+(x^2))<0))|(((14+(6*x))<0)&(((9+(5*x)+(x^2))=0)|~(((9+(5*x)+(x^2))=0)|((9+(5*x)+(x^2))<0)))))&(((2+(2*x)+(x^2))=0)|~(((2+(2*x)+(x^2))=0)|((2+(2*x)+(x^2))<0))))))|(((((2+(2*x)+(x^2))<0)&((((-14-(6*x))<0)&((9+(5*x)+(x^2))<0))|(((4+(2*(x^2))+(4*x))<0)&(((9+(5*x)+(x^2))=0)|~(((9+(5*x)+(x^2))=0)|((9+(5*x)+(x^2))<0))))))|((((0<0)&(((9+(5*x)+(x^2))=0)|~(((9+(5*x)+(x^2))=0)|((9+(5*x)+(x^2))<0))))|(((-18-(10*x)-(2*(x^2)))<0)&((9+(5*x)+(x^2))<0)))&(((2+(2*x)+(x^2))=0)|~(((2+(2*x)+(x^2))=0)|((2+(2*x)+(x^2))<0)))))&(((7+(3*x))=0)|~(((7+(3*x))=0)|((7+(3*x))<0))))
(((7+(3*x))<0)&((((18+(10*x)+(2*(x^2)))<0)&((2+(2*x)+(x^2))<0)&(((9+(5*x)+(x^2))=0)|~(((9+(5*x)+(x^2))=0)|((9+(5*x)+(x^2))<0))))|(((((-4-(2*(x^2))-(4*x))<0)&((9+(5*x)+(x^2))<0))|(((14+(6*x))<0)&(((9+(5*x)+(x^2))=0)|~(((9+(5*x)+(x^2))=0)|((9+(5*x)+(x^2))<0)))))&(((2+(2*x)+(x^2))=0)|~(((2+(2*x)+(x^2))=0)|((2+(2*x)+(x^2))<0))))))|(((((-18-(10*x)-(2*(x^2)))<0)&((9+(5*x)+(x^2))<0)&(((2+(2*x)+(x^2))=0)|~(((2+(2*x)+(x^2))=0)|((2+(2*x)+(x^2))<0))))|(((2+(2*x)+(x^2))<0)&((((-14-(6*x))<0)&((9+(5*x)+(x^2))<0))|(((4+(2*(x^2))+(4*x))<0)&(((9+(5*x)+(x^2))=0)|~(((9+(5*x)+(x^2))=0)|((9+(5*x)+(x^2))<0)))))))&(((7+(3*x))=0)|~(((7+(3*x))=0)|((7+(3*x))<0))))
x∈(-inf,-7/3)
=> x∈(-inf,-7/3)

? (A-B)|(B-A) <-> (A|B)-(A&B)
thinking...
=> true

? (cosec(x)-cot(x))^2=(1-cos(x))/(1+cos(x))
thinking...
(((-1+cos(x))/(1+cos(x)))+((cosec(x)-cot(x))^2))=0
(((-1+cos(x))/(1+cos(x)))+(((1/sin(x))+(-cos(x)/sin(x)))^2))=0
0=0
true
=> true

? x^2 = 4 & x+y^2 = 1
thinking...
((-1+(y^2)+x)=0)&((-4+(x^2))=0)
(((-2+x)=0)&((1+(y^2))=0))|(((2+x)=0)&((-sqrt(3)+y)=0))
(x∈{-2}&y∈{sqrt(12)/2})|x∈{}
=> (x∈{-2}&y∈{sqrt(12)/2})|x∈{}

? x + y*x = 5 & y + z=5 & z = 4
thinking...
((-4+z)=0)&((-5+(x*y)+x)=0)&((-5+y+z)=0)
((-1+y)=0)&((-4+z)=0)&((-5+(x*y)+x)=0)
((-1+y)=0)&((-5+(2*x))=0)&z∈{4}
x∈{5/2}&y∈{1}&z∈{4}
=> x∈{5/2}&y∈{1}&z∈{4}

? integrate(abs(x+1),x,-4,10)
thinking...
-subs((((2*x)+(x^2))/2),x,-1)-subs(((-(2*x)-(x^2))/2),x,-4)+subs((((2*x)+(x^2))/2),x,10)+subs(((-(2*x)-(x^2))/2),x,-1)
=> 65

? integrate(abs(sin(x)),x,-pi,pi/6)
thinking...
-subs(cos(x),x,-pi)-subs(-cos(x),x,0)+subs(cos(x),x,0)+subs(-cos(x),x,(pi/6))
=> 3+(-sqrt(3)/2)

? x^(2*x)=1
thinking...
(-1+(x^(2*x)))=0
(((1+x)=0)&(((2*x)%2)=0))|((x=0)&~(x=0))|((-1+x)=0)
(((1+x)=0)&(((2*x)%2)=0))|((x=0)&~(x=0))|((-1+x)=0)
((1+x)=0)|x∈{1}
x∈{-1,1}
=> x∈{-1,1}

? -i*(i+1)^5
thinking...
=> -4+(4*i)

? sqrt(x) = x-2
thinking...
(2-x+sqrt(x))=0
x∈{4}
=> x∈{4}

? integrate(sin(x+a)/sin(x),x)
thinking...
integrate((((cos(x)*sin(a))+(cos(a)*sin(x)))/sin(x)),x)
integrate(((sin((-x+a))/(2*sin(x)))+(sin((-a+x))/(2*sin(x)))+(sin((x+a))/sin(x))),x)
(integrate((((cos(-x)*sin(a))+(cos(a)*sin(-x)))/sin(x)),x)/2)+(integrate((((cos(-a)*sin(x))+(cos(x)*sin(-a)))/sin(x)),x)/2)+integrate((((cos(x)*sin(a))+(cos(a)*sin(x)))/sin(x)),x)
integrate((cos(a)+((cos(x)*sin(a))/sin(x))),x)
(cos(a)*x)+(integrate((cos(x)/sin(x)),x)*sin(a))
(cos(a)*x)+(sin(a)*try(subs(integrate((-y/(1-(y^2))),y),y,cos(x)),subs(integrate((1/y),y),y,sin(x)),subs(integrate(-sin((1/y)),y),y,(1/sin(x)))))
(cos(a)*x)+(sin(a)*try(subs((log(abs((-1+(y^2))))/2),y,cos(x)),subs(log(abs(y)),y,sin(x)),subs(-integrate(sin((1/y)),y),y,(1/sin(x)))))
=> ((log(abs((-1+(cos(x)^2))))*sin(a))/2)+(cos(a)*x)

? integrate(sqrt(sin(2*x))*cos(2*x),x)
thinking...
integrate((cos((2*x))*sqrt(sin((2*x)))),x)
integrate((((2*sqrt(2)*sqrt(sin(x)))/(1/(cos(x)^(5/2))))-(sqrt(2)*sqrt(cos(x))*sqrt(sin(x)))),x)
(2*integrate((sqrt(sin(x))/(1/(cos(x)^(5/2)))),x)*sqrt(2))-(integrate((sqrt(cos(x))*sqrt(sin(x))),x)*sqrt(2))
(2*sqrt(2)*try(subs(integrate((sqrt(y)/(1/((1-(y^2))^(3/4)))),y),y,sin(x)),subs(integrate((-1/((1/((1-(y^2))^(-1/4)))*(1/(y^(5/2))))),y),y,cos(x)),subs(integrate(((2*sin((y^2)))/(1/(cos((y^2))^(3/2)))),y),y,sqrt(sin(x)))))-(sqrt(2)*try(subs(integrate((-sqrt(y)/(1/((1-(y^2))^(-1/4)))),y),y,cos(x)),subs(integrate((sqrt(y)/(1/((1-(y^2))^(-1/4)))),y),y,sin(x)),subs(integrate(((2*sin((y^2)))/(1/(cos((y^2))^(-1/2)))),y),y,sqrt(sin(x)))))
(2*sqrt(2)*try(subs(integrate((sqrt(y)/(1/(((1-y)*(1+y))^(3/4)))),y),y,sin(x)),subs(-integrate((1/((1/(((1-y)*(1+y))^(-1/4)))*(1/(y^(5/2))))),y),y,cos(x)),subs((2*integrate((sin((y^2))/(1/(cos((y^2))^(3/2)))),y)),y,sqrt(sin(x)))))-(sqrt(2)*try(subs(-integrate((sqrt(y)/(1/(((1-y)*(1+y))^(-1/4)))),y),y,cos(x)),subs(integrate((sqrt(y)/(1/(((1-y)*(1+y))^(-1/4)))),y),y,sin(x)),subs((2*integrate((sin((y^2))/(1/(cos((y^2))^(-1/2)))),y)),y,sqrt(sin(x)))))
(2*sqrt(2)*try(subs(integrate((sqrt(y)/(1/(((1-y)*(1+y))^(3/4)))),y),y,sin(x)),subs(-integrate((1/((1/(((1-y)*(1+y))^(-1/4)))*(1/(y^(5/2))))),y),y,cos(x)),subs((2*integrate((sin((y^2))/(1/(cos((y^2))^(3/2)))),y)),y,sqrt(sin(x)))))-(sqrt(2)*try(subs(-integrate((sqrt(y)/(1/(((1-y)*(1+y))^(-1/4)))),y),y,cos(x)),subs(integrate((sqrt(y)/(1/(((1-y)*(1+y))^(-1/4)))),y),y,sin(x)),subs((2*integrate((sin((y^2))/(1/(cos((y^2))^(-1/2)))),y)),y,sqrt(sin(x)))))
try(subs(integrate((sqrt(y)/2),y),y,sin((2*x))),subs(integrate(((cos(y)*sqrt(sin(y)))/2),y),y,(2*x)),subs(integrate((-y/(2*(1/((1-(y^2))^(-1/4))))),y),y,cos((2*x))))
try(subs((1/(3*(1/(y^(3/2))))),y,sin((2*x))),subs((integrate((cos(y)*sqrt(sin(y))),y)/2),y,(2*x)),subs((-integrate((y/(1/(((1-y)*(1+y))^(-1/4)))),y)/2),y,cos((2*x))))
=> 1/(3*(1/(sin((2*x))^(3/2))))

? x = y & y = z & x+y+z=180
thinking...
((-180+x+y+z)=0)&((-y+x)=0)&((-z+y)=0)
((-60+x)=0)&((-60+y)=0)&((-60+z)=0)
x∈{60}&y∈{60}&z∈{60}
=> x∈{60}&y∈{60}&z∈{60}

? sec(x)^2*tan(y)+sec(y)^2*tan(x)*dif(y,x)=0
thinking...
(-integrate((1/(cos(x)*sin(x))),x)-integrate((1/(cos(y)*sin(y))),y)+c1)=0
(-integrate((2/sin((2*x))),x)-integrate((2/sin((2*y))),y)+c1)=0
(-log(abs(tan(x)))-log(abs(tan(y)))+c1)=0
=> (-log(abs((sin(x)/cos(x))))-log(abs((sin(y)/cos(y))))+c1)=0

? x + y = 10 & x*y = 24
thinking...
((-10+x+y)=0)&((-24+(x*y))=0)
(((-10+x+y)=0)&((-4+x)=0))|(((-10+x+y)=0)&((-4+x)=0)&((-4+y)=0))|(((-10+x+y)=0)&((-4+x)=0)&((-4+y)=0)&((6-x)=0))|(((-10+x+y)=0)&((-4+x)=0)&((-4+y)=0)&((6-y)=0))|(((-10+x+y)=0)&((-4+x)=0)&((6-x)=0))|(((-10+x+y)=0)&((-4+x)=0)&((6-x)=0)&((6-y)=0))|(((-10+x+y)=0)&((-4+x)=0)&((6-y)=0))|(((-10+x+y)=0)&((-4+y)=0))|(((-10+x+y)=0)&((-4+y)=0)&((6-x)=0))|(((-10+x+y)=0)&((-4+y)=0)&((6-x)=0)&((6-y)=0))|(((-10+x+y)=0)&((-4+y)=0)&((6-y)=0))|(((-10+x+y)=0)&((6-x)=0))|(((-10+x+y)=0)&((6-x)=0)&((6-y)=0))|(((-10+x+y)=0)&((6-y)=0))
(((-10+x+y)=0)&x∈{})|(((-10+x+y)=0)&y∈{})|(((-4+x)=0)&((-6+y)=0))|(((-4+x)=0)&((-6+y)=0)&x∈{4})|(((-4+x)=0)&((-6+y)=0)&x∈{6})|(((-4+x)=0)&((-6+y)=0)&x∈{})|(((-4+x)=0)&((-6+y)=0)&y∈{})|(((-4+y)=0)&((-6+x)=0))|(((-4+y)=0)&((-6+x)=0)&x∈{4})|(((-4+y)=0)&((-6+x)=0)&x∈{6})|(((-4+y)=0)&((-6+x)=0)&x∈{})|(((-4+y)=0)&((-6+x)=0)&y∈{})
(x∈{4}&y∈{6})|(x∈{6}&y∈{4})|(x∈{}&y∈{4})|(x∈{}&y∈{6})|x∈{}
(x∈{4}&y∈{6})|(x∈{6}&y∈{4})|x∈{}
=> (x∈{4}&y∈{6})|(x∈{6}&y∈{4})|x∈{}

? (x+y)*dif(y,x)=1
thinking...
((x/(e^y))-integrate((y/(e^y)),y)-c1)=0
((x/(e^y))-try(subs(integrate((z/(e^-z)),z),z,-y),subs(integrate(log(z),z),z,(e^-y)))-c1)=0
((x/(e^y))-try(subs(((integrate((e^z),z)*z)-integrate(integrate((e^z),z),z)),z,-y),subs(try(((integrate(1,z)*log(z))-integrate((integrate(1,z)/z),z)),(integrate(log(z),z)-integrate(0,z))),z,(e^-y)))-c1)=0
((x/(e^y))-try(subs(((-1/(e^-z))+(z/(e^-z))),z,-y),subs(try(((log(z)*z)-z),integrate(log(z),z)),z,(e^-y)))-c1)=0
=> ((x/(e^y))+(y/(e^y))-c1+(e^-y))=0

? abs(abs(x-2)-3)<=2
thinking...
(-2+abs((-3+abs((-2+x)))))<=0
(((-2+x)<0)&((((-1-x)<0)&(((-1+x)=0)|((-1+x)<0)))|((((-1-x)=0)|~(((-1-x)=0)|((-1-x)<0)))&(((-3-x)=0)|((-3-x)<0)))))|(((((-5+x)<0)&(((3-x)=0)|((3-x)<0)))|((((-5+x)=0)|~(((-5+x)=0)|((-5+x)<0)))&(((-7+x)=0)|((-7+x)<0))))&(((-2+x)=0)|~(((-2+x)=0)|((-2+x)<0))))
(((-2+x)<0)&((((-1-x)<0)&(((-1+x)=0)|((-1+x)<0)))|((((-1-x)=0)|~(((-1-x)=0)|((-1-x)<0)))&(((-3-x)=0)|((-3-x)<0)))))|(((((-5+x)<0)&(((3-x)=0)|((3-x)<0)))|((((-5+x)=0)|~(((-5+x)=0)|((-5+x)<0)))&(((-7+x)=0)|((-7+x)<0))))&(((-2+x)=0)|~(((-2+x)=0)|((-2+x)<0))))
x∈(-3,1)U(3,7)U{1,7,3,-3}
=> x∈(-3,1)U(3,7)U{1,7,3,-3}

? abs(x)>=0
thinking...
((x<0)&((x=0)|~((x=0)|(x>0))))|(x=0)|~((x=0)|(x<0))
((x<0)&((x=0)|~((x=0)|(x>0))))|(x=0)|~((x=0)|(x<0))
((x<0)&((x=0)|~((x=0)|~(x<=0))))|(x=0)|~((x=0)|(x<0))
true
=> true

? dif(y,x)=arcsin(x)
thinking...
(integrate(arcsin(x),x)-y+c1)=0
(-y+try(((arcsin(x)*integrate(1,x))-integrate((integrate(1,x)/(1/((1-(x^2))^(-1/2)))),x)),(integrate(arcsin(x),x)-integrate(0,x)))+c1)=0
(-y+try(((arcsin(x)*x)+sqrt((1-(x^2)))),integrate(arcsin(x),x))+c1)=0
=> ((arcsin(x)*x)-y+sqrt((1-(x^2)))+c1)=0

? integrate(sin(x)^6+cos(x)^6+3*sin(x)^2*cos(x)^2,x)
thinking...
integrate((cos(x)^6),x)+integrate((sin(x)^6),x)+(3*integrate(((cos(x)^2)*(sin(x)^2)),x))
integrate(((5/16)+(cos((6*x))/32)+((15*cos((2*x)))/32)+((3*cos((4*x)))/16)),x)+integrate(((5/16)+((3*cos((4*x)))/16)+(-cos((6*x))/32)+(-(15*cos((2*x)))/32)),x)+(3*integrate(((1/8)+(-cos((4*x))/8)),x))
((3*sin((4*x)))/32)+((5*x)/8)+(3*((-sin((4*x))/32)+(x/8)))
=> x

? integrate((x^4+x^2+1)/(x^2-x+1),x)
thinking...
integrate(((1+(x^2)+(x^4))/(1-x+(x^2))),x)
integrate((1+(x^2)+x),x)
((2*(x^3))+(3*(x^2))+(6*x))/6
=> ((x^2)/2)+((x^3)/3)+x

? integrate(1/(sin(x)^2*cos(x)^2),x)
thinking...
integrate((1/((cos(x)^2)*(sin(x)^2))),x)
integrate((4/((1+cos((2*x)))*(1-cos((2*x))))),x)
4*integrate((1/((1+cos((2*x)))*(1-cos((2*x))))),x)
integrate(((1/(cos(x)^2))+(1/(sin(x)^2))),x)
-cot(x)+tan(x)
=> (-cos(x)/sin(x))+(sin(x)/cos(x))

? integrate(x/sqrt(x+4),x)
thinking...
integrate((x/(1/((4+x)^(-1/2)))),x)
try(subs(integrate(((-4+y)/(1/(y^(-1/2)))),y),y,(4+x)),subs(integrate(((2*(4+(-1/(y^2))))/(y^2)),y),y,((4+x)^(-1/2))))
try(subs(integrate(((-4+y)/(1/(y^(-1/2)))),y),y,(4+x)),subs((2*integrate(((-1+(4*(y^2)))/(y^4)),y)),y,((4+x)^(-1/2))))
try(subs(integrate(((-4+y)/(1/(y^(-1/2)))),y),y,(4+x)),subs((2*integrate(((4*((-1/2)+y)*((1/2)+y))/(y^4)),y)),y,((4+x)^(-1/2))))
try(subs(integrate(((-4+y)/(1/(y^(-1/2)))),y),y,(4+x)),subs((8*integrate(((((-1/2)+y)*((1/2)+y))/(y^4)),y)),y,((4+x)^(-1/2))))
try(subs(integrate(((-4+y)/(1/(y^(-1/2)))),y),y,(4+x)),subs((2*integrate(((4+(-1/(y^2)))/(y^2)),y)),y,((4+x)^(-1/2))))
try(subs(integrate(((-4/(1/(y^(-1/2))))+sqrt(y)),y),y,(4+x)),subs((2*integrate(((-1/(y^4))+(4/(y^2))),y)),y,((4+x)^(-1/2))))
try(subs(((2*(-(12*sqrt(y))+(y^(3/2))))/3),y,(4+x)),subs((2*integrate(((-1+(4*(y^2)))/(y^4)),y)),y,((4+x)^(-1/2))))
=> (2/(3*(1/((4+x)^(3/2)))))-(8*sqrt((4+x)))

? integrate(sin(x)^4,x)
thinking...
integrate((sin(x)^4),x)
integrate(((3/8)+(cos((4*x))/8)+(-cos((2*x))/2)),x)
((3*x)/8)+(-sin((2*x))/4)+(sin((4*x))/32)
=> ((3*x)/8)+(-sin((2*x))/4)+(sin((4*x))/32)

? integrate(2*x/(1+x^2),x)
thinking...
log(abs((1+(x^2))))
=> log(abs((1+(x^2))))

? integrate(sin(2*x+5)^2,x)
thinking...
integrate((((cos(5)*sin((2*x)))+(cos((2*x))*sin(5)))^2),x)
integrate((((cos(5)*sin((2*x)))+(cos((2*x))*sin(5)))^2),x)
integrate(((1/2)+(cos((-10+(4*x)))/8)+(-cos((10+(4*x)))/2)+(-cos((10-(4*x)))/8)),x)
((((cos(-10)*sin((4*x)))/4)+((cos((4*x))*sin(-10))/4))/8)+((((cos(10)*sin(-(4*x)))/4)+((cos(-(4*x))*sin(10))/4))/8)+(((-(cos(10)*sin((4*x)))/4)+(-(cos((4*x))*sin(10))/4))/2)+(x/2)
=> (-(cos(10)*sin((4*x)))/8)+(-(cos((4*x))*sin(10))/8)+(x/2)

? integrate(sqrt(a*x+b),x)
thinking...
2/(3*(1/(((x*a)+b)^(3/2)))*a)
=> 2/(3*(1/(((x*a)+b)^(3/2)))*a)

? integrate(x*sqrt(x),x)
thinking...
2/(5*(1/(x^(5/2))))
=> 2/(5*(1/(x^(5/2))))

? integrate(x*sqrt(1+2*x^2),x)
thinking...
integrate((sqrt((1+(2*(x^2))))*x),x)
integrate((sqrt((1+(2*(x^2))))*x),x)
try(subs(integrate(((1+(2*((sqrt((-1+(y^2)))/(2^-(-1/2)))^2)))/2),y),y,sqrt((1+(2*(x^2))))),subs(integrate((sqrt((1+(2*y)))/2),y),y,(x^2)))
try(subs(((integrate(((-1+y)*(1+y)),y)+y)/2),y,sqrt((1+(2*(x^2))))),subs((1/(6*(1/((1+(2*y))^(3/2))))),y,(x^2)))
=> 1/(6*(1/((1+(2*(x^2)))^(3/2))))

? integrate(e^(2*x+3),x)
thinking...
1/(2*(e^(-3-(2*x))))
=> 1/(2*(e^(-3-(2*x))))

? integrate(x/e^(x^2),x)
thinking...
integrate((x/(e^(x^2))),x)
integrate((x/(e^(x^2))),x)
try(subs(integrate((1/(2*(e^y))),y),y,(x^2)),subs(integrate((-1/2),y),y,(e^-(x^2))))
try(subs((-1/(2*(e^y))),y,(x^2)),subs((-y/2),y,(e^-(x^2))))
=> -1/(2*(e^(x^2)))

? integrate(sin(x)*sin(cos(x)),x)
thinking...
integrate((sin(cos(x))*sin(x)),x)
integrate(((cos((cos(x)-x))/2)+(-cos((cos(x)+x))/2)),x)
((integrate((cos(cos(x))*cos(-x)),x)-integrate((sin(cos(x))*sin(-x)),x))/2)+((integrate((sin(cos(x))*sin(x)),x)-integrate((cos(cos(x))*cos(x)),x))/2)
try(subs(integrate((-sin(sqrt((1-(y^2))))/cos(sqrt((1-(y^2))))),y),y,sin(cos(x))),subs(integrate(((sin(sqrt((1-(y^2))))*y)/(1/((1-(y^2))^(-1/2)))),y),y,sin(x)),subs(integrate(-sin(y),y),y,cos(x)))
try(subs(-integrate((sin((sqrt((1-y))*sqrt((1+y))))/cos((sqrt((1-y))*sqrt((1+y))))),y),y,sin(cos(x))),subs(integrate(((sin((sqrt((1-y))*sqrt((1+y))))*y)/((1/((1-y)^(-1/2)))*(1/((1+y)^(-1/2))))),y),y,sin(x)),subs(cos(y),y,cos(x)))
=> cos(cos(x))

? integrate(sin(3*x)*cos(4*x),x)
thinking...
integrate((cos((4*x))*sin((3*x))),x)
integrate(((-sin(x)/2)+(sin((7*x))/2)),x)
(cos(x)/2)+(-cos((7*x))/14)
=> (cos(x)/2)+(-cos((7*x))/14)

? integrate(cos(2*x)*cos(4*x)*cos(6*x),x)
thinking...
integrate((cos((2*x))*cos((4*x))*cos((6*x))),x)
integrate(((1/4)+(cos((12*x))/4)+(cos((4*x))/4)+(cos((8*x))/4)),x)
(sin((12*x))/48)+(sin((4*x))/16)+(sin((8*x))/32)+(x/4)
=> (sin((12*x))/48)+(sin((4*x))/16)+(sin((8*x))/32)+(x/4)

? integrate(sin(2*x+1)^3,x)
thinking...
integrate((((cos(1)*sin((2*x)))+(cos((2*x))*sin(1)))^3),x)
integrate((((cos(1)*sin((2*x)))+(cos((2*x))*sin(1)))^3),x)
integrate((((25*sin((-1+(2*x))))/32)+((25*sin((1-(2*x))))/32)+((3*sin((-1+(6*x))))/16)+((3*sin((1-(6*x))))/16)+(-(3*sin((-1-(6*x))))/8)+(-(3*sin((-3+(2*x))))/16)+(-(3*sin((-3-(2*x))))/8)+(-(3*sin((1+(6*x))))/8)+(-(3*sin((3+(2*x))))/8)+(-(3*sin((3-(2*x))))/16)+(-sin((-1-(2*x)))/4)+(-sin((-3+(6*x)))/32)+(-sin((3+(6*x)))/4)+(-sin((3-(6*x)))/32)+(sin((1+(2*x)))/2)),x)
((((cos(-3)*cos((6*x)))/6)+(-(sin(-3)*sin((6*x)))/6))/32)+((((cos(3)*cos((6*x)))/6)+(-(sin(3)*sin((6*x)))/6))/4)+((((sin(-1)*sin(-(2*x)))/2)+(-(cos(-1)*cos(-(2*x)))/2))/4)+((((sin(1)*sin((2*x)))/2)+(-(cos(1)*cos((2*x)))/2))/2)+((((sin(3)*sin(-(6*x)))/6)+(-(cos(3)*cos(-(6*x)))/6))/32)+((25*(((cos(1)*cos(-(2*x)))/2)+(-(sin(1)*sin(-(2*x)))/2)))/32)+((25*(((sin(-1)*sin((2*x)))/2)+(-(cos(-1)*cos((2*x)))/2)))/32)+((3*(((cos(-3)*cos((2*x)))/2)+(-(sin(-3)*sin((2*x)))/2)))/16)+((3*(((cos(1)*cos((6*x)))/6)+(-(sin(1)*sin((6*x)))/6)))/8)+((3*(((cos(1)*cos(-(6*x)))/6)+(-(sin(1)*sin(-(6*x)))/6)))/16)+((3*(((cos(3)*cos((2*x)))/2)+(-(sin(3)*sin((2*x)))/2)))/8)+((3*(((sin(-1)*sin((6*x)))/6)+(-(cos(-1)*cos((6*x)))/6)))/16)+((3*(((sin(-1)*sin(-(6*x)))/6)+(-(cos(-1)*cos(-(6*x)))/6)))/8)+((3*(((sin(-3)*sin(-(2*x)))/2)+(-(cos(-3)*cos(-(2*x)))/2)))/8)+((3*(((sin(3)*sin(-(2*x)))/2)+(-(cos(3)*cos(-(2*x)))/2)))/16)
=> ((3*sin(1)*sin((2*x)))/8)+((cos(3)*cos((6*x)))/24)+(-(3*cos(1)*cos((2*x)))/8)+(-(sin(3)*sin((6*x)))/24)

? integrate(sin(x)^3*cos(x)^3,x)
thinking...
integrate(((cos(x)^3)*(sin(x)^3)),x)
integrate((((3*sin((2*x)))/32)+(-sin((6*x))/32)),x)
(cos((6*x))/192)+(-(3*cos((2*x)))/64)
=> (cos((6*x))/192)+(-(3*cos((2*x)))/64)

? integrate(sin(x)*sin(2*x)*sin(3*x),x)
thinking...
integrate((sin((2*x))*sin((3*x))*sin(x)),x)
integrate(((-sin((6*x))/4)+(sin((2*x))/4)+(sin((4*x))/4)),x)
(cos((6*x))/24)+(-cos((2*x))/8)+(-cos((4*x))/16)
=> (cos((6*x))/24)+(-cos((2*x))/8)+(-cos((4*x))/16)

? integrate(sin(4*x)*sin(8*x),x)
thinking...
integrate((sin((4*x))*sin((8*x))),x)
integrate(((cos((4*x))/2)+(-cos((12*x))/2)),x)
(-sin((12*x))/24)+(sin((4*x))/8)
=> (-sin((12*x))/24)+(sin((4*x))/8)

? integrate(cos(2*x)^4,x)
thinking...
integrate((cos((2*x))^4),x)
integrate(((3/8)+(cos((4*x))/2)+(cos((8*x))/8)),x)
((3*x)/8)+(sin((4*x))/8)+(sin((8*x))/64)
=> ((3*x)/8)+(sin((4*x))/8)+(sin((8*x))/64)

? integrate(x/((x+1)*(x+2)),x)
thinking...
(log(abs((2+(3*x)+(x^2))))/2)+(-(3*integrate((1/(2+(3*x)+(x^2))),x))/2)
(log(abs(((1+x)*(2+x))))/2)+(-(3*integrate((1/((1+x)*(2+x))),x))/2)
(log(abs(((1+x)*(2+x))))/2)+(-(3*integrate(((-1/(1+x))+(1/(2+x))),x))/2)
(log(abs(((1+x)*(2+x))))/2)+((3*(log(abs((1+x)))-log(abs((2+x)))))/2)
=> (log(abs((2+(3*x)+(x^2))))/2)+((3*log(abs((1+x))))/2)+(-(3*log(abs((2+x))))/2)

? integrate(1/(x^2-9),x)
thinking...
integrate((1/((-3+x)*(3+x))),x)
integrate(((-1/(6*(-3+x)))+(1/(6*(3+x)))),x)
(log(abs((3+x)))/6)+(-log(abs((-3+x)))/6)
=> (log(abs((3+x)))/6)+(-log(abs((-3+x)))/6)

? integrate((3*x-1)/((x-1)*(x-2)*(x-3)),x)
thinking...
integrate(((-1+(3*x))/((-1+x)*(-2+x)*(-3+x))),x)
integrate(((-1/(-1+x))+(-4/(-3+x))+(5/(-2+x))),x)
(5*log(abs((-2+x))))-log(abs((-1+x)))-(4*log(abs((-3+x))))
=> (5*log(abs((-2+x))))-log(abs((-1+x)))-(4*log(abs((-3+x))))

? integrate(x/((x-1)*(x-2)*(x-3)),x)
thinking...
integrate((x/((-1+x)*(-2+x)*(-3+x))),x)
integrate(((-1/(2*(-1+x)))+(-3/(2*(-3+x)))+(2/(-2+x))),x)
(-log(abs((-1+x)))/2)+(-(3*log(abs((-3+x))))/2)+(2*log(abs((-2+x))))
=> (-log(abs((-1+x)))/2)+(-(3*log(abs((-3+x))))/2)+(2*log(abs((-2+x))))

? integrate(2*x/(x^2+3*x+2),x)
thinking...
2*((log(abs((2+(3*x)+(x^2))))/2)+(-(3*integrate((1/(2+(3*x)+(x^2))),x))/2))
2*((log(abs(((1+x)*(2+x))))/2)+(-(3*integrate((1/((1+x)*(2+x))),x))/2))
2*((log(abs(((1+x)*(2+x))))/2)+(-(3*integrate(((-1/(1+x))+(1/(2+x))),x))/2))
2*((log(abs(((1+x)*(2+x))))/2)+((3*(log(abs((1+x)))-log(abs((2+x)))))/2))
=> log(abs((2+(3*x)+(x^2))))+(3*log(abs((1+x))))-(3*log(abs((2+x))))

? integrate((1-x^2)/(x*(1-2*x)),x)
thinking...
integrate((((1-x)*(1+x))/((1-(2*x))*x)),x)
integrate(((-1/x)+(-2/(1-(2*x)))),x)
log(abs((1-(2*x))))-log(abs(x))
=> log(abs((1-(2*x))))-log(abs(x))

? integrate(x/((x-1)^2*(x+2)),x)
thinking...
integrate((x/((2+x)*((-1+x)^2))),x)
integrate(((-1/(3*((-1+x)^2)))+(-2/(9*(-1+x)))+(2/(9*(2+x)))),x)
(1/(3*(-1+x)))+((2*log(abs((2+x))))/9)+(-(2*log(abs((-1+x))))/9)
=> (1/(3*(-1+x)))+((2*log(abs((-1+x))))/(9*(-1+x)))+((2*log(abs((2+x)))*x)/(9*(-1+x)))+(-(2*log(abs((-1+x)))*x)/(9*(-1+x)))+(-(2*log(abs((2+x))))/(9*(-1+x)))

? integrate((2*x-3)/((x^2-1)*(2*x+3)),x)
thinking...
integrate(((-3+(2*x))/((-1+x)*(1+x)*(3+(2*x)))),x)
integrate(((-5/(2*(1+x)))+(1/(10*(-1+x)))+(24/(5*(3+(2*x))))),x)
(log(abs((-1+x)))/10)+((12*log(abs((3+(2*x)))))/5)+(-(5*log(abs((1+x))))/2)
=> (log(abs((-1+x)))/10)+((12*log(abs((3+(2*x)))))/5)+(-(5*log(abs((1+x))))/2)

? integrate(5*x/((x+1)*(x^2-4)),x)
thinking...
5*integrate((x/((-2+x)*(1+x)*(2+x))),x)
5*integrate(((-1/(3*(1+x)))+(-1/(6*(-2+x)))+(1/(2*(2+x)))),x)
5*((log(abs((2+x)))/2)+(-log(abs((-2+x)))/6)+(-log(abs((1+x)))/3))
=> ((5*log(abs((2+x))))/2)+(-(5*log(abs((-2+x))))/6)+(-(5*log(abs((1+x))))/3)

? (x+2)*(x+3)/((x-2)*(x-3))<=1
thinking...
(-1+(((2+x)*(3+x))/((-2+x)*(-3+x))))<=0
((-1+(((2+x)*(3+x))/((-2+x)*(-3+x))))=0)|((-1+(((2+x)*(3+x))/((-2+x)*(-3+x))))<0)
((-1+(6/((-2+x)*(-3+x)))+((5*x)/((-2+x)*(-3+x)))+((x^2)/((-2+x)*(-3+x))))=0)|((-1+(6/((-2+x)*(-3+x)))+((5*x)/((-2+x)*(-3+x)))+((x^2)/((-2+x)*(-3+x))))<0)
(((10*(x^5))+(360*x)+(370*(x^3))-(100*(x^4))-(600*(x^2)))=0)|((((10*(x^5))+(360*x)+(370*(x^3))-(100*(x^4))-(600*(x^2)))/(((-2+x)^3)*((-3+x)^3)))<0)
((((10*(x^5))+(360*x)+(370*(x^3))-(100*(x^4))-(600*(x^2)))=0)|((((10*(x^5))+(360*x)+(370*(x^3))-(100*(x^4))-(600*(x^2)))/(((-2+x)^3)*((-3+x)^3)))<0))&x∈(-inf,+inf)-{2,3}
((((10*(x^5))+(360*x)+(370*(x^3))-(100*(x^4))-(600*(x^2)))=0)|((((10*(x^5))+(360*x)+(370*(x^3))-(100*(x^4))-(600*(x^2)))/(((-2+x)^3)*((-3+x)^3)))<0))&x∈(-inf,+inf)-{3,2}
=> ((((10*(x^5))+(360*x)+(370*(x^3))-(100*(x^4))-(600*(x^2)))=0)|((((10*(x^5))+(360*x)+(370*(x^3))-(100*(x^4))-(600*(x^2)))/(((-2+x)^3)*((-3+x)^3)))<0))&x∈(-inf,+inf)-{3,2}

? cos(x)/(1+sin(x))+(1+sin(x))/cos(x)=2*sec(x)
thinking...
(((1+sin(x))/cos(x))+(cos(x)/(1+sin(x)))-(2*sec(x)))=0
((-2/cos(x))+((1+sin(x))/cos(x))+(cos(x)/(1+sin(x))))=0
0=0
true
=> true

? tan(x)/(1-cot(x))+cot(x)/(1-tan(x))=1+sec(x)*cosec(x)
thinking...
(-1+(cot(x)/(1-tan(x)))+(tan(x)/(1-cot(x)))-(cosec(x)*sec(x)))=0
(-1+(-1/(cos(x)*sin(x)))+(cos(x)/((1+(-sin(x)/cos(x)))*sin(x)))+(sin(x)/((1+(-cos(x)/sin(x)))*cos(x))))=0
0=0
true
=> true

? (1+sec(x))/sec(x)=sin(x)^2/(1-cos(x))
thinking...
(((1+sec(x))/sec(x))+(-(sin(x)^2)/(1-cos(x))))=0
((-(sin(x)^2)/(1-cos(x)))+((1+(1/cos(x)))*cos(x)))=0
0=0
true
=> true

? (cos(x)-sin(x)+1)/(cos(x)+sin(x)-1)=cosec(x)+cot(x)
thinking...
(((1+cos(x)-sin(x))/(-1+cos(x)+sin(x)))-cosec(x)-cot(x))=0
((-1/sin(x))+((1+cos(x)-sin(x))/(-1+cos(x)+sin(x)))+(-cos(x)/sin(x)))=0
0=0
true
=> true

? integrate(x/((x-1)*(x^2+1)),x)
thinking...
integrate((x/((-1+x)*(1+(x^2)))),x)
integrate(((-1/(2*(-1+x)))+(((-1/2)+(x/2))/(1+(x^2)))),x)
(log(abs((1+(x^2))))/4)+(-arctan(x)/2)+(-log(abs((-1+x)))/2)
=> (log(abs((1+(x^2))))/4)+(-arctan(x)/2)+(-log(abs((-1+x)))/2)

? (sin(x)-2*sin(x)^3)/(2*cos(x)^3-cos(x))=tan(x)
thinking...
(((-(2*(sin(x)^3))+sin(x))/((2*(cos(x)^3))-cos(x)))-tan(x))=0
(((-(2*(sin(x)^3))+sin(x))/((2*(cos(x)^3))-cos(x)))+(-sin(x)/cos(x)))=0
0=0
true
=> true

? (cosec(x)-sin(x))*(sec(x)-cos(x))=1/(tan(x)+cot(x))
thinking...
((-1/(cot(x)+tan(x)))+((cosec(x)-sin(x))*(-cos(x)+sec(x))))=0
((-1/((cos(x)/sin(x))+(sin(x)/cos(x))))+(((1/cos(x))-cos(x))*((1/sin(x))-sin(x))))=0
0=0
true
=> true

? integrate(2/((1-x)*(1+x^2)),x)
thinking...
2*integrate((1/((1-x)*(1+(x^2)))),x)
2*integrate(((-1/(2*(1-x)))+(((-1/2)+(-x/2))/(1+(x^2)))),x)
2*((log(abs((1-x)))/2)+(-arctan(x)/2)+(-log(abs((1+(x^2))))/4))
=> (-log(abs((1+(x^2))))/2)+log(abs((1-x)))-arctan(x)

? x^2-abs(x+2)+x>0
thinking...
(-abs((2+x))+(x^2)+x)>0
(((2+x)<0)&~(((2+(2*x)+(x^2))=0)|((2+(2*x)+(x^2))<0)))|(~(((-2+(x^2))=0)|((-2+(x^2))<0))&(((2+x)=0)|~(((2+x)=0)|((2+x)<0))))
(((2+x)<0)&~(((2+(2*x)+(x^2))=0)|((2+(2*x)+(x^2))<0)))|(~(((-2+(x^2))=0)|((-2+(x^2))<0))&(((2+x)=0)|~(((2+x)=0)|((2+x)<0))))
x∈(-inf,-sqrt(8)/2)U(sqrt(8)/2,+inf)
=> x∈(-inf,-sqrt(8)/2)U(sqrt(8)/2,+inf)

? limit(sin(x)/x,x)
thinking...
=> 1

? limit((x^2 - 1)/(x-1),x,1)
thinking...
=> 2

? dif(y,x)=sqrt(4-y^2)
thinking...
(-arcsin((y/2))+x+c1)=0
=> (-arcsin((y/2))+x+c1)=0

? dif(y,x)+y=1
thinking...
(log(abs((1-y)))+x+c1)=0
=> (log(abs((1-y)))+x+c1)=0

? x^5*dif(y,x)=-y^5
thinking...
((4*(x^4)*(y^4)*c1)+(x^4)+(y^4))=0
=> ((4*(x^4)*(y^4)*c1)+(x^4)+(y^4))=0

? dif(y,x)=(1+x^2)*(1+y^2)
thinking...
((3*x)+(3*c1)-(3*arctan(y))+(x^3))=0
=> ((3*x)+(3*c1)-(3*arctan(y))+(x^3))=0

? x*(x^2-1)*dif(y,x)=1
thinking...
(integrate((1/((-1+x)*(1+x)*x)),x)-y+c1)=0
(integrate(((-1/(2*(-1+x)))+(-1/(2*(1+x)))+(1/x)),x)-y+c1)=0
((-log(abs((-1+x)))/2)+(-log(abs((1+x)))/2)+log(abs(x))-y+c1)=0
=> ((4*log(abs(x)))+(4*c1)-(2*log(abs((-1+x))))-(2*log(abs((1+x))))-(4*y))=0

? (x^2+x*y)*dif(y,x)=(x^2+y^2)
thinking...
try(subs((integrate(((1+z)/(-1+z)),z)+log(abs(x))+c1),z,(y/x)))=0
try(subs((integrate(((1/(-1+z))+(z/(-1+z))),z)+log(abs(x))+c1),z,(y/x)))=0
try(subs((integrate((z/(-1+z)),z)+log(abs((-1+z)))+log(abs(x))+c1),z,(y/x)))=0
try(subs((integrate(((-1+(z^2))/((-1+z)^2)),z)+log(abs(x))+c1),z,(y/x)))=0
try(subs((integrate(((1/(-1+z))+(z/(-1+z))),z)+log(abs(x))+c1),z,(y/x)))=0
try(subs((log(abs((-1+z)))+log(abs(x))+try(subs(integrate(((-1+(-1/a))/a),a),a,(1/(-1+z))),subs(integrate(((1+a)/a),a),a,(-1+z)))+c1),z,(y/x)))=0
try(subs((log(abs((-1+z)))+log(abs(x))+try(subs(((-log(abs((a^2)))/2)-integrate((1/(a^2)),a)),a,(1/(-1+z))),subs(integrate(((1+a)/a),a),a,(-1+z)))+c1),z,(y/x)))=0
try(subs((log(abs((-1+z)))+log(abs(x))+try(subs(((1/a)+(-log(abs((a^2)))/2)),a,(1/(-1+z))),subs(integrate(((1+a)/a),a),a,(-1+z)))+c1),z,(y/x)))=0
=> ((2*log(abs((-1+(y/x))))*x)+(2*log(abs(x))*x)+(2*x*c1)+(2*y)-(2*x)-(log(abs((1/((-1+(y/x))^2))))*x))=0

? dif(y,x)=(x+y)/x
thinking...
try(subs((log(abs(x))-z+c1),z,(y/x)))=0
=> ((log(abs(x))*x)+(x*c1)-y)=0

? (x-y)*dif(y,x)-(x+y)=0
thinking...
try(subs(((log(abs((-1-(z^2))))/2)+log(abs(x))-arctan(z)+c1),z,(y/x)))=0
=> (log(abs((-1+(-(y^2)/(x^2)))))+(2*log(abs(x)))+(2*c1)-(2*arctan((y/x))))=0

? (x^2-y^2)+2*x*y*dif(y,x)=0
thinking...
try(subs((((2*c1)-log(abs((1+(z^2))))-log(abs(x)))/2),z,(y/x)))=0
=> ((2*c1)-log(abs((1+((y^2)/(x^2)))))-log(abs(x)))=0

? x*dif(y,x)-y+x*sin(y/x)=0
thinking...
try(subs((-log(abs(tan((z/2))))-log(abs(x))+c1),z,(y/x)))=0
=> (-log(abs((sin((y/(2*x)))/cos((y/(2*x))))))-log(abs(x))+c1)=0

? (a+b)^2 = a^2 + b^2 + 2*a*b
thinking...
(-(2*a*b)-(a^2)-(b^2)+((a+b)^2))=0
0=0
true
=> true

? (x-1)*(x+1) = x^2 - 1
thinking...
(1+((-1+x)*(1+x))-(x^2))=0
0=0
true
=> true

? integrate((7^(7^(7^x)))*(7^(7^x))*(7^x),x)
thinking...
integrate((7^((7^(7^x))+(7^x)+x)),x)
subs(integrate((1/((7^-y)*(log(7)^2))),y),y,(7^(7^x)))
subs((1/((7^-y)*(log(7)^3))),y,(7^(7^x)))
=> 1/((7^-(7^(7^x)))*(log(7)^3))
```
