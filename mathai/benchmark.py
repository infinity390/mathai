import random
import copy
from pathlib import Path
from .simplify import simplify
from .expand import expand
from .parser import parse
from .fraction import fraction
from .apart import apart
from .integrate import integrate_formula, integrate_trig_formula, integrate_fraction
from .integrate import integrate_subs_main as integrate_subs
from .integrate import solve_integrate as integrate_clean
from .factor import factor2
from .trig import trig0, trig1, trig4, trig6
from .univariate_inequality import simple_wavycurvy, absolute
from .limit import limit1
from .logic import logic0
from .base import *

fx_list = [lambda x: dowhile(x, absolute), logic0, limit1, simple_wavycurvy, simplify, expand, fraction, integrate_formula, integrate_subs, integrate_trig_formula, integrate_clean, apart, trig0, trig1, trig4, integrate_fraction, factor2, trig6]
name_list = "absolute, logic0, limit1, simple_wavycurvy, simplify, expand, fraction, integrate_formula, integrate_subs, integrate_trig_formula, integrate_clean, apart, trig0, trig1, trig4, integrate_fraction, factor2, trig6".split(", ")

def benchmark(s="ncert_data"):
    data_path = Path(__file__).parent / f"{s}.txt"
    output_path = Path(__file__).parent / f"{s}_optimized.txt"
    
    optimized_lines = []
    
    with open(data_path, "r", encoding="utf-8") as file:
        content = file.read().strip().split("\n")
        count = 0
        for item in content:
            count += 1
            item = item.strip()
            if not item:
                continue
            parts = item.split(" ")
            expr_str = parts[0]
            eq = simplify(parse(expr_str))
            
            effective_steps = [expr_str]
            
            for func_name in parts[1:]:
                func_idx = name_list.index(func_name)
                func = fx_list[func_idx]
                
                # Deepcopy to avoid in-place mutation reference traps
                prev_eq = copy.deepcopy(eq)
                eq = func(eq)
                
                # Check if the function changed the equation
                if eq == prev_eq:
                    pass
                else:
                    effective_steps.append(func_name)
            
            print(f"{count}. {expr_str} => {eq}")
            optimized_lines.append(" ".join(effective_steps))
            
    # Write out the optimized lines without non-changing functions
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write("\n".join(optimized_lines) + "\n")
        
    print(f"\nOptimized dataset successfully written to: {output_path}")
