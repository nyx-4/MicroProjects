import math
import sys
from calculator import lexical_analyzer


def calc(expr, *, scale=6, base=10, scale_mode="default") -> int:
    print(f"{expr=} {scale=} {base=} {scale_mode=}")
    return 0


def main() -> None:
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
        sys.exit("math: expected >= 1 arguments; got 0")

    sys.exit(
        calc(
            lexical_analyzer.normalize_expr(sys.argv[i:]),
            scale=scale,
            base=base,
            scale_mode=scale_mode,
        )
    )


if __name__ == "__main__":
    main()
