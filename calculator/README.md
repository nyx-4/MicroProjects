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
    - [From Python](#from-python)
- [Syntax](#syntax)
    - [Operators](#operators)
    - [Constants](#constants)
    - [Functions](#functions)
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
calc bitand 0xFE, 0x2e
```


### From Python

```py
from calculator import calc


calc("192", base=16)
calc("10 / 6", scale=3)
calc("sin(pi)")
calc("bitand 0xFE, 0x2e")
```


## Syntax
`calc` knows some operators, constants, functions and can (obviously) read numbers.

For numbers, `.` is always the radix character regardless of locale - `2.5`, not `2,5`. Scientific notation (`10e5`) and hexadecimal (`0xFF`) are also available.

`calc` also allows the use of underscores as visual separators for digit grouping. For example, you can write `1_000_000`, `0x_89_AB_CD_EF`, and `1.234_567_e89`.

### Operators
All of these [operators](https://fishshell.com/docs/current/cmds/math.html#operators). Note that `^` is used for exponentiation, not `**`.

### Constants
All of these [constants](https://fishshell.com/docs/current/cmds/math.html#constants).


### Functions
All of these [functions](https://fishshell.com/docs/current/cmds/math.html#functions) and all of these [functions](https://docs.python.org/3/library/math.html)




## Examples

Taken verbatium from [math - perform mathematics calculations](https://fishshell.com/docs/current/cmds/math.html#examples)

`calc 1+1` outputs `2`.  

`calc 10 / 6` outputs `1.666667`.  

`calc -s0 10.0 / 6.0` outputs `1`.  

`calc -s3 10 / 6` outputs `1.667`.  

`calc "sin(pi)"` outputs `0`.  

`calc 5 \* 2` or `math "5 * 2"` or math `5 "*" 2` all output 10.  

`calc 0xFF` outputs 255, `math 0 x 3` outputs `0` (because it computes 0 multiplied by 3).  

`calc bitand 0xFE, 0x2e` outputs `46`.  

`calc "bitor(9,2)"` outputs `11`.  

`calc --base=hex 192` prints `0xc0`.  

`calc 'ncr(49,6)'` prints `13983816` - that’s the number of possible picks in 6-from-49 lotto.  

`calc max 5,2,3,1` prints `5`.  


## Contributing


## License
All the code here is licensed under [GPL 3.0](https://www.gnu.org/licenses/gpl-3.0.en.html). The content and tests taken fish-shell are rightfully theirs and covered under [fish license](https://github.com/fish-shell/fish-shell/?tab=License-1-ov-file)

