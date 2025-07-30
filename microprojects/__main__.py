def main():
    """Running microprojects as a module causes ambuiguity because
    we provides multiple executable scripts.

    Did you mean:
        python -m microprojects.calc
        python -m microprojects.ngit
    """
    print(main.__doc__)


if __name__ == "__main__":
    main()
