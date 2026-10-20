from .fraction import fraction
from .simplify import simplify
from .parser import parse
from .base import *
from .expand import expand

from .limit import limit1, limit2, limit0, limit3, limit4

from .factor import factor2

from .inverse import inverse

from .integrate import integrate_subs_main as integrate_subs
from .integrate import byparts as integrate_byparts
from .integrate import integrate_fraction
from .integrate import solve_integrate as integrate_clean
from .integrate import integrate_formula, integrate_full
from .integrate import normalize as integration_basic

from .diff import diff
from .formula_compiler import formula_list_compiler

def helium_gse():
    basic_int = lambda x: dowhile(x, lambda y: expand(simplify(integrate_formula(y))))
    algebra = lambda x: dowhile(x, lambda y: expand(simplify(y)))
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
        nonlocal a0, pi, euler, Z
        two = tree_form("d_2")
        return (Z**3 / (pi * a0**3)) * euler**(-Z * (r1 + r2) / a0)
    def r12(r1, r2, theta1, theta2, phi1, phi2):
        return TreeNode("f_max", [r1, r2])
    f = psi(r1, r2)
    def pdif(eq, wrt):
        return diff(eq, wrt.name)
    def laplacian_r1(f):
        nonlocal r1, theta1, phi1
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
        nonlocal r2, theta2, phi2
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
      eq = basic_int(eq)
      eq = simplify(expand(eq))
      eq = basic_int(eq)
      eq = simplify(fraction(eq))
      eq_a = TreeNode("f_limit", [replace(eq, wrt, wrt+a), wrt])
      eq_a = limit1(eq_a)
      eq_b = None
      if b == tree_form("s_inf"):
          eq = algebra(eq)
          eq = simplify(expand(eq))
          eq_b = TreeNode("f_limitpinf", [eq, wrt])
          eq_b = dowhile(eq_b, lambda x: expand(limit3(simplify(x))))
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
    return compute(simplify(H/e1))

power_rule_s = "a^sum(b,c) a^b*a^c [] x _ _ _"
power_rule = formula_list_compiler(power_rule_s)

def hydrogen_gse():
    basic_int = lambda x: dowhile(x, lambda y: integrate_formula(simplify(expand(simplify(power_rule(y))))))
    algebra = lambda x: dowhile(x, lambda y: expand(simplify(y)))
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
    integral_psi2 = basic_int(copy.deepcopy(integral_psi2))
    a = limit1(TreeNode("f_limit", [integral_psi2, r]))
    b = limit3(simplify(TreeNode("f_limitpinf", [integral_psi2, r])))
    integral_psi2 = algebra(b-a)
    V = -(k * z * e1**2)/r
    Hpsi = -hbar**2/(2*m) * laplace_psi + V*psi
    psiHpsi = psi * Hpsi
    integral_psiHpsi = TreeNode("f_integrate", [psiHpsi * parse("4")* pi * r**2, r])
    integral_psiHpsi = basic_int(integral_psiHpsi)
    a = limit1(TreeNode("f_limit", [integral_psiHpsi, r]))
    b = limit3(simplify(expand(TreeNode("f_limitpinf", [integral_psiHpsi, r]))))
    integral_psiHpsi = algebra(b-a)
    result =  integral_psiHpsi / integral_psi2
    return compute(simplify(result /e1))
