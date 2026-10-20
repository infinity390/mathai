import random
from .simplify import simplify
from .expand import expand
from .parser import parse
from .fraction import fraction
from .apart import apart
from .integrate import integrate_formula, integrate_trig_formula, integrate_fraction
from .integrate import integrate_subs_main as integrate_subs
from .integrate import solve_integrate as integrate_clean
from .factor import factor2
from .trig import trig0, trig1, trig4
from pathlib import Path
fx_list = [simplify, expand, fraction, integrate_formula, integrate_subs, integrate_trig_formula, integrate_clean, apart, trig0, trig1, trig4, integrate_fraction, factor2]
name_list = "simplify, expand, fraction, integrate_formula, integrate_subs, integrate_trig_formula, integrate_clean, apart, trig0, trig1, trig4, integrate_fraction, factor2".split(", ")
def benchmark_ncert():
    # Locate ncert_data.txt in the same directory as this benchmark.py file
    data_path = Path(__file__).parent / "ncert_data.txt"
    
    with open(data_path, "r", encoding="utf-8") as file:
        content = file.read().strip().split("\n")
        count = 0
        for item in content:
            count += 1
            item = item.strip()
            if not item:
                continue
            parts = item.split(" ")
            eq = simplify(parse(parts[0]))
            for item2 in parts[1:]:
                eq = fx_list[name_list.index(item2)](eq)
            print(f"{count}. {parts[0]} => {eq}")
