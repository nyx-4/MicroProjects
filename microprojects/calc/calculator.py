import math
import sys
from microprojects.calc import analyzer


def calc(expr, *, scale=6, base=10, scale_mode="default") -> int:
    lexemes: dict = {
        "min": min,
        "max": max,
        "c": 299_792_458,
        "pi": 3.14159265358979323,
        "pow": pow,
        "bitand": lambda x, y: x & y,
    }

    print(analyzer.lexical_analyzer(expr, known_lexemes=lexemes))
    # print(f"{expr=} {scale=} {base=} {scale_mode=}")
    return 0


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

    calc(
        " ".join(sys.argv[i:]),
        scale=scale,
        base=base,
        scale_mode=scale_mode,
    )
