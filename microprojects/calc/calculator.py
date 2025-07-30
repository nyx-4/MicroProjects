import math
import sys
from microprojects.calc import analyzer


def calc(expr, *, scale=6, scale_mode="default") -> int | float:
    def Min(*args):
        return min(args) if type(args) is tuple else args

    def Max(*args):
        return max(args) if type(args) is tuple else args

    def Sum(*args):
        return sum(args) if type(args) is tuple else args

    lexemes: dict = {
        "^": lambda x, y: x**y,
        "%": lambda x, y: x % y,
        "/": lambda x, y: x / y,
        "*": lambda x, y: x * y,
        "+": lambda x, y: x + y,
        "-": lambda x, y: x - y,
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
        "c": 299_792_458,
        "bitand": lambda x, y: int(x) & int(y),
        "bitor": lambda x, y: int(x) | int(y),
        "bitxor": lambda x, y: int(x) ^ int(y),
        "min": Min,
        "max": Max,
        "sum": Sum,
        "round": round,
        "pow": math.pow,
        "ncr": math.comb,
        "npr": math.perm,
        "perm": math.perm,
        "comb": math.comb,
        "factorial": math.factorial,
        "fac": math.factorial,
        "gcd": math.gcd,
        "lcm": math.lcm,
        "isqrt": math.isqrt,
        "ceil": math.ceil,
        "fabs": math.fabs,
        "floor": math.floor,
        "fma": math.fma,
        "fmod": math.fmod,
        "modf": math.modf,
        "remainder": math.remainder,
        "trunc": math.trunc,
        "cbrt": math.cbrt,
        "exp": math.exp,
        "exp2": math.exp2,
        "expm1": math.expm1,
        "log": math.log,
        "ln": math.log1p,
        "log1p": math.log1p,
        "log2": math.log2,
        "log10": math.log10,
        "sqrt": math.sqrt,
        "dist": math.dist,
        "fsum": math.fsum,
        "hypot": math.hypot,
        "prod": math.prod,
        "sumprod": math.sumprod,
        "degrees": math.degrees,
        "radians": math.radians,
        "acos": math.acos,
        "asin": math.asin,
        "atan": math.atan,
        "atan2": math.atan2,
        "cos": math.cos,
        "sin": math.sin,
        "tan": math.tan,
        "acosh": math.acosh,
        "asinh": math.asinh,
        "atanh": math.atanh,
        "cosh": math.cosh,
        "sinh": math.sinh,
        "tanh": math.tanh,
        "gamma": math.gamma,
        "lgamma": math.lgamma,
    }

    operators: str = "^%/*+-"

    token_stream: list = analyzer.lexical_analyzer(expr, lexemes)
    rev_polish: list = analyzer.shunting_yard(token_stream, operators)
    answer = analyzer.solve_rpn(rev_polish, operators, lexemes)
    if type(answer) is int:  # int doesn't need scale or scale_mode
        return answer
    else:  # Using scale and scale_mode to format output
        if scale == 0:  # scale_mode, only works if scale is 0
            if scale_mode == "round":
                return round(answer)
            elif scale_mode == "ceiling":
                return math.ceil(answer)
            elif scale_mode == "floor":
                return math.floor(answer)
            else:
                return math.trunc(answer)
        else:
            return round(answer, scale)


def calc_main() -> None:
    scale: int = 6
    base: int = 10
    scale_mode: str = "default"

    i: int = 1
    while i != len(sys.argv):
        if sys.argv[i] in ["-s", "--scale"]:
            scale = int(sys.argv[i + 1])
        elif sys.argv[i] in ["-b", "--base"]:
            base = int(sys.argv[i + 1])
        elif sys.argv[i] in ["-m", "--scale-mode"]:
            scale_mode = sys.argv[i + 1]
        else:
            break
        i += 2
    else:
        sys.exit("calc: expected >= 1 arguments; got 0")

    answer = calc(" ".join(sys.argv[i:]), scale=scale, scale_mode=scale_mode)
    if base == 2:
        print(f"{int(answer):#b}")
    elif base == 8:
        print(f"0{int(answer):o}")
    elif base == 16:
        print(f"{int(answer):#x}")
    else:
        print(f"{answer}")
