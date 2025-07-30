## Calculator - A Simple Python Calculator
A simple calculator written in Python that _just_ works. **This Calculator is highly inspired by fish-shell's `math` command, it may be considered a port of `math` in Python.**  

## Table of Content
- [Calculator - A Simple Python Calculator](#calculator---a-simple-python-calculator)
- [Table of Content](#table-of-content)
- [Synopsis](#synopsis)
- [Description](#description)
- [Quick start](#quick-start)
- [Getting Calculator](#getting-calculator)
    - [Source](#source)
    - [PyPI (Python)](#pypi-python)
- [Usage](#usage)
    - [From CLI](#from-cli)
    - [As Python module](#as-python-module)
    - [From Python source](#from-python-source)
- [CLI flags](#cli-flags)
    - [`-b BASE or --base BASE`:](#-b-base-or---base-base)
    - [`m MODE or --scale-mode MODE`:](#m-mode-or---scale-mode-mode)
    - [`-s N or --scale N`;](#-s-n-or---scale-n)
- [Syntax](#syntax)
    - [Operators](#operators)
    - [Constants](#constants)
    - [Functions](#functions)
- [Deviations from fish-shell's `math`](#deviations-from-fish-shells-math)
    - [Handling Hexadecimals](#handling-hexadecimals)
    - [Function's paranthesis](#functions-paranthesis)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Synopsis
```sh
calc [(-s | --scale) N] [(-b | --base) BASE] [(-m | --scale-mode) MODE] EXPRESSION ...
```
```py
calc(expr, scale=6, base=10, scale_mode="default")
```


## Description
`Calculator` is a Python-based drop-in replacement for the `math` command in [fish-shell](https://fishshell.com/docs/current/cmds/math.html), providing basic arithmetic operations like `addition`, `subtraction`, and so on, as well as mathematical functions like `sin()`, `ln()`, and `nPr()`.  
Like the fish implementation of `math`, the paranthesis for functions are optional (but recommended) and whitespaces between arguments are ignored.  

## Quick start


## Getting Calculator

### Source

Clone the development version from [MicroProjects - GitHub](https://github.com/nyx-4/MicroProjects.git)

```sh
git clone https://github.com/nyx-4/MicroProjects.git
cd MicroProjects
pip install .
```

### PyPI (Python)

Use the package manager pip to install foobar.

```sh
pip install microprojects
```


## Usage

Also see [Examples](#examples).

### From CLI

```sh
calc --base 16 192
calc -s 3 10 / 6
calc "sin(pi)"
calc "bitand(0xFE, 0x2e)"
```


### As Python module

```sh
python -m microprojects.calc --base 16 192
python -m microprojects.calc -s 3 10 / 6
python -m microprojects.calc "sin(pi)"
python -m microprojects.calc "bitand(0xFE, 0x2e)"
```


### From Python source

```py
from calculator import calc


microprojects.calc("192", base=16)
microprojects.calc("10 / 6", scale=3)
microprojects.calc("sin(pi)")
microprojects.calc("bitand(0xFE, 0x2e)")
```

## CLI flags
### `-b BASE or --base BASE`:
Sets the numeric base used for output. It currently supports 2, 8, 10 and 16. The prefix of 0b, 0o, and 0x will be used.
> [!NOTE]
> The base's other than 10 implies the scale of 0. The output is rounded to nearest even number.

### `m MODE or --scale-mode MODE`:
Sets scale behavior. The MODE can be `truncate`, `round`, `floor`, `ceiling`. The default value of scale mode is `round`.
> [!NOTE]
> The scale-mode is ignored if scale is not 0.

### `-s N or --scale N`;
Sets the scale of the result. `N` must be an interger.


## Syntax
`calc` knows some operators, constants, functions and can (obviously) read numbers.

For numbers, `.` is always the radix character regardless of locale - `2.5`, not `2,5`. Scientific notation (`10e5`) and hexadecimal (`0xFF`) are also available.

`calc` also allows the use of underscores as visual separators for digit grouping. For example, you can write `1_000_000`, `0x_89_AB_CD_EF`, and `1.234_567_e89`.

### Operators
All of these [operators](https://fishshell.com/docs/current/cmds/math.html#operators). 
> [!NOTE]
> `^` is used for exponentiation, not `**`.

### Constants
`e`: Euler's number
`pi`: Pi
`tau`: Tau, equivalent to 2 * pi
`c`: The speed of light

### Functions
All of these [functions](https://fishshell.com/docs/current/cmds/math.html#functions) and all of these [functions](https://docs.python.org/3/library/math.html)


## Deviations from fish-shell's `math`

### Handling Hexadecimals
1. In `calc`, _0_ before _x_ in hexadecimals is optional.
2. The delimeter after a hexadecimal is optional, if the next char happens to be non-hexademical character (i.e., not `0123456789ABCDEFabcdef`)  
3. The `math` supports decimal-point in Hexadecimals, `calc` does not.

In `calc`, _x3_ is same as _0x3_ (or 3). In `math`, _x3_ responds with _**Error**: Unknown function_.  
_0x4.5_ is valid in `math`, but invalid in `calc`.  
In `calc`, _min(0x1api)_ is same as _min(0x1a, pi)_. In `math`, _min(0x1api)_ reponds with either _**Error**: Unexpected token_, or _**Error**: Too few arguments_ or _**Error**: Too many arguments_ depending on context [^0x1api].

[^0x1api]: The Errors and their context in math is:  
    `math 'min(0x1api)'` responds _**Error**: Too few arguments_.  
    `math '0x1api'` responds _**Error**: Unexpected token_  
    `math 'min(2,0x1api)'` responds _**Error**: Too many arguments_  


### Function's paranthesis
1. In `calc`, paranthesis are required to distinguish between _functions_ and _constants_. In `math`, paranthesis are optional.

In `calc`, the **_min_** in _min 1, 2_ is interpreted as constant. In `math`, _min 1, 2_ is same as _min(1, 2)_.  


## Examples

Taken verbatium from [math - perform mathematics calculations](https://fishshell.com/docs/current/cmds/math.html#examples)

`calc 1+1` outputs `2`.  

`calc 10 / 6` outputs `1.666667`.  

`calc -s0 10.0 / 6.0` outputs `1`.  

`calc -s3 10 / 6` outputs `1.667`.  

`calc "sin(pi)"` outputs `0`.  

`calc 5 \* 2` or `math "5 * 2"` or math `5 "*" 2` all output 10.  

`calc 0xFF` outputs 255, `math 0 x 3` outputs `0` (because it computes 0 multiplied by 3).  

`calc bitand (0xFE, 0x2e)` outputs `46`.  

`calc "bitor(9,2)"` outputs `11`.  

`calc --base=hex 192` prints `0xc0`.  

`calc 'ncr(49,6)'` prints `13983816` - that’s the number of possible picks in 6-from-49 lotto.  

`calc max(5,2,3,1)` prints `5`.  


## Contributing


## License
All my code here is licensed under [GPL 3.0](https://www.gnu.org/licenses/gpl-3.0.en.html). The content and tests taken fish-shell are rightfully theirs and covered under [fish license](https://github.com/fish-shell/fish-shell/?tab=License-1-ov-file)

