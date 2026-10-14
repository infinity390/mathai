from .base import *
from .simplify import simplify

expect = lambda x: load_formula("statistics_1")(x)
expect_2 = lambda x: load_formula("statistics_2")(x)
