import check50


@check50.check()
def exists():
    """Checking whether calculator/main.py exists"""
    check50.exists("microprojects/calc/__main__.py")
    check50.exists("microprojects/calc/__init__.py")


@check50.check(exists)
def pip_install_proj():
    """If this test fails, try using venv by `python3 -m venv .venv && source .venv/bin/activate`"""
    check50.run("pip install -e .").stdout(
        "Successfully installed microprojects", timeout=30
    ).exit(0, timeout=30)


@check50.check(pip_install_proj)
def calc_():
    """Checking whether `calc` exists"""
    check50.run("calc").stdout("calc: expected >= 1 arguments; got 0").exit(1)


@check50.check(calc_)
def test_sub():
    """testing output of 1-1"""
    check50.run("calc 1-1").stdout("0", regex=False).exit(0)
